"""Forms for the public blueprint."""
from flask_wtf import Form
from flask_social_auth.user.models import User
from wtforms import PasswordField, TextField
from wtforms.validators import DataRequired


class LoginForm(Form):

    """Login form."""

    email = TextField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Init the form."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user:
            self.email.errors.append('Unknown email address')
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        if not self.user.active:
            self.email.errors.append('User not activated')
            return False
        return True
