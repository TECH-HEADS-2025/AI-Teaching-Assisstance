# models/assessment.py
from datetime import datetime
from . import db

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    total_points = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    questions = db.relationship('AssessmentQuestion', backref='assessment', lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship('AssessmentSubmission', backref='assessment', lazy=True)
    
    def __repr__(self):
        return f'<Assessment {self.title}>'

class AssessmentQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, short_answer, essay, etc.
    points = db.Column(db.Integer, default=1)
    order = db.Column(db.Integer, default=0)
    
    # For multiple choice questions, store options as JSON string
    options = db.Column(db.Text, nullable=True)  # JSON string
    correct_answer = db.Column(db.Text, nullable=True)  # For auto-graded questions
    
    # Foreign keys
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    
    # Relationships
    answers = db.relationship('QuestionAnswer', backref='question', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Question {self.id}: {self.question_text[:20]}...>'

class AssessmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Float, nullable=True)  # Calculated after grading
    graded = db.Column(db.Boolean, default=False)
    graded_at = db.Column(db.DateTime, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # Foreign keys
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessment.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    grader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationships
    answers = db.relationship('QuestionAnswer', backref='submission', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Submission {self.id} for Assessment {self.assessment_id}>'

class QuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer_text = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)  # For auto-graded questions
    points_earned = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    
    # Foreign keys
    question_id = db.Column(db.Integer, db.ForeignKey('assessment_question.id'), nullable=False)
    submission_id = db.Column(db.Integer, db.ForeignKey('assessment_submission.id'), nullable=False)
    
    def __repr__(self):
        return f'<Answer {self.id} for Question {self.question_id}>'