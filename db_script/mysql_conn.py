import mysql.connector

def get_mysql_connection():
    return mysql.connector.connect(
        host='crossover.proxy.rlwy.net',
        port=31173,
        user='root',
        password='oewmpnuichBzGMWnGJdjTJYxZfKUBBzS',
        database='railway',
        charset='utf8mb4'
    )
