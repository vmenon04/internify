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


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vasudev123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
    jobs = Job.query.all()
    return render_template('job_list.html', jobs=jobs)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

# Create registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/job/<int:job_id>')
@login_required
def job_details(job_id):
    job = Job.query.get(job_id)

    if current_user.role == 'intern':
        application_status = InternshipApplication.query.filter_by(intern_id=current_user.id, job_id=job.id).first() != None
        return render_template('job_details_intern.html', job=job, application_status=application_status, role=current_user.role)
    if current_user.role == 'employer':
        internship_applications = InternshipApplication.query.filter_by(job_id=job.id).all()
        can_edit = job.owner == current_user.id
        if can_edit:
            return render_template('job_details_employer.html', job=job, internship_applications=internship_applications, can_edit=can_edit)
        else:
            return render_template('job_details_intern.html', job=job, application_status=False, role=current_user.role)


@app.route('/employer/post_job', methods=['GET', 'POST'])
@login_required
def post_job():
    # Check if user is an authenticated employer
    if not current_user.is_authenticated or not current_user.role == 'employer':
        flash('You do not have permission to post jobs.', 'danger')
        return redirect(url_for('index'))

    form = JobForm()
    if form.validate_on_submit():
        job = Job(title=form.title.data, description=form.description.data, owner=current_user.id)
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('post_job.html', form=form)

@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    # Check if user is an authenticated employer
    if not current_user.is_authenticated or not current_user.role == 'employer':
        flash('You do not have permission to delete jobs.', 'danger')
        return redirect(url_for('index'))
    
    job = Job.query.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('index'))
    
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted successfully', 'success')
    return redirect(url_for('index'))


@app.route('/application_submitted')
def application_submitted():
    return render_template('application_submitted.html')

@app.route('/intern/apply_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    form = ApplicationForm()

    # Check if the job with the given job_id exists
    job = Job.query.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('index'))
    
    application_status = InternshipApplication.query.filter_by(intern_id=current_user.id, job_id=job.id).first() != None
    if application_status:
        flash('You have already applied for this job', 'danger')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        resume_blob = None

        # Check if a resume file was uploaded
        if 'resume' in request.files:
            resume_file = request.files['resume']

            if resume_file:
                resume_blob = resume_file.read()
        resume_blob = b64encode(resume_blob)
        application = InternshipApplication(intern_id=current_user.id, job_id=job.id, intern=current_user, essay=form.essay.data, resume=resume_blob)
        db.session.add(application)
        db.session.commit()

        return redirect(url_for('application_submitted'))  # Redirect to the success page

    return render_template('apply_job.html', form=form, job=job)

@app.route('/internship_application/<int:application_id>')
@login_required
def internship_application_details(application_id):
    # Check if user is an authenticated employer
    if not current_user.is_authenticated or not current_user.role == 'employer':
        flash('You do not have permission to post jobs.', 'danger')
        return redirect(url_for('index'))
    
    application = InternshipApplication.query.get(application_id)
    if not application:
        flash('Internship application not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('internship_application_details.html', application=application)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)