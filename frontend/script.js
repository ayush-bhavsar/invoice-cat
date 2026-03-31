const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseLink = document.querySelector('.browse-link');
const loader = document.getElementById('loader');
const uploadText = document.querySelector('.upload-text');
const uploadIcon = document.querySelector('.upload-icon');
const resultContainer = document.getElementById('result-container');
const resetBtn = document.getElementById('reset-btn');

const queueUi = document.getElementById('queue-ui');
const queueText = document.getElementById('queue-text');
const startProcessBtn = document.getElementById('start-process-btn');
const clearQueueBtn = document.getElementById('clear-queue-btn');

let queuedFiles = [];

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

    dropZone.addEventListener('click', () => fileInput.click());
}

if (fileInput) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) queueFiles(fileInput.files);
    });
}

function queueFiles(files) {
    const validFiles = Array.from(files).filter(f =>
        ['image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'application/pdf'].includes(f.type)
    );

    if (validFiles.length === 0) return;

    queuedFiles = queuedFiles.concat(validFiles);

    uploadText.innerText = "Files ready!";
    queueUi.classList.remove('hidden');

    const count = queuedFiles.length;
    queueText.innerHTML = `<span style="color: var(--primary); font-size: 1.2rem;">${count}</span> invoice${count > 1 ? 's' : ''} locked and loaded. Let's go. 🔥`;

    document.getElementById('global-actions').classList.add('hidden');
}

if (clearQueueBtn) {
    clearQueueBtn.addEventListener('click', () => {
        queuedFiles = [];
        queueUi.classList.add('hidden');
        uploadText.innerHTML = 'Drag & Drop invoices or <span class="browse-link">Browse</span>';
        fileInput.value = '';
    });
}

if (startProcessBtn) {
    startProcessBtn.addEventListener('click', () => {
        if (queuedFiles.length > 0) {
            handleFiles(queuedFiles);
        }
    });
}

async function handleFiles(files) {
    if (files.length === 0) return;

    const batchProgress = document.getElementById('batch-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const globalActions = document.getElementById('global-actions');
    const downloadBtn = document.getElementById('download-report-btn');
    const processMoreBtn = document.getElementById('process-more-btn');

    processMoreBtn.onclick = () => {
        batchProgress.classList.add('hidden');
        globalActions.classList.add('hidden');
        uploadIcon.classList.remove('hidden');
        uploadText.innerHTML = 'Drag & Drop invoices or <span class="browse-link">Browse</span>';

        progressBar.style.width = '0%';
        progressText.innerText = 'Processed 0 / 0';

        fileInput.value = '';
        queuedFiles = [];

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

    const batchId = Date.now().toString();

    for (const file of files) {
        if (!['image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'application/pdf'].includes(file.type)) continue;

        uploadText.innerText = `Processing: ${file.name}`;

        try {
            await processSingleFile(file, batchId);
        } catch (e) {
            console.error(e);
        }

        processedCount++;
        const percent = (processedCount / total) * 100;
        progressBar.style.width = percent + '%';
        progressText.innerText = `Processed ${processedCount} / ${total}`;
    }

    uploadText.innerText = "Batch Complete!";
    globalActions.classList.remove('hidden');

    downloadBtn.onclick = () => {
        window.location.href = `http://127.0.0.1:5000/download_report?batch_id=${batchId}`;
    };

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

    const toggleElement = document.getElementById('classification-method-toggle');
    const classificationMethod = toggleElement && toggleElement.checked ? 'gemini' : 'local_nn';

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

    return response.json();
}

function showResults(data) {
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
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function resetUIAfterError() {
    loader.classList.add('hidden');
    uploadIcon.classList.remove('hidden');
    uploadText.innerHTML = 'Drag & Drop your invoice or <span class="browse-link">Browse</span>';
}



const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.querySelectorAll('.scroll-reveal').forEach(el => {
    observer.observe(el);
});

(function initSettings() {
    const settingsBtn = document.getElementById('settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const settingsOverlay = document.getElementById('settings-overlay');
    const apiKeyInput = document.getElementById('api-key-input');
    const saveBtn = document.getElementById('save-api-key-btn');
    const apiStatus = document.getElementById('api-status');
    const settingsDot = document.getElementById('settings-dot');

    if (!settingsBtn || !settingsModal) return;

    function openSettings() {
        settingsModal.classList.add('visible');
        settingsOverlay.classList.add('visible');
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

    settingsModal.addEventListener('click', (e) => e.stopPropagation());

    function saveApiKey() {
        const key = apiKeyInput.value.trim();
        if (!key) return;

        localStorage.setItem('gemini_api_key', key);
        updateStatus(true);

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

    function updateStatus(hasKey) {
        if (hasKey) {
            apiStatus.className = 'api-status configured';
            apiStatus.innerHTML = '<span><i class="fa-solid fa-circle-check"></i> API Key Locked In. Beast Mode ON. 🔥</span><button class="btn-clear-key" id="clear-api-key-btn"><i class="fa-solid fa-trash-can"></i> Clear</button>';
            settingsDot.className = 'status-dot active';

            document.getElementById('clear-api-key-btn').addEventListener('click', () => {
                localStorage.removeItem('gemini_api_key');
                apiKeyInput.value = '';
                updateStatus(false);
            });
        } else {
            apiStatus.className = 'api-status not-configured';
            apiStatus.innerHTML = '<span><i class="fa-solid fa-circle-xmark"></i> No API Key. The AI is starving. 😢</span>';
            settingsDot.className = 'status-dot inactive';
        }
    }

    const existingKey = localStorage.getItem('gemini_api_key');
    updateStatus(!!existingKey);
})();
