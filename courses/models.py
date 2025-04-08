# models.py
import os
import json
import re # Import regex
import fitz  # PyMuPDF
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging # Import the logging library

# Get an instance of the logger we configured in settings.py
logger = logging.getLogger('courses.extraction')

User = get_user_model()

class Category(models.Model):
    categoryImage = models.ImageField(upload_to='images/', null=True, blank=True)
    categoryName = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.categoryName

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    pdfs = models.FileField(upload_to='courses/pdfs/', null=True, blank=True, verbose_name='PDF Document')
    videos = models.FileField(upload_to='courses/videos/', null=True, blank=True, verbose_name='Video File')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    file_type = models.CharField(max_length=50, choices=[('pdf', 'PDF'), ('video', 'Video')], default='video')
    duration = models.CharField(max_length=20, blank=True)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # Removed _original_file_name, CoursePdfInternal handles this now
    # Note: The OneToOneField to CoursePdfInternal is added implicitly by the relation

    def __str__(self):
        return self.title

    # --- Updated PDF Extraction Logic ---
    def extract_data_from_pdf(self):
        """
        Extracts structured sections (title, content) and a table of contents
        from the PDF file, prioritizing embedded TOC if available.
        Returns: tuple(list_of_sections, list_of_toc_entries)
        """
        if not self.pdfs or self.file_type != 'pdf':
            logger.debug(f"Extraction skipped for {getattr(self.pdfs, 'name', 'N/A')}: Not a PDF or no file.")
            return [], []

        sections = []
        toc = []
        seen_titles = set()  # To track titles that have already been added
        current_section_data = None
        section_order = 0
        MAIN_HEADING_PATTERN = re.compile(r"^(?:[IVXLCDM]+\.|[A-Z]\.|[0-9]+\.)\s+.{3,}", re.IGNORECASE)
        SUB_HEADING_PATTERN = re.compile(r"^(?:[a-z]\.|[0-9]+\.[0-9]+(?:\.[0-9]+)*)\s+.{3,}", re.IGNORECASE)

        try:
            file_path = os.path.join(settings.MEDIA_ROOT, self.pdfs.name)
            doc = fitz.open(file_path)

            # --- Attempt to extract sections ---
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("blocks", sort=True)
                for b in blocks:
                    block_text = b[4].strip()
                    lines = block_text.split('\n')
                    if not lines: continue
                    first_line = lines[0].strip()

                    # Check if the first line is a potential title
                    is_potential_title = False
                    title_text = first_line
                    is_main_heading = MAIN_HEADING_PATTERN.match(first_line)
                    is_sub_heading = SUB_HEADING_PATTERN.match(first_line)

                    if is_main_heading and not is_sub_heading:
                        is_potential_title = True

                    # If it's a potential title and not seen before
                    if is_potential_title and title_text not in seen_titles:
                        if current_section_data:
                            sections.append(current_section_data)  # Save the previous section
                        current_section_data = {
                            'title': title_text,
                            'content': "\n".join(lines[1:]),  # Start new section content
                            'order': section_order
                        }
                        toc.append({'title': title_text, 'order': section_order})
                        seen_titles.add(title_text)  # Add title to the set
                        section_order += 1
                    elif current_section_data:
                        current_section_data['content'] += block_text + "\n"  # Append to current section

            # Append the last section if it exists
            if current_section_data:
                sections.append(current_section_data)

            logger.info(f"Successfully extracted {len(sections)} sections.")
            return sections, toc

        except Exception as e:
            logger.error(f"Error processing PDF {file_path or getattr(self.pdfs, 'name', 'N/A')}: {e}", exc_info=True)
            return [], []

# --- Signal Receiver (Refactored) ---

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizResult(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField()
    completed_at = models.DateTimeField(auto_now_add=True)


# New model to hold extracted PDF data
class CoursePdfInternal(models.Model):
    course = models.OneToOneField(
        'Course',
        related_name='pdf_internal_data', # How to access this from Course
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=512, blank=True) # Store the filename
    # Store extracted table of contents (list of titles/orders)
    table_of_contents = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Internal Data for {self.course.title} ({self.name})"

# CourseSection now links to CoursePdfInternal
class CourseSection(models.Model):
    # Changed ForeignKey to point to CoursePdfInternal
    pdf_data = models.ForeignKey(
        CoursePdfInternal,
        related_name='sections', # How to access sections from CoursePdfInternal
        on_delete=models.CASCADE,
        null=True # Temporarily allow null for migration
    )
    title = models.CharField(max_length=500)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        # Adjust __str__ to reflect the new relationship
        return f"{self.pdf_data.course.title} - Section {self.order}: {self.title}"


class Review(models.Model):
    cours = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.etudiant.username} - {self.cours.title} - {self.note}/5"


class EnrolledCourse(models.Model):
    cours = models.ForeignKey(Course, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cours', 'etudiant')

    def __str__(self):
        return f"{self.etudiant.username} inscrit à {self.cours.title}"


# No pre_save needed now

@receiver(post_save, sender=Course)
def process_course_pdf(sender, instance, created, **kwargs):
    """
    Processes the PDF associated with a Course instance after it's saved.
    Creates/updates CoursePdfInternal and related CourseSection objects.
    """
    should_process = False
    pdf_data_instance = None

    # Try to get existing internal data
    try:
        pdf_data_instance = instance.pdf_internal_data
    except CoursePdfInternal.DoesNotExist:
        pdf_data_instance = None

    # Case 1: New course with a PDF file
    if created and instance.pdfs and instance.file_type == 'pdf':
        should_process = True
        logger.info(f"New course with PDF detected: {instance.title}")

    # Case 2: Existing course, file changed TO a PDF or PDF file was updated
    elif not created and instance.pdfs and instance.file_type == 'pdf':
        if pdf_data_instance:
            if pdf_data_instance.name != instance.pdfs.name:
                should_process = True
                logger.info(f"PDF filename change detected for: {instance.title}")
        else:
            should_process = True
            logger.info(f"Course updated to PDF type: {instance.title}")

    # Case 3: Course type changed FROM PDF or file removed
    elif not created and (instance.file_type != 'pdf' or not instance.pdfs):
        if pdf_data_instance:
            logger.info(f"PDF removed or type changed for: {instance.title}. Deleting internal data.")
            pdf_data_instance.delete()  # Also cascades to delete sections
            return  # Stop processing

    # --- Perform Processing ---
    if should_process:
        logger.info(f"Starting PDF processing for course: {instance.title} (ID: {instance.pk})")
        try:
            # Create or get the CoursePdfInternal instance
            if not pdf_data_instance:
                pdf_data_instance = CoursePdfInternal.objects.create(course=instance)

            # Extract data
            extracted_sections, extracted_toc = instance.extract_data_from_pdf()
            logger.info(f"Extracted {len(extracted_sections)} sections and {len(extracted_toc)} TOC entries.")

            # Update CoursePdfInternal fields
            pdf_data_instance.name = instance.pdfs.name
            pdf_data_instance.table_of_contents = extracted_toc
            pdf_data_instance.save()  # Save name and toc

            # Delete old sections before creating new ones
            pdf_data_instance.sections.all().delete()

            # Create CourseSection objects linked to pdf_data_instance
            for section_data in extracted_sections:
                CourseSection.objects.create(
                    pdf_data=pdf_data_instance,  # Link to the internal data object
                    title=section_data['title'],
                    content=section_data['content'],
                    order=section_data['order']
                )
            logger.info(f"Successfully processed and saved sections for course: {instance.title}")
        except Exception as e:
            logger.error(f"Error in process_course_pdf signal for course {instance.pk}: {e}", exc_info=True)
    