from flask import render_template
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        token = get_jwt()
        if token["sub"] != 'admin':
            return render_template('error.html', text_error='Access denied!')
        return fn(*args, **kwargs)
    return wrapper