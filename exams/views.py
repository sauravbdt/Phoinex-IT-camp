from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from users.models import UserProfile

from .models import (
    MockTest,
    Section,
    Question,
    AnswerOption,
    AudioMaterial,
    ExamAnswer,
    ReadingPassage,
)


# =========================================================
# EXAMINER DASHBOARD
# =========================================================

@login_required
def examiner_dashboard(request):

    profile = UserProfile.objects.get(
        user=request.user
    )

    if profile.role != "examiner":
        return redirect("test_list")


    # =====================================================
    # CREATE MOCK TEST
    # =====================================================

    if request.method == "POST":

        title = request.POST.get(
            "title",
            ""
        ).strip()

        description = request.POST.get(
            "description",
            ""
        ).strip()

        duration = request.POST.get(
            "duration",
            "180"
        )


        if title:

            test = MockTest.objects.create(
                title=title,
                description=description,
                duration=int(duration)
            )

            return redirect(
                "test_detail",
                test_id=test.id
            )


    # =====================================================
    # SHOW MOCK TESTS
    # =====================================================

    tests = MockTest.objects.all().order_by(
        "-created_at"
    )


    return render(
        request,
        "exams/dashboard.html",
        {
            "tests": tests
        }
    )


# =========================================================
# PUBLISH / UNPUBLISH MOCK TEST
# =========================================================

@login_required
def toggle_publish_test(request, test_id):

    profile = UserProfile.objects.get(
        user=request.user
    )

    if profile.role != "examiner":
        return redirect("test_list")


    test = get_object_or_404(
        MockTest,
        id=test_id
    )


    if request.method == "POST":

        test.is_published = not test.is_published

        test.save()


    return redirect(
        "examiner_dashboard"
    )


# =========================================================
# TEST DETAIL / MANAGE TEST
# =========================================================

def test_detail(request, test_id):

    test = get_object_or_404(
        MockTest,
        id=test_id
    )

    sections = test.sections.all().order_by("order")

    return render(
        request,
        "exams/test_detail.html",
        {
            "test": test,
            "sections": sections,
        }
    )


# =========================================================
# SECTION DETAIL / MANAGE SECTION
# =========================================================

def section_detail(request, section_id):

    section = get_object_or_404(
        Section,
        id=section_id
    )


    # -----------------------------------------------------
    # SAVE READING PASSAGE
    # -----------------------------------------------------

    if request.method == "POST":

        if section.section_type == "reading":

            title = request.POST.get(
                "passage_title",
                ""
            ).strip()

            passage_text = request.POST.get(
                "passage",
                ""
            ).strip()

            passage_order = request.POST.get(
                "passage_order"
            )


            if title and passage_text and passage_order:

                try:

                    passage_order = int(
                        passage_order
                    )


                    ReadingPassage.objects.update_or_create(

                        section=section,

                        order=passage_order,

                        defaults={
                            "title": title,
                            "passage_text": passage_text,
                        }
                    )


                except ValueError:

                    pass


            return redirect(
                "section_detail",
                section_id=section.id
            )


    # -----------------------------------------------------
    # QUESTIONS
    # -----------------------------------------------------

    questions = (
        section.questions
        .all()
        .order_by("order")
    )


    # -----------------------------------------------------
    # READING PASSAGES
    # -----------------------------------------------------

    reading_passages = (
        section.reading_passages
        .all()
        .order_by("order")
    )


    # -----------------------------------------------------
    # LISTENING AUDIO
    # -----------------------------------------------------

    audio_files = section.audio_files.all()


    return render(
        request,
        "exams/section_detail.html",
        {
            "section": section,
            "questions": questions,
            "audio_files": audio_files,
            "reading_passages": reading_passages,
        }
    )


# =========================================================
# ADD QUESTION
# =========================================================

def add_question(request, section_id):

    section = get_object_or_404(
        Section,
        id=section_id
    )


    reading_passages = (
        section.reading_passages
        .all()
        .order_by("order")
    )


    if request.method == "POST":

        question_text = request.POST.get(
            "question_text",
            ""
        ).strip()

        question_type = request.POST.get(
            "question_type",
            ""
        ).strip()


        # -------------------------------------------------
        # CORRECT ANSWER
        # -------------------------------------------------

        correct_answer = request.POST.get(
            "correct_answer",
            ""
        ).strip()


        marks = request.POST.get(
            "marks",
            1
        )


        order = request.POST.get(
            "order",
            1
        )


        reading_passage_id = request.POST.get(
            "reading_passage"
        )


        # -------------------------------------------------
        # READING PASSAGE
        # -------------------------------------------------

        reading_passage = None


        if section.section_type == "reading":

            if reading_passage_id:

                reading_passage = get_object_or_404(
                    ReadingPassage,
                    id=reading_passage_id,
                    section=section
                )


        # -------------------------------------------------
        # CREATE QUESTION
        # -------------------------------------------------

        question = Question.objects.create(

            section=section,

            reading_passage=reading_passage,

            question_text=question_text,

            correct_answer=correct_answer,

            question_type=question_type,

            marks=int(marks),

            order=int(order)

        )


        # -------------------------------------------------
        # MCQ OPTIONS
        # -------------------------------------------------

        if question_type == "mcq":

            options = request.POST.getlist(
                "options"
            )


            correct_option = request.POST.get(
                "correct_option"
            )


            for index, option_text in enumerate(
                options
            ):

                option_text = option_text.strip()


                if option_text:

                    AnswerOption.objects.create(

                        question=question,

                        option_text=option_text,

                        is_correct=(
                            str(index)
                            == str(correct_option)
                        )

                    )


        # -------------------------------------------------
        # REDIRECT
        # -------------------------------------------------

        return redirect(
            "section_detail",
            section_id=section.id
        )


    # -----------------------------------------------------
    # SHOW ADD QUESTION PAGE
    # -----------------------------------------------------

    return render(
        request,
        "exams/add_question.html",
        {
            "section": section,
            "reading_passages": reading_passages,
        }
    )


# =========================================================
# UPLOAD LISTENING AUDIO
# =========================================================

def upload_audio(request, section_id):

    section = get_object_or_404(
        Section,
        id=section_id
    )


    if section.section_type != "listening":

        return redirect(
            "section_detail",
            section_id=section.id
        )


    if request.method == "POST":

        audio_file = request.FILES.get(
            "audio_file"
        )


        title = request.POST.get(
            "title"
        )


        if audio_file:

            AudioMaterial.objects.create(

                section=section,

                title=title or audio_file.name,

                audio_file=audio_file

            )


        return redirect(
            "section_detail",
            section_id=section.id
        )


    return redirect(
        "section_detail",
        section_id=section.id
    )


# =========================================================
# TEST LIST
# =========================================================

def test_list(request):

    tests = (
        MockTest.objects
        .filter(is_published=True)
        .order_by("-created_at")
    )


    return render(
        request,
        "exams/test_list.html",
        {
            "tests": tests
        }
    )


# =========================================================
# TEST START
# =========================================================

def test_start(request, test_id):

    test = get_object_or_404(
        MockTest,
        id=test_id,
        is_published=True
    )


    sections = (
        test.sections
        .all()
        .order_by("order")
    )


    return render(
        request,
        "exams/test_start.html",
        {
            "test": test,
            "sections": sections,
        }
    )


# =========================================================
# TAKE TEST
# =========================================================

def take_test(request, test_id):

    test = get_object_or_404(
        MockTest,
        id=test_id,
        is_published=True
    )


    # -----------------------------------------------------
    # START / CONTINUE EXAM SESSION
    # -----------------------------------------------------

    session_test_id = request.session.get(
        "exam_test_id"
    )


    exam_start_time = request.session.get(
        "exam_start_time"
    )


    exam_section_index = request.session.get(
        "exam_section_index"
    )


    # -----------------------------------------------------
    # START NEW EXAM SESSION
    # -----------------------------------------------------

    if (
        session_test_id != test.id
        or not exam_start_time
        or exam_section_index is None
    ):

        request.session["exam_test_id"] = test.id


        request.session["exam_start_time"] = (
            timezone.now().timestamp()
        )


        request.session["exam_section_index"] = 0


        exam_start_time = request.session[
            "exam_start_time"
        ]


        exam_section_index = 0


    # -----------------------------------------------------
    # GET SECTIONS
    # -----------------------------------------------------

    sections = list(
        test.sections
        .all()
        .order_by("order")
    )


    # -----------------------------------------------------
    # CHECK SECTION EXISTS
    # -----------------------------------------------------

    if not sections:

        return render(
            request,
            "exams/take_test.html",
            {
                "test": test,
                "sections": [],
                "current_section": None,
                "exam_start_time": exam_start_time,
            }
        )


    # -----------------------------------------------------
    # MAKE SURE INDEX IS VALID
    # -----------------------------------------------------

    if exam_section_index >= len(sections):

        exam_section_index = (
            len(sections) - 1
        )


        request.session[
            "exam_section_index"
        ] = exam_section_index


    # -----------------------------------------------------
    # CURRENT SECTION
    # -----------------------------------------------------

    current_section = sections[
        exam_section_index
    ]


    current_section.exam_questions = (
        current_section.questions
        .all()
        .order_by("order")
    )


    current_section.exam_passages = (
        current_section.reading_passages
        .all()
        .order_by("order")
    )


    # -----------------------------------------------------
    # SAVE ANSWERS / MOVE NEXT
    # -----------------------------------------------------

    if request.method == "POST":

        if not request.session.session_key:

            request.session.create()


        session_key = (
            request.session.session_key
        )


        # -------------------------------------------------
        # SAVE CURRENT SECTION ANSWERS
        # -------------------------------------------------

        for question in current_section.exam_questions:

            field_name = (
                f"question_{question.id}"
            )


            submitted_answer = request.POST.get(
                field_name,
                ""
            )


            is_correct = False


            # ---------------------------------------------
            # MCQ
            # ---------------------------------------------

            if question.question_type == "mcq":

                try:

                    selected_option = (
                        AnswerOption.objects.get(
                            id=submitted_answer,
                            question=question
                        )
                    )


                    is_correct = (
                        selected_option.is_correct
                    )


                except AnswerOption.DoesNotExist:

                    is_correct = False


            # ---------------------------------------------
            # TRUE / FALSE
            # ---------------------------------------------

            elif question.question_type == "true_false":

                is_correct = False


            # ---------------------------------------------
            # SAVE ANSWER
            # ---------------------------------------------

            ExamAnswer.objects.update_or_create(

                test=test,

                question=question,

                session_key=session_key,

                defaults={
                    "answer": submitted_answer,
                    "is_correct": is_correct,
                }

            )


        # -------------------------------------------------
        # LAST SECTION
        # -------------------------------------------------

        if exam_section_index >= len(sections) - 1:

            return redirect(
                "test_result",
                test_id=test.id
            )


        # -------------------------------------------------
        # NEXT SECTION
        # -----------------------------------------------------

        exam_section_index += 1


        request.session[
            "exam_section_index"
        ] = exam_section_index


        # -------------------------------------------------
        # RESET SECTION TIMER
        # -------------------------------------------------

        request.session[
            "exam_start_time"
        ] = timezone.now().timestamp()


        return redirect(
            "take_test",
            test_id=test.id
        )


    # -----------------------------------------------------
    # SHOW CURRENT SECTION
    # -----------------------------------------------------

    return render(
        request,
        "exams/take_test.html",
        {
            "test": test,
            "sections": sections,
            "current_section": current_section,
            "exam_start_time": exam_start_time,
            "exam_section_index": exam_section_index,
            "total_sections": len(sections),
        }
    )


# =========================================================
# TEST RESULT
# =========================================================

def test_result(request, test_id):

    test = get_object_or_404(
        MockTest,
        id=test_id,
        is_published=True
    )


    if not request.session.session_key:

        return redirect(
            "test_start",
            test_id=test.id
        )


    session_key = (
        request.session.session_key
    )


    answers = (
        ExamAnswer.objects
        .filter(
            test=test,
            session_key=session_key
        )
        .select_related("question")
    )


    total_marks = 0

    obtained_marks = 0


    for answer in answers:

        total_marks += (
            answer.question.marks
        )


        if answer.is_correct:

            obtained_marks += (
                answer.question.marks
            )


    return render(
        request,
        "exams/test_result.html",
        {
            "test": test,
            "answers": answers,
            "total_marks": total_marks,
            "obtained_marks": obtained_marks,
        }
    )