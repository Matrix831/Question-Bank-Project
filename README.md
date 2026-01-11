# ⚡ Engineering Question Randomizer & Study Portal
> A professional study ecosystem for Engineering students, designed for active recall and exam preparation.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Flask Framework](https://img.shields.io/badge/framework-Flask-lightgrey)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📖 Overview
This system is a **hierarchical question bank** designed to help engineering students (specifically Electrical Engineering) master complex subjects. It allows users to drill down from major **Subjects** to specific **Subtopics** and solve problems in a minimalist, distraction-free environment.

Built with **Python Flask**, it features a robust LaTeX rendering engine powered by **MathJax**, making it perfect for complex formulas, circuit analysis, and calculus.

## ✨ Key Features
* **Zen Mode Solving:** A centered, minimalist interface for focused problem-solving.
* **LaTeX Integration:** Full support for engineering symbols ($\Omega, \tau, \phi, \int, \angle$) using MathJax.
* **Image Support:** Upload circuit diagrams or screenshots directly from textbooks (like *Siskind's Electrical Circuits*).
* **Batch Import:** Quickly upload hundreds of questions via **CSV files**.
* **Management Dashboard:** A full UI to search, edit, and delete questions from the database.
* **Keyboard Shortcuts:** * `Spacebar` to reveal the answer.
    * `Right Arrow` to load the next question.
    * `Esc` to return to the portal.

---

## 🛠️ Tech Stack
* **Backend:** Python & Flask
* **Frontend:** HTML5, CSS3 (Modern Dark Theme), JavaScript
* **Math Rendering:** MathJax 3.0
* **Hardware Target:** Optimized to run on **Orange Pi PC** as a local Wi-Fi Study Hotspot.

---

## 🚀 Getting Started

### 1. Installation
Clone the repository to your local machine or Orange Pi:
```bash
git clone [https://github.com/Matrix831/Question-Bank-Project](https://github.com/Matrix831/Question-Bank-Project)
cd Question-Bank-Project

```

### 2. Setup Environment

It is recommended to use a virtual environment to avoid conflicts:

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# venv\Scripts\activate   # On Windows
pip install flask

```

### 3. Run the Application

```bash
python app.py

```

Visit `http://127.0.0.1:5000` in your browser.

---

## 📂 CSV Import Format

To batch import questions from textbooks, use a `.csv` file with the following header structure:
`subject,subtopic,question,answer,solution`

| subject | subtopic | question | answer | solution |
| --- | --- | --- | --- | --- |
| Circuits 1 | Ohm's Law | Find  if  and  |  | Use  |

---

## 🗺️ Roadmap

* [x] Implement a pomodoro timer in Study Mode.
* [x] Create a "Mock Exam" PDF generator.
* [x] Absolute Path Data Integrity
* [x] Dedicated Multi-Subtopic Exam Generator
* [x] Mobile-friendly Checkbox UI
* [x] One-click Database Backup
* [ ] Next: Solution Masking toggle for Study Mode
* [ ] Next: Android Studio WebView (.apk) build
* [ ] Future: Image-to-Text (OCR) for textbook scanning

## 👤 Author

**Wilford Bordeos** *Electrical Engineering Student* [GitHub Profile](https://www.google.com/search?q=https://github.com/Matrix831)

---

*Developed for the love of Engineering and Open Source.*
