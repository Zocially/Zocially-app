import os
import google.generativeai as genai
import PyPDF2

class CVProcessor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

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



    def tailor_cv(self, cv_text, job_description):
        """Rewrites the CV to match the job description."""
        prompt = f"""
        Act as an expert CV writer. Tailor the following CV to match the Job Description provided.
        
        **CRITICAL INSTRUCTION ON DATES:**
        You must PRESERVE all dates exactly as they appear in the original CV. 
        - Do NOT change "Jan 2020" to "January 2020".
        - Do NOT change "2020 - Present" to "2020 - 2023".
        - Keep the exact date strings for every work experience and education entry.

        **Guidelines:**
        1. **Structure:** Follow this standard professional format:
           - **Header:** Name, Contact Info (Email, Phone, LinkedIn, Location).
           - **Professional Summary:** A strong, tailored summary (3-4 lines) aligning with the job.
           - **Skills:** A concise list of relevant hard and soft skills.
           - **Work Experience:** Reverse chronological order. For each role include **Job Title**, **Company**, **Location**, and **Date Range**.
           - **Education:** Degree, University, Year.
           - **Projects/Certifications:** (If applicable and relevant).
        2. **Content:** Optimize for ATS (Applicant Tracking Systems) by using keywords from the job description.
        3. **Tone:** Professional, confident, and action-oriented.
        4. **Format:** Return ONLY the content of the new CV, formatted in clean Markdown. 
           - Use `##` for section headers (e.g., ## Professional Summary).
           - Use `###` for sub-headers (e.g., ### Software Engineer | Google).
           - Use `**bold**` for key terms.
           - Use `*italic*` for less emphatic emphasis if needed.
           - Use `-` for bullet points.

        CV Content:
        {cv_text}
        
        Job Description:
        {job_description}
        """
        
        response = self.model.generate_content(prompt)
        return response.text

    def validate_cv(self, cv_text: str) -> str:
        """Simple validation of the generated CV.
        Checks for presence of key sections and returns a report.
        """
        import re
        required_sections = [
            "Header",
            "Professional Summary",
            "Skills",
            "Work Experience",
            "Education",
        ]
        missing = []
        for sec in required_sections:
            pattern = rf"##\s*{re.escape(sec)}"
            if not re.search(pattern, cv_text, re.IGNORECASE):
                missing.append(sec)
        if missing:
            return "Missing sections: " + ", ".join(missing)
        return "CV looks good – all required sections are present."


    def generate_cover_letter(self, cv_text, job_info):
        """Generates a cover letter using job info (title, company, description)."""
        # Support both dict and plain description string
        if isinstance(job_info, dict):
            title = job_info.get('title', '')
            company = job_info.get('company', '')
            description = job_info.get('description', '')
            summary = job_info.get('summary', '')
        else:
            title = ''
            company = ''
            description = job_info
            summary = ''
        # Truncate description to avoid overly long prompts
        max_len = 1500
        if len(description) > max_len:
            description = description[:max_len] + "..."
        # Build a detailed prompt, optionally including a summary
        prompt = f"""
        You are a professional cover letter writer.
        Write a concise, targeted cover letter for the position \"{title}\" at \"{company}\".
        Use the candidate's CV content and align with the job description below.
        """
        if summary:
            prompt += f"\nAdditional summary of the role (highlights, required skills, responsibilities):\n{summary}\n"
        prompt += f"""
        CV Content:
        {cv_text}
        
        Job Description:
        {description}
        """
        response = self.model.generate_content(prompt)
        return response.text
