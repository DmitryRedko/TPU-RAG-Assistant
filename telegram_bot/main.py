import telebot
from telebot import types
from config import BOT_TOKEN
from tpu_model import DialogAssistant
from tpu_find_topic import TopicAssistant
from tpu_parser import LinkParser
from tpu_info_base import TextSearchEngine
import logging
import random
from datetime import datetime, timedelta


import difflib

def parse_teachers(file_path):
    teachers = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data = line.strip().split('\t')
            
            if data[0] != "Сотрудники":
                full_name = data[0]
                last_name = data[0].split(' ')[0]
                # Добавление данных в словарь
                teachers[full_name] = {'full_name': full_name,'name': last_name, 'info': line.replace('\t', '\n')}
            
    return teachers

# Загрузка данных о преподавателях
teachers = parse_teachers("./data/staff.txt")

# Функция для поиска преподавателя по ФИО с возможностью коррекции ошибок
def find_teacher(input_name):
    # Приведение входного имени к нижнему регистру для сравнения
    input_name_lower = input_name.lower()
    
    # Инициализация списка возможных совпадений
    possible_matches = difflib.get_close_matches(input_name_lower, teachers.keys(), n=1, cutoff=0.6)
    
    # Проверка наличия совпадений
    if possible_matches:
        best_match_name = possible_matches[0]
        # Возвращаем данные о преподавателе
        return teachers[best_match_name]
    else:
        # Если нет совпадений, попробуем искать только по фамилии
        # Разбиваем входное имя на компоненты
        name_parts = input_name.split()
        # Берем только последнюю часть (фамилию)
        last_name = name_parts[-1].lower()
        # Ищем наиболее подходящую фамилию из словаря
        possible_last_names = difflib.get_close_matches(last_name, [name.split()[1].lower() for name in teachers.keys()], n=1, cutoff=0.4)
        if possible_last_names:
            # Если нашли подходящую фамилию, ищем преподавателя по ней
            best_match_name = possible_last_names[0]
            return teachers[best_match_name]
        else:
            # Если и по фамилии нет совпадений, возвращаем None
            return None

# Настройка логгирования
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(message)s')

# Функция для форматирования времени
def current_time():
    return datetime.now().strftime("%H:%M:%S")

print("Инициализация парсера")
parser = LinkParser('links.txt','./data')
print("Инициализация парсера завершилась")
print("Запуск парсера")
topic_list, parsed_data = parser.parse_all_pages()
print("Парсер отработал, тематики")
print(topic_list)
print("Инициализация модели")
llm_model = DialogAssistant()
print("Инициализация модели завершилась")
print("Инициализация топик-модели")
topic_bot = TopicAssistant(topic_list)
print("Инициализация топик-модели завершилась")
teacher_by_fio_flag =  0

pattern_sentences = [
    "Дайте мне минутку на размышление!",
    "Позвольте мне минутку подумать!",
    "Дам себе минутку, чтобы все обдумать!",
    "Я возьму минутку, чтобы обдумать это!",
    "Я сделаю перерыв на минутку, чтобы обдумать!",
    "Позвольте мне немного подумать!",
    "Подождите минутку, я все обдумаю!",
    "У меня есть пара минут на размышление!",
    "Дайте мне секундочку, чтобы все взвесить!",
    "Я задумаюсь над этим на минутку!"
]

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Начать")
    btn2 = types.KeyboardButton("🔍 Поиск преподавателя по ФИО")
    # btn3 = types.KeyboardButton("🔍 Быстрый поиск преподавателя по ФИО")
    markup.add(btn1)
    markup.add(btn2)
    # markup.add(btn3)
    bot.send_message(message.from_user.id, "👋 Привет! Я - Политехник! Я был создан студентами группы 0В02 Томского Политехнического Университета. Моя основная задача - помогать студентам университета в решении различных вопросов и проблем. Я могу предоставить информацию о направлениях обучения, стипендиях, практических возможностях, спортивных и культурных мероприятиях, а также о других аспектах студенческой жизни в ТПУ.", reply_markup=markup)

def echo_all_about_user(message):
    user_info = "Unknown user\n"
    try:
        user = message.from_user
        user_info = f"ID: {user.id} "
        user_info += f"Имя: {user.first_name} "
        user_info += f"Фамилия: {user.last_name} "
        user_info += f"Логин: @{user.username} " if user.username else "Логин: Не установлен "
        user_info += f"Язык: {user.language_code}\n"
    except:
        pass
    return user_info

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global teacher_by_fio_flag
    if message.text == '👋 Начать':
        bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', parse_mode='Markdown')
        teacher_by_fio_flag = 0
    elif message.text == '🔍 Поиск преподавателя по ФИО':
        bot.send_message(message.from_user.id, '❓ Введите ФИО преподавателя', parse_mode='Markdown')
        teacher_by_fio_flag = 1
    # elif message.text == '🔍 Быстрый поиск преподавателя по ФИО':
    #     bot.send_message(message.from_user.id, '❓ Введите ФИО преподавателя', parse_mode='Markdown')
    #     teacher_by_fio_flag = 2
    elif teacher_by_fio_flag == 1:
        first_time = current_time()
        request_time = datetime.now()
        formatted_request_time = request_time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info("\n=============================================================================\n" + formatted_request_time + "\n" + echo_all_about_user(message) +"ВОПРОС:\t" + message.text)
        bot.send_message(message.from_user.id, '🔍 Уже ищу!', parse_mode='Markdown')
        try:
            teacher_info = find_teacher(message.text)
        except:
            teacher_info = None
            
        if teacher_info:
            logging.info("*******************************************\n БАЗА знаний\t")
            logging.info(teacher_info['info'])
            logging.info("*******************************************")
            response = llm_model.get_answer(message.text,teacher_info['info'])
        else:
            response ="Извините, преподаватель не найден. Возможно, вы допустили ошибку в ФИО или у меня нет актуальной информации по данному преподавателю."
        second_time = current_time()
        first_time_obj = datetime.strptime(first_time, "%H:%M:%S").time()
        second_time_obj = datetime.strptime(second_time, "%H:%M:%S").time()
        time_difference = timedelta(hours=second_time_obj.hour - first_time_obj.hour,
                                    minutes=second_time_obj.minute - first_time_obj.minute,
                                    seconds=second_time_obj.second - first_time_obj.second)
        formatted_time_difference = datetime(1, 1, 1) + time_difference
        
        bot.send_message(message.from_user.id, response, parse_mode='Markdown')
        
        
        logging.info(second_time + "\tОТВЕТ\t" + response + "\nВремя ответа:\t" + formatted_time_difference.strftime("%H:%M:%S") + "\n=============================================================================\n")
        teacher_by_fio_flag = 0
    # elif teacher_by_fio_flag == 2:
    #     first_time = current_time()
    #     request_time = datetime.now()
    #     formatted_request_time = request_time.strftime("%Y-%m-%d %H:%M:%S")
    #     logging.info("\n=============================================================================\n" + formatted_request_time + "\n" + echo_all_about_user(message) +"ВОПРОС:\t" + message.text)
    #     bot.send_message(message.from_user.id, '🔍 Уже ищу!', parse_mode='Markdown')
    #     try:
    #         teacher_info = find_teacher(message.text)
    #     except:
    #         teacher_info = None
            
    #     if teacher_info:
    #         bot.send_message(message.from_user.id, teacher_info['info'], parse_mode='Markdown')
    #     else:
    #         bot.send_message(message.from_user.id,  "Извините, преподаватель не найден. Возможно, вы допустили ошибку в ФИО или у меня нет актуальной информации по данному преподавателю.", parse_mode='Markdown')
    #     second_time = current_time()
    #     first_time_obj = datetime.strptime(first_time, "%H:%M:%S").time()
    #     second_time_obj = datetime.strptime(second_time, "%H:%M:%S").time()
    #     time_difference = timedelta(hours=second_time_obj.hour - first_time_obj.hour,
    #                                 minutes=second_time_obj.minute - first_time_obj.minute,
    #                                 seconds=second_time_obj.second - first_time_obj.second)
    #     formatted_time_difference = datetime(1, 1, 1) + time_difference
    #     logging.info(second_time + "\tОТВЕТ\t" + str(teacher_info) + "\nВремя ответа:\t" + formatted_time_difference.strftime("%H:%M:%S") + "\n=============================================================================\n")
    #     teacher_by_fio_flag = 0
    elif len(message.text) > 0:
        teacher_by_fio_flag = 0
        bot.send_message(message.from_user.id, random.choice(pattern_sentences), parse_mode='Markdown')
        try:
            first_time = current_time()
            request_time = datetime.now()
            formatted_request_time = request_time.strftime("%Y-%m-%d %H:%M:%S")
            logging.info("\n=============================================================================\n" + formatted_request_time + "\n" + echo_all_about_user(message) +"ВОПРОС:\t" + message.text)
            topic = topic_bot.get_topic(message.text).strip().replace("'", '').replace('Ответ: ', '').replace('"', '').replace("[",'').replace("]",'').replace("(",'').replace(")",'')
            logging.info("ТОПИК:\t" + topic)
            teacher = None
            try:
                if("ФИО:".lower() in topic.lower()):
                    teacher = find_teacher(topic.lower().replace('фио:',''))['info']
                search_engine = TextSearchEngine(parsed_data[topic])
            except:
                search_engine = TextSearchEngine(parsed_data["Другое"])
            if(teacher is None):
                closest_matching_text = search_engine.get_closest_matching_text(message.text)
            else:
                closest_matching_text = teacher 
            response = llm_model.get_answer(message.text,str(closest_matching_text))

            logging.info("*******************************************\n БАЗА знаний\t")
            if(teacher is None):
                for x in closest_matching_text:
                    logging.info(x)
            else:
                logging.info(closest_matching_text)
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

