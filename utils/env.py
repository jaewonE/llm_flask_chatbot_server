from dotenv import load_dotenv
import os


class Env():
    def __init__(self):
        load_dotenv()

    def get(self, key):
        return os.getenv(key)

    def set(self, key, value):
        os.environ[key] = value

    def unset(self, key):
        os.environ.pop(key)


env = Env()
