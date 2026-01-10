from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import random
import os
import urllib.parse

app = Flask(__name__)
DB_FILE = 'questions.json'

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

@app.route('/get_subtopics/<subject>')
def get_subtopics(subject):
    data = load_db()
    subtopics = list(data.get(subject, {}).keys())
    return jsonify(subtopics)

@app.route('/get_question/<subject>/<subtopic>')
def get_question(subject, subtopic):
    data = load_db()
    questions = data.get(subject, {}).get(subtopic, [])
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
    
    new_q = {
        "question": request.form['question'],
        "answer": request.form['answer'],
        "solution": request.form['solution']
    }
    
    if sub not in data: data[sub] = {}
    if topic not in data[sub]: data[sub][topic] = []
    
    data[sub][topic].append(new_q)
    save_db(data)
    return redirect(url_for('index'))

@app.route('/study/<subject>/<subtopic>')
def study_page(subject, subtopic):
    # This just opens the dedicated study window
    return render_template('study.html', subject=subject, subtopic=subtopic)

if __name__ == '__main__':
    app.run(debug=True, port=5000)