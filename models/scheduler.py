import threading
from queue import Queue
from time import sleep, time
from models.mock import MockModel


class ModelScheduler():
    def __init__(self):
        self.models = {}
        self.lock = threading.Lock()
        self.request_queues = {}

    def add_model(self, model_name, model):
        with self.lock:
            self.models[model_name] = model
            self.request_queues[model_name] = Queue()

    def generate(self, model_name: str, prompt: str):
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")

        result = Queue()
        self.request_queues[model_name].put((prompt, result))
        response = result.get()
        return response

    def _process_requests(self, model_name):
        while True:
            prompt, result = self.request_queues[model_name].get()
            response = self.models[model_name].generate_response(prompt)
            result.put(response)

    def start_processing(self):
        for model_name in self.models.keys():
            thread = threading.Thread(
                target=self._process_requests, args=(model_name,))
            thread.daemon = True
            thread.start()


# Usage example
if __name__ == "__main__":
    scheduler = ModelScheduler()

    # Add models
    model_a = MockModel(model_name="ModelA")
    model_b = MockModel(model_name="ModelB")
    scheduler.add_model("ModelA", model_a)
    scheduler.add_model("ModelB", model_b)

    # Start processing requests
    scheduler.start_processing()

    # Generate responses
    def async_generate(scheduler, model_name, prompt):
        response = scheduler.generate(model_name, prompt)

    # Create threads to simulate asynchronous requests
    threading.Thread(target=async_generate, args=(
        scheduler, "ModelA", "Model A-1")).start()
    threading.Thread(target=async_generate, args=(
        scheduler, "ModelA", "Model A-2")).start()
    threading.Thread(target=async_generate, args=(
        scheduler, "ModelB", "Model B-1")).start()
    threading.Thread(target=async_generate, args=(
        scheduler, "ModelB", "Model B-2")).start()

    # Keep the main thread alive to let background threads finish
    while threading.active_count() > 1:
        sleep(0.1)
