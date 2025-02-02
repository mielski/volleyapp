from functools import wraps

from flask import redirect, url_for, request
from flask_login import current_user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    decorated_function.login_required = True
    return decorated_function
