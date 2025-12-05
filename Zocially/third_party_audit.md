# Zocially Third-Party Integration Audit

This document lists all external services and third-party websites that the Zocially application interacts with. Use this for your personal records and privacy compliance.

## 1. Backend & Database
| Service | Purpose | Files Involved | Data Shared |
| :--- | :--- | :--- | :--- |
| **Supabase** | **Database** for Deals, Orders, and (Planned) Sponsors. | `Zocially/script.js`, `Zocially/scripts/sync_supabase.py` | User orders, email addresses, deal information. |
| **Google Gemini AI** | **AI Processing** for CV tailoring and Cover Letters. | `app.py`, `cv_processor.py` | CV text, Job Descriptions. |
| **Google Sheets** | **Logging** job applications (Job Hunter). | `app.py`, `google_handler.py` | Company name, job title, application status. |
| **Google Drive** | **Storage** for generated CVs and Cover Letters. | `app.py`, `google_handler.py` | Generated PDF/Text files. |

## 2. Frontend Services
| Service | Purpose | Files Involved | Data Shared |
| :--- | :--- | :--- | :--- |
| **EmailJS** | **Sending Emails** (Contact Form, Order Confirmation). | `Zocially/script.js` | Name, Email, Message content. |
| **PayPal** | **Payments** for Marketplace deals. | `Zocially/script.js` | Transaction details (redirects user). |
| **Google Fonts** | **Typography** (Outfit font). | All HTML files (`<head>`) | IP address (standard web request). |
| **JSDelivr (CDN)** | **Hosting Libraries** (Supabase SDK, EmailJS SDK). | All HTML files (`<head>`) | IP address (standard web request). |

## 3. Automation & Data Sources
| Service | Purpose | Files Involved | Data Shared |
| :--- | :--- | :--- | :--- |
| **GitHub Actions** | **Automation** (Daily updates). | `.github/workflows/update_sponsors.yml` | Source code, Secrets (Supabase keys). |
| **GOV.UK** | **Data Source** for Sponsor Licence Register. | `Zocially/scripts/update_sponsors.py` | None (Public data download). |

## 4. Credentials & Secrets
Ensure these keys are kept private in your `.env` file or GitHub Secrets:
*   `SUPABASE_URL` & `SUPABASE_KEY`
*   `GOOGLE_API_KEY` (Gemini)
*   `SPREADSHEET_ID` (Google Sheets)
*   `EMAILJS_PUBLIC_KEY`, `SERVICE_ID`, `TEMPLATE_ID` (Exposed in frontend code, which is standard for EmailJS, but ensure origin protection in EmailJS dashboard).
