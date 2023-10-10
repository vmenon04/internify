from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from models import db, Job, Employer, Intern
from forms import JobForm, ApplicationForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vasudev123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'

db.init_app(app)

@app.route('/')
def index():
    jobs = Job.query.all()
    return render_template('job_list.html', jobs=jobs)

@app.route('/job/<int:job_id>')
def job_details(job_id):
    job = Job.query.get(job_id)
    return render_template('job_details.html', job=job)

@app.route('/employer/post_job', methods=['GET', 'POST'])
def post_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(title=form.title.data, description=form.description.data)
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('post_job.html', form=form)

@app.route('/application_submitted')
def application_submitted():
    return render_template('application_submitted.html')

@app.route('/intern/apply_job/<int:job_id>', methods=['GET', 'POST'])
def apply_job(job_id):
    form = ApplicationForm()
    
    # Check if the job with the given job_id exists
    job = Job.query.get(job_id)
    if not job:
        flash('Job not found', 'danger')
        return redirect(url_for('index'))
    
    if form.validate_on_submit():
        intern = Intern(name=form.name.data, email=form.email.data)
        db.session.add(intern)
        db.session.commit()
        return redirect(url_for('application_submitted'))  # Redirect to the success page
    
    return render_template('apply_job.html', form=form, job=job)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
