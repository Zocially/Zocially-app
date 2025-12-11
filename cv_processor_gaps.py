import os
import google.generativeai as genai
import PyPDF2
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions
import re

class CVProcessor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Configure safety settings to prevent blocking professional CV content
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
        
        safety_settings = [
            {
                "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
            {
                "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": HarmBlockThreshold.BLOCK_NONE,
            },
        ]
        
        # Switch to 2.0-flash-exp (available and free tier)
        # Switch to gemini-flash-latest (Explicitly available in user list)
        self.model = genai.GenerativeModel(
            'gemini-flash-latest',
            safety_settings=safety_settings
        )

    def extract_text(self, file_path):
        """Extracts text from PDF."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""

    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def assess_cv(self, cv_text):
        """Assess the CV against general best practices."""
        prompt = f"""
        Act as an expert career coach. Review the following CV and provide a brief assessment.
        Highlight 3 strengths and 3 areas for improvement.
        
        CV Content:
        {cv_text}
        """
        response = self.model.generate_content(prompt)
        return response.text
    
    def identify_cv_gaps(self, cv_text):
        """
        Identifies missing or weak elements in the CV.
        Returns a dict with gaps and user-friendly prompts.
        """
        gaps = {
            'has_gaps': False,
            'missing_elements': [],
            'prompts': {}
        }
        
        # Check for phone number
        has_phone = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', cv_text))
        if not has_phone:
            gaps['missing_elements'].append('phone')
            gaps['prompts']['phone'] = "📞 Phone Number (e.g., (555) 123-4567)"
            gaps['has_gaps'] = True
        
        # Check for LinkedIn
        has_linkedin = bool(re.search(r'linkedin\.com/in/[\w-]+', cv_text, re.IGNORECASE))
        if not has_linkedin:
            gaps['missing_elements'].append('linkedin')
            gaps['prompts']['linkedin'] = "🔗 LinkedIn Profile URL (e.g., https://linkedin.com/in/yourname)"
            gaps['has_gaps'] = True
        
        # Check for location
        has_location = bool(re.search(r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b', cv_text))  # City, ST format
        if not has_location:
            gaps['missing_elements'].append('location')
            gaps['prompts']['location'] = "📍 Location (e.g., New York, NY or London, UK)"
            gaps['has_gaps'] = True
        
        # Check for professional summary
        has_summary = bool(re.search(r'##\s*(Professional\s+)?Summary', cv_text, re.IGNORECASE))
        summary_text = ""
        if has_summary:
            # Extract summary section
            summary_match = re.search(r'##\s*(Professional\s+)?Summary\s*\n(.+?)(?=\n##|\Z)', cv_text, re.IGNORECASE | re.DOTALL)
            if summary_match:
                summary_text = summary_match.group(2).strip()
        
        if not has_summary or len(summary_text) < 50:
            gaps['missing_elements'].append('summary')
            gaps['prompts']['summary'] = "💼 Professional Summary (Brief overview of your career and goals)"
            gaps['has_gaps'] = True
        
        # Check for skills section
        has_skills = bool(re.search(r'##\s*(Skills|Core\s+Competencies|Technical\s+Skills)', cv_text, re.IGNORECASE))
        if not has_skills:
            gaps['missing_elements'].append('skills')
            gaps['prompts']['skills'] = "🎯 Key Skills (Comma-separated, e.g., Python, Project Management, Communication)"
            gaps['has_gaps'] = True
        
        # Check for quantifiable achievements
        numbers_count = len(re.findall(r'\d+%|\$\d+|\d+\+', cv_text))
        if numbers_count < 3:
            gaps['missing_elements'].append('achievements')
            gaps['prompts']['achievements'] = "📊 Key Achievements (Include numbers/metrics, e.g., 'Increased sales by 30%')"
            gaps['has_gaps'] = True
        
        return gaps
