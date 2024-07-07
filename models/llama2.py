from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from huggingface_hub import login
from peft import PeftModel
from utils.env import env
import os
import torch


class Lamma2Model():
    def __init__(self, model_name='Lamma2', max_length=512, device='cuda'):
        os.environ["TRANSFORMERS_CACHE"] = env.get("MODEL_CAHCE_PATH")
        model = "meta-llama/Llama-2-7b-chat-hf"
        access_token = env.get("HF_ACCESS")
        login(token=access_token)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        self.tokenizer = AutoTokenizer.from_pretrained(model)
        auto_model = AutoModelForCausalLM.from_pretrained(
            model,
            token=access_token,
            quantization_config=bnb_config,
            device_map={"": 0},
        )
        self.model = PeftModel.from_pretrained(model=auto_model,
                                               model_id=env.get("LLAMA2_MODEL_ID"))
        self.model.to(device)
        self.max_length = max_length
        print(f"Load {model_name} model complete.")

    def generate_response(self, x, messages=[]):
        tokenizer_res = self.tokenizer(
            #                 f"### 질문: {x}\n\n### 답변:",
            x,
            return_tensors='pt',
            return_token_type_ids=False
        )
        gened = self.model.generate(
            **tokenizer_res,
            max_new_tokens=self.max_length,
            early_stopping=True,
            do_sample=True,
            eos_token_id=2,
        )
        res = self.tokenizer.decode(gened[0])
        if res.startswith("<s>"):
            res = res[len("<s>"):]
        if res.endswith("</s>"):
            res = res[:-len("</s>")]
        return res

    def set_max_length(self, max_length):
        self.max_length = max_length
