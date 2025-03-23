from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Assessment, Submission

assessment_bp = Blueprint('assessment', __name__, url_prefix='/assessment')

@assessment_bp.route('/')
def index():
    assessments = Assessment.query.all()
    return render_template('assessment/index.html', assessments=assessments)

@assessment_bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        # Handle the form submission
        title = request.form.get('title')
        description = request.form.get('description')
        questions = request.form.get('questions')  # You might want to handle this differently
        student_id = request.form.get('student_id')
        created_by = request.form.get('created_by')  # Typically from the session
        
        assessment = Assessment(
            title=title,
            description=description,
            questions=questions,
            student_id=student_id,
            created_by=created_by
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        flash('Assessment created successfully', 'success')
        return redirect(url_for('assessment.index'))
        
    # GET request - show the form
    return render_template('assessment/new.html')

# Add more routes for viewing, editing, and deleting assessments