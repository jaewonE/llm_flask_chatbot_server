from apis import main_bp
from apis.user import user_bp
from apis.history import history_bp
from apis.chat import chat_bp
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(user_bp)
    return app


app = create_app()

if __name__ == '__main__':
    app.run('0.0.0.0', port=8502, debug=True)
