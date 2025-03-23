from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize database
db = SQLAlchemy()

# User Model (Authentication)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_teacher = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    students = db.relationship('Student', backref='teacher', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Student Model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    grade_level = db.Column(db.Integer, nullable=True)
    profile_image = db.Column(db.String(200), nullable=True, default='default.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Assessment Model
class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    total_points = db.Column(db.Integer, default=100)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('AssessmentQuestion', backref='assessment', lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship('AssessmentSubmission', backref='assessment', lazy=True, cascade="all, delete-orphan")

# Assessment Question Model
class AssessmentQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, default=10)
    options = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    answers = db.relationship('QuestionAnswer', backref='question', lazy=True, cascade="all, delete-orphan")

# Assessment Submission Model
class AssessmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded = db.Column(db.Boolean, default=False)
    total_score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    answers = db.relationship('QuestionAnswer', backref='submission', lazy=True, cascade="all, delete-orphan")

# Question Answer Model
class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('assessment_submission.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('assessment_question.id'), nullable=False)
    answer_text = db.Column(db.Text)
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    ai_graded = db.Column(db.Boolean, default=False)