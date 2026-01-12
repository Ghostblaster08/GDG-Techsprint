import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def extract_name_from_resume(resume_text):
    """
    Use Gemini to extract the candidate's full name from resume text.
    Handles various resume formats accurately.
    """
    # Check if API key is configured
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        print("Gemini API key not configured, skipping AI extraction")
        return None
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
Extract ONLY the candidate's full name from this resume. 

RULES:
- Return ONLY the person's name (e.g., "John Smith" or "Maria Garcia")
- Do NOT include job titles, email addresses, or any other text
- Do NOT include words like "Resume", "CV", "Profile"
- If you see an email like "john.smith@email.com", extract "John Smith" from it
- Return the name in proper case (Capital Letters)

Resume text:
{resume_text[:3000]}

Candidate's Full Name:"""

        response = model.generate_content(prompt)
        name = response.text.strip()
        
        # Clean up the response
        name = name.replace('Full Name:', '').strip()
        name = name.replace('Name:', '').strip()
        
        return name if name and len(name) > 2 else None
        
    except Exception as e:
        print(f"Error extracting name with Gemini: {e}")
        return None


def get_interview_recommendations(resume_data):
    """
    Use Gemini to analyze resume data and recommend:
    1. Goal (Full Technical Interview / Focused Practice / Quick Mock)
    2. Target Level (Entry/Mid/Senior)
    3. Domain/Field
    """
    # Check if API key is configured
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        print("Gemini API key not configured, returning defaults")
        return {
            "goal": "Focused Practice",
            "target_level": "Entry Level",
            "domain": "Software Development",
            "reasoning": {
                "goal_reason": "API key not configured",
                "level_reason": "API key not configured",
                "domain_reason": "API key not configured"
            }
        }
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Prepare resume summary
        resume_summary = f"""
Resume Data:
- Name: {resume_data.get('full_name', 'N/A')}
- Email: {resume_data.get('email', 'N/A')}
- Skills: {', '.join(resume_data.get('skills', [])[:20])}
- Experience: {json.dumps(resume_data.get('experience', [])[:3], indent=2)}
- Education: {json.dumps(resume_data.get('education', []), indent=2)}
- Projects: {json.dumps(resume_data.get('projects', [])[:2], indent=2)}
- Certifications: {', '.join(resume_data.get('certifications', [])[:5])}
"""

        prompt = f"""
You are an expert career counselor and technical recruiter. Analyze the following resume data and provide recommendations.

{resume_summary}

Based on this resume, provide recommendations in the following JSON format:

{{
  "goal": "Full Technical Interview" or "Focused Practice" or "Quick Mock",
  "target_level": "Entry Level" or "Mid Level" or "Senior Level",
  "domain": "specific domain name like 'Full Stack Development', 'Data Science', 'Machine Learning', 'DevOps', 'Frontend Development', 'Backend Development', 'Mobile Development', etc.",
  "reasoning": {{
    "goal_reason": "brief explanation for goal recommendation",
    "level_reason": "brief explanation for level recommendation",
    "domain_reason": "brief explanation for domain recommendation"
  }}
}}

RULES:
1. For "goal":
   - Recommend "Full Technical Interview" if candidate has 2+ years experience or multiple projects
   - Recommend "Focused Practice" if candidate has 0-2 years experience or specific skill gaps
   - Recommend "Quick Mock" if candidate is a fresher or student with limited experience

2. For "target_level":
   - "Entry Level": 0-2 years experience, recent graduate, or student
   - "Mid Level": 2-5 years experience, multiple projects, diverse skills
   - "Senior Level": 5+ years experience, leadership roles, advanced skills

3. For "domain":
   - Identify the PRIMARY technical domain based on skills and experience
   - Use standard industry terms

Return ONLY the JSON object, no other text.
"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Extract JSON from response (remove markdown if present)
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        recommendations = json.loads(result_text)
        return recommendations
        
    except Exception as e:
        print(f"Error getting recommendations with Gemini: {e}")
        # Return default recommendations
        return {
            "goal": "Focused Practice",
            "target_level": "Entry Level",
            "domain": "Software Development",
            "reasoning": {
                "goal_reason": "Default recommendation",
                "level_reason": "Default recommendation",
                "domain_reason": "Default recommendation"
            }
        }


def extract_all_resume_data(resume_text, email=None):
    """
    Use Gemini AI to extract ALL information from resume in one comprehensive call.
    Returns complete structured data ready for database storage.
    """
    # Check if API key is configured
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        print("Gemini API key not configured, using fallback extraction")
        return None
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
You are an expert resume parser. Extract ALL information from this resume and return as valid JSON.

CRITICAL: Return ONLY valid JSON. No markdown, no explanation, no code blocks.

Extract the following:

{{
  "full_name": "candidate's full name (First Last format)",
  "email": "email address from resume or '{email}'",
  "phone": "phone number",
  "location": "city, country",
  "linkedin": "LinkedIn URL if present",
  "github": "GitHub URL if present", 
  "website": "personal website URL if present",
  
  "summary": "professional summary or objective (2-3 sentences describing their career goals/profile)",
  "years_of_experience": 0,
  
  "skills": ["skill1", "skill2", "skill3"],
  
  "education": [
    {{
      "degree": "full degree name (e.g., Bachelor of Technology in Computer Science)",
      "institution": "university/college name",
      "year": "graduation year or expected year"
    }}
  ],
  
  "experience": [
    {{
      "title": "job title or position",
      "company": "company/organization name",
      "duration": "time period (e.g., Jan 2023 - Present)",
      "description": "key responsibilities and achievements"
    }}
  ],
  
  "projects": [
    {{
      "name": "project name",
      "description": "what the project does and your role",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  
  "certifications": ["certification name 1", "certification name 2"],
  
  "languages": ["English", "Hindi"],
  
  "key_strengths": ["strength 1", "strength 2", "strength 3"]
}}

RULES:
- full_name: Extract the person's actual name, NOT job titles or skills
- If email is in resume, use it; otherwise use '{email}'
- summary: Write a professional 2-3 sentence summary if not explicitly stated
- years_of_experience: Calculate based on work history (0 if student/fresher)
- skills: List ALL technical skills, tools, languages, frameworks
- education: Include ALL degrees (high school, bachelor's, master's, etc.)
- experience: Include internships, jobs, volunteer work, leadership roles
- projects: Include academic, personal, and professional projects
- certifications: Include courses, certificates, online courses
- languages: Spoken/written languages
- key_strengths: Top 3-5 technical/professional strengths

Resume Text:
{resume_text}

Return ONLY the JSON object:"""

        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean up response
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        # Remove any leading/trailing text
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            result_text = result_text[start_idx:end_idx]
        
        extracted_data = json.loads(result_text)
        print(f"✅ AI extracted name: {extracted_data.get('full_name')}")
        print(f"✅ AI extracted {len(extracted_data.get('skills', []))} skills")
        print(f"✅ AI extracted {len(extracted_data.get('education', []))} education entries")
        print(f"✅ AI extracted {len(extracted_data.get('experience', []))} experience entries")
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ Error extracting resume data with Gemini: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_interview_recording(video_file, participant_count=1):
    """
    Analyze interview recording to generate:
    1. Personal performance analysis
    2. Integrity/behavioral indicators
    3. Relative ranking among participants
    
    CRITICAL: Uses rule-based prompting to ensure unique, evidence-based outputs.
    NO hardcoded examples. NO generic templates. Each analysis must be original.
    
    Args:
        video_file: Uploaded video/audio file object
        participant_count: Number of participants in the recording (default 1 for solo interview)
    
    Returns:
        dict: Structured analysis results
    """
    # Check if API key is configured
    if not GEMINI_API_KEY or GEMINI_API_KEY == 'your_gemini_api_key_here':
        print("Gemini API key not configured, returning error")
        return {
            "error": "Gemini API key not configured. Please set GEMINI_API_KEY in .env file."
        }
    
    try:
        # Upload file to Gemini for analysis
        print(f"📤 Uploading {video_file.name} to Gemini API for analysis...")
        uploaded_file = genai.upload_file(video_file.temporary_file_path(), mime_type=video_file.content_type)
        print(f"✅ File uploaded: {uploaded_file.name}")
        
        # Wait for file to be processed
        import time
        while uploaded_file.state.name == "PROCESSING":
            print("⏳ Processing video...")
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
        
        if uploaded_file.state.name == "FAILED":
            raise ValueError("Video processing failed")
        
        print(f"✅ Video ready for analysis")
        
        # Initialize Gemini model (using gemini-2.5-flash as required)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # CRITICAL: Rule-based prompt that forces unique, evidence-specific outputs
        prompt = f"""You are an expert behavioral analyst conducting a post-interview performance review.

ANALYZE the provided interview recording and generate a comprehensive, ORIGINAL assessment.

⚠️ CRITICAL REQUIREMENTS:
1. Base ALL observations on actual visible/audible evidence from THIS specific recording
2. Use DIFFERENT phrasing for every analysis - never repeat templated language
3. Describe patterns observed over TIME, not isolated moments
4. Vary your vocabulary and sentence structure naturally
5. Ground every claim in specific behavioral evidence
6. If analyzing multiple participants, compare their relative performance

📋 ANALYSIS FRAMEWORK:

I. EMOTIONAL & CONFIDENCE ANALYSIS
- Observe facial expressions, body language, and vocal tone patterns throughout the recording
- Track how emotional state evolves from beginning to end
- Assess confidence based on: speech fluency, hesitation frequency, posture changes, eye contact
- Calculate confidence score (0-100) based on observable behavioral cues
- Use evidence-specific descriptors, NOT generic labels like "calm" or "nervous"

II. COMMUNICATION QUALITY
- Evaluate articulation, clarity, pacing, and coherence
- Note any hesitations, filler words, or communication barriers
- Assess how effectively ideas are conveyed
- Identify communication strengths and areas for improvement

III. BEHAVIORAL INTEGRITY INDICATORS (NOT Deterministic)
- Analyze eye movement patterns: scanning behavior, gaze direction, focus consistency
- Assess attention level: engagement with questions, distraction signs, focus duration
- Estimate integrity risk (low/medium/high) based on behavioral anomalies:
  * Frequent looking away from screen (may indicate reading from notes)
  * Sudden changes in speech patterns (may indicate external input)
  * Unnatural pauses or delays (may indicate searching for information)
  * Inconsistent eye contact or gaze patterns
- IMPORTANT: These are behavioral observations only, NOT accusations

IV. STRENGTHS & IMPROVEMENTS
- Identify 3-5 specific strengths demonstrated in THIS recording
- Suggest 3-5 concrete improvements based on observed gaps
- Use evidence from the recording to support each point
- Be specific and actionable

V. RELATIVE RANKING (if multiple participants detected)
- Compare performance across participants on this call
- Rank based on: communication clarity, technical depth, confidence, engagement
- Calculate relative percentile band
- Total participants: {participant_count}

🎯 OUTPUT FORMAT:
Return ONLY a valid JSON object following this exact structure:

{{
  "personal_report": {{
    "emotion_trend": "<describe the emotional progression/pattern you observed throughout - use specific behavioral descriptors>",
    "confidence_score": <integer 0-100 based on observable cues>,
    "communication": "<specific analysis of how this person communicated - cite actual patterns you noticed>",
    "strengths": [
      "<specific strength #1 with evidence from recording>",
      "<specific strength #2 with evidence from recording>",
      "<specific strength #3 with evidence from recording>"
    ],
    "improvements": [
      "<specific improvement #1 based on observed gaps>",
      "<specific improvement #2 based on observed gaps>",
      "<specific improvement #3 based on observed gaps>"
    ]
  }},
  "integrity_analysis": {{
    "eye_movement": "<describe the actual eye movement pattern you observed - be specific about what you saw>",
    "attention_level": "<low|moderate|high - based on engagement cues>",
    "suspicion_risk": "<low|medium|high - based on behavioral anomalies>",
    "notes": "<explain WHY you assigned this risk level - what specific behaviors led to this assessment>"
  }},
  "ranking": {{
    "position": <integer position among participants>,
    "total_participants": {participant_count},
    "percentile": "<e.g., 'Top 25%', 'Upper Middle 50%', 'Bottom 25%' - based on relative comparison>"
  }},
  "disclaimer": "This analysis provides behavioral insights only and should not be used as the sole basis for hiring decisions. Integrity indicators are probabilistic, not deterministic."
}}

⚠️ REMEMBER:
- Generate ORIGINAL content based on THIS recording
- Use VARIED language - never copy phrasing from previous analyses
- Ground observations in ACTUAL evidence
- Confidence score must reflect observable behavioral cues
- Integrity risk is a behavioral probability, NOT a verdict

Now analyze the interview recording and return ONLY the JSON object:"""

        # Generate analysis
        print("🤖 Generating AI analysis...")
        response = model.generate_content([uploaded_file, prompt])
        result_text = response.text.strip()
        
        # Parse JSON response
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        # Extract JSON object
        start_idx = result_text.find('{')
        end_idx = result_text.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            result_text = result_text[start_idx:end_idx]
        
        analysis_result = json.loads(result_text)
        
        print("✅ Analysis complete")
        print(f"   Confidence Score: {analysis_result.get('personal_report', {}).get('confidence_score', 'N/A')}")
        print(f"   Suspicion Risk: {analysis_result.get('integrity_analysis', {}).get('suspicion_risk', 'N/A')}")
        print(f"   Ranking: {analysis_result.get('ranking', {}).get('position', 'N/A')}/{participant_count}")
        
        # Clean up uploaded file
        genai.delete_file(uploaded_file.name)
        print("🗑️ Temporary file deleted from Gemini")
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ Error analyzing interview with Gemini: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Failed to analyze interview recording: {str(e)}"
        }
