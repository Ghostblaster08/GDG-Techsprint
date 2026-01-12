from rest_framework import serializers
from .models import UserProfile, ResumeData, InterviewAnalysis


class ResumeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeData
        fields = '__all__'
        read_only_fields = ('user', 'uploaded_at', 'updated_at')


class InterviewAnalysisSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = InterviewAnalysis
        fields = '__all__'
        read_only_fields = ('user', 'analyzed_at')


class UserProfileSerializer(serializers.ModelSerializer):
    resume = ResumeDataSerializer(read_only=True, required=False)
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
