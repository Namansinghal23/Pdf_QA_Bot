import os
import PyPDF2
import requests
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import json
#import openai

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenRouter configuration - YOU NEED TO CHANGE THIS
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Replace with your actual API key
# openai.api_key = OPENAI_API_KEY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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

# def query_openai(question, context, model="gpt-3.5-turbo"):
#     """Query OpenAI API with context and question"""
#     try:
#         prompt = f"""Based on the following document content, please answer the user's question accurately and concisely.

def query_openai_working(question, context):
    import openai
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    prompt = f"""Based on this PDF content, answer the question:

PDF Content: {context[:2000]}

Question: {question}

Answer:"""
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

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
    # answer = query_openai(question, pdf_content[current_filename], model)
    answer = query_openai_working(question, pdf_content[current_filename])
    
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
    # For Vercel deployment
application = app







