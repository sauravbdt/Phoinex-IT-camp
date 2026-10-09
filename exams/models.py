from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# =========================================================
# MOCK TEST
# =========================================================

class MockTest(models.Model):

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    is_published = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title


# =========================================================
# SECTION
# =========================================================

class Section(models.Model):

    SECTION_TYPES = [
        ("listening", "Listening"),
        ("reading", "Reading"),
        ("writing", "Writing"),
        ("speaking", "Speaking"),
    ]

    test = models.ForeignKey(
        MockTest,
        on_delete=models.CASCADE,
        related_name="sections"
    )

    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPES
    )

    title = models.CharField(
        max_length=200
    )

    order = models.PositiveIntegerField(
        default=1
    )

    def __str__(self):
        return f"{self.test.title} - {self.title}"


# =========================================================
# READING PASSAGE
# =========================================================

class ReadingPassage(models.Model):

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="reading_passages"
    )

    title = models.CharField(
        max_length=200
    )

    passage_text = models.TextField()

    order = models.PositiveIntegerField(
        default=1
    )

    class Meta:

        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["section", "order"],
                name="unique_reading_passage_order"
            )
        ]

    def __str__(self):
        return f"{self.section.title} - {self.title}"


# =========================================================
# QUESTION
# =========================================================

class Question(models.Model):

    QUESTION_TYPES = [

        # Reading / Listening
        ("mcq", "Multiple Choice"),

        ("true_false", "True / False / Not Given"),

        ("fill_blank", "Fill in the Blank"),

        ("matching", "Matching"),

        ("short_answer", "Short Answer"),

        # Writing
        ("writing_task_1", "Writing Task 1"),

        ("writing_task_2", "Writing Task 2"),

        # General essay type
        ("essay", "Essay"),

        # Speaking
        ("speaking", "Speaking"),
    ]


    # -----------------------------------------------------
    # SECTION
    # -----------------------------------------------------

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="questions"
    )


    # -----------------------------------------------------
    # READING PASSAGE
    # -----------------------------------------------------
    # Only used for Reading questions.
    #
    # Nullable so Listening, Writing and Speaking
    # questions continue working normally.

    reading_passage = models.ForeignKey(
        ReadingPassage,
        on_delete=models.SET_NULL,
        related_name="questions",
        null=True,
        blank=True
    )


    # -----------------------------------------------------
    # QUESTION TEXT
    # -----------------------------------------------------

    question_text = models.TextField()


    # -----------------------------------------------------
    # CORRECT ANSWER
    # -----------------------------------------------------
    # Used for automatically checking objective questions
    # such as:
    #
    # True / False / Not Given
    # Fill in the Blank
    # Matching
    # Short Answer
    #
    # It can remain blank for:
    # MCQ
    # Writing
    # Speaking
    # Essay

    correct_answer = models.TextField(
        blank=True
    )


    # -----------------------------------------------------
    # WRITING TASK IMAGE
    # -----------------------------------------------------
    # Used for IELTS Writing Task 1 images such as:
    # charts, graphs, maps, tables and diagrams.
    #
    # Optional so existing questions continue working normally.

    task_image = models.ImageField(
        upload_to="writing/",
        null=True,
        blank=True
    )


    # -----------------------------------------------------
    # QUESTION TYPE
    # -----------------------------------------------------

    question_type = models.CharField(
        max_length=30,
        choices=QUESTION_TYPES
    )


    # -----------------------------------------------------
    # MARKS
    # -----------------------------------------------------

    marks = models.PositiveIntegerField(
        default=1
    )


    # -----------------------------------------------------
    # QUESTION ORDER
    # -----------------------------------------------------

    order = models.PositiveIntegerField(
        default=1
    )


    def __str__(self):

        return f"{self.section.title} - Question {self.order}"


# =========================================================
# ANSWER OPTION
# =========================================================

class AnswerOption(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options"
    )

    option_text = models.CharField(
        max_length=500
    )

    is_correct = models.BooleanField(
        default=False
    )

    def __str__(self):

        return self.option_text


# =========================================================
# LISTENING AUDIO
# =========================================================

class AudioMaterial(models.Model):

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="audio_files"
    )

    title = models.CharField(
        max_length=200
    )

    audio_file = models.FileField(
        upload_to="listening/"
    )

    def __str__(self):

        return self.title


# =========================================================
# EXAM ANSWER
# =========================================================

class ExamAnswer(models.Model):

    test = models.ForeignKey(
        MockTest,
        on_delete=models.CASCADE,
        related_name="exam_answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="exam_answers"
    )

    session_key = models.CharField(
        max_length=100
    )

    answer = models.TextField(
        blank=True
    )

    is_correct = models.BooleanField(
        default=False
    )

    submitted_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return f"{self.test.title} - Question {self.question.order}"


# =========================================================
# CREATE DEFAULT SECTIONS
# =========================================================

@receiver(post_save, sender=MockTest)
def create_default_sections(
    sender,
    instance,
    created,
    **kwargs
):

    if created:

        default_sections = [

            (
                "listening",
                "Listening Section",
                1
            ),

            (
                "reading",
                "Reading Section",
                2
            ),

            (
                "writing",
                "Writing Section",
                3
            ),

            (
                "speaking",
                "Speaking Section",
                4
            ),

        ]


        for (
            sec_type,
            sec_title,
            sec_order
        ) in default_sections:

            Section.objects.create(

                test=instance,

                section_type=sec_type,

                title=sec_title,

                order=sec_order,

            )