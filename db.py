import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="cs480Project",
        user="postgres",
        password=os.getenv("DB_PASSWORD")
    )

#user can register as a manager by providing name, SSN, and email.
def managerRegister(name, ssn, email):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO managers (ssn, full_name, email) VALUES (%s, %s, %s)""", (ssn, name, email))
    connection.commit()
    cursor.close()
    connection.close()
    print("Manager is registered!!!")

#manager can log in using their SSN
def managerLogin(ssn):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT full_name
        FROM managers
        WHERE ssn = %s
        """, (ssn,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        print(result[0], "you are successfully registered!")
    else:
        print("Error. No manager exists with this SSN")
