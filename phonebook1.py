import psycopg2
import csv
from psycopg2 import Error

def main():
    try:
        # Подключение к базе данных
        connection = psycopg2.connect(
            user="kamilabalabatyr",
            password="Kamila97",
            host="localhost",
            port="5432",
            database="postgres"
        )
        cursor = connection.cursor()

        # 1. Создание таблицы (соответствует существующей структуре)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50),
            phone_number VARCHAR(15) UNIQUE NOT NULL
        );
        ''')
        connection.commit()

        # 2. Функция загрузки из CSV
        def upload_csv():
            file_path = input("Введите путь к CSV файлу: ")
            try:
                with open(file_path, 'r') as file:
                    reader = csv.reader(file)
                    next(reader)  # Пропускаем заголовок
                    for row in reader:
                        cursor.execute(
                            "INSERT INTO phonebook (first_name, phone_number) VALUES (%s, %s) "
                            "ON CONFLICT (phone_number) DO NOTHING",
                            (row[0], row[1]))
                connection.commit(),
                print(f"Данные из {file_path} успешно загружены!")
            except Exception as e:
                print(f"Ошибка при загрузке CSV: {e}")
                connection.rollback()

        # 3. Добавление контакта
        def inp():
            first_name = input("Введите имя: ")
            last_name = input("Введите фамилию (необязательно): ")
            phone_number = input("Введите номер телефона: ")
            try:
                cursor.execute(
                    "INSERT INTO phonebook (first_name, last_name, phone_number) VALUES (%s, %s, %s)",
                    (first_name, last_name if last_name else None, phone_number)
                )
                connection.commit()
                print("Контакт добавлен!")
            except Error as e:
                print("Ошибка при добавлении:", e)
                connection.rollback()

        # 4. Обновление контакта
        def update():
            user_id = input("Введите ID контакта: ")
            new_first_name = input("Новое имя (оставьте пустым, если не меняется): ")
            new_last_name = input("Новая фамилия (оставьте пустым, если не меняется): ")
            new_phone = input("Новый телефон (оставьте пустым, если не меняется): ")
            try:
                if new_first_name:
                    cursor.execute(
                        "UPDATE phonebook SET first_name = %s WHERE id = %s",
                        (new_first_name, user_id))
                if new_last_name:
                    cursor.execute(
                        "UPDATE phonebook SET last_name = %s WHERE id = %s",
                        (new_last_name, user_id))
                if new_phone:
                    cursor.execute(
                        "UPDATE phonebook SET phone_number = %s WHERE id = %s",
                        (new_phone, user_id))
                connection.commit()
                print("Данные обновлены!")
            except Error as e:
                print("Ошибка при обновлении:", e)
                connection.rollback()

        # 5. Поиск контакта
        def query():
            print("\n1. По имени\n2. По фамилии\n3. По телефону")
            choice = input("Ваш выбор: ")
            try:
                if choice == "1":
                    name = input("Введите имя: ")
                    cursor.execute(
                        "SELECT * FROM phonebook WHERE first_name = %s",
                        (name,))
                elif choice == "2":
                    last_name = input("Введите фамилию: ")
                    cursor.execute(
                        "SELECT * FROM phonebook WHERE last_name = %s",
                        (last_name,))
                elif choice == "3":
                    phone = input("Введите телефон: ")
                    cursor.execute(
                        "SELECT * FROM phonebook WHERE phone_number = %s",
                        (phone,))
                else:
                    print("Неверный выбор!")
                    return
                
                results = cursor.fetchall()
                if not results:
                    print("Контакты не найдены")
                else:
                    for row in results:
                        print(f"ID: {row[0]}, Имя: {row[1]}, Фамилия: {row[2]}, Телефон: {row[3]}")
            except Error as e:
                print("Ошибка при поиске:", e)

        # 6. Удаление контакта
        def delete_data():
            print("\n1. По ID\n2. По имени\n3. По фамилии\n4. По телефону")
            choice = input("Ваш выбор: ")
            try:
                if choice == "1":
                    user_id = input("Введите ID: ")
                    cursor.execute(
                        "DELETE FROM phonebook WHERE id = %s",
                        (user_id,))
                elif choice == "2":
                    name = input("Введите имя: ")
                    cursor.execute(
                        "DELETE FROM phonebook WHERE first_name = %s",
                        (name,))
                elif choice == "3":
                    last_name = input("Введите фамилию: ")
                    cursor.execute(
                        "DELETE FROM phonebook WHERE last_name = %s",
                        (last_name,))
                elif choice == "4":
                    phone = input("Введите телефон: ")
                    cursor.execute(
                        "DELETE FROM phonebook WHERE phone_number = %s",
                        (phone,))
                else:
                    print("Неверный выбор!")
                    return
                connection.commit()
                print("Контакт удален!")
            except Error as e:
                print("Ошибка при удалении:", e)
                connection.rollback()

        # Главное меню
        while True:
            print("\n=== ТЕЛЕФОННАЯ КНИГА ===")
            print("1. Добавить контакт (вручную)")
            print("2. Загрузить из CSV")
            print("3. Обновить контакт")
            print("4. Найти контакт")
            print("5. Удалить контакт")
            print("6. Выход")
            
            choice = input("Выберите действие (1-6): ")
            
            if choice == "1":
                inp()
            elif choice == "2":
                upload_csv()
            elif choice == "3":
                update()
            elif choice == "4":
                query()
            elif choice == "5":
                delete_data()
            elif choice == "6":
                break
            else:
                print("Неверный ввод! Попробуйте снова.")

    except Error as e:
        print(f"Ошибка PostgreSQL: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Соединение с БД закрыто")

if __name__ == "__main__":
    main()