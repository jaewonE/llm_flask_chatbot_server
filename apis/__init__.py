from flask import Blueprint, jsonify
from utils.model import able_model_list

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return jsonify({'status': 'success', 'message': 'Welcome to EaiLab chat API.', 'data': {'able_model_list': able_model_list}})
