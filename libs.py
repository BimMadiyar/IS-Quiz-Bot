import sqlite3
from datetime import datetime
import json


DB_PATH = 'database.db'


def add_new_user(user):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        if not user_exists(user.id):
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute("INSERT INTO users (userid, username, name, date, admin, INF207, INF202, INF313) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user.id, user.username, f"{user.first_name} {user.last_name}", start_time, 0, 0, 0, 0))
            conn.commit()


def get_user_ids():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userid FROM users;")
        return [int(row[0]) for row in cur.fetchall()]


def create_users_file():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT userid, username, name, INF207, INF202, INF313 FROM users")
        all_users = cur.fetchall()

        file_path = "users_list.txt"
        with open(file_path, 'w', encoding="utf-8") as file:
            if not all_users:
                file.write("No users in the table!")
            else:
                for userid, username, name, INF207, INF202, INF313 in all_users:
                    file.write(f"{username} : {name} : {userid}\nINF207 : {INF207}   INF202 : {INF202}   INF313 : {INF313}\n\n")

    return file_path


def give_access(course, userid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        try:
            query = f"UPDATE users SET {course} = 1 WHERE userid = ?"
            cur.execute(query, (userid,))
            conn.commit()
            return f"Username '{userid}' got access to {course} successfully!"
        except sqlite3.Error as e:
            return f"Database error: {e}"


def remove_access(course, userid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        try:
            query = f"UPDATE users SET {course} = 0 WHERE userid = ?"
            cur.execute(query, (userid,))
            conn.commit()
            return f"Currently, username '{userid}' doesn't have access to {course}!"
        except sqlite3.Error as e:
            return f"Database error: {e}"


def user_exists(userid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        result = cur.execute("SELECT 1 FROM users WHERE userid = ? LIMIT 1", (userid,)).fetchone()
        return result is not None


def is_admin(userid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        result = cur.execute("SELECT admin FROM users WHERE userid = ?", (userid,)).fetchone()[0]
        return result == 1


def is_free_inf207(userid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        result = cur.execute("SELECT INF207 FROM users WHERE userid = ?", (userid,)).fetchone()[0]
        return result == 1


def is_free_inf202(userid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        result = cur.execute("SELECT INF202 FROM users WHERE userid = ?", (userid,)).fetchone()[0]
        return result == 1


def is_free_inf313(userid):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        result = cur.execute("SELECT INF313 FROM users WHERE userid = ?", (userid,)).fetchone()[0]
        return result == 1


def get_errors(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist


def add_errors(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def error_exists(file_path, user_id, question):
    data = get_errors(file_path)
    user_data = next((user for user in data if user["user_id"] == user_id), None)
    if user_data:
        return any(q["question"] == question for q in user_data["questions"])
    return False


def add_error(file_path, user_id, question, options, correct_answer):
    data = get_errors(file_path)
    user_data = next((user for user in data if user["user_id"] == user_id), None)
    new_error = {
        "question": question,
        "options": options,
        "answer_index": correct_answer
    }
    if user_data:
        if error_exists(file_path, user_id, question):
            print("Error already exists for this question!")
            return
        user_data["questions"].append(new_error)
    else:
        data.append({"user_id": user_id, "questions": [new_error]})

    add_errors(file_path, data)


def get_user_errors(file_path, user_id):
    data = get_errors(file_path)
    user_data = next((user for user in data if user["user_id"] == user_id), None)
    return user_data["questions"] if user_data else []


def delete_error(file_path, user_id, question):
    data = get_errors(file_path)
    user_data = next((user for user in data if user["user_id"] == user_id), None)

    if user_data:
        original_count = len(user_data["questions"])
        user_data["questions"] = [
            q for q in user_data["questions"] if q["question"] != question
        ]
        if len(user_data["questions"]) < original_count:
            if not user_data["questions"]:
                # Remove the user entry if they have no more errors
                data = [user for user in data if user["user_id"] != user_id]
            add_errors(file_path, data)
            return True
        else:
            print("Error not found for this question.")
    else:
        print(f"No errors found for user {user_id}.")

    return False