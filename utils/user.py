from typing import Optional
from utils.file import load_json, save_json
from constants.path import USER_INFO_PATH


def get_user_info(user_name: str) -> Optional[dict]:
    user_json = load_json(USER_INFO_PATH)
    return user_json.get(user_name)


def append_user_info(user_name: str) -> None:
    user_json = load_json(USER_INFO_PATH)
    user_json[user_name] = {'user_name': user_name}
    save_json(USER_INFO_PATH, user_json)
