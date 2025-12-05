# Deployment Guide for Zocially

To offer a "seamless service" where your users can access both the website and the Job Hunter tool online, you need to host two separate components.

## Architecture
1.  **Frontend (Zocially Folder)**: These are static files (HTML, CSS, JS).
2.  **Backend (Root Folder)**: This is a Python application (`app.py`) using Streamlit.

## Recommended Hosting Strategy

### Step 1: Host the Backend (Streamlit)
**Platform**: [Streamlit Community Cloud](https://streamlit.io/cloud) (Free & Easiest)
1.  Push your code to GitHub.
2.  Sign up for Streamlit Cloud and connect your GitHub repository.
3.  Select the `app.py` file as the main entry point.
4.  **Important**: In the "Advanced Settings" on Streamlit Cloud, you must add your secrets (API Keys) that are currently in your `.env` file (`GOOGLE_API_KEY`, etc.).
5.  Once deployed, you will get a URL (e.g., `https://your-app.streamlit.app`).

### Step 2: Update the Frontend
1.  Open `Zocially/job-hunter.html`.
2.  Find the `<iframe>` line:
    ```html
    <iframe src="http://localhost:8501" ...></iframe>
    ```
3.  Change `http://localhost:8501` to your new Streamlit URL from Step 1.
    ```html
    <iframe src="https://your-app.streamlit.app" ...></iframe>
    ```

### Step 3: Host the Frontend (Zocially)
**Platform**: [Netlify](https://www.netlify.com/) or [Vercel](https://vercel.com/) (Free & Fast)
1.  Drag and drop the `Zocially` folder into Netlify Drop (or connect your Git repo and set the "Publish directory" to `Zocially`).
2.  You will get a website URL (e.g., `https://zocially.netlify.app`).

## Summary
- Your **Backend** runs on Streamlit servers and handles the heavy lifting (AI, PDF processing).
- Your **Frontend** runs on a fast CDN (Netlify) and shows the beautiful UI.
- The **Integration** happens via the `iframe` in `job-hunter.html`.
