from django.urls import path

from . import views


urlpatterns = [

    # =====================================================
    # EXAMINER
    # =====================================================

    path(
    "test/<int:test_id>/toggle-publish/",
    views.toggle_publish_test,
    name="toggle_publish_test"
    ),
    path(
        "",
        views.examiner_dashboard,
        name="examiner_dashboard"
    ),

    path(
        "create-mock-test/",
        views.examiner_dashboard,
        name="create_mock_test"
    ),

    path(
        "test/<int:test_id>/",
        views.test_detail,
        name="test_detail"
    ),

    path(
        "section/<int:section_id>/",
        views.section_detail,
        name="section_detail"
    ),

    path(
        "section/<int:section_id>/add-question/",
        views.add_question,
        name="add_question"
    ),

    path(
        "section/<int:section_id>/upload-audio/",
        views.upload_audio,
        name="upload_audio"
    ),


    # =====================================================
    # EXAM-TAKER
    # =====================================================

    path(
        "tests/",
        views.test_list,
        name="test_list"
    ),

    path(
        "tests/<int:test_id>/start/",
        views.test_start,
        name="test_start"
    ),

    path(
        "tests/<int:test_id>/take/",
        views.take_test,
        name="take_test"
    ),

    path(
        "tests/<int:test_id>/result/",
        views.test_result,
        name="test_result"
    ),
    

    

]