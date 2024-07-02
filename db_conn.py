import psycopg2

host = "localhost"
user = "rejoller"
port = 5432
database = "mchs_tg"
password = "9205"


connection = psycopg2.connect(
        host=host,
        user=user,
        port=port,
        database=database,
        password=password
    )