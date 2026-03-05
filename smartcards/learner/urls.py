from django.urls import path
from . import views

app_name = "learner"
urlpatterns = [
    path("", views.menu, name="menu"),
    path("study/<path:subject>/", views.study, name="study"),   # existing flow
    path("flip/<path:subject>/", views.flip, name="flip"),      # NEW flipcard webapp
    # path("learner/api/notes/<slug:question_id>/", views.note_api, name="note_api"),
    path("api/notes/<str:question_id>/", views.note_api, name="note_api"),
]
