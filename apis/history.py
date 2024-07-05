from flask import Blueprint, jsonify
from utils.history import get_history, get_history_list

history_bp = Blueprint('history', __name__)


@history_bp.route('/history/<chat_id>', methods=['GET'])
def get_history_of_chatid(chat_id):
    history = get_history(chat_id)
    if not history:
        return jsonify({'status': 'error', 'message': 'Chat history not found.'}), 404
    return jsonify({'status': 'success', 'message': 'Chat history retrieved successfully.', 'data': {'history': history}})


@history_bp.route('/history/list/all', methods=['GET'])
def list_all_history():
    response_list = get_history_list()
    return jsonify({'status': 'success', 'message': 'All chat histories retrieved successfully.', 'data': {'history_list': response_list}})


@history_bp.route('/history/list/user/<user_name>', methods=['GET'])
def list_user_history(user_name):
    response_list = get_history_list(user_name)
    return jsonify({'status': 'success', 'message': 'User chat histories retrieved successfully.', 'data': {'history_list': response_list}})
