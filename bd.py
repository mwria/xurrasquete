import telebot
import mysql.connector
import time
from telebot.types import InputMediaPhoto
import datetime as dt_module  
from datetime import datetime, timedelta
from datetime import date
from telebot import types

bot = telebot.TeleBot("7088149058:AAEnXEEGhCwU6-BlNcTgghAbtK0L-HWB2J4")
def db_config():
    return {
        'host': '127.0.0.1',
        'database': 'garden',
        'user': 'root',
        'password': '#Folkevermore13',
        'ssl_disabled': True

    }
    
def conectar_banco_dados():
    while True:
        try:
            conn = mysql.connector.connect(**db_config())
            cursor = conn.cursor()
            return conn, cursor
        except mysql.connector.Error as e:
            print(f"Erro na conexão com o banco de dados: {e}")
            print("Tentando reconectar em 5 segundos...")
            time.sleep(5)

conn, cursor = conectar_banco_dados()

def fechar_conexao(cursor, conn):
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()   