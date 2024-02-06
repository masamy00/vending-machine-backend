import logging

from flask import jsonify, request
from db.models import User
from utils.aux_functions import make_logger
from functools import wraps

logger = make_logger(__name__)


def check_user_role(roles: list[str]):
    """
    Decorator for checking the role and return unauthorized response or pass the request
    :param roles: specify the authorized role
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = request.headers.get('User-Id')
            user = User.query.get(user_id)
            if not user_id or not user:
                return jsonify({"error": "a valid User-Id is required in the header"}), 401
            if user.role not in roles:
                return jsonify({"error": f"Unauthorized access from role {user.role}"}), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Authentication decorator
def requires_authentication(func):
    """
    Decorator for user authentication:
     - user_id, password should be provided in the request header
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get('User-Id')
        password = request.headers.get('Password')
        logger.debug("User ID: {}, Password: {}".format(user_id, password))

        if not user_id or not password:
            return jsonify({"error": "User-Id and Password are required in the header"}), 401

        user = User.query.get(user_id)

        if not user or not user.check_password(password):
            return jsonify({"error": "Unauthorized access. Invalid User-Id or Password"}), 401

        return func(*args, **kwargs)

    return wrapper
