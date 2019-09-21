from functools import wraps
from flask import jsonify, make_response
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def with_required_roles(group=[]):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()["identity"]

            if user["role"] not in group:
                error_response = jsonify(msg='Unauthorized user.')
                return make_response(error_response, 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator