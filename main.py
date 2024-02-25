from flask import Flask, request, jsonify, render_template
from tpu_model import DialogAssistant
from tpu_find_topic import TopicAssistant
from tpu_parser import LinkParser
from tpu_info_base import TextSearchEngine

app = Flask(__name__)
print("Инициализация парсера")
parser = LinkParser('links.txt')
print("Инициализация парсера завершилась")
print("Запуск парсера")
topic_list, parsed_data = parser.parse_all_pages()
print("Парсер отработал")
print("Инициализация модели")
bot = DialogAssistant()
print("Инициализация модели завершилась")
print("Инициализация топик-модели")
topic_bot = TopicAssistant(topic_list)
print("Инициализация топик-модели завершилась")

messages = []

def process_message(message):
    topic = topic_bot.get_topic(message).strip()
    print(topic)
    search_engine = TextSearchEngine(parsed_data[topic])
    closest_matching_text = search_engine.get_closest_matching_text(message)
    response = bot.get_answer(message,str(closest_matching_text))
    print(topic + "\n" + closest_matching_text[0] + "\n" + closest_matching_text[1] + "\n" + closest_matching_text[2])
    return response
    

# Главная страница с формой для отправки сообщений
@app.route('/')
def index():
    return render_template('index.html', messages=messages)

# API endpoint для отправки сообщений
@app.route('/send_message', methods=['POST'])
def send_message():
    content = request.json['content']
    messages.append({'sender': 'User', 'content': content})
    bot_response = process_message(content)
    messages.append({'sender': 'Bot', 'content': bot_response})
    return jsonify({'status': 'ok', 'bot_response': bot_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)


# 172.20.113.192