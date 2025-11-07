from rest_framework import serializers
from .models import CourseStream, Topic, TopicSubmission, Specialty
from users.models import User


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name', 'email')


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = ('code', 'name')


class MyStreamSerializer(serializers.ModelSerializer):
    specialty = SpecialtySerializer(read_only=True)

    class Meta:
        model = CourseStream
        fields = ('id', 'name', 'is_active', 'specialty', 'academic_year', 'semester', 'course_number')


class CourseStreamDetailSerializer(serializers.ModelSerializer):
    specialty = SpecialtySerializer(read_only=True)

    class Meta:
        model = CourseStream
        fields = (
            'id', 
            'name', 
            'academic_year', 
            'semester', 
            'course_number', 
            'specialty', 
            'is_active'
        )


class TopicStreamSerializer(serializers.ModelSerializer):
     class Meta:
        model = CourseStream
        fields = ('id', 'name',)


class TopicSerializer(serializers.ModelSerializer):
    teacher = UserSimpleSerializer(read_only=True)
    stream = MyStreamSerializer(read_only=True)

    class Meta:
        model = Topic
        fields = ('id', 'title', 'description', 'status', 'teacher', 'stream')
        read_only_fields = ('status', 'teacher')


class TopicCreateSerializer(serializers.ModelSerializer):
    stream_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Topic
        fields = ('title', 'description', 'stream_id')


class SubmissionTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('title', 'description')


class TopicSubmissionSerializer(serializers.ModelSerializer):
    topic = TopicSerializer(read_only=True)
    student = UserSimpleSerializer(read_only=True)

    class Meta:
        model = TopicSubmission
        fields = ('id', 'status', 'topic', 'student', 'student_vision', 'created_at')


class TopicWithSubmissionsSerializer(TopicSerializer):
    submissions = TopicSubmissionSerializer(many=True, read_only=True)

    class Meta(TopicSerializer.Meta):
        fields = TopicSerializer.Meta.fields + ('submissions',)


class TopicSubmissionCreateSerializer(serializers.ModelSerializer):
    topic_id = serializers.IntegerField(write_only=True)
    student_vision = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = TopicSubmission
        fields = ('topic_id', 'student_vision')