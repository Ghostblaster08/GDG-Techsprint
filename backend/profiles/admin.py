from django.contrib import admin
from .models import UserProfile, ResumeData, InterviewAnalysis


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name', 'email', 'created_at')
    search_fields = ('name', 'email', 'uid')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ResumeData)
class ResumeDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'file_name', 'uploaded_at')
    search_fields = ('full_name', 'email', 'user__email')
    list_filter = ('uploaded_at',)
    readonly_fields = ('uploaded_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'email', 'phone', 'location')
        }),
        ('Professional Links', {
            'fields': ('linkedin', 'github', 'website')
        }),
        ('Resume Data', {
            'fields': ('summary', 'skills', 'experience', 'education', 'projects', 'certifications', 'languages')
        }),
        ('File Information', {
            'fields': ('file_name', 'file_url', 'uploaded_at', 'updated_at')
        }),
        ('Raw Data', {
            'fields': ('raw_text',),
            'classes': ('collapse',)
        }),
    )


@admin.register(InterviewAnalysis)
class InterviewAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'confidence_score', 'suspicion_risk', 'ranking_position', 'total_participants', 'analyzed_at')
    search_fields = ('user__name', 'user__email')
    list_filter = ('analyzed_at', 'suspicion_risk', 'attention_level')
    readonly_fields = ('analyzed_at',)
    
    fieldsets = (
        ('User & File Info', {
            'fields': ('user', 'recording_filename', 'recording_duration_seconds', 'analyzed_at')
        }),
        ('Performance Analysis', {
            'fields': ('emotion_trend', 'confidence_score', 'communication_analysis', 'strengths', 'improvements')
        }),
        ('Integrity Analysis', {
            'fields': ('eye_movement_pattern', 'attention_level', 'suspicion_risk', 'integrity_notes')
        }),
        ('Ranking', {
            'fields': ('ranking_position', 'total_participants', 'percentile_band')
        }),
        ('Raw AI Response', {
            'fields': ('raw_ai_response',),
            'classes': ('collapse',)
        }),
    )

