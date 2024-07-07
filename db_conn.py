import psycopg

host = "localhost"
user = "rejoller"
port = 5432
database = "mchs_tg"
password = "9205"

connection = None

async def create_connection():
    await psycopg.AsyncConnection.connect(
        host=host,
        user=user,
        port=port,
        dbname=database,  
        password=password
    )
    return connection