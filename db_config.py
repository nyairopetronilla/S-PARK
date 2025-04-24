# db_config.py

def get_db_connection():
    import pymysql
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",  # Update if needed
        db="trial",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
