# AI-Powered Virtual Teaching Assistant (SaaS)

## About the Project
This project is an AI-powered Virtual Teaching Assistant SaaS designed to help teachers generate content, grade assignments, and track student performance efficiently. It provides an interactive chatbot, AI-based grading system, and a student performance dashboard to enhance the teaching experience.

## Features
### Home Page

- AI chatbot for students and teachers.
- Students: Career guidance, learning roadmaps.
- Teachers: AI-generated lesson plans, assignments, activity suggestions.

### Teacher Profile Page

- Manage student profiles and content.
- Generate and share quizzes/tests.
- AI-assisted grading and feedback.
- Track student performance.
- Schedule classes with reminders.

## Tech Stack
- Frontend: HTML, CSS, Bootstrap, JavaScript.
- Backend: Python, Flask.
- Database: SQLite.
- AI Integration: OpenAI API for chat and grading.

## Installation & Setup
### Clone the Repository
```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/teacher-assistant-saas.git
cd teacher-assistant-saas
```

### Set Up Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Set Up the Database
```sh
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Run the Application
```sh
flask run
```
Access the app at `http://127.0.0.1:5000/`.

## Usage Guide
- Sign up as a teacher.
- Add student profiles and generate quizzes.
- Use AI for lesson planning and grading.
- Track student progress over time.

## Pending Integrations & Bug Fixes
### Features Yet to be Integrated
- AI grading system final integration.
- Full chatbot integration with student and teacher functionalities.
- Email notifications for scheduled classes.
- Exporting student performance reports as PDFs.
- Multi-user role support (Admin, Teacher, Student).

### Known Issues & Fixes Needed
- Home page navigation issues.
- Session management improvements.
- Error handling for invalid inputs in quiz creation.
- Optimization of AI chatbot response time.
- UI enhancements for a better user experience.
