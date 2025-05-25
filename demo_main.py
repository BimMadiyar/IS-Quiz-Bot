import telebot
import keyboards as kb
import questions as qs
import libs
import random
import os
from telebot.handler_backends import State, StatesGroup
import importlib

bot = telebot.TeleBot('demo:secret')

subjects = qs.subjects
course = None

user_progress = {}

all_user_ids = libs.get_user_ids()
for userid in all_user_ids:
    user_progress[userid] = {
        "current_subject": "",
        "current_lecture": None,
        "remaining_questions": [],
        "answered_count": 0,
        "correct_answers": 0,
        "current_question_data": None
    }
    # bot.send_message(userid, "The Server is rebooted!\nChoose the Subject again:", reply_markup=kb.create_subject_buttons())


def update_questions():
    global subjects
    importlib.reload(qs)
    subjects = qs.subjects

# Define states for the FSM
class UserStates(StatesGroup):
    DEFAULT_STATE = State()  # Default state
    CHECK_STATE = State()  # Waiting for check upload state
    QUIZ_STATE = State() # Waiting for finishing the quiz


@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    if bot.get_state(chat_id) == "UserStates:QUIZ_STATE":
        bot.delete_message(chat_id, message.message_id)
        bot.send_message(chat_id, "Messages are disabled during the quiz. Use /stop_quiz to exit.", protect_content=True)
        return

    update_questions()
    libs.add_new_user(message.from_user)

    user_progress[chat_id] = {
        "current_subject": "" ,
        "current_lecture": None,
        "remaining_questions": [],
        "answered_count": 0,
        "correct_answers": 0,
        "current_question_data": None
    }
    bot.send_message(chat_id, "Choose the Subject:", reply_markup=kb.create_subject_buttons(), protect_content=True)


@bot.message_handler(commands=['stop_quiz'])
def stop_quiz(message):
    chat_id = message.chat.id
    if bot.get_state(chat_id) != "UserStates:QUIZ_STATE":
        bot.send_message(chat_id, "You have NOT even started the Quiz!", protect_content=True)
    else:
        send_results(message.chat.id)


@bot.message_handler(commands=['iamadmin'])
def iAmAdmin(message):
    if libs.is_admin(message.chat.id):
        markup = kb.admin_markup()
        bot.send_message(message.chat.id, "Now you have an Admin features", reply_markup=markup, protect_content=True)


@bot.message_handler(commands=['allUsers'])
def allUsers(message):
    if libs.is_admin(message.chat.id):
        file_path = libs.create_users_file()
        with open(file_path, 'rb') as file:
            bot.send_document(message.chat.id, file)
        os.remove(file_path)  # Clean up by removing the file after sending


@bot.message_handler(commands=['giveAccess'])
def giveAccess(message):
    if libs.is_admin(message.chat.id):
        bot.send_message(message.chat.id, "1. Select the course to give access:", reply_markup=kb.give_access_markup(), protect_content=True)

def giveUserid(message):
    global course
    userID = message.text.strip()
    if libs.user_exists(userID):
        bot.send_message(message.chat.id, libs.give_access(course, userID), protect_content=True)
        bot.send_message(userID, f"Your payment has been accepted. You now have access to '{course}'!", protect_content=True)
        userID = int(userID)
        if course == "INF207":
            bot.send_message(userID, "The main quiz channel:\nhttps://t.me/+h37xuoP1Hk1jZTcy\n\n[INF 207] channel:\nhttps://t.me/+eGy8B04_XP04OWI6", protect_content=True)
        elif course == "INF202":
            bot.send_message(userID, "The main quiz channel:\nhttps://t.me/+h37xuoP1Hk1jZTcy\n\n[INF 202] channel:\nhttps://t.me/+03ppqqWCe1UyMmYy", protect_content=True)
        elif course == "INF313":
            bot.send_message(userID, "The main quiz channel:\nhttps://t.me/+h37xuoP1Hk1jZTcy\n\n[INF 313] channel:\nhttps://t.me/+Wn-oITkf_WdkZjcy", protect_content=True)
    else:
        bot.send_message(message.chat.id, "This userID never started the bot!", protect_content=True)


@bot.message_handler(commands=['removeAccess'])
def removeAccess(message):
    if libs.is_admin(message.chat.id):
        bot.send_message(message.chat.id, "1. Select the course to remove access:", reply_markup=kb.remove_access_markup(), protect_content=True)

def removeUserid(message):
    global course
    userID = message.text.strip()
    if libs.user_exists(userID):
        bot.send_message(message.chat.id, libs.remove_access(course, userID), protect_content=True)
    else:
        bot.send_message(message.chat.id, "This userID never started the bot!", protect_content=True)


@bot.message_handler(content_types=['document', 'photo'])
def handle_uploaded_file(message):
    # Check if the user is in the "check state"
    current_state = bot.get_state(message.chat.id)
    if current_state == "UserStates:CHECK_STATE":
        if message.content_type == 'document' or message.content_type == 'photo':
            bot.send_message(message.chat.id, f"Wait for the Admin's response...\nCourse: {user_progress[message.chat.id]['current_subject']}\nAccept... / Reject...", protect_content=True)
            if message.content_type == 'document':
                file_id = message.document.file_id
            else:
                file_id = message.photo[-1].file_id

            bot.forward_message(-4711060393,  message.chat.id, message.message_id)
            bot.send_message(-4711060393, f"Check of '{user_progress[message.chat.id]['current_subject']}' from user {message.chat.id} ", reply_markup=kb.accept_reject_markup(message))
            # Reset the user's state to the default state
            bot.set_state(message.chat.id, UserStates.DEFAULT_STATE)
    else:
        bot.send_message(message.chat.id, "I didn't ask you to upload the document or photo", protect_content=True)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    message_id = message.message_id

    if bot.get_state(chat_id) == "UserStates:QUIZ_STATE":
        bot.delete_message(chat_id, message_id)
        bot.send_message(chat_id, "Messages are disabled during the quiz. Use /stop_quiz to exit.", protect_content=True)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    global subjects, course
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    if callback.data.startswith("Subject_"):
        update_questions()
        subject_name = callback.data.split("_", 1)[1]
        current_subjects = {
            "Intro To Business (INF 207)": ("INF207", libs.is_free_inf207),
            "DBMS (INF 202)": ("INF202", libs.is_free_inf202),
            "Cisco (INF 313)": ("INF313", libs.is_free_inf313),
        }

        if subject_name in current_subjects:
            current_subject, is_free_function = current_subjects[subject_name]
            if not is_free_function(chat_id):
                user_progress[chat_id]["current_subject"] = subject_name
                bot.edit_message_text("You DON'T have access to this course. You can buy it below:", chat_id, message_id, reply_markup=kb.buy_course_markup())
                return
            else:
                user_progress[chat_id]["current_subject"] = subject_name
                lectures = subjects[subject_name]
                bot.edit_message_text("Choose the Lecture:", chat_id, message_id, reply_markup=kb.create_lecture_buttons(lectures))

    elif callback.data.startswith("Lecture_"):
        update_questions()
        lectures = subjects[user_progress[chat_id]["current_subject"]]
        lecture_name = callback.data.split("_", 1)[1]
        user_progress[chat_id]["current_lecture"] = lecture_name
        if lecture_name == "Random Final Exam (VIP)":
            questions_pool = []

            # Collect random questions from each lecture
            for lecture in lectures:
                selected_questions = []
                if lecture.startswith("Lecture"):
                    questions = lectures[lecture]
                    selected_questions = random.sample(questions, 2)
                questions_pool.extend(selected_questions)
            lectures[lecture_name] = questions_pool
        elif lecture_name == "❌ Wrong Answered Questions":
            current_course = user_progress[chat_id]["current_subject"].split("(")[1].split(")")[0].replace(" ", "")
            lectures[lecture_name] = libs.get_user_errors(f"errors_{current_course.lower()}.json", chat_id)
        if len(lectures[lecture_name]) == 0:
            bot.edit_message_text(f'The "{lecture_name}" is Empty Now!', chat_id, message_id)
            bot.send_message(chat_id, "Choose the Lecture:", reply_markup=kb.create_lecture_buttons(lectures), protect_content=True)
        else:
            bot.edit_message_text("Choose the Order of Questions:", chat_id, message_id, reply_markup=kb.create_order_buttons())

    elif callback.data == "random_order":
        lectures = subjects[user_progress[chat_id]["current_subject"]]
        user_progress[chat_id]["remaining_questions"] = random.sample(lectures[user_progress[chat_id]["current_lecture"]], len(lectures[user_progress[chat_id]["current_lecture"]]))
        user_progress[chat_id]["answered_count"] = 0
        user_progress[chat_id]["correct_answers"] = 0

        bot.edit_message_text(
            f"You selected {user_progress[chat_id]['current_lecture']}.\n"
            f"*Number of Questions: {len(user_progress[chat_id]['remaining_questions'])}*\n"
            f"Let's start!",
            chat_id,
            message_id,
            parse_mode="Markdown"  # Use Markdown for formatting
        )
        bot.set_state(chat_id, UserStates.QUIZ_STATE)
        send_poll(chat_id)

    elif callback.data == "simple_order":
        lectures = subjects[user_progress[chat_id]["current_subject"]]

        user_progress[chat_id]["remaining_questions"] = lectures[user_progress[chat_id]["current_lecture"]][:]
        user_progress[chat_id]["answered_count"] = 0
        user_progress[chat_id]["correct_answers"] = 0

        bot.edit_message_text(
            f"You selected {user_progress[chat_id]['current_lecture']}.\n"
            f"*Number of Questions: {len(user_progress[chat_id]['remaining_questions'])}*\n"
            f"Let's start!",
            chat_id,
            message_id,
            parse_mode="Markdown"  # Use Markdown for formatting
        )
        bot.set_state(chat_id, UserStates.QUIZ_STATE)
        send_poll(chat_id)

    elif callback.data == "back_to_subjects":
        bot.edit_message_text("Choose the Subject:", chat_id, message_id, reply_markup=kb.create_subject_buttons())

    elif callback.data == "back_to_lectures":
        lectures = subjects[user_progress[chat_id]["current_subject"]]
        bot.edit_message_text("Choose the Lecture:", chat_id, message_id, reply_markup=kb.create_lecture_buttons(lectures))

    elif callback.data.startswith("give_"):
        course = callback.data.split("_")[1]
        bot.edit_message_text("2. Enter the ID of user to give access:", chat_id, message_id)
        bot.register_next_step_handler(callback.message, giveUserid)

    elif callback.data.startswith("remove_"):
        course = callback.data.split("_")[1]
        bot.edit_message_text("2. Enter the ID of user to remove access:", chat_id, message_id)
        bot.register_next_step_handler(callback.message, removeUserid)

    elif callback.data == "buy_course":
        # Set the user's state to "check state"
        bot.set_state(chat_id, UserStates.CHECK_STATE)
        bot.edit_message_text("Send the check (PDF or image) for buying this course.\nKaspi number: 87775738047 Madiyar B.\nPrice: 500 KZT", chat_id, message_id)

    elif callback.data.startswith("accept_") or callback.data.startswith("reject_"):
        action, current_userid = callback.data.split("_", 1)
        current_userid = int(current_userid)
        current_course = user_progress[current_userid]["current_subject"]

        if action == "accept":
            bot.send_message(current_userid, f"Your payment has been accepted. You now have access to '{current_course}'!", protect_content=True)
            bot.edit_message_text(f"User's access to '{current_course}' has been granted ✅", chat_id, message_id)
            current_course = current_course.split("(")[1].split(")")[0].replace(" ", "")
            libs.give_access(current_course, current_userid)  # Grant access in the database
            if current_course == "INF207":
                bot.send_message(current_userid, "The main quiz channel:\nhttps://t.me/+h37xuoP1Hk1jZTcy\n\n[INF 207] channel:\nhttps://t.me/+eGy8B04_XP04OWI6", protect_content=True)
            elif current_course == "INF202":
                bot.send_message(current_userid, "The main quiz channel:\nhttps://t.me/+h37xuoP1Hk1jZTcy\n\n[INF 202] channel:\nhttps://t.me/+03ppqqWCe1UyMmYy", protect_content=True)
            elif current_course == "INF313":
                bot.send_message(current_userid, "The main quiz channel:\nhttps://t.me/+h37xuoP1Hk1jZTcy\n\n[INF 313] channel:\nhttps://t.me/+Wn-oITkf_WdkZjcy", protect_content=True)
        elif action == "reject":
            bot.send_message(current_userid, f"Your payment for '{current_course}' has been rejected. Please contact support.", protect_content=True)
            bot.edit_message_text(f"User's access to '{current_course}' request has been rejected ❌", chat_id, message_id)

    elif callback.data == "subjects":
        bot.edit_message_text("Choose the Subject:", chat_id, message_id, reply_markup=kb.create_subject_buttons())


def send_poll(chat_id):
    progress = user_progress[chat_id]
    remaining_questions = progress["remaining_questions"]

    if remaining_questions:
        question_data = remaining_questions.pop(0)  # Get the next question
        progress["current_question_data"] = question_data  # Store the question in user-specific progress
        progress["answered_count"] += 1

        bot.send_poll(
            chat_id=chat_id,
            question=str(progress["answered_count"]) + ". " + question_data["question"],
            options=question_data["options"],
            type="quiz",
            correct_option_id=question_data["answer_index"],
            is_anonymous=False,
            protect_content=True
        )

        if progress["answered_count"] % 3 == 0:
            bot.send_message(chat_id, "You can use /stop_quiz command, if you want to Stop The Quiz right now.", protect_content=True)
        
    else:
        send_results(chat_id)


@bot.poll_answer_handler(func=lambda answer: True)
def handle_poll_answer(poll_answer):
    user_id = poll_answer.user.id
    progress = user_progress[user_id]
    current_question_data = progress["current_question_data"]  # Retrieve user-specific question data

    current_course = user_progress[user_id]["current_subject"].split("(")[1].split(")")[0].replace(" ", "").lower()

    if poll_answer.option_ids[0] == current_question_data["answer_index"]:
        progress["correct_answers"] += 1

        # Remove the question from the user's wrong answered questions if it exists
        if libs.error_exists(f"errors_{current_course}.json", user_id, current_question_data["question"]):
            libs.delete_error(f"errors_{current_course}.json", user_id, current_question_data["question"])
    else:
        # Add the question to the user's wrong answered questions if it doesn't exist
        if not libs.error_exists(f"errors_{current_course}.json", user_id, current_question_data["question"]):
            libs.add_error(
                f"errors_{current_course}.json",
                user_id,
                current_question_data["question"],
                current_question_data["options"],
                current_question_data["answer_index"]
            )
    send_poll(user_id)


def send_results(chat_id):
    progress = user_progress.get(chat_id, {})
    correct_answers = progress.get("correct_answers", 0)
    total_questions = progress.get("answered_count", 0)

    bot.send_message(chat_id, f"You've completed the quiz! 🎉\n"
                              f"Correct Answers: {correct_answers}/{total_questions}", protect_content=True)
    user_progress[chat_id]["answered_count"] = 0
    user_progress[chat_id]["correct_answers"] = 0

    bot.set_state(chat_id, UserStates.DEFAULT_STATE)
    bot.send_message(chat_id, "Choose the Lecture:", reply_markup=kb.create_lecture_buttons(subjects[user_progress[chat_id]["current_subject"]]), protect_content=True)


print("Bot is running...")
bot.infinity_polling()

