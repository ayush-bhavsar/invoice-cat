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
    if (fileInput.files.length) handleFile(fileInput.files[0]);
});

resetBtn.addEventListener('click', () => {
    resultContainer.classList.add('hidden');
    dropZone.classList.remove('hidden');
    fileInput.value = '';

    // Reset visuals
    uploadText.innerHTML = 'Drag & Drop your invoice or <span class="browse-link">Browse</span>';
    uploadIcon.classList.remove('hidden');
});

// --- Main Logic ---
async function handleFile(file) {
    if (!['image/png', 'image/jpeg', 'image/jpg'].includes(file.type)) {
        alert("Please upload a valid image (PNG/JPG).");
        return;
    }

    // Show Loading State
    uploadText.innerText = `Processing ${file.name}...`;
    uploadIcon.classList.add('hidden');
    loader.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Call our Flask Backend
        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showResults(data);
        } else {
            alert(`Error: ${data.error}`);
            resetUIAfterError();
        }

    } catch (error) {
        console.error("API Error:", error);
        alert("Failed to connect to the backend. Is api.py running?");
        resetUIAfterError();
    }
}

function showResults(data) {
    // Hide Loader
    loader.classList.add('hidden');

    // Hide Upload Box (optional, or just show below)
    dropZone.classList.add('hidden');

    // Populate Data
    document.getElementById('file-name-display').innerText = data.filename;
    document.getElementById('res-date').innerText = data.date || "Not Found";
    document.getElementById('res-amount').innerText = data.total_amount ? `$${data.total_amount}` : "Not Found";
    document.getElementById('res-category').innerText = data.category || "Unknown";

    // Show Results
    resultContainer.classList.remove('hidden');

    // Attach data to Download Button
    const downloadBtn = document.getElementById('download-btn');
    downloadBtn.onclick = () => downloadCSV(data);
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
