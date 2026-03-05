const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseLink = document.querySelector('.browse-link');
const loader = document.getElementById('loader');
const uploadText = document.querySelector('.upload-text');
const uploadIcon = document.querySelector('.upload-icon');
const resultContainer = document.getElementById('result-container');
const resetBtn = document.getElementById('reset-btn');

// --- New Queue UI Elements ---
const queueUi = document.getElementById('queue-ui');
const queueText = document.getElementById('queue-text');
const startProcessBtn = document.getElementById('start-process-btn');
const clearQueueBtn = document.getElementById('clear-queue-btn');

let queuedFiles = [];

// --- Drag & Drop Events ---
if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
        dropZone.style.transform = 'scale(1.02)';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'white';
        dropZone.style.transform = 'scale(1)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'white';
        dropZone.style.transform = 'scale(1)';
        const files = e.dataTransfer.files;
        if (files.length) queueFiles(files);
    });

    // --- Click Events ---
    dropZone.addEventListener('click', () => fileInput.click());
}

if (fileInput) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) queueFiles(fileInput.files);
    });
}

// --- Queue Logic ---
function queueFiles(files) {
    // Convert FileList to Array and filter valid types
    const validFiles = Array.from(files).filter(f =>
        ['image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'application/pdf'].includes(f.type)
    );

    if (validFiles.length === 0) return;

    // Add to our queue array
    queuedFiles = queuedFiles.concat(validFiles);

    // Update UI
    uploadText.innerText = "Files ready!";
    queueUi.classList.remove('hidden');

    const count = queuedFiles.length;
    queueText.innerHTML = `<span style="color: var(--primary); font-size: 1.2rem;">${count}</span> invoice${count > 1 ? 's' : ''} selected and ready for processing.`;

    // Hide global actions if they were visible from a previous run
    document.getElementById('global-actions').classList.add('hidden');
}

if (clearQueueBtn) {
    clearQueueBtn.addEventListener('click', () => {
        queuedFiles = [];
        queueUi.classList.add('hidden');
        uploadText.innerHTML = 'Drag & Drop invoices or <span class="browse-link">Browse</span>';
        fileInput.value = ''; // Reset input
    });
}

if (startProcessBtn) {
    startProcessBtn.addEventListener('click', () => {
        if (queuedFiles.length > 0) {
            handleFiles(queuedFiles);
        }
    });
}

// --- Main Logic ---
async function handleFiles(files) {
    if (files.length === 0) return;

    // Reset UI
    const batchProgress = document.getElementById('batch-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const globalActions = document.getElementById('global-actions');
    const downloadBtn = document.getElementById('download-report-btn');
    const processMoreBtn = document.getElementById('process-more-btn');

    // Reset Logic for New Batch
    processMoreBtn.onclick = () => {
        // Reset UI
        batchProgress.classList.add('hidden');
        globalActions.classList.add('hidden');
        uploadIcon.classList.remove('hidden');
        uploadText.innerHTML = 'Drag & Drop invoices or <span class="browse-link">Browse</span>';

        // Reset Progress
        progressBar.style.width = '0%';
        progressText.innerText = 'Processed 0 / 0';

        // Reset Input and Queue
        fileInput.value = '';
        queuedFiles = [];

        // Re-attach browse link listener since we overwrote HTML
        document.querySelector('.browse-link').addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    };

    queueUi.classList.add('hidden');
    uploadIcon.classList.add('hidden');
    batchProgress.classList.remove('hidden');
    globalActions.classList.add('hidden');
    uploadText.innerText = "Processing batch...";

    let processedCount = 0;
    const total = files.length;

    // Generate unique Batch ID
    const batchId = Date.now().toString();

    // Iterate
    for (const file of files) {
        if (!['image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'application/pdf'].includes(file.type)) continue;

        // Update Text
        uploadText.innerText = `Processing: ${file.name}`;

        try {
            await processSingleFile(file, batchId);
        } catch (e) {
            console.error(e);
        }

        processedCount++;
        // Update Progress
        const percent = (processedCount / total) * 100;
        progressBar.style.width = percent + '%';
        progressText.innerText = `Processed ${processedCount} / ${total}`;
    }

    // Done
    uploadText.innerText = "Batch Complete!";
    globalActions.classList.remove('hidden');

    // Enable Download with Batch ID
    downloadBtn.onclick = () => {
        window.location.href = `http://127.0.0.1:5000/download_report?batch_id=${batchId}`;
    };

    // Enable Analyse Results button
    const analyseBtn = document.getElementById('analyse-results-btn');
    if (analyseBtn) {
        analyseBtn.onclick = () => {
            window.location.href = `/analytics?batch_id=${batchId}`;
        };
    }
}

async function processSingleFile(file, batchId) {
    const formData = new FormData();
    formData.append('file', file);

    // Get classification method from UI toggle
    const toggleElement = document.getElementById('classification-method-toggle');
    const classificationMethod = toggleElement && toggleElement.checked ? 'gemini' : 'local_nn';

    // Add query param save=true, batch_id, AND classification method
    const headers = {};
    const savedApiKey = localStorage.getItem('gemini_api_key');
    if (savedApiKey) {
        headers['X-API-Key'] = savedApiKey;
    }

    const response = await fetch(`http://127.0.0.1:5000/upload?save=true&batch_id=${batchId}&method=${classificationMethod}`, {
        method: 'POST',
        body: formData,
        headers: headers
    });

    // We don't need to show every single result card for batch upload,
    // just ensure it processed.
    return response.json();
}

function showResults(data) {
    // Legacy function support if needed, but for batch we skip showing individual cards
    // unless it was a single file? 
    // For simplicity, let's just stick to the Batch UI for everything.
}

function downloadCSV(data) {
    const headers = ["Filename", "Date", "Total Amount", "Category"];
    const rows = [[data.filename, data.date, data.total_amount, data.category]];

    let csvContent = "data:text/csv;charset=utf-8,"
        + headers.join(",") + "\n"
        + rows.map(e => e.join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "invoice_report.csv");
    document.body.appendChild(link); // Required for FF
    link.click();
    document.body.removeChild(link);
}

function resetUIAfterError() {
    loader.classList.add('hidden');
    uploadIcon.classList.remove('hidden');
    uploadText.innerHTML = 'Drag & Drop your invoice or <span class="browse-link">Browse</span>';
}



// --- Scroll Reveal Animation ---
const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target); // Only animate once
        }
    });
}, observerOptions);

document.querySelectorAll('.scroll-reveal').forEach(el => {
    observer.observe(el);
});

// ===================================================================
// SETTINGS MODAL LOGIC
// ===================================================================
(function initSettings() {
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const settingsOverlay = document.getElementById('settings-overlay');
    const apiKeyInput = document.getElementById('api-key-input');
    const saveBtn = document.getElementById('save-api-key-btn');
    const apiStatus = document.getElementById('api-status');
    const settingsDot = document.getElementById('settings-dot');

    if (!settingsBtn || !settingsModal) return;

    // --- Open / Close ---
    function openSettings() {
        settingsModal.classList.add('visible');
        settingsOverlay.classList.add('visible');
        // Show masked key if stored
        const stored = localStorage.getItem('gemini_api_key');
        if (stored) {
            apiKeyInput.value = stored;
        }
        setTimeout(() => apiKeyInput.focus(), 300);
    }

    function closeSettings() {
        settingsModal.classList.remove('visible');
        settingsOverlay.classList.remove('visible');
    }

    settingsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openSettings();
    });

    settingsOverlay.addEventListener('click', closeSettings);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeSettings();
    });

    // Prevent modal click from closing
    settingsModal.addEventListener('click', (e) => e.stopPropagation());

    // --- Save Key ---
    function saveApiKey() {
        const key = apiKeyInput.value.trim();
        if (!key) return;

        localStorage.setItem('gemini_api_key', key);
        updateStatus(true);

        // Brief success flash
        saveBtn.textContent = '✓ Saved';
        saveBtn.style.background = 'linear-gradient(135deg, #34d399, #059669)';
        setTimeout(() => {
            saveBtn.textContent = 'Save';
            saveBtn.style.background = '';
        }, 1500);
    }

    saveBtn.addEventListener('click', saveApiKey);
    apiKeyInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') saveApiKey();
    });

    // --- Update Status ---
    function updateStatus(hasKey) {
        if (hasKey) {
            apiStatus.className = 'api-status configured';
            apiStatus.innerHTML = '<span><i class="fa-solid fa-circle-check"></i> API Key Configured</span><button class="btn-clear-key" id="clear-api-key-btn"><i class="fa-solid fa-trash-can"></i> Clear</button>';
            settingsDot.className = 'status-dot active';

            // Attach clear handler
            document.getElementById('clear-api-key-btn').addEventListener('click', () => {
                localStorage.removeItem('gemini_api_key');
                apiKeyInput.value = '';
                updateStatus(false);
            });
        } else {
            apiStatus.className = 'api-status not-configured';
            apiStatus.innerHTML = '<span><i class="fa-solid fa-circle-xmark"></i> No API Key configured</span>';
            settingsDot.className = 'status-dot inactive';
        }
    }

    // --- Init state on page load ---
    const existingKey = localStorage.getItem('gemini_api_key');
    updateStatus(!!existingKey);
})();
