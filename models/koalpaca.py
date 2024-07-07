from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import prepare_model_for_kbit_training
from utils.env import env
import os
import torch
import re


class KoalpacaModel():
    def __init__(self, model_name='Koalpaca', max_length=512, model_path=None, user_name="고객님", device='cuda'):
        os.environ["TRANSFORMERS_CACHE"] = env.get("KOALPACA_ADAPTER_PATH")
        model_path = env.get(
            "KOALPACA_ADAPTER_PATH") if model_path == None else model_path
        model_id = 'EleutherAI/polyglot-ko-12.8b'
        model = AutoModelForCausalLM.from_pretrained(
            model_path if model_path != None else model_id,
            device_map={"": 0},
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            ))

        self.ask_times = 0

        model.gradient_checkpointing_enable()
        self.model = prepare_model_for_kbit_training(model)
        self.model.eval()
        self.model.config.use_cache = True

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.max_length = max_length
        self.user_name = user_name
        print(f"Load {model_name} model complete.")

    def prefix_answer(self, text: str) -> str:  # 결과를 다 지우는 경우도 고려해야 함.
        print("Get Res")
        print(text)
        start_keyword = "### 답변:"
        end_keyword = "###"

        # '### 답변:' 이후 내용 시작 인덱스를 찾음
        start_idx = text.find(start_keyword) + len(start_keyword)
        # 다음 '###' 섹션을 찾기 위해 start_idx 이후의 내용에서 검색
        end_idx = text.find(end_keyword, start_idx)

        # 답변 내용 추출
        if end_idx == -1:
            answer = text[start_idx:].strip()
        else:
            answer = text[start_idx:end_idx].strip()

        # "1)" 또는 "(1)" 형태를 "1. "로 변환
        answer = re.sub(r'\(?(\d+)\)?\)', r'\1. ', answer)
        # 위의 정규식에서 중복으로 ")"를 처리할 수 있으므로 조정이 필요
        answer = re.sub(r'\. \)', r'. ', answer)

        # 숫자로 시작하는 답변들을 새로운 줄에 배치
        formatted_answer = re.sub(r'(\d+)\.', r'\n\1.', answer)

        formatted_answer = formatted_answer.replace(
            '�', '').replace("사우님", self.user_name)

        # 대괄호로 시작하는 문장을 찾고 그 이후 모든 내용 삭제
        formatted_answer = re.sub(
            r'\[.*?\].*', '', formatted_answer, flags=re.DOTALL)

        # 숫자 리스트 항목을 찾아서 개행을 삽입
        formatted_answer = re.sub(r'(\d+)\.\s*', r'\n\1. ', formatted_answer)
        # 별표(*)로 시작하는 리스트 항목을 찾아서 개행을 삽입
        formatted_answer = re.sub(r'\*\s*', r'\n* ', formatted_answer)

        # 두 개 이상의 연속된 개행을 하나로 조정
        formatted_answer = re.sub(r'\n{2,}', '\n', formatted_answer)
        # 숫자 리스트와 별표 리스트의 끝에는 추가 개행을 삽입하지 않음
        # 문장 끝에 개행 제거
        formatted_answer = re.sub(r'\n$', '', formatted_answer)

        # 첫째, 둘째, 셋째와 같은 형식을 새 줄로 시작하게 함
        formatted_answer = re.sub(
            r'(첫째,|둘째,|셋째,|넷째,|다섯째,|여섯째,|일곱째,|여덟째,|아홉째,|열째,)', r'\n\n\1 ', formatted_answer)
        # 첫 번째, 두 번째, 세 번째와 같은 형식을 새 줄로 시작하게 함
        formatted_answer = re.sub(
            r'(첫 번째,|두 번째,|세 번째,|네 번째,|다섯 번째,|여섯 번째,|일곱 번째,|여덟 번째,|아홉 번째,|열 번째,)', r'\n\n\1 ', formatted_answer)

        # 연속된 개행을 하나로 조정
        formatted_answer = re.sub(r'\n+', '\n', formatted_answer).strip()

        # 각 문단을 개별적으로 처리하며, 올바른 구두점으로 끝나는 문장만 선택
        paragraphs = formatted_answer.split('\n')
        filtered_paragraphs = []
        previous_line = None

        for line in paragraphs:
            # 문장 구분에 빈 줄을 두는 방식은 유지
            if previous_line and not re.match(r'^(\d+\.|\*)', previous_line) and not re.match(r'^(\d+\.|\*)', line):
                filtered_paragraphs.append('')  # 빈 줄 추가 (문단 사이)

            if self.is_complete_sentence(line):
                filtered_paragraphs.append(line)
            previous_line = line
        filtered_paragraphs = [line.lstrip() for line in filtered_paragraphs]
        filtered_paragraphs_text = '\n'.join(filtered_paragraphs)
        filtered_paragraphs_text = re.sub(
            r'\n+', '\n', filtered_paragraphs_text).strip()
        print("filtered_paragraphs_text")
        print(filtered_paragraphs_text)
        return filtered_paragraphs_text

    # 문장을 끝내는 올바른 구두점인지 확인하는 함수
    def is_complete_sentence(self, sentence):
        return re.search(r'[.!?]$', sentence.strip()) is not None

    def extract_nth_occurrence(self, input_text: str, keyword: str, n: int) -> str:
        # Find the starting index of the nth occurrence of the keyword
        current_index = -1
        for _ in range(n):
            current_index = input_text.find(keyword, current_index + 1)
            if current_index == -1:
                break

        if current_index == -1:
            # If nth occurrence not found, find the last occurrence
            current_index = input_text.rfind(keyword)

        # Extract and return the substring starting from the found occurrence till the end
        return input_text[current_index:] if current_index != -1 else ""

    def generate_response(self, prompt, messages=[]):
        ask_message = ""
        for message in messages:
            if message['role'] == 'user':
                ask_message += f"### 질문: {message['content']}\n\n### 답변:"
            elif message['role'] == 'assistant':
                ask_message += f"{ message['content']}\n\n"

        ask_message += f"### 질문: {prompt}\n\n### 답변:"
        print("Prompt Input")
        print(ask_message)

        gened = self.model.generate(
            **self.tokenizer(
                ask_message,
                return_tensors='pt',
                return_token_type_ids=False
            ),
            max_new_tokens=self.max_length,
            early_stopping=True,
            do_sample=True,
            eos_token_id=2,
        )
        res = self.tokenizer.decode(gened[0])
        if len(messages) > 0:
            res = self.extract_nth_occurrence(res, "### 답변:", len(messages))
        answer = self.prefix_answer(res)

        return answer

    def set_max_length(self, max_length):
        self.max_length = max_length
