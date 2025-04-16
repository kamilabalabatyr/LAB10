from pynput import keyboard
import psycopg2
import pygame
import time

def get_conn():
    return psycopg2.connect("dbname=postgres user=kamilabalabatyr password=your_password")

def save_game(user_id, score, level):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET score = %s, level = %s WHERE id = %s", (score, level, user_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_level(level):
    levels = {1: {'speed': 5, 'walls': 3}, 2: {'speed': 7, 'walls': 5}, 3: {'speed': 9, 'walls': 7}}
    return levels.get(level, {'speed': 5, 'walls': 3})

def get_or_create_user(username):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, level FROM Users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user:
        user_id, current_level = user
    else:
        cursor.execute("INSERT INTO Users (username) VALUES (%s) RETURNING id", (username,))
        user_id = cursor.fetchone()[0]
        current_level = 1
    conn.commit()
    cursor.close()
    conn.close()
    return user_id, current_level

def on_press(key):
    try:
        if key.char == 'p':  # Для паузы
            print("Game paused. Saving progress...")
            save_game(user_id, current_score, current_level)
            return False  # Остановить слушатель
    except AttributeError:
        pass

def start_game():
    pygame.init()
    username = input("Enter your username: ")
    user_id, current_level = get_or_create_user(username)
    level_settings = get_level(current_level)
    speed, walls = level_settings['speed'], level_settings['walls']
    
    print(f"Level {current_level}: Speed = {speed}, Walls = {walls}")

    current_score = 0
    max_level = 3
    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # Запуск слушателя

    while True:
        current_score += 10
        if current_score % 100 == 0 and current_level < max_level:
            current_level += 1
            print(f"Level up! Now you are at level {current_level}.")
        time.sleep(1 / speed)

    save_game(user_id, current_score, current_level)
    print(f"Game over. Your final score is {current_score}. Your level is {current_level}.")
    pygame.quit()

start_game()
