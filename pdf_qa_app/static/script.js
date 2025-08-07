// Global variables
let chatHistory = [];
let currentFilename = null;

// DOM elements
const uploadArea = document.getElementById('uploadArea');
const pdfFile = document.getElementById('pdfFile');
const browseBtn = document.getElementById('browseBtn');
const uploadStatus = document.getElementById('uploadStatus');
const previewSection = document.getElementById('previewSection');
const modelSection = document.getElementById('modelSection');
const questionSection = document.getElementById('questionSection');
const answerSection = document.getElementById('answerSection');
const chatHistorySection = document.getElementById('chatHistory');
const controlSection = document.getElementById('controlSection');
const loadingSpinner = document.getElementById('loadingSpinner');

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // File upload events
    browseBtn.addEventListener('click', () => pdfFile.click());
    pdfFile.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // Question and control events
    document.getElementById('askBtn').addEventListener('click', askQuestion);
    document.getElementById('newQuestionBtn').addEventListener('click', showQuestionSection);
    document.getElementById('clearBtn').addEventListener('click', clearSession);
    
    // Enter key to submit question
    document.getElementById('questionInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            askQuestion();
        }
    });
});

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            pdfFile.files = files;
            handleFileSelect();
        } else {
            showStatus('Please select a PDF file.', 'error');
        }
    }
}

function handleFileSelect() {
    const file = pdfFile.files[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
        showStatus('Please select a PDF file.', 'error');
        return;
    }
    
    if (file.size > 16 * 1024 * 1024) {
        showStatus('File size must be less than 16MB.', 'error');
        return;
    }
    
    uploadFile(file);
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showStatus('Uploading and processing PDF...', 'info');
    showLoading(true);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.success) {
            currentFilename = data.filename;
            showStatus(data.message, 'success');
            showDocumentPreview(data.filename, data.preview);
            showModelSection();
            showQuestionSection();
        } else {
            showStatus(data.error || 'Upload failed', 'error');
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Upload error:', error);
        showStatus('Upload failed. Please try again.', 'error');
    });
}

// UI functions
function showStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `status-message ${type}`;
    uploadStatus.style.display = 'block';
    
    if (type === 'success') {
        setTimeout(() => {
            uploadStatus.style.display = 'none';
        }, 3000);
    }
}

function showDocumentPreview(filename, preview) {
    const documentInfo = document.getElementById('documentInfo');
    const textPreview = document.getElementById('textPreview');
    
    documentInfo.innerHTML = `
        <strong>📄 File:</strong> ${filename}<br>
        <strong>📊 Status:</strong> Successfully processed<br>
        <strong>💾 Preview Length:</strong> ${preview.length} characters shown
    `;
    
    textPreview.textContent = preview;
    previewSection.style.display = 'block';
}

function showModelSection() {
    modelSection.style.display = 'block';
}

function showQuestionSection() {
    questionSection.style.display = 'block';
    document.getElementById('questionInput').focus();
}

function showLoading(show) {
    loadingSpinner.style.display = show ? 'block' : 'none';
}

// Question handling
function askQuestion() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter a question.');
        return;
    }
    
    if (!currentFilename) {
        alert('Please upload a PDF file first.');
        return;
    }
    
    const selectedModel = document.querySelector('input[name="model"]:checked').value;
    
    showLoading(true);
    questionSection.style.display = 'none';
    
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            question: question,
            model: selectedModel
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        
        if (data.error) {
            alert(data.error);
            questionSection.style.display = 'block';
        } else {
            // Add to chat history
            chatHistory.push({
                question: data.question,
                answer: data.answer,
                model: data.model_used,
                timestamp: new Date().toLocaleString()
            });
            
            showAnswer(data.answer, data.model_used);
            updateChatHistory();
            showControlSection();
            
            // Clear question input
            questionInput.value = '';
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('Question error:', error);
        alert('Failed to get answer. Please try again.');
        questionSection.style.display = 'block';
    });
}

function showAnswer(answer, model) {
    const answerContent = document.getElementById('answerContent');
    answerContent.innerHTML = `
        <div style="margin-bottom: 10px;">
            <small><strong>Model:</strong> ${model}</small>
        </div>
        <div>${answer.replace(/\n/g, '<br>')}</div>
    `;
    answerSection.style.display = 'block';
}

function updateChatHistory() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '';

    chatHistory.forEach((chat, index) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message';
        messageDiv.innerHTML = `
            <div><strong>Q${index + 1}:</strong> ${chat.question}</div>
            <div><strong>Ans:</strong> ${chat.answer}</div>
            <div><small>Model: ${chat.model} | Time: ${chat.timestamp}</small></div>
            <hr/>
        `;
        chatMessages.appendChild(messageDiv);
    });
}


// ✅ Function 1: Clears session
function clearSession() {
    console.log("Session cleared");
    // Backend call bhi kar sakta hai yahan agar chahiye to
}

// ✅ Function 2: Show control section (after file upload)
function showControlSection() {
    console.log("Showing control section");
    const section = document.getElementById("control-section");
    if (section) {
        section.style.display = "block";
    }
}


// function updateChatHistory() {
//     const chatMessages = document.getElementById('chatMessages');
//     chatMessages.innerHTML = '';
    
//     chatHistory.forEach((chat, index) => )}