from django.urls import path
from . import views


urlpatterns = [
    path("streams/my/", views.get_my_streams, name="my-streams"),
    path("streams/<int:stream_id>/topics/", views.get_stream_topics, name="stream-topics"),

    path("topics/my/", views.get_my_topics, name="my-topics"),
    path("topics/", views.create_topic, name="create-topic"),
    path("topics/<int:topic_id>/", views.update_topic, name="update-topic"),
    path("topics/<int:topic_id>/delete/", views.delete_topic, name="delete-topic"),

    path("submissions/my/", views.get_my_submissions, name="my-submissions"),
    path("submissions/", views.create_submission, name="create-submission"),
    path("submissions/<int:submission_id>/", views.cancel_submission, name="cancel-submission"),
    path("submissions/received/", views.get_received_submissions, name="received-submissions"),
    path("submissions/<int:submission_id>/approve/", views.approve_submission, name="approve-submission"),
    path("submissions/<int:submission_id>/reject/", views.reject_submission, name="reject-submission")
]