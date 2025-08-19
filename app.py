from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    events = db.relationship('Event', backref='creator', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'event', 'competition', 'program'
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    max_participants = db.Column(db.Integer, nullable=True)
    current_participants = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='upcoming')  # 'upcoming', 'ongoing', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'max_participants': self.max_participants,
            'current_participants': self.current_participants,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'creator': self.creator.username if self.creator else None
        }

    def __repr__(self):
        return f'<Event {self.title}>'

# Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., 'CSE110'
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'description': self.description,
            'department': self.department,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<Course {self.course_code}>'

# CourseResource model
class CourseResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(db.String(50), nullable=False)  # 'document', 'link', 'video', 'assignment', 'syllabus'
    file_path = db.Column(db.String(500), nullable=True)  # For uploaded files
    external_link = db.Column(db.String(500), nullable=True)  # For external links
    file_size = db.Column(db.Integer, nullable=True)  # File size in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref='resources')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'resource_type': self.resource_type,
            'file_path': self.file_path,
            'external_link': self.external_link,
            'file_size': self.file_size,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'course_id': self.course_id
        }

    def __repr__(self):
        return f'<CourseResource {self.title}>'

# Helper function to check if user is logged in
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/21201327')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        events = Event.query.filter_by(user_id=user.id).order_by(Event.date.desc()).all()
        return render_template('home.html', user=user, events=events)
    return redirect(url_for('login'))

@app.route('/register/21201327', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!')
            return redirect(url_for('register'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered!')
            return redirect(url_for('register'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login/21201327', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout/21201327')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out!')
    return redirect(url_for('login'))

# Event Management Routes (Web Interface)
@app.route('/events/21201327')
@login_required
def events():
    user = User.query.get(session['user_id'])
    events = Event.query.filter_by(user_id=user.id).order_by(Event.date.desc()).all()
    return render_template('events.html', user=user, events=events)

@app.route('/events/create/21201327', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        event_type = request.form['event_type']
        date_str = request.form['date']
        location = request.form['location']
        max_participants = request.form.get('max_participants')
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format!')
            return redirect(url_for('create_event'))
        
        new_event = Event(
            title=title,
            description=description,
            event_type=event_type,
            date=date,
            location=location,
            max_participants=int(max_participants) if max_participants else None,
            user_id=session['user_id']
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        flash('Event created successfully!')
        return redirect(url_for('events'))
    
    return render_template('create_event.html')

@app.route('/events/<int:event_id>/21201327')
@login_required
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != session['user_id']:
        flash('You can only view your own events!')
        return redirect(url_for('events'))
    return render_template('view_event.html', event=event)

@app.route('/events/<int:event_id>/edit/21201327', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != session['user_id']:
        flash('You can only edit your own events!')
        return redirect(url_for('events'))
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.event_type = request.form['event_type']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%dT%H:%M')
        event.location = request.form['location']
        event.max_participants = int(request.form.get('max_participants')) if request.form.get('max_participants') else None
        event.status = request.form['status']
        
        db.session.commit()
        flash('Event updated successfully!')
        return redirect(url_for('view_event', event_id=event.id))
    
    return render_template('edit_event.html', event=event)

@app.route('/events/<int:event_id>/delete/21201327', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != session['user_id']:
        flash('You can only delete your own events!')
        return redirect(url_for('events'))
    
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!')
    return redirect(url_for('events'))

# Course Repository Routes
@app.route('/courses/21201327')
@login_required
def courses():
    user = User.query.get(session['user_id'])
    search_query = request.args.get('search', '')
    
    if search_query:
        # Search in course code, course name, and department
        courses = Course.query.filter(
            db.or_(
                Course.course_code.ilike(f'%{search_query}%'),
                Course.course_name.ilike(f'%{search_query}%'),
                Course.department.ilike(f'%{search_query}%')
            )
        ).order_by(Course.course_code).all()
    else:
        courses = Course.query.order_by(Course.course_code).all()
    
    return render_template('courses.html', user=user, courses=courses, search_query=search_query)

@app.route('/courses/<int:course_id>/21201327')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    resources = CourseResource.query.filter_by(course_id=course_id).order_by(CourseResource.uploaded_at.desc()).all()
    return render_template('view_course.html', course=course, resources=resources)

@app.route('/courses/<int:course_id>/resources/add/21201327', methods=['GET', 'POST'])
@login_required
def add_resource(course_id):
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        resource_type = request.form['resource_type']
        external_link = request.form.get('external_link', '')
        
        # Handle file upload if resource_type is document
        file_path = None
        file_size = None
        
        if resource_type == 'document':
            if 'file' in request.files:
                file = request.files['file']
                if file and file.filename:
                    # Save file to uploads directory
                    upload_folder = 'uploads'
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    filename = f"{course.course_code}_{file.filename}"
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    file_size = os.path.getsize(file_path)
                else:
                    flash('Please select a file for document type resources.')
                    return redirect(url_for('add_resource', course_id=course_id))
            else:
                flash('Please select a file for document type resources.')
                return redirect(url_for('add_resource', course_id=course_id))
        
        new_resource = CourseResource(
            title=title,
            description=description,
            resource_type=resource_type,
            file_path=file_path,
            external_link=external_link,
            file_size=file_size,
            course_id=course_id
        )
        
        db.session.add(new_resource)
        db.session.commit()
        
        flash('Resource added successfully!')
        return redirect(url_for('view_course', course_id=course_id))
    
    return render_template('add_resource.html', course=course)

@app.route('/courses/resources/<int:resource_id>/delete/21201327', methods=['POST'])
@login_required
def delete_resource(resource_id):
    resource = CourseResource.query.get_or_404(resource_id)
    course_id = resource.course_id
    
    # Delete file if it exists
    if resource.file_path and os.path.exists(resource.file_path):
        os.remove(resource.file_path)
    
    db.session.delete(resource)
    db.session.commit()
    
    flash('Resource deleted successfully!')
    return redirect(url_for('view_course', course_id=course_id))

@app.route('/courses/resources/<int:resource_id>/download/21201327')
@login_required
def download_resource(resource_id):
    resource = CourseResource.query.get_or_404(resource_id)
    
    if resource.file_path and os.path.exists(resource.file_path):
        return send_file(resource.file_path, as_attachment=True, download_name=os.path.basename(resource.file_path))
    else:
        flash('File not found!')
        return redirect(url_for('view_course', course_id=resource.course_id))

# Public API Routes for Course Repository
@app.route('/api/courses/21201327', methods=['GET'])
def api_get_courses():
    """
    PUBLIC API ENDPOINT: Get all courses
    Method: GET
    Authentication: Not required (Public API)
    Returns: JSON array of all courses with resource count
    """
    try:
        search_query = request.args.get('search', '')
        
        if search_query:
            # Search in course code, course name, and department
            courses = Course.query.filter(
                db.or_(
                    Course.course_code.ilike(f'%{search_query}%'),
                    Course.course_name.ilike(f'%{search_query}%'),
                    Course.department.ilike(f'%{search_query}%')
                )
            ).order_by(Course.course_code).all()
        else:
            courses = Course.query.order_by(Course.course_code).all()
        
        courses_data = []
        for course in courses:
            course_data = {
                'course_id': course.id,
                'course_code': course.course_code,
                'course_name': course.course_name,
                'description': course.description,
                'department': course.department,
                'resource_count': len(course.resources),
                'created_at': course.created_at.isoformat() if course.created_at else None
            }
            courses_data.append(course_data)
        
        return jsonify(courses_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<int:course_id>/21201327', methods=['GET'])
def api_get_course(course_id):

    try:
        course = Course.query.get_or_404(course_id)
        resources = CourseResource.query.filter_by(course_id=course_id).order_by(CourseResource.uploaded_at.desc()).all()
        
        course_data = {
            'course_id': course.id,
            'course_code': course.course_code,
            'course_name': course.course_name,
            'description': course.description,
            'department': course.department,
            'created_at': course.created_at.isoformat() if course.created_at else None,
            'resources': []
        }
        
        for resource in resources:
            resource_data = {
                'resource_id': resource.id,
                'title': resource.title,
                'description': resource.description,
                'resource_type': resource.resource_type,
                'file_size': resource.file_size,
                'external_link': resource.external_link,
                'uploaded_at': resource.uploaded_at.isoformat() if resource.uploaded_at else None
            }
            course_data['resources'].append(resource_data)
        
        return jsonify(course_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/<int:course_id>/resources/21201327', methods=['GET'])
def api_get_course_resources(course_id):

    try:
        course = Course.query.get_or_404(course_id)
        resources = CourseResource.query.filter_by(course_id=course_id).order_by(CourseResource.uploaded_at.desc()).all()
        
        resources_data = []
        for resource in resources:
            resource_data = {
                'resource_id': resource.id,
                'title': resource.title,
                'description': resource.description,
                'resource_type': resource.resource_type,
                'file_size': resource.file_size,
                'external_link': resource.external_link,
                'uploaded_at': resource.uploaded_at.isoformat() if resource.uploaded_at else None
            }
            resources_data.append(resource_data)
        
        return jsonify(resources_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/courses/resources/<int:resource_id>/21201327', methods=['GET'])
def api_get_resource(resource_id):
    """
    PUBLIC API ENDPOINT: Get specific resource details
    Method: GET
    Authentication: Not required (Public API)
    Returns: JSON object of resource details
    """
    try:
        resource = CourseResource.query.get_or_404(resource_id)
        
        resource_data = {
            'resource_id': resource.id,
            'title': resource.title,
            'description': resource.description,
            'resource_type': resource.resource_type,
            'file_size': resource.file_size,
            'external_link': resource.external_link,
            'uploaded_at': resource.uploaded_at.isoformat() if resource.uploaded_at else None,
            'course_id': resource.course_id,
            'course_code': resource.course.course_code,
            'course_name': resource.course.course_name
        }
        
        return jsonify(resource_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/21201327', methods=['GET'])
def api_get_events():

    try:
       
        events = Event.query.order_by(Event.date.desc()).all()
        events_data = []
        
        for event in events:
            event_data = {
                'event_id': event.id,
                'event_title': event.title,
                'event_description': event.description,
                'event_type': event.event_type,
                'event_date': event.date.isoformat() if event.date else None,
                'event_location': event.location,
                'max_participants': event.max_participants,
                'current_participants': event.current_participants,
                'event_status': event.status,
                'created_at': event.created_at.isoformat() if event.created_at else None,
                'created_by': event.creator.username if event.creator else None,
                'creator_id': event.user_id
            }
            events_data.append(event_data)
        
        return jsonify(events_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/21201327', methods=['POST'])
def api_create_event():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['title', 'description', 'event_type', 'date', 'location']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    try:
        date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
    
    user_id = data.get('user_id')
    if not user_id:
        default_user = User.query.first()
        if not default_user:
            default_user = User(
                username='public_user',
                email='public@example.com',
                password=generate_password_hash('public123')
            )
            db.session.add(default_user)
            db.session.commit()
        user_id = default_user.id
    
    new_event = Event(
        title=data['title'],
        description=data['description'],
        event_type=data['event_type'],
        date=date,
        location=data['location'],
        max_participants=data.get('max_participants'),
        user_id=user_id
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    return jsonify(new_event.to_dict()), 201

@app.route('/api/events/<int:event_id>/21201327', methods=['GET'])
def api_get_event(event_id):
    """
    PUBLIC API ENDPOINT: Get a specific event by ID
    Method: GET
    Authentication: Not required (Public API)
    Parameters: event_id (integer)
    Returns: JSON object of the event with explicit formatting
    """
    try:
        event = Event.query.get(event_id)
        if not event:
            return jsonify({
                'status': 'error',
                'message': f'Event with ID {event_id} not found',
                'endpoint': f'/api/events/{event_id}/21201327',
                'method': 'GET'
            }), 404
        
        event_data = {
            'event_id': event.id,
            'event_title': event.title,
            'event_description': event.description,
            'event_type': event.event_type,
            'event_date': event.date.isoformat() if event.date else None,
            'event_location': event.location,
            'max_participants': event.max_participants,
            'current_participants': event.current_participants,
            'event_status': event.status,
            'created_at': event.created_at.isoformat() if event.created_at else None,
            'created_by': event.creator.username if event.creator else None,
            'creator_id': event.user_id
        }
        
        return jsonify({
            'status': 'success',
            'message': f'Event {event_id} retrieved successfully',
            'data': event_data,
            'endpoint': f'/api/events/{event_id}/21201327',
            'method': 'GET'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve event: {str(e)}',
            'endpoint': f'/api/events/{event_id}/21201327',
            'method': 'GET'
        }), 500

@app.route('/api/events/<int:event_id>/21201327', methods=['PUT'])
def api_update_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' in data:
        event.title = data['title']
    if 'description' in data:
        event.description = data['description']
    if 'event_type' in data:
        event.event_type = data['event_type']
    if 'date' in data:
        try:
            event.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    if 'location' in data:
        event.location = data['location']
    if 'max_participants' in data:
        event.max_participants = data['max_participants']
    if 'status' in data:
        event.status = data['status']
    
    db.session.commit()
    return jsonify(event.to_dict())

@app.route('/api/events/<int:event_id>/21201327', methods=['DELETE'])
def api_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create sample courses if none exist
        if not Course.query.first():
            sample_courses = [
                Course(
                    course_code='CSE110',
                    course_name='Programming Language I',
                    description='Introduction to programming concepts using Python. Covers basic syntax, data types, control structures, functions, and object-oriented programming fundamentals.',
                    department='Computer Science and Engineering'
                ),
                Course(
                    course_code='CSE111',
                    course_name='Programming Language II',
                    description='Advanced programming concepts including data structures, algorithms, and software development practices.',
                    department='Computer Science and Engineering'
                ),
                Course(
                    course_code='CSE220',
                    course_name='Data Structures',
                    description='Study of fundamental data structures including arrays, linked lists, stacks, queues, trees, and graphs.',
                    department='Computer Science and Engineering'
                ),
                Course(
                    course_code='CSE221',
                    course_name='Algorithms',
                    description='Analysis and design of algorithms, complexity analysis, and algorithm optimization techniques.',
                    department='Computer Science and Engineering'
                ),
                Course(
                    course_code='CSE310',
                    course_name='Database Management Systems',
                    description='Introduction to database concepts, SQL, database design, and database management systems.',
                    department='Computer Science and Engineering'
                )
            ]
            
            for course in sample_courses:
                db.session.add(course)
            
            db.session.commit()
            
            # Add sample resources for CSE110
            cse110 = Course.query.filter_by(course_code='CSE110').first()
            if cse110:
                sample_resources = [
                    CourseResource(
                        title='Week 1 Lecture Notes',
                        description='Introduction to Python programming basics, variables, and data types.',
                        resource_type='document',
                        course_id=cse110.id
                    ),
                    CourseResource(
                        title='Python Installation Guide',
                        description='Step-by-step guide for installing Python and setting up the development environment.',
                        resource_type='link',
                        external_link='https://www.python.org/downloads/',
                        course_id=cse110.id
                    ),
                    CourseResource(
                        title='Assignment 1: Hello World',
                        description='First programming assignment to create a simple Hello World program.',
                        resource_type='assignment',
                        course_id=cse110.id
                    ),
                    CourseResource(
                        title='Course Syllabus',
                        description='Complete course syllabus with topics, schedule, and grading policy.',
                        resource_type='syllabus',
                        course_id=cse110.id
                    )
                ]
                
                for resource in sample_resources:
                    db.session.add(resource)
                
                db.session.commit()
            
            print("Sample courses and resources created successfully!")
    
    app.run(debug=True)
