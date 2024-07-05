from flask import g, request, jsonify
from functools import wraps


def validate_json(required_fields):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not request.is_json:
                return jsonify({'status': 'error', 'message': 'Invalid JSON format.'}), 400
            data = request.get_json()
            missing_field = next(
                (field for field in required_fields if field not in data), None)
            if missing_field:
                return jsonify({'status': 'error', 'message': f'{missing_field} not provided.'}), 400
            g.data = data
            return f(*args, **kwargs)
        return wrapped
    return decorator
