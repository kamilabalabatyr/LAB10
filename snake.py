import psycopg2
import pygame
import random
import time
from psycopg2 import Error

#Настройки игры 
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
FPS = 10

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змейка с БД")
clock = pygame.time.Clock()

#Подключение к PostgreSQL
def connect():
    try:
        return psycopg2.connect(
            user="kamilabalabatyr",
            password="Kamila97",
            host="localhost",
            port="5432",
            database="postgres"
        )
    except Error as e:
        print("Ошибка подключения к БД:", e)
        exit()

#Cоздание таблиц
def init():
    conn = connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS user_scores CASCADE")
        cursor.execute("DROP TABLE IF EXISTS users CASCADE")
        conn.commit()
        
        # Создаем таблицу users
        cursor.execute('''
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        )
        ''')
        
        # Создаем таблицу user_scores
        cursor.execute('''
        CREATE TABLE user_scores (
            score_id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            level INTEGER NOT NULL,
            score INTEGER NOT NULL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        print("Таблицы успешно созданы!")
    except Error as e:
        print("Ошибка при инициализации БД:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

#Работа с пользователем
def get_or_create_user(username):
    conn = connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            print(f"Добро пожаловать, {username}!")
        else:
            # Создаем нового пользователя
            cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id", (username,))
            user_id = cursor.fetchone()[0]
            print(f"Новый пользователь {username} создан!")
        
        conn.commit()
        return user_id
    except Error as e:
        print("Ошибка при работе с пользователем:", e)
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

#Сохранение результата
def save_score(user_id, level, score):
    conn = connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO user_scores (user_id, level, score) VALUES (%s, %s, %s)",
            (user_id, level, score)
        )
        conn.commit()
        print("Результат сохранен!")
    except Error as e:
        print("Ошибка при сохранении результата:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

#Получение лучшего результата
def get_high_score(user_id):
    conn = connect()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT level, score FROM user_scores 
        WHERE user_id = %s 
        ORDER BY score DESC LIMIT 1
        ''', (user_id,))
        return cursor.fetchone()
    except Error as e:
        print("Ошибка при получении рекорда:", e)
        return None
    finally:
        cursor.close()
        conn.close()

#cама игра
def game(user_id):
    snake = [(WIDTH//2, HEIGHT//2)]
    direction = (GRID_SIZE, 0)
    food = (random.randrange(0, WIDTH, GRID_SIZE), 
            random.randrange(0, HEIGHT, GRID_SIZE))
    score = 0
    level = 1
    running = True
    paused = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p: 
                    paused = not paused
                    if paused:
                        save_score(user_id, level, score)
                if not paused:
                    if event.key == pygame.K_UP and direction != (0, GRID_SIZE):
                        direction = (0, -GRID_SIZE)
                    elif event.key == pygame.K_DOWN and direction != (0, -GRID_SIZE):
                        direction = (0, GRID_SIZE)
                    elif event.key == pygame.K_LEFT and direction != (GRID_SIZE, 0):
                        direction = (-GRID_SIZE, 0)
                    elif event.key == pygame.K_RIGHT and direction != (-GRID_SIZE, 0):
                        direction = (GRID_SIZE, 0)
        
        if paused:
            continue
            
        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        
        if (new_head in snake or 
            new_head[0] < 0 or new_head[0] >= WIDTH or 
            new_head[1] < 0 or new_head[1] >= HEIGHT):
            print("Игра окончена! Счет:", score)
            save_score(user_id, level, score)
            break
        
        snake.insert(0, new_head)
        
        if snake[0] == food:
            score += 10
            if score % 50 == 0:  
                level += 1
                print(f"Уровень {level}!")
            food = (random.randrange(0, WIDTH, GRID_SIZE), 
                   random.randrange(0, HEIGHT, GRID_SIZE))
        else:
            snake.pop()
        
        screen.fill(BLACK)
        for segment in snake:
            pygame.draw.rect(screen, GREEN, (segment[0], segment[1], GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, RED, (food[0], food[1], GRID_SIZE, GRID_SIZE))
        
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Счет: {score} | Уровень: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
        clock.tick(FPS + level*2) 

def main():
    init()
    
    print("\nЗМЕЙКА")
    username = input("Введите ваш ник: ")
    user_id = get_or_create_user(username)
    
    if user_id:
        high_score = get_high_score(user_id)
        if high_score:
            print(f"Ваш рекорд: Уровень {high_score[0]}, Очки: {high_score[1]}")
        else:
            print("У вас еще нет рекордов!")
        
        input("Нажмите Enter для начала игры")
        game(user_id)
    
    pygame.quit()

if __name__ == "__main__":
    main()