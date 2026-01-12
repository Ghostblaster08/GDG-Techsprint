from django.urls import path
from . import views

urlpatterns = [
    path('profile/create/', views.create_profile, name='create_profile'),
    path('profile/', views.get_profile, name='get_profile'),
    path('resume/upload/', views.upload_resume, name='upload_resume'),
    path('resume/', views.get_resume, name='get_resume'),
    path('recommendations/', views.get_recommendations, name='get_recommendations'),
    path('questions/generate/', views.generate_questions, name='generate_questions'),
    
    # Interview Analysis endpoints
    path('interview/analyze/', views.analyze_interview, name='analyze_interview'),
    path('interview/analysis/<int:analysis_id>/', views.get_interview_analysis, name='get_interview_analysis'),
    path('interview/analyses/', views.get_user_interview_analyses, name='get_user_interview_analyses'),
]
