import os
from datetime import datetime
from typing import List, Optional
from utils.file import load_json, save_json


def get_history(chat_id: str) -> Optional[dict]:
    return load_json(f"history/{chat_id}.json")


def append_history(chat_id: str, user_name: str, query: str, response: str) -> bool:
    history = get_history(chat_id)
    if not history:
        return False
    history['messages'].append({'role': 'user', 'content': query, 'time': datetime.now(
    ).strftime('%Y-%m-%d %H:%M:%S'), 'user_name': user_name})
    history['messages'].append({'role': 'assistant', 'content': response})
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
                'first_message': history['messages'][0]['content'],
                'last_modified_time': history['last_modified_time']
            })
    response_list.sort(key=lambda x: x['last_modified_time'], reverse=True)
    return response_list
