import telebot
import libs
import questions as qs
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


subjects = qs.subjects


def create_lecture_buttons(lectures):
    markup = InlineKeyboardMarkup()
    for lecture in lectures.keys():
        markup.add(InlineKeyboardButton(lecture, callback_data=f"Lecture_{lecture}"))
    markup.add(InlineKeyboardButton("⬅️ Back to Subjects", callback_data="back_to_subjects"))
    return markup


def create_subject_buttons():
    markup = InlineKeyboardMarkup()
    for subject in subjects:
        markup.add(InlineKeyboardButton(subject, callback_data=f"Subject_{subject}"))
    markup.add(InlineKeyboardButton("Support Service", url="https://t.me/@fatherofcs"))
    return markup


def stop_quiz_markup():
    markup = InlineKeyboardMarkup()
    stop_button = InlineKeyboardButton("Stop The Quiz", callback_data="stop_quiz")
    markup.add(stop_button)
    return markup


def create_order_buttons():
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("Simple Order", callback_data="simple_order"), InlineKeyboardButton("Random Order", callback_data="random_order"))
    markup.add(InlineKeyboardButton("⬅️ Back to Lectures", callback_data="back_to_lectures"))
    return markup


def admin_markup():
    markup = telebot.types.ReplyKeyboardMarkup()
    allUsers = telebot.types.KeyboardButton("/allUsers")
    giveAccess = telebot.types.KeyboardButton("/giveAccess")
    removeAccess = telebot.types.KeyboardButton("/removeAccess")
    markup.add(allUsers)
    markup.row(giveAccess, removeAccess)
    return markup


def give_access_markup():
    markup = InlineKeyboardMarkup()
    INF207 = InlineKeyboardButton("INF207", callback_data="give_INF207")
    INF202 = InlineKeyboardButton("INF202", callback_data="give_INF202")
    INF313 = InlineKeyboardButton("INF313", callback_data="give_INF313")
    markup.row(INF207, INF202, INF313)
    return markup

def remove_access_markup():
    markup = InlineKeyboardMarkup()
    INF207 = InlineKeyboardButton("INF207", callback_data="remove_INF207")
    INF202 = InlineKeyboardButton("INF202", callback_data="remove_INF202")
    INF313 = InlineKeyboardButton("INF313", callback_data="remove_INF313")
    markup.row(INF207, INF202, INF313)
    return markup

def buy_course_markup():
    markup = InlineKeyboardMarkup()
    buy_button = InlineKeyboardButton("Buy the course", callback_data="buy_course")
    other_subjects = InlineKeyboardButton("Other Subjects", callback_data="subjects")
    markup.row(buy_button, other_subjects)
    return markup

def accept_reject_markup(message):
    markup = InlineKeyboardMarkup()
    accept_button = InlineKeyboardButton("✅ Accept", callback_data=f"accept_{message.chat.id}")
    reject_button = InlineKeyboardButton("❌ Reject", callback_data=f"reject_{message.chat.id}")
    markup.row(accept_button, reject_button)
    return markup

