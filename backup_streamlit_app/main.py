import os
import sys
import datetime
from dotenv import load_dotenv
from google_handler import GoogleHandler
from cv_processor import CVProcessor
from job_finder import JobFinder

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: Please set GOOGLE_API_KEY in .env file.")
        return

    # Initialize handlers
    # Initialize handlers
    base_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(base_dir, 'credentials.json')
    token_path = os.path.join(base_dir, 'token.pickle')
    
    try:
        google_handler = GoogleHandler(credentials_file=credentials_path, token_file=token_path)
        cv_processor = CVProcessor()
        job_finder = JobFinder()
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    print("Welcome to Job Hunter!")
    
    # 1. Assess CV
    resume_path = os.path.join(base_dir, "resume.pdf")
    if not os.path.exists(resume_path):
        print(f"Resume not found at {resume_path}. Please place your resume in the project folder.")
        return
        
    print("Reading CV...")
    cv_text = cv_processor.extract_text(resume_path)
    if not cv_text:
        print("Could not read CV text.")
        return

    print("\n--- CV Assessment ---")
    assessment = cv_processor.assess_cv(cv_text)
    print(assessment)
    print("---------------------\n")

    # 2. Get Job URL
    job_url = input("Enter a Job URL to apply for (or 'q' to quit): ").strip()
    if job_url.lower() == 'q':
        return

    # 3. Process Job
    print(f"Processing {job_url}...")
    job_details = job_finder.extract_job_details(job_url)
    
    if job_details:
        print(f"Found Job: {job_details['title']}")
        
        # Tailor CV and Cover Letter
        print("Generating Cover Letter...")
        cover_letter = cv_processor.generate_cover_letter(cv_text, job_details['description'])
        
        print("Tailoring CV...")
        new_cv_content = cv_processor.tailor_cv(cv_text, job_details['description'])
        
        # Upload to Drive
        # Create a folder for the company
        # For simplicity, we just upload to root or a specific folder if configured
        # Let's create a "Job Applications" folder if we can, but for now just upload
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name = job_details['company'] if job_details['company'] != "Unknown Company" else "Job"
        
        # Save locally first (optional, but good for debugging)
        # Then upload
        
        print("Uploading to Google Drive...")
        # We need to convert markdown/text to PDF or Docx for real usage, 
        # but for now we'll upload as text files or PDF if we had a converter.
        # Let's upload as text files for simplicity in this iteration.
        
        cl_link = google_handler.upload_file(cover_letter, f"Cover_Letter_{company_name}_{timestamp}.txt")
        cv_link = google_handler.upload_file(new_cv_content, f"CV_{company_name}_{timestamp}.txt")
        
        print(f"Uploaded! CV: {cv_link}, CL: {cl_link}")
        
        # Log to Sheets
        print("Logging to Google Sheets...")
        # We need a spreadsheet ID. For now, let's create one if we don't have it, 
        # or ask the user. For automation, let's try to find one or create one.
        # Ideally, we store the ID in .env or a config file. 
        # For this run, let's create a new sheet every time or hardcode if user provides.
        # Let's create one and print the ID for future use.
        
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            print("Creating new Google Sheet...")
            spreadsheet_id = google_handler.create_sheet(title="Job Applications Tracker")
            print(f"Created Sheet with ID: {spreadsheet_id}. Please save this to your .env as SPREADSHEET_ID for future runs.")
        
        job_data = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'company': company_name,
            'title': job_details['title'],
            'link': job_details['link'],
            'status': 'Applied',
            'cv_link': cv_link,
            'cover_letter_link': cl_link
        }
        
        google_handler.log_job(job_data, spreadsheet_id)
        print("Done!")
    else:
        print("Failed to extract job details.")

if __name__ == "__main__":
    main()
