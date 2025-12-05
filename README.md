# Job Hunter Setup

## 1. Google Cloud Credentials
To use Google Drive and Sheets, you need a `credentials.json` file.
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable **Google Drive API** and **Google Sheets API**.
4. Go to **Credentials** > **Create Credentials** > **OAuth client ID**.
5. Select **Desktop app**.
6. Download the JSON file and rename it to `credentials.json`.
7. Place `credentials.json` in this folder.

## 2. LLM API Key
Create a `.env` file in this folder with your API key:
```
GOOGLE_API_KEY=your_gemini_key_here
# OR
OPENAI_API_KEY=your_openai_key_here
```

## 3. Resume
Place your resume (PDF or DOCX) in this folder and rename it to `resume.pdf` (or update `main.py`).
