from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from models import db, Job, User, InternshipApplication
from forms import JobForm, ApplicationForm, LoginForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash
from base64 import b64encode

# Initialize the Flask application
app = Flask(__name__)

# Uses a secret key to encrypt session data (unsafe for production)
app.config['SECRET_KEY'] = 'vasudev123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'

# Initialize the database
db.init_app(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Index route (home page). Returns the list of jobs
@app.route('/')
def index():
    jobs = Job.query.all()
    return render_template('job_list.html', jobs=jobs)

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login route. Allows users to log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Check if the form was submitted and if it is valid
    if form.validate_on_submit():

        # Get the username and password from the form
        username = form.username.data
        password = form.password.data

        # Check if the username exists and if the password is correct
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

# Registration route. Allows users to register for an account
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    # Check if the form was submitted and if it is valid
    if form.validate_on_submit():

        # Get the form data
        username = form.username.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = form.password.data
        role = form.role.data

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another username.', 'danger')
        else:
            # Create a new user and hash the password
            new_user = User(username=username, password_hash=generate_password_hash(password), role=role, firstname=firstname, lastname=lastname, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))  # Redirect to the login page after registration
    return render_template('register.html', form=form)

# Profile route. Displays the user's profile
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# Logout route. Logs the user out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# Job details route. Displays the details of a job
@app.route('/job/<int:job_id>')
@login_required
def job_details(job_id):

    # Get the job with the given job_id
    job = Job.query.get(job_id)

    # Case where the user is an intern
    if current_user.role == 'intern':

        # Get application status (whether the user has applied for the job or not)
        application_status = InternshipApplication.query.filter_by(intern_id=current_user.id, job_id=job.id).first() != None
        return render_template('job_details_intern.html', job=job, application_status=application_status, role=current_user.role)
   
    # Case where the user is an employer
    if current_user.role == 'employer':

        # Get all the internship applications for the job
        internship_applications = InternshipApplication.query.filter_by(job_id=job.id).all()

        # Check if the user is the owner of the job (so that they can edit/delete the job)
        can_edit = job.owner == current_user.id
        if can_edit:
            return render_template('job_details_employer.html', job=job, internship_applications=internship_applications, can_edit=can_edit)
        else:
            # If the user is not the owner of the job, they can only view the job details (like an intern)
            return render_template('job_details_intern.html', job=job, application_status=False, role=current_user.role)

# Route for posting a job
@app.route('/employer/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    # Check if user is an authenticated employer
    if not current_user.is_authenticated or not current_user.role == 'employer':
        flash('You do not have permission to post jobs.', 'danger')
        return redirect(url_for('index'))

    form = JobForm()
    # Check if the form was submitted and if it is valid
    if form.validate_on_submit():
        
        # Create a new job
        job = Job(title=form.title.data, description=form.description.data, owner=current_user.id)

        # Add the job to the database
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('post_job.html', form=form)

# Route for deleting a job
@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    # Check if user is an authenticated employer
    if not current_user.is_authenticated or not current_user.role == 'employer':
        flash('You do not have permission to delete jobs.', 'danger')
        return redirect(url_for('index'))
    
    # Check if the job with the given job_id exists
    job = Job.query.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('index'))
    
    # Delete the job from the database
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully', 'success')
    return redirect(url_for('index'))

# Route shown when an application is submitted successfully
@app.route('/application_submitted')
def application_submitted():
    return render_template('application_submitted.html')

# Route for applying to a job
@app.route('/intern/apply_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    form = ApplicationForm()

    # Check if the job with the given job_id exists
    job = Job.query.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('index'))
    
    # Check if the user has already applied for the job
    application_status = InternshipApplication.query.filter_by(intern_id=current_user.id, job_id=job.id).first() != None
    if application_status:
        flash('You have already applied for this job', 'danger')
        return redirect(url_for('index'))

    # Check if the form was submitted
    if form.validate_on_submit():
        resume_blob = None

        # Check if a resume file was uploaded
        if 'resume' in request.files:
            resume_file = request.files['resume']

            # Read the resume file
            if resume_file:
                resume_blob = resume_file.read()
         
        # Encode the resume file as a base64 string
        resume_blob = b64encode(resume_blob)

        # Create a new internship application and add it to the database (with the resume file)
        application = InternshipApplication(intern_id=current_user.id, job_id=job.id, intern=current_user, essay=form.essay.data, resume=resume_blob)
        db.session.add(application)
        db.session.commit()

        return redirect(url_for('application_submitted'))  # Redirect to the success page

    return render_template('apply_job.html', form=form, job=job)

# Route for viewing internship applications
@app.route('/internship_application/<int:application_id>')
@login_required
def internship_application_details(application_id):
    # Check if user is an authenticated employer
    if not current_user.is_authenticated or not current_user.role == 'employer':
        flash('You do not have permission to post jobs.', 'danger')
        return redirect(url_for('index'))
    
    # Check if the internship application with the given application_id exists
    application = InternshipApplication.query.get(application_id)
    if not application:
        flash('Internship application not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('internship_application_details.html', application=application)

# Create the database tables.
with app.app_context():
    db.create_all()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)