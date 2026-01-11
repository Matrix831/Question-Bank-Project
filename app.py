from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import json
import random
import os
import urllib.parse
import csv 
import io

app = Flask(__name__)

# 1. Define the BASE_DIR and DB_FILE first using absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'questions.json')

# 2. Define the UPLOAD_FOLDER
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 3. Create the upload folder and print the database path
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"🚀 YOUR DATABASE IS ACTUALLY HERE: {DB_FILE}")

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    data = load_db()
    return render_template('index.html', subjects=data.keys())

# --- MANAGEMENT ROUTES ---

@app.route('/manage')
def manage_page():
    """Page to view all questions for editing or deleting"""
    data = load_db()
    return render_template('manage.html', data=data)

@app.route('/download_db')
def download_db():
    """Allows downloading the JSON file directly from the browser"""
    return send_file(DB_FILE, as_attachment=True)

@app.route('/delete/<subject>/<subtopic>/<int:index>', methods=['POST'])
def delete_question(subject, subtopic, index):
    data = load_db()
    sub_decoded = urllib.parse.unquote(subject)
    topic_decoded = urllib.parse.unquote(subtopic)
    
    if sub_decoded in data and topic_decoded in data[sub_decoded]:
        deleted_q = data[sub_decoded][topic_decoded].pop(index)
        
        if deleted_q.get('image'):
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], deleted_q['image'])
            if os.path.exists(img_path):
                os.remove(img_path)
        
        if not data[sub_decoded][topic_decoded]:
            del data[sub_decoded][topic_decoded]
            
        if not data[sub_decoded]:
            del data[sub_decoded]
            
        save_db(data)
    return redirect(url_for('manage_page'))

@app.route('/edit/<subject>/<subtopic>/<int:index>', methods=['GET', 'POST'])
def edit_question(subject, subtopic, index):
    data = load_db()
    sub_decoded = urllib.parse.unquote(subject)
    topic_decoded = urllib.parse.unquote(subtopic)
    
    if request.method == 'POST':
        data[sub_decoded][topic_decoded][index] = {
            "question": request.form['question'],
            "answer": request.form['answer'],
            "solution": request.form['solution'],
            "image": data[sub_decoded][topic_decoded][index].get('image')
        }
        save_db(data)
        return redirect(url_for('manage_page'))
    
    question_data = data[sub_decoded][topic_decoded][index]
    return render_template('edit.html', q=question_data, sub=sub_decoded, topic=topic_decoded, idx=index)

# --- QUESTION & STUDY ROUTES ---

@app.route('/get_subtopics/<subject>')
def get_subtopics(subject):
    data = load_db()
    subject_decoded = urllib.parse.unquote(subject)
    subtopics = list(data.get(subject_decoded, {}).keys())
    return jsonify(subtopics)

@app.route('/get_question/<subject>/<subtopic>')
def get_question(subject, subtopic):
    data = load_db()
    sub_decoded = urllib.parse.unquote(subject)
    topic_decoded = urllib.parse.unquote(subtopic)
    questions = data.get(sub_decoded, {}).get(topic_decoded, [])
    if questions:
        return jsonify(random.choice(questions))
    return jsonify({"error": "No questions found"})

@app.route('/add')
def add_page():
    return render_template('add.html')

@app.route('/save', methods=['POST'])
def save_question():
    data = load_db()
    sub = request.form['subject']
    topic = request.form['subtopic']
    file = request.files.get('image')
    image_name = None
    if file and file.filename != '':
        image_name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
    
    new_q = {
        "question": request.form['question'],
        "answer": request.form['answer'],
        "solution": request.form['solution'],
        "image": image_name 
    }
    
    if sub not in data: data[sub] = {}
    if topic not in data[sub]: data[sub][topic] = []
    data[sub][topic].append(new_q)
    save_db(data)
    return redirect(url_for('index'))

@app.route('/import_csv', methods=['POST'])
def import_csv():
    file = request.files.get('csv_file')
    if not file or file.filename == '':
        return redirect(url_for('add_page'))
    stream = file.stream.read().decode("UTF8").splitlines()
    reader = csv.DictReader(stream)
    data = load_db()
    for row in reader:
        sub = row['subject']
        topic = row['subtopic']
        if sub not in data: data[sub] = {}
        if topic not in data[sub]: data[sub][topic] = []
        data[sub][topic].append({
            "question": row['question'], "answer": row['answer'],
            "solution": row['solution'], "image": None
        })
    save_db(data)
    return redirect(url_for('index'))

@app.route('/study/<subject>/<subtopic>')
def study_page(subject, subtopic):
    return render_template('study.html', subject=subject, subtopic=subtopic)

# --- EXAM ROUTES ---

@app.route('/generate_exam')
def generate_exam_page():
    data = load_db()
    return render_template('generate_exam.html', subjects=data.keys())

@app.route('/mock_exam_custom/<subject>/<subtopics_json>/<int:count>')
def mock_exam_custom(subject, subtopics_json, count):
    data = load_db()
    subject_decoded = urllib.parse.unquote(subject)
    subtopics_list = json.loads(urllib.parse.unquote(subtopics_json))
    
    all_qs = []
    subject_data = data.get(subject_decoded, {})
    for topic in subtopics_list:
        if topic in subject_data:
            all_qs.extend(subject_data[topic])
    
    if not all_qs: return "No questions found!", 404
    
    exam_qs = random.sample(all_qs, min(len(all_qs), count))
    return render_template('exam_print.html', questions=exam_qs, subject=subject_decoded)

@app.route('/bulk_delete', methods=['POST'])
def bulk_delete():
    target_ids = request.json.get('ids', [])
    data = load_db()
    target_ids.sort(key=lambda x: int(x.split('|')[2]), reverse=True)
    
    for item in target_ids:
        sub, topic, idx = item.split('|')
        idx = int(idx)
        if sub in data and topic in data[sub]:
            data[sub][topic].pop(idx)
            if not data[sub][topic]: del data[sub][topic]
            if not data[sub]: del data[sub]
            
    save_db(data)
    return jsonify({"status": "success"})

@app.route('/download_template')
def download_template():
    headers = "subject,subtopic,question,answer,solution\n"
    proxy = io.StringIO()
    proxy.write(headers)
    mem = io.BytesIO()
    mem.write(proxy.getvalue().encode('utf-8'))
    mem.seek(0)
    proxy.close()
    return send_file(mem, mimetype='text/csv', as_attachment=True, download_name='ee_portal_template.csv')

if __name__ == '__main__':
    app.run(debug=True, port=5000)