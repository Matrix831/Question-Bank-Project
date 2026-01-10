from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
import json
import random
import os
import urllib.parse
import csv 

app = Flask(__name__)
DB_FILE = 'questions.json'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route('/delete/<subject>/<subtopic>/<int:index>', methods=['POST'])
def delete_question(subject, subtopic, index):
    data = load_db()
    sub_decoded = urllib.parse.unquote(subject)
    topic_decoded = urllib.parse.unquote(subtopic)
    
    if sub_decoded in data and topic_decoded in data[sub_decoded]:
        # Remove the question at the specific index
        deleted_q = data[sub_decoded][topic_decoded].pop(index)
        
        # Clean up the image file if it exists
        if deleted_q.get('image'):
            img_path = os.path.join(app.config['UPLOAD_FOLDER'], deleted_q['image'])
            if os.path.exists(img_path):
                os.remove(img_path)
        
        # If subtopic is empty, remove it
        if not data[sub_decoded][topic_decoded]:
            del data[sub_decoded][topic_decoded]
            
        # If subject is empty, remove it
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
        # Update the question with form data
        data[sub_decoded][topic_decoded][index] = {
            "question": request.form['question'],
            "answer": request.form['answer'],
            "solution": request.form['solution'],
            "image": data[sub_decoded][topic_decoded][index].get('image') # Keep existing image
        }
        save_db(data)
        return redirect(url_for('manage_page'))
    
    # GET request: Show the edit form with current data
    question_data = data[sub_decoded][topic_decoded][index]
    return render_template('edit.html', q=question_data, sub=sub_decoded, topic=topic_decoded, idx=index)

# --- EXISTING ROUTES ---

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)