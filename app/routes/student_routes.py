# At the top of your file, add this import:
from flask import current_app
# routes/student_routes.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models import db, Student
from datetime import datetime
from werkzeug.utils import secure_filename
import os

student_bp = Blueprint('students', __name__)

# Helper function for file upload
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# API Routes
@student_bp.route('/api/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

@student_bp.route('/api/students/<int:id>', methods=['GET'])
def get_student(id):
    student = Student.query.get_or_404(id)
    return jsonify(student.to_dict())

@student_bp.route('/api/students', methods=['POST'])
def create_student():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"{field} is required"}), 400
    
    # Check if student with email already exists
    existing_student = Student.query.filter_by(email=data['email']).first()
    if existing_student:
        return jsonify({"error": "Student with this email already exists"}), 400
    
    # Parse date of birth if provided
    date_of_birth = None
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Create new student
    student = Student(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        date_of_birth=date_of_birth,
        grade_level=data.get('grade_level'),
        profile_image=data.get('profile_image', 'default.jpg')
    )
    
    db.session.add(student)
    db.session.commit()
    
    return jsonify(student.to_dict()), 201

@student_bp.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    
    # Update fields
    if 'first_name' in data:
        student.first_name = data['first_name']
    if 'last_name' in data:
        student.last_name = data['last_name']
    if 'email' in data:
        # Check if email is already in use by another student
        existing_student = Student.query.filter_by(email=data['email']).first()
        if existing_student and existing_student.id != id:
            return jsonify({"error": "Email already in use"}), 400
        student.email = data['email']
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            student.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    if 'grade_level' in data:
        student.grade_level = data['grade_level']
    
    db.session.commit()
    
    return jsonify(student.to_dict())

@student_bp.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    
    db.session.delete(student)
    db.session.commit()
    
    return jsonify({"message": "Student deleted successfully"})

# Web Routes
@student_bp.route('/students')
def student_list():
    students = Student.query.all()
    return render_template('students/index.html', students=students)

@student_bp.route('/students/new', methods=['GET', 'POST'])
def new_student():
    if request.method == 'POST':
        # Handle form submission
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        # Validate required fields
        if not all([first_name, last_name, email]):
            flash('Please fill out all required fields', 'danger')
            return render_template('students/new.html')
        
        # Check if student with email already exists
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            flash('A student with this email already exists', 'danger')
            return render_template('students/new.html')
        
        # Parse date of birth
        date_of_birth = None
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            try:
                date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD', 'danger')
                return render_template('students/new.html')
        
        # Handle file upload
        profile_image = 'default.jpg'
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                profile_image = filename
        
        # Create new student
        grade_level = request.form.get('grade_level')
        if grade_level:
            try:
                grade_level = int(grade_level)
            except ValueError:
                grade_level = None
        
        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            grade_level=grade_level,
            profile_image=profile_image
        )
        
        db.session.add(student)
        db.session.commit()
        
        flash('Student created successfully', 'success')
        return redirect(url_for('students.student_list'))
    
    return render_template('students/new.html')

@student_bp.route('/students/<int:id>')
def view_student(id):
    student = Student.query.get_or_404(id)
    return render_template('students/view.html', student=student)

@student_bp.route('/students/<int:id>/edit', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        # Handle form submission
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        
        # Validate required fields
        if not all([first_name, last_name, email]):
            flash('Please fill out all required fields', 'danger')
            return render_template('students/edit.html', student=student)
        
        # Check if email is already in use by another student
        existing_student = Student.query.filter_by(email=email).first()
        if existing_student and existing_student.id != id:
            flash('Email already in use by another student', 'danger')
            return render_template('students/edit.html', student=student)
        
        # Update student data
        student.first_name = first_name
        student.last_name = last_name
        student.email = email
        
        # Parse date of birth
        dob_str = request.form.get('date_of_birth')
        if dob_str:
            try:
                student.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Use YYYY-MM-DD', 'danger')
                return render_template('students/edit.html', student=student)
        
        # Handle file upload
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                # Remove old file if not default
                if student.profile_image != 'default.jpg':
                    try:
                        old_file = os.path.join(current_app.config['UPLOAD_FOLDER'], student.profile_image)
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    except Exception as e:
                        # Log error but continue
                        print(f"Error removing old file: {e}")
                student.profile_image = filename
        
        # Update grade level
        grade_level = request.form.get('grade_level')
        if grade_level:
            try:
                student.grade_level = int(grade_level)
            except ValueError:
                student.grade_level = None
        
        db.session.commit()
        
        flash('Student updated successfully', 'success')
        return redirect(url_for('students.view_student', id=student.id))
    
    return render_template('students/edit.html', student=student)

@student_bp.route('/students/<int:id>/delete', methods=['POST'])
def delete_student_ui(id):
    student = Student.query.get_or_404(id)
    
    db.session.delete(student)
    db.session.commit()
    
    flash('Student deleted successfully', 'success')
    return redirect(url_for('students.student_list'))