import os
import PyPDF2
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenRouter configuration - YOU NEED TO CHANGE THIS
OPENROUTER_API_KEY = "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"  # Replace with your actual API key
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# Store PDF content in memory
pdf_content = {}
current_filename = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return None

def query_openrouter(question, context, model="openai/gpt-3.5-turbo"):
    """Query OpenRouter API with context and question"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Based on the following document content, please answer the user's question accurately and concisely.

Document Content:
{context[:4000]}

Question: {question}

Please provide a clear and helpful answer based only on the information in the document. If the answer cannot be found in the document, please say so."""

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided document content."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(OPENROUTER_BASE_URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error querying API: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_filename, pdf_content
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from PDF
        text = extract_pdf_text(filepath)
        if text:
            pdf_content[filename] = text
            current_filename = filename
            return jsonify({
                'success': True, 
                'message': f'PDF "{filename}" uploaded successfully!',
                'filename': filename,
                'preview': text[:500] + "..." if len(text) > 500 else text
            })
        else:
            return jsonify({'error': 'Failed to extract text from PDF'}), 400
    else:
        return jsonify({'error': 'Please upload a valid PDF file'}), 400

@app.route('/ask', methods=['POST'])
def ask_question():
    global current_filename, pdf_content
    
    if not current_filename or current_filename not in pdf_content:
        return jsonify({'error': 'No PDF uploaded. Please upload a PDF first.'}), 400
    
    data = request.json
    question = data.get('question', '').strip()
    model = data.get('model', 'openai/gpt-3.5-turbo')
    
    if not question:
        return jsonify({'error': 'Please enter a question'}), 400
    
    # Query OpenRouter API
    answer = query_openrouter(question, pdf_content[current_filename], model)
    
    return jsonify({
        'question': question,
        'answer': answer,
        'filename': current_filename,
        'model_used': model
    })

@app.route('/clear', methods=['POST'])
def clear_session():
    global current_filename, pdf_content
    
    # Clear uploaded files
    if current_filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], current_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    current_filename = None
    pdf_content.clear()
    
    return jsonify({'success': True, 'message': 'Session cleared successfully'})

if __name__ == '__main__':
    print("Starting PDF Q&A Application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)