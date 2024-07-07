from flask import Blueprint, request, jsonify, g
from utils.validate import validate_json
from utils.user import get_user_info, append_user_info
from utils.jwt import jwt_instance
import bcrypt

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/signup', methods=['POST'])
@validate_json(['user_name', 'user_password'])
def signup_api():
    user_name, user_password = g.data['user_name'], g.data['user_password']
    if get_user_info(user_name):
        return jsonify({'status': 'error', 'message': 'User already exists.'}), 400
    hashed_password = bcrypt.hashpw(
        user_password.encode(), bcrypt.gensalt()).decode()
    append_user_info(user_name, hashed_password)
    return jsonify({
        'status': 'success',
        'message': 'User created successfully.',
        'x-jwt': jwt_instance.sign_user(user_name)})


@user_bp.route('/user/signin', methods=['POST'])
@validate_json(['user_name', 'user_password'])
def signin_api():
    user_name, user_password = g.data['user_name'], g.data['user_password']
    user_info = get_user_info(user_name)
    if not user_info:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404
    if not bcrypt.checkpw(user_password.encode(), user_info['user_password'].encode()):
        return jsonify({'status': 'error', 'message': 'Password incorrect.'}), 400
    return jsonify({
        'status': 'success',
        'message': 'Login successful.',
        'x-jwt': jwt_instance.sign_user(user_name)})
