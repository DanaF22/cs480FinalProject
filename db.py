import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="cs480",
        user="postgres",
        password="yourpassword" # Each person needs to replace this with their password
    )