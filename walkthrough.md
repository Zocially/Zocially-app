# Job Hunter Fix Walkthrough

I have updated the "Job Hunter" application to fix the crash on `zocially.co.in`.
The issue was caused by the authentication method (`InstalledAppFlow`) which tries to open a browser window—something that isn't possible on a cloud server.

I have implemented a fix that allows the app to use **Streamlit Secrets** with a Service Account, which is the standard, secure way to handle Google authentication in the cloud.

## Changes Made
-   **Modified `google_handler.py`**: Added logic to look for `[gcp_service_account]` in Streamlit Secrets.
-   **Updated `app.py`**:
    -   Added a check for Secrets configuration.
    -   improved error reporting (errors are now shown in the UI instead of a blank screen).
    -   Updated the "Setup" screen with new instructions.

## 🚀 Final Step: Configure Secrets (Optional)

**You can now run the app with just the Gemini API Key!**

If you want to enable the **"Upload to Google Drive"** feature, you need to configure the Google Cloud Service Account. Otherwise, you can skip this section.

### To Enable Google Drive Integration:

1.  **Get your Service Account Key**:
    -   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    -   Select your project.
    -   Go to **IAM & Admin** > **Service Accounts**.
    -   Create a new Service Account.
    -   Go to **Keys** > **Add Key** > **Create new key** (JSON).
    -   Download the JSON file.

2.  **Configure Streamlit Secrets**:
    -   Go to your [Streamlit Cloud Dashboard](https://share.streamlit.io/).
    -   Find your app (`zocially-app`).
    -   Click **Settings** > **Secrets**.
    -   Add your Service Account JSON under `[gcp_service_account]`:

```toml
GOOGLE_API_KEY = "your-gemini-api-key-here"

[gcp_service_account]
type = "service_account"
project_id = "..."
# ... paste the rest of your JSON content here
```

> [!TIP]
> You can just copy the entire JSON content from your key file and paste it under `[gcp_service_account]`. Make sure to convert the JSON syntax to TOML (Streamlit usually handles the conversion if you paste it right, otherwise just ensure the structure matches above).
> **Easier way**: Just define the keys inside `[gcp_service_account]` matching exactly what is in your JSON.

4.  **Restart the App**:
    -   Once saved, click "Reboot" or "Manage app" -> "Reboot" in Streamlit Cloud.
    -   Your Job Hunter AI should now be fully functional!
