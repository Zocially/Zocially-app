import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import existing logic
from cv_processor import CVProcessor
from job_finder import JobFinder
from google_handler import GoogleHandler

# Load env vars
load_dotenv()

app = FastAPI(title="Job Hunter API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Static Files (Frontend)
app.mount("/static", StaticFiles(directory="web"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('web/index.html')

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# Initialize Handlers
# Note: We initialize them globally for simplicity in this script.
# In a production app, you might want dependency injection.
try:
    cv_processor = CVProcessor()
    job_finder = JobFinder()
    
    # Google Handler requires credentials
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(base_dir, 'credentials.json')
    token_path = os.path.join(base_dir, 'token.pickle')
    
    # Check if we can initialize GoogleHandler
    if os.path.exists(cred_path) or os.path.exists(token_path):
        google_handler = GoogleHandler(credentials_file=cred_path, token_file=token_path)
    else:
        google_handler = None
        print("Warning: Google Credentials not found. Upload/Log features will be disabled.")

except Exception as e:
    print(f"Error initializing handlers: {e}")
    cv_processor = None
    job_finder = None
    google_handler = None

# Data Models
class JobRequest(BaseModel):
    url: str

class GenerateRequest(BaseModel):
    cv_text: str
    job_description: str
    job_title: str
    company: str
    summary: Optional[str] = ""

class SubmitRequest(BaseModel):
    cv_text: str
    cover_letter: str
    job_title: str
    company: str
    job_link: str

@app.get("/")
def read_root():
    return {"status": "Job Hunter API is running"}

@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    if not cv_processor:
        raise HTTPException(status_code=500, detail="CV Processor not initialized (Check API Key)")
    
    try:
        # Save temp file
        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Extract text
        text = cv_processor.extract_text(temp_filename)
        
        # Assess
        assessment = cv_processor.assess_cv(text)
        
        # Cleanup
        os.remove(temp_filename)
        
        return {
            "text": text,
            "assessment": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-job")
async def analyze_job(request: JobRequest):
    if not job_finder:
        raise HTTPException(status_code=500, detail="Job Finder not initialized")
    
    try:
        details = job_finder.extract_job_details(request.url)
        if not details:
            raise HTTPException(status_code=404, detail="Could not extract job details")
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_application(request: GenerateRequest):
    if not cv_processor:
        raise HTTPException(status_code=500, detail="CV Processor not initialized")
    
    try:
        # Prepare job info for cover letter
        job_info = {
            "title": request.job_title,
            "company": request.company,
            "description": request.job_description,
            "summary": request.summary
        }
        
        # Generate Cover Letter
        cover_letter = cv_processor.generate_cover_letter(request.cv_text, job_info)
        
        # Tailor CV
        # We use the raw description for tailoring to ensure accuracy
        tailored_cv = cv_processor.tailor_cv(request.cv_text, request.job_description)
        
        # Validate
        validation = cv_processor.validate_cv(tailored_cv)
        
        return {
            "cover_letter": cover_letter,
            "tailored_cv": tailored_cv,
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class DownloadRequest(BaseModel):
    cv_text: str
    filename: str = "Tailored_CV.docx"

@app.post("/download-docx")
async def download_docx(request: DownloadRequest):
    if not cv_processor:
        raise HTTPException(status_code=500, detail="CV Processor not initialized")
    
    try:
        # Ensure filename is safe
        safe_filename = "".join([c for c in request.filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
        if not safe_filename.endswith('.docx'):
            safe_filename += '.docx'
            
        # Generate file
        filepath = cv_processor.generate_docx(request.cv_text, safe_filename)
        
        # Return file
        return FileResponse(filepath, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=safe_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit")
async def submit_application(request: SubmitRequest):
    if not google_handler:
        raise HTTPException(status_code=503, detail="Google Handler not initialized (Missing credentials)")
    
    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Upload files
        cl_name = f"Cover_Letter_{request.company}_{timestamp}.txt"
        cv_name = f"CV_{request.company}_{timestamp}.txt"
        
        cl_link = google_handler.upload_file(request.cover_letter, cl_name)
        cv_link = google_handler.upload_file(request.cv_text, cv_name)
        
        if not cl_link or not cv_link:
            raise HTTPException(status_code=500, detail="Failed to upload files to Drive")
            
        # Log to Sheets
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        if not spreadsheet_id:
            # Create if not exists (simple logic for now)
            spreadsheet_id = google_handler.create_sheet(title="Job Applications Tracker")
            # Ideally we should save this ID back to env or config, but for now we return it
        
        job_data = {
            'date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'company': request.company,
            'title': request.job_title,
            'link': request.job_link,
            'status': 'Applied',
            'cv_link': cv_link,
            'cover_letter_link': cl_link
        }
        
        logged = google_handler.log_job(job_data, spreadsheet_id)
        
        return {
            "status": "success",
            "cv_link": cv_link,
            "cover_letter_link": cl_link,
            "logged_to_sheet": logged,
            "spreadsheet_id": spreadsheet_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
