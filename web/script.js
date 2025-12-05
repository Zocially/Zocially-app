// const API_URL = "http://localhost:8000"; // Removed to use relative paths
const API_URL = "http://localhost:8000"; // Explicitly set for local dev

// State
let cvText = "";

// Elements that need to be globally accessible or initialized later
// loader and loaderText are used by showLoader/hideLoader which are global functions,
// but they are also accessed within the DOMContentLoaded block.
// To ensure they are available when needed, they should be defined within DOMContentLoaded.
// However, the provided instruction snippet only moves dropZone and fileInput.
// For now, I will keep loader and loaderText global but ensure they are initialized correctly.
// A better approach would be to pass them to functions or define them within the DOMContentLoaded scope.
let loader;
let loaderText;

// Global variables for loader message cycling
let loaderInterval;
const loadingMessages = [
    "Reading your CV...",
    "Analyzing your skills...",
    "Matching with job requirements...",
    "Drafting your cover letter...",
    "Tailoring your resume...",
    "Polishing the formatting...",
    "Almost there..."
];

function showLoader(initialText = "Processing...") {
    const loader = document.getElementById('loader');
    const text = document.getElementById('loader-text');
    const subtext = document.getElementById('loader-subtext');

    if (loader && text) {
        text.textContent = initialText;
        if (subtext) subtext.textContent = "Please wait...";

        loader.classList.remove('hidden');
        loader.style.display = 'flex'; // Override inline style if present

        // Start message cycling
        let msgIndex = 0;
        if (subtext) {
            clearInterval(loaderInterval);
            loaderInterval = setInterval(() => {
                subtext.textContent = loadingMessages[msgIndex % loadingMessages.length];
                msgIndex++;
            }, 2000); // Change message every 2 seconds
        }
    }
}

function hideLoader() {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.classList.add('hidden');
        loader.style.display = 'none'; // Force hide
        clearInterval(loaderInterval);
    }
}

// --- Initialization ---

document.addEventListener('DOMContentLoaded', () => {
    log("Script loaded and DOM ready");

    // Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('cv-upload');
    // loader = document.getElementById('loader'); // Initialized by showLoader/hideLoader directly
    // loaderText = document.getElementById('loader-text'); // Initialized by showLoader/hideLoader directly

    // File Upload Listeners
    if (dropZone && fileInput) {
        dropZone.addEventListener('click', (e) => {
            // Prevent double-trigger if clicking the input directly
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.borderColor = '#4f46e5'; });
        dropZone.addEventListener('dragleave', (e) => { e.preventDefault(); dropZone.style.borderColor = '#cbd5e1'; });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.style.borderColor = '#cbd5e1';
            if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
        });
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) handleFileUpload(e.target.files[0]);
        });
        log("File upload listeners attached");
    } else {
        log("ERROR: Drop zone or file input not found");
    }

    // Job Analysis Listener
    const analyzeBtn = document.getElementById('analyze-btn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            const url = document.getElementById('job-url').value;
            if (!url) return showError("Please enter a URL");

            showLoader("Analyzing Job...");
            try {
                const res = await fetch(`${API_URL}/analyze-job`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });
                if (!res.ok) throw new Error("Failed to analyze job");

                const data = await res.json();
                document.getElementById('job-title').value = data.title || "";
                document.getElementById('job-company').value = data.company || "";
                document.getElementById('job-desc').value = data.description || "";

                document.getElementById('job-details-form').classList.remove('hidden');
            } catch (e) {
                showError(e.message);
            } finally {
                hideLoader();
            }
        });
    }

    // Generate Application Listener
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            if (!cvText) return showError("Please upload a CV first");

            showLoader("Generating Application... (This may take a minute)");
            try {
                const payload = {
                    cv_text: cvText,
                    job_description: document.getElementById('job-desc').value,
                    job_title: document.getElementById('job-title').value,
                    company: document.getElementById('job-company').value,
                    summary: document.getElementById('job-summary').value
                };

                const res = await fetch(`${API_URL}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) throw new Error("Generation failed");

                const data = await res.json();

                // Populate Results
                document.getElementById('cover-letter-output').value = data.cover_letter;
                document.getElementById('cv-output').value = data.tailored_cv;

                // Validation Report
                const reportDiv = document.getElementById('validation-report');
                reportDiv.textContent = `Validation: ${data.validation}`;
                reportDiv.style.backgroundColor = data.validation.includes("Missing") ? "#fee2e2" : "#d1fae5";
                reportDiv.style.color = data.validation.includes("Missing") ? "#991b1b" : "#065f46";

                document.getElementById('results-section').classList.remove('hidden');
                document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });

            } catch (e) {
                showError(e.message);
            } finally {
                hideLoader();
            }
        });
    }

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
        });
    });

    // Test Connection Listener
    const testBtn = document.getElementById('test-conn-btn');
    if (testBtn) {
        testBtn.addEventListener('click', async () => {
            log("Testing connection to " + API_URL + "/health");
            try {
                const res = await fetch(`${API_URL}/health`);
                log(`Response status: ${res.status}`);

                if (res.ok) {
                    const data = await res.json();
                    log("Connection Successful: " + JSON.stringify(data));
                    alert("Connected! Server says: " + data.message);
                } else {
                    log("Connection Failed: " + res.status);
                    alert("Connection Failed: " + res.status);
                }
            } catch (e) {
                console.error(e);
                log(`Connection Error (${e.name}): ${e.message}`);
                alert(`Connection Error: ${e.message}\nCheck Debug Log for details.`);
            }
        });
    }

    // Download DOCX
    const downloadBtn = document.getElementById('download-docx-btn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', async () => {
            const cvText = document.getElementById('cv-output').value;
            if (!cvText) return showError("No CV to download");

            const jobTitle = document.getElementById('job-title').value || "Job";
            const company = document.getElementById('job-company').value || "Company";
            const filename = `${jobTitle}_${company}_CV.docx`;

            showLoader("Generating DOCX...");
            try {
                const res = await fetch(`${API_URL}/download-docx`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ cv_text: cvText, filename: filename })
                });

                if (!res.ok) throw new Error("Download failed");

                // Trigger download
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                a.remove();

            } catch (e) {
                showError(e.message);
            } finally {
                hideLoader();
            }
        });
    }

    // Submit / Upload Listener
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', async () => {
            showLoader("Uploading to Drive...");
            try {
                const payload = {
                    cv_text: document.getElementById('cv-output').value,
                    cover_letter: document.getElementById('cover-letter-output').value,
                    job_title: document.getElementById('job-title').value,
                    company: document.getElementById('job-company').value,
                    job_link: document.getElementById('job-url').value
                };

                const res = await fetch(`${API_URL}/submit`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) throw new Error("Upload failed");

                const data = await res.json();
                const statusDiv = document.getElementById('submit-status');
                statusDiv.innerHTML = `
                    <p style="color: green; margin-top: 10px;">✅ Uploaded Successfully!</p>
                    <p><a href="${data.cv_link}" target="_blank">View CV</a> | <a href="${data.cover_letter_link}" target="_blank">View Cover Letter</a></p>
                `;

            } catch (e) {
                showError(e.message);
            } finally {
                hideLoader();
            }
        });
    }
});

// --- Functions ---

function log(msg) {
    console.log(msg);
    const logDiv = document.getElementById('debug-log');
    if (logDiv) {
        logDiv.innerHTML += `<div>${new Date().toLocaleTimeString()} - ${msg}</div>`;
        logDiv.scrollTop = logDiv.scrollHeight;
    }
}

async function handleFileUpload(file) {
    log(`Starting file upload: ${file.name}`);
    if (file.type !== 'application/pdf') return showError("Only PDF files are allowed");

    showLoader("Reading CV...");
    const formData = new FormData();
    formData.append('file', file);

    try {
        log(`Sending POST request to ${API_URL}/upload-cv`);
        const res = await fetch(`${API_URL}/upload-cv`, {
            method: 'POST',
            body: formData
        });
        log(`Response status: ${res.status}`);

        if (!res.ok) {
            const errText = await res.text();
            throw new Error(`Upload failed: ${res.status} ${errText}`);
        }

        const data = await res.json();
        log("Data parsed successfully");
        cvText = data.text;

        // Update UI
        document.getElementById('cv-filename').textContent = file.name;
        document.getElementById('cv-status').classList.remove('hidden');
        document.getElementById('drop-zone').classList.add('hidden');

        // Show Assessment
        document.getElementById('assessment-content').innerHTML = marked.parse(data.assessment);
        document.getElementById('assessment-result').classList.remove('hidden');

        // Show Next Section
        document.getElementById('job-section').classList.remove('hidden');
        log("UI updated successfully");
    } catch (e) {
        log(`ERROR: ${e.message}`);
        showError(e.message);
    } finally {
        log("Hiding loader");
        hideLoader();
    }
}

function showLoader(text) {
    loaderText.textContent = text;
    loader.classList.remove('hidden');
}

function hideLoader() {
    loader.classList.add('hidden');
}

function showError(message) {
    hideLoader(); // Ensure loader is gone

    // Create or find error container
    let errorDiv = document.getElementById('error-container');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'error-container';
        errorDiv.style.position = 'fixed';
        errorDiv.style.top = '20px';
        errorDiv.style.right = '20px';
        errorDiv.style.zIndex = '2000';
        document.body.appendChild(errorDiv);
    }

    // Create toast
    const toast = document.createElement('div');
    toast.style.background = '#fee2e2';
    toast.style.color = '#991b1b';
    toast.style.padding = '1rem';
    toast.style.marginBottom = '10px';
    toast.style.borderRadius = '8px';
    toast.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.justifyContent = 'space-between';
    toast.style.minWidth = '300px';

    toast.innerHTML = `
        <span>${message}</span>
        <button style="background:none;border:none;color:inherit;cursor:pointer;font-weight:bold;margin-left:10px;">&times;</button>
    `;

    toast.querySelector('button').onclick = () => toast.remove();

    errorDiv.appendChild(toast);

    // Auto remove after 5s
    setTimeout(() => {
        if (toast.parentElement) toast.remove();
    }, 5000);
}
