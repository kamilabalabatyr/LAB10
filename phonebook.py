import psycopg2

conn = psycopg2.connect("dbname=postgres user=kamilabalabatyr password=your_password")
cursor = conn.cursor()

first_name = input("Enter first name: ")
last_name = input("Enter last name: ")
phone = input("Enter phone number: ")

cursor.execute("INSERT INTO PhoneBook (first_name, last_name, phone_number) VALUES (%s, %s, %s)", (first_name, last_name, phone))

conn.commit()
cursor.close()
conn.close()
