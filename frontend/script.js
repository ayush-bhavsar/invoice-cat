const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseLink = document.querySelector('.browse-link');
const loader = document.getElementById('loader');
const uploadText = document.querySelector('.upload-text');
const uploadIcon = document.querySelector('.upload-icon');
const resultContainer = document.getElementById('result-container');
const resetBtn = document.getElementById('reset-btn');

// --- Drag & Drop Events ---
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
    if (files.length) handleFile(files[0]);
});

// --- Click Events ---
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFiles(fileInput.files);
});

// --- Main Logic ---
async function handleFiles(files) {
    if (files.length === 0) return;

    // Reset UI
    const batchProgress = document.getElementById('batch-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const globalActions = document.getElementById('global-actions');
    const downloadBtn = document.getElementById('download-report-btn');

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
        if (!['image/png', 'image/jpeg', 'image/jpg'].includes(file.type)) continue;

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
}

async function processSingleFile(file, batchId) {
    const formData = new FormData();
    formData.append('file', file);

    // Add query param save=true and batch_id
    const response = await fetch(`http://127.0.0.1:5000/upload?save=true&batch_id=${batchId}`, {
        method: 'POST',
        body: formData
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
