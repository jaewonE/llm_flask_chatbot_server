from transformers import AutoTokenizer, AutoModelForCausalLM


class GemmaModel():
    def __init__(self, model_name='Gemma', max_length=30):
        self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-2b")
        self.model = AutoModelForCausalLM.from_pretrained("google/gemma-2b")
        self.max_length = max_length
        print(f"Load {model_name} model complete.")

    def generate_response(self, prompt, messages=[]):
        input_ids = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**input_ids, max_length=self.max_length)
        res = self.tokenizer.decode(outputs[0])
        if res.startswith("<bos>"):
            res = res[len("<bos>"):]
        if res.endswith("<eos>"):
            res = res[:-len("<eos>")]
        return res

    def set_max_length(self, max_length):
        self.max_length = max_length
