import telebot
import mysql.connector
from telebot.types import InputMediaPhoto
import datetime as dt_module  
from datetime import datetime, timedelta
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import urlparse
from bd import *

def buscar_subcategorias(categoria, user_id=None):
    conn, cursor = conectar_banco_dados()
    try:
        if categoria == 'geral':
            cursor.execute('SELECT DISTINCT subcategoria FROM personagens')
        elif user_id is None:
            cursor.execute('SELECT DISTINCT subcategoria FROM personagens WHERE categoria = %s', (categoria,))
        else:
            cursor.execute('SELECT DISTINCT subcategoria FROM personagens WHERE categoria = %s AND user_id != %s',
                           (categoria, user_id))

        subcategorias = [row[0] for row in cursor.fetchall()]
        return subcategorias

    except mysql.connector.Error as err:
        print(f"Erro ao buscar subcategorias: {err}")
        return []

    finally:
        fechar_conexao(cursor, conn)
        
def buscar_cartas_usuario(id_usuario, id_personagem):
    try:
        conn, cursor = conectar_banco_dados()
        query = "SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s"
        cursor.execute(query, (id_usuario, id_personagem))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0

    except mysql.connector.Error as err:
        print(f"Erro ao buscar cartas {id_personagem} do usuário {id_usuario}: {err}")
    finally:
        fechar_conexao(cursor, conn)
        
def obter_link_formatado(link):
    parsed_url = urlparse(link)
    if parsed_url.scheme and parsed_url.netloc:
        return f"<a href='{link}'>🎨 | Créditos da imagem!</a>"
    else:
        return "CR"
    

def procurar_subcategorias_similares(cursor, subcategoria):
    try:
        subnova = subcategoria.split(' ', 1)[1].strip().title()
        sql_consultar_subcategorias = """
            SELECT DISTINCT(subcategoria)
            FROM personagens
            WHERE subcategoria LIKE %s
        """
        cursor.execute(sql_consultar_subcategorias, (f'%{subnova}%',))
        subcategorias_similares = cursor.fetchall()
        return subcategorias_similares[0] if subcategorias_similares else None  # Retorna o primeiro elemento ou None se vazio
    except Exception as e:
        print("Erro ao consultar subcategorias:", e)
        return None
def verificar_cesta_vazia(id_usuario, subcategoria, cursor):
    try:
        sql_verificar_cartas = """
            SELECT COUNT(*)
            FROM inventario i
            JOIN personagens p ON i.id_personagem = p.id_personagem
            WHERE i.id_usuario = %s AND p.subcategoria LIKE %s
        """
        cursor.execute(sql_verificar_cartas, (id_usuario, f'%{subcategoria}%'))
        count_cartas = cursor.fetchone()[0]
        return count_cartas == 0
    except Exception as e:
        print("Erro ao verificar a cesta:", e)
        return True  # Se houver algum erro, considerar cesta vazia
    
def excluir_registros_antigos(cursor, conn, usuario, subcategoria_like):
    try:
        sql_excluir_cartas = """
            DELETE FROM temp_cartas
            WHERE id_usuario = %s AND subcategoria LIKE %s
        """
        cursor.execute(sql_excluir_cartas, (usuario, f'%{subcategoria_like}%'))
        conn.commit()
        print("Registros antigos excluídos com sucesso.")
    except Exception as e:
        print("Erro ao excluir registros antigos:", e)
        conn.rollback()


def quantidade_cartas_usuario(id_usuario, id_personagem):

    try:
        conn, cursor = conectar_banco_dados()

        query_quantidade_cartas = """
            SELECT quantidade
            FROM inventario
            WHERE id_usuario = %s AND id_personagem = %s
        """
        cursor.execute(query_quantidade_cartas, (id_usuario, id_personagem))
        quantidade = cursor.fetchone()

        if quantidade:
            return quantidade[0]
        else:
            return 0  

    except mysql.connector.Error as e:
        print(f"Erro ao obter quantidade de cartas do usuário: {e}")
        return 0  

    finally:
        fechar_conexao(cursor, conn)


        
