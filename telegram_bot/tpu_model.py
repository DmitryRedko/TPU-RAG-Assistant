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
                 "content": f"""Ты ассистент помощник студентам Томского Политехнического Университета. Тебя создали программисты ТПУ. Тебя зовут Политехник! Отвечай так на всех языках! Ты не Алиса и не DeepSeek! Ответ давай не более чем 200 слов. Ответ дай на основе базы знаний: {info_base}. Пользуйся историей диалога {history} Ссылки ищи в базе."""},
                {"role": "user", "content": user_question},
        ],
            max_tokens=512,
            temperature=0.8,
            stream=False
        )
        answer = response.choices[0].message.content
        self.save_history(answer)
        return answer
    
    def get_history(self):
        return self.history
    
    def save_history(self, output):
        self.history += [output]
        if(len(self.history)>2):
            self.history.pop(0)
        return self.history
            
    
        