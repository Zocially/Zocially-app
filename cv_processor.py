import os
import google.generativeai as genai
import PyPDF2
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions

class CVProcessor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Switch to 2.0-flash-exp (available and free tier)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

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

    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
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
            # "Header", # Header is usually implicit at the top
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

    def generate_docx(self, cv_text, filename):
        """Converts Markdown CV text to a professionally formatted DOCX file."""
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        import re

        doc = Document()
        
        # --- Styles ---
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)

        # Helper to add styled paragraph
        def add_styled_para(text, bold=False, italic=False, size=None, align=None, space_after=None):
            p = doc.add_paragraph()
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            if size:
                run.font.size = Pt(size)
            if align:
                p.alignment = align
            if space_after is not None:
                p.paragraph_format.space_after = Pt(space_after)
            return p

        # --- Parsing ---
        # Clean up markdown code blocks if present
        cv_text = cv_text.replace("```markdown", "").replace("```", "").strip()
        
        lines = cv_text.split('\n')
        
        # 1. Extract Header (Name & Contact)
        # Assumption: The first H1 is the Name, followed by contact lines until the next Header.
        header_lines = []
        body_lines = []
        
        is_header = True
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # If we hit a section header (##), header is done
            if line.startswith('## '):
                is_header = False
            
            if is_header:
                # Remove markdown headers for the name
                clean_line = line.replace('# ', '').replace('**', '').strip()
                header_lines.append(clean_line)
            else:
                body_lines.append(line)

        # 2. Write Header
        if header_lines:
            # Name (First line)
            name = header_lines[0]
            add_styled_para(name, bold=True, size=24, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
            
            # Contact Info (Joined by |)
            contact_info = " | ".join(header_lines[1:])
            add_styled_para(contact_info, size=10, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
            
            # Horizontal Line
            p = doc.add_paragraph()
            p.paragraph_format.border_bottom_color = RGBColor(0, 0, 0)
            p.paragraph_format.border_bottom_width = Pt(1)
            p.paragraph_format.space_after = Pt(12)

        # 3. Write Body Sections
        current_section = ""
        skills_buffer = []
        
        def flush_skills():
            nonlocal skills_buffer
            if skills_buffer:
                # Join with a bullet point separator
                skill_text = " • ".join(skills_buffer)
                p = doc.add_paragraph(skill_text)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.space_after = Pt(12)
                skills_buffer = []

        for line in body_lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we are hitting a header or new section, flush skills if needed
            if line.startswith('## ') or line.startswith('### '):
                flush_skills()

            # Section Headers (##)
            if line.startswith('## '):
                current_section = line[3:].strip()
                p = doc.add_heading(current_section.upper(), level=1)
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(6)
                continue
                
            # Sub-headers (###)
            if line.startswith('### '):
                text = line[4:].strip().replace('**', '')
                p = doc.add_heading(text, level=2)
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(3)
                continue
                
            # Bullet Points
            if line.startswith('- ') or line.startswith('* '):
                text = line[2:].strip().replace('**', '') # Simple bold removal for cleanliness
                
                # Special formatting for Skills section
                if "SKILLS" in current_section.upper():
                    skills_buffer.append(text)
                else:
                    # Normal bullet point
                    p = doc.add_paragraph(text, style='List Bullet')
            
            # Normal Text
            else:
                # If we encounter normal text in skills section, flush buffer first
                if "SKILLS" in current_section.upper() and skills_buffer:
                    flush_skills()

                # Handle bolding within text **like this**
                p = doc.add_paragraph()
                parts = re.split(r'(\*\*.*?\*\*)', line)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        run = p.add_run(part[2:-2])
                        run.bold = True
                    else:
                        p.add_run(part)
        
        # Final flush
        flush_skills()

        doc.save(filename)
        return filename


    @retry(
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
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
