from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, ResumeData, InterviewAnalysis
from .serializers import UserProfileSerializer, ResumeDataSerializer, InterviewAnalysisSerializer
from .resume_parser import parse_resume
from .gemini_analyzer import get_interview_recommendations, analyze_interview_recording
from .question_generator import generate_interview_questions
import json


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def create_profile(request):
    """Create a new user profile"""
    try:
        data = request.data
        
        # Check if user already exists
        if UserProfile.objects.filter(uid=data.get('uid')).exists():
            return Response({
                'message': 'Profile already exists',
                'profile': UserProfileSerializer(UserProfile.objects.get(uid=data.get('uid'))).data
            }, status=status.HTTP_200_OK)
        
        # Create new profile
        serializer = UserProfileSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile created successfully',
                'profile': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile(request):
    """Get user profile by Firebase UID"""
    try:
        # Get UID from query params or request headers
        uid = request.GET.get('uid') or request.headers.get('X-User-UID')
        
        if not uid:
            return Response({
                'error': 'UID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            profile = UserProfile.objects.get(uid=uid)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def upload_resume(request):
    """Upload and parse resume - NO cloud storage needed, just extract and save data"""
    try:
        uid = request.data.get('uid') or request.headers.get('X-User-UID')
        
        if not uid:
            return Response({
                'error': 'UID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user exists
        try:
            user = UserProfile.objects.get(uid=uid)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get uploaded file
        if 'file' not in request.FILES:
            return Response({
                'error': 'No file uploaded'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        
        # Parse resume and extract all important data
        # We don't store the file, just the extracted information!
        parsed_data = parse_resume(uploaded_file, uploaded_file.name)
        
        # Debug: Print parsed name
        print(f"Parsed name: {parsed_data.get('full_name')}")
        print(f"Parsed email: {parsed_data.get('email')}")
        print(f"Skills count: {len(parsed_data.get('skills', []))}")
        
        # Update or create resume data in SQLite
        resume_data, created = ResumeData.objects.update_or_create(
            user=user,
            defaults=parsed_data
        )
        
        serializer = ResumeDataSerializer(resume_data)
        
        return Response({
            'message': 'Resume analyzed and data saved successfully',
            'resume': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_resume(request):
    """Get resume data by user UID"""
    try:
        uid = request.GET.get('uid') or request.headers.get('X-User-UID')
        
        if not uid:
            return Response({
                'error': 'UID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserProfile.objects.get(uid=uid)
            resume_data = ResumeData.objects.get(user=user)
            serializer = ResumeDataSerializer(resume_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except ResumeData.DoesNotExist:
            return Response({
                'error': 'Resume not found'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_recommendations(request):
    """Get AI-powered interview recommendations based on resume data"""
    try:
        uid = request.GET.get('uid') or request.headers.get('X-User-UID')
        
        if not uid:
            return Response({
                'error': 'UID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserProfile.objects.get(uid=uid)
            resume_data = ResumeData.objects.get(user=user)
            
            # Convert resume data to dict for analysis
            resume_dict = {
                'full_name': resume_data.full_name,
                'email': resume_data.email,
                'skills': resume_data.skills,
                'experience': resume_data.experience,
                'education': resume_data.education,
                'projects': resume_data.projects,
                'certifications': resume_data.certifications,
                'years_of_experience': resume_data.years_of_experience,
                'key_strengths': resume_data.key_strengths,
            }
            
            # Get AI recommendations
            recommendations = get_interview_recommendations(resume_dict)
            
            return Response({
                'recommendations': recommendations,
                'resume_summary': {
                    'name': resume_data.full_name,
                    'years_experience': resume_data.years_of_experience,
                    'skills_count': len(resume_data.skills),
                    'projects_count': len(resume_data.projects),
                    'key_strengths': resume_data.key_strengths
                }
            }, status=status.HTTP_200_OK)
            
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except ResumeData.DoesNotExist:
            return Response({
                'error': 'Resume not found. Please upload your resume first.'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def generate_questions(request):
    """Generate interview questions based on configuration and resume"""
    try:
        data = request.data
        uid = data.get('uid')
        goal = data.get('goal')  # full, focused, quick
        target_level = data.get('level')  # entry, mid, etc.
        domain = data.get('domain')  # dsa, web, ml, core
        
        if not all([uid, goal, target_level, domain]):
            return Response({
                'error': 'Missing required parameters (uid, goal, level, domain)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's resume data for personalization
        resume_dict = None
        try:
            user = UserProfile.objects.get(uid=uid)
            resume_data = ResumeData.objects.get(user=user)
            
            resume_dict = {
                'full_name': resume_data.full_name,
                'years_of_experience': resume_data.years_of_experience,
                'skills': resume_data.skills,
                'key_strengths': resume_data.key_strengths,
                'projects': resume_data.projects,
            }
        except (UserProfile.DoesNotExist, ResumeData.DoesNotExist):
            print("No resume data found, generating generic questions")
        
        # Generate questions using AI
        questions = generate_interview_questions(goal, target_level, domain, resume_dict)
        
        return Response({
            'questions': questions,
            'total': len(questions),
            'config': {
                'goal': goal,
                'level': target_level,
                'domain': domain
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def analyze_interview(request):
    """
    POST /api/interview/analyze/
    
    Analyzes an uploaded interview recording (video/audio) using Gemini AI.
    Generates:
    1. Personal performance analysis (emotion, confidence, communication)
    2. Integrity/behavioral indicators (eye movement, attention, risk assessment)
    3. Relative ranking among participants
    
    Request:
        - uid: Firebase user ID (query param or header X-User-UID)
        - recording: Video/audio file upload
        - participant_count: Number of participants in recording (optional, default: 1)
    
    Response:
        - analysis: Complete analysis object
        - analysis_id: ID of saved analysis record
    """
    try:
        # Get user UID from request
        uid = request.data.get('uid') or request.headers.get('X-User-UID')
        
        if not uid:
            return Response({
                'error': 'UID is required (provide in body as uid or header as X-User-UID)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate user exists
        try:
            user = UserProfile.objects.get(uid=uid)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found. Please create a profile first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get uploaded recording file
        if 'recording' not in request.FILES:
            return Response({
                'error': 'No recording file uploaded. Please upload a video or audio file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        recording_file = request.FILES['recording']
        
        # Validate file type (video or audio)
        allowed_types = ['video/mp4', 'video/webm', 'video/avi', 'audio/mp3', 'audio/wav', 'audio/mpeg', 'audio/webm']
        if recording_file.content_type not in allowed_types:
            return Response({
                'error': f'Invalid file type: {recording_file.content_type}. Allowed: video (mp4, webm, avi) or audio (mp3, wav, mpeg).'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get participant count (default to 1 for solo interview)
        participant_count = int(request.data.get('participant_count', 1))
        if participant_count < 1:
            participant_count = 1
        
        print(f"🎬 Analyzing interview for user: {user.name} ({user.email})")
        print(f"   File: {recording_file.name} ({recording_file.size} bytes)")
        print(f"   Participants: {participant_count}")
        
        # Analyze recording using Gemini AI
        analysis_result = analyze_interview_recording(recording_file, participant_count)
        
        # Check for errors in analysis
        if 'error' in analysis_result:
            return Response({
                'error': analysis_result['error']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Extract analysis components
        personal_report = analysis_result.get('personal_report', {})
        integrity_analysis = analysis_result.get('integrity_analysis', {})
        ranking = analysis_result.get('ranking', {})
        
        # Save analysis to database
        interview_analysis = InterviewAnalysis.objects.create(
            user=user,
            recording_filename=recording_file.name,
            recording_duration_seconds=0,  # Could extract from file metadata if needed
            
            # Personal report
            emotion_trend=personal_report.get('emotion_trend', ''),
            confidence_score=personal_report.get('confidence_score', 0),
            communication_analysis=personal_report.get('communication', ''),
            strengths=personal_report.get('strengths', []),
            improvements=personal_report.get('improvements', []),
            
            # Integrity analysis
            eye_movement_pattern=integrity_analysis.get('eye_movement', ''),
            attention_level=integrity_analysis.get('attention_level', ''),
            suspicion_risk=integrity_analysis.get('suspicion_risk', ''),
            integrity_notes=integrity_analysis.get('notes', ''),
            
            # Ranking
            ranking_position=ranking.get('position', 1),
            total_participants=ranking.get('total_participants', participant_count),
            percentile_band=ranking.get('percentile', ''),
            
            # Store raw response for debugging
            raw_ai_response=analysis_result
        )
        
        serializer = InterviewAnalysisSerializer(interview_analysis)
        
        print(f"✅ Analysis saved with ID: {interview_analysis.id}")
        print(f"   Confidence: {interview_analysis.confidence_score}/100")
        print(f"   Suspicion Risk: {interview_analysis.suspicion_risk}")
        print(f"   Ranking: {interview_analysis.ranking_position}/{interview_analysis.total_participants}")
        
        return Response({
            'message': 'Interview analysis completed successfully',
            'analysis_id': interview_analysis.id,
            'analysis': {
                'personal_report': {
                    'emotion_trend': interview_analysis.emotion_trend,
                    'confidence_score': interview_analysis.confidence_score,
                    'communication': interview_analysis.communication_analysis,
                    'strengths': interview_analysis.strengths,
                    'improvements': interview_analysis.improvements
                },
                'integrity_analysis': {
                    'eye_movement': interview_analysis.eye_movement_pattern,
                    'attention_level': interview_analysis.attention_level,
                    'suspicion_risk': interview_analysis.suspicion_risk,
                    'notes': interview_analysis.integrity_notes
                },
                'ranking': {
                    'position': interview_analysis.ranking_position,
                    'total_participants': interview_analysis.total_participants,
                    'percentile': interview_analysis.percentile_band
                },
                'disclaimer': analysis_result.get('disclaimer', 'Behavioral insights only. Not a hiring decision.')
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ Error in analyze_interview endpoint: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Failed to analyze interview: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_interview_analysis(request, analysis_id):
    """
    GET /api/interview/analysis/<analysis_id>/
    
    Retrieve a specific interview analysis by ID.
    """
    try:
        analysis = InterviewAnalysis.objects.get(id=analysis_id)
        serializer = InterviewAnalysisSerializer(analysis)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except InterviewAnalysis.DoesNotExist:
        return Response({
            'error': 'Interview analysis not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_interview_analyses(request):
    """
    GET /api/interview/analyses/?uid=<uid>
    
    Retrieve all interview analyses for a specific user.
    """
    try:
        uid = request.GET.get('uid') or request.headers.get('X-User-UID')
        
        if not uid:
            return Response({
                'error': 'UID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserProfile.objects.get(uid=uid)
            analyses = InterviewAnalysis.objects.filter(user=user)
            serializer = InterviewAnalysisSerializer(analyses, many=True)
            return Response({
                'count': analyses.count(),
                'analyses': serializer.data
            }, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)