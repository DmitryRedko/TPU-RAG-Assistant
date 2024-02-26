from tpu_info_base import TextSearchEngine
from openai import OpenAI
from config import OPEN_AI_TOKEN, WEB_URL

class DialogAssistant:
    def __init__(self):
        self.history = []
        self.client = OpenAI(api_key=OPEN_AI_TOKEN, base_url=WEB_URL)

    def get_answer(self, user_question,info_base):
        history = self.get_history()
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", 
                 "content": f"""Ты ассистент помощник студентам Томского Политехнического Университета. Тебя зовут политехник! Отвечай так на всех языках! Ты не Алиса и не DeepSeek Ничего не придумывай! Ответ давай не более чем 200 слов. Ответ дай на основе базы знаний: {info_base}. Пользуйся историей диалога {history} Ссылки ищи в базе."""},
                {"role": "user", "content": user_question},
        ],
            max_tokens=512,
            temperature=0.8,
            stream=False
        )
        answer = response.choices[0].message.content
        self.save_history(answer)
        return answer
    
    def get_base_info(self, user_question):
        info_base = self.search_engine.get_closest_matching_text(user_question)
        res_str = ""
        break_counter=0
        for i in range(len(info_base)):
            res_str += str([info_base[i]])
            break_counter+=1
            if(break_counter==3):
                break
        return res_str
    
    def get_history(self):
        return self.history
    
    def save_history(self, output):
        self.history += [output]
        if(len(self.history)>2):
            self.history.pop(0)
        return self.history
            
    
        