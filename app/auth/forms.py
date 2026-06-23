import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')


class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(3, 40)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(8, 128)])
    confirm = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Crear cuenta')

    def validate_username(self, field):
        if not re.match(r'^[a-zA-Z0-9_]+$', field.data):
            raise ValidationError('Solo letras, números y guión bajo.')
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Ese nombre de usuario ya existe.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Ese correo ya está registrado.')

    def validate_password(self, field):
        p = field.data
        if not re.search(r'[A-Z]', p):
            raise ValidationError('Debe tener al menos una mayúscula.')
        if not re.search(r'[0-9]', p):
            raise ValidationError('Debe tener al menos un número.')
        if not re.search(r'[^a-zA-Z0-9]', p):
            raise ValidationError('Debe tener al menos un carácter especial.')
