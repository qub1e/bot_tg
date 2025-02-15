from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

# ID папки в Google Drive
FOLDER_ID = "1mx27Ti_bBmq5R6Q6o62Bs1yJ6Yq0RPNX"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if os.getenv("GOOGLE_SHEETS_CREDENTIALS"):
    creds_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
else:
    # Локально используем файл
    creds = ServiceAccountCredentials.from_json_keyfile_name("valiant-metric-385117-91f6496009ee.json", scope)

client = gspread.authorize(creds)
sheet = client.open("telegram-bot").sheet1

def list_files_in_drive():
    """Возвращает список аудиофайлов в папке Google Drive"""
    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='audio/mpeg'",
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])

def download_file_from_drive(file_id, file_name):
    """Скачивает аудиофайл из Google Drive"""
    request = drive_service.files().get_media(fileId=file_id)
    file_path = f"./downloads/{file_name}"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Загрузка {file_name}: {int(status.progress() * 100)}%")

    return file_path

questions = [
    {"question": {"en": "What is your gender?", "ru": "Какой у вас пол?"},
     "type": "closed",
     "options": {"en": ["Male", "Female", "Prefer not to say"],
                 "ru": ["Мужской", "Женский", "Предпочитаю не указывать"]}},

    {"question": {"en": "What is your age group?", "ru": "В какой возрастной группе вы находитесь?"},
     "type": "closed",
     "options": {"en": ["<18", "18-24", "25-34", "35-44", "45-54", "55+"],
                 "ru": ["<18", "18-24", "25-34", "35-44", "45-54", "55+"]}},

    {"question": {"en": "What is your highest level of education?", "ru": "Какой у вас самый высокий уровень образования?"},
     "type": "closed",
     "options": {"en": ["No formal education", "Primary", "Secondary", "Bachelor's", "Master's", "Doctorate"],
                 "ru": ["Нет формального образования", "Начальное", "Среднее", "Бакалавр", "Магистр", "Докторантура"]}},

    {"question": {"en": "Which region do you live in?", "ru": "В каком регионе вы проживаете?"},
     "type": "closed",
     "options": {"en": ["North America", "Europe", "Asia", "South America", "Africa", "Australia/Oceania"],
                 "ru": ["Северная Америка", "Европа", "Азия", "Южная Америка", "Африка", "Австралия/Океания"]}},

    {"question": {"en": "Do you live in an urban or rural area?", "ru": "Вы живете в городе или сельской местности?"},
     "type": "closed",
     "options": {"en": ["Urban", "Rural"],
                 "ru": ["Город", "Сельская местность"]}},

    {"question": {"en": "What is your employment status?", "ru": "Каков ваш статус занятости?"},
     "type": "closed",
     "options": {"en": ["Employed", "Unemployed", "Student", "Retired"],
                 "ru": ["Работаю", "Безработный", "Студент", "На пенсии"]}},

    {"question": {"en": "What is your monthly income?", "ru": "Какой у вас ежемесячный доход?"},
     "type": "closed",
     "options": {"en": ["< $500", "$500-$1000", "$1000-$3000", "$3000+", "Prefer not to say"],
                 "ru": ["< $500", "$500-$1000", "$1000-$3000", "$3000+", "Предпочитаю не указывать"]}},

    {"question": {"en": "Do you enjoy music with strong bass frequencies?", "ru": "Вам нравится музыка с мощными басами?"},
     "type": "closed",
     "options": {"en": ["Yes", "No", "Neutral"],
                 "ru": ["Да", "Нет", "Нейтрально"]}},

    {"question": {"en": "Do you prefer vocals or instrumental music?", "ru": "Вы предпочитаете вокальную или инструментальную музыку?"},
     "type": "closed",
     "options": {"en": ["Vocals", "Instrumental", "Both"],
                 "ru": ["Вокал", "Инструментальная", "Обе"]}},

    {"question": {"en": "What time of day do you usually listen to music?", "ru": "В какое время суток вы обычно слушаете музыку?"},
     "type": "closed",
     "options": {"en": ["Morning", "Afternoon", "Evening", "Night"],
                 "ru": ["Утро", "День", "Вечер", "Ночь"]}},

    {"question": {"en": "How does music usually affect your emotions?", "ru": "Как музыка обычно влияет на ваши эмоции?"},
     "type": "closed",
     "options": {"en": ["Lifts my mood", "Helps me relax", "Makes me feel energetic", "Makes me nostalgic", "Helps me focus", "Other"],
                 "ru": ["Поднимает настроение", "Помогает расслабиться", "Заряжает энергией", "Вызывает ностальгию", "Помогает сосредоточиться", "Другое"]}},

    {"question": {"en": "What factors make a music recommendation good for you?", "ru": "Какие факторы делают музыкальную рекомендацию хорошей для вас?"},
     "type": "closed",
     "options": {"en": ["Matching mood", "Discovering new genres", "Fitting current activities", "Introducing unique sounds", "Ease of access", "Other"],
                 "ru": ["Совпадение с настроением", "Открытие новых жанров", "Соответствие текущей деятельности", "Уникальное звучание", "Легкость доступа", "Другое"]}},

    {"question": {"en": "Do you usually listen to music alone or with others?", "ru": "Вы обычно слушаете музыку в одиночку или с другими?"},
     "type": "closed",
     "options": {"en": ["Alone", "With others", "Both equally"],
                 "ru": ["В одиночку", "С другими", "Одинаково"]}},

    {"question": {"en": "Do you change your music preferences based on your mood?", "ru": "Меняете ли вы свои музыкальные предпочтения в зависимости от настроения?"},
     "type": "closed",
     "options": {"en": ["Yes", "No", "Sometimes"],
                 "ru": ["Да", "Нет", "Иногда"]}},

    {"question": {"en": "How do you usually listen to music: for nostalgia or creating new experiences?", "ru": "Как вы обычно слушаете музыку: ради ностальгии или для создания новых впечатлений?"},
     "type": "closed",
     "options": {"en": ["Nostalgia", "New experiences", "Both"],
                 "ru": ["Ностальгия", "Новые впечатления", "Оба варианта"]}},

    {"question": {"en": "What is your primary reason for listening to music?", "ru": "Какова ваша основная причина для прослушивания музыки?"},
     "type": "closed",
     "options": {"en": ["Entertainment", "Relaxation", "Focus", "Emotional connection", "Background noise"],
                 "ru": ["Развлечение", "Расслабление", "Концентрация", "Эмоциональная связь", "Фоновый шум"]}},

    {"question": {"en": "What is the most important factor in your music preference?",
                  "ru": "Какой фактор наиболее важен для ваших музыкальных предпочтений?"},
     "type": "closed",
     "options": {"en": ["Genre", "Mood", "Lyrics", "Beats", "Other"],
                 "ru": ["Жанр", "Настроение", "Тексты", "Биты", "Другое"]}},

    {"question": {"en": "Which platform do you primarily use to listen to music?",
                  "ru": "Какую платформу вы в основном используете для прослушивания музыки?"},
     "type": "closed",
     "options": {"en": ["Spotify", "Apple Music", "YouTube", "Yandex Music", "Other"],
                 "ru": ["Spotify", "Apple Music", "YouTube", "Яндекс Музыка", "Другое"]}},

    {"question": {"en": "What device do you use most often for listening to music?",
                  "ru": "Какое устройство вы чаще всего используете для прослушивания музыки?"},
     "type": "closed",
     "options": {"en": ["Phone", "Laptop", "Smart Speakers", "Earphones", "Other"],
                 "ru": ["Телефон", "Ноутбук", "Умные колонки", "Наушники", "Другое"]}},

    {"question": {"en": "What is your top favorite music genre?", "ru": "Какой ваш любимый музыкальный жанр?"},
     "type": "closed",
     "options": {
         "en": ["Pop", "Rock", "Jazz", "Hip-Hop", "Classical", "EDM", "Country", "Reggae", "Blues", "Metal", "Folk",
                "Other"],
         "ru": ["Поп", "Рок", "Джаз", "Хип-хоп", "Классика", "Электронная музыка", "Кантри", "Регги", "Блюз", "Метал",
                "Фолк", "Другое"]}},

    {"question": {
        "en": "Do you prefer music with high energy (fast, upbeat), low energy (slow, calming), or mid-range?",
        "ru": "Вы предпочитаете музыку с высокой энергией (быструю, бодрящую), низкой энергией (медленную, успокаивающую) или среднюю?"},
     "type": "closed",
     "options": {"en": ["High energy", "Low energy", "Mid-range"],
                 "ru": ["Высокая энергия", "Низкая энергия", "Средняя"]}}
]

big_five_questions = [
    {"en": "Am the life of the party.", "ru": "Я душа компании."},
    {"en": "Feel little concern for others.", "ru": "Меня мало волнуют проблемы других."},
    {"en": "Am always prepared.", "ru": "Я всегда подготовлен."},
    {"en": "Get stressed out easily.", "ru": "Я легко поддаюсь стрессу."},
    {"en": "Have a rich vocabulary.", "ru": "У меня богатый словарный запас."},
    {"en": "Don't talk a lot.", "ru": "Я мало говорю."},
    {"en": "Am interested in people.", "ru": "Мне интересны люди."},
    {"en": "Leave my belongings around.", "ru": "Я разбрасываю свои вещи."},
    {"en": "Am relaxed most of the time.", "ru": "Я расслаблен большую часть времени."},
    {"en": "Have difficulty understanding abstract ideas.", "ru": "Мне сложно понимать абстрактные идеи."},
    {"en": "Feel comfortable around people.", "ru": "Я чувствую себя комфортно среди людей."},
    {"en": "Insult people.", "ru": "Я оскорбляю людей."},
    {"en": "Pay attention to details.", "ru": "Я обращаю внимание на детали."},
    {"en": "Worry about things.", "ru": "Я часто беспокоюсь."},
    {"en": "Have a vivid imagination.", "ru": "У меня богатое воображение."},
    {"en": "Keep in the background.", "ru": "Я предпочитаю оставаться в тени."},
    {"en": "Sympathize with others' feelings.", "ru": "Я сопереживаю чувствам других."},
    {"en": "Make a mess of things.", "ru": "Я часто создаю беспорядок."},
    {"en": "Seldom feel blue.", "ru": "Я редко чувствую себя подавленным."},
    {"en": "Am not interested in abstract ideas.", "ru": "Мне неинтересны абстрактные идеи."},
    {"en": "Start conversations.", "ru": "Я легко начинаю разговоры."},
    {"en": "Am not interested in other people's problems.", "ru": "Меня не интересуют проблемы других людей."},
    {"en": "Get chores done right away.", "ru": "Я выполняю дела сразу же."},
    {"en": "Am easily disturbed.", "ru": "Меня легко вывести из равновесия."},
    {"en": "Have excellent ideas.", "ru": "У меня отличные идеи."},
    {"en": "Have little to say.", "ru": "Мне мало что есть сказать."},
    {"en": "Have a soft heart.", "ru": "Я добросердечный человек."},
    {"en": "Often forget to put things back in their proper place.", "ru": "Я часто забываю класть вещи на место."},
    {"en": "Get upset easily.", "ru": "Я легко расстраиваюсь."},
    {"en": "Do not have a good imagination.", "ru": "У меня слабое воображение."},
    {"en": "Talk to a lot of different people at parties.", "ru": "Я разговариваю со многими разными людьми на вечеринках."},
    {"en": "Am not really interested in others.", "ru": "Мне не очень интересны другие люди."},
    {"en": "Like order.", "ru": "Я люблю порядок."},
    {"en": "Change my mood a lot.", "ru": "У меня часто меняется настроение."},
    {"en": "Am quick to understand things.", "ru": "Я быстро схватываю суть вещей."},
    {"en": "Don't like to draw attention to myself.", "ru": "Я не люблю привлекать к себе внимание."},
    {"en": "Take time out for others.", "ru": "Я уделяю время другим людям."},
    {"en": "Shirk my duties.", "ru": "Я избегаю своих обязанностей."},
    {"en": "Have frequent mood swings.", "ru": "У меня часто меняется настроение."},
    {"en": "Use difficult words.", "ru": "Я использую сложные слова."},
    {"en": "Don't mind being the center of attention.", "ru": "Мне нравится быть в центре внимания."},
    {"en": "Feel others' emotions.", "ru": "Я чувствую эмоции других людей."},
    {"en": "Follow a schedule.", "ru": "Я придерживаюсь расписания."},
    {"en": "Get irritated easily.", "ru": "Я легко раздражаюсь."},
    {"en": "Spend time reflecting on things.", "ru": "Я часто размышляю о вещах."},
    {"en": "Am quiet around strangers.", "ru": "Я молчалив в обществе незнакомцев."},
    {"en": "Make people feel at ease.", "ru": "Я создаю комфортную атмосферу для людей."},
    {"en": "Am exacting in my work.", "ru": "Я требователен к своей работе."},
    {"en": "Often feel blue.", "ru": "Я часто чувствую себя подавленным."},
    {"en": "Am full of ideas.", "ru": "У меня много идей."}
]

def list_files_in_drive():
    """Возвращает список аудиофайлов в папке Google Drive"""
    results = drive_service.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType='audio/mpeg'",
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])

def download_file_from_drive(file_id, file_name):
    """Скачивает аудиофайл из Google Drive"""
    file_path = f"./downloads/{file_name}"

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    request = drive_service.files().get_media(fileId=file_id)
    with open(file_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Загрузка {file_name}: {int(status.progress() * 100)}%")

    return file_path

async def send_message(update: Update, text: str, reply_markup=None) -> None:
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "\U0001F3B5 Welcome!\n\n"
        "This bot is designed to study the connection between personality and musical preferences. Survey completion time: ~5-7 minutes.\n\n"
        "Please choose a languane.\n\n"
        "\U0001F3B5 Добро пожаловать!\n\n"
        "Этот бот создан для исследования связи между личностью и музыкальными предпочтениями. Время прохождения: ~5-7 минут.\n\n"
        "Пожалуйста выберите язык."
    )

    keyboard = [
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Русский", callback_data="lang_ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    lang = query.data.split("_")[1]  # Получаем 'en' или 'ru'
    context.user_data["lang"] = lang
    await query.answer()

    if lang == "en":
        explanation = (
            "You will go through several stages:\n\n"
            "1️⃣ Survey – short questions about your musical habits and preferences.\n\n"
            "2️⃣ Big Five Test – a scientifically validated psychological test that evaluates your personality based on five traits:\n\n"
            "   • Extraversion (sociability, energy)\n"
            "   • Agreeableness (friendliness, willingness to help)\n"
            "   • Conscientiousness (organization, self-discipline)\n"
            "   • Neuroticism (tendency to stress)\n"
            "   • Openness to Experience (creativity and love for new ideas)\n\n"
            "Your results will help us understand how personality influences musical preferences. The test does not rate you as “good” or “bad”, but simply shows your inclinations.\n\n"
            "3️⃣ Song Ranking – you will be asked to rank several musical tracks from 1 (liked the most) to 9 (liked the least).\n\n"
            "\U0001F4CC All responses are anonymous and will be used for research purposes only."
        )
    else:
        explanation = (
            "Вам предстоит пройти несколько этапов:\n\n"
            "1️⃣ Анкетирование – короткие вопросы о ваших музыкальных привычках и предпочтениях.\n\n"
            "2️⃣ Тест Big Five – научно обоснованный психологический тест, который оценивает вашу личность по пяти основным чертам:\n\n"
            "   • Экстраверсия (общительность, энергичность)\n"
            "   • Доброжелательность (дружелюбие, готовность помочь)\n"
            "   • Добросовестность (организованность, самодисциплина)\n"
            "   • Нейротизм (склонность к стрессу)\n"
            "   • Открытость к новому опыту (любовь к творчеству и новым идеям)\n\n"
            "Ваши результаты помогут понять, как личность влияет на музыкальные предпочтения. Тест не оценивает вас “хорошим” или “плохим”, а просто показывает ваши склонности.\n\n"
            "3️⃣ Ранжирование песен – вам будет предложено оценить несколько музыкальных композиций по шкале от 1 (понравилась больше всего) до 9 (понравилась меньше всего).\n\n"
            "\U0001F4CC Все ответы остаются анонимными и будут использованы только в исследовательских целях."
        )

    await query.message.reply_text(explanation)
    await next_question(update, context)

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    lang = user_data.get("lang", "en")  # Default to English
    current_index = user_data.get("current_question", 0)

    if current_index >= len(questions):
        await update.effective_message.reply_text(
            "General survey completed! Now let's move on to the Big Five Personality Test. Here are the possible options:\n\n"
            "1 - disagree\n\n"
            "2 - slightly disagree\n\n"
            "3 - neutral,\n\n"
            "4 - slightly agree\n\n"
            "5 - agree"
            if lang == "en" else
            "Опрос завершен! Теперь переходим к тесту личности Большой Пятерки. Вот возможные ответы:\n\n"
            "1 - не согласен\n"
            "2 - частично не согласен\n"
            "3 - нейтрально\n"
            "4 - частично согласен\n"
            "5 - согласен"
        )
        user_data["current_question"] = 0  # Reset index for Big Five questions
        await big_five_test(update, context)  # Start Big Five test
        return

    question_data = questions[current_index]
    question_text = question_data["question"][lang]

    # Store options in user data with indexes
    user_data["current_options"] = {str(i): option for i, option in enumerate(question_data["options"][lang])}

    options = [
        [InlineKeyboardButton(option, callback_data=f"q_{i}")]  # Use index instead of full text
        for i, option in user_data["current_options"].items()
    ]

    reply_markup = InlineKeyboardMarkup(options)
    user_data["current_question"] = current_index + 1
    await update.effective_message.reply_text(question_text, reply_markup=reply_markup)

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_data = context.user_data
    lang = user_data.get("lang", "en")  # Получаем язык пользователя

    # Обработка ответов Big Five
    if query.data.startswith("big5_"):
        _, question_index, score = query.data.split("_")  # Извлекаем данные
        user_data[f"big_five_question_{question_index}"] = int(score)  # Сохраняем ответ

        response_message = (
            f"Thank you for your response: {score}" if lang == "en" else f"Спасибо за ваш ответ: {score}"
        )

        await query.edit_message_text(response_message)
        await big_five_test(update, context)  # Переход к следующему вопросу
        return

    # Обработка ответов общего опроса
    if query.data.startswith("q_"):
        option_index = query.data[2:]  # Извлекаем числовой индекс
        selected_option = user_data["current_options"].get(option_index, "Unknown")
        user_data[f"question_{user_data['current_question'] - 1}"] = selected_option  # Сохраняем ответ

        response_message = (
            f"Thank you for your response: {selected_option}"
            if lang == "en"
            else f"Спасибо за ваш ответ: {selected_option}"
        )

        await query.answer()
        await query.edit_message_text(response_message)
        await next_question(update, context)  # Переход к следующему вопросу
        return

    # Обработка неожиданных данных
    error_message = (
        "Unexpected input. Please try again." if lang == "en" else "Неожиданный ввод. Попробуйте снова."
    )
    await query.answer(error_message)

def calculate_big_five_scores(user_data):
    scores = {
        "Extraversion/Экстраверсия": 20
            + int(user_data.get("big_five_question_0", 0))
            - int(user_data.get("big_five_question_5", 0))
            + int(user_data.get("big_five_question_10", 0))
            - int(user_data.get("big_five_question_15", 0))
            + int(user_data.get("big_five_question_20", 0))
            - int(user_data.get("big_five_question_25", 0))
            + int(user_data.get("big_five_question_30", 0))
            - int(user_data.get("big_five_question_35", 0))
            + int(user_data.get("big_five_question_40", 0))
            - int(user_data.get("big_five_question_45", 0)),
        "Agreeableness/Доброжелательность": 14
            - int(user_data.get("big_five_question_1", 0))
            + int(user_data.get("big_five_question_6", 0))
            - int(user_data.get("big_five_question_11", 0))
            + int(user_data.get("big_five_question_16", 0))
            - int(user_data.get("big_five_question_21", 0))
            + int(user_data.get("big_five_question_26", 0))
            - int(user_data.get("big_five_question_31", 0))
            + int(user_data.get("big_five_question_36", 0))
            + int(user_data.get("big_five_question_41", 0))
            + int(user_data.get("big_five_question_46", 0)),
        "Conscientiousness/Добросовестность": 14
            + int(user_data.get("big_five_question_2", 0))
            - int(user_data.get("big_five_question_7", 0))
            + int(user_data.get("big_five_question_12", 0))
            - int(user_data.get("big_five_question_17", 0))
            + int(user_data.get("big_five_question_22", 0))
            - int(user_data.get("big_five_question_27", 0))
            + int(user_data.get("big_five_question_32", 0))
            - int(user_data.get("big_five_question_37", 0))
            + int(user_data.get("big_five_question_42", 0))
            + int(user_data.get("big_five_question_47", 0)),
        "Neuroticism/Нейротизм": 38
            - int(user_data.get("big_five_question_3", 0))
            + int(user_data.get("big_five_question_8", 0))
            - int(user_data.get("big_five_question_13", 0))
            + int(user_data.get("big_five_question_18", 0))
            - int(user_data.get("big_five_question_23", 0))
            - int(user_data.get("big_five_question_28", 0))
            - int(user_data.get("big_five_question_33", 0))
            - int(user_data.get("big_five_question_38", 0))
            - int(user_data.get("big_five_question_43", 0))
            - int(user_data.get("big_five_question_48", 0)),
        "Openness/Открытость": 8
            + int(user_data.get("big_five_question_4", 0))
            - int(user_data.get("big_five_question_9", 0))
            + int(user_data.get("big_five_question_14", 0))
            - int(user_data.get("big_five_question_19", 0))
            + int(user_data.get("big_five_question_24", 0))
            - int(user_data.get("big_five_question_29", 0))
            + int(user_data.get("big_five_question_34", 0))
            + int(user_data.get("big_five_question_39", 0))
            + int(user_data.get("big_five_question_44", 0))
            + int(user_data.get("big_five_question_49", 0)),
    }

    return scores

async def big_five_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    lang = user_data.get("lang", "en")  # Default to English

    if user_data.get("big_five_in_progress", False):
        return
    user_data["big_five_in_progress"] = True

    current_index = user_data.get("big_five_question", 0)

    if current_index >= len(big_five_questions):
        await update.effective_message.reply_text(
            "Thank you for completing the Big Five Personality Test!" if lang == "en" else "Спасибо за прохождение теста Big Five!"
        )

        scores = calculate_big_five_scores(user_data)
        results_message = "Here are your Big Five Personality Test results:\n\n" if lang == "en" else "Вот ваши результаты теста Big Five:\n\n"
        for trait, score in scores.items():
            results_message += f"{trait}: {score}\n"

        await update.effective_message.reply_text(results_message)

        # Save full survey and Big Five data immediately

        await update.effective_message.reply_text(
            "Now let's move to the song ranking phase." if lang == "en" else "Теперь перейдем к ранжированию песен."
        )
        await send_song_ranking(update, context)  # Proceed to song ranking
        return

    question_text = big_five_questions[current_index][lang]
    user_data["big_five_question"] = current_index + 1

    options = [
        [InlineKeyboardButton("1", callback_data=f"big5_{current_index}_1")],
        [InlineKeyboardButton("2", callback_data=f"big5_{current_index}_2")],
        [InlineKeyboardButton("3", callback_data=f"big5_{current_index}_3")],
        [InlineKeyboardButton("4", callback_data=f"big5_{current_index}_4")],
        [InlineKeyboardButton("5", callback_data=f"big5_{current_index}_5")]
    ]

    reply_markup = InlineKeyboardMarkup(options)
    await update.effective_message.reply_text(question_text, reply_markup=reply_markup)

    user_data["big_five_in_progress"] = False

async def send_song_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    lang = user_data.get("lang", "en")  # Получаем язык пользователя
    current_index = user_data.get("current_song", 0)

    # Получаем список всех песен из Google Drive
    all_songs = list_files_in_drive()

    # Проверяем, все ли песни уже оценены
    if current_index >= len(all_songs):
        final_message = (
            "Thank you for ranking the songs!" if lang == "en" else "Спасибо за ранжирование песен!"
        )
        await update.effective_message.reply_text(final_message)
        user_id = update.effective_user.id
        save_song_ranking(user_id, user_data)
        return

    # Берем текущую песню
    song = all_songs[current_index]
    file_id = song["id"]
    file_name = song["name"]

    # Скачиваем файл
    file_path = download_file_from_drive(file_id, file_name)

    # Отправляем песню в Telegram
    try:
        with open(file_path, "rb") as f:
            await update.effective_message.reply_audio(
                audio=f,
                caption=f"🎵 Now playing: {file_name}" if lang == "en" else f"🎵 Сейчас играет: {file_name}"
            )
    except Exception as e:
        error_message = (
            f"Error sending audio: {e}" if lang == "en" else f"Ошибка отправки аудио: {e}"
        )
        await update.effective_message.reply_text(error_message)
        return

    # Определяем доступные ранги (1-9)
    used_ranks = {user_data.get(f"song_rank_{song['name']}", None) for song in all_songs}
    available_ranks = [i for i in range(1, 10) if i not in used_ranks]

    # Генерируем кнопки для ранжирования
    options = [[InlineKeyboardButton(str(i), callback_data=f"rank_{current_index}_{i}")] for i in available_ranks]
    reply_markup = InlineKeyboardMarkup(options)

    # Сообщение с запросом оценки песни
    message_text = (
        f"Please rank the song '{file_name}' from 1 (most liked) to 9 (least liked):"
        if lang == "en"
        else f"Пожалуйста, оцените песню '{file_name}' по шкале от 1 (понравилась больше всего) до 9 (понравилась меньше всего):"
    )

    await update.effective_message.reply_text(message_text, reply_markup=reply_markup)

def save_song_ranking(user_id, user_data):
    # Получаем актуальный список песен из Google Drive
    all_songs = list_files_in_drive()

    # Заголовки (User ID + названия песен)
    headers = ["User ID"] + [f"Rank for {song['name']}" for song in all_songs]

    # Достаем ранги песен из user_data
    song_ranks = [user_data.get(f"song_rank_{song['name']}", "N/A") for song in all_songs]

    # Итоговая строка данных (User ID + ранги)
    row = [user_id] + song_ranks

    try:
        # Проверяем заголовки в Google Sheets
        sheet_data = sheet.get_all_values()
        if not sheet_data or sheet_data[0] != headers:
            sheet.clear()
            sheet.append_row(headers, value_input_option="USER_ENTERED")

        # Добавляем строку данных
        sheet.append_row(row, value_input_option="USER_ENTERED")
        print(f"✅ Song rankings for user {user_id} successfully saved to Google Sheets.")
    except Exception as e:
        print(f"❌ Error saving song rankings to Google Sheets: {e}")

async def handle_song_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_data = context.user_data

    if not query.data.startswith("rank_"):
        await query.answer("Unexpected input. Please try again.")
        return

    try:
        _, song_index, rank = query.data.split("_")
        song_index, rank = int(song_index), int(rank)
    except ValueError:
        await query.answer("Invalid input. Please try again.")
        return

    # Получаем список всех песен
    all_songs = list_files_in_drive()

    # Проверяем, что индекс песни корректен
    if song_index >= len(all_songs):
        await query.answer("Invalid song selection.")
        return

    song_title = all_songs[song_index]["name"]

    # **СОХРАНЯЕМ РАНГ**
    user_data[f"song_rank_{song_title}"] = rank

    # **Переход к следующей песне**
    user_data["current_song"] = song_index + 1

    await query.answer(f"Ranked '{song_title}' as {rank}.")
    lang = user_data.get("lang", "en")  # Получаем язык пользователя

    rank_message = (
        f"You ranked '{song_title}' as {rank}."
        if lang == "en"
        else f"Вы оценили '{song_title}' как {rank}."
    )

    await query.edit_message_text(rank_message)

    # **🔥 FIXED: СОХРАНЯЕМ ДАННЫЕ ТОЛЬКО ПОСЛЕ ПОСЛЕДНЕЙ ПЕСНИ 🔥**
    if user_data["current_song"] >= len(all_songs):
        user_id = update.effective_user.id
        big_five_scores = calculate_big_five_scores(user_data)
        save_to_google_sheets(user_id, user_data, big_five_scores)
        await update.effective_message.reply_text("✅ Thank you for completing survey, have a good day!\n\n"
                                                  "✅ Спасибо за прохождение теста, всего хорошего!!")

    else:
        await send_song_ranking(update, context)  # Продолжаем ранжирование

def save_to_google_sheets(user_id, user_data, big_five_scores):
    # Заголовки для анкеты
    base_headers = [
        "User ID", "Gender", "Age Group", "Education", "Region", "Urban/Rural",
        "Employment", "Income", "Bass Preference", "Vocals/Instrumental", "Listening Time",
        "Emotion Effect", "Recommendation Factors", "Listening Style", "Mood-based Preference",
        "Nostalgia vs. New Experiences", "Primary Reason", "Important factor", "Platform", "Device", "Genre", "Energy"
    ]

    # Заголовки для Big Five
    big_five_headers = ["Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"]

    # Получаем список песен
    all_songs = list_files_in_drive()
    song_headers = [f"Rank for {song['name']}" for song in all_songs]

    # Полный список заголовков
    full_headers = base_headers + big_five_headers + song_headers

    # **Собираем ответы на вопросы анкеты**
    survey_answers = [user_data.get(f"question_{i}", "N/A") for i in range(len(questions))]

    # **Собираем результаты Big Five**
    big_five_results = [big_five_scores.get(trait, "N/A") for trait in big_five_headers]

    # **Собираем ранги песен**
    song_ranks = [user_data.get(f"song_rank_{song['name']}", "N/A") for song in all_songs]

    # Полная строка данных
    row = [user_id] + survey_answers + big_five_results + song_ranks

    print(f"🔹 Final Save to Google Sheets: {row}")  # Для отладки

    try:
        # Проверяем заголовки в Google Sheets
        sheet_data = sheet.get_all_values()
        if not sheet_data or sheet_data[0] != full_headers:
            sheet.clear()
            sheet.append_row(full_headers, value_input_option="USER_ENTERED")

        # Добавляем строку данных
        sheet.append_row(row, value_input_option="USER_ENTERED")
        print(f"✅ Final data for user {user_id} successfully saved to Google Sheets.")
    except Exception as e:
        print(f"❌ Error saving data to Google Sheets: {e}")

def main():
    app = Application.builder().token("8193853273:AAHV1zxcuPB3YQuzIwr9nJMRrnkVuMx0ww4").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_question))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))

    # IMPORTANT: Register the ranking handler and the general handler so they do not conflict.
    app.add_handler(CallbackQueryHandler(handle_song_ranking, pattern="^rank_\\d+_\\d+$"))
    app.add_handler(CallbackQueryHandler(handle_response, pattern="^(q_|big5_)"))

    app.run_polling()

if __name__ == "__main__":
    main()

