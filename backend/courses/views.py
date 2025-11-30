from django.db import transaction
from django.db.models import Max, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CourseStream, Topic, TopicSubmission
from .permissions import IsStudent, IsTeacher
from .serializers import MyStreamSerializer, TopicSerializer, TopicSubmissionSerializer, TopicSubmissionCreateSerializer, TopicCreateSerializer, TopicWithSubmissionsSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_streams(request):
    is_active_param = request.query_params.get('is_active', 'true').lower()
    is_active = is_active_param == 'true'
    
    streams = request.user.streams.filter(is_active=is_active)
    serializer = MyStreamSerializer(streams, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def get_stream_topics(request, stream_id):
    stream = get_object_or_404(CourseStream, id=stream_id)
    if request.user not in stream.users.all():
        return Response(
            {"detail": "Not authorized to view topics for this stream."},
            status=status.HTTP_403_FORBIDDEN,
        )

    topics = Topic.objects.filter(stream=stream, status=Topic.TopicStatus.AVAILABLE)
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsStudent])
def get_my_submissions(request):
    submissions = request.user.submissions.order_by('-created_at')
    serializer = TopicSubmissionSerializer(submissions, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def create_submission(request):
    serializer = TopicSubmissionCreateSerializer(data=request.data)
    if serializer.is_valid():
        topic_id = serializer.validated_data["topic_id"]
        student_vision = serializer.validated_data.get("student_vision", "")

        if not student_vision or not student_vision.strip():
            return Response({"detail": "The 'student_vision' field cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        topic = get_object_or_404(Topic, id=topic_id)
        student = request.user

        if student not in topic.stream.users.all():
            return Response(
                {"detail": "You are not enrolled in the stream for this topic."},
                status=status.HTTP_403_FORBIDDEN,
            )

        existing_submissions = TopicSubmission.objects.filter(
            student=student,
            topic__stream=topic.stream,
            status__in=[TopicSubmission.SubmissionStatus.PENDING, TopicSubmission.SubmissionStatus.APPROVED],
        ).exists()

        if existing_submissions:
            return Response(
                {
                    "detail": "You already have a pending or approved submission in this stream."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission = TopicSubmission.objects.create(
            student=student, 
            topic=topic,
            student_vision=student_vision
        )
        response_serializer = TopicSubmissionSerializer(submission)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsStudent])
def cancel_submission(request, submission_id):
    submission = get_object_or_404(
        TopicSubmission, id=submission_id, student=request.user
    )
    if submission.status != TopicSubmission.SubmissionStatus.PENDING:
        return Response(
            {"detail": "Only PENDING submissions can be canceled."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    submission.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def get_my_topics(request):
    is_active_param = request.query_params.get('is_active', 'true').lower()
    is_active = is_active_param == 'true'

    topics = request.user.topics.filter(stream__is_active=is_active)
    serializer = TopicSerializer(topics, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def create_topic(request):
    serializer = TopicCreateSerializer(data=request.data)
    if serializer.is_valid():
        stream_id = serializer.validated_data["stream_id"]
        stream = get_object_or_404(CourseStream, id=stream_id)
        teacher = request.user

        if teacher not in stream.users.all():
            return Response(
                {"detail": "You are not assigned to this stream."},
                status=status.HTTP_403_FORBIDDEN,
            )

        topic = Topic.objects.create(
            teacher=teacher,
            stream=stream,
            title=serializer.validated_data["title"],
            description=serializer.validated_data["description"],
        )
        response_serializer = TopicSerializer(topic)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsTeacher])
def update_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id, teacher=request.user)
    serializer = TopicCreateSerializer(topic, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        response_serializer = TopicSerializer(topic)
        return Response(response_serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsTeacher])
def delete_topic(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id, teacher=request.user)
    if topic.submissions.exists():
        return Response(
            {"detail": "Cannot delete a topic that has submissions."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    topic.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsTeacher])
def get_received_submissions(request):
    prefetch_submissions = Prefetch(
        'submissions',
        queryset=TopicSubmission.objects.order_by('-created_at').select_related('student'),
    )

    topics_with_submissions = Topic.objects.filter(
        teacher=request.user,
        submissions__isnull=False
    ).annotate(
        latest_submission_date=Max('submissions__created_at')
    ).distinct().prefetch_related(
        prefetch_submissions
    ).order_by('-latest_submission_date')

    serializer = TopicWithSubmissionsSerializer(topics_with_submissions, many=True)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def approve_submission(request, submission_id):
    submission = get_object_or_404(
        TopicSubmission, id=submission_id, topic__teacher=request.user
    )
    if submission.status != TopicSubmission.SubmissionStatus.PENDING:
        return Response(
            {"detail": "This submission is not pending approval."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    topic = submission.topic

    with transaction.atomic():
        submission.status = TopicSubmission.SubmissionStatus.APPROVED
        submission.save()

        topic.status = Topic.TopicStatus.TAKEN
        topic.save()

        TopicSubmission.objects.filter(
            topic=topic, status=TopicSubmission.SubmissionStatus.PENDING
        ).update(status=TopicSubmission.SubmissionStatus.REJECTED)

    serializer = TopicSubmissionSerializer(submission)
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsTeacher])
def reject_submission(request, submission_id):
    submission = get_object_or_404(
        TopicSubmission, id=submission_id, topic__teacher=request.user
    )

    if submission.status != TopicSubmission.SubmissionStatus.PENDING:
        return Response(
            {"detail": "This submission is not pending rejection."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    submission.status = TopicSubmission.SubmissionStatus.REJECTED
    submission.save()
    serializer = TopicSubmissionSerializer(submission)
    return Response(serializer.data)