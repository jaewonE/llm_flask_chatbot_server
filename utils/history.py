import os
from datetime import datetime
from typing import List, Optional
from utils.file import load_json, save_json
from uuid import uuid4


def get_history(chat_id: str) -> Optional[dict]:
    history = load_json(f"history/{chat_id}.json")
    messages = history.get('messages', [])
    messages.sort(key=lambda x: x['time'], reverse=True)
    history['messages'] = messages
    return history


def append_history(chat_id: str, user_name: str, query: str, response: str) -> bool:
    history = get_history(chat_id)
    if not history:
        return False
    history['messages'].append(
        {'role': 'user',
         'content': query,
         'mes_id': str(uuid4()),
         'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         'user_name': user_name})
    history['messages'].append(
        {'role': 'assistant',
         'content': response,
         'mes_id': str(uuid4()),
         'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
         'user_name': 'assistant'})
    history['last_modified_time'] = datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S')
    save_json(f"history/{chat_id}.json", history)
    return True


def get_history_list(user_name: Optional[str] = None) -> List[dict]:
    history_files = [f for f in os.listdir("history") if f.endswith(".json")]
    response_list = []
    for file in history_files:
        history = load_json(f"history/{file}")
        if user_name is None or history['creater'] == user_name:
            response_list.append({
                'chat_id': history['chat_id'],
                'creater': history['creater'],
                'model_name': history['model_name'],
                'last_message': history['messages'][-1]['content'],
                'last_modified_time': history['last_modified_time']
            })
    response_list.sort(key=lambda x: x['last_modified_time'], reverse=True)
    return response_list
