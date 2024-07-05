from flask import Blueprint, jsonify, g
from uuid import uuid4
from datetime import datetime
from utils.file import save_json
from utils.model import load_model, model_locks, able_model_list
from utils.validate import validate_json

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat/new', methods=['POST'])
@validate_json(['model_name', 'user_name', 'query'])
def new_chat():
    model_name, user_name, query = g.data['model_name'], g.data['user_name'], g.data['query']
    max_length = g.data.get('max_length', 512)

    if model_name not in able_model_list:
        return jsonify({'status': 'error', 'message': 'Model not found.'}), 400

    model = load_model(model_name, max_length=max_length)
    chat_id = str(uuid4())
    cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    model_lock = model_locks[model_name]
    with model_lock:
        response = model.generate_response(query)

    history = {
        'init_time': cur_time,
        'last_modified_time': cur_time,
        'chat_id': chat_id,
        'creater': user_name,
        'model_name': model_name,
        'messages': [
            {'role': 'user', 'content': query,
                'time': cur_time, 'user_name': user_name},
            {'role': 'assistant', 'content': response}
        ]
    }
    save_json(f"history/{chat_id}.json", history)

    return jsonify({'status': 'success', 'message': 'Chat created successfully.', 'data': {'chat_id': chat_id, 'answer': response}})


@chat_bp.route('/chat/<chat_id>', methods=['POST'])
@validate_json(['model_name', 'user_name', 'query'])
def add_message(chat_id):
    model_name, user_name, query = g.data['model_name'], g.data['user_name'], g.data['query']
    max_length = g.data.get('max_length', 512)

    if model_name not in able_model_list:
        return jsonify({'status': 'error', 'message': 'Model not found.'}), 400

    history = get_history(chat_id)
    if not history:
        return jsonify({'status': 'error', 'message': 'Chat history not found.'}), 404

    model = load_model(model_name, max_length=max_length)

    model_lock = model_locks[model_name]
    with model_lock:
        response = model.generate_response(query, history['messages'])

    if not append_history(chat_id, user_name, query, response):
        return jsonify({'status': 'error', 'message': 'Chat history not found.'}), 404

    return jsonify({'status': 'success', 'message': 'Message added successfully.', 'data': {'answer': response}})
