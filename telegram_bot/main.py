# from flask import Flask, request, jsonify, render_template
# from tpu_model import DialogAssistant
# from tpu_find_topic import TopicAssistant
# from tpu_parser import LinkParser
# from tpu_info_base import TextSearchEngine

# app = Flask(__name__)
# print("Инициализация парсера")
# parser = LinkParser('links.txt')
# print("Инициализация парсера завершилась")
# print("Запуск парсера")
# topic_list, parsed_data = parser.parse_all_pages()
# print("Парсер отработал")
# print("Инициализация модели")
# bot = DialogAssistant()
# print("Инициализация модели завершилась")
# print("Инициализация топик-модели")
# topic_bot = TopicAssistant(topic_list)
# print("Инициализация топик-модели завершилась")

# messages = []

# def process_message(message):
#     topic = topic_bot.get_topic(message).strip().replace("'", '').replace('Ответ: ', '').replace('"', '')
#     print(topic)
#     search_engine = TextSearchEngine(parsed_data[topic])
#     closest_matching_text = search_engine.get_closest_matching_text(message)
#     response = bot.get_answer(message,str(closest_matching_text))
#     print(topic + "\n" + closest_matching_text[0] + "\n" + closest_matching_text[1] + "\n" + closest_matching_text[2])
#     return response
    

# # Главная страница с формой для отправки сообщений
# @app.route('/')
# def index():
#     return render_template('index.html', messages=messages)

# # API endpoint для отправки сообщений
# @app.route('/send_message', methods=['POST'])
# def send_message():
#     content = request.json['content']
#     messages.append({'sender': 'User', 'content': content})
#     bot_response = process_message(content)
#     messages.append({'sender': 'Bot', 'content': bot_response})
#     return jsonify({'status': 'ok', 'bot_response': bot_response})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5025)


# 172.20.113.192


import telebot
from telebot import types
from config import BOT_TOKEN
from tpu_model import DialogAssistant
from tpu_find_topic import TopicAssistant
from tpu_parser import LinkParser
from tpu_info_base import TextSearchEngine

print("Инициализация парсера")
parser = LinkParser('links.txt')
print("Инициализация парсера завершилась")
print("Запуск парсера")
topic_list, parsed_data = parser.parse_all_pages()
print("Парсер отработал")
print("Инициализация модели")
llm_model = DialogAssistant()
print("Инициализация модели завершилась")
print("Инициализация топик-модели")
topic_bot = TopicAssistant(topic_list)
print("Инициализация топик-модели завершилась")


bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник!", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', parse_mode='Markdown')
    elif(len(message.text)>0):
        bot.send_message(message.from_user.id, "Дайте мне минуту на размышления!", parse_mode='Markdown')
        try:
            topic = topic_bot.get_topic(message.text).strip().replace("'", '').replace('Ответ: ', '').replace('"', '').replace("[",'').replace("]",'').replace("(",'').replace(")",'')
            print("\n=============================================================================\nВОПРОС:\t",message.text,"\n")
            print("ТОПИК:\t",topic)
            try:
                search_engine = TextSearchEngine(parsed_data[topic])
            except:
                search_engine = TextSearchEngine(parsed_data["Другое"])
                
            closest_matching_text = search_engine.get_closest_matching_text(message.text)
            response = llm_model.get_answer(message.text,str(closest_matching_text))
            print("\n*******************************************\n БАЗА знаний\t")
            for x in closest_matching_text:
                print(x)
            print("\n*******************************************\n")
                # response = "Упс, ошибка. Попробуйте задать вопрос ещё раз!"
            print("ОТВЕТ\t", response,"\n=============================================================================\n")
        except:
            response = "Ой, вышла ошибка. Я не могу сейчас дать ответ на этот вопрос. Можете попробовть спросить еще раз или уточнить какую-либо другую информацию. Буду рад помочь!"
        bot.send_message(message.from_user.id, response, parse_mode='Markdown')



bot.polling(none_stop=True, interval=0) 