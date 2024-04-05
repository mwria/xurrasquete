import telebot
import mysql.connector
import random
import requests
import time
import datetime
from telebot.types import InputMediaPhoto
import datetime as dt_module  
from datetime import datetime, timedelta
import re
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import io
from io import BytesIO
from telebot import types
import functools
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import urlparse
from bd import *

def buscar_subcategorias(categoria, user_id=None):
    try:
        conn, cursor = conectar_banco_dados()

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

def verificar_giros(id_pessoa):
    try:
        conn, cursor = conectar_banco_dados()

        try:
            query = f"SELECT iscas FROM usuarios WHERE id_usuario = {id_pessoa}"
            cursor.execute(query)
            resultado = cursor.fetchone()

            if resultado:
                qtd_iscas = int(resultado[0])
                return qtd_iscas
            else:
                return 0

        except Exception as e:
            print(f"Erro ao executar a consulta de verificação de giros: {e}")

    finally:
        fechar_conexao(cursor, conn)

def verificar_id_na_tabela(id_pessoa, tabela, coluna_iduser):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE {coluna_iduser} = %s", (id_pessoa,))
        resultado_contagem = cursor.fetchone()[0]

        if resultado_contagem > 0:
            raise ValueError(f"ID {id_pessoa} já está na tabela '{tabela}' na coluna '{coluna_iduser}'")

    except mysql.connector.Error as err:
        print(f"Erro ao verificar ID {id_pessoa} na tabela '{tabela}': {err}")

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
        
def obter_username_por_id(user_id):
    try:
        user_info = bot.get_chat(user_id)
        if user_info.username:
            return f"O username do usuário com o ID {user_id} é: @{user_info.username}"
        else:
            return f"O usuário com o ID {user_id} não possui um username público."
    except Exception as e:
        return f"Erro ao obter o username: {e}"
    
def obter_gif_url(id_personagem, id_usuario):
    conn, cursor = conectar_banco_dados()
    try:
        sql_gif = """
            SELECT link
            FROM gif
            WHERE id_personagem = %s AND id_usuario = %s
        """
        values_gif = (id_personagem, id_usuario)
        print(values_gif)
        cursor.execute(sql_gif, values_gif)
        resultado_gif = cursor.fetchall()
        for gif in resultado_gif:
            print(gif)
        return resultado_gif[0][0] if resultado_gif else None
    finally:
        fechar_conexao(cursor, conn)
        
def obter_nome(id_personagem):
    try:
        query_fav_usuario_personagens = f"""
            SELECT p.nome AS nome_personagem
            FROM personagens p
            WHERE p.id_personagem = {id_personagem}
        """
        query_fav_usuario_eventos = f"""
            SELECT e.nome AS nome_personagem
            FROM evento e
            WHERE e.id_personagem = {id_personagem}
        """

        conn, cursor = conectar_banco_dados()
        cursor.execute(query_fav_usuario_personagens)
        resultado_fav_personagens = cursor.fetchone()

        if resultado_fav_personagens:
            nome_carta = resultado_fav_personagens[0] 
            return nome_carta

        cursor.execute(query_fav_usuario_eventos)
        resultado_fav_eventos = cursor.fetchone()

        if resultado_fav_eventos:
            nome_carta = resultado_fav_eventos[0]  
            return nome_carta
        
        return None

    except Exception as e:
        print(f"Erro ao obter nome da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)

    try:
        query_fav_usuario_personagens = f"""
            SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, 0 AS quantidade, p.categoria, p.imagem
            FROM personagens p
            WHERE p.id_personagem = {id_personagem}
        """
        query_fav_usuario_eventos = f"""
            SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria, e.imagem
            FROM evento e
            WHERE e.id_personagem = {id_personagem}
"""
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_fav_usuario_personagens)
        resultado_fav_personagens = cursor.fetchone()

        if resultado_fav_personagens:
            nome_carta = resultado_fav_personagens[2]
            return nome_carta
        cursor.execute(query_fav_usuario_eventos)
        resultado_fav_eventos = cursor.fetchone()

        if resultado_fav_eventos:
            nome_carta = resultado_fav_eventos[2] 
            return nome_carta
        return None

    except Exception as e:
        print(f"Erro ao obter nome da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)

def obter_imagem_carta(id_usuario):
    try:
        query_fav_usuario_personagens = f"""
            SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, 0 AS quantidade, p.categoria, p.imagem
            FROM personagens p
            WHERE p.id_personagem = (
                SELECT fav
                FROM usuarios
                WHERE id_usuario = {id_usuario}
            )
        """
        query_fav_usuario_eventos = f"""
            SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria, e.imagem
            FROM evento e
            WHERE e.id_personagem = (
                SELECT fav
                FROM usuarios
                WHERE id_usuario = {id_usuario}
            )
        """

        conn, cursor = conectar_banco_dados()
        cursor.execute(query_fav_usuario_personagens)
        resultado_fav_personagens = cursor.fetchone()

        if resultado_fav_personagens:
            id_carta_personagens = resultado_fav_personagens[0]
            query_obter_imagem_personagens = "SELECT imagem FROM personagens WHERE id_personagem = %s"
            cursor.execute(query_obter_imagem_personagens, (id_carta_personagens,))
            imagem_carta_personagens = cursor.fetchone()
            
            if imagem_carta_personagens:
                return imagem_carta_personagens[0]

        cursor.execute(query_fav_usuario_eventos)
        resultado_fav_eventos = cursor.fetchone()

        if resultado_fav_eventos:
            id_carta_eventos = resultado_fav_eventos[0]
            query_obter_imagem_eventos = "SELECT imagem FROM evento WHERE id_personagem = %s"
            cursor.execute(query_obter_imagem_eventos, (id_carta_eventos,))
            imagem_carta_eventos = cursor.fetchone()

            if imagem_carta_eventos:
                return imagem_carta_eventos[0]
        return None

    except Exception as e:
        print(f"Erro ao obter imagem da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)
        
def obter_nome_carta(id_usuario):
    try:
        query_fav_usuario = f"""
            SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, 0 AS quantidade, p.categoria, p.imagem
            FROM personagens p
            WHERE p.id_personagem = (
                SELECT fav
                FROM usuarios
                WHERE id_usuario = {id_usuario}
            )
        """
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_fav_usuario)
        resultado_fav = cursor.fetchone()

        if resultado_fav:
            nome_carta = resultado_fav[2] 
            return nome_carta
        else:
            return None
    except Exception as e:
        print(f"Erro ao obter nome da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)
                    
def obter_quantidade_total_cartas(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT COUNT(DISTINCT id_personagem) FROM inventario WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            return 0
    finally:
        fechar_conexao(cursor, conn)
        
def obter_cartas_subcateg(subcategoria, conn):
    try:
        subcategoria = subcategoria.split('_')[-1].lower()
        cursor = conn.cursor()
        cursor.execute("SELECT id_personagem, emoji, nome, imagem FROM personagens WHERE subcategoria = %s", (subcategoria,))
        cartas = cursor.fetchall()
        return cartas

    except mysql.connector.Error as err:
        print(f"Erro ao obter cartas da subcategoria: {err}")
        return None
    finally:
        fechar_conexao(cursor, conn)     
                   
def obter_total_pescagens(id_personagem, cursor):
    cursor.execute("SELECT total FROM personagens WHERE id_personagem = %s", (id_personagem,))
    total_pescagens = cursor.fetchone()
    return total_pescagens[0] if total_pescagens else 0
        
def obter_informacoes_carta(card_id):
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT id_personagem, emoji, nome, subcategoria FROM personagens WHERE id_personagem = %s", (card_id,))
    result_personagens = cursor.fetchone()

    if result_personagens:
        return result_personagens
    cursor.execute("SELECT id_personagem, emoji, nome, subcategoria FROM evento WHERE id_personagem = %s", (card_id,))
    result_evento = cursor.fetchone()
    return result_evento

def obter_nome_usuario_por_id(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        query = "SELECT nome_usuario FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0] 
        else:
            return "Nome de Usuário Desconhecido"
    except Exception as e:
        print(f"Erro ao obter nome do usuário: {e}")
        return "Nome de Usuário Desconhecido"      

def obter_url_imagem_por_id(id_carta):
    try:
        conn, cursor = conectar_banco_dados()
        sql = "SELECT imagem FROM personagens WHERE id_personagem = %s"
        cursor.execute(sql, (id_carta,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            return None
    except Exception as e:
        print(f"Erro ao obter URL da imagem por ID: {e}")
        return None
    finally:
        fechar_conexao(cursor, conn)

def obter_info_carta_por_id(id_carta):
    try:
        conn, cursor = conectar_banco_dados()
        sql = """
            SELECT emoji, id_personagem, nome, subcategoria
            FROM personagens
            WHERE id_personagem = %s
        """
        values = (id_carta,)
        cursor.execute(sql, values)
        resultado = cursor.fetchone()

        if resultado:
            emoji, id_personagem, nome, subcategoria = resultado
            info_carta = {
                'emoji': emoji,
                'id': id_personagem,
                'nome': nome,
                'subcategoria': subcategoria
            }
            return info_carta
        return None
    except mysql.connector.Error as e:
        print(f"Erro ao obter informações da carta por ID: {e}")
    finally:
        fechar_conexao(cursor, conn)
        
def obter_nome_do_usuario(id_usuario):
    try:
        conn = mysql.connector.connect(**db_config())  # Substitua db_config() pelas suas configurações de conexão
        cursor = conn.cursor()

        query = "SELECT nome FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]  # Retorna o valor da primeira coluna (nome) da linha encontrada
        else:
            return None  # Retorna None se nenhum usuário com o ID fornecido for encontrado

    except mysql.connector.Error as err:
        print(f"Erro ao obter nome do usuário: {err}")
        return None

    finally:
        cursor.close()
        conn.close()        

def verificar_evento(cursor, id_personagem):
    try:
        cursor.execute("SELECT id_personagem FROM evento WHERE id_personagem = %s", (id_personagem,))
        result = cursor.fetchone()
        cursor.fetchall()
        return result is not None
    
    except Exception as e:
        print(f"Erro ao verificar evento: {e}")
        return False
    
def obter_link_formatado(link):
    parsed_url = urlparse(link)
    if parsed_url.scheme and parsed_url.netloc:
        return f"<a href='{link}'>🎨 | Créditos da imagem!</a>"
    else:
        return "CR"
    
def obter_resultados_faltante(subcategoria, numero_pagina, id_usuario):
    subcategoria_com_prefixo = "f " + subcategoria
    conn, cursor = conectar_banco_dados()
    try:
        print(subcategoria_com_prefixo, numero_pagina, id_usuario)
        cursor.execute("SELECT cartas_json FROM temp_cartas WHERE subcategoria = %s AND pagina = %s AND id_usuario = %s", (subcategoria_com_prefixo, numero_pagina, id_usuario))
        resultados = cursor.fetchall()
        
        return resultados
    finally:
        fechar_conexao(cursor, conn)
 
def inventario_existe(id_usuario, id_personagem):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT 1 FROM inventario WHERE id_usuario = %s AND id_personagem = %s", (id_usuario, id_personagem))
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"Erro ao verificar inventário: {e}")
        return False
    finally:
        fechar_conexao(cursor, conn)
        