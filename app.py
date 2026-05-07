from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import requests

# ================= LOAD ENV =================
load_dotenv()

# ================= FLASK APP =================
app = Flask(__name__)
CORS(app)

# ================= API KEY =================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print(f"🔑 API Key loaded: {'✅ Yes' if GROQ_API_KEY else '❌ No'}")

# ================= ROOT DIRECTORY =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= HTML ROUTES =================
@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'welcomepage.html')

@app.route('/login')
def login():
    return send_from_directory(BASE_DIR, 'loginpage.html')

@app.route('/work-experience')
def work_experience():
    return send_from_directory(BASE_DIR, 'work-experience.html')

@app.route('/analyzer')
def analyzer():
    return send_from_directory(BASE_DIR, 'analyzer.html')

@app.route('/education')
def education():
    return send_from_directory(BASE_DIR, 'education.html')

@app.route('/project')
def project():
    return send_from_directory(BASE_DIR, 'project.html')

@app.route('/skill')
def skill():
    return send_from_directory(BASE_DIR, 'skill.html')

@app.route('/template-selection')
def template_selection():
    return send_from_directory(BASE_DIR, 'template-selection.html')

@app.route('/certification')
def certification():
    return send_from_directory(BASE_DIR, 'certification.html')

@app.route('/userpage')
def userpage():
    return send_from_directory(BASE_DIR, 'Userpage.html')

@app.route('/summary')
def summary():
    return send_from_directory(BASE_DIR, 'summary.html')

@app.route('/resume-analyzer')
def resume_analyzer():
    return send_from_directory(BASE_DIR, 'analyzer.html')

# ================= GENERATE SUMMARY =================
@app.route('/generate-summary', methods=['POST'])
def generate_summary():
    try:
        data = request.get_json()
        user_data = data.get('userData', {})

        prompt = f"""
You are an expert resume writer.

Create a professional summary for:

Name: {user_data.get('firstName', '')} {user_data.get('surname', '')}
Profession: {user_data.get('profession', 'Professional')}
Location: {user_data.get('city', '')}, {user_data.get('country', '')}

Write ONLY a strong professional summary in 3-4 sentences.
"""

        # ================= AI SUMMARY =================
        if GROQ_API_KEY:

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional resume writer."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 250
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25
            )

            if response.status_code == 200:

                result = response.json()

                generated_summary = (
                    result.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )

                return jsonify({
                    "success": True,
                    "summary": generated_summary,
                    "using_api": True
                })

        # ================= FALLBACK =================
        fallback_summary = f"""
{user_data.get('firstName', '')} {user_data.get('surname', '')}
is a dedicated {user_data.get('profession', 'professional')}
with strong problem-solving abilities and a passion for excellence.
"""

        return jsonify({
            "success": True,
            "summary": fallback_summary,
            "using_api": False
        })

    except Exception as e:
        print("❌ Summary Error:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        })

# ================= RESUME ANALYZER =================
@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():

    try:
        data = request.get_json()
        resume_text = data.get("resumeText", "")

        if not resume_text or len(resume_text) < 50:
            return jsonify({
                "success": False,
                "error": "Resume content too short"
            })

        prompt = f"""
Analyze this resume:

{resume_text[:5000]}

Return ONLY valid JSON:

{{
    "score": 85,
    "strengths": [],
    "weaknesses": [],
    "suggestions": [],
    "keywords": [],
    "detailed_analysis": ""
}}
"""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "system",
                    "content": "Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,
            "max_tokens": 2000
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=25
        )

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"API Error {response.status_code}"
            })

        result = response.json()

        analysis_text = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        # ================= CLEAN JSON =================
        if "```json" in analysis_text:
            analysis_text = analysis_text.split("```json")[1].split("```")[0]

        elif "```" in analysis_text:
            analysis_text = analysis_text.split("```")[1].split("```")[0]

        analysis_text = analysis_text.strip()

        analysis = json.loads(analysis_text)

        return jsonify({
            "success": True,
            "analysis": analysis
        })

    except Exception as e:
        print("❌ Analyze Error:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        })

# ================= START SERVER =================
if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))

    print(f"🚀 Server running on port {port}")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )