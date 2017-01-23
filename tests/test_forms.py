"""Test the forms."""
from flask_social_auth.public.forms import LoginForm
from flask_social_auth.user.forms import RegisterForm


class TestRegisterForm:

    """Test register form."""

    def test_validate_email_already_registered(self, user):
        """Enter email that is already registered."""
        form = RegisterForm(email=user.email, password='example')

        assert form.validate() is False
        assert 'Email already registered' in form.email.errors

    def test_validate_success(self, db):
        """Test validate success."""
        form = RegisterForm(email='new@test.test', password='example')
        assert form.validate() is True


class TestLoginForm:

    """Test login form."""

    def test_validate_success(self, user):
        """Test validate success."""
        user.set_password('example')
        user.save()
        form = LoginForm(email=user.email, password='example')
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_email(self, db):
        """Test unknown email."""
        form = LoginForm(email='unknown@u.com', password='example')
        assert form.validate() is False
        assert 'Unknown email' in form.email.errors
        assert form.user is None

    def test_validate_invalid_password(self, user):
        """Test invalid password."""
        user.set_password('example')
        user.save()
        form = LoginForm(email=user.email, password='wrongpassword')
        assert form.validate() is False
        assert 'Invalid password' in form.password.errors

    def test_validate_inactive_user(self, user):
        """Test validate inactive user."""
        user.active = False
        user.set_password('example')
        user.save()
        # Correct email and password, but user is not activated
        form = LoginForm(email=user.email, password='example')
        assert form.validate() is False
        assert 'User not activated' in form.email.errors
