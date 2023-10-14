from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileField, FileRequired

# Form for creating a new job
class JobForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])

# Form for creating a new application
class ApplicationForm(FlaskForm):
    essay = TextAreaField('Essay', validators=[DataRequired()])
    resume = FileField('Resume', validators=[FileRequired()])

# Form for a user to log in 
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# Form for creating a new user through registration
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2)])
    email = StringField('Email', validators=[DataRequired(), Length(min=6)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('employer', 'Employer'), ('intern', 'Intern')], validators=[DataRequired()])
    submit = SubmitField('Register')