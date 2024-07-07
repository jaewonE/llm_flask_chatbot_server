from time import sleep
from utils.env import env


class MockModel():
    def __init__(self, max_length=30, delay=3, init_delay=2, model_name="MockModel"):
        self.max_length = max_length
        self.delay = delay
        sleep(init_delay)
        print(f"Load {model_name} model complete.")

    def generate_response(self, prompt, messages=[]):
        sleep(self.delay)
        return prompt

    def set_max_length(self, max_length):
        self.max_length = max_length
