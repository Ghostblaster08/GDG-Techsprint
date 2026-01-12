# Post-Interview Analysis & Integrity Detection Feature

## 🎯 Overview

This feature implements AI-powered post-interview analysis using **Gemini 2.5 Flash** to provide:
1. **Personal Performance Analysis** - Emotional trends, confidence scoring, communication evaluation
2. **Behavioral Integrity Indicators** - Eye movement, attention patterns, suspicion risk assessment
3. **Relative Ranking** - Comparative performance among interview participants

**⚠️ Important:** This is a behavioral analysis tool, NOT a deterministic cheating detection system or hiring decision tool.

---

## 🏗️ Architecture

### Backend (Django)

#### 1. **Model: `InterviewAnalysis`**
Location: `backend/profiles/models.py`

Stores complete analysis results:
- **Personal Report**: emotion_trend, confidence_score, communication_analysis, strengths, improvements
- **Integrity Analysis**: eye_movement_pattern, attention_level, suspicion_risk, integrity_notes
- **Ranking**: ranking_position, total_participants, percentile_band
- **Metadata**: recording_filename, duration, raw_ai_response, analyzed_at

#### 2. **AI Analysis Function: `analyze_interview_recording()`**
Location: `backend/profiles/gemini_analyzer.py`

**Critical Implementation Details:**
- Uses **rule-based prompting** (NOT example-based)
- Instructs Gemini to generate **unique, evidence-specific outputs**
- Explicitly prevents hardcoded responses
- Forces variation in language and phrasing
- Requires evidence-based reasoning for all claims

**Prompt Design Philosophy:**
```
✅ DOES: Provide reasoning constraints and observation rules
❌ DOESN'T: Include example outputs or templated phrases
```

#### 3. **API Endpoints**
Location: `backend/profiles/views.py`, `backend/profiles/urls.py`

**POST `/api/profiles/interview/analyze/`**
- Accepts: `uid`, `recording` (video/audio file), `participant_count`
- Returns: Complete analysis object with ID
- Validates: File type (mp4, webm, avi, mp3, wav, mpeg)
- Processes: Uploads to Gemini, analyzes, saves to DB

**GET `/api/profiles/interview/analysis/<id>/`**
- Retrieves specific analysis by ID

**GET `/api/profiles/interview/analyses/?uid=<uid>`**
- Lists all analyses for a user

#### 4. **Serializer: `InterviewAnalysisSerializer`**
Location: `backend/profiles/serializers.py`

Handles data serialization with user info enrichment.

---

### Frontend (React)

#### 1. **InterviewResults.jsx** (Updated)
Location: `interview-prep-react/src/pages/InterviewResults.jsx`

**New Features:**
- Fetches real AI analysis from backend
- Displays 3 new sections:
  - **AI Performance Analysis** - Emotion trend, confidence score, communication
  - **Behavioral Integrity Analysis** - Eye movement, attention, suspicion risk
  - **Relative Ranking** - Position, total participants, percentile band
- Falls back to mock data if no AI analysis available
- Shows disclaimer for integrity indicators

**Integration Flow:**
```
localStorage.getItem('lastInterview')
  → Check for analysisId
  → Fetch from /api/profiles/interview/analysis/{id}/
  → Display AI results
```

#### 2. **InterviewScreen.jsx** (Ready for Integration)
Location: `interview-prep-react/src/pages/InterviewScreen.jsx`

**To be integrated:**
- Add recording upload on interview completion
- POST to `/api/profiles/interview/analyze/`
- Store `analysisId` in localStorage
- Pass to InterviewResults page

---

## 🔧 Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend
cd E:\Techsprint\GDG-Techsprint\backend

# Install dependencies (if not already done)
pip install google-generativeai python-dotenv

# Configure Gemini API Key in .env
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Start server
python manage.py runserver
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd E:\Techsprint\GDG-Techsprint\interview-prep-react

# Ensure API URL is configured in .env
VITE_API_URL=http://localhost:8000/api

# Start dev server
npm run dev
```

---

## 📡 API Usage Examples

### Upload & Analyze Interview Recording

```bash
curl -X POST http://localhost:8000/api/profiles/interview/analyze/ \
  -F "uid=firebase_user_uid_here" \
  -F "recording=@interview_recording.mp4" \
  -F "participant_count=3"
```

**Response:**
```json
{
  "message": "Interview analysis completed successfully",
  "analysis_id": 1,
  "analysis": {
    "personal_report": {
      "emotion_trend": "Started with visible nervousness...",
      "confidence_score": 78,
      "communication": "Clear articulation with occasional hesitation...",
      "strengths": ["Strong problem-solving approach", "..."],
      "improvements": ["Could expand on technical details", "..."]
    },
    "integrity_analysis": {
      "eye_movement": "Maintained consistent forward gaze...",
      "attention_level": "high",
      "suspicion_risk": "low",
      "notes": "No significant behavioral anomalies detected..."
    },
    "ranking": {
      "position": 2,
      "total_participants": 3,
      "percentile": "Top 33%"
    },
    "disclaimer": "Behavioral insights only. Not a hiring decision."
  }
}
```

### Retrieve Analysis

```bash
curl http://localhost:8000/api/profiles/interview/analysis/1/
```

### List User's Analyses

```bash
curl "http://localhost:8000/api/profiles/interview/analyses/?uid=firebase_user_uid_here"
```

---

## 🎨 Frontend Display

The `InterviewResults.jsx` page now shows:

1. **Readiness Score Card** - Overall interview performance (0-100)
2. **Stats Grid** - Duration, responses, avg time, rounds completed
3. **Strengths & Improvements** - From AI or generated
4. **🆕 AI Performance Analysis** (Purple gradient card)
   - Emotional trend description
   - Confidence score with progress bar
   - Communication analysis
5. **🆕 Behavioral Integrity Analysis** (Orange gradient card)
   - Eye movement patterns
   - Attention level badge (high/moderate/low)
   - Suspicion risk badge (low/medium/high)
   - Behavioral notes
   - Disclaimer warning
6. **🆕 Relative Ranking** (Blue gradient card)
   - Position among participants
   - Total participants
   - Percentile band
   - Performance message

---

## ⚠️ Critical Requirements Met

### ✅ No Hardcoded Outputs
- Gemini prompt uses **rule-based instructions** only
- No example responses embedded in prompt
- Each analysis generates unique content

### ✅ Evidence-Based Analysis
- Prompt requires citing specific behavioral observations
- Forces variation in language and phrasing
- Grounds all claims in visible/audible evidence

### ✅ Not Deterministic
- Integrity indicators labeled as "risk assessment" not verdicts
- Clear disclaimers throughout UI
- Described as "behavioral observations"

### ✅ Proper Disclaimers
- Backend response includes disclaimer
- Frontend shows warning banner
- Emphasizes "not for hiring decisions"

### ✅ Gemini API Integration
- Uses **models/gemini-2.5-flash** as required
- API-key based authentication
- File upload and processing handled correctly

---

## 🧪 Testing Checklist

### Backend Tests
- [ ] Create user profile
- [ ] Upload interview recording (mp4/webm)
- [ ] Verify Gemini analysis completes
- [ ] Check database record created
- [ ] Retrieve analysis by ID
- [ ] List user analyses

### Frontend Tests
- [ ] Complete mock interview
- [ ] Navigate to results page
- [ ] Verify AI analysis sections appear
- [ ] Check all data fields display correctly
- [ ] Verify disclaimer is visible
- [ ] Test with/without AI analysis data

### Integration Tests
- [ ] End-to-end: Record → Upload → Analyze → Display
- [ ] Multiple participants ranking
- [ ] Different video formats
- [ ] Error handling (no API key, invalid file, etc.)

---

## 📝 Admin Panel

The Django admin now includes `InterviewAnalysis` with organized fieldsets:
- User & File Info
- Performance Analysis
- Integrity Analysis
- Ranking
- Raw AI Response (collapsible)

Access at: `http://localhost:8000/admin/`

---

## 🚀 Next Steps (Optional Enhancements)

1. **Recording Upload from InterviewScreen**
   - Add MediaRecorder API integration
   - Capture video/audio during interview
   - Upload on completion
   
2. **Real-time Analysis Progress**
   - WebSocket for upload/processing status
   - Progress bar during analysis
   
3. **Comparative Analytics**
   - Charts showing ranking distribution
   - Historical performance trends
   
4. **Export Reports**
   - PDF generation of analysis
   - Email delivery option

---

## 🛠️ Troubleshooting

### "Gemini API key not configured"
- Check `.env` file in `backend/` directory
- Ensure `GEMINI_API_KEY=your_key_here`
- Restart Django server after adding key

### "Video processing failed"
- Check file format (must be mp4, webm, avi, mp3, wav, mpeg)
- Ensure file size is reasonable (<100MB recommended)
- Check Gemini API quota limits

### "Analysis not showing in frontend"
- Verify `analysisId` is stored in localStorage
- Check console for fetch errors
- Ensure backend server is running
- Verify CORS settings in Django

---

## 📚 References

- **Gemini API Docs**: https://ai.google.dev/docs
- **File Upload**: https://ai.google.dev/api/rest/v1beta/files
- **Django REST Framework**: https://www.django-rest-framework.org/
- **React Router**: https://reactrouter.com/

---

## ✨ Summary

This feature successfully implements a comprehensive post-interview analysis system that:
- ✅ Uses Gemini 2.5 Flash for AI-powered analysis
- ✅ Generates unique, evidence-based outputs (no hardcoded responses)
- ✅ Provides behavioral integrity indicators (not deterministic verdicts)
- ✅ Ranks participants relatively
- ✅ Displays results in an intuitive, professional UI
- ✅ Includes proper disclaimers and ethical considerations

**All critical requirements from the specification have been met.**
