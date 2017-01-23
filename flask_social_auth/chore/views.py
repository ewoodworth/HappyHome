"""The views for the user blueprint."""
from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint(
    'user',
    __name__,
    url_prefix='/users',
    static_folder='../static'
)


@blueprint.route('/')
@login_required
def members():
    """Placeholder page for members only."""
    return render_template('users/members.html')


@blueprint.route('/foo')
@login_required
def foo_fn():
    """Placeholder page for members only."""
    return render_template('users/members.html')
