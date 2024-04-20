import telebot
from telebot import types
from config import BOT_TOKEN
from tpu_model import DialogAssistant
from tpu_find_topic import TopicAssistant
from tpu_parser import LinkParser
from tpu_info_base import TextSearchEngine
import logging
from datetime import datetime, timedelta

# Настройка логгирования
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(message)s')

# Функция для форматирования времени
def current_time():
    return datetime.now().strftime("%H:%M:%S")

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

# Инициализация бота
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
    elif len(message.text) > 0:
        bot.send_message(message.from_user.id, "Дайте мне минуту на размышления!", parse_mode='Markdown')
        try:
            first_time = current_time()
            logging.info("\n=============================================================================\n"+ first_time + "\tВОПРОС:\t" + message.text)
            topic = topic_bot.get_topic(message.text).strip().replace("'", '').replace('Ответ: ', '').replace('"', '').replace("[",'').replace("]",'').replace("(",'').replace(")",'')
            logging.info("ТОПИК:\t" + topic)
            try:
                search_engine = TextSearchEngine(parsed_data[topic])
            except:
                search_engine = TextSearchEngine(parsed_data["Другое"])

            closest_matching_text = search_engine.get_closest_matching_text(message.text)
            response = llm_model.get_answer(message.text,str(closest_matching_text))
            logging.info("*******************************************\n БАЗА знаний\t")
            for x in closest_matching_text:
                logging.info(x)
            logging.info("*******************************************")
            second_time = current_time()
            # Парсим строки времени в объекты datetime.time
            first_time_obj = datetime.strptime(first_time, "%H:%M:%S").time()
            second_time_obj = datetime.strptime(second_time, "%H:%M:%S").time()

            # Вычисляем разницу во времени
            time_difference = timedelta(hours=second_time_obj.hour - first_time_obj.hour,
                                        minutes=second_time_obj.minute - first_time_obj.minute,
                                        seconds=second_time_obj.second - first_time_obj.second)
            
            formatted_time_difference = datetime(1, 1, 1) + time_difference
            
            logging.info(second_time + "\tОТВЕТ\t" + response + "\nВремя ответа:\t" + formatted_time_difference.strftime("%H:%M:%S") + "\n=============================================================================\n")
        except Exception as e:
            logging.error("Ошибка: " + str(e))
            response = "Ой, вышла ошибка. Я не могу сейчас дать ответ на этот вопрос. Можете попробовть спросить еще раз или уточнить какую-либо другую информацию. Буду рад помочь!"
        bot.send_message(message.from_user.id, response, parse_mode='Markdown')

# Начать прослушивание входящих сообщений
bot.polling(none_stop=True, interval=0)

