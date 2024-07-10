from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={
        'class': 'form-control', 'placeholder': 'Username'
    })
    first_name = StringField('First Name', validators=[
                             DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={
                            'class': 'form-control', 'placeholder': 'Last Name'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={
                        'class': 'form-control', 'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={
                             'class': 'form-control', 'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')], render_kw={'class': 'form-control', 'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired(
    )], render_kw={'class': 'form-control', 'placeholder': 'Username or Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={
                             'class': 'form-control', 'placeholder': 'Password'})
    submit = SubmitField('Sign In')

class ClientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'Username'})
    company_name = StringField('Company Name', validators=[DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'Company Name'})
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'First Name'})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'Last Name'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'class': 'form-control', 'placeholder': 'Email'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'class': 'form-control', 'placeholder': 'Password'})
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')], render_kw={'class': 'form-control', 'placeholder': 'Confirm Password'})
    submit = SubmitField('Sign Up')