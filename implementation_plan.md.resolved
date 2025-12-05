# Job Hunter Application Implementation Plan

## Goal Description
Build a Python-based automation tool to:
1.  Assess the user's CV.
2.  Find relevant job openings in the UK.
3.  Tailor the CV and write a cover letter for each job.
4.  Upload documents to Google Drive.
5.  Track applications in Google Sheets.

## User Review Required
> [!IMPORTANT]
> **Credentials Needed**:
> 1.  **Google Cloud Service Account JSON**: Required for accessing Google Drive and Sheets APIs.
> 2.  **LLM API Key**: Required for Gemini or OpenAI to process text.
>
> **Job Search Strategy**:
> Automated job searching is complex due to anti-bot measures on sites like LinkedIn/Indeed.
> *   **Option A**: Use a specialized API (e.g., SerpApi, JSearch).
> *   **Option B**: User provides a list of URLs manually.
> *   **Option C**: Simple Google Search scraping (less reliable).
> *   **Recommendation**: Option A or B.

## Proposed Changes

### Project Structure
We will create a modular Python project in the workspace.

#### [NEW] [main.py](file:///Users/arunkumarkv/.gemini/antigravity/brain/1174efc3-cb8f-40f3-9fa7-5e2a294ae156/main.py)
- Orchestrates the workflow.
- Loads configuration.

#### [NEW] [cv_processor.py](file:///Users/arunkumarkv/.gemini/antigravity/brain/1174efc3-cb8f-40f3-9fa7-5e2a294ae156/cv_processor.py)
- Reads PDF/DOCX resume.
- Uses LLM to assess and amend the CV content.
- Generates new PDF/DOCX.

#### [NEW] [job_finder.py](file:///Users/arunkumarkv/.gemini/antigravity/brain/1174efc3-cb8f-40f3-9fa7-5e2a294ae156/job_finder.py)
- Implements the search strategy (API or Scraping).
- Extracts job description and requirements.

#### [NEW] [google_handler.py](file:///Users/arunkumarkv/.gemini/antigravity/brain/1174efc3-cb8f-40f3-9fa7-5e2a294ae156/google_handler.py)
- Authenticates with Google APIs.
- Uploads files to Drive.
- Appends rows to Sheets.

#### [NEW] [requirements.txt](file:///Users/arunkumarkv/.gemini/antigravity/brain/1174efc3-cb8f-40f3-9fa7-5e2a294ae156/requirements.txt)
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`
- `openai` or `google-generativeai`
- `PyPDF2` or `pdfplumber`
- `python-docx`

## Verification Plan

### Automated Tests
- We will write unit tests for the parsing and Google API helper functions (mocking the actual API calls).

### Manual Verification
1.  **Setup**: Place `credentials.json` and `resume.pdf` in the project root.
2.  **Run**: Execute `python main.py`.
3.  **Verify**:
    - Check console output for job findings.
    - Check Google Drive for new folder/files.
    - Check Google Sheet for new row.
