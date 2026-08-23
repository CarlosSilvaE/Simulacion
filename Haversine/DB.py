import mysql.connector

def conectar_edificios():
    conn_ed = mysql.connector.connect(
        host="localhost",
        user="root",
        password="KillGarrah12",
        database="edificios_escolares"
    )

    return conn_ed