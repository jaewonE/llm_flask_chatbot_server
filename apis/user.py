from flask import Blueprint, request, jsonify, g
from utils.validate import validate_json
from utils.user import get_user_info, append_user_info

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/signup', methods=['POST'])
@validate_json(['user_name'])
def signup_api():
    user_name = g.data['user_name']
    if get_user_info(user_name):
        return jsonify({'status': 'error', 'message': 'User already exists.'}), 400
    append_user_info(user_name)
    return jsonify({'status': 'success', 'message': 'User created successfully.'})


@user_bp.route('/user/signin', methods=['POST'])
@validate_json(['user_name'])
def signin_api():
    user_name = g.data['user_name']
    user_info = get_user_info(user_name)
    if not user_info:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404
    return jsonify({'status': 'success', 'message': 'Login successful.'})
