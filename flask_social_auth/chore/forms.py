"""Forms for the user blueprint."""
from flask_wtf import Form
from wtforms import PasswordField, TextField
from wtforms.validators import DataRequired, Email, Length

from .models import User


class RegisterForm(Form):

    """Registration form."""

    email = TextField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=254)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=255)]
    )

    def __init__(self, *args, **kwargs):
        """Init the form."""
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        email = User.query.filter_by(email=self.email.data).first()
        if email:
            self.email.errors.append('Email already registered')
            return False
        return True
