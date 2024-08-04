from flask import Blueprint, jsonify, g
from uuid import uuid4
from datetime import datetime
from utils.file import save_json
from utils.model import load_model, able_model_list, scheduler
from utils.validate import validate_json
from utils.history import get_history, append_history
from utils.jwt import jwt_required
from uuid import uuid4

chat_bp = Blueprint('chat', __name__)

# http://localhost:8502/chat/new # 새로운 채팅


@chat_bp.route('/chat/new', methods=['POST'])
@jwt_required
@validate_json(['model_name', 'user_name', 'query'])
def new_chat():
    model_name, user_name, query = g.data['model_name'], g.data['user_name'], g.data['query']
    max_length = g.data.get('max_length', 512)

    if model_name not in able_model_list:
        return jsonify({'status': 'error', 'message': 'Model not found.'}), 400

    load_model(model_name, max_length=max_length)
    chat_id = str(uuid4())
    cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    response = scheduler.generate(model_name, query)

    history = {
        'init_time': cur_time,
        'last_modified_time': cur_time,
        'chat_id': chat_id,
        'creater': user_name,
        'model_name': model_name,
        'messages': [
            {'role': 'user',
             'content': query,
             'mes_id': str(uuid4()),
             'time': cur_time,
             'user_name': user_name},
            {'role': 'assistant',
             'content': response,
             'mes_id': str(uuid4()),
             'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             'user_name': 'assistant'}
        ]
    }
    save_json(f"history/{chat_id}.json", history)

    return jsonify({'status': 'success', 'message': 'Chat created successfully.', 'data': {'chat_id': chat_id, 'answer': response}})

 # http://localhost:8502/chat/<chat_id>
 # 기존에 있던 채팅 방에서 이어 채팅하기.


@chat_bp.route('/chat/<chat_id>', methods=['POST'])
@jwt_required
@validate_json(['model_name', 'user_name', 'query'])
def add_message(chat_id):
    model_name, user_name, query = g.data['model_name'], g.data['user_name'], g.data['query']
    max_length = g.data.get('max_length', 512)

    if model_name not in able_model_list:
        return jsonify({'status': 'error', 'message': 'Model not found.'}), 400

    history = get_history(chat_id)
    if not history:
        return jsonify({'status': 'error', 'message': 'Chat history not found.'}), 404

    if not append_history(chat_id, user_name, query):
        return jsonify({'status': 'error', 'message': 'Chat history not found.'}), 404

    load_model(model_name, max_length=max_length)

    response = scheduler.generate(model_name, query, history['messages'])

    if not append_history(chat_id, 'assistant', response):
        return jsonify({'status': 'error', 'message': 'Chat history not found.'}), 404

    return jsonify({'status': 'success', 'message': 'Message added successfully.', 'data': {'answer': response}})
