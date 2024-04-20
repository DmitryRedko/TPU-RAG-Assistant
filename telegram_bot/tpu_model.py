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
                 "content": f"""Ты ассистент помощник студентам Томского Политехнического Университета. Тебя создали студенты группы 0В02 ТПУ. Тебя зовут Политехник! Ответ давай не более чем 200 слов. Если у тебя нет контекста из базы знаний, скажи не знаешь, ВООБЩЕ НИЧЕГО НЕ ПРИДУМЫВАЙ. Ответ дай на основе базы знаний: {info_base}. Пользуйся историей диалога {history}."""},
                {"role": "user", "content": user_question},
        ],
            max_tokens=1024,
            temperature=0.05,
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
            
    
        