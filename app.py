from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from werkzeug.utils import secure_filename
from parser import parse_resume
from db import init_db, insert_candidate, search_candidates, get_all_candidates

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return render_template('upload.html', error='No file uploaded')
    
    file = request.files['resume']
    if file.filename == '':
        return render_template('upload.html', error='No file selected')
    
    if not allowed_file(file.filename):
        return render_template('upload.html', error='Invalid file type. Please upload PDF or DOCX')
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Parse the resume
    data = parse_resume(filepath)
    
    # Store in database
    insert_candidate(data)
    
    return render_template('result.html', data=data)

@app.route('/candidates')
def candidates():
    skill = request.args.get('skill', '').strip()
    name = request.args.get('name', '').strip()
    
    if skill or name:
        results = search_candidates(skill=skill, name=name)
    else:
        results = get_all_candidates()
    
    return render_template('candidates.html', candidates=results, search_skill=skill, search_name=name)

@app.route('/api/candidates')
def api_candidates():
    skill = request.args.get('skill', '').strip()
    results = search_candidates(skill=skill) if skill else get_all_candidates()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
