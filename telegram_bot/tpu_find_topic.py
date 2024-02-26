from openai import OpenAI
from config import OPEN_AI_TOKEN, WEB_URL

class TopicAssistant:
    def __init__(self,topic_list):
        self.client = OpenAI(api_key=OPEN_AI_TOKEN, base_url=WEB_URL)
        self.topic_list = topic_list

    def get_topic(self, user_question):
        self
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", 
                 "content": f"""Из списка {self.topic_list} выбери наиболее близкий и верни без изменений и без кавычек. Только элемент списка, ничего больше. Если не соответствует ничему, возвращай 'Другое'. Отвечать на вопросы не нужно."""},
                {"role": "user", "content": user_question},
        ],
            max_tokens=100,
            temperature=0.7,
            stream=False
        )
        answer = response.choices[0].message.content
        return answer
    

            
    
        