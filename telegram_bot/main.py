
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
            print("ОТВЕТ\t", response,"\n=============================================================================\n")
        except:
            response = "Ой, вышла ошибка. Я не могу сейчас дать ответ на этот вопрос. Можете попробовть спросить еще раз или уточнить какую-либо другую информацию. Буду рад помочь!"
        bot.send_message(message.from_user.id, response, parse_mode='Markdown')



bot.polling(none_stop=True, interval=0) 