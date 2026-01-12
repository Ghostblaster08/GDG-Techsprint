from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    """
    User profile model that stores information from Firebase authentication
    and additional profile data
    """
    uid = models.CharField(max_length=255, unique=True, primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email})"


class ResumeData(models.Model):
    """
    Resume data model that stores parsed information from uploaded resumes
    """
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='resume')
    
    # Personal Information
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Professional Summary
    summary = models.TextField(blank=True, null=True)
    
    # Experience (stored as JSON)
    experience = models.JSONField(default=list, blank=True)
    
    # Education (stored as JSON)
    education = models.JSONField(default=list, blank=True)
    
    # Skills
    skills = models.JSONField(default=list, blank=True)
    
    # Projects (stored as JSON)
    projects = models.JSONField(default=list, blank=True)
    
    # Certifications (stored as JSON)
    certifications = models.JSONField(default=list, blank=True)
    
    # Languages
    languages = models.JSONField(default=list, blank=True)
    
    # Additional AI-extracted fields
    years_of_experience = models.IntegerField(default=0, blank=True, null=True)
    key_strengths = models.JSONField(default=list, blank=True)
    
    # Raw text from resume
    raw_text = models.TextField(blank=True, null=True)
    
    # File info
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resume_data'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Resume of {self.user.name}"


class InterviewAnalysis(models.Model):
    """
    Post-interview analysis with AI-powered performance insights and integrity detection
    """
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='interview_analyses')
    
    # File information (not permanently stored, just metadata)
    recording_filename = models.CharField(max_length=255, blank=True, null=True)
    recording_duration_seconds = models.IntegerField(default=0)
    
    # Personal Performance Report
    emotion_trend = models.TextField(blank=True, null=True, help_text="Emotional pattern observed throughout the interview")
    confidence_score = models.IntegerField(default=0, help_text="Confidence level 0-100")
    communication_analysis = models.TextField(blank=True, null=True, help_text="Analysis of communication clarity and style")
    strengths = models.JSONField(default=list, blank=True, help_text="List of observed strengths")
    improvements = models.JSONField(default=list, blank=True, help_text="List of suggested improvements")
    
    # Integrity Analysis (behavioral indicators only, not deterministic)
    eye_movement_pattern = models.TextField(blank=True, null=True, help_text="Observed eye movement behavior")
    attention_level = models.CharField(max_length=50, blank=True, null=True, help_text="low, moderate, or high")
    suspicion_risk = models.CharField(max_length=50, blank=True, null=True, help_text="low, medium, or high")
    integrity_notes = models.TextField(blank=True, null=True, help_text="Behavioral observations")
    
    # Relative Ranking (among participants on the call)
    ranking_position = models.IntegerField(default=0, help_text="Position among participants")
    total_participants = models.IntegerField(default=1, help_text="Total participants analyzed")
    percentile_band = models.CharField(max_length=50, blank=True, null=True, help_text="Performance percentile")
    
    # Raw AI response for debugging
    raw_ai_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    analyzed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'interview_analyses'
        ordering = ['-analyzed_at']
        verbose_name_plural = 'Interview Analyses'
    
    def __str__(self):
        return f"Interview Analysis for {self.user.name} on {self.analyzed_at.strftime('%Y-%m-%d')}"

