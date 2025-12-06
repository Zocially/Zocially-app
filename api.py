
import streamlit as st
import os
import datetime
from dotenv import load_dotenv

# Lazy load custom modules inside main_app or where needed
# from google_handler import GoogleHandler
# from cv_processor import CVProcessor
# from job_finder import JobFinder
# from docx_utils import create_docx_from_markdown

# Load environment variables
load_dotenv()

# Helper to check configuration
def is_configured() -> bool:
    """Return True if Gemini API key is present. Google Drive credentials are optional."""
    api_key = os.getenv("GOOGLE_API_KEY")
    return bool(api_key)

# Setup screen for first‑time users
def setup_screen():
    st.title("🚀 Job Hunter AI – Setup")
    
    # Check if token.pickle exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(base_dir, "token.pickle")
    has_token = os.path.exists(token_path)
    
    st.markdown(
        """
        **Welcome!** It looks like the app is not fully configured.
        
        ### Required:
        1. **Google Gemini API Key**: Get it from [Google AI Studio](https://aistudio.google.com/).
        
        ### Optional (for Drive/Sheets integration):
        - **Local**: Upload `credentials.json`.
        - **Cloud Deployment**: Configure `[gcp_service_account]` in Streamlit Secrets.
        """
    )
    
    st.divider()
    
    gemini_key = st.text_input("Enter your Google Gemini API Key", type="password")
    
    label = "Upload `credentials.json` (Optional - Google OAuth)"
    if has_token:
        label += " - [Existing login found]"
    
    cred_file = st.file_uploader(label, type="json")
    
    if st.button("Save & Continue"):
        if not gemini_key:
            st.error("Please provide the Gemini API key.")
            return
        
        # Save API key to .env
        from dotenv import set_key
        set_key('.env', 'GOOGLE_API_KEY', gemini_key)
        
        # Save credentials file if provided
        if cred_file:
            cred_path = os.path.join(base_dir, "credentials.json")
            with open(cred_path, "wb") as f:
                f.write(cred_file.getbuffer())
                
        st.success("Configuration saved! Restarting app…")
        st.rerun()

# Rate Limiter Class
class RateLimiter:
    def __init__(self, db_path="usage.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usage_logs
                     (ip TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def get_client_ip(self):
        # Try to get IP from Streamlit context
        try:
            if st.context.headers:
                headers = st.context.headers
                return headers.get("X-Forwarded-For", headers.get("Remote-Addr", "unknown"))
        except:
            pass
        return "unknown"

    def check_limit(self, ip, limit=5):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Check usage in last 24 hours
        c.execute("SELECT count(*) FROM usage_logs WHERE ip=? AND timestamp > datetime('now', '-1 day')", (ip,))
        count = c.fetchone()[0]
        conn.close()
        return count < limit

    def log_usage(self, ip):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO usage_logs (ip) VALUES (?)", (ip,))
        conn.commit()
        conn.close()

# Main application UI (original content)
def main_app():
    # Page Config
    
    st.set_page_config(
        page_title="Job Hunter AI",
        page_icon="🇬🇧",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://www.zocially.co.in/contact',
            'Report a bug': "https://www.zocially.co.in/contact",
            'About': "# Job Hunter AI by Zocially"
        }
    )

    
    # Rate Limiter Init
    # limiter = RateLimiter()
    # client_ip = limiter.get_client_ip()
    client_ip = "unknown"

    # Initialize Handlers
    def get_handlers():
        # Imports here to avoid top-level crashes
        from google_handler import GoogleHandler
        from cv_processor import CVProcessor
        from job_finder import JobFinder
        
        gh = None
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(base_dir, 'credentials.json')
            token_path = os.path.join(base_dir, 'token.pickle')
            # Try to init Google Handler, but allow failure
            try:
                gh = GoogleHandler(credentials_file=credentials_path, token_file=token_path)
            except Exception as e:
                # Fail silently for optional feature
                print(f"Google Drive integration disabled: {e}")
                gh = None
            
            cv = CVProcessor()
            jf = JobFinder()
            return gh, cv, jf
        except Exception as e:
            st.error(f"Initialization Error: {e}")
            return None, None, None
    google_handler, cv_processor, job_finder = get_handlers()
    # Title and Description
    st.title("🚀 Job Hunter AI")
    st.markdown("Automate your job application process with AI. Upload your CV, provide a job link, and let the magic happen.")


    # Sidebar for Configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("GOOGLE_API_KEY not found in .env")
        else:
            st.success("API Key Found")
        
        if st.button("Reset Configuration"):
            # Clear .env file
            with open('.env', 'w') as f:
                f.write('')
            # Remove credentials.json
            cred_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credentials.json")
            if os.path.exists(cred_path):
                os.remove(cred_path)
            # Clear session state
            st.session_state.clear()
            st.rerun()

        st.divider()

        # Debug Section
        with st.expander("Debug Info"):
            import google.generativeai as genai
            st.write(f"GenAI Version: {genai.__version__}")
            if st.button("List Models"):
                try:
                     models = [m.name for m in genai.list_models()]
                     st.write(models)
                except Exception as e:
                     st.error(f"Error listing models: {e}")


    # Main Content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Upload Resume")
        uploaded_file = st.file_uploader("Upload your CV (PDF)", type="pdf")
        
        # Initialize or retrieve CV text from session state
        if 'cv_text' not in st.session_state:
            st.session_state.cv_text = ""
        cv_text = st.session_state.cv_text
        if uploaded_file:
            # Save temp file to read it
            with open("temp_resume.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            with st.spinner("Reading CV..."):
                extracted_text = cv_processor.extract_text("temp_resume.pdf")
                if extracted_text:
                    st.session_state.cv_text = extracted_text
                    cv_text = extracted_text
                    st.success("CV Loaded Successfully!")
                    with st.expander("View Extracted Text"):
                        st.text(cv_text[:1000] + "...")
                else:
                    st.error("Could not read CV text.")

        if cv_text:
            if st.button("Assess CV"):
                with st.spinner("Analyzing CV with Gemini..."):
                    try:
                        assessment = cv_processor.assess_cv(cv_text)
                        st.markdown("### CV Assessment")
                        st.markdown(assessment)
                    except Exception as e:
                        st.error(f"Error assessing CV: {e}")
                        if "API key" in str(e):
                            st.warning("💡 It looks like your API Key might be invalid. Please use the 'Reset Configuration' button in the sidebar to enter a new key.")

    with col2:
        st.subheader("2. Job Details")
        job_url = st.text_input("Enter Job URL")
        
        if job_url and cv_text:
            if st.button("Generate Application"):
                # Rate Limiting (Disabled by default - set to True to enable)
                ENABLE_RATE_LIMIT = False
                
                if ENABLE_RATE_LIMIT:
                    # Check Rate Limit
                    if not limiter.check_limit(client_ip):
                        st.error("🚫 Daily Limit Reached. You can only generate 5 applications per day.")
                        return

                    # Log Usage
                    limiter.log_usage(client_ip)

                with st.spinner(f"Processing {job_url}..."):
                    job_details = job_finder.extract_job_details(job_url)
                    
                    if job_details:
                        st.success(f"Found Job: {job_details['title']} at {job_details['company']}")
                        
                        # Allow user to edit title, company, and description
                        title = st.text_input("Job Title (editable)", value=job_details.get('title', ''), key="job_title")
                        company = st.text_input("Company (editable)", value=job_details.get('company', ''), key="job_company")
                        if 'job_desc' not in st.session_state:
                            st.session_state.job_desc = job_details.get('description', '')
                        edited_desc = st.text_area("Edit Job Description (optional)", st.session_state.job_desc, height=200, key="job_desc")

                        
                        # New textarea for a concise job summary (highlights, key responsibilities)
                        if 'job_summary' not in st.session_state:
                            st.session_state.job_summary = ""
                        summary_text = st.text_area("Job Summary (highlights you want the cover letter to address)", st.session_state.job_summary, height=150, key="job_summary")

                        
                        # Update job_details dict with edited values and summary
                        job_details['title'] = title
                        job_details['company'] = company
                        job_details['description'] = edited_desc
                        job_details['summary'] = summary_text
                        
                        # Tabs for results
                        tab1, tab2, tab3 = st.tabs(["Cover Letter", "Tailored CV", "Actions"])
                        
                        with tab1:
                            st.subheader("Generated Cover Letter")
                            try:
                                cover_letter = cv_processor.generate_cover_letter(cv_text, job_details)
                                st.text_area("Cover Letter", cover_letter, height=400)
                                # Download button for the generated cover letter
                                st.download_button(
                                    label="Download Cover Letter",
                                    data=cover_letter,
                                    file_name="cover_letter.txt",
                                    mime="text/plain"
                                )
                                # View in browser (data URL)
                                import urllib.parse
                                data_url = f"data:text/plain;charset=utf-8,{urllib.parse.quote(cover_letter)}"
                                st.markdown(f"[Open Cover Letter in Browser]({data_url})", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Error generating cover letter: {e}")
                                if "API key" in str(e):
                                    st.warning("💡 It looks like your API Key might be invalid. Please use the 'Reset Configuration' button in the sidebar to enter a new key.")
                        
                        with tab2:
                            st.subheader("Tailored CV")
                            try:
                                # Trim description for CV tailoring
                                safe_description = job_details['description'][:2000]
                                new_cv = cv_processor.tailor_cv(cv_text, safe_description)
                                validation_report = cv_processor.validate_cv(new_cv)
                                if "Missing sections" in validation_report:
                                     st.warning(f"⚠️ CV Validation: {validation_report}")
                                else:
                                     st.success(f"✅ CV Validation: {validation_report}")
                                # Part of main_app
                                import difflib
                                # Highlight added/changed lines in the tailored CV
                                diff_lines = difflib.unified_diff(cv_text.splitlines(), new_cv.splitlines(), lineterm='')
                                highlighted_html = ""
                                for line in diff_lines:
                                    # Skip diff metadata lines
                                    if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                                        continue
                                    if line.startswith('+'):
                                        # Added line (skip the leading '+')
                                        highlighted_html += f"<span style='background:#a6f3a6; color:black;'>{line[1:]}</span><br>"
                                    elif line.startswith('-'):
                                        # Removed line (show with red background and strikethrough)
                                        highlighted_html += f"<span style='background:#f7c6c7; color:black; text-decoration:line-through;'>{line[1:]}</span><br>"
                                    else:
                                        # Unchanged/context line
                                        highlighted_html += f"{line}<br>"
                                import streamlit.components.v1 as components
                                if highlighted_html:
                                    components.html(highlighted_html, height=600, scrolling=True)
                                else:
                                    if new_cv and new_cv.strip():
                                        st.info("No significant changes detected or CV was rewritten completely. Showing tailored CV below:")
                                        st.markdown(new_cv)
                                    else:
                                        st.error("Tailored CV generation returned empty result.")
                                # Prepare filename based on job title
                                import re
                                safe_title = re.sub(r'[^a-zA-Z0-9]', '_', job_details.get('title', 'Job')).strip('_')
                                
                                # Download button for the tailored CV (Markdown)
                                st.download_button(
                                    label="Download Tailored CV (Markdown)",
                                    data=new_cv,
                                    file_name=f"Tailored_CV_{safe_title}.md",
                                    mime="text/markdown"
                                )
                                
                                # Download button for the tailored CV (Word)
                                from docx_utils import create_docx_from_markdown
                                docx_filename = f"Tailored_CV_{safe_title}.docx"
                                create_docx_from_markdown(new_cv, docx_filename)
                                
                                with open(docx_filename, "rb") as f:
                                    st.download_button(
                                        label="Download Tailored CV (Word)",
                                        data=f,
                                        file_name=docx_filename,
                                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                    )
                            except Exception as e:
                                st.error(f"Error generating tailored CV: {e}")
                                if "API key" in str(e):
                                    st.warning("💡 It looks like your API Key might be invalid. Please use the 'Reset Configuration' button in the sidebar to enter a new key.")
                        
                        with tab3:
                            st.subheader("Upload & Track")
                            
                            if google_handler is None:
                                st.warning("⚠️ Google Drive integration is not configured.")
                                st.info("To enable this feature, please configure `[gcp_service_account]` in Streamlit Secrets or upload `credentials.json` locally.")
                            else:
                                if st.button("Upload to Google Drive & Log"):
                                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                    company_name = job_details['company'] if job_details['company'] != "Unknown Company" else "Job"
                                    
                                    with st.spinner("Uploading..."):
                                        cl_link = google_handler.upload_file(cover_letter, f"Cover_Letter_{company_name}_{timestamp}.txt")
                                        cv_link = google_handler.upload_file(new_cv, f"CV_{company_name}_{timestamp}.txt")
                                        
                                        if cl_link and cv_link:
                                            st.success("Files Uploaded!")
                                            st.markdown(f"[View Cover Letter]({cl_link})")
                                            st.markdown(f"[View Tailored CV]({cv_link})")
                                            
                                            # Log to Sheets
                                            spreadsheet_id = os.getenv("SPREADSHEET_ID")
                                            if not spreadsheet_id:
                                                spreadsheet_id = google_handler.create_sheet(title="Job Applications Tracker")
                                                st.info(f"Created new Sheet. ID: {spreadsheet_id}")
                                            
                                            job_data = {
                                                'date': datetime.datetime.now().strftime("%Y-%m-%d"),
                                                'company': company_name,
                                                'title': job_details['title'],
                                                'link': job_details['link'],
                                                'status': 'Applied',
                                                'cv_link': cv_link,
                                                'cover_letter_link': cl_link
                                            }
                                            
                                            if google_handler.log_job(job_data, spreadsheet_id):
                                                st.success("Logged to Google Sheets!")
                                            else:
                                                st.error("Failed to log to Sheets.")
                                        else:
                                            st.error("Failed to upload files.")
                    else:
                        st.error("Failed to extract job details. Please check the URL.")
if is_configured():
    try:
        main_app()
    except Exception as e:
        st.error("An unexpected error occurred in the application.")
        st.error(f"Error details: {e}")
        import traceback
        st.code(traceback.format_exc())
else:
    setup_screen()
