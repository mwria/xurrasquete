
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
from io import BytesIO
from telebot import types
import functools
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import urlparse
import threading
import os
import Levenshtein
from mysql.connector import Error
import re
import time

# mabi
bot = telebot.TeleBot("6322486327:AAFiMFBB1qbUBUXm1apMDndfIVY0L8FbMz0")
# Dicionário para armazenar os peixes divididos por página
dict_peixes_por_pagina = {}
# Dicionário para rastrear a página atual de cada usuário
user_pages = {}
#dicionarios
callbacks_temp = {}
estados = {}
links_gif = {}
motivos_reprovacao = {}
ultima_interacao = {}
armazem_info = {}
cartas_legenda = {}
ultimo_clique = {}
categoria_escolhida = {}
message_ids = {}
mensagens_editaveis = []
cesta_info = []
botao_clicado = False

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
# Diretório para o cache de imagens
CACHE_DIR = "cache_imagens"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


def evento_command(message):
    try:
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        conn, cursor = conectar_banco_dados()
        qnt_carta(message.from_user.id)
        id_usuario = message.from_user.id
        user = message.from_user
        usuario = user.first_name
        
        comando_parts = message.text.split('/evento ', 1)[1].strip().lower().split(' ')
        if len(comando_parts) >= 2:
            evento = comando_parts[1]
            print(evento)
            subcategoria = ' '.join(comando_parts[1:])
        else:
            resposta = "Comando inválido. Use /evento <evento> <subcategoria>."
            bot.send_message(message.chat.id, resposta)
            return

        sql_evento_existente = f"SELECT DISTINCT evento FROM evento WHERE evento = '{evento}'"
        cursor.execute(sql_evento_existente)
        evento_existente = cursor.fetchone()
        if not evento_existente:
            resposta = f"Evento '{evento}' não encontrado na tabela de eventos."
            bot.send_message(message.chat.id, resposta)
            return

        if message.text.startswith('/evento s'):
            resposta_completa = comando_evento_s(id_usuario, evento, subcategoria, cursor,usuario)
        elif message.text.startswith('/evento f'):
            resposta_completa = comando_evento_f(id_usuario, evento, subcategoria, cursor,usuario)
        else:
            resposta = "Comando inválido. Use /evento s <evento> <subcategoria> ou /evento f <evento> <subcategoria>."
            bot.send_message(message.chat.id, resposta)
            return

        if isinstance(resposta_completa, tuple):
            subcategoria_pesquisada, lista = resposta_completa
            resposta = f"{lista}"
            bot.send_message(message.chat.id, resposta)
        else:
            bot.send_message(message.chat.id, resposta_completa)
    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)
    finally:
        fechar_conexao(cursor, conn)
        
def comando_evento_s(id_usuario, evento, subcategoria, cursor,usuario):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    sql_usuario = f"""
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        JOIN inventario i ON e.id_personagem = i.id_personagem
        WHERE i.id_usuario = {id_usuario} AND e.evento = '{evento}'
        ORDER BY e.id_personagem ASC;
    """

    cursor.execute(sql_usuario)
    resultados_usuario = cursor.fetchall()
    if resultados_usuario:
        lista_cartas = ""
        cartas_removidas = []

        for carta in resultados_usuario:
            id_carta = carta[1]
            emoji_carta = carta[0]
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas += f"{emoji_carta} {formatar_id(id_carta)} — {nome_carta}\n"
        if lista_cartas:
            resposta = f"🌾 | Cartas do evento {evento} no inventario de {usuario}:\n\n{lista_cartas}"
            return subcategoria_carta, resposta
    return f"🌧 Sem cartas de {subcategoria} no evento {evento}! A jornada continua..."


def comando_evento_f(id_usuario, evento, subcategoria, cursor,usuario):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    sql_faltantes = f"""
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        WHERE e.evento = '{evento}' 
            AND NOT EXISTS (
                SELECT 1
                FROM inventario i
                WHERE i.id_usuario = {id_usuario} AND i.id_personagem = e.id_personagem
            )
    """
    cursor.execute(sql_faltantes)
    resultados_faltantes = cursor.fetchall()

    if resultados_faltantes:
        lista_cartas = ""
        for carta in resultados_faltantes:
            id_carta = carta[1]
            emoji_carta = carta[0]
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas += f"{emoji_carta} {formatar_id(id_carta)} — {nome_carta}\n"
        if lista_cartas:
            resposta = f"☀️ | Cartas do evento {evento} que não estão no inventário de {usuario}:\n\n{lista_cartas}"
            return subcategoria_carta, resposta
    return f"☀️ Nada como a alegria de ter todas as cartas de {subcategoria} no evento {evento} na cesta!"

def comando_evento_s(id_usuario, evento, subcategoria, cursor,usuario):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    sql_usuario = f"""
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        JOIN inventario i ON e.id_personagem = i.id_personagem
        WHERE i.id_usuario = {id_usuario} AND e.evento = '{evento}'
        ORDER BY e.id_personagem ASC;
    """

    cursor.execute(sql_usuario)
    resultados_usuario = cursor.fetchall()
    if resultados_usuario:
        lista_cartas = ""
        cartas_removidas = []

        for carta in resultados_usuario:
            id_carta = carta[1]
            emoji_carta = carta[0]
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas += f"{emoji_carta} {formatar_id(id_carta)} — {nome_carta}\n"
        if lista_cartas:
            resposta = f"🌾 | Cartas do evento {evento} no inventario de {usuario}:\n\n{lista_cartas}"
            return subcategoria_carta, resposta
    return f"🌧 Sem cartas de {subcategoria} no evento {evento}! A jornada continua..."


def comando_evento_f(id_usuario, evento, subcategoria, cursor,usuario):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    sql_faltantes = f"""
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        WHERE e.evento = '{evento}' 
            AND NOT EXISTS (
                SELECT 1
                FROM inventario i
                WHERE i.id_usuario = {id_usuario} AND i.id_personagem = e.id_personagem
            )
    """
    cursor.execute(sql_faltantes)
    resultados_faltantes = cursor.fetchall()

    if resultados_faltantes:
        lista_cartas = ""
        for carta in resultados_faltantes:
            id_carta = carta[1]
            emoji_carta = carta[0]
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas += f"{emoji_carta} {formatar_id(id_carta)} — {nome_carta}\n"
        if lista_cartas:
            resposta = f"☀️ | Cartas do evento {evento} que não estão no inventário de {usuario}:\n\n{lista_cartas}"
            return subcategoria_carta, resposta
    return f"☀️ Nada como a alegria de ter todas as cartas de {subcategoria} no evento {evento} na cesta!"
def verificar_evento(cursor, id_personagem):
    try:
        cursor.execute("SELECT id_personagem FROM evento WHERE id_personagem = %s", (id_personagem,))
        result = cursor.fetchone()
        cursor.fetchall()
        return result is not None
    
    except Exception as e:
        print(f"Erro ao verificar evento: {e}")
        return False


def evento_command_handler(message):
    try:
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        conn, cursor = conectar_banco_dados()
        qnt_carta(message.from_user.id)
        id_usuario = message.from_user.id
        user = message.from_user
        usuario = user.first_name
        
        comando_parts = message.text.split('/evento ', 1)[1].strip().lower().split(' ')
        if len(comando_parts) >= 2:
            evento = comando_parts[1]
            print(evento)
            subcategoria = ' '.join(comando_parts[1:])
        else:
            resposta = "Comando inválido. Use /evento <evento> <subcategoria>."
            bot.send_message(message.chat.id, resposta)
            return

        sql_evento_existente = f"SELECT DISTINCT evento FROM evento WHERE evento = '{evento}'"
        cursor.execute(sql_evento_existente)
        evento_existente = cursor.fetchone()
        if not evento_existente:
            resposta = f"Evento '{evento}' não encontrado na tabela de eventos."
            bot.send_message(message.chat.id, resposta)
            return

        if message.text.startswith('/evento s'):
            resposta_completa = comando_evento_s(id_usuario, evento, subcategoria, cursor,usuario)
        elif message.text.startswith('/evento f'):
            resposta_completa = comando_evento_f(id_usuario, evento, subcategoria, cursor,usuario)
        else:
            resposta = "Comando inválido. Use /evento s <evento> <subcategoria> ou /evento f <evento> <subcategoria>."
            bot.send_message(message.chat.id, resposta)
            return

        if isinstance(resposta_completa, tuple):
            subcategoria_pesquisada, lista = resposta_completa
            resposta = f"{lista}"
            bot.send_message(message.chat.id, resposta)
        else:
            bot.send_message(message.chat.id, resposta_completa)
    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)
    finally:
        fechar_conexao(cursor, conn)
        
def get_random_card_valentine(subcategoria):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute(
            "SELECT id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'amor' ORDER BY RAND() LIMIT 1",
            (subcategoria,))
        evento_aleatorio = cursor.fetchone()
        if evento_aleatorio:
            chance = random.randint(1, 100)

            if chance <= 100:
                id_personagem, nome, subcategoria, imagem = evento_aleatorio
                evento_formatado = {
                    'id_personagem': id_personagem,
                    'nome': nome,
                    'subcategoria': subcategoria,
                    'imagem': imagem  
                }

                return evento_formatado
            else:
                return None
        else:
            print("Nenhum evento fixo encontrado. Procedendo com lógica normal.")

    except Exception as e:
        print(f"Erro ao verificar subcategoria na tabela de eventos: {e}")
        return None

def alternar_evento():
    global evento_ativo
    evento_ativo = not evento_ativo

def get_random_subcategories_all_valentine(connection):
    cursor = connection.cursor()
    query = "SELECT subcategoria FROM evento WHERE evento = 'amor' ORDER BY RAND() LIMIT 2"
    cursor.execute(query)
    subcategories_valentine = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return subcategories_valentine      
def obter_informacoes_loja(ids_do_dia):
    try:
        conn, cursor = conectar_banco_dados()
        placeholders = ', '.join(['%s' for _ in ids_do_dia])
        cursor.execute(
            f"SELECT id_personagem, emoji, nome, subcategoria FROM personagens WHERE id_personagem IN ({placeholders})",
            tuple(ids_do_dia))
        cartas_loja = cursor.fetchall()
        return cartas_loja

    except mysql.connector.Error as err:
        print(f"Erro ao obter informações da loja: {err}")
    finally:
        cursor.close()
        conn.close()
        
def obter_ids_loja_do_dia(data_atual):
    try:
        conn, cursor = conectar_banco_dados()
        ordem_categorias = {'Música': 1, 'animangá': 2, 'Filmes': 3, 'Séries': 4, 'Jogos': 5, 'Miscelânea': 6}
        cursor.execute(
            "SELECT l.id_personagem FROM loja AS l "
            "JOIN personagens AS p ON l.id_personagem = p.id_personagem "
            "WHERE l.data = %s "
            "ORDER BY FIELD(p.categoria, %s)",
            (data_atual, ','.join(f"'{cat}'" for cat in ordem_categorias.keys()))
        )
        ids_do_dia = [id_tuple[0] for id_tuple in cursor.fetchall()]
        print(ids_do_dia)
        return ids_do_dia
    except mysql.connector.Error as err:
        print(f"Erro ao obter IDs da loja para o dia de hoje: {err}")
    finally:
        fechar_conexao(cursor, conn)

def obter_cartas_aleatorias(quantidade=6):
    try:
        conn, cursor = conectar_banco_dados()
        categorias = ['Música', 'Séries', 'Filmes', 'Miscelanêa', 'Jogos', 'Animangá']
        cartas_aleatorias = []

        for categoria in categorias:
            while True:
                cursor.execute(
                    "SELECT id_personagem, nome, subcategoria, imagem, emoji FROM personagens WHERE categoria = %s AND imagem IS NOT NULL ORDER BY RAND() LIMIT 1",
                    (categoria,))
                carta_aleatoria = cursor.fetchone()

                if carta_aleatoria and carta_aleatoria[0]:
                    id_personagem = carta_aleatoria[0]
                    if not id_ja_registrado_na_loja(cursor, id_personagem):
                        cartas_dict = {
                            "id": id_personagem,
                            "nome": carta_aleatoria[1],
                            "subcategoria": carta_aleatoria[2],
                            "imagem": carta_aleatoria[3],
                            "emoji": carta_aleatoria[4],
                            "categoria": categoria 
                        }
                        cartas_aleatorias.append(cartas_dict)
                        print(f"Carta adicionada: {cartas_dict} - Categoria: {categoria}")
                        break
                    else:
                        print(f"ID {id_personagem} já registrado na loja. Tentando outra carta.")
                else:
                    print("Carta não encontrada para a categoria:", categoria)
                    break
        return cartas_aleatorias

    except Exception as e:
        print(f"Erro ao obter cartas aleatórias: {e}")
        return []
    finally:
        fechar_conexao(cursor, conn)

def registrar_cartas_loja(cartas_aleatorias, data_atual):
    try:
        conn, cursor = conectar_banco_dados()

        for carta in cartas_aleatorias:
            id_personagem = carta['id']
            categoria = carta['categoria']
            cursor.execute(
                "SELECT COUNT(*) FROM loja WHERE id_personagem = %s AND data = %s",
                (id_personagem, data_atual)
            )
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute(
                    "INSERT INTO loja (id_personagem, data, categoria) VALUES (%s, %s, %s)",
                    (id_personagem, data_atual, categoria) 
                )
        conn.commit()

    except Exception as e:
        print(f"Erro ao registrar cartas na loja: {e}")
    finally:
        fechar_conexao(cursor, conn)

def id_ja_registrado_na_loja(cursor, id_personagem):
    cursor.execute("SELECT COUNT(*) FROM loja WHERE id_personagem = %s", (id_personagem,))
    count = cursor.fetchone()[0]
    return count > 0
            
def enviar_pergunta_cenoura(message, id_usuario, id_personagem, quantidade):
    try:
        texto_pergunta = f"Você deseja mesmo cenourar a carta {id_personagem}?"
        keyboard = telebot.types.InlineKeyboardMarkup()
        sim_button = telebot.types.InlineKeyboardButton(text="Sim",
                                                         callback_data=f"cenourar_sim_{id_usuario}_{id_personagem}")
        nao_button = telebot.types.InlineKeyboardButton(text="Não",
                                                         callback_data=f"cenourar_nao_{id_usuario}_{id_personagem}")
        keyboard.row(sim_button, nao_button)
        bot.send_message(message.chat.id, texto_pergunta, reply_markup=keyboard)
    except Exception as e:
        print(f"Erro ao enviar pergunta de cenourar: {e}")

def verificar_e_cenourar_carta(message):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = message.from_user.id
        id_personagem = message.text.replace('/cenourar', '').strip()
        print(id_usuario, id_personagem)

        cursor.execute(
            "SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
            (id_usuario, id_personagem)
        )
        quantidade_atual = cursor.fetchone()
        print(quantidade_atual)

        if quantidade_atual:
            res = functools.reduce(lambda sub, ele: sub * 10 + ele, quantidade_atual)
            if res >= 1:
                nova_quantidade = res - 1
                cursor.execute(
                    "UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s",
                    (nova_quantidade, id_usuario, id_personagem)
                )
                enviar_pergunta_cenoura(message, id_usuario, id_personagem, nova_quantidade)
            else:
                bot.send_message(message.chat.id, "Você não possui cenouras suficientes para cenourar esta carta.")
        else:
            bot.send_message(message.chat.id, "Você não possui essa carta no inventário.")

    except Exception as e:
        print(f"Erro ao processar o comando de cenourar: {e}")
        chat = message.chat.id
        bot.send_message(chat_id=chat, text="Erro ao processar o comando de cenourar.")

    finally:
        fechar_conexao(cursor, conn)


def cenourar_carta(message, id_usuario, id_personagens, sim=True):
    try:
        conn, cursor = conectar_banco_dados()
        mensagem_cenoura = f"Cenourando carta:\n"
        cartas_cenouradas = []
        
        for id_personagem in id_personagens.split(","):
            id_personagem = id_personagem.strip()
            cursor.execute(
                "SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                (id_usuario, id_personagem))
            quantidade_atual = cursor.fetchone()

            if quantidade_atual is not None and quantidade_atual[0] > 0:
                quantidade_atual = int(quantidade_atual[0])
                cursor.execute(
                    "SELECT cenouras FROM usuarios WHERE id_usuario = %s",
                    (id_usuario,))
                cenouras = int(cursor.fetchone()[0])
                
                if quantidade_atual >= 1:
                    nova_quantidade = quantidade_atual - 1
                    novas_cenouras = cenouras + 1
                    cursor.execute(
                        "UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s",
                        (nova_quantidade, id_usuario, id_personagem))
                    cursor.execute(
                        "UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s",
                        (novas_cenouras, id_usuario))

                    cartas_cenouradas.append((id_personagem, nova_quantidade))
                    mensagem_cenoura += f"{id_personagem}\n"
                    conn.commit()

            else:
                mensagem_erro = f"Erro ao processar a cenoura. A carta {id_personagem} não foi encontrada no inventário."
                bot.send_message(message.chat.id, mensagem_erro)

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=mensagem_cenoura)
        mensagem_consolidada = "Cartas cenouradas com sucesso:\n"
        for carta, nova_quantidade in cartas_cenouradas:
            mensagem_consolidada += f"{carta} - Nova quantidade: {nova_quantidade}\n"
        bot.send_message(message.chat.id, mensagem_consolidada)
    except Exception as e:
        print(f"Erro ao processar cenoura: {e}")
    finally:
        fechar_conexao(cursor, conn)

def verificar_id_na_tabelabeta(user_id):
    try:
        conn, cursor = conectar_banco_dados() 
        query = f"SELECT id FROM beta WHERE id = {user_id}"
        cursor.execute(query)
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return resultado is not None
    except Exception as e:
        print(f"Erro ao verificar ID na tabela beta: {e}")
        raise ValueError("Erro ao verificar ID na tabela beta")
    
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
                # Consulta SQL combinada para buscar cartas do usuário em ambas as tabelas
        # Consulta SQL para buscar imagem por id_carta na tabela personagens ou evento
        sql = f"""
            SELECT id_personagem, imagem
            FROM (
                SELECT id_personagem, imagem
                FROM personagens
                WHERE id_personagem = %s
                UNION ALL
                SELECT id_personagem, imagem
                FROM evento
                WHERE id_personagem = %s
            ) AS cartas_usuario
        """
        cursor.execute(sql, (id_carta, id_carta))
        resultado = cursor.fetchone()
        print(id_carta)
        print("resultado:",resultado)
        if resultado:
            return resultado[1]
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

def obter_limite_cativeiro(id_personagem):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta para obter o limite atual do cativeiro para o id_personagem
        query_obter_limite = "SELECT limite FROM cativeiro WHERE id_personagem = %s"
        cursor.execute(query_obter_limite, (id_personagem,))
        resultado = cursor.fetchone()

        if resultado:
            limite_atual = resultado[0]
            return limite_atual
        else:
            return 100  # Retorna um limite padrão de 100 se não houver registro para o personagem

    except mysql.connector.Error as e:
        print(f"Erro ao obter limite do cativeiro para o personagem {id_personagem}: {e}")
        return 100  # Retorna um limite padrão de 100 em caso de erro

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


def verificar_registro_cativeiro(id_usuario, id_personagem):
    # Verifica se o usuário está registrado no cativeiro desta carta
    try:
        conn, cursor = conectar_banco_dados()

        query_verificar_registro = """
            SELECT id_usuario
            FROM seeds
            WHERE id_usuario = %s AND id_personagem = %s
        """
        cursor.execute(query_verificar_registro, (id_usuario, id_personagem))
        result = cursor.fetchone()

        if result:
            return True
        else:
            return False

    except mysql.connector.Error as e:
        print(f"Erro ao verificar registro no cativeiro: {e}")
        return False

    finally:
        fechar_conexao(cursor, conn)

def quantidade_cartas_usuario(id_usuario, id_personagem):
    # Retorna a quantidade total de cartas que um usuário possui de um personagem específico
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
            return 0  # Retorna 0 se não houver registros
        print("quantidade",quantidade)
    except mysql.connector.Error as e:
        print(f"Erro ao obter quantidade de cartas do usuário: {e}")
        return 0  # Retorna 0 em caso de erro

    finally:
        fechar_conexao(cursor, conn)


def verifica_limite_cativeiro(id_personagem):
    # Verifica se o limite de cativeiro para um usuário e uma carta específicos foi atingido
    try:
        conn, cursor = conectar_banco_dados()

        # Obter o limite de cativeiro para essa carta
        query_verificar_limite = """
            SELECT limite
            FROM cativeiro
            WHERE id_personagem = %s
        """
        cursor.execute(query_verificar_limite, (id_personagem,))
        result = cursor.fetchone()

        if result:
            limite_cativeiro = result[0]
            return limite_cativeiro
        else:
            limite_cativeiro = 100  # Limite padrão 100 se não houver limite definido
            return limite_cativeiro

    except mysql.connector.Error as e:
        print(f"Erro ao verificar limite de cativeiro: {e}")
        return False, 100  # Retornar limite padrão 100 em caso de erro

    finally:
        fechar_conexao(cursor, conn)
            
@bot.message_handler(commands=['iduser'])
def handle_iduser_command(message):
    if message.reply_to_message:
        idusuario = message.reply_to_message.from_user.id
        bot.send_message(chat_id=message.chat.id, text=f"O ID do usuário é <code>{idusuario}</code>", reply_to_message_id=message.message_id,parse_mode="HTML")


user_data = {}

def gerar_id_unico():
    if "ultimo_id" not in user_data:
        user_data["ultimo_id"] = 0
    user_data["ultimo_id"] += 1
    return user_data["ultimo_id"]

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
        
def obter_resultados_pagina_f(subcategoria, numero_pagina, id_usuario):
    print("2")
    subcategoria_com_prefixo = "f " + subcategoria
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("SELECT cartas_json FROM temp_cartas WHERE subcategoria = %s AND pagina = %s AND id_usuario = %s", (subcategoria_com_prefixo, numero_pagina, id_usuario))
        resultados = cursor.fetchall()
    
        return resultados
    finally:
        fechar_conexao(cursor, conn)

def obter_resultados_pagina(subcategoria, numero_pagina, id_usuario):
    print("2")
    subcategoria_com_prefixo = "s " + subcategoria
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("SELECT cartas_json FROM temp_cartas WHERE subcategoria = %s AND pagina = %s AND id_usuario = %s", (subcategoria_com_prefixo, numero_pagina, id_usuario))
        resultados = cursor.fetchall()
    
        return resultados
    finally:
        fechar_conexao(cursor, conn)

def registrar_cartas_cesta_f(usuario, subcategoria, resposta_completa, modo):
    conn, cursor = conectar_banco_dados()
    modo = "f"

    # Ajustar a subcategoria para buscar subcategorias semelhantes na tabela personagens
    split_subcategoria = subcategoria.split(' ', 1)
    if len(split_subcategoria) > 1:
        subcategoria_pesquisada = split_subcategoria[1].strip().title()
    else:
        subcategoria_pesquisada = subcategoria.strip().title()

    subcategoria_like = f'{modo} {subcategoria_pesquisada}'
    deletar = f'{modo} {subcategoria}'

    try:
        # Excluir os registros antigos para o usuário e subcategoria diretamente
        sql_excluir_registros = f"""
            DELETE FROM temp_cestaf
            WHERE id_usuario = {usuario} AND subcategoria = '{deletar}'
        """
        cursor.execute(sql_excluir_registros)
        conn.commit()

        # Procurar a primeira subcategoria similar na tabela personagens
        primeira_subcategoria_similar = procurar_subcategorias_similares(cursor, subcategoria_like)

        if primeira_subcategoria_similar:
            subcategoria_similar = f'{modo} {primeira_subcategoria_similar[0]}'

            # Verificar se resposta_completa é uma lista de dicionários
            if isinstance(resposta_completa, list) and all(isinstance(carta, dict) for carta in resposta_completa):
                # Extrair os IDs das cartas da resposta completa
                ids_cartas = [carta['id'] for carta in resposta_completa]

                # Dividir os IDs em páginas de até 15 IDs por página
                paginas_ids = [ids_cartas[i:i+15] for i in range(0, len(ids_cartas), 15)]

                for pagina_numero, ids_pagina in enumerate(paginas_ids, start=1):
                    # Filtrar as cartas da página atual
                    cartas_pagina = [carta for carta in resposta_completa if carta['id'] in ids_pagina]

                    # Formatar as cartas da página em formato JSON
                    cartas_json = "\n".join([f"{carta['emoji']} {carta['id']} - {carta['nome']}" for carta in cartas_pagina])

                    # Inserir a página no banco de dados
                    sql_inserir_cartas = """
                        INSERT INTO temp_cestaf (id_usuario, subcategoria, cartas_json, pagina)
                        VALUES (%s, %s, %s, %s)
                    """
                    try:
                        cursor.execute(sql_inserir_cartas, (usuario, subcategoria_similar, cartas_json, pagina_numero))
                        print(f"Página {pagina_numero} registrada para subcategoria:", subcategoria_similar)
                        conn.commit()
                    except Exception as e:
                        print("Erro ao registrar página:", e)

                return len(paginas_ids)
            else:
                print("O parâmetro 'resposta_completa' não é uma lista válida de dicionários.")
                return 0
        else:
            print("Nenhuma subcategoria similar encontrada.")
            return 0

    except Exception as e:
        print("Erro ao registrar cartas na cesta F:", e)
        return 0

    finally:
        # Sempre fechar a conexão com o banco de dados
        fechar_conexao(cursor, conn)

def enviar_mensagem_inicial(chat_id, mensagem, total_paginas, subcategoria_pesquisada, nome_usuario,message):
    print("1")
    conn, cursor = conectar_banco_dados()
    subcategoria = subcategoria_pesquisada
    idusuario = nome_usuario
    numero_pagina = 1
    
    mensagem_id = gerar_id_unico()
    pagina_atual = 1
    foto_subcategoria = obter_foto_subcategoria(subcategoria, cursor)
    user_data[mensagem_id] = {"texto": mensagem, "chat_id": chat_id}
    resultados_pagina = obter_resultados_pagina(subcategoria, pagina_atual, idusuario)
    print(resultados_pagina)
    texto_formatado = construir_mensagem(resultados_pagina, subcategoria, idusuario, modo='s')  # Alterado para 'f' para a subcategoria faltante
    print(texto_formatado)
    
    if not texto_formatado:  # Verifica se o texto formatado está vazio
        print("Nenhum resultado encontrado.")
        return  # Não envia a mensagem se não houver resultados
    if foto_subcategoria:
        if len(texto_formatado) > 1000:
            mensagem_legenda = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {nome_usuario}:\n\n{texto_formatado}"
        else:
            mensagem_legenda = texto_formatado
        bot.send_photo(chat_id, foto_subcategoria, caption=mensagem_legenda, reply_markup=criar_teclado_paginacao(pagina_atual, total_paginas, mensagem_id, subcategoria, nome_usuario, modo='s'))  # Alterado para 'f' para a subcategoria faltante
    else:
        mensagem_texto = f"\n\n{texto_formatado}"
        bot.send_message(chat_id, mensagem_texto, reply_markup=criar_teclado_paginacao(pagina_atual, total_paginas, mensagem_id, subcategoria, nome_usuario, modo='s'),reply_to_message_id=message.message_id,parse_mode="HTML")  # Alterado para 'f' para a subcategoria faltante
               
def criar_teclado_paginacao(pagina_atual, total_paginas, mensagem_id, subcategoria, id_usuario, modo):
    print("3")
    markup = telebot.types.InlineKeyboardMarkup()
    botoes = []
    if pagina_atual > 1:
        botoes.append(telebot.types.InlineKeyboardButton("⬅️", callback_data=f"vem_{modo}_{pagina_atual}_{total_paginas}_{mensagem_id}_{subcategoria}_{id_usuario}"))
    if pagina_atual < total_paginas:
        botoes.append(telebot.types.InlineKeyboardButton("➡️", callback_data=f"vai_{modo}_{pagina_atual}_{total_paginas}_{mensagem_id}_{subcategoria}_{id_usuario}"))
    markup.row(*botoes)
    return markup

def enviar_resultados_pagina(chat_id, message_id, mensagem, pagina_atual, total_paginas, subcategoria, id_usuario, modo):
    print("5")
    conn, cursor = conectar_banco_dados()
    foto_subcategoria = obter_foto_subcategoria(subcategoria, cursor)
    if foto_subcategoria:
        bot.edit_message_caption(chat_id=chat_id, message_id=message_id, caption=mensagem, reply_markup=criar_teclado_paginacao(pagina_atual, total_paginas, message_id, subcategoria, id_usuario, modo),parse_mode="HTML")
    else:
        print(mensagem)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem, reply_markup=criar_teclado_paginacao(pagina_atual, total_paginas, message_id, subcategoria, id_usuario, modo),parse_mode="HTML")

def construir_mensagem(resultados_pagina, subcategoria, nome_usuario, modo):
    print("6")
    nome_usuario = obter_nome_do_usuario(nome_usuario)
    if modo == 's':
        mensagem = f"🧺 | Cartas de {subcategoria} na cesta de {nome_usuario}:\n\n"
    elif modo == 'f':
        mensagem = f"🧺 | Cartas de {subcategoria} faltantes na cesta de <b>{nome_usuario}</b>:\n\n"
    else:
        mensagem = ""
    
    for resultado in resultados_pagina:
        print(resultado[0])
        mensagem += resultado[0] + "\n"  # Assumindo que o resultado é uma tupla e o texto está na primeira posição
    print(mensagem)
    return mensagem

def obter_foto_subcategoria(subcategoria, cursor):
    conn, cursor = conectar_banco_dados()
    subcategoria_sem_prefixo = subcategoria[2:].strip() if subcategoria.startswith(('s', 'f', 'fn', 'sn')) else subcategoria
    sql = "SELECT imagem FROM subcategorias WHERE nomesub = %s"
    cursor.execute(sql, (subcategoria_sem_prefixo,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def registrar_categorias(id_usuario, categoria, resposta_completa, cursor):
    conn, cursor = conectar_banco_dados()

    # Verificar se já existe um registro para a categoria e o usuário
    sql_verificar_registro = """
        SELECT COUNT(*) FROM temp_categorias
        WHERE id_usuario = %s AND subcategoria = %s
    """
    cursor.execute(sql_verificar_registro, (id_usuario, categoria))
    registro_existente = cursor.fetchone()[0]

    if registro_existente > 0:
        # Se houver registro existente, exclua-o antes de inserir um novo
        sql_excluir_registro = """
            DELETE FROM temp_categorias
            WHERE id_usuario = %s AND subcategoria = %s
        """
        try:
            cursor.execute(sql_excluir_registro, (id_usuario, categoria))
            conn.commit()
            print("Registro existente para categoria excluído com sucesso.")
        except Exception as e:
            print("Erro ao excluir registro existente:", e)

    cartas = resposta_completa[1].split("\n")
    paginas = [cartas[i:i+15] for i in range(0, len(cartas), 15)]

    for i, pagina in enumerate(paginas, start=1):
        cartas_json = "\n".join(pagina)
        pagina_registro = i

        sql_inserir_categorias = """
            INSERT INTO temp_categorias (id_usuario, subcategoria, cartas_json, pagina)
            VALUES (%s, %s, %s, %s)
        """
        try:
            cursor.execute(sql_inserir_categorias, (id_usuario, categoria, cartas_json, pagina_registro))
            print("Página registrada para categoria:", categoria, "-", pagina_registro)
            conn.commit()
        except Exception as e:
            print("Erro ao registrar página de categoria:", e)

    return len(paginas)

def registrar_cartas(usuario, subcategoria, resposta_completa, modo):
    conn, cursor = conectar_banco_dados()

    # Ajustar a subcategoria para buscar subcategorias semelhantes na tabela personagens
    subcategoria_pesquisada = subcategoria.split(' ', 1)[1].strip().title()
    subcategoria_like = f'{modo} {subcategoria_pesquisada}'

    # Excluir os registros antigos para o usuário e subcategoria
    excluir_registros_antigos(cursor, conn, usuario, subcategoria_like)

    # Procurar a primeira subcategoria similar na tabela personagens
    primeira_subcategoria_similar = procurar_subcategorias_similares(cursor, subcategoria_like)

    if primeira_subcategoria_similar:
        subcategoria_similar = f'{modo} {primeira_subcategoria_similar[0]}'
        cartas = resposta_completa[1].split("\n")
        paginas = [cartas[i:i+15] for i in range(0, len(cartas), 15)]

        for i, pagina in enumerate(paginas, start=1):
            cartas_json = "\n".join(pagina)
            pagina_registro = i

            sql_inserir_cartas = """
                INSERT INTO temp_cartas (id_usuario, subcategoria, cartas_json, pagina)
                VALUES (%s, %s, %s, %s)
            """
            try:
                cursor.execute(sql_inserir_cartas, (usuario, subcategoria_similar, cartas_json, pagina_registro))
                print("Página registrada para subcategoria:", subcategoria_similar, "-", pagina_registro)
                conn.commit()
            except Exception as e:
                print("Erro ao registrar página:", e)

        return len(paginas)
    else:
        print("Nenhuma subcategoria similar encontrada.")
        return 0
    
def comando_cesta_s(id_usuario, subcategoria, cursor):
    subcategoria = subcategoria.split(' ', 1)[1].strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    sql = f"""
SELECT * FROM (
    SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria, i.quantidade, 'normal' AS tipo
    FROM personagens p
    JOIN inventario i ON p.id_personagem = i.id_personagem
    WHERE i.id_usuario = {id_usuario} AND (p.subcategoria LIKE '{subcategoria}%' OR p.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
    UNION ALL
    SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria, i.quantidade, 'evento' AS tipo
    FROM evento e
    JOIN inventario i ON e.id_personagem = i.id_personagem
    WHERE i.id_usuario = {id_usuario} AND (e.subcategoria LIKE '{subcategoria}%' OR e.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
) AS combined
ORDER BY
    CASE WHEN tipo = 'evento' THEN 1 ELSE 2 END,  -- Ordenar eventos primeiro (tipo = 'evento' é 1, outros são 2)
    id_personagem ASC  -- Em seguida, ordenar por nome_personagem em ordem crescente

    """

    cursor.execute(sql)
    resultados = cursor.fetchall()
    if resultados:
        lista_cartas = ""
        for carta in resultados:
            emoji_carta = carta[0]
            id_carta = carta[1] # Formata o id_personagem
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            quantidade_carta = carta[4]
            if quantidade_carta == 1:
                letra_quantidade = ""
            elif 2 <= quantidade_carta <= 4:
                letra_quantidade = "🌾"
            elif 5 <= quantidade_carta <= 9:
                letra_quantidade = "🌼"
            elif 10 <= quantidade_carta <= 19:
                letra_quantidade = "☀️"
            elif 20 <= quantidade_carta <= 29:
                letra_quantidade = "🍯️"
            elif 30 <= quantidade_carta <= 39:
                letra_quantidade = "🐝"
            elif 40 <= quantidade_carta <= 49:
                letra_quantidade = "🌻"
            elif 50 <= quantidade_carta:
                letra_quantidade = "👑"
            else:
                letra_quantidade = ""
            lista_cartas += f"{emoji_carta} {id_carta} — {nome_carta} {letra_quantidade}\n"
        return subcategoria_carta, lista_cartas
    else:
        return f"🌧️ Sem cartas de {subcategoria} na cesta! A jornada continua..."

def comando_cesta_f(id_usuario, subcategoria_comando, cursor):
    try:
        # Extrair a subcategoria do comando
        partes = subcategoria_comando.split(' ', 1)
        if len(partes) < 2:
            return "Formato inválido. Use '/cesta f <subcategoria>'."

        subcategoria = partes[1].strip().title()
        print("Subcategoria:", subcategoria)  # Log: Verifica o valor da subcategoria recebida

        def formatar_id(id_personagem):
            return str(id_personagem).zfill(4)

        sql = f"""
SELECT * FROM (
    SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria, 'normal' AS tipo
    FROM personagens p
    WHERE (p.subcategoria LIKE '{subcategoria}%' OR p.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
        AND NOT EXISTS (
            SELECT 1
            FROM inventario i
            WHERE i.id_usuario = {id_usuario} AND i.id_personagem = p.id_personagem
        )
    UNION ALL
    SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria, 'evento' AS tipo
    FROM evento e
    WHERE (e.subcategoria LIKE '{subcategoria}%' OR e.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
        AND NOT EXISTS (
            SELECT 1
            FROM inventario i
            WHERE i.id_usuario = {id_usuario} AND i.id_personagem = e.id_personagem
        )
) AS combined
ORDER BY
    CASE WHEN tipo = 'evento' THEN 1 ELSE 2 END,  -- Ordenar eventos primeiro (tipo = 'evento' é 1, outros são 2)
    id_personagem ASC  -- Em seguida, ordenar por id_personagem em ordem crescente

        """

        cursor.execute(sql)
        resultados = cursor.fetchall()

        if resultados:
            lista_cartas = []
            for carta in resultados:
                emoji_carta = carta[0]
                id_carta = carta[1]  # Formata o id_personagem
                nome_carta = carta[2]
                subcategoria_carta = carta[3].title()
                lista_cartas.append({"emoji": emoji_carta, "id": id_carta, "nome": nome_carta})

            registrar_cartas_cesta_f(id_usuario, subcategoria, lista_cartas, modo='f')
            return lista_cartas, subcategoria

        else:
            mensagem = f"☀️ Nada como a alegria de ter todos os peixes de {subcategoria} na cesta!"
            print("Mensagem:", mensagem)  # Log: Exibe a mensagem quando não há cartas encontradas
            subcategoria = None
            return mensagem,subcategoria

    except Exception as e:
        print(f"Erro ao processar comando /cesta: {e}")
        return "Ocorreu um erro ao processar o comando /cesta."


def comando_cesta_fn(id_usuario, subcategoria, cursor):
    subcategoria = subcategoria.split(' ', 1)[1].strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    sql = f"""
        SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria
        FROM personagens p
        WHERE (p.subcategoria LIKE '{subcategoria}%' OR p.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
            AND NOT EXISTS (
                SELECT 1
                FROM inventario i
                WHERE i.id_usuario = {id_usuario} AND i.id_personagem = p.id_personagem
            )
        ORDER BY id_personagem DESC
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()
    if resultados:
        lista_cartas = ""
        for carta in resultados:
            emoji_carta = carta[0]
            id_carta = formatar_id(carta[1])  # Formata o id_personagem
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas += f"{emoji_carta} {id_carta} — {nome_carta}\n"
        return subcategoria_carta, lista_cartas
    else:
        return f"☀️ Nada como a alegria de ter todos os peixes de {subcategoria} na cesta!"
    
def comando_cesta_cs(id_usuario, categoria, cursor):
    print("chegou")
    categoria = categoria.split(' ', 1)[1].strip().title()
    sql = f"""
        SELECT * FROM (
            SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria
            FROM personagens p
            JOIN inventario i ON p.id_personagem = i.id_personagem
            WHERE i.id_usuario = {id_usuario} AND (p.categoria LIKE '{categoria}%' OR p.categoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{categoria}' AND tipo = 'Categoria'))
        ) AS combined
        ORDER BY nome_personagem
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()
    if resultados:
        lista_cartas = ""
        for carta in resultados:
            emoji_carta = carta[0]
            id_carta = carta[1]
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas += f"{emoji_carta} {id_carta} • {nome_carta} — {subcategoria_carta}\n"
        return categoria, lista_cartas
    else:
        return f"🌧️ Sem cartas da categoria {categoria} na cesta! A jornada continua..."

@bot.message_handler(commands=['supergroupid'])
def supergroup_id_command(message):
    chat_id = message.chat.id
    chat_type = message.chat.type

    if chat_type == 'supergroup':
        chat_info = bot.get_chat(chat_id)
        bot.send_message(chat_id, f"O ID deste supergrupo é: <code>{chat_info.id}</code>", reply_to_message_id=message.message_id,parse_mode="HTML")
    else:
        bot.send_message(chat_id, "Este chat não é um supergrupo.")

@bot.message_handler(commands=['idchat'])
def handle_idchat_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"O ID deste chat é<code>{chat_id}</code>", reply_to_message_id=message.message_id,parse_mode="HTML")

def verificar_valor_existente(coluna, valor):
    try:
        conn, cursor = conectar_banco_dados()
        query = f"SELECT * FROM usuarios WHERE {coluna} = %s"
        cursor.execute(query, (valor,))
        resultado = cursor.fetchone()

        return resultado is not None

    except mysql.connector.Error as err:
        print(f"Erro ao verificar {coluna}: {err}")

    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['setuser'])
def setuser_comando(message):
    command_parts = message.text.split()
    if len(command_parts) != 2:
        bot.send_message(message.chat.id, "Formato incorreto. Use /setuser seguido do nome desejado, por exemplo: /setuser novouser.", reply_to_message_id=message.message_id)
        return

    nome_usuario = command_parts[1].strip()


    # Verificar se o nome de usuário contém apenas caracteres permitidos e não ultrapassa 20 caracteres
    if not re.match("^[a-zA-Z0-9_]{1,20}$", nome_usuario):
        bot.send_message(message.chat.id, "Nome de usuário inválido. Use apenas letras, números e '_' e não ultrapasse 20 caracteres.", reply_to_message_id=message.message_id)
        return

    try:
        conn, cursor = conectar_banco_dados()

        # Verificar se o nome de usuário já está em uso
        cursor.execute("SELECT 1 FROM usuarios WHERE user = %s", (nome_usuario,))
        if cursor.fetchone():
            bot.send_message(message.chat.id, "O nome de usuário já está em uso. Escolha outro nome de usuário.", reply_to_message_id=message.message_id)
            return
        # Verificar se o nome de usuário já está banido
        cursor.execute("SELECT 1 FROM usuarios_banidos WHERE id_usuario = %s", (nome_usuario,))
        if cursor.fetchone():
            bot.send_message(message.chat.id, "O nome de usuário já está em uso. Escolha outro nome de usuário.", reply_to_message_id=message.message_id)
            return
        # Atualizar o nome de usuário na tabela 'usuarios'
        cursor.execute("UPDATE usuarios SET user = %s WHERE id_usuario = %s", (nome_usuario, message.from_user.id))
        conn.commit()

        bot.send_message(message.chat.id, f"O nome de usuário foi alterado para '{nome_usuario}'.", reply_to_message_id=message.message_id)

    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao processar comando /setuser: {err}", reply_to_message_id=message.message_id)

    finally:
        fechar_conexao(cursor, conn)



def registrar_usuario(id_usuario, nome_usuario, username):
    try:
        conn, cursor = conectar_banco_dados()
        
        if verificar_valor_existente("id_usuario", id_usuario):
            print(f"O usuário com ID {id_usuario} já existe na tabela. Nenhum novo registro é necessário.")
            return

        query = "INSERT INTO usuarios (id_usuario, nome_usuario, nome, qntcartas, fav, cenouras, iscas) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (id_usuario,username, nome_usuario,0,0,10,10))
        conn.commit()

        print(f"Registro para o usuário com ID {id_usuario} e nome {nome_usuario} inserido com sucesso.")

    except mysql.connector.Error as err:
        print(f"Erro ao registrar usuário: {err}")

    finally:
        fechar_conexao(cursor, conn)
# Função para verificar se o usuário está registrado no grupo
def usuario_registrado_no_grupo(user_id, chat_id):
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT * FROM grupos WHERE user_id = %s AND chat_id = %s", (user_id, chat_id))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

# Função para registrar o usuário no grupo
def registrar_usuario_no_grupo(user_id, user_name, chat_id, chat_title):
    conn, cursor = conectar_banco_dados()
    cursor.execute("INSERT INTO grupos (user_id, user_name, chat_id, chat_title) VALUES (%s, %s, %s, %s)",
                   (user_id, user_name, chat_id, chat_title))
    conn.commit()
    conn.close()

# Função para registrar a mensagem privada
def registrar_mensagem_privada(user_id):
    conn, cursor = conectar_banco_dados()
    cursor.execute("INSERT INTO mensagens_privadas (user_id) VALUES (%s)", (user_id,))
    conn.commit()
    conn.close()

# Função para registrar a mensagem e o usuário no grupo
def registrar_mensagem(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.from_user.username
        chat_type = message.chat.type
        chat_title = message.chat.title if hasattr(message.chat, 'title') else None

        # Verifica se o usuário já está registrado no grupo
        if chat_type == 'group':
            if not usuario_registrado_no_grupo(user_id, chat_id):
                registrar_usuario_no_grupo(user_id, user_name, chat_id, chat_title)
        elif chat_type == 'private':
            registrar_mensagem_privada(user_id)

    except Exception as e:
        print(f"Erro ao registrar mensagem: {e}")

def registrar_valor(coluna, valor, id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        if not verificar_valor_existente("id_usuario", id_usuario):
            query = f"INSERT INTO usuarios (id_usuario, {coluna}, qntcartas, cenouras, iscas) VALUES (%s, %s, 0, 0, 0, 0)"
            conn.commit()
            print(f"Novo registro adicionado para o ID do usuário {id_usuario}")

        else:
            query = f"UPDATE usuarios SET {coluna} = %s WHERE id_usuario = %s"
            cursor.execute(query, (valor, id_usuario))
            conn.commit()
            print(f"Valor {valor} registrado na coluna {coluna} para o ID do usuário {id_usuario}")

    except mysql.connector.Error as err:
        print(f"Erro ao registrar {coluna}: {err}")

    finally:
        fechar_conexao(cursor, conn)
        
@bot.message_handler(commands=['start'])
def start_comando(message):
    user_id = message.from_user.id
    nome_usuario = message.from_user.first_name  
    username = message.chat.username
    print(f"Comando /start recebido. ID do usuário: {user_id} - {nome_usuario}")

    try:
        verificar_id_na_tabela(user_id, "ban", "iduser")
        print("novo /start ",{user_id},"-",{nome_usuario},"-",{username})

        if verificar_id_na_tabelabeta(message.from_user.id):
            registrar_usuario(user_id, nome_usuario, username)
            registrar_valor("nome_usuario", nome_usuario, user_id)
            keyboard = telebot.types.InlineKeyboardMarkup()
            image_path = "jungk.jpg"
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo,
                               caption='Seja muito bem-vindo ao MabiGarden! Entre, busque uma sombra e aproveite a estadia.',
                               reply_markup=keyboard, reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, "Ei visitante, você não foi convidado! 😡", reply_to_message_id=message.message_id)

    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido, reply_to_message_id=message.message_id)
        
@bot.message_handler(commands=['removefav'])
def remove_fav_command(message):
    id_usuario = message.from_user.id

    # Defina a coluna 'fav' como NULL para o usuário atual
    conn, cursor = conectar_banco_dados()
    cursor.execute("UPDATE usuarios SET fav = NULL WHERE id_usuario = %s", (id_usuario,))
    conn.commit()

    bot.send_message(message.chat.id, "Favorito removido com sucesso.", reply_to_message_id=message.message_id)

           
@bot.message_handler(commands=['setfav'])
def set_fav_command(message):

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2 and command_parts[1].isdigit():
        id_personagem = int(command_parts[1])
        print(id_personagem)
        id_usuario = message.from_user.id
        nome_personagem = obter_nome(id_personagem)
        print(nome_personagem)
        qtd_cartas = buscar_cartas_usuario(id_usuario, id_personagem)

        if qtd_cartas > 0:
            atualizar_coluna_usuario(id_usuario, 'fav', id_personagem)
            bot.send_message(message.chat.id, f"❤ {id_personagem} — {nome_personagem} definido como favorito.", reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, f"Você não possui {id_personagem} no seu inventário, que tal ir pescar?", reply_to_message_id=message.message_id)


@bot.message_handler(commands=['setnome'])
def set_nome_command(message):

    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) == 2:
        novo_nome = command_parts[1]
        id_usuario = message.from_user.id
        atualizar_coluna_usuario(id_usuario, 'nome', novo_nome)
        bot.send_message(message.chat.id, f"Nome atualizado para: {novo_nome}", reply_to_message_id=message.message_id)
    else:
        bot.send_message(message.chat.id,
                         "Formato incorreto. Use /setnome seguido do novo nome, por exemplo: /setnome Manoela Gavassi", reply_to_message_id=message.message_id)

@bot.message_handler(commands=['usuario'])
def obter_username_por_comando(message):
    if len(message.text.split()) == 2 and message.text.split()[1].isdigit():
        user_id = int(message.text.split()[1])
        username = obter_username_por_id(user_id)
        bot.reply_to(message, username)
    else:
        bot.reply_to(message, "Formato incorreto. Use /usuario seguido do ID desejado, por exemplo: /usuario 123")

@bot.message_handler(commands=['eu'])
def me_command(message):
    id_usuario = message.from_user.id   
    query_verificar_usuario = "SELECT COUNT(*) FROM usuarios WHERE id_usuario = %s"

    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_verificar_usuario, (id_usuario,))
        usuario_existe = cursor.fetchone()[0]  # Extrair o resultado da contagem

        if usuario_existe > 0:  # Verificar se há pelo menos um usuário com o ID fornecido
            qnt_carta(id_usuario)
            query_obter_perfil = """
                SELECT 
                    u.nome, u.nome_usuario, u.fav, u.adm, u.qntcartas, u.cenouras, u.iscas, u.bio, u.musica, u.pronome, u.privado, u.user, u.beta,
                    COALESCE(p.nome, e.nome) AS nome_fav, 
                    COALESCE(p.imagem, e.imagem) AS imagem_fav
                FROM usuarios u
                LEFT JOIN personagens p ON u.fav = p.id_personagem
                LEFT JOIN evento e ON u.fav = e.id_personagem
                WHERE u.id_usuario = %s
            """
            cursor.execute(query_obter_perfil, (id_usuario,))
            
            perfil = cursor.fetchone()

            if perfil:
                nome, nome_usuario, fav, adm, qntcartas, cenouras, iscas, bio, musica, pronome, privado, user, beta, nome_fav, imagem_fav = perfil

                resposta = f"<b>Perfil de {nome}</b>\n\n" \
                        f"✨ Fav: {fav} — {nome_fav}\n\n"
                if user == "midnightsun":
                    resposta += f"⭐️ Fã nº1 do Mabi Garden\n\n"
                if adm:
                    resposta += f"🌈 Adm: {adm.capitalize()}\n\n"
                if beta:
                    resposta += f"🍀 Usuario Beta\n\n" # Adiciona essa linha se o usuário for beta
                resposta += f"‍🧑‍🌾 Camponês: {user}\n" \
                            f"🐟 Peixes: {qntcartas}\n" \
                            f"🥕 Cenouras: {cenouras}\n" \
                            f"🪝 Iscas: {iscas}\n"

                if pronome:
                    resposta += f"🌺 Pronomes: {pronome}\n\n"

                resposta += f"✍ {bio}\n\n" \
                            f"🎧: {musica}"

                enviar_perfil(message.chat.id, resposta, imagem_fav, fav, id_usuario,message)
            else:
                bot.send_message(message.chat.id, "Perfil não encontrado.", reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, "Você ainda não iniciou o bot. Use /start para começar.", reply_to_message_id=message.message_id)

    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao verificar perfil: {err}", reply_to_message_id=message.message_id)
    finally:
        fechar_conexao(cursor, conn)

        
def enviar_perfil(chat_id, legenda, imagem_fav, fav, id_usuario,message):
    print(fav)
    gif_url = obter_gif_url(fav, id_usuario)
    if gif_url:

        if gif_url.lower().endswith(('.mp4', '.gif')):
            bot.send_animation(chat_id, gif_url, caption=legenda, parse_mode="HTML",reply_to_message_id=message.message_id)
        else:
            bot.send_photo(chat_id, gif_url, caption=legenda, parse_mode="HTML",reply_to_message_id=message.message_id)
    elif legenda:

        if imagem_fav.lower().endswith(('.jpg', '.jpeg', '.png')):
            bot.send_photo(chat_id, imagem_fav, caption=legenda, parse_mode="HTML",reply_to_message_id=message.message_id)
        elif imagem_fav.lower().endswith(('.mp4', '.gif')):
            bot.send_animation(chat_id, imagem_fav, caption=legenda, parse_mode="HTML",reply_to_message_id=message.message_id)
    else: 
        bot.send_message(chat_id, legenda, parse_mode="HTML")
        
@bot.message_handler(commands=['gperfil'])
def gperfil_command(message):
    # Verificar se o comando foi inserido corretamente
    if len(message.text.split()) != 2:
        bot.send_message(message.chat.id, "Formato incorreto. Use /gperfil seguido do nome de usuário desejado.")
        return

    # Extrair o nome de usuário do comando
    username = message.text.split()[1].strip()

    try:
        conn, cursor = conectar_banco_dados()

        # Verificar se o usuário existe na tabela
        query_verificar_usuario = "SELECT 1 FROM usuarios WHERE user = %s"
        cursor.execute(query_verificar_usuario, (username,))
        usuario_existe = cursor.fetchone()

        if usuario_existe:
            # Consultar o perfil do usuário
            query_obter_perfil = """
                SELECT 
                    u.nome, u.nome_usuario, u.fav, u.adm, u.qntcartas, u.cenouras, u.iscas, u.bio, u.musica, u.pronome, u.privado, u.beta,
                    COALESCE(p.nome, e.nome) AS nome_fav, 
                    COALESCE(p.imagem, e.imagem) AS imagem_fav
                FROM usuarios u
                LEFT JOIN personagens p ON u.fav = p.id_personagem
                LEFT JOIN evento e ON u.fav = e.id_personagem
                WHERE u.user = %s
            """
            cursor.execute(query_obter_perfil, (username,))
            perfil = cursor.fetchone()

            if perfil:
                nome, nome_usuario, fav, adm, qntcartas, cenouras, iscas, bio, musica, pronome, privado, beta, nome_fav, imagem_fav = perfil

                # Verificar se o usuário é beta
                if beta == 1:
                    usuario_beta = True
                else:
                    usuario_beta = False
                print(usuario_beta)
                # Se o perfil estiver privado, mostrar apenas a mensagem indicando que está trancado
                if privado == 1:
                    resposta = f"<b>Perfil de {username}</b>\n\n" \
                               f"✨ Fav: {fav} — {nome_fav}\n\n"
                    if usuario_beta:
                        resposta += f"🍀 Usuario Beta\n\n" # Adiciona essa linha se o usuário for beta            
                    if adm:
                        resposta += f"🌈 Adm: {adm.capitalize()}\n\n"
                    if pronome:
                        resposta += f"🌺 Pronomes: {pronome.capitalize()}\n\n" 
                          
                    resposta += f"🔒 Perfil Privado"
                else:
                    resposta = f"<b>Perfil de {nome_usuario}</b>\n\n" \
                               f"✨ Fav: {fav} — {nome_fav}\n\n" \
                      
                    if usuario_beta:
                        resposta += f"🍀 <b>Usuario Beta</b>\n\n" # Adiciona essa linha se o usuário for beta  
                               # Adicionar pronome ao perfil se estiver disponível
                    if adm:
                        resposta += f"🌈 Adm: {adm.capitalize()}\n\n"
                    if pronome:
                        resposta += f"🌺 Pronomes: {pronome.capitalize()}\n\n" \
 
                    
                    resposta += f"‍🧑‍🌾 Camponês: {nome}\n" \
                                f"🐟 Peixes: {qntcartas}\n" \
                                f"🥕 Cenouras: {cenouras}\n" \
                                f"🪝 Iscas: {iscas}\n" \
                                f"✍ {bio}\n\n" \
                                f"🎧: {musica}"

                enviar_perfil(message.chat.id, resposta, imagem_fav, fav, message.from_user.id,message)
            else:
                bot.send_message(message.chat.id, "Perfil não encontrado.")
        else:
            bot.send_message(message.chat.id, "O nome de usuário especificado não está registrado.")

    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao verificar o perfil: {err}")
    finally:
        fechar_conexao(cursor, conn)


       
def qnt_carta(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        query_atualizar_qnt_cartas = """
            UPDATE usuarios u
            SET u.qntcartas = (
                SELECT COALESCE(SUM(i.quantidade), 0)
                FROM inventario i
                WHERE i.id_usuario = %s
            )
            WHERE u.id_usuario = %s
        """
        cursor.execute(query_atualizar_qnt_cartas, (id_usuario, id_usuario))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar quantidade total de cartas do usuário: {err}")
    finally:
        fechar_conexao(cursor, conn)

@bot.callback_query_handler(func=lambda call: call.data.startswith('notificar_'))
def callback_handler(call):
    try:
        id_personagem = int(call.data.split('_')[1])
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT rodados FROM cartas WHERE id_personagem = %s", (id_personagem,))
        quantidade_personagem = cursor.fetchone()

        if quantidade_personagem is not None and quantidade_personagem[0] >= 0:
            bot.answer_callback_query(call.id, f"Esta carta foi rodada {quantidade_personagem[0]} vezes!")
        else:
            bot.answer_callback_query(call.id, f"Esta carta não foi rodada ainda :(!")
            bot.answer_callback_query(call.id, "Erro ao obter a quantidade da carta.")
    except Exception as e:
        print(f"Erro ao lidar com o callback: {e}")
    finally:
        fechar_conexao(cursor, conn)
        
def create_next_button_markup(current_index, total_count):
    markup = types.InlineKeyboardMarkup()
    button_text = f"Próximo ({current_index}/{total_count})"
    button_callback = f"next_button_{current_index}_{total_count}"
    markup.add(types.InlineKeyboardButton(text=button_text, callback_data=button_callback))
    return markup

def send_message_with_buttons(chat_id, mensagens, current_index=0):
    total_count = len(mensagens)

    if current_index < total_count:
        media_url, mensagem = mensagens[current_index]
        markup = create_next_button_markup(current_index + 1, total_count)

        if media_url:
            bot.send_photo(chat_id, media_url, caption=mensagem, reply_markup=markup)
        else:
            bot.send_message(chat_id, mensagem, reply_markup=markup)
            
        user_id = chat_id 
        save_user_state(user_id, 'gnomes', mensagens, chat_id)

    else:
        bot.send_message(chat_id, "Não há mais personagens disponíveis.")
        clear_user_state(chat_id, 'gnomes')

@bot.message_handler(commands=['config'])
def handle_config(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Pronomes', callback_data='bpronomes_')
    btn2 = types.InlineKeyboardButton('Privacidade', callback_data='privacy')
    btn_cancelar = types.InlineKeyboardButton('❌ Cancelar', callback_data='pcancelar')
    markup.add(btn1, btn2)
    markup.add(btn_cancelar)
    bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)

# Função para mostrar opções de pronome ✅
def mostrar_opcoes_pronome(chat_id, message_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    itembtn1 = types.InlineKeyboardButton('Ele/dele', callback_data='pronomes_Ele/Dele')
    itembtn2 = types.InlineKeyboardButton('Ela/dela', callback_data='pronomes_Ela/Dela')
    itembtn3 = types.InlineKeyboardButton('Elu/delu', callback_data='pronomes_Elu/Delu')
    itembtn4 = types.InlineKeyboardButton('Outros', callback_data='pronomes_Outros')
    itembtn5 = types.InlineKeyboardButton('Todos', callback_data='pronomes_Todos')
    itembtn6 = types.InlineKeyboardButton('Remover Pronome', callback_data='pronomes_remove')
    itembtn7 = types.InlineKeyboardButton('❌ Cancelar', callback_data='pcancelar')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
    markup.add(itembtn7)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Escolha o seu pronome:", reply_markup=markup)

def obter_privacidade_perfil(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        sql = "SELECT privado FROM usuarios WHERE id_usuario = %s"
        cursor.execute(sql, (id_usuario,))
        resultado = cursor.fetchone()
        
        if resultado:
            return bool(resultado[0])  # Convertendo para tipo booleano
        else:
            return False
    except Exception as e:
        print("Erro ao obter status de privacidade do perfil:", e)
        return False  # Retornar False em caso de erro


def atualizar_privacidade_perfil(id_usuario, privacidade):
    try:
        conn, cursor = conectar_banco_dados()
        sql = "UPDATE usuarios SET privado = %s WHERE id_usuario = %s"
        cursor.execute(sql, (int(privacidade), id_usuario))
        conn.commit()
        return True  
    except Exception as e:
        print("Erro ao atualizar status de privacidade do perfil:", e)
        return False 
    
def construir_mensagem_privacidade(nome_usuario, status_perfil):
    mensagem = f"Olá, {nome_usuario}. Atualmente seu perfil está: {'Trancado' if status_perfil else 'Aberto'}.\n\nDeseja trocar?"
    return mensagem

def editar_mensagem_privacidade(chat_id, message_id, nome_usuario, id_usuario, status_perfil):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if status_perfil:  # Se o perfil estiver aberto
        btn_alterar = types.InlineKeyboardButton('🔐 Abrir perfil', callback_data='open_profile')
    else:  # Se o perfil estiver fechado
        btn_alterar = types.InlineKeyboardButton('🔒 Fechar perfil', callback_data='lock_profile')

    btn_cancelar = types.InlineKeyboardButton('❌ Cancelar', callback_data='pcancelar')
    markup.add(btn_alterar, btn_cancelar)
    
    mensagem = construir_mensagem_privacidade(nome_usuario, status_perfil)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem, reply_markup=markup)
    
@bot.message_handler(commands=['gnome'])
def gnome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    conn, cursor = conectar_banco_dados()
    idmens = message.message_id
    try:
        nome = message.text.split('/gnome', 1)[1].strip()
        sql_personagens = """
            SELECT
                p.id_personagem,
                p.nome,
                p.subcategoria,
                p.categoria,
                i.quantidade AS quantidade_usuario,
                p.imagem
            FROM personagens p
            LEFT JOIN inventario i ON p.id_personagem = i.id_personagem AND i.id_usuario = %s
            WHERE p.nome LIKE %s
        """
        values_personagens = (user_id, f"%{nome}%")

        cursor.execute(sql_personagens, values_personagens)
        resultados_personagens = cursor.fetchall()
        
        if len(resultados_personagens) == 1:
            # Se houver apenas um resultado, envie a mensagem sem botões
            mensagem = resultados_personagens[0]
            id_personagem, nome, subcategoria, categoria, quantidade_usuario, imagem_url = mensagem

            mensagem = f"💌 | Personagem: \n\n<code>{id_personagem}</code> • {nome}\nde {subcategoria}"
            if quantidade_usuario is None:
                mensagem += f"\n\n🌧 | Tempo fechado..."
            elif quantidade_usuario > 0:
                mensagem += f"\n\n☀ | {quantidade_usuario}⤫"
            else:
                mensagem += f"\n\n🌧 | Tempo fechado..."

            gif_url = obter_gif_url(id_personagem, user_id)

            if gif_url:
                imagem_url = gif_url
                if imagem_url.lower().endswith(".gif"):
                    send_message_with_buttons(chat_id, idmens, [(imagem_url, mensagem)], reply_to_message_id=message.message_id)
                elif imagem_url.lower().endswith(".mp4"):
                    send_message_with_buttons(chat_id, idmens, [(imagem_url, mensagem)], reply_to_message_id=message.message_id)
                elif imagem_url.lower().endswith((".jpeg", ".jpg", ".png")):
                    send_message_with_buttons(chat_id, idmens, [(imagem_url, mensagem)], reply_to_message_id=message.message_id)
                else:
                    send_message_with_buttons(chat_id, idmens, [(None, mensagem)], reply_to_message_id=message.message_id)
            else:
                if  imagem_url.lower().endswith(".gif"):
                    send_message_with_buttons(chat_id, idmens, [(imagem_url, mensagem)], reply_to_message_id=message.message_id)
                elif imagem_url.lower().endswith(".mp4"):
                    send_message_with_buttons(chat_id, idmens, [(imagem_url, mensagem)], reply_to_message_id=message.message_id)
                elif imagem_url.lower().endswith((".jpeg", ".jpg", ".png")):
                    send_message_with_buttons(chat_id, idmens, [(imagem_url, mensagem)], reply_to_message_id=message.message_id)
                else:
                    send_message_with_buttons(chat_id, idmens, [(None, mensagem)], reply_to_message_id=message.message_id)
                
            user_id = chat_id
            save_user_state(user_id, 'gnomes', mensagem, chat_id)

        else:
            # Se houver mais de um resultado, envie a mensagem com botões
            mensagens = []
            for resultado_personagem in resultados_personagens:
                id_personagem, nome, subcategoria, categoria, quantidade_usuario, imagem_url = resultado_personagem
                mensagem = f"💌 | Personagem: \n\n<code>{id_personagem}</code> • {nome}\nde {subcategoria}"
                if quantidade_usuario is None:
                    mensagem += f"\n\n🌧 | Tempo fechado..."
                elif quantidade_usuario > 0:
                    mensagem += f"\n\n☀ | {quantidade_usuario}⤫"
                else:
                    mensagem += f"\n\n🌧 | Tempo fechado..."

                gif_url = obter_gif_url(id_personagem, user_id)
                if gif_url:
                    mensagens.append((gif_url, mensagem))
                elif imagem_url:
                    mensagens.append((imagem_url, mensagem))
                else:
                    mensagens.append((None, mensagem))

            save_user_state(user_id, 'gnomes', mensagens, chat_id)
            send_message_with_buttons(chat_id, idmens, mensagens, reply_to_message_id=message.message_id)

    except Exception as e:
        import traceback
        traceback.print_exc()

    finally:
        fechar_conexao(cursor, conn)

def create_next_button_markup(current_index, total_count):
    markup = types.InlineKeyboardMarkup()

    if current_index > 0:
        prev_button_text = f"Anterior ({current_index}/{total_count})"
        prev_button_callback = f"prev_button_{current_index}_{total_count}"
        markup.add(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))
        markup.add(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))

    if current_index < total_count - 1:
        next_button_text = f"Próximo ({current_index + 2}/{total_count})"
        next_button_callback = f"next_button_{current_index + 2}_{total_count}"
        markup.add(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))
        markup.add(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))
    return markup

def send_message_with_buttons(chat_id, idmens, mensagens, current_index=0, reply_to_message_id=None):
    total_count = len(mensagens)

    if current_index < total_count:
        media_url, mensagem = mensagens[current_index]
        markup = create_navigation_markup(current_index, total_count)

        if media_url.lower().endswith(".gif"):
            bot.send_animation(chat_id, media_url, caption=mensagem, reply_markup=markup, parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        elif media_url.lower().endswith(".mp4"):
            bot.send_video(chat_id, media_url, caption=mensagem, reply_markup=markup, parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        elif media_url.lower().endswith((".jpeg", ".jpg", ".png")):
            bot.send_photo(chat_id, media_url, caption=mensagem, reply_markup=markup, parse_mode="HTML", reply_to_message_id=reply_to_message_id)
        else:
            bot.send_message(chat_id, mensagem, reply_markup=markup, reply_to_message_id=reply_to_message_id)

        user_id = chat_id
        save_user_state(user_id, 'gnomes', mensagens, chat_id)

    else:
        bot.send_message(chat_id, "Não há mais personagens disponíveis.")
        clear_user_state(chat_id, 'gnomes')
        
def save_user_state(user_id, command, data, chat_id):
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("REPLACE INTO user_state (user_id, command, data, chat_id) VALUES (%s, %s, %s, %s)",
                       (user_id, command, json.dumps(data), chat_id))
        conn.commit()
    finally:
        fechar_conexao(cursor, conn)

def load_user_state(user_id, command):
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("SELECT data, chat_id FROM user_state WHERE user_id = %s AND command = %s", (user_id, command))
        result = cursor.fetchone()
        if result:
            data = json.loads(result[0])
            chat_id = result[1]
            return data, chat_id
        else:
            return None, None
    finally:
        fechar_conexao(cursor, conn)

def clear_user_state(user_id, command):
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("DELETE FROM user_state WHERE user_id = %s AND command = %s", (user_id, command))
        conn.commit()
    finally:
        fechar_conexao(cursor, conn)

def create_navigation_markup(current_index, total_count):
    markup = types.InlineKeyboardMarkup()
    buttons = []

    if current_index == 0:
        prev_button_text = f"⬅"
        prev_button_callback = f"prev_button_{total_count}_{total_count}"
        buttons.append(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))      
    elif current_index > 0:
        prev_button_text = f"⬅"
        prev_button_callback = f"prev_button_{current_index}_{total_count}"
        buttons.append(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))
        print(prev_button_text, prev_button_callback)
    elif current_index == total_count:
        prev_button_text = f"⬅"
        prev_button_callback = f"next_button_{current_index}_{total_count}"
        next_button_text = f"➡️"
        next_button_callback = f"next_button_{-1}_{total_count}"
        buttons.append(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))
        buttons.append(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))
        print(next_button_text, next_button_callback)
        
    if current_index < total_count - 1:
        next_button_text = f"➡️"
        next_button_callback = f"next_button_{current_index}_{total_count}"
        buttons.append(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))
        print(next_button_text, next_button_callback)
    else:
        next_button_text = f"➡️"
        next_button_callback = f"next_button_-1_{total_count}"
        buttons.append(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))
        print(next_button_text, next_button_callback)
    markup.add(*buttons)
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith(('next_button', 'prev_button')))
def navigate_messages(call):
    try:
        chat_id = call.message.chat.id
        data_parts = call.data.split('_')

        if len(data_parts) == 4 and data_parts[0] in ('next', 'prev'):
            direction, current_index, total_count = data_parts[0], int(data_parts[2]), int(data_parts[3])
        else:
            raise ValueError("Callback_data com número incorreto de partes ou formato inválido.")

        user_id = call.from_user.id
        mensagens, _ = load_user_state(user_id, 'gnomes')
        if direction == 'next':
            current_index += 1
        elif direction == 'prev':
            current_index -= 1
        media_url, mensagem = mensagens[current_index]
        markup = create_navigation_markup(current_index, len(mensagens))

        if media_url:
            if media_url.lower().endswith(".gif"):
                bot.edit_message_media(chat_id=chat_id, message_id=call.message.message_id, media=telebot.types.InputMediaAnimation(media=media_url, caption=mensagem, parse_mode="HTML"), reply_markup=markup)
            elif media_url.lower().endswith(".mp4"):
                bot.edit_message_media(chat_id=chat_id, message_id=call.message.message_id, media=telebot.types.InputMediaVideo(media=media_url, caption=mensagem, parse_mode="HTML"), reply_markup=markup)
            elif media_url.lower().endswith((".jpeg", ".jpg", ".png")):
                bot.edit_message_media(chat_id=chat_id, message_id=call.message.message_id, media=telebot.types.InputMediaPhoto(media=media_url, caption=mensagem, parse_mode="HTML"), reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mensagem, reply_markup=markup, parse_mode="HTML")
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mensagem, reply_markup=markup, parse_mode="HTML")

    except Exception as e:
        print("Erro ao processar callback dos botões de navegação:", str(e))

@bot.message_handler(commands=['gnomes'])
def gnome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    conn, cursor = conectar_banco_dados()

    try:
        nome = message.text.split('/gnomes', 1)[1].strip()
        if len(nome) <= 2:
            bot.send_message(chat_id, "Por favor, forneça um nome com mais de 3 letras.", reply_to_message_id=message.message_id)
            return
        sql_personagens = """
            SELECT
                p.emoji,
                p.id_personagem,
                p.nome,
                p.subcategoria
            FROM personagens p
            WHERE p.nome LIKE %s
        """
        values_personagens = (f"%{nome}%",)
        pesquisa = nome
        cursor.execute(sql_personagens, values_personagens)
        resultados_personagens = cursor.fetchall()

        if resultados_personagens:
            total_resultados = len(resultados_personagens)
            resultados_por_pagina = 15
            total_paginas = -(-total_resultados // resultados_por_pagina)  # Arredondamento para cima
            pagina_solicitada = 1

            if total_resultados > resultados_por_pagina:
                if len(message.text.split()) == 3 and message.text.split()[2].isdigit():
                    pagina_solicitada = min(int(message.text.split()[2]), total_paginas)
                resultados_pagina_atual = resultados_personagens[(pagina_solicitada - 1) * resultados_por_pagina : pagina_solicitada * resultados_por_pagina]
                lista_resultados = [F"{emoji} <code>{id_personagem}</code> • {nome}\nde {subcategoria}"  for emoji, id_personagem, nome, subcategoria in resultados_pagina_atual]

                mensagem_final = f"🐠 Peixes de nome', página {pagina_solicitada}/{total_paginas}:\n\n" + "\n".join(lista_resultados)
                markup = create_navigation_markup(pagina_solicitada, total_paginas)
                message = bot.send_message(chat_id, mensagem_final, reply_markup=markup, reply_to_message_id=message.message_id,parse_mode="HTML")
                
                save_state(user_id, 'gnomes', resultados_personagens, chat_id, message.message_id)
            else:
                lista_resultados = [f"{emoji} <code>{id_personagem}</code> • {nome}\nde {subcategoria}" for emoji, id_personagem, nome, subcategoria in resultados_personagens]

                mensagem_final = f"🐠 Peixes de nome '{pesquisa}':\n\n" + "\n".join(lista_resultados)
                bot.send_message(chat_id, mensagem_final, reply_to_message_id=message.message_id,parse_mode='HTML')

        else:
            bot.send_message(chat_id, f"Nenhum resultado encontrado para o nome '{nome}'.", reply_to_message_id=message.message_id)
    finally:
        fechar_conexao(cursor, conn)

def save_state(user_id, command, data, chat_id, message_id):
    conn, cursor = conectar_banco_dados()

    try:
        cursor.execute("REPLACE INTO user_state (user_id, command, data, chat_id, message_id) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, command, json.dumps(data), chat_id, message_id))
        conn.commit()
    finally:
        fechar_conexao(cursor, conn)
        
load_state = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith(('prox_button', 'ant_button')))
def navigate_gnome_results(call):
    try:
        chat_id = call.message.chat.id
        data_parts = call.data.split('_')

        if len(data_parts) == 4 and data_parts[0] in ('prox', 'ant'):
            direction, current_page, total_pages = data_parts[0], int(data_parts[2]), int(data_parts[3])
        else:
            raise ValueError("Callback_data com número incorreto de partes ou formato inválido.")

        user_id = call.from_user.id
        resultados, _, message_id = load_state(user_id, 'gnomes')
        if direction == 'prox':
            current_page = min(current_page + 1, total_pages)
        elif direction == 'ant':
            current_page = max(current_page - 1, 1)
            
        resultados_pagina_atual = resultados[(current_page - 1) * 15 : current_page * 15]
        lista_resultados = [f"{emoji} - {id_personagem} - {nome} de {subcategoria}" for emoji, id_personagem, nome, subcategoria in resultados_pagina_atual]
        mensagem_final = f"🐠 Peixes de nome', página {current_page}/{total_pages}:\n\n" + "\n".join(lista_resultados)
        markup = create_navegacao_markup(current_page, total_pages)

        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem_final, reply_markup=markup)

    except Exception as e:
        print("Erro ao processar callback dos botões de navegação:", str(e))

def create_navegacao_markup(pagina_atual, total_paginas):
    markup = types.InlineKeyboardMarkup()
    if pagina_atual > 1:
        prev_button_text = f"< Anterior"
        prev_button_callback = f"prev_button_{pagina_atual - 1}_{total_paginas}"
        markup.add(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))

    if pagina_atual < total_paginas:
        next_button_text = f"Próximo >"
        next_button_callback = f"next_button_{pagina_atual + 1}_{total_paginas}"
        markup.add(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))
    return markup

@bot.message_handler(commands=['gid'])
def obter_id_e_enviar_info_com_imagem(message):
    conn, cursor = conectar_banco_dados()
    user_id = message.from_user.id
    chat_id = message.chat.id

    command_parts = message.text.split()
    if len(command_parts) == 2 and command_parts[1].isdigit():
        id_pesquisa = command_parts[1]

        is_evento = verificar_evento(cursor, id_pesquisa)

        if is_evento:
            sql_evento = """
                SELECT
                    e.id_personagem,
                    e.nome,
                    e.subcategoria,
                    e.categoria,
                    i.quantidade AS quantidade_usuario,
                    e.imagem
                FROM evento e
                LEFT JOIN inventario i ON e.id_personagem = i.id_personagem AND i.id_usuario = %s
                WHERE e.id_personagem = %s
            """
            values_evento = (message.from_user.id, id_pesquisa)

            cursor.execute(sql_evento, values_evento)
            resultado_evento = cursor.fetchone()

            if resultado_evento:
                id_personagem, nome, subcategoria, categoria, quantidade_usuario, imagem_url = resultado_evento

                mensagem = f"💌 | Personagem: \n\n{id_personagem} • {nome}\nde {subcategoria}"

                if quantidade_usuario == None:
                    mensagem += f"\n\n🌧 | Tempo fechado..."
                elif quantidade_usuario == 1:
                    mensagem += f"\n\n{'☀  '}"
                else:
                    mensagem += f"\n\n{'☀ 𖡩'}"

                try:
                    if imagem_url.lower().endswith(('.jpg', '.jpeg', '.png')):
                        bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=mensagem, reply_to_message_id=message.message_id)
                    elif imagem_url.lower().endswith(('.mp4', '.gif')):
                        bot.send_video(chat_id=message.chat.id, video=imagem_url, caption=mensagem, reply_to_message_id=message.message_id)
                except Exception as e:
                    bot.send_message(chat_id, mensagem, reply_to_message_id=message.message_id)
            else:
                bot.send_message(chat_id, f"Nenhum resultado encontrado para o ID '{id_pesquisa}'.", reply_to_message_id=message.message_id)

        else:
            sql_normal = """
                SELECT
                    p.id_personagem,
                    p.nome,
                    p.subcategoria,
                    p.categoria,
                    i.quantidade AS quantidade_usuario,
                    p.imagem,
                    p.cr
                FROM personagens p
                LEFT JOIN inventario i ON p.id_personagem = i.id_personagem AND i.id_usuario = %s
                WHERE p.id_personagem = %s
            """
            values_normal = (message.from_user.id, id_pesquisa)

            cursor.execute(sql_normal, values_normal)
            resultado_normal = cursor.fetchone()

            if resultado_normal:
                id_personagem, nome, subcategoria, categoria, quantidade_usuario, imagem_url, cr = resultado_normal

                mensagem = f"💌 | Personagem: \n\n{id_personagem} • {nome}\nde {subcategoria}"

                if quantidade_usuario is not None and quantidade_usuario > 0:
                    mensagem += f"\n\n☀ | {quantidade_usuario}⤫"
                else:
                    mensagem += f"\n\n🌧 | Tempo fechado..."

                # Verificar se a coluna cr não está nula
                if cr:
                    link_cr = obter_link_formatado(cr)
                    mensagem += f"\n\n{link_cr}"

                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(InlineKeyboardButton("💟", callback_data=f"total_{id_pesquisa}"))

                gif_url = obter_gif_url(id_personagem, user_id)
                if gif_url:
                    imagem_url = gif_url
                    if  imagem_url.lower().endswith(".gif"):
                        bot.send_video(chat_id=message.chat.id, video=imagem_url, caption=mensagem, reply_markup=markup, reply_to_message_id=message.message_id,parse_mode="HTML")
                    elif imagem_url.lower().endswith(".mp4"):
                        bot.send_video(chat_id=message.chat.id, video=imagem_url, caption=mensagem, reply_markup=markup, reply_to_message_id=message.message_id,parse_mode="HTML")
                    elif imagem_url.lower().endswith((".jpeg", ".jpg", ".png")):
                        bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=mensagem, reply_markup=markup, reply_to_message_id=message.message_id,parse_mode="HTML")
                    else:
                        bot.send_message(chat_id, mensagem)
                else:
                    if  imagem_url.lower().endswith(".gif"):
                        bot.send_video(chat_id=message.chat.id, video=imagem_url, caption=mensagem, reply_markup=markup, reply_to_message_id=message.message_id,parse_mode="HTML")
                    elif imagem_url.lower().endswith(".mp4"):
                        bot.send_video(chat_id=message.chat.id, video=imagem_url, caption=mensagem, reply_markup=markup, reply_to_message_id=message.message_id,parse_mode="HTML")
                    elif imagem_url.lower().endswith((".jpeg", ".jpg", ".png")):
                        bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=mensagem, reply_markup=markup, reply_to_message_id=message.message_id,parse_mode="HTML")
                    else:
                        bot.send_message(chat_id, mensagem) 
            else:
                bot.send_message(chat_id, f"Nenhum resultado encontrado para o ID '{id_pesquisa}'.", reply_to_message_id=message.message_id)
    else:
        bot.send_message(chat_id, "Formato incorreto. Use /gid seguido do ID desejado, por exemplo: /gid 123", reply_to_message_id=message.message_id)

def gerar_id_unico():
    if "ultimo_id" not in user_data:
        user_data["ultimo_id"] = 0
    user_data["ultimo_id"] += 1
    return user_data["ultimo_id"]

user_data = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith(('vai_', 'vem_')))
def callback_paginacao(call):
    try:
        print("4")
        conn, cursor = conectar_banco_dados()
        dados = call.data.split("_")
        modo = dados[1]
        pagina_atual = int(dados[2])
        total_paginas = int(dados[3])
        mensagem_id = dados[4]
        subcategoria = "_".join(dados[5:-1])
        id_usuario = int(dados[-1])
        
        if call.data.startswith("vem_"):
            pagina_atual -= 1
        elif call.data.startswith("vai_"):
            pagina_atual += 1
        
        resultados_pagina = obter_resultados_pagina(subcategoria, pagina_atual, id_usuario) if modo == 's' else obter_resultados_faltante(subcategoria, pagina_atual, id_usuario)
        
        mensagem = construir_mensagem(resultados_pagina, subcategoria, id_usuario, modo)
        
        enviar_resultados_pagina(call.message.chat.id, call.message.message_id, mensagem, pagina_atual, total_paginas, subcategoria, id_usuario, modo)

    except Exception as e:
        import traceback
        traceback.print_exc()

@bot.callback_query_handler(func=lambda call: call.data.startswith(('vaic_', 'vemc_')))
def callback_paginacao_c(call):
    try:
        conn, cursor = conectar_banco_dados()
        dados = call.data.split("_")
        modo = "c"  
        pagina_atual = int(dados[1])
        total_paginas = int(dados[3])
        categoria = (dados[4]) 
        id_usuario = int(dados[-1])
        if call.data.startswith("vemc_"):
            pagina_atual -= 1
        elif call.data.startswith("vaic_"):
            pagina_atual += 1
        print("passo4 ")
        resultados_pagina = obter_resultados_pagina_c(categoria, pagina_atual, id_usuario)
        mensagem = construir_mensagem_cesta_c(resultados_pagina, categoria, id_usuario, modo)
        enviar_resultados_pagina_c(call.message.chat.id, call.message.message_id, mensagem, pagina_atual, total_paginas, categoria, id_usuario, modo)

    except Exception as e:
        import traceback
        traceback.print_exc()        
# Definir o número máximo de cartas por página
cartas_por_pagina = 15       
@bot.message_handler(commands=['cesta'])
def cesta_command(message):
    try:
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        print("Usuário não está banido. Pode acessar a cesta.")
        conn, cursor = conectar_banco_dados()
        qnt_carta(message.from_user.id)
        id_usuario = message.from_user.id
        user = message.from_user
        usuario = user.first_name
        subcategoria = message.text.split('/cesta ', 1)[1].strip().lower() if len(message.text.split('/cesta ', 1)) > 1 else None
        print(subcategoria)
        
        if subcategoria:
            if message.text.startswith('/cesta s'):
                resposta_completa = comando_cesta_s(id_usuario, subcategoria, cursor)
                paginas_registradas = registrar_cartas(id_usuario, subcategoria, resposta_completa, modo='s')
                print("Total de páginas registradas:", paginas_registradas)
                if paginas_registradas >= 2:
                    subcategoria_pesquisada, lista = resposta_completa
                    foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
                    if foto_subcategoria:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        enviar_mensagem_inicial(message.chat.id, resposta, paginas_registradas, subcategoria_pesquisada, id_usuario,message)
                    else:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        enviar_mensagem_inicial(message.chat.id, resposta, paginas_registradas, subcategoria_pesquisada, id_usuario,message)
                else:
                    subcategoria_pesquisada, lista = resposta_completa
                    foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
                    if foto_subcategoria:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        bot.send_photo(message.chat.id, foto_subcategoria, caption=resposta, reply_to_message_id=message.message_id)
                    else:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        bot.send_message(message.chat.id, resposta, reply_to_message_id=message.message_id)

            elif message.text.startswith('/cesta f') or message.text.startswith('/cesta fn'):
                try:
                    conn, cursor = conectar_banco_dados()
                    # Obter o ID do usuário
                    id_usuario = message.from_user.id
                    mensagem = message.message_id
                    # Extrair a subcategoria do comando
                    subcategoria = message.text.split(' ', 1)[1].strip().title()
                    print(subcategoria)
                    
                    # Chamar a função comando_cesta_f para obter os resultados
                    resultados, subcategoria_pesquisada = comando_cesta_f(id_usuario, subcategoria, cursor)

                    if isinstance(resultados, list) and resultados:
                        # Armazenar os resultados na página inicial (1)
                        user_pages[id_usuario] = {
                            'cartas': resultados,
                            'subcategoria': subcategoria_pesquisada,
                            'pagina_atual': 1,
                            'mensagem_id': None  # Para armazenar o ID da mensagem enviada
                        }

                        # Enviar a mensagem da primeira página
                        send_initial_message(id_usuario, message) 

                    else:
                        # Se não foram encontradas cartas, enviar a resposta como mensagem simples
                        bot.send_message(message.chat.id, resultados,reply_to_message_id=id_usuario)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                finally:
                    fechar_conexao(cursor, conn)


        elif message.text.startswith('/cesta c'):
                # Comando /cesta c
                print("chegou")
                resposta_completa = comando_cesta_cs(id_usuario, subcategoria, cursor)
                if isinstance(resposta_completa, tuple):
                    categoria_pesquisada, lista = resposta_completa
                    paginas_registradas = registrar_categorias(id_usuario, categoria_pesquisada, resposta_completa, cursor)
                    print("Total de páginas de categorias registradas:", paginas_registradas)
                    if paginas_registradas >= 2:
                        print("passo 1")
                        enviar_mensagem_inicial_cesta_c(message.chat.id, lista, paginas_registradas, categoria_pesquisada, id_usuario)
                    else:
                        bot.send_message(message.chat.id, lista, reply_to_message_id=message.message_id)
                else:
                    bot.send_message(message.chat.id, resposta_completa, reply_to_message_id=message.message_id)
            

    except Exception as e:
        import traceback
        traceback.print_exc()
        
        if verificar_id_na_tabela(message.from_user.id, "ban", "iduser"):
            mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
            bot.send_message(message.chat.id, mensagem_banido,reply_to_message_id=message.message_id)
        else:
            mensagem = "Um erro ocorreu."
            bot.send_message(message.chat.id, mensagem,reply_to_message_id=message.message_id)
    finally:
        fechar_conexao(cursor, conn)
        
# Função para calcular o número total de páginas com base no número de cartas
def total_paginas(cartas):
    return (len(cartas) + cartas_por_pagina - 1) // cartas_por_pagina

def send_initial_message(id_usuario, message):
    try:
        conn, cursor = conectar_banco_dados()
        subcategoria = message.text.split(' ', 1)[1].strip().title()
        
        # Chamar a função comando_cesta_f para obter os resultados
        resultados, subcategoria_pesquisada = comando_cesta_f(id_usuario, subcategoria, cursor)

        if isinstance(resultados, list) and resultados:
            # Armazenar os resultados na página inicial (1) para este usuário e subcategoria
            if id_usuario not in user_pages:
                user_pages[id_usuario] = {}
            user_pages[id_usuario][subcategoria_pesquisada] = {
                'cartas': resultados,
                'pagina_atual': 1,
                'mensagem_id': None  # Para armazenar o ID da mensagem enviada
            }

            # Enviar a mensagem da primeira página
            send_cartas_message(id_usuario, subcategoria_pesquisada, message)

        else:
            # Se não foram encontradas cartas, enviar a resposta como mensagem simples
            bot.send_message(message.chat.id, resultados, reply_to_message_id=message.message_id)
    
    except Exception as e:
        print(f"Erro ao processar o comando: {e}")
    finally:
        fechar_conexao(cursor, conn)

def send_cartas_message(id_usuario, subcategoria_pesquisada, message):
    try:
        conn, cursor = conectar_banco_dados()

        if id_usuario in user_pages and subcategoria_pesquisada in user_pages[id_usuario]:
            user_data = user_pages[id_usuario][subcategoria_pesquisada]
            cartas = user_data['cartas']
            pagina_atual = user_data['pagina_atual']
            mensagem_id = user_data['mensagem_id']
            nome_usuario = obter_nome_do_usuario(id_usuario)
            
            inicio = (pagina_atual - 1) * cartas_por_pagina
            fim = inicio + cartas_por_pagina
            cartas_pagina = cartas[inicio:fim]

            # Formatar os resultados para exibição
            cartas_formatadas = []
            for carta in cartas_pagina:
                cartas_formatadas.append(f"{carta['emoji']} {carta['id']} - {carta['nome']}")

            # Construir a mensagem com estilo
            mensagem_construida = f"🧺 | Cartas de {subcategoria_pesquisada} faltantes na cesta de {nome_usuario}:\n\n"
            if cartas_formatadas:
                mensagem_construida += '\n'.join(cartas_formatadas)
            else:
                mensagem_construida += "Nenhuma carta encontrada."

            # Adicionar informação de paginação
            total_pages = total_paginas(cartas)
            markup = None  # Inicializar markup como None

            if total_pages > 1:
                mensagem_construida += f"\n\nPágina {pagina_atual}/{total_pages}"

                # Criar os botões inline para navegação
                markup = telebot.types.InlineKeyboardMarkup()
                btn_ver_mais = telebot.types.InlineKeyboardButton('⬅️', callback_data=f'cestafvoltar_{subcategoria_pesquisada}')
                btn_outra_acao = telebot.types.InlineKeyboardButton('➡️', callback_data=f'cestafir_{subcategoria_pesquisada}')
                markup.row(btn_ver_mais, btn_outra_acao)

            # Verificar se há uma foto associada à subcategoria
            foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
            if foto_subcategoria:
                if mensagem_id:
                    # Editar a legenda da foto existente
                    bot.edit_message_caption(chat_id=message.chat.id, message_id=mensagem_id, caption=mensagem_construida, reply_markup=markup, parse_mode="HTML")
                else:
                    # Enviar a foto com legenda como uma nova mensagem no grupo original
                    sent_message = bot.send_photo(chat_id=message.chat.id, photo=foto_subcategoria, caption=mensagem_construida, reply_markup=markup, parse_mode="HTML", reply_to_message_id=message.message_id)
                    user_pages[id_usuario][subcategoria_pesquisada]['mensagem_id'] = sent_message.message_id
            else:
                if mensagem_id:
                    # Editar a mensagem existente
                    bot.edit_message_text(chat_id=message.chat.id, message_id=mensagem_id, text=mensagem_construida, reply_markup=markup, parse_mode="HTML")
                else:
                    # Enviar uma nova mensagem de texto no grupo original
                    sent_message = bot.send_message(chat_id=message.chat.id, text=mensagem_construida, reply_markup=markup, parse_mode="HTML", reply_to_message_id=message.message_id)
                    user_pages[id_usuario][subcategoria_pesquisada]['mensagem_id'] = sent_message.message_id
        else:
            # Caso ocorra algum problema ou usuário não tenha página definida
            bot.send_message(chat_id=id_usuario, text="Desculpe, ocorreu um erro ao processar a sua solicitação.")

    except Exception as e:
        print(f"Erro ao enviar/editar mensagem: {e}")
    finally:
        fechar_conexao(cursor, conn)
        
# Manipulador para o comando /seeds
@bot.message_handler(commands=['seeds'])
def seeds_command(message):
    # Verificar se o comando foi enviado corretamente com um argumento
    if len(message.text.split()) != 2:
        bot.reply_to(message, "Formato incorreto. Use /seeds id_personagem")
        return

    # Extrair o ID do personagem a partir do comando
    try:
        id_personagem = int(message.text.split()[1])
    except ValueError:
        bot.reply_to(message, "ID do personagem inválido. Use um número inteiro.")
        return

    # Extrair o ID do usuário do objeto message
    id_usuario = message.from_user.id

    try:
        conn, cursor = conectar_banco_dados()

        # Verificar se o usuário já está inscrito neste cativeiro para este personagem
        query_verificar_inscricao = """
            SELECT id_usuario
            FROM seeds
            WHERE id_usuario = %s AND id_personagem = %s
        """
        cursor.execute(query_verificar_inscricao, (id_usuario, id_personagem))
        existing_inscricao = cursor.fetchone()

        if existing_inscricao:
            bot.reply_to(message, "Você já está inscrito neste cativeiro para este personagem.")
            return

        # Consultar a quantidade de cartas que o usuário possui desse personagem na tabela inventario
        query_quantidade_cartas = """
            SELECT quantidade
            FROM inventario
            WHERE id_usuario = %s AND id_personagem = %s
        """
        cursor.execute(query_quantidade_cartas, (id_usuario, id_personagem))
        resultado_quantidade = cursor.fetchone()

        if resultado_quantidade:
            qnt_cartas = resultado_quantidade[0]
        else:
            qnt_cartas = 0  # Definir como 0 se não houver registros na tabela inventario

        # Registrar informações na tabela seeds
        query_registrar_seed = """
            INSERT INTO seeds (id_usuario, id_personagem, qnt_cartas, limite_atual)
            VALUES (%s, %s, %s, 100)  # Definir limites iniciais
        """
        cursor.execute(query_registrar_seed, (id_usuario, id_personagem, qnt_cartas))

        # Verificar se o cativeiro já existe para o id_personagem
        query_verificar_cativeiro = """
            SELECT qntcativeiros
            FROM cativeiro
            WHERE id_personagem = %s
        """
        cursor.execute(query_verificar_cativeiro, (id_personagem,))
        existing_cativeiro = cursor.fetchone()

        if existing_cativeiro:
            # Cativeiro já existe, então atualize a quantidade
            quantidade_atual = existing_cativeiro[0]
            nova_quantidade = quantidade_atual + 1

            query_atualizar_cativeiro = """
                UPDATE cativeiro
                SET qntcativeiros = %s
                WHERE id_personagem = %s
            """
            cursor.execute(query_atualizar_cativeiro, (nova_quantidade, id_personagem))
        else:
            # Cativeiro não existe, então insira um novo registro
            query_adicionar_cativeiro = """
                INSERT INTO cativeiro (id_personagem, qntcativeiros,limite)
                VALUES (%s, 1,100)
            """
            cursor.execute(query_adicionar_cativeiro, (id_personagem,))


        # Commit da transação no banco de dados
        conn.commit()

        # Responder ao usuário com uma mensagem de confirmação
        bot.reply_to(message, f"Registro na tabela seeds realizado com sucesso para o personagem {id_personagem}!")

    except mysql.connector.Error as e:
        bot.reply_to(message, f"Erro ao processar comando: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def obter_historico_trocas(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta SQL para obter as últimas 10 trocas do usuário
        query_obter_historico = """
            SELECT id_usuario1, id_usuario2, id_carta_usuario1, id_carta_usuario2, aceita
            FROM historico_trocas
            WHERE id_usuario1 = %s
            ORDER BY id DESC
            LIMIT 10
        """
        cursor.execute(query_obter_historico, (id_usuario,))
        historico = cursor.fetchall()

        if historico:
            return historico
        else:
            return []

    except mysql.connector.Error as e:
        print(f"Erro ao obter histórico de trocas: {e}")
        return []

    finally:
        fechar_conexao(cursor, conn)

def obter_historico_pescas(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta SQL para obter as últimas 10 pescas do usuário
        query_obter_historico = """
            SELECT id_carta, data_hora
            FROM historico_cartas_giradas
            WHERE id_usuario = %s
            ORDER BY data_hora DESC
            LIMIT 10
        """
        cursor.execute(query_obter_historico, (id_usuario,))
        historico = cursor.fetchall()

        if historico:
            return historico
        else:
            return []

    except mysql.connector.Error as e:
        print(f"Erro ao obter histórico de pescas: {e}")
        return []

    finally:
        fechar_conexao(cursor, conn)

# Manipulador para o comando /hist
@bot.message_handler(commands=['hist'])
def command_historico(message):
    id_usuario = message.chat.id  # Obtém o ID do usuário a partir da mensagem recebida
    tipo_historico = message.text.split()[-1].lower()  # Obtém o tipo de histórico do comando

    if tipo_historico == 'troca':
        historico = obter_historico_trocas(id_usuario)
        if historico:
            historico_mensagem = "🤝 | Seu histórico de trocas:\n\n"
            for troca in historico:
                id_usuario1, id_usuario2, carta1, carta2, aceita = troca
                carta1 = obter_nome(carta1)
                carta2 = obter_nome(carta2)
                nome1 = obter_nome_usuario_por_id(id_usuario1)
                nome2 = obter_nome_usuario_por_id(id_usuario2)
                status = "✅" if aceita else "⛔️"
                mensagem = f"ꕤ Troca entre {nome1} e {nome2}:\n{carta1} e {carta2} - {status}\n\n"
                historico_mensagem += mensagem

            # Envia a mensagem com o histórico de trocas para o usuário
            bot.send_message(id_usuario, historico_mensagem)
        else:
            # Envia uma mensagem se nenhum histórico de trocas foi encontrado
            bot.send_message(id_usuario, "Nenhuma troca encontrada para este usuário.")

    elif tipo_historico == 'pesca':
        historico = obter_historico_pescas(id_usuario)
        if historico:
            historico_mensagem = "🎣 | Seu histórico de pescas:\n\n"
            for pesca in historico:
                id_carta, data_hora = pesca
                carta1 = obter_nome(id_carta)
                data_formatada = datetime.strftime(data_hora, "%d/%m/%Y - %H:%M")
                mensagem = f"✦ Carta: {id_carta} → {carta1}\nPescada em: {data_formatada}\n\n"
                historico_mensagem += mensagem

            # Envia a mensagem com o histórico de pescas para o usuário
            bot.send_message(id_usuario, historico_mensagem)
        else:
            # Envia uma mensagem se nenhum histórico de pescas foi encontrado
            bot.send_message(id_usuario, "Nenhuma pesca encontrada para este usuário.")

 # Função para obter o nome de usuário por ID de usuário
def user(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta para buscar o nome de usuário pelo ID de usuário
        query_obter_user = "SELECT user FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query_obter_user, (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            nome_usuario = resultado[0]
            return nome_usuario
        else:
            return "Usuário não encontrado"  # Retornar uma mensagem de erro ou padrão

    except mysql.connector.Error as e:
        print(f"Erro ao obter o nome de usuário: {e}")
        return None  # Retornar None ou outra indicação de erro

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Manipulador para o comando /cativeiro
@bot.message_handler(commands=['cativeiro'])
def cativeiro_command(message):
    # Verificar se o comando foi enviado corretamente com um argumento
    if len(message.text.split()) != 2:
        bot.reply_to(message, "Formato incorreto. Use /cativeiro id_personagem")
        return

    # Extrair o ID do personagem a partir do comando
    try:
        id_personagem = int(message.text.split()[1])
    except ValueError:
        bot.reply_to(message, "ID do personagem inválido. Use um número inteiro.")
        return

    try:
        conn, cursor = conectar_banco_dados()

        # Consultar a lista de usuários associados ao cativeiro (id_personagem)
        query_consultar_cativeiro = """
            SELECT s.id_usuario, s.qnt_cartas
            FROM seeds s
            WHERE s.id_personagem = %s
        """
        cursor.execute(query_consultar_cativeiro, (id_personagem,))
        usuarios_cativeiro = cursor.fetchall()
        nome_personagem = obter_nome(id_personagem)
        limite = verifica_limite_cativeiro(id_personagem)
        if usuarios_cativeiro:
            # Construir a lista de usuários formatada
            resposta = f"🍊| Lista de usuários no cativeiro de <b>{id_personagem}</b> — <b> {nome_personagem}</b>:\n\n"
            for usuario_id, quantidade in usuarios_cativeiro:
                username = user(usuario_id)
                quantidade_faltante = (limite - quantidade)  # Calcular quantidade faltante até o limite
                resposta += f"🌿 <b>{username}</b> ⭑ <i>quantidade faltante:</i> {quantidade_faltante}\n"

            # Responder ao usuário com a lista de usuários formatada
            bot.reply_to(message, resposta, parse_mode='HTML')
        else:
            bot.reply_to(message, f"Nenhum usuário encontrado para o cativeiro (id_personagem {id_personagem}).")

    except mysql.connector.Error as e:
        bot.reply_to(message, f"Erro ao processar comando: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
   

def verificar_e_atualizar_limites(message):
    try:
        conn, cursor = conectar_banco_dados()
        chat_id = message.chat.id
        # Consultar todos os id_personagem na tabela cativeiro
        cursor.execute("SELECT DISTINCT id_personagem FROM cativeiro")
        id_personagens = cursor.fetchall()

        for id_personagem in id_personagens:
            id_personagem = id_personagem[0]

            # Consultar a quantidade total de registros na tabela seeds para este id_personagem
            cursor.execute("SELECT COUNT(*) FROM seeds WHERE id_personagem = %s", (id_personagem,))
            total_registros = cursor.fetchone()[0]

            # Calcular a metade da quantidade total
            metade_total = total_registros // 2

            # Consultar a quantidade de registros na tabela seeds que atingiram ou ultrapassaram o limite atual
            cursor.execute("SELECT COUNT(*) FROM seeds WHERE id_personagem = %s AND qnt_cartas >= limite_atual", (id_personagem,))
            usuarios_com_limite = cursor.fetchone()[0]

            # Verificar se a metade dos usuários atingiu ou ultrapassou o limite atual
            if usuarios_com_limite >= metade_total:
                # Consultar o limite atual na tabela cativeiro
                cursor.execute("SELECT limite FROM cativeiro WHERE id_personagem = %s", (id_personagem,))
                limite_atual = cursor.fetchone()[0]

                # Dobrar o limite atual
                novo_limite = limite_atual * 2

                # Atualizar o limite na tabela cativeiro
                cursor.execute("UPDATE cativeiro SET limite = %s WHERE id_personagem = %s", (novo_limite, id_personagem))

                # Enviar mensagem informando sobre o aumento do limite
                bot.send_message(chat_id, f"O limite de cativeiros para o personagem {id_personagem} foi aumentado para {novo_limite}.")

        # Commit da transação no banco de dados
        conn.commit()

    except mysql.connector.Error as e:
        print(f"Erro ao verificar e atualizar os limites: {e}")

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()


# Handler para os callbacks dos botões inline específicos
@bot.callback_query_handler(func=lambda call: call.data.startswith('cestafvoltar_') or call.data.startswith('cestafir_'))
def handle_pagination_buttons(call):
    try:
        id_usuario = call.from_user.id
        callback_data = call.data
        _, subcategoria_pesquisada = callback_data.split('_')

        if id_usuario in user_pages and subcategoria_pesquisada in user_pages[id_usuario]:
            user_data = user_pages[id_usuario][subcategoria_pesquisada]
            cartas = user_data['cartas']
            pagina_atual = user_data['pagina_atual']

            if callback_data.startswith('cestafvoltar'):
                # Voltar para a página anterior
                user_pages[id_usuario][subcategoria_pesquisada]['pagina_atual'] = max(1, pagina_atual - 1)
            elif callback_data.startswith('cestafir'):
                # Avançar para a próxima página
                total_pages = total_paginas(cartas)
                user_pages[id_usuario][subcategoria_pesquisada]['pagina_atual'] = min(total_pages, pagina_atual + 1)

            # Enviar ou editar a mensagem com base na página atual atualizada
            send_cartas_message(id_usuario, subcategoria_pesquisada, call.message)

            bot.answer_callback_query(call.id)

    except Exception as e:
        print(f"Erro ao processar callback: {e}")



# Função para mostrar a primeira página de IDs de usuário e nomes de personagens associados a uma determinada tag
def mostrar_primeira_pagina_tag(message, nometag, id_usuario):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta SQL para contar o número total de registros
        query_total = "SELECT COUNT(id_personagem) FROM tags WHERE nometag = %s"
        cursor.execute(query_total, (nometag,))
        total_registros = cursor.fetchone()[0]

        # Calcular o número total de páginas
        total_paginas = (total_registros // 10) + (1 if total_registros % 10 > 0 else 0)

        # Verificar se há registros
        if total_registros == 0:
            bot.reply_to(message, f"Nenhum registro encontrado para a tag '{nometag}'.")
            return

        # Consulta SQL para recuperar os registros da primeira página
        query = "SELECT id_personagem FROM tags WHERE nometag = %s LIMIT 10"
        cursor.execute(query, (nometag,))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Cartas na tag {nometag}:\n\n"
            for resultado in resultados:
                id_personagem = resultado[0]
                
                # Consultar informações da carta na tabela personagens
                cursor.execute("SELECT emoji, nome FROM personagens WHERE id_personagem = %s", (id_personagem,))
                carta_info_personagens = cursor.fetchone()

                # Consultar informações da carta na tabela evento
                cursor.execute("SELECT emoji, nome FROM evento WHERE id_personagem = %s", (id_personagem,))
                carta_info_evento = cursor.fetchone()

                # Verificar qual consulta retornou dados
                if carta_info_personagens:
                    emoji, nome = carta_info_personagens
                elif carta_info_evento:
                    emoji, nome = carta_info_evento
                else:
                    # Carta não encontrada
                    resposta += f"ℹ️ | Carta não encontrada para ID: {id_personagem}\n"
                    continue
                
                # Verificar se a carta está no inventário do usuário
                emoji_status = '☀️' if inventario_existe(id_usuario, id_personagem) else '🌧️'

                # Adicionar carta à resposta
                resposta += f"{emoji_status} | {emoji} ⭑ {id_personagem} - {nome}\n"

            # Enviar mensagem
            markup = None
            if total_paginas > 1:
                markup = criar_markup_tag(1, total_paginas, nometag)
            resposta += f"\nPágina 1/{total_paginas}"
            bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.reply_to(message, f"Nenhum registro encontrado para a tag '{nometag}'.")

    except Exception as e:
        print(f"Erro ao processar comando /tag: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")



# Função para editar a mensagem com a página correspondente
def editar_mensagem_tag(message, nometag, pagina_atual, id_usuario, total_paginas):
    try:
        conn, cursor = conectar_banco_dados()
        # Consulta SQL para recuperar os registros da página atual
        offset = (pagina_atual - 1) * 10
        query = "SELECT id_personagem FROM tags WHERE nometag = %s LIMIT 10 OFFSET %s"
        cursor.execute(query, (nometag, offset))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Cartas na tag {nometag}:\n\n"
            for resultado in resultados:
                id_personagem = resultado[0]
                
                # Consultar informações da carta na tabela personagens
                cursor.execute("SELECT emoji, nome FROM personagens WHERE id_personagem = %s", (id_personagem,))
                carta_info_personagens = cursor.fetchone()

                # Consultar informações da carta na tabela evento
                cursor.execute("SELECT emoji, nome FROM evento WHERE id_personagem = %s", (id_personagem,))
                carta_info_evento = cursor.fetchone()

                # Verificar qual consulta retornou dados
                if carta_info_personagens:
                    emoji, nome = carta_info_personagens
                elif carta_info_evento:
                    emoji, nome = carta_info_evento
                else:
                    # Carta não encontrada
                    resposta += f"ℹ️ | Carta não encontrada para ID: {id_personagem}\n"
                    continue
                
                # Verificar se a carta está no inventário do usuário
                emoji_status = '☀️' if inventario_existe(id_usuario, id_personagem) else '🌧️'

                # Adicionar carta à resposta
                resposta += f"{emoji_status} | {emoji} ⭑ {id_personagem} - {nome}\n"

            # Enviar mensagem
            markup = None
            if int(total_paginas) > 1:
                markup = criar_markup_tag(pagina_atual, total_paginas, nometag)
            resposta += f"\nPágina {pagina_atual}/{total_paginas}"
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.reply_to(message, f"Nenhum registro encontrado para a tag '{nometag}'.")

    except Exception as e:
        print(f"Erro ao editar mensagem de tag: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")

# Função para criar os botões de página para navegação entre os resultados
def criar_markup_tag(pagina_atual, total_paginas, nometag):
    markup = telebot.types.InlineKeyboardMarkup()

    # Botões na mesma linha
    btn_anterior = telebot.types.InlineKeyboardButton("⬅️", callback_data=f"tag_{pagina_atual-1}_{nometag}_{total_paginas}")
    btn_proxima = telebot.types.InlineKeyboardButton("➡️", callback_data=f"tag_{pagina_atual+1}_{nometag}_{total_paginas}")
    markup.row(btn_anterior, btn_proxima)

    return markup

# Função para lidar com o entrada de comando /tag
@bot.message_handler(commands=['tag'])
def verificar_comando_tag(message):
    try:
        parametros = message.text.split(' ', 1)[1:]  # Obtém os parâmetros do comando

        # Se não houver parâmetros, solicita o nome da tag
        if not parametros:
            bot.reply_to(message, "Por favor, forneça o nome da tag.")
            return

        nometag = parametros[0]  # Obtém o nome da tag fornecido
        id_usuario = message.from_user.id
        # Mostrar os IDs de usuário e os nomes de personagens associados à tag
        mostrar_primeira_pagina_tag(message, nometag,id_usuario)

    except Exception as e:
        print(f"Erro ao processar comando /tag: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")


@bot.message_handler(commands=['addtag'])
def adicionar_tag(message):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = message.from_user.id
        args = message.text.split(maxsplit=1)
        
        if len(args) == 2:
            tag_info = args[1]
            tag_parts = tag_info.split('|')
            
            if len(tag_parts) == 2:
                ids_personagens_str = tag_parts[0].strip()
                nometag = tag_parts[1].strip()
                
                # Verificar se há IDs de personagens e a tag não está vazia
                if ids_personagens_str and nometag:
                    ids_personagens = [id_personagem.strip() for id_personagem in ids_personagens_str.split(',')]
                    
                    # Verificar se cada ID de personagem existe na tabela 'personagens' ou 'evento'
                    valid_ids = []
                    invalid_ids = []
                    
                    for id_personagem in ids_personagens:
                        cursor.execute("SELECT COUNT(*) FROM personagens WHERE id_personagem = %s", (id_personagem,))
                        count_personagens = cursor.fetchone()[0]
                        
                        cursor.execute("SELECT COUNT(*) FROM evento WHERE id_personagem = %s", (id_personagem,))
                        count_evento = cursor.fetchone()[0]
                        
                        if count_personagens > 0 or count_evento > 0:
                            valid_ids.append(id_personagem)
                        else:
                            invalid_ids.append(id_personagem)
                    
                    if valid_ids:
                        # Inserir os IDs de personagem e a tag na tabela 'tags'
                        for id_personagem in valid_ids:
                            cursor.execute("INSERT INTO tags (id_usuario, id_personagem, nometag) VALUES (%s, %s, %s)",
                                           (id_usuario, id_personagem, nometag))
                            conn.commit()
                        
                        bot.reply_to(message, f"Tag '{nometag}' adicionada com sucesso.")
                    else:
                        bot.reply_to(message, "Nenhum ID de personagem válido encontrado.")
                else:
                    bot.reply_to(message, "Formato incorreto. Use /addtag id1,id2,... | nometag")
            else:
                bot.reply_to(message, "Formato incorreto. Use /addtag id1,id2,... | nometag")
        else:
            bot.reply_to(message, "Formato incorreto. Use /addtag id1,id2,... | nometag")
    
    except mysql.connector.Error as err:
        print(f"Erro de MySQL: {err}")
        bot.reply_to(message, "Ocorreu um erro ao processar a operação no banco de dados.")
    
    except Exception as e:
        print(f"Erro ao adicionar tag: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar a operação.")
    
    finally:
        fechar_conexao(cursor, conn)



@bot.message_handler(commands=['deltag'])
def deletar_tag(message):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = message.from_user.id
        args = message.text.split(maxsplit=1)
        
        print(f"id_usuario: {id_usuario}")
        print(f"args: {args}")
        
        if len(args) == 2:
            tag_info = args[1].strip()
            print(f"tag_info: {tag_info}")
            
            # Verificar se o comando inclui uma lista de IDs e uma tag
            if '|' in tag_info:
                id_list, nometag = [part.strip() for part in tag_info.split('|')]
                ids_personagens = [id.strip() for id in id_list.split(',')]
                
                print(f"ids_personagens: {ids_personagens}")
                print(f"nometag: {nometag}")
                
                # Verificar se os IDs estão associados à tag para o usuário
                for id_personagem in ids_personagens:
                    cursor.execute("SELECT idtags FROM tags WHERE id_usuario = %s AND id_personagem = %s AND nometag = %s",
                                   (id_usuario, id_personagem, nometag))
                    tag_existente = cursor.fetchone()
                    
                    if tag_existente:
                        idtag = tag_existente[0]
                        cursor.execute("DELETE FROM tags WHERE idtags = %s", (idtag,))
                        conn.commit()
                        bot.reply_to(message, f"ID {id_personagem} removido da tag '{nometag}' com sucesso.")
                    else:
                        bot.reply_to(message, f"O ID {id_personagem} não está associado à tag '{nometag}'.")
            
            else:
                # Apenas o nome da tag foi fornecido para exclusão completa
                nometag = tag_info.strip()
                cursor.execute("DELETE FROM tags WHERE id_usuario = %s AND nometag = %s", (id_usuario, nometag))
                conn.commit()
                bot.reply_to(message, f"A tag '{nometag}' foi removida completamente.")
        
        else:
            bot.reply_to(message, "Formato incorreto. Use /deltag id1, id2, id3 | nometag para remover IDs específicos da tag ou /deltag nometag para remover a tag inteira.")

    except Exception as e:
        print(f"Erro ao deletar tag: {e}")
    finally:
        fechar_conexao(cursor, conn)


def criar_lista_paginas(personagens_ids_quantidade, items_por_pagina):
    paginas = []
    pagina_atual = []
    for i, (personagem_id, quantidade) in enumerate(personagens_ids_quantidade.items(), start=1):
        personagem = get_personagem_by_id(personagem_id)
        if personagem:
            emoji = personagem['emoji']
            card_id = personagem['id']
            name = personagem['nome']
            if quantidade > 1:
                item = f"{emoji} <code>{card_id}</code>. <b>{name}</b> ({int(quantidade)}x)"
            else:
                item = f"{emoji} <code>{card_id}</code>. <b>{name}</b>"
            pagina_atual.append(item)

            if len(pagina_atual) == items_por_pagina or i == len(personagens_ids_quantidade):
                paginas.append(pagina_atual)
                pagina_atual = []

    return paginas

@bot.message_handler(commands=['sub'])
def handle_sub_command(message):
    try:
        _, sub_command, sub_name = message.text.split()
        sub_name = sub_name.lower()
    except ValueError:
        bot.reply_to(message, "Por favor, use o formato correto: /sub [s|f] [subobra]")
        return

    if sub_command == 's':
        handle_sub_s(message, sub_name)
    elif sub_command == 'f':
        handle_sub_f(message, sub_name)
    else:
        bot.reply_to(message, "Comando inválido. Use '/sub s' ou '/sub f' para mostrar os personagens desta subobra.")

def handle_sub_s(message, sub_name):
    subcategoria = get_subcategoria_by_name(sub_name)
    if not subcategoria:
        bot.reply_to(message, "Subobra não encontrada.")
        return

    id_subcategoria = subcategoria['id_subcategoria']
    user_id = message.from_user.id

    personagens_ids_quantidade = get_personagens_ids_quantidade_por_subcategoria_s(id_subcategoria, user_id)

    if not personagens_ids_quantidade:
        response = f"Você não possui nenhum personagem de {subcategoria['nomesub']}."
        bot.reply_to(message, response)
        return

    total_personagens = len(personagens_ids_quantidade)
    total_subobra = get_total_personagens_subobra(id_subcategoria)

    items_por_pagina = 1
    paginas = criar_lista_paginas(personagens_ids_quantidade, items_por_pagina)

    for i, pagina in enumerate(paginas, start=1):
        response = f"💌 | <b>{subcategoria['nomesub']}</b>\n⏱️ | ({total_personagens}/{total_subobra}) - Página {i}\n\n"
        response += '\n'.join(pagina)
        bot.send_photo(message.chat.id, subcategoria['imagem'], caption=response, parse_mode='HTML')

def handle_sub_f(message, sub_name):
    subcategoria = get_subcategoria_by_name(sub_name)
    if not subcategoria:
        bot.reply_to(message, "Subobra não encontrada.")
        return

    id_subcategoria = subcategoria['id_subcategoria']
    user_id = message.from_user.id

    personagens_ids_quantidade = get_personagens_ids_quantidade_por_subcategoria_f(id_subcategoria, user_id)

    if not personagens_ids_quantidade:
        response = f"Você já possui todos os personagens de {subcategoria['nomesub']}."
        bot.reply_to(message, response)
        return

    total_personagens = len(personagens_ids_quantidade)
    total_subobra = get_total_personagens_subobra(id_subcategoria)

    items_por_pagina = 1
    paginas = criar_lista_paginas(personagens_ids_quantidade, items_por_pagina)

    for i, pagina in enumerate(paginas, start=1):
        response = f"💌 | <b>{subcategoria['nomesub']}</b>\n⏱️ | ({total_personagens}/{total_subobra}) - Página {i}\n\n"
        response += '\n'.join(pagina)
        bot.send_photo(message.chat.id, subcategoria['imagem'], caption=response, parse_mode='HTML')
def get_personagens_ids_quantidade_por_subcategoria_s(id_subcategoria, user_id):
    query = """
    SELECT aps.id_personagem, SUM(inv.quantidade) as quantidade
    FROM associacao_pessoa_subcategoria aps
    LEFT JOIN inventario inv ON aps.id_personagem = inv.id_personagem AND inv.id_usuario = %s
    WHERE aps.id_subcategoria = %s
    AND (inv.id_personagem IS NOT NULL AND inv.quantidade > 0)
    GROUP BY aps.id_personagem
    """
    cursor.execute(query, (user_id, id_subcategoria))
    return {row[0]: row[1] for row in cursor.fetchall()}

def get_personagens_ids_por_subcategoria_f(id_subcategoria, user_id):
    query = """
    SELECT aps.id_personagem
    FROM associacao_pessoa_subcategoria aps
    LEFT JOIN inventario inv ON aps.id_personagem = inv.id_personagem AND inv.id_usuario = %s
    WHERE aps.id_subcategoria = %s
    AND (inv.id_personagem IS NULL OR inv.quantidade = 0)
    """
    cursor.execute(query, (user_id, id_subcategoria))
    return [row[0] for row in cursor.fetchall()]

def get_subcategoria_by_name(sub_name):
    query = "SELECT * FROM subcategorias WHERE nomesub = %s"
    cursor.execute(query, (sub_name,))
    result = cursor.fetchone()
    if result:
        return {
            'id_subcategoria': result[0],
            'nomesub': result[1],
            'imagem': result[3]
        }
    return None

def get_personagem_by_id(id_personagem):
    query = "SELECT * FROM cartas WHERE id = %s"
    cursor.execute(query, (id_personagem,))
    result = cursor.fetchone()
    if result:
        return {
            'id': result[0],
            'nome': result[1],
            'subcategoria': result[2],
            'emoji': result[3],
            'categoria': result[4],
            'imagem': result[5]
        }
    return None

def get_inventario_do_usuario_por_personagem(user_id, personagem_id):
    query = "SELECT * FROM inventario WHERE id_usuario = %s AND id_personagem = %s"
    cursor.execute(query, (user_id, personagem_id))
    row = cursor.fetchone()
    if row:
        return {'quantidade': row[3]}
    return None

def get_total_personagens_subobra(id_subcategoria):
    query = "SELECT COUNT(*) FROM associacao_pessoa_subcategoria WHERE id_subcategoria = %s"
    cursor.execute(query, (id_subcategoria,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return 0

def get_personagens_ids_quantidade_por_subcategoria_f(id_subcategoria, user_id):
    query = """
    SELECT aps.id_personagem, SUM(inv.quantidade) as quantidade
    FROM associacao_pessoa_subcategoria aps
    LEFT JOIN inventario inv ON aps.id_personagem = inv.id_personagem AND inv.id_usuario = %s
    WHERE aps.id_subcategoria = %s
    AND (inv.id_personagem IS NULL OR inv.quantidade = 0)
    GROUP BY aps.id_personagem
    """
    cursor.execute(query, (user_id, id_subcategoria))
    return {row[0]: row[1] for row in cursor.fetchall()}

@bot.message_handler(commands=['apoiar'])
def doacao(message):
    markup = telebot.types.InlineKeyboardMarkup()
    chave_pix = "80388add-294e-4075-8cd5-8765cc9f9be0"
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text="Link do apoia.se 🌟", url="https://apoia.se/garden"))
    mensagem = f"👨🏻‍🌾 Oi, jardineiro! Se está vendo esta mensagem, significa que está interessado em nos ajudar, certo? A equipe MabiGarden fica muito feliz em saber que nosso trabalho o agradou e o motivou a nos ajudar! \n\nCaso deseje contribuir com PIX, a chave é: <code>{chave_pix}</code> (clique na chave para copiar automaticamente) \n\nSe preferir, pode usar a plataforma apoia-se no botão abaixo!"
    bot.send_message(message.chat.id, mensagem, reply_markup=markup, parse_mode="HTML", reply_to_message_id=message.message_id)

@bot.message_handler(commands=['gift'])
def handle_gift_cards(message):
    conn, cursor = conectar_banco_dados()
    if message.from_user.id != 1112853187:
        bot.reply_to(message, "Você não é a Hashi para usar esse comando.")
        return
    try:
        _, quantity, card_id, user_id = message.text.split()
        quantity = int(quantity)
        card_id = int(card_id)
        user_id = int(user_id)
    except (ValueError, IndexError):
        bot.reply_to(message, "Por favor, use o formato correto: /gift quantidade card_id user_id")
        return
    gift_cards(quantity, card_id, user_id)
    bot.reply_to(message, f"{quantity} cartas adicionadas com sucesso!")

def gift_cards(quantity, card_id, user_id):

    conn, cursor = conectar_banco_dados()
    query = "SELECT * FROM inventario WHERE id_personagem = %s AND id_usuario = %s"
    cursor.execute(query, (card_id, user_id))
    existing_card = cursor.fetchone()
    print(quantity)
    if existing_card:
        new_quantity = int(existing_card[3]) + int(quantity)
        print(new_quantity)
        update_query = "UPDATE inventario SET quantidade = %s WHERE id_personagem = %s AND id_usuario = %s"
        cursor.execute(update_query, (new_quantity, card_id, user_id))
    else:
        insert_query = "INSERT INTO inventario (id_personagem, id_usuario, quantidade) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (card_id, user_id,quantity))

    update_total_query = "UPDATE personagens SET total = total + 1 WHERE id_personagem = %s"
    cursor.execute(update_total_query, (card_id,))
    conn.commit()
def update_total_personagem(id_personagem, quantidade):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("UPDATE personagens SET total = total - %s WHERE id_personagem = %s", (quantidade, id_personagem))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar o total na tabela personagens: {err}")
    finally:
        fechar_conexao(cursor, conn)

def cenourar_carta(message, id_usuario, id_personagens, sim=True):
    try:
        conn, cursor = conectar_banco_dados()
        mensagem_cenoura = f"Cenourando carta:\n"
        cartas_cenouradas = []

        for id_personagem in id_personagens.split(","):
            id_personagem = id_personagem.strip()
            cursor.execute(
                "SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                (id_usuario, id_personagem))
            quantidade_atual = cursor.fetchone()

            if quantidade_atual is not None and quantidade_atual[0] > 0:
                quantidade_atual = int(quantidade_atual[0])
                cursor.execute(
                    "SELECT cenouras FROM usuarios WHERE id_usuario = %s",
                    (id_usuario,))
                cenouras = int(cursor.fetchone()[0])

                if quantidade_atual >= 1:
                    nova_quantidade = quantidade_atual - 1
                    novas_cenouras = cenouras + 1
                    cursor.execute(
                        "UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s",
                        (nova_quantidade, id_usuario, id_personagem))
                    cursor.execute(
                        "UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s",
                        (novas_cenouras, id_usuario))

                    cartas_cenouradas.append((id_personagem, nova_quantidade))
                    mensagem_cenoura += f"{id_personagem}\n"
                    update_total_personagem(id_personagem, 1) 
                    conn.commit()

            else:
                mensagem_erro = f"Erro ao processar a cenoura. A carta {id_personagem} não foi encontrada no inventário."
                bot.send_message(message.chat.id, mensagem_erro)

        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=mensagem_cenoura)
        mensagem_consolidada = "Cartas cenouradas com sucesso:\n"
        for carta, nova_quantidade in cartas_cenouradas:
            mensagem_consolidada += f"{carta} - Nova quantidade: {nova_quantidade}\n"
        bot.send_message(message.chat.id, mensagem_consolidada)
    except Exception as e:
        print(f"Erro ao processar cenoura: {e}")
    finally:
        fechar_conexao(cursor, conn)
@bot.callback_query_handler(func=lambda call: call.data.startswith('total_'))
def callback_total_personagem(call):
    conn, cursor = conectar_banco_dados()
    chat_id = call.message.chat.id

    id_pesquisa = call.data.split('_')[1]

    sql_total = "SELECT total FROM personagens WHERE id_personagem = %s"
    cursor.execute(sql_total, (id_pesquisa,))
    total_pescados = cursor.fetchone()

    if total_pescados is not None and total_pescados[0] is not None:
        if total_pescados[0] > 1:
            bot.answer_callback_query(call.id, text=f"O personagem foi pescado {total_pescados[0]} vezes!", show_alert=True)
        elif total_pescados[0] == 1:
            bot.answer_callback_query(call.id, text=f"O personagem foi pescado {total_pescados[0]} vez!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, text="Esse personagem ainda não foi pescado :(", show_alert=True)
    else:
        bot.answer_callback_query(call.id, text="Esse personagem ainda não foi pescado :(", show_alert=True)
        
@bot.message_handler(commands=['rev'])
def handle_rev_cards(message):
    if message.from_user.id != 1112853187:
        bot.reply_to(message, "Você não é a Maria para usar esse comando.")
        return
    try:
        _, quantity, card_id, user_id = message.text.split()
        quantity = int(quantity)
        card_id = int(card_id)
        user_id = int(user_id)
    except (ValueError, IndexError):
        bot.reply_to(message, "Por favor, use o formato correto: /rev quantidade card_id user_id")
        return
    success = rev_cards(message, quantity, card_id, user_id)
    if success:
        bot.reply_to(message, f"{quantity} cartas removidas com sucesso!")

def rev_cards(message, quantity, card_id, user_id):
    for _ in range(quantity):
        query = "SELECT * FROM inventario WHERE id_personagem = %s AND id_usuario = %s"
        cursor.execute(query, (card_id, user_id))
        existing_card = cursor.fetchone()

        if existing_card and int(existing_card[3]) > 0:
            new_quantity = int(existing_card[3]) - 1
            update_query = "UPDATE inventario SET quantidade = %s WHERE id_personagem = %s AND id_usuario = %s"
            cursor.execute(update_query, (new_quantity, card_id, user_id))
        else:
            bot.reply_to(message, f"O usuário {user_id} não tem cartas suficientes do ID {card_id} para remover.")
            return False

        update_total_query = "UPDATE cartas SET total = total - 1 WHERE id = %s"
        cursor.execute(update_total_query, (card_id,))

    conn.commit()
    return True


@bot.message_handler(commands=['armazém', 'armazem', 'amz'])
def armazem_command(message):
    try:
        id_usuario = message.from_user.id
        usuario = message.from_user.first_name
        verificar_id_na_tabela(id_usuario, "ban", "iduser")
        
        conn, cursor = conectar_banco_dados()
        qnt_carta(id_usuario)
        armazem_info[id_usuario] = {'id_usuario': id_usuario, 'usuario': usuario}
        pagina = 1
        resultados_por_pagina = 15
        
        # Consulta para verificar se há um favorito definido para o usuário
        query_fav_usuario = f"""
            SELECT fav
            FROM usuarios
            WHERE id_usuario = {id_usuario}
        """
        cursor.execute(query_fav_usuario)
        resultado_fav_usuario = cursor.fetchone()

        if resultado_fav_usuario and resultado_fav_usuario[0] is not None:
            # Se houver um favorito definido, tratamos conforme a lógica anterior
            id_fav_usuario = resultado_fav_usuario[0]

            # Consulta para obter a imagem associada ao favorito
            query_imagem_fav = f"""
                SELECT id_personagem, imagem
                FROM personagens
                WHERE id_personagem = '{id_fav_usuario}'
            """
            cursor.execute(query_imagem_fav)
            resultado_imagem_fav = cursor.fetchone()

            if resultado_imagem_fav and resultado_imagem_fav[1]:
                id_carta_fav, imagem_fav = resultado_imagem_fav
                print(id_carta_fav)
                # Montar a resposta com o favorito e enviar a foto com os botões de paginação
                nome_fav = obter_nome_carta(id_usuario)
                resposta = f"💌 | Cartas no armazém de {usuario}:\n\n❤️ Fav: {nome_fav}\n\n"

                sql = f"""
                    SELECT id_personagem, emoji, nome_personagem, subcategoria, quantidade, categoria
                    FROM (
                        SELECT i.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, i.quantidade, p.categoria
                        FROM inventario i
                        JOIN personagens p ON i.id_personagem = p.id_personagem
                        WHERE i.id_usuario = {id_usuario} AND i.quantidade > 0

                        UNION

                        SELECT e.id_personagem, '🪴' AS emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria
                        FROM evento e
                        WHERE e.id_personagem IN (
                            SELECT id_personagem
                            FROM inventario
                            WHERE id_usuario = {id_usuario} AND quantidade > 0
                        )
                    ) AS combined
                    ORDER BY CASE WHEN categoria = 'evento' THEN 0 ELSE 1 END, categoria, subcategoria, id_personagem ASC
                    LIMIT {15}
                """
                cursor.execute(sql)
                resultados = cursor.fetchall()

                if resultados:
                    markup = telebot.types.InlineKeyboardMarkup()
                    buttons_row = [
                        telebot.types.InlineKeyboardButton("⏪️", callback_data=f"armazem_primeira_{pagina}_{id_usuario}"),
                        telebot.types.InlineKeyboardButton("◀️", callback_data=f"armazem_anterior_{pagina}_{id_usuario}"),
                        telebot.types.InlineKeyboardButton("▶️", callback_data=f"armazem_proxima_{pagina}_{id_usuario}"),
                        telebot.types.InlineKeyboardButton("⏩️", callback_data=f"armazem_ultima_{pagina}_{id_usuario}")
                    ]
                    markup.row(*buttons_row)

                    for carta in resultados:
                        id_carta, emoji_carta, nome_carta, subcategoria_carta, quantidade_carta, categoria_carta = carta
                        quantidade_carta = int(quantidade_carta) if quantidade_carta is not None else 0

                        # Lógica para determinar a letra de quantidade
                        if quantidade_carta == 1:
                            letra_quantidade = ""
                        elif 2 <= quantidade_carta <= 4:
                            letra_quantidade = "🌾"
                        elif 5 <= quantidade_carta <= 9:
                            letra_quantidade = "🌼"
                        elif 10 <= quantidade_carta <= 19:
                            letra_quantidade = "☀️"
                        elif 20 <= quantidade_carta <= 29:
                            letra_quantidade = "🍯️"
                        elif 30 <= quantidade_carta <= 39:
                            letra_quantidade = "🐝"
                        elif 40 <= quantidade_carta <= 49:
                            letra_quantidade = "🌻"
                        elif 50 <= quantidade_carta <= 100:
                            letra_quantidade = "👑"
                        elif 101 <= quantidade_carta:
                            letra_quantidade = "👑"    
                        else:
                            letra_quantidade = ""

                        resposta += f" {emoji_carta} <code>{id_carta}</code> • {nome_carta} - {subcategoria_carta} {letra_quantidade}\n"

                    quantidade_total_cartas = obter_quantidade_total_cartas(id_usuario)
                    total_paginas = (quantidade_total_cartas + resultados_por_pagina - 1) // resultados_por_pagina
                    resposta += f"\n{pagina}/{total_paginas}"
                    gif_url = obter_gif_url(id_carta_fav, id_usuario)
                    print("gif",gif_url)
                    if gif_url:
                        bot.send_animation(
                            chat_id=message.chat.id,
                            animation=gif_url,
                            caption=resposta,
                            reply_to_message_id=message.message_id,
                            reply_markup=markup,
                            parse_mode="HTML"
                        )
                    else:
                        bot.send_photo(
                            chat_id=message.chat.id,
                            photo=imagem_fav,
                            caption=resposta,
                            reply_to_message_id=message.message_id,
                            reply_markup=markup,
                            parse_mode="HTML"
                        )
                return  # Sai da função após enviar a foto do favorito

        # Se não houver favorito definido ou imagem associada ao favorito, continuar com cartas aleatórias
        resposta = f"💌 | Cartas no armazém de {usuario}:\n\n"

        # Montar a consulta SQL para buscar as cartas no armazém
        sql = f"""
            SELECT id_personagem, emoji, nome_personagem, subcategoria, quantidade, categoria
            FROM (
                -- Consulta para cartas no inventário do usuário
                SELECT i.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, i.quantidade, p.categoria
                FROM inventario i
                JOIN personagens p ON i.id_personagem = p.id_personagem
                WHERE i.id_usuario = {id_usuario} AND i.quantidade > 0

                UNION ALL

                -- Consulta para cartas de evento que o usuário possui
                SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria
                FROM evento e
                WHERE e.id_personagem IN (
                    SELECT id_personagem
                    FROM inventario
                    WHERE id_usuario = {id_usuario} AND quantidade > 0
                )
            ) AS combined
            ORDER BY CASE WHEN categoria = 'evento' THEN 0 ELSE 1 END, categoria, subcategoria, id_personagem ASC
            LIMIT {resultados_por_pagina} OFFSET {(pagina - 1) * resultados_por_pagina}
        """
        cursor.execute(sql)
        resultados = cursor.fetchall()

        if resultados:
            markup = telebot.types.InlineKeyboardMarkup()
            buttons_row = [
                telebot.types.InlineKeyboardButton("⏪️", callback_data=f"armazem_primeira_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("◀️", callback_data=f"armazem_anterior_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("▶️", callback_data=f"armazem_proxima_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("⏩️", callback_data=f"armazem_ultima_{pagina}_{id_usuario}")
            ]
            markup.row(*buttons_row)

            for carta in resultados:
                id_carta, emoji_carta, nome_carta, subcategoria_carta, quantidade_carta, categoria_carta = carta
                quantidade_carta = int(quantidade_carta) if quantidade_carta is not None else 0

                if quantidade_carta == 1:
                    letra_quantidade = ""
                elif 2 <= quantidade_carta <= 4:
                    letra_quantidade = "🌾"
                elif 5 <= quantidade_carta <= 9:
                    letra_quantidade = "🌼"
                elif 10 <= quantidade_carta <= 19:
                    letra_quantidade = "☀️"
                elif 20 <= quantidade_carta <= 29:
                    letra_quantidade = "🍯️"
                elif 30 <= quantidade_carta <= 39:
                    letra_quantidade = "🐝"
                elif 40 <= quantidade_carta <= 49:
                    letra_quantidade = "🌻"
                elif 50 <= quantidade_carta <= 100:
                    letra_quantidade = "👑"
                elif 101 <= quantidade_carta:
                    letra_quantidade = "👑"    
                else:
                    letra_quantidade = ""

                resposta += f" {emoji_carta} <code>{id_carta}</code> • {nome_carta} - {subcategoria_carta} {letra_quantidade}\n"

            quantidade_total_cartas = obter_quantidade_total_cartas(id_usuario)
            total_paginas = (quantidade_total_cartas + resultados_por_pagina - 1) // resultados_por_pagina
            resposta += f"\n{pagina}/{total_paginas}"
            
            carta_aleatoria = random.choice(resultados)
            id_carta_aleatoria, emoji_carta_aleatoria, _, _, _, _ = carta_aleatoria
            foto_carta_aleatoria = obter_url_imagem_por_id(id_carta_aleatoria)
            if foto_carta_aleatoria:
                bot.send_photo(chat_id=message.chat.id, photo=foto_carta_aleatoria, caption=resposta, reply_to_message_id=message.message_id, reply_markup=markup, parse_mode="HTML")
            else:       
                bot.send_message(
                    chat_id=message.chat.id,
                    text=resposta,
                    reply_to_message_id=message.message_id,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text="Você não possui cartas no armazém.",
                reply_to_message_id=message.message_id
            )

    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a consulta no banco de dados.")
    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)
    except telebot.apihelper.ApiHTTPException as e:
        print(f"Erro na API do Telegram: {e}")
    finally:
        fechar_conexao(cursor, conn)


@bot.callback_query_handler(func=lambda call: call.data.startswith(('armazem_anterior_', 'armazem_proxima_','armazem_ultima_','armazem_primeira_')))
def callback_paginacao_armazem(call):
    try:
        conn, cursor = conectar_banco_dados()
        chat_id = call.message.chat.id
        _, direcao, pagina_str, id_usuario = call.data.split('_')
        pagina = int(pagina_str)
        info_armazem = armazem_info.get(int(id_usuario), {})
        id_usuario = info_armazem.get('id_usuario', '')
        usuario = info_armazem.get('usuario', '')
        resultados_por_pagina = 15
        offset = (pagina - 1) * resultados_por_pagina

        quantidade_total_cartas = obter_quantidade_total_cartas(id_usuario)
        total_paginas = quantidade_total_cartas // resultados_por_pagina + 1
        limite = resultados_por_pagina

        if pagina == 1 and call.data.startswith("armazem_anterior_"):
            print("Indo para a última página")
            pagina = total_paginas
            offset = (pagina - 1) * resultados_por_pagina
            limite = quantidade_total_cartas % resultados_por_pagina or resultados_por_pagina

        elif pagina == total_paginas and call.data.startswith("armazem_proxima_"):
            print("Indo para a primeira página")
            pagina = 1
            offset = 0
            limite = min(quantidade_total_cartas, resultados_por_pagina)

        else:
            if call.data.startswith("armazem_anterior_"):
                print("Indo para a página anterior")
                pagina -= 1
            elif call.data.startswith("armazem_ultima_"):
                print("Indo para a última página")
                pagina = total_paginas
            elif call.data.startswith("armazem_primeira_"):
                print("Indo para a primeira página")
                pagina = 1
            elif call.data.startswith("armazem_proxima_"):
                print("Indo para a próxima página")
                pagina += 1
            offset = (pagina - 1) * resultados_por_pagina

            
        sql = f"""
            SELECT id_personagem, emoji, nome_personagem, subcategoria, quantidade, categoria
            FROM (
                SELECT i.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, i.quantidade, p.categoria
                FROM inventario i
                JOIN personagens p ON i.id_personagem = p.id_personagem
                WHERE i.id_usuario = {id_usuario} AND i.quantidade > 0

                UNION

                SELECT e.id_personagem, '🪴' AS emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria
                FROM evento e
                WHERE e.id_personagem IN (
                    SELECT id_personagem
                    FROM inventario
                    WHERE id_usuario = {id_usuario} AND quantidade > 0
                )
            ) AS combined
            ORDER BY CASE WHEN categoria = 'evento' THEN 0 ELSE 1 END, categoria, subcategoria, id_personagem ASC
            LIMIT {limite} OFFSET {offset}
        """
        cursor.execute(sql)
        resultados = cursor.fetchall()
        if resultados:
            markup = telebot.types.InlineKeyboardMarkup()
            if quantidade_total_cartas > 10:
                buttons_row = [
                    telebot.types.InlineKeyboardButton("⏪️", callback_data=f"armazem_primeira_{pagina}_{id_usuario}"),
                    telebot.types.InlineKeyboardButton("◀️", callback_data=f"armazem_anterior_{pagina}_{id_usuario}"),
                    telebot.types.InlineKeyboardButton("▶️", callback_data=f"armazem_proxima_{pagina}_{id_usuario}"),
                    telebot.types.InlineKeyboardButton("⏩️", callback_data=f"armazem_ultima_{pagina}_{id_usuario}")
                ]
                markup.row(*buttons_row)

            nome_fav = obter_nome_carta(id_usuario)
            resposta = f"💌 | Cartas no armazém de {usuario}:\n\n❤️ Fav: {nome_fav}\n\n"

            for carta in resultados:
                id_carta = carta[0]
                emoji_carta = carta[1]
                nome_carta = carta[2]
                subcategoria_carta = carta[3]
                quantidade_carta = carta[4]

                if quantidade_carta is None:
                    quantidade_carta = 0
                else:
                    quantidade_carta = int(quantidade_carta)

                if quantidade_carta == 1:
                    letra_quantidade = ""
                elif 2 <= quantidade_carta <= 4:
                    letra_quantidade = "🌾"
                elif 5 <= quantidade_carta <= 9:
                    letra_quantidade = "🌼"
                elif 10 <= quantidade_carta <= 19:
                    letra_quantidade = "☀️"
                elif 20 <= quantidade_carta <= 29:
                    letra_quantidade = "🍯️"
                elif 30 <= quantidade_carta <= 39:
                    letra_quantidade = "🐝"
                elif 40 <= quantidade_carta <= 49:
                    letra_quantidade = "🌻"
                elif 50 <= quantidade_carta <= 100:
                    letra_quantidade = "👑"
                elif 101 <= quantidade_carta:
                    letra_quantidade = "👑"    
                else:
                    letra_quantidade = ""

                resposta += f" {emoji_carta} <code>{id_carta}</code> • {nome_carta} - {subcategoria_carta} {letra_quantidade}\n"

            resposta += f"\n{pagina}/{total_paginas}"
            bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption=resposta, reply_markup=markup, parse_mode="HTML")

        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Nenhuma carta encontrada.")
    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        print("Callback detectado:", call.data)
        message = call.message
        conn, cursor = conectar_banco_dados()
        chat_id = call.message.chat.id

        if call.message:
            chat_id = call.message.chat.id
            if not verificar_tempo_passado(chat_id):
                print(
                    f"Tempo insuficiente passado desde a última interação para o chat ID {chat_id}. Ignorando callback.")
                return
            else:
                ultima_interacao[chat_id] = datetime.now()

            if call.data.startswith('pescar_'):
                categoria_callback(call)
            elif call.data.startswith("subcategory_"):
                    subcategory_data = call.data.split("_")
                    subcategory = subcategory_data[1]
                    is_valentine = len(subcategory_data) > 2 and subcategory_data[2] == "valentine"

                    if is_valentine:
                        card = get_random_card_valentine(subcategory)
                    else:
                        categoria_handler(call.message, categoria)
                    print(card)
                    if card:
                        emoji = "🎁"
                        card_id = card['id_personagem']
                        name = card['nome']
                        subcategoria = card['subcategoria']
                        image_link = card['imagem']
                        user_id = call.from_user.id
                        evento_aleatorio = card
                        print(evento_aleatorio)
                        send_card_message(message, evento_aleatorio, cursor=cursor, conn=conn)
                    else:
                        bot.reply_to(call.message, "Desculpe, não foi possível encontrar uma carta para essa subcategoria.")


            elif call.data.startswith('choose_subcategoria_'):
                subcategoria = call.data.replace('choose_subcategoria_', '')
                choose_subcategoria_callback(call, subcategoria, cursor, conn)
            elif call.data.startswith('loja_geral'):
                loja_geral_callback(call)
            elif call.data.startswith('img'): 
                dados = call.data.split('_')
                print(dados)
                pagina = int(dados[-2])
                subcategoria = dados[-1]
                callback_img_peixes(call,pagina,subcategoria)
            elif call.data.startswith('peixes'):
                dados = call.data.split('_')
                pagina = int(dados[-2])
                subcategoria = dados[-1]
                print(subcategoria)
                print(pagina)
                pagina_peixes_callback(call, pagina, subcategoria)
            elif call.data.startswith("geral_compra_"):
                geral_compra_callback(call)
            elif call.data.startswith('tag_'):
                callback_pagina_tag(call)
            elif call.data.startswith('confirmar_iscas'):
                message_id = call.message.message_id
                confirmar_iscas(call,message_id)
            elif call.data.startswith('doar_cenoura'):
                message_id = call.message.message_id
                doar_cenoura(call,message_id)    
            elif call.data.startswith('loja_compras'):
                message_data = call.data.replace('loja_', '')
                print(message_data)
                if message_data:
                    try:

                        conn, cursor = conectar_banco_dados()
                        id_usuario = call.from_user.id
                        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                        result = cursor.fetchone()

                        imagem_url = 'https://telegra.ph/file/a4c194082eab84886cbd4.jpg'
                        original_message_id = call.message.message_id

                        keyboard = telebot.types.InlineKeyboardMarkup()

                        primeira_coluna = [
                            telebot.types.InlineKeyboardButton(text="🐟 Comprar Iscas", callback_data=f'compras_iscas_callback')
                            ]

                        segunda_coluna = [
                            telebot.types.InlineKeyboardButton(text="🥕 Doar Cenouras", callback_data=f'doar_cenoura_{id_usuario}_{original_message_id}')
                                              ]

                        keyboard.row(*primeira_coluna)
                        keyboard.row(*segunda_coluna)
                        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                        result = cursor.fetchone()

                        if result:
                            qnt_cenouras = int(result[0])
                        else:
                            qnt_cenouras = 0
                        mensagem = f"🐇 Bem vindo a nossa lojinha. O que você quer levar?\n\n🥕 Saldo Atual: {qnt_cenouras}"
                        bot.edit_message_caption(chat_id=message.chat.id, message_id=original_message_id,caption=mensagem, reply_markup=keyboard)

                    except Exception as e:
                         print(f"Erro ao processar comando: {e}")
            elif call.data.startswith('compras_iscas_'):
                compras_iscas_callback(call)
            elif call.data.startswith("tcancelar"):
                chat_id = call.message.chat.id
                data = call.data.split('_')
                message_id = call.message.message_id

                print(data)
                destinatario_id = int(data[1])

                if destinatario_id == call.from_user.id:  # Verifica se o usuário que aceita é o destinatário correto    
                # Excluir a mensagem quando o botão "Cancelar" for clicado
                    bot.delete_message(call.message.chat.id, call.message.message_id) 
                else:       
                    bot.answer_callback_query(callback_query_id=call.id, text="Você não pode aceitar esta doação.")

            elif call.data.startswith("confirmar_doacao_"):
                chat_id = call.message.chat.id
                data = call.data.split('_')
                message_id = call.message.message_id

                if len(data) >= 6:
                    destinatario_id = int(data[4])

                    if destinatario_id != call.from_user.id:  # Verifica se o usuário que aceita é o destinatário correto
                        eu = int(data[2])
                        minhacarta = int(data[3])
                        destinatario_id = int(data[4])
                        qnt = int(data[5])
                        confirmar_doacao(eu, minhacarta, destinatario_id, chat_id, message_id,qnt)
                    else:
                        print("Erro: Você não tem permissão para aceitar esta doação.")
                        bot.answer_callback_query(callback_query_id=call.id, text="Você não pode aceitar esta doação.")
                else:
                    bot.send_message(chat_id, "O formato da mensagem de confirmação está incorreto.")


            elif call.data.startswith('aprovar_'):
                aprovar_callback(call)
            elif call.data.startswith('reprovar_'):
                reprovar_callback(call)
            elif call.data.startswith('repor_'):
                quantidade = 1
                message_data = call.data
                parts = message_data.split('_')
                id_usuario = parts[1]
                adicionar_iscas(id_usuario, quantidade,message) 
            elif call.data.startswith('cenourar_sim_'):
                ids_personagem = call.data.replace('cenourar_sim_', '').split(',')
                ids_personagem = [id.strip() for id in ids_personagem if id.strip()]

                for id_personagem in ids_personagem:
                    cenourar_carta(call.message, call.message.chat.id, id_personagem)
            elif call.data.startswith('cenourar_nao_'):
                id_usuario, id_personagem = call.data.split('_')
                bot.send_message(message.chat.id, "Você escolheu não cenourar a carta.")

            elif call.data.startswith('loja_loja'):
                try:
                    message_data = call.data.replace('loja_', '')
                    if message_data == "loja":
                        data_atual = dt_module.date.today().strftime("%Y-%m-%d")
                        print(data_atual)
                        id_usuario = call.from_user.id
                        ids_do_dia = obter_ids_loja_do_dia(data_atual)
                        resultado = obter_informacoes_loja(ids_do_dia)
                        imagem_url = 'https://telegra.ph/file/a60b21f603ad26eb8608a.jpg'
                        original_message_id = call.message.message_id
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        primeira_coluna = [
                            telebot.types.InlineKeyboardButton(text="☁️", callback_data=f'compra_musica_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🍄", callback_data=f'compra_series_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🍰", callback_data=f'compra_filmes_{id_usuario}_{original_message_id}')
                        ]
                        segunda_coluna = [
                            telebot.types.InlineKeyboardButton(text="🍂", callback_data=f'compra_miscelanea_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🧶", callback_data=f'compra_jogos_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🌷", callback_data=f'compra_animanga_{id_usuario}_{original_message_id}')
                            
                        ]
                        keyboard.row(*primeira_coluna)
                        keyboard.row(*segunda_coluna)

                        mensagem = "𝐀𝐡, 𝐨𝐥𝐚́! 𝐕𝐨𝐜𝐞̂ 𝐜𝐡𝐞𝐠𝐨𝐮 𝐧𝐚 𝐡𝐨𝐫𝐚 𝐜𝐞𝐫𝐭𝐚! \n\nNosso pescador acabou de chegar com os peixes fresquinhos de hoje:\n\n"

                        for carta_id in ids_do_dia:
                            id_personagem, emoji, nome, subcategoria = obter_informacoes_carta(carta_id)
                            mensagem += f"{emoji} - {nome} de {subcategoria}\n"

                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            reply_markup=keyboard,
                            media=telebot.types.InputMediaPhoto(media=imagem_url, caption=mensagem)
                        )
                except Exception as e:
                    print(f"Erro ao processar loja_loja_callback: {e}")


            elif call.data.startswith('compra_'):
                try:
                    chat_id = call.message.chat.id
                    message_data = call.data
                    parts = message_data.split('_')
                    categoria = parts[1]
                    id_usuario = parts[2]
                    original_message_id = parts[3]
                    conn, cursor = conectar_banco_dados()
                    cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                    result = cursor.fetchone()

                    if result:
                        qnt_cenouras = int(result[0])
                    else:
                        qnt_cenouras = 0

                    if qnt_cenouras >= 5:
                        cursor.execute(
                            "SELECT loja.id_personagem, personagens.nome, personagens.subcategoria, personagens.emoji "
                            "FROM loja "
                            "JOIN personagens ON loja.id_personagem = personagens.id_personagem "
                            "WHERE loja.categoria = %s AND loja.data = %s ORDER BY RAND() LIMIT 1",
                            (categoria, dt_module.date.today().strftime("%Y-%m-%d"))
                        )

                        carta_comprada = cursor.fetchone()

                        if carta_comprada:
                            id_personagem, nome, subcategoria, emoji = carta_comprada
                            mensagem = f"Você tem {qnt_cenouras} cenouras. \nDeseja usar 5 para comprar o seguinte peixe: \n\n{emoji} {id_personagem} - {nome} \nde {subcategoria}?"
                            keyboard = telebot.types.InlineKeyboardMarkup()
                            keyboard.row(
                                telebot.types.InlineKeyboardButton(text="Sim",
                                                                callback_data=f'confirmar_compra_{categoria}_{id_usuario}'),
                                telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')
                            )
                            imagem_url = "https://telegra.ph/file/d4d5d0af60ec66f35e29c.jpg"
                            bot.edit_message_media(
                                chat_id=chat_id,
                                message_id=original_message_id,
                                reply_markup=keyboard,
                                media=telebot.types.InputMediaPhoto(media=imagem_url, caption=mensagem)
                            )
                        else:
                            print(f"Nenhuma carta disponível para compra na categoria {categoria} hoje.")
                    else:
                        print("Usuário não tem cenouras suficientes para comprar.")

                except Exception as e:
                    print(f"Erro ao processar a compra: {e}")
                finally:
                    fechar_conexao(cursor, conn)
            elif call.data.startswith("bpronomes_"):
                try:
                    mostrar_opcoes_pronome(call.message.chat.id, call.message.message_id)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            
            elif call.data.startswith("liberar_beta"):
                try:
                    # Extrair o ID do usuário da chamada
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id
                    
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa a ser liberada no beta:")                    
                   

                    bot.register_next_step_handler(message, obter_id_beta)

                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")

            elif call.data.startswith("remover_beta"):
                try:
                    # Extrair o ID do usuário da chamada
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id
                    
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa a ser removida do beta:")                    
                   

                    bot.register_next_step_handler(message, remover_beta)

                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")
                            
            elif call.data.startswith("beta_"):
                
                try:
                    # Extrair o ID do usuário da chamada
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    # Enviar mensagem com quatro botões inline
                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("🥕 Liberar Usuario", callback_data=f"liberar_beta")
                    btn_iscas = types.InlineKeyboardButton("🐟 Remover Usuario", callback_data=f"remover_beta")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_5)

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Escolha o que deseja fazer:",reply_markup=markup)                    
                   
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    
            elif call.data.startswith("liberar_beta"):
                try:
                    # Extrair o ID do usuário da chamada
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id
                    
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa a ser liberada no beta:")                    
                   

                    bot.register_next_step_handler(message, obter_id_beta)

                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")
                    
            elif call.data.startswith("verificarban_"):
                verificar_ban(call)
                  
            elif call.data.startswith("ban_"):
                
                try:
                    # Extrair o ID do usuário da chamada
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id
                    
                    # Enviar mensagem com quatro botões inline
                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("🚫 Banir", callback_data=f"banir_{id_usuario}")
                    btn_iscas = types.InlineKeyboardButton("🔍 Verificar Banimento", callback_data=f"verificarban_{id_usuario}")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_5)

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Escolha o que deseja fazer:",reply_markup=markup)                    
                   
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            elif call.data.startswith("novogif"):
                processar_comando_gif(message)
            elif call.data.startswith("delgif"):
                processar_comando_delgif(message)             
            elif call.data.startswith("gif_"):
                try:
                    # Extrair o ID do usuário da chamada
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    # Enviar mensagem com quatro botões inline
                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("Alterar gif", callback_data=f"novogif")
                    btn_iscas = types.InlineKeyboardButton("Deletar Gif", callback_data=f"delgif")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_5)

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Escolha o que deseja fazer:",reply_markup=markup)                    
                   
                except Exception as e:
                    import traceback
                    traceback.print_exc()    
            elif call.data.startswith("tag"):
                    try:
                        # Extrair informações do callback data
                        parts = call.data.split('_')
                        print(f"Parts: {parts}")

                        
                        pagina = int(parts[1])
                        nometag = parts[2]
                        id_usuario = call.from_user.id 
                        editar_mensagem_tag(message, nometag, pagina,id_usuario)


                    except Exception as e:
                        print(f"Erro ao processar callback de página para a tag: {e}")
            
            elif call.data.startswith("admdar_"):
                
                try:
                    # Extrair o ID do usuário da chamada
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    # Enviar mensagem com quatro botões inline
                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("🥕 Dar Cenouras", callback_data=f"dar_cenoura_{id_usuario}")
                    btn_iscas = types.InlineKeyboardButton("🐟 Dar Iscas", callback_data=f"dar_iscas_{id_usuario}")
                    btn_1 = types.InlineKeyboardButton("🥕 Tirar Cenouras", callback_data=f"tirar_cenoura_{id_usuario}")
                    btn_2 = types.InlineKeyboardButton("🐟 Tirar Iscas", callback_data=f"tirar_isca_{id_usuario}")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_1, btn_2)
                    markup.row(btn_5)

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Escolha o que deseja fazer:",reply_markup=markup)                    
                   
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    
            elif call.data.startswith("dar_cenoura"):
                try:
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa junto da quantidade de cenouras a adicionar:")                    
                    bot.register_next_step_handler(message, obter_id_cenouras)

                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")
                    
            elif call.data.startswith("dar_iscas"):
                try:
                    # Solicitar o ID e o nome da pessoa
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa junto da quantidade de iscas a adicionar:")                    
                    bot.register_next_step_handler(message, obter_id_iscas)
                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")
                    
            elif call.data.startswith("tirar_cenoura"):
                try:
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa junto da quantidade de cenouras a retirar:")                    
                    bot.register_next_step_handler(message, adicionar_iscas)
                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")
                    
            elif call.data.startswith("tirar_isca"):
                try:
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    # Solicitar o ID e o nome da pessoa
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa junto da quantidade de iscas a retirar:")
                    bot.register_next_step_handler(message, remover_id_iscas)

                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")    
                        
            elif call.data.startswith("privacy"):
                #usar para editar mensagem com callback
                message_id = call.message.message_id
                usuario = call.message.chat.first_name
                id_usuario = call.message.chat.id

                status_perfil = obter_privacidade_perfil(id_usuario)

                editar_mensagem_privacidade(call.message.chat.id, message_id, usuario, id_usuario, status_perfil)

            elif call.data == 'open_profile':
                # Atualizar a privacidade do perfil para aberto
                atualizar_privacidade_perfil(call.message.chat.id, privacidade=False)
                
                # Editar mensagem para refletir a alteração
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Perfil alterado para aberto.")

            elif call.data == 'lock_profile':
                # Atualizar a privacidade do perfil para trancado
                atualizar_privacidade_perfil(call.message.chat.id, privacidade=True)
                
                # Editar mensagem para refletir a alteração
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Perfil alterado para trancado.")
            elif call.data == 'pcancelar':
                # Excluir a mensagem quando o botão "Cancelar" for clicado
                bot.delete_message(call.message.chat.id, call.message.message_id)     
         
            elif call.data.startswith("pronomes_"):
                pronome = call.data.replace('pronomes_', '')  # Remover o prefixo 'pronomes_'
                print(pronome)
                if pronome == 'remove':
                    pronome = None  # Definir como None para remover o pronome
                    atualizar_pronome(call.message.chat.id, pronome)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="Pronome removido com sucesso.")
                else:
                    atualizar_pronome(call.message.chat.id, pronome)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f"Pronome atualizado para: {pronome.capitalize()}")

            elif call.data.startswith("confirmar_compra_"):
                try:
                    data_atual = dt_module.date.today().strftime("%Y-%m-%d")  
                    parts = call.data.split('_')
                    categoria = parts[2]
                    id_usuario = parts[3]

                    cursor.execute(
                        "SELECT p.id_personagem, p.nome, p.subcategoria, p.imagem, p.emoji "
                        "FROM loja AS l "
                        "JOIN personagens AS p ON l.id_personagem = p.id_personagem "
                        "WHERE l.categoria = %s AND l.data = %s ORDER BY RAND() LIMIT 1",
                        (categoria, data_atual)
                    )
                    carta_comprada = cursor.fetchone()

                    if carta_comprada:
                        id_personagem, nome, subcategoria, imagem, emoji = carta_comprada
                        mensagem = f"𝐂𝐨𝐦𝐩𝐫𝐚 𝐟𝐞𝐢𝐭𝐚 𝐜𝐨𝐦 𝐬𝐮𝐜𝐞𝐬𝐬𝐨! \n\nO seguinte peixe foi adicionado à sua cesta: \n\n{emoji} {id_personagem} • {nome}\nde {subcategoria}\n\n𝐕𝐨𝐥𝐭𝐞 𝐬𝐞𝐦𝐩𝐫𝐞!"
                        print(f"{id_usuario} comprou a carta com ID {id_personagem} da categoria {categoria}.")
                        add_to_inventory(id_usuario, id_personagem)
                        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                        quantidade = cursor.fetchone()
                        res = functools.reduce(lambda sub, ele: sub * 10 + ele, quantidade)
                        valor = 5
                        diminuir_cenouras(id_usuario, valor)

                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            media=telebot.types.InputMediaPhoto(media=imagem,
                                                                caption=mensagem)
                            
                        )
                    else:
                        print(f"Nenhuma carta disponível para compra na categoria {categoria} hoje.")
                except Exception as e:
                    print(f"Erro ao processar a compra: {e}")
                finally:
                    fechar_conexao(cursor, conn)
            elif call.data.startswith('troca_'):
                troca_callback(call)
    except Exception as e:
        import traceback
        traceback.print_exc()
# Função para lidar com o callback de página de tag
def callback_pagina_tag(call):
    try:
        # Extrair informações do callback data
        parts = call.data.split('_')
        pagina_atual = int(parts[1])
        nometag = parts[2]
        total_paginas = parts[3]
        id_usuario = call.from_user.id 
        if pagina_atual < 1:
            bot.answer_callback_query(call.id, text="Página inválida.")
            return

        # Atualizar a mensagem com a página correspondente
        editar_mensagem_tag(call.message, nometag, pagina_atual,id_usuario,total_paginas)

    except Exception as e:
        print(f"Erro ao processar callback de tag: {e}")
        bot.answer_callback_query(call.id, text="Ocorreu um erro ao processar a consulta.")
        
# Função para verificar se um ID de usuário está na tabela ban
def verificar_ban(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        
        # Consultar a tabela ban para verificar se o ID está presente
        cursor.execute("SELECT * FROM ban WHERE iduser = %s", (str(id_usuario),))
        ban_info = cursor.fetchone()

        if ban_info:
            # Se o ID estiver na tabela ban, informar motivo e nome
            motivo = ban_info[3]
            nome = ban_info[2]
            return True, motivo, nome
        else:
            # Se o ID não estiver na tabela ban
            return False, None, None

    except Exception as e:
        print(f"Erro ao verificar na tabela ban: {e}")
        return False, None, None                      
def categoria_callback(call):
    try:
        categoria = call.data.replace('pescar_', '')
        ultimo_clique[call.message.chat.id] = {'categoria': categoria}
        categoria_handler(call.message, categoria)
    except Exception as e:
        print(f"Erro ao processar categoria_callback: {e}")
# Função para adicionar ou atualizar um GIF na tabela
def adicionar_atualizar_gif(id_personagem, id_usuario, link):
    try:
        conn, cursor = conectar_banco_dados()

        # Verifica se já existe um GIF para esse par de IDs
        query_select = "SELECT idgif FROM gif WHERE id_personagem = %s AND id_usuario = %s"
        cursor.execute(query_select, (id_personagem, id_usuario))
        gif_existente = cursor.fetchone()

        if gif_existente:
            # Se existir, atualiza o link do GIF
            query_update = "UPDATE gif SET link = %s WHERE id_personagem = %s AND id_usuario = %s"
            cursor.execute(query_update, (link, id_personagem, id_usuario))
            conn.commit()
            return "GIF atualizado com sucesso!"
        else:
            # Se não existir, insere um novo registro na tabela
            query_insert = "INSERT INTO gif (id_personagem, id_usuario, link) VALUES (%s, %s, %s)"
            cursor.execute(query_insert, (id_personagem, id_usuario, link))
            conn.commit()
            return "GIF adicionado com sucesso!"

    except mysql.connector.Error as error:
        return f"Erro ao adicionar/atualizar GIF: {error}"

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def obter_dados_gif(message):
    try:
        parametros = message.text.split()
        if len(parametros) != 3:
            bot.reply_to(message, "Por favor, forneça exatamente três parâmetros: ID da pessoa, ID do personagem e link do GIF.")
            return

        id_personagem = int(parametros[0])
        id_usuario = int(parametros[1])
        link = parametros[2]

        resposta = adicionar_atualizar_gif(id_personagem, id_usuario, link)
        bot.reply_to(message, resposta)

    except ValueError:
        bot.reply_to(message, "Os IDs devem ser números inteiros.")


def processar_comando_gif(message):
    try:
        bot.reply_to(message, "Por favor, forneça  o ID do personagem, o ID da pessoa, e o link do GIF.")

        # Aguarda a resposta do usuário
        bot.register_next_step_handler(message, obter_dados_gif)

    except Exception as e:
        bot.reply_to(message, f"Erro ao processar comando /gif: {e}")
# Função para deletar o GIF da tabela
def deletar_gif(id_personagem, id_usuario):
    try:
        conn, cursor = conectar_banco_dados()

        # Verifica se existe um GIF para esse par de IDs
        query_select = "SELECT idgif FROM gif WHERE id_personagem = %s AND id_usuario = %s"
        cursor.execute(query_select, (id_personagem, id_usuario))
        gif_existente = cursor.fetchone()

        if gif_existente:
            # Se existir, deleta o registro da tabela
            query_delete = "DELETE FROM gif WHERE id_personagem = %s AND id_usuario = %s"
            cursor.execute(query_delete, (id_personagem, id_usuario))
            conn.commit()
            return "GIF deletado com sucesso!"
        else:
            return "Nenhum GIF encontrado para esse usuário e ID de personagem."

    except mysql.connector.Error as error:
        return f"Erro ao deletar GIF: {error}"

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
def processar_comando_delgif(message):
    try:
        bot.reply_to(message, "Por favor, forneça o ID do personagem e o ID do usuário.")

        # Aguarda a resposta do usuário
        bot.register_next_step_handler(message, obter_ids)

    except Exception as e:
        bot.reply_to(message, f"Erro ao processar comando /delgif: {e}")

def obter_ids(message):
    try:
        parametros = message.text.split()
        if len(parametros) != 2:
            bot.reply_to(message, "Por favor, forneça exatamente dois IDs.")
            return

        id_personagem = int(parametros[0])
        id_usuario = int(parametros[1])

        resposta = deletar_gif(id_personagem, id_usuario)
        bot.reply_to(message, resposta)

    except ValueError:
        bot.reply_to(message, "Os IDs devem ser números inteiros.")    

@bot.message_handler(commands=['verificar'])              
def verificar_aumentar_limite_cativeiro(message):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta SQL para obter todos os cativeiros
        query_obter_cativeiros = """
            SELECT id_personagem, limite_atual, COUNT(id_usuario) AS qtd_usuarios, SUM(IF(qnt_cartas >= limite_atual, 1, 0)) AS qtd_usuarios_limite
            FROM seeds
            GROUP BY id_personagem, limite_atual
        """
        cursor.execute(query_obter_cativeiros)
        resultados = cursor.fetchall()

        cativeiros_aumentados = []
        mensagem = "Resultado da verificação de cativeiros:\n"

        for resultado in resultados:
            id_personagem, limite_atual, qtd_usuarios, qtd_usuarios_limite = resultado

            # Mensagem de debug para o cativeiro atual
            mensagem_debug = (
                f"Cativeiro {id_personagem} - Limite atual: {limite_atual}, "
                f"Usuários: {qtd_usuarios}, Usuários no limite: {qtd_usuarios_limite}"
            )
            print(mensagem_debug)

            if qtd_usuarios > 0 and qtd_usuarios_limite >= qtd_usuarios / 2:
                # Aumentar o limite atual em 100 para este cativeiro na tabela seeds
                query_aumentar_limite_seeds = f"""
                    UPDATE seeds
                    SET limite_atual = limite_atual + 100
                    WHERE id_personagem = {id_personagem}
                """
                cursor.execute(query_aumentar_limite_seeds)
                conn.commit()
                cativeiros_aumentados.append(id_personagem)

                # Aumentar o limite atual em 100 para este cativeiro na tabela cativeiro
                query_aumentar_limite_cativeiro = f"""
                    UPDATE cativeiro
                    SET limite = limite + 100
                    WHERE id_personagem = {id_personagem}
                """
                cursor.execute(query_aumentar_limite_cativeiro)
                conn.commit()

                # Mensagem de debug para o aumento do limite
                mensagem_debug = f"Limite atual do cativeiro {id_personagem} aumentado em 100 com sucesso!"
                print(mensagem_debug)

            # Adicionar informações do cativeiro à mensagem final
            mensagem += (
                f"- Cativeiro {id_personagem}: Limite atual = {limite_atual}, "
                f"Usuários = {qtd_usuarios}, Usuários no limite = {qtd_usuarios_limite}\n"
            )
        # Consulta SQL para obter informações de todos os cativeiros
        query_obter_cativeiros = """
            SELECT id_personagem, COUNT(id_usuario) AS qtd_usuarios,
                   SUM(qnt_cartas) AS total_cartas
            FROM seeds
            GROUP BY id_personagem
        """
        cursor.execute(query_obter_cativeiros)
        resultados = cursor.fetchall()

        for resultado in resultados:
            id_personagem, qtd_usuarios, total_cartas = resultado

            # Calcular a média de cartas por usuário no cativeiro
            if qtd_usuarios > 0:
                media_cartas = total_cartas / qtd_usuarios
            else:
                media_cartas = 0

            # Atualizar a coluna 'media' na tabela 'cativeiro' com a média calculada
            query_atualizar_media_cativeiro = f"""
                UPDATE cativeiro
                SET media = {media_cartas:.2f}
                WHERE id_personagem = {id_personagem}
            """
            cursor.execute(query_atualizar_media_cativeiro)
            conn.commit()

            # Mensagem de debug para a atualização da média
            mensagem_debug = (
                f"Média de cartas por usuário atualizada para o cativeiro {id_personagem}: {media_cartas:.2f}"
            )
            print(mensagem_debug)

        print("Média de cartas por usuário atualizada com sucesso!")
        # Adicionar informações sobre os cativeiros aumentados à mensagem final
        if cativeiros_aumentados:
            mensagem += f"\nOs seguintes cativeiros foram aumentados em 100 no limite atual: {', '.join(map(str, cativeiros_aumentados))}"

        print("Limite atual dos cativeiros aumentado com sucesso!")

        return mensagem

    except mysql.connector.Error as e:
        print(f"Erro ao verificar e aumentar o limite dos cativeiros: {e}")
        return "Ocorreu um erro ao verificar os cativeiros."

    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['evento'])
def evento_command(message):
    try:
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        conn, cursor = conectar_banco_dados()
        qnt_carta(message.from_user.id)
        id_usuario = message.from_user.id
        user = message.from_user
        usuario = user.first_name
        
        comando_parts = message.text.split('/evento ', 1)[1].strip().lower().split(' ')
        if len(comando_parts) >= 2:
            evento = comando_parts[1]
            print(evento)
            subcategoria = ' '.join(comando_parts[1:])
        else:
            resposta = "Comando inválido. Use /evento <evento> <subcategoria>."
            bot.send_message(message.chat.id, resposta)
            return

        sql_evento_existente = f"SELECT DISTINCT evento FROM evento WHERE evento = '{evento}'"
        cursor.execute(sql_evento_existente)
        evento_existente = cursor.fetchone()
        if not evento_existente:
            resposta = f"Evento '{evento}' não encontrado na tabela de eventos."
            bot.send_message(message.chat.id, resposta)
            return

        if message.text.startswith('/evento s'):
            resposta_completa = comando_evento_s(id_usuario, evento, subcategoria, cursor,usuario)
        elif message.text.startswith('/evento f'):
            resposta_completa = comando_evento_f(id_usuario, evento, subcategoria, cursor,usuario)
        else:
            resposta = "Comando inválido. Use /evento s <evento> <subcategoria> ou /evento f <evento> <subcategoria>."
            bot.send_message(message.chat.id, resposta)
            return

        if isinstance(resposta_completa, tuple):
            subcategoria_pesquisada, lista = resposta_completa
            resposta = f"{lista}"
            bot.send_message(message.chat.id, resposta)
        else:
            bot.send_message(message.chat.id, resposta_completa)
    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)
    finally:
        fechar_conexao(cursor, conn)
def send_card_message(message, *args, cursor=None, conn=None):
    try:
        if len(args) == 1 and isinstance(args[0], dict):
            evento_aleatorio = args[0]
            subcategoria_display = evento_aleatorio['subcategoria'].split('_')[-1]

            if evento_aleatorio['imagem'] is None:
                imagem= "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n {evento_aleatorio['id_personagem']} - {evento_aleatorio['nome']}\nde {subcategoria_display}"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    media=telebot.types.InputMediaPhoto(media=imagem,
                                                        caption=text))
            else:
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n🎁∙ {evento_aleatorio['id_personagem']} — {evento_aleatorio['nome']}\nde {subcategoria_display}"
                imagem = evento_aleatorio['imagem']
                if imagem.lower().endswith(('.jpg', '.jpeg', '.png')):
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        media=telebot.types.InputMediaPhoto(media=imagem,
                                                            caption=text))
                elif imagem.lower().endswith(('.mp4', '.gif')):
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        media=telebot.types.InputMediaVideo(media=imagem,
                                                            caption=text))
            id_usuario = message.chat.id
            id_personagem = evento_aleatorio['id_personagem']
            nome = evento_aleatorio['nome']
            subcategoria = evento_aleatorio['subcategoria']
            # Adicione a carta ao inventário do usuário
            add_to_inventory(id_usuario, id_personagem)
            # Registre a carta girada no histórico
            register_card_history(id_usuario, id_personagem)

            # Verificar se a quantidade de cartas atingiu 50 ou mais
            quantidade = verifica_inventario_troca(id_usuario, id_personagem)
            if quantidade >= 50:
                bot.send_message(id_usuario, "🎉 Parabéns! Você alcançou 50 cartas do personagem!")
                

        elif len(args) == 5:
            emoji_categoria, id_personagem, nome, subcategoria, imagem = args
            subcategoria_display = subcategoria.split('_')[-1]
            id_usuario = message.chat.id
            # Adicione a carta ao inventário do usuário
            add_to_inventory(id_usuario, id_personagem)
            if imagem is None:
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n{emoji_categoria} {id_personagem} - {nome}\nde {subcategoria_display}"

                imagem_url="https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                        caption=text)
                )

            else:
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n{emoji_categoria} {id_personagem} - {nome}\nde {subcategoria_display}"

                if imagem.lower().endswith(('.jpg', '.jpeg', '.png')):
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        media=telebot.types.InputMediaPhoto(media=imagem,
                                                            caption=text))
                elif imagem.lower().endswith(('.mp4', '.gif')):
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        media=telebot.types.InputMediaVideo(media=imagem,
                                                            caption=text))
            # Registre a carta girada no histórico
            register_card_history(id_usuario, id_personagem)

            # Verificar se a quantidade de cartas atingiu 50 ou mais
            quantidade = verifica_inventario_troca(id_usuario, id_personagem)
            if quantidade >= 50:
                bot.send_message(id_usuario, "🎉 Parabéns! Você alcançou 50 cartas do personagem!")
                
        else:
            print("Número incorreto de argumentos.")
    except Exception as e:
        print(f"Erro ao enviar a mensagem da carta: {e}") 
        

def verificar_subcategoria_evento(subcategoria, cursor):
    try:
        cursor.execute(
            "SELECT id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'fixo' ORDER BY RAND() LIMIT 1",
            (subcategoria,))
        evento_aleatorio = cursor.fetchone()
        if evento_aleatorio:
            print(f"Evento fixo aleatório: {evento_aleatorio}")
            chance = random.randint(1, 100)

            if chance <= 20:
                id_personagem, nome, subcategoria, imagem = evento_aleatorio
                evento_formatado = {
                    'id_personagem': id_personagem,
                    'nome': nome,
                    'subcategoria': subcategoria,
                    'imagem': imagem
                }
                print(f"CHANCE SUFICIENTE: {subcategoria} - {chance}")
                return evento_formatado
            else:
                print(f"CHANCE INSUFICIENTE: {subcategoria} - {chance}")
                return None
        else:
            print("Nenhum evento fixo encontrado. Procedendo com lógica normal.")

    except Exception as e:
        print(f"Erro ao verificar subcategoria na tabela de eventos: {e}")
        return None
        
def choose_subcategoria_callback(call, subcategoria, cursor, conn):
    try:
        categoria_info = ultimo_clique.get(call.message.chat.id, {})
        categoria = categoria_info.get('categoria', '')

        if categoria.lower() == 'geral':
            evento_aleatorio = verificar_subcategoria_evento(subcategoria, cursor)
            if evento_aleatorio:
                send_card_message(call.message, evento_aleatorio)
            else:
                subcategoria_handler(call.message, subcategoria, cursor, conn, None)
        else:
            subcategoria_handler(call.message, subcategoria, cursor, conn, None)
    except Exception as e:
        print(f"Erro durante o processamento: {e}")

def loja_geral_callback(call):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = call.from_user.id
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()
        if result:
            qnt_cenouras = int(result[0])
        else:
            qnt_cenouras = 0
        if qnt_cenouras >= 3:
            mensagem = f"Você tem {qnt_cenouras} cenouras. Deseja usar 3 para ganhar um peixe aleatório?"
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton(text="Sim", callback_data=f'geral_compra_{id_usuario}'),
                telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')
            )
            imagem_url = "https://telegra.ph/file/d4d5d0af60ec66f35e29c.jpg"
            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                media=telebot.types.InputMediaPhoto(media=imagem_url, caption=mensagem)
            )
    except Exception as e:
        print(f"Erro ao processar loja_geral_callback: {e}")

import random

def geral_compra_callback(call):
    try:
        conn, cursor = conectar_banco_dados()
        
        # Selecionar aleatoriamente uma carta da tabela 'personagens'
        query_personagens = "SELECT * FROM personagens ORDER BY RAND() LIMIT 1"
        cursor.execute(query_personagens)
        carta_personagem = cursor.fetchone()
        
        # Selecionar aleatoriamente uma carta da tabela 'evento'
        query_evento = "SELECT * FROM evento ORDER BY RAND() LIMIT 1"
        cursor.execute(query_evento)
        carta_evento = cursor.fetchone()

        if carta_personagem and carta_evento:
            # Escolher aleatoriamente entre as cartas de 'personagens' e 'evento'
            if random.choice([True, False]):
                carta_aleatoria = carta_personagem
            else:
                carta_aleatoria = carta_evento

            id_personagem, nome, subcategoria, categoria, evento, imagem, emoji, cr = carta_aleatoria[:8]
            id_usuario = call.from_user.id
            valor = 3
            add_to_inventory(id_usuario, id_personagem)
            diminuir_cenouras(id_usuario, valor)

            resposta = f"🎴 Os mares trazem para sua rede:\n\n" \
                       f"{emoji} • {id_personagem} - {nome} \n{subcategoria} - {evento}\n\nVolte sempre!"

            if imagem:
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=imagem,
                    caption=resposta
                )
            else:
                resposta1 = f"🎴 Os mares trazem para sua rede:\n\n {emoji} • {id_personagem} - {nome} \n{subcategoria} - {evento}\n\n (A carta não possui foto ainda :())"
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=resposta1
                )
        else:
            bot.send_message(call.message.chat.id, "Não foi possível encontrar uma carta aleatória.")
    except mysql.connector.Error as err:
        bot.send_message(call.message.chat.id, f"Erro ao sortear carta: {err}")
    finally:
        fechar_conexao(cursor, conn)


def geral_compra_callback(call):
    try:
        conn, cursor = conectar_banco_dados()
        
        # Selecionar aleatoriamente uma carta da tabela 'personagens'
        query_personagens = "SELECT id_personagem, nome, subcategoria,  emoji, categoria,  imagem, cr FROM personagens ORDER BY RAND() LIMIT 1"
        cursor.execute(query_personagens)
        carta_personagem = cursor.fetchone()
        chance = random.choices([True, False], weights=[5, 95])[0]
        print(chance)
        # Se não houver carta de personagem, selecionar aleatoriamente uma carta da tabela 'evento' com 5% de chance
        if chance:
            query_evento = "SELECT id_personagem, nome, subcategoria, categoria, evento, emoji, cr, imagem FROM evento ORDER BY RAND() LIMIT 1"
            cursor.execute(query_evento)
            carta_evento = cursor.fetchone()
        else:
            carta_evento = None
        print(carta_personagem)
        if carta_personagem or carta_evento:
            # Se houver carta de evento, enviar carta de evento
            if carta_evento:
                id_personagem, nome, subcategoria, categoria, evento, emoji, cr, imagem = carta_evento
                categoria = "Evento"
            # Se não houver carta de evento, enviar carta de personagem
            else:
                id_personagem, nome, subcategoria,  emoji, categoria,  imagem, cr = carta_personagem
                evento = ""
                categoria = categoria.capitalize()  # Ajustando a categoria para ficar em maiúsculas

            id_usuario = call.from_user.id
            valor = 3
            add_to_inventory(id_usuario, id_personagem)
            diminuir_cenouras(id_usuario, valor)

            resposta = f"🎴 Os mares trazem para sua rede:\n\n" \
           f"{emoji} • {id_personagem} - {nome} \n{subcategoria}{' - ' + evento if not carta_personagem else ''}\n\nVolte sempre!"



            if imagem:
                bot.edit_message_media(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    media=telebot.types.InputMediaPhoto(media=imagem, caption=resposta)
                )
            else:
                resposta1 = f"🎴 Os mares trazem para sua rede:\n\n {emoji} • {id_personagem} - {nome} \n{subcategoria} - {categoria if carta_personagem else evento}\n\n (A carta não possui foto ainda :())"
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=resposta1,
                    reply_markup=None
                )
        else:
            bot.send_message(call.message.chat.id, "Não foi possível encontrar uma carta aleatória.")
    except mysql.connector.Error as err:
        bot.send_message(call.message.chat.id, f"Erro ao sortear carta: {err}")
    finally:
        fechar_conexao(cursor, conn)
# Função para responder ao callback query
def answer_callback_query(bot, callback_query_id, text):
    bot.answer_callback_query(callback_query_id, text)
    
# Função para definir uma reação de emoji em uma mensagem
def set_reaction(chat_id, message_id, emoji):
    url = f"https://api.telegram.org/bot{bot.token}/setMessageReaction"
    data = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reaction': json.dumps([{'type': 'emoji', 'emoji': emoji}])
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("Reação definida com sucesso.")
    else:
        print(f"Erro ao definir a reação: {response.status_code} - {response.text}")
        
def confirmar_iscas(call,message_id):
    try:
        print(message_id)
        chat_id = call.message.chat.id
        id_usuario = call.message.chat.id
        conn, cursor = conectar_banco_dados()
        
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        if result and len(result) > 0:  # Verifica se há resultados na consulta
            qnt_cenouras = int(result[0])
            if qnt_cenouras >= 5:
                cursor.execute("UPDATE usuarios SET cenouras = cenouras - 5 WHERE id_usuario = %s", (id_usuario,))
                cursor.execute("UPDATE usuarios SET iscas = iscas + 1 WHERE id_usuario = %s", (id_usuario,))
                conn.commit()

                mensagem = "Parabéns! Você comprou uma isca.\n\nBoas pescas."
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=mensagem
                )
            else:
                mensagem = "Desculpe, você não tem cenouras suficientes para comprar uma isca."
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=mensagem
                )
        else:
            mensagem = "Desculpe, não foi possível encontrar suas cenouras."
            bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=mensagem
                )
    except Exception as e:
        print(f"Erro ao processar confirmar_compra_iscas: {e}")


def compras_iscas_callback(call):
    try:
        message_id = call.message.message_id
        chat_id = call.message.chat.id
        id_usuario = call.message.chat.id
        conn, cursor = conectar_banco_dados()

        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        print(f"DEBUG - Resultado da consulta: {result}")
        print(f"message id: {message_id}")
        if result and len(result) > 0:  # Verifica se há resultados na consulta
            qnt_cenouras = int(result[0])
            if qnt_cenouras >= 5:
                mensagem = f"Você tem {qnt_cenouras} cenouras. Deseja usar 5 para comprar iscas?"
                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.row(
                    telebot.types.InlineKeyboardButton(text="Sim", callback_data='confirmar_iscas'),
                    telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')
                )
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=keyboard,
                    caption=mensagem
                )
            else:
                bot.send_message(chat_id, "Você não tem cenouras suficientes para comprar iscas.")
        else:
            bot.send_message(chat_id, "Desculpe, ocorreu um erro ao verificar suas cenouras.")
    except Exception as e:
        print(f"Erro ao processar compras_iscas_callback: {e}")

def doar_cenoura(call):
    try:
        conn, cursor = conectar_banco_dados()
        message_id = call.message.message_id
        chat_id = call.message.chat.id
        id_usuario = call.from_user.id

        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        print(f"DEBUG - Resultado da consulta: {result}")

        if result and len(result) > 0:  # Verifica se há resultados na consulta
            qnt_cenouras = int(result[0])
            if qnt_cenouras >= 1:
                mensagem = f"Você tem {qnt_cenouras} cenouras. \n\nPara doar, digite o usuário do Garden e a quantidade. \n\nExemplo: user1 100"
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=mensagem
                )

                # Adicionando um próximo handler para tratar a resposta do usuário
                @bot.message_handler(func=lambda message: message.chat.id == chat_id and message.from_user.id == id_usuario)
                def processar_resposta(message):
                    try:
                        conn, cursor = conectar_banco_dados()
                        resposta = message.text
                        
                        usuario_destino, quantidade = resposta.split()
                        
                        # Verificar se o usuário existe na tabela
                        cursor.execute("SELECT id_usuario FROM usuarios WHERE username = %s", (usuario_destino,))
                        usuario_existe = cursor.fetchone()
                        
                        if usuario_existe:
                            if int(quantidade) <= qnt_cenouras:
                                diminuir_cenouras(id_usuario, quantidade)
                                aumentar_cenouras(usuario_existe[0], quantidade)
                                caption = f"Você doou {quantidade} cenouras para {usuario_destino}."
                            else:
                                caption = "Você não tem essa quantidade de cenouras."
 
                        else:
                            caption = "O usuário digitado não existe, verifique e tente novamente."
                        
                        bot.send_message(chat_id, caption)
                    except Exception as e:
                        print(f"Erro ao processar resposta do usuário: {e}")
            else:
                bot.send_message(chat_id, "Você não tem cenouras suficientes para doar.")
        else:
            bot.send_message(chat_id, "Desculpe, ocorreu um erro ao verificar suas cenouras.")
    except Exception as e:
        print(f"Erro ao processar doar_cenoura: {e}")


def aprovar_callback(call):
    try:
        data = call.data.replace('aprovar_', '').strip().split('_')
        data_atual = datetime.now().strftime("%Y-%m-%d")
        hora_atual = datetime.now().strftime("%H:%M:%S")
        
        print("Data:", data)
        print("Data atual:", data_atual)
        print("Hora atual:", hora_atual)
        print(len(data))
        if len(data) == 2:
            conn, cursor = conectar_banco_dados()
            id_usuario, id_personagem = data
            
            print("ID do usuário:", id_usuario)
            print("ID do personagem:", id_personagem)
            
            sql_temp_select = "SELECT valor FROM temp_data WHERE id_usuario = %s AND id_personagem = %s"
            values_temp_select = (id_usuario, id_personagem)
            cursor.execute(sql_temp_select, values_temp_select)
            link_gif = cursor.fetchone()
            cursor.fetchall()  # Limpa os resultados do cursor antes de executar a próxima consulta
            print()

            if link_gif:
                sql_check_gif = "SELECT id_personagem FROM gif WHERE id_usuario = %s AND id_personagem = %s"
                cursor.execute(sql_check_gif, (id_usuario, id_personagem))
                cursor.fetchall()  # Limpa os resultados do cursor antes de executar a próxima consulta
                existing_gif_id = cursor.fetchone()

                if existing_gif_id:
                    sql_update_gif = "UPDATE gif SET link = %s WHERE id_personagem = %s"
                    cursor.execute(sql_update_gif, (link_gif[0], existing_gif_id[0]))
                else:
                    sql_insert_gif = "INSERT INTO gif (id_personagem, id_usuario, link) VALUES (%s, %s, %s)"
                    cursor.execute(sql_insert_gif, (id_personagem, id_usuario, link_gif[0]))

                sql_logs = "INSERT INTO logs (id_usuario, nome_usuario, ação, horario, data, aprovado, adm) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                values_logs = (id_usuario, obter_nome_usuario_por_id(id_usuario), 'gif', hora_atual, data_atual, 'sim', call.from_user.username if call.from_user.username else call.from_user.first_name)
                cursor.execute(sql_logs, values_logs)

                conn.commit()

                print("Dados inseridos com sucesso.")
                mensagem = f"Seu GIF para o personagem {id_personagem} foi atualizado!"
                bot.send_message(id_usuario, mensagem)

                grupo_id = -1002144134360 
                nome_usuario = obter_nome_usuario_por_id(id_usuario)
                mensagem_grupo = f"🎉 O GIF para o personagem {id_personagem} de {nome_usuario} foi aprovado! 🎉"
                bot.send_message(grupo_id, mensagem_grupo)
            else:
                print("Formato de callback incorreto. Esperado: 'aprovar_id_usuario_id_personagem'.")
    except Exception as e:
        import traceback
        traceback.print_exc()


def reprovar_callback(call):
    try:
        data = call.data.replace('reprovar_', '').strip().split('_')
        if len(data) == 2:
            id_usuario, id_personagem = data
            mensagem = f"Seu gif para o personagem {id_personagem} foi recusado"
            bot.send_message(id_usuario, mensagem)

            grupo_id = -1002144134360
            nome_usuario = obter_nome_usuario_por_id(id_usuario)
            mensagem_grupo = f"O GIF para o personagem {id_personagem} de {nome_usuario} foi reprovado... 😐"
            bot.send_message(grupo_id, mensagem_grupo)
        else:
            print("Formato de callback incorreto. Esperado: 'reprovar_id_usuario_id_personagem'")
    except Exception as e:
        print(f"Erro ao processar reprovar_callback: {e}")

def compra_callback(call):
    try:
        chat_id = call.message.chat.id
        message_data = call.data
        parts = message_data.split('_')
        categoria = parts[1]
        id_usuario = parts[2]
        original_message_id = parts[3]
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        if result:
            qnt_cenouras = int(result[0])
        else:
            qnt_cenouras = 0

        if qnt_cenouras >= 3:
            mensagem = f"Você tem {qnt_cenouras} cenouras. Deseja usar 3 para ganhar um peixe aleatório?"
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton(text="Sim", callback_data=f'confirmar_compra_{categoria}_{id_usuario}_{original_message_id}'),
                telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')
            )
            bot.edit_message_text(chat_id=chat_id, message_id=original_message_id, text=" ", reply_markup=keyboard)
        else:
            mensagem = "Desculpe, você não tem cenouras suficientes para comprar um peixe. Volte quando tiver pelo menos 3 cenouras!"
            bot.edit_message_text(chat_id=chat_id, message_id=original_message_id, text=mensagem)
    except Exception as e:
        print(f"Erro ao processar compra_callback: {e}")

def confirmar_compra_callback(call):
    try:
        chat_id = call.message.chat.id
        message_data = call.data
        parts = message_data.split('_')
        categoria = parts[1]
        id_usuario = parts[2]
        original_message_id = parts[3]
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        if result:
            qnt_cenouras = int(result[0])
        else:
            qnt_cenouras = 0

        if qnt_cenouras >= 3:
            cursor.execute("UPDATE usuarios SET cenouras = cenouras - 3 WHERE id_usuario = %s", (id_usuario,))
            cursor.execute("SELECT id_personagem FROM personagens WHERE subcategoria = %s ORDER BY RAND() LIMIT 1", (categoria,))
            result = cursor.fetchone()

            if result:
                id_personagem = result[0]
                cursor.execute("INSERT INTO colecao_usuario (id_usuario, id_personagem) VALUES (%s, %s)", (id_usuario, id_personagem))
                conn.commit()

                mensagem = f"Parabéns! Você comprou um peixe aleatório da categoria {categoria} por 3 cenouras."
                bot.edit_message_text(chat_id=chat_id, message_id=original_message_id, text=mensagem)
            else:
                mensagem = "Desculpe, ocorreu um erro ao processar sua compra. Tente novamente mais tarde."
                bot.edit_message_text(chat_id=chat_id, message_id=original_message_id, text=mensagem)
        else:
            mensagem = "Desculpe, você não tem cenouras suficientes para comprar um peixe. Volte quando tiver pelo menos 3 cenouras!"
            bot.edit_message_text(chat_id=chat_id, message_id=original_message_id, text=mensagem)
    except Exception as e:
        print(f"Erro ao processar confirmar_compra_callback: {e}")

def troca_callback(call):
    try:
        message_data = call.data.replace('troca_sim_', '').replace('troca_nao_', '')
        parts = message_data.split('_')

        
        if len(parts) >= 5:
            eu, voce, minhacarta, suacarta, message = parts
            qntminha_antes = verifica_inventario_troca(eu, minhacarta)
            qntsua_antes = verifica_inventario_troca(voce, suacarta)
            chat_id = call.message.chat.id if call.message else None
            user_id = call.from_user.id if call.from_user else None
    

            eu = int(eu)
            voce = int(voce)

            if user_id in [eu, voce]:
                
                if call.data.startswith('troca_sim_'):
                    if eu != user_id:
                        if int(voce) == 6127981599:
                            bot.edit_message_caption(chat_id=chat_id,
                                                     caption="Você não pode fazer trocas com a Mabi :(")
                        elif voce == eu:
                            bot.edit_message_caption(chat_id=chat_id,
                                                     caption="Você não pode fazer trocas consigo mesmo!")
                        else:
                            realizar_troca(call.message, eu, voce, minhacarta, suacarta, chat_id,qntminha_antes,qntsua_antes)
                    else:
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Você não pode aceitar seu próprio lanche.")
                
                elif call.data.startswith('troca_nao_'):
                    if chat_id and call.message:
                        
                        sql_insert = "INSERT INTO historico_trocas (id_usuario1, id_usuario2, quantidade_cartas_antes_usuario1, quantidade_cartas_depois_usuario1, quantidade_cartas_antes_usuario2, quantidade_cartas_depois_usuario2, id_carta_usuario1, id_carta_usuario2, aceita) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        val = (eu, voce, qntminha_antes, 0, qntsua_antes, 0, minhacarta, suacarta, False)
                        cursor.execute(sql_insert, val)
            
                        # Commit novamente após a inserção na tabela historico_trocas
                        conn.commit()
                        bot.edit_message_caption(chat_id=chat_id,
                                                 message_id=call.message.message_id,
                                                 caption="Poxa, um de vocês esqueceu a comida. 🕊"
                                                         "\nQuem sabe na próxima?")
                    else:
                        print("Erro: Não há informações suficientes no callback_data.")
                        bot.answer_callback_query(callback_query_id=call.id,
                                                  text="Você não pode aceitar esta troca.")
            else:
                bot.answer_callback_query(callback_query_id=call.id,
                                          text="Você não pode realizar esta ação nesta troca.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        chat_id = call.message.chat.id if call.message else None
        bot.edit_message_caption(chat_id=chat_id,
                                 message_id=call.message.message_id,
                                 caption="Alguém não tem o lanche enviado.\nQue tal olhar sua cesta novamente?")
    finally:
        fechar_conexao(cursor, conn)

        
def send_notification(chat_id, message_text):
    try:
        bot.send_message(chat_id, message_text)
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")

def aumentar_cenouras(user, valor):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT cenouras FROM usuarios WHERE user = %s", (user,))
        resultado = cursor.fetchone()

        if resultado:
            cenouras_atuais = int(resultado[0]) 
            print(cenouras_atuais)
            print(valor)
            nova_quantidade = cenouras_atuais + int(valor)
            cursor.execute("UPDATE usuarios SET cenouras = %s WHERE user = %s", (nova_quantidade, user))
            print(f"Cenouras aumentadas para o usuário {user}.")
            conn.commit()
        else:
            print("Erro: Usuário não encontrado.")

    except Exception as e:
        print(f"Erro ao diminuir cenouras: {e}")

    finally:
        fechar_conexao(cursor, conn)
        
def diminuir_cenouras(id_usuario, valor):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            cenouras_atuais = int(resultado[0]) 
            print(cenouras_atuais)
            print(valor)
            if cenouras_atuais >= int(valor):
                nova_quantidade = cenouras_atuais - int(valor)
                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s", (nova_quantidade, id_usuario))
                print(f"Cenouras diminuídas para o usuário {id_usuario}.")
                conn.commit()
            else:
                print("Erro: Não há cenouras suficientes para diminuir.")
        else:
            print("Erro: Usuário não encontrado.")

    except Exception as e:
        print(f"Erro ao diminuir cenouras: {e}")

    finally:
        fechar_conexao(cursor, conn)

def diminuir_peixes(id_usuario, valor):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            cenouras_atuais = int(resultado[0]) 
            if cenouras_atuais >= valor:
                nova_quantidade = cenouras_atuais - valor
                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s", (nova_quantidade, id_usuario))
                print(f"Cenouras diminuídas para o usuário {id_usuario}.")
                conn.commit()
            else:
                print("Erro: Não há cenouras suficientes para diminuir.")
        else:
            print("Erro: Usuário não encontrado.")

    except Exception as e:
        print(f"Erro ao diminuir cenouras: {e}")

    finally:
        fechar_conexao(cursor, conn)
        
def diminuir_giros(id_usuario, quantidade):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT id_usuario, nome, iscas FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado_usuario = cursor.fetchone()

        if resultado_usuario:
            id_usuario = resultado_usuario[0]
            nome_usuario = resultado_usuario[1]
            iscas_atuais = int(resultado_usuario[2]) 

            if iscas_atuais >= quantidade:
                nova_quantidade = iscas_atuais - quantidade
                cursor.execute("UPDATE usuarios SET iscas = %s WHERE id_usuario = %s", (nova_quantidade, id_usuario))

                conn.commit()
            else:
                print("Erro: Não há iscas suficientes para diminuir.")
        else:
            print("Erro: Usuário não encontrado.")
    except Exception as e:
        print(f"Erro ao diminuir iscas: {e}")
    finally:
        fechar_conexao(cursor, conn)

def verificar_tempo_passado(chat_id):
    if chat_id in ultima_interacao:
        tempo_passado = datetime.now() - ultima_interacao[chat_id]
        return tempo_passado.total_seconds() >=1
    else:
        return True

@bot.message_handler(commands=['wishlist'])
def verificar_cartas(message):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = message.from_user.id

        sql_wishlist = f"""
            SELECT p.id_personagem, p.nome AS nome_personagem, p.subcategoria, p.emoji
            FROM wishlist w
            JOIN personagens p ON w.id_personagem = p.id_personagem
            WHERE w.id_usuario = {id_usuario}
            
            UNION
            
            SELECT e.id_personagem, e.nome AS nome_personagem, e.subcategoria, e.emoji
            FROM wishlist w
            JOIN evento e ON w.id_personagem = e.id_personagem
            WHERE w.id_usuario = {id_usuario}
        """

        cursor.execute(sql_wishlist)
        cartas_wishlist = cursor.fetchall()

        if cartas_wishlist:
            cartas_removidas = []

            for carta_wishlist in cartas_wishlist:
                id_personagem_wishlist = carta_wishlist[0]
                nome_carta_wishlist = carta_wishlist[1]
                subcategoria_carta_wishlist = carta_wishlist[2]
                emoji_carta_wishlist = carta_wishlist[3]

                # Verificar se a carta está no inventário
                cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (id_usuario, id_personagem_wishlist))
                existing_inventory_count = cursor.fetchone()[0]
                inventory_exists = existing_inventory_count > 0

                if inventory_exists:
                    # Remover a carta da wishlist
                    cursor.execute("DELETE FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                                   (id_usuario, id_personagem_wishlist))
                    cartas_removidas.append(f"{emoji_carta_wishlist} - {nome_carta_wishlist} de {subcategoria_carta_wishlist}")

            if cartas_removidas:
                resposta = f"Algumas cartas foram removidas da wishlist porque já estão no inventário:\n{', '.join(map(str, cartas_removidas))}"
                bot.send_message(message.chat.id, resposta, reply_to_message_id=message.message_id)

            # Montar mensagem com cartas na wishlist
            lista_wishlist_atualizada = f"🤞 | Cartas na wishlist de {message.from_user.first_name}:\n\n"
            for carta_atualizada in cartas_wishlist:
                emoji_carta = carta_atualizada[3]
                nome_carta = carta_atualizada[1]
                subcategoria_carta = carta_atualizada[2]
                lista_wishlist_atualizada += f"{emoji_carta} - {nome_carta} de {subcategoria_carta}\n"

            bot.send_message(message.chat.id, lista_wishlist_atualizada, reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, "Sua Wishlist está vazia :)", reply_to_message_id=message.message_id)

    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a consulta no banco de dados.", reply_to_message_id=message.message_id)
    finally:
        conn.commit() 
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['addw'])
def add_to_wish(message):
    try:
        chat_id = message.chat.id
        id_usuario = message.from_user.id
        command_parts = message.text.split()
        if len(command_parts) == 2:
            id_personagem = command_parts[1]

            conn, cursor = conectar_banco_dados()
            cursor.execute("SELECT COUNT(*) FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                           (id_usuario, id_personagem))
            existing_wishlist_count = cursor.fetchone()[0]
            wishlist_exists = existing_wishlist_count > 0

            if wishlist_exists:
                bot.send_message(chat_id, "Você já possui essa carta na wishlist!", reply_to_message_id=message.message_id)
            else:
                cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (id_usuario, id_personagem))
                existing_inventory_count = cursor.fetchone()[0]
                inventory_exists = existing_inventory_count > 0

                if inventory_exists:
                    bot.send_message(chat_id, "Você já possui essa carta no inventário!", reply_to_message_id=message.message_id)
                else:
                    cursor.execute("INSERT INTO wishlist (id_personagem, id_usuario) VALUES (%s, %s)",
                                   (id_personagem, id_usuario))
                    bot.send_message(chat_id, "Carta adicionada à sua wishlist!\nBoa sorte!", reply_to_message_id=message.message_id)
            conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar carta à wishlist: {err}")
    finally:
        fechar_conexao(cursor, conn)
import time

# Comando /ping para verificar o tempo de resposta do bot
@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()  # Tempo inicial
    
    # Responde ao comando /ping com "🏓 Pong"
    bot.reply_to(message, "🏓 Pong")
    
    end_time = time.time()  # Tempo final
    elapsed_time = end_time - start_time  # Tempo decorrido
    
    # Evita a divisão por zero se o tempo decorrido for muito pequeno
    rps = 1 / elapsed_time if elapsed_time > 0 else float('inf')
    
    # Envia a mensagem com o tempo de resposta e pedidos por segundo
    bot.send_message(message.chat.id, f"🏓 Pong \n\n🕒 Ping: {elapsed_time:.2f} segundos\n🚀 RPS: {rps:.2f}")


@bot.message_handler(commands=['removew'])
@bot.message_handler(commands=['delw'])
def remover_da_wishlist(message):
    try:
        chat_id = message.chat.id
        id_usuario = message.from_user.id
        command_parts = message.text.split()
        if len(command_parts) == 2:
            id_personagem = command_parts[1]
            
        print(f"ID do usuário: {id_usuario}")
        print(f"ID da carta: {id_personagem}")

        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT COUNT(*) FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                       (id_usuario, id_personagem))
        existing_carta_count = cursor.fetchone()[0]

        if existing_carta_count > 0:
            cursor.execute("DELETE FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                           (id_usuario, id_personagem))
            bot.send_message(chat_id=chat_id, text="Carta removida da sua wishlist!", reply_to_message_id=message.message_id)
        else:
            bot.send_message(chat_id=chat_id, text="Você não possui essa carta na wishlist.", reply_to_message_id=message.message_id)
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao remover carta da wishlist: {err}")
    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['cenourar'])
def cenoura(message):
    try:
        conn, cursor = conectar_banco_dados()
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        print("Usuário não está banido. Pode cenourar.")
        id_usuario = message.from_user.id
        print(id_usuario)
        ids_personagem = message.text.replace('/cenourar', '').strip().split(',')
        ids_personagem = [id.strip() for id in ids_personagem if id.strip()]

        if ids_personagem:
            ids_formatados = ', '.join(ids_personagem)
            confirmacao = f"Deseja cenourar as cartas:\n\n{ids_formatados}?"
            keyboard = telebot.types.InlineKeyboardMarkup()
            sim_button = telebot.types.InlineKeyboardButton(text="Sim",
                                                            callback_data=f"cenourar_sim_{','.join(ids_personagem)}")
            nao_button = telebot.types.InlineKeyboardButton(text="Não",
                                                            callback_data="cenourar_nao")
            keyboard.row(sim_button, nao_button)
            bot.send_message(message.chat.id, confirmacao, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Nenhum ID de personagem fornecido.")
    except Exception as e:
        print(f"Erro ao processar o comando de cenourar: {e}")
        chat = message.chat.id
        bot.send_message(chat_id=chat, text="Erro ao processar o comando de cenourar.")
    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['pesca'])
@bot.message_handler(commands=['pescar'])
def pescar(message):
    try:

        nome = message.from_user.first_name
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        
        qtd_iscas = verificar_giros(message.from_user.id)
        if qtd_iscas == 0:
            mensagem_iscas = "Você está sem iscas."
            bot.send_message(message.chat.id, mensagem_iscas, reply_to_message_id=message.message_id)
        else:
            if not verificar_tempo_passado(message.chat.id):
                return
            else:
                ultima_interacao[message.chat.id] = datetime.now()

            if verificar_id_na_tabelabeta(message.from_user.id):
                diminuir_giros(message.from_user.id, 1)
                keyboard = telebot.types.InlineKeyboardMarkup()

                primeira_coluna = [
                    telebot.types.InlineKeyboardButton(text="☁  Música", callback_data='pescar_musica'),
                    telebot.types.InlineKeyboardButton(text="🌷 Anime", callback_data='pescar_animanga'),
                    telebot.types.InlineKeyboardButton(text="🧶  Jogos", callback_data='pescar_jogos')
                ]
                segunda_coluna = [
                    telebot.types.InlineKeyboardButton(text="🍰  Filmes", callback_data='pescar_filmes'),
                    telebot.types.InlineKeyboardButton(text="🍄  Séries", callback_data='pescar_series'),
                    telebot.types.InlineKeyboardButton(text="🍂  Misc", callback_data='pescar_miscelanea')
                ]

                keyboard.add(*primeira_coluna)
                keyboard.add(*segunda_coluna)
                keyboard.row(telebot.types.InlineKeyboardButton(text="🫧  Geral", callback_data='pescar_geral'))
                
                photo = "https://telegra.ph/file/b3e6d2a41b68c2ceec8e5.jpg"
                bot.send_photo(message.chat.id, photo=photo, caption=f'<i>Olá! {nome}, \nVocê tem disponivel: {qtd_iscas} iscas. \nBoa pesca!\n\nSelecione uma categoria:</i>', reply_markup=keyboard, reply_to_message_id=message.message_id,parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, "Ei visitante, você não foi convidado! 😡", reply_to_message_id=message.message_id)

    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido, reply_to_message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pescar_'))
def escolher_categoria_pescar(call):
    try:
        if verificar_tempo_passado(call.message.chat.id):
            categoria_escolhida[call.message.chat.id] = call.data.replace('pescar_', '')
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text=f"Você escolheu a categoria: {categoria_escolhida[call.message.chat.id]}")
        else:
            print(f"Tempo insuficiente passado desde a última interação. Ignorando callback.")
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
        

def register_card_history(id_usuario, id_carta):
    try:
        conn, cursor = conectar_banco_dados()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO historico_cartas_giradas (id_usuario, id_carta, data_hora) VALUES (%s, %s, %s)",
                       (id_usuario, id_carta, data_hora))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao registrar o histórico da carta: {err}")
    finally:
        fechar_conexao(cursor, conn)

def add_to_inventory(id_usuario, id_personagem):
    try:

        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                       (id_usuario, id_personagem))
        existing_carta = cursor.fetchone()

        if existing_carta:
            nova_quantidade = existing_carta[0] + 1
            cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s",
                           (nova_quantidade, id_usuario, id_personagem))
        else:
            cursor.execute("INSERT INTO inventario (id_personagem, id_usuario, quantidade) VALUES (%s, %s, 1)",
                           (id_personagem, id_usuario))

        cursor.execute("UPDATE personagens SET total = IFNULL(total, 0) + 1 WHERE id_personagem = %s", (id_personagem,))

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao adicionar carta ao inventário: {err}")
    finally:
        fechar_conexao(cursor, conn)
        
@bot.callback_query_handler(func=lambda call: call.data.startswith('total_'))
def callback_total_personagem(call):
    conn, cursor = conectar_banco_dados()
    chat_id = call.message.chat.id

    id_pesquisa = call.data.split('_')[1]

    sql_total = "SELECT total FROM personagens WHERE id_personagem = %s"
    cursor.execute(sql_total, (id_pesquisa,))
    total_pescados = cursor.fetchone()

    if total_pescados is not None and total_pescados[0] is not None:
        if total_pescados[0] > 1:
            bot.answer_callback_query(call.id, text=f"O personagem foi pescado {total_pescados[0]} vezes!", show_alert=True)
        elif total_pescados[0] == 1:
            bot.answer_callback_query(call.id, text=f"O personagem foi pescado {total_pescados[0]} vez!", show_alert=True)
        else:
            bot.answer_callback_query(call.id, text="Esse personagem ainda não foi pescado :(", show_alert=True)
    else:
        bot.answer_callback_query(call.id, text="Esse personagem ainda não foi pescado :(", show_alert=True)

def atualizar_coluna_usuario(id_usuario, coluna, novo_valor):
    try:
        conn, cursor = conectar_banco_dados()
        query = f"UPDATE usuarios SET {coluna} = %s WHERE id_usuario = %s"
        cursor.execute(query, (novo_valor, id_usuario))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao atualizar {coluna}: {err}")
    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['setbio'])
def set_bio_command(message):

    id_usuario = message.from_user.id
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        nova_bio = command_parts[1].strip()
        atualizar_coluna_usuario(id_usuario, 'bio', nova_bio)
        bot.send_message(message.chat.id, f"Bio do {id_usuario} atualizada para: {nova_bio}")
    else:
        bot.send_message(message.chat.id, "Formato incorreto. Use /setbio seguido da nova bio desejada, por exemplo: /setbio Nova bio incrível.")

def verifica_tempo_ultimo_gif(id_usuario):
    try:
        query_ultimo_gif = f"""
            SELECT MAX(data) AS ultima_data, MAX(horario) AS ultima_hora 
            FROM logs 
            WHERE id_usuario = {id_usuario} AND ação = 'gif'
        """
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_ultimo_gif)
        ultimo_gif = cursor.fetchone()

        if ultimo_gif and ultimo_gif[0]:
            ultima_data_hora_str = f"{ultimo_gif[0]} {ultimo_gif[1]}"
            ultimo_gif_datetime = datetime.strptime(ultima_data_hora_str, "%Y-%m-%d %H:%M:%S")
            
            if ultimo_gif_datetime.date() == datetime.now().date():
                ultimo_gif_datetime = ultimo_gif_datetime.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
            
            diferenca_tempo = datetime.now() - ultimo_gif_datetime
            if diferenca_tempo.total_seconds() < 3600:
                tempo_restante = timedelta(seconds=(3600 - diferenca_tempo.total_seconds()))
                return tempo_restante
            else:
                return None
        else:
            return None

    except Exception as e:
        print(f"Erro ao verificar tempo do último gif: {e}")
    finally:
        fechar_conexao(cursor, conn)

# Comando para enviar GIF
@bot.message_handler(commands=['setgif'])
def enviar_gif(message):
    try:
        # Extrair o id do personagem e o possível código da mensagem
        comando = message.text.split('/setgif', 1)[1].strip().lower()
        partes_comando = comando.split(' ')
        id_personagem = partes_comando[0]
        
        # Verificar se o código foi incluído no comando
        if 'eusoqueriasernormal' in partes_comando:
            tempo_restante = None  # Define o tempo como None para "burlar" o tempo
        else:
            # Verificar o tempo restante normalmente
            tempo_restante = verifica_tempo_ultimo_gif(message.from_user.id)
            if tempo_restante:
                bot.send_message(message.chat.id, f"Você já enviou um gif recentemente. Aguarde {tempo_restante} antes de enviar outro.")
                return

        bot.send_message(message.chat.id, "Eba! Você pode escolher um gif!\nEnvie o link do gif gerado pelo @UploadTelegraphBot:")
        links_gif[message.from_user.id] = id_personagem
        bot.register_next_step_handler(message, receber_link_gif, id_personagem)
    
    except IndexError:
        bot.send_message(message.chat.id, "Por favor, forneça o ID do personagem.")

def receber_link_gif(message, id_personagem):
    id_usuario = message.from_user.id
    print("Debug - id_usuario:", id_usuario)

    if id_usuario:
        link_gif = message.text
        print("Debug - link_gif:", link_gif)

        id_personagem = links_gif.get(id_usuario)
        print("Debug - id_personagem:", id_personagem)

        if id_personagem:
            numero_personagem = id_personagem.split('_')[0]
            print("Debug - numero_personagem:", numero_personagem)
            conn, cursor = conectar_banco_dados()
            sql_usuario = "SELECT nome_usuario, nome FROM usuarios WHERE id_usuario = %s"
            values_usuario = (id_usuario,)
            cursor.execute(sql_usuario, values_usuario)
            resultado_usuario = cursor.fetchone()
            print("Debug - resultado_usuario:", resultado_usuario)

            username_usuario = message.from_user.username
            print("Debug - username_usuario:", username_usuario)

            sql_personagem = "SELECT nome, subcategoria FROM personagens WHERE id_personagem = %s"
            values_personagem = (numero_personagem,)
            cursor.execute(sql_personagem, values_personagem)
            resultado_personagem = cursor.fetchone()
            print("Debug - resultado_personagem:", resultado_personagem)

            if resultado_usuario and resultado_personagem:
                nome_usuario = resultado_usuario[0]
                print("Debug - nome_usuario:", nome_usuario)

                nome_personagem = resultado_personagem[0]
                print("Debug - nome_personagem:", nome_personagem)

                subcategoria_personagem = resultado_personagem[1]
                print("Debug - subcategoria_personagem:", subcategoria_personagem)

                data_atual = datetime.now().strftime("%Y-%m-%d")
                hora_atual = datetime.now().strftime("%H:%M:%S")

                sql_temp_insert = "INSERT INTO temp_data (id_usuario, chave, valor, id_personagem) VALUES (%s, %s, %s, %s)"
                values_temp_insert = (id_usuario, f"{id_usuario}_{numero_personagem}", link_gif, numero_personagem)
                cursor.execute(sql_temp_insert, values_temp_insert)
                conn.commit()

                keyboard = telebot.types.InlineKeyboardMarkup()
                btn_aprovar = telebot.types.InlineKeyboardButton(text="✔️ Aprovar", callback_data=f"aprovar_{id_usuario}_{numero_personagem}")
                btn_reprovar = telebot.types.InlineKeyboardButton(text="❌ Reprovar", callback_data=f"reprovar_{id_usuario}_{numero_personagem}")

                keyboard.row(btn_aprovar, btn_reprovar)
                bot.forward_message(chat_id=-1002144134360, from_chat_id=message.chat.id, message_id=message.message_id)
                chat_id=-1002144134360
                mensagem = f"Pedido de aprovação de GIF:\n\n"
                mensagem += f"ID Personagem: {numero_personagem}\n"
                mensagem += f"{nome_personagem} de {subcategoria_personagem}\n\n"
                mensagem += f"Usuário: @{username_usuario}\n"
                mensagem += f"Nome: {nome_usuario}\n"

                bot.send_message(chat_id, mensagem, reply_markup=keyboard)
                bot.send_message(message.chat.id, "Link do GIF registrado com sucesso. Aguardando aprovação.")
            else:
                bot.send_message(message.chat.id, "Erro ao obter informações do usuário ou do personagem.")
        else:
            bot.send_message(message.chat.id, "Erro ao processar o link do GIF. Por favor, use o comando /setgif novamente.")
    else:
        bot.send_message(message.chat.id, "Erro ao processar o link do GIF. ID de usuário inválido.")


def verifica_inventario(id_usuario, id_personagem):
    conn, cursor = conectar_banco_dados()
    query = f"SELECT quantidade FROM inventario WHERE id_usuario = {id_usuario} AND id_personagem = {id_personagem}"
    cursor.execute(query)
    quantidade_total = cursor.fetchone()[0]
    print(quantidade_total)
    return quantidade_total > 29

def verifica_inventario_troca(id_usuario, id_personagem):
    conn, cursor = conectar_banco_dados()
    query = f"SELECT quantidade FROM inventario WHERE id_usuario = {id_usuario} AND id_personagem = {id_personagem}"
    cursor.execute(query)
    quantidade_total = cursor.fetchone()
    if quantidade_total is None:
        return 0  # Retorna 0 se a quantidade total for nula
    else:
        return quantidade_total[0]

@bot.message_handler(commands=['setmusica'])
def set_musica_command(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        nova_musica = command_parts[1].strip()
        id_usuario = message.from_user.id

        atualizar_coluna_usuario(id_usuario, 'musica', nova_musica)
        bot.send_message(message.chat.id, f"Música atualizada para: {nova_musica}")
    else:
        bot.send_message(message.chat.id, "Formato incorreto. Use /setmusica seguido da nova música, por exemplo: /setmusica nova_musica.")

@bot.message_handler(commands=['picnic'])
@bot.message_handler(commands=['trocar'])
@bot.message_handler(commands=['troca'])
def trade(message):
    try:
        chat_id = message.chat.id
        eu = message.from_user.id
        voce = message.reply_to_message.from_user.id
        seunome = message.reply_to_message.from_user.first_name
        meunome = message.from_user.first_name
        bot_id = 7088149058
        categoria = message.text.replace('/troca', '')
        minhacarta = message.text.split()[1]
        suacarta = message.text.split()[2]

        if voce == bot_id:
            bot.send_message(chat_id, "Você não pode fazer trocas com a Mabi :(", reply_to_message_id=message.message_id)
            return

        # Verifica se o usuário tem a carta que deseja trocar
        if verifica_inventario_troca(eu, minhacarta) == 0:
            bot.send_message(chat_id, f"🌦️ ་  {meunome}, você não possui o peixe {minhacarta} para trocar.", reply_to_message_id=message.message_id)
            return
        
        if verifica_inventario_troca(voce, suacarta) == 0:
            bot.send_message(chat_id, f"🌦️ ་  Parece que {seunome} não possui o peixe {suacarta} para trocar.", reply_to_message_id=message.message_id)
            return

        # Obtém informações das cartas
        info_minhacarta = obter_informacoes_carta(minhacarta)
        info_suacarta = obter_informacoes_carta(suacarta)
        emojiminhacarta, idminhacarta, nomeminhacarta, subcategoriaminhacarta = info_minhacarta
        emojisuacarta, idsuacarta, nomesuacarta, subcategoriasuacarta = info_suacarta
        meu_username = bot.get_chat_member(chat_id, eu).user.username
        seu_username = bot.get_chat_member(chat_id, voce).user.username

        seu_nome_formatado = f"@{seu_username}" if seu_username else seunome
        texto = (
            f"🥪 | Hora do picnic!\n\n"
            f"{meunome} oferece de lanche:\n"
            f" {idminhacarta} {emojiminhacarta}  —  {nomeminhacarta} de {subcategoriaminhacarta}\n\n"
            f"E {seunome} oferece de lanche:\n"
            f" {idsuacarta} {emojisuacarta}  —  {nomesuacarta} de {subcategoriasuacarta}\n\n"
            f"Podemos começar a comer, {seu_nome_formatado}?"
        )

        keyboard = types.InlineKeyboardMarkup()

        # Adiciona opções de confirmação à troca
        primeiro = [
            types.InlineKeyboardButton(text="✅",
                                       callback_data=f'troca_sim_{eu}_{voce}_{minhacarta}_{suacarta}_{chat_id}'),
            types.InlineKeyboardButton(text="❌", callback_data=f'troca_nao_{eu}_{voce}_{minhacarta}_{suacarta}_{chat_id}'),
        ]
        keyboard.add(*primeiro)

        image_url = "https://telegra.ph/file/8672c8f91c8e77bcdad45.jpg"
        bot.send_photo(chat_id, image_url, caption=texto, reply_markup=keyboard, reply_to_message_id=message.reply_to_message.message_id)

    except Exception as e:
        print(f"Erro durante a troca: {e}")


def realizar_troca(message, eu, voce, minhacarta, suacarta, chat_id, qntminha_antes, qntsua_antes):
    try:
        print("Variáveis recebidas:")
        print("eu:", eu)
        print("voce:", voce)
        print("minhacarta:", minhacarta)
        print("suacarta:", suacarta)
        print("chatid:", chat_id)

        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                       (eu, minhacarta))
        qntminha = cursor.fetchone()
        print(qntminha)
        print(cursor.fetchone())
        cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                       (voce, suacarta))
        qntsua = cursor.fetchone()
        print(cursor.fetchone())
        qntminha = functools.reduce(lambda sub, ele: sub * 10 + ele, qntminha) if qntminha else 0
        qntsua = functools.reduce(lambda sub, ele: sub * 10 + ele, qntsua) if qntsua else 0

        if qntminha > 0 and qntsua > 0:
            cursor.execute(
                "UPDATE inventario SET quantidade = %s - 1 WHERE id_usuario = %s AND id_personagem = %s",
                (qntminha, eu, minhacarta))
            cursor.execute(
                "UPDATE inventario SET quantidade = %s - 1 WHERE id_usuario = %s AND id_personagem = %s",
                (qntsua, voce, suacarta))
            cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                           (voce, minhacarta))
            qnt = cursor.fetchone()

            if qnt:
                cursor.execute(
                    "UPDATE inventario SET quantidade = quantidade + 1 WHERE id_usuario = %s AND id_personagem = %s",
                    (voce, minhacarta))
            else:
                cursor.execute("INSERT INTO inventario (id_usuario, id_personagem, quantidade) VALUES (%s, %s, 1)",
                               (voce, minhacarta,))
            cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                           (eu, suacarta))
            existe = cursor.fetchone()

            if existe:
                existe = functools.reduce(lambda sub, ele: sub * 10 + ele, existe)
                cursor.execute(
                    "UPDATE inventario SET quantidade = %s + 1 WHERE id_usuario = %s AND id_personagem = %s",
                    (existe, eu, suacarta))
            else:
                cursor.execute("INSERT INTO inventario (id_usuario, id_personagem, quantidade) VALUES (%s, %s, 1)",
                               (eu, suacarta,))
            conn.commit()
            
            qntminha_depois = verifica_inventario_troca(eu, minhacarta)
            qntsua_depois = verifica_inventario_troca(voce, suacarta)
            qntminha_depois = qntminha_depois if qntminha_depois is not None else 0
            qntsua_depois = qntsua_depois if qntsua_depois is not None else 0
            # Execute a inserção na tabela historico_trocas
            sql_insert = "INSERT INTO historico_trocas (id_usuario1, id_usuario2, quantidade_cartas_antes_usuario1, quantidade_cartas_depois_usuario1, quantidade_cartas_antes_usuario2, quantidade_cartas_depois_usuario2, id_carta_usuario1, id_carta_usuario2, aceita) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (eu, voce, qntminha_antes, qntminha_depois, qntsua_antes, qntsua_depois, minhacarta, suacarta, True)
            cursor.execute(sql_insert, val)
            
            # Commit novamente após a inserção na tabela historico_trocas
            conn.commit()
            image_url = "https://telegra.ph/file/8672c8f91c8e77bcdad45.jpg"
            bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message.message_id,
                media=telebot.types.InputMediaPhoto(media=image_url,
                                                    caption="Troca realizada com sucesso. Até a próxima!")
            )
    except mysql.connector.Error as err:
        bot.edit_message_caption(chat_id=message.chat.id, caption="Houve um problema com a troca, tente novamente!")


def confirmar_doacao(eu, minhacarta, destinatario_id, chat_id,message_id,qnt):
    try:
        conn, cursor = conectar_banco_dados()

        # Verificar se o usuário possui a carta que deseja doar
        qnt_carta = verifica_inventario_troca(eu, minhacarta)
        valor = qnt
        diminuir_cenouras(eu, valor)
        if qnt_carta > 0:
            # Reduzir a quantidade da carta no inventário do doador
            cursor.execute("UPDATE inventario SET quantidade = quantidade - %s WHERE id_usuario = %s AND id_personagem = %s",
                           (qnt, eu, minhacarta))

            # Verificar se o destinatário já possui essa carta
            cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                           (destinatario_id, minhacarta))
            qnt_destinatario = cursor.fetchone()

            if qnt_destinatario:
                # Incrementar a quantidade no inventário do destinatário
                cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_usuario = %s AND id_personagem = %s",
                               (qnt, destinatario_id, minhacarta))
            else:
                # Adicionar a carta ao inventário do destinatário
                cursor.execute("INSERT INTO inventario (id_usuario, id_personagem, quantidade) VALUES (%s, %s, %s)",
                               (destinatario_id, minhacarta,qnt))

            conn.commit()
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Doação realizada com sucesso!")
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Você não pode doar uma carta que não possui.")

    except mysql.connector.Error as err:
        print(f"Erro durante a doação: {err}")
        bot.send_message(chat_id, "Houve um erro ao processar a doação. Tente novamente.")

# Função para verificar se o usuário está autorizado
def verificar_autorizacao(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        # Consulta para verificar se o usuário está autorizado
        cursor.execute("SELECT adm FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        if result and result[0] is not None:
            return True  # Usuário autorizado
        else:
            return False  # Usuário não autorizado

    except Exception as e:
        print(f"Erro ao verificar autorização: {e}")
        return False  # Em caso de erro, considerar como não autorizado

    finally:
        # Fechar conexão com o banco de dados
        if conn.is_connected():
            cursor.close()
            conn.close()
# Função para inserir dados na tabela beta
def inserir_na_tabela_beta(id_usuario, nome):
    try:
        conn, cursor = conectar_banco_dados()
        # Inserir dados na tabela beta
        cursor.execute("INSERT INTO beta (id, nome) VALUES (%s, %s)", (id_usuario, nome))
        conn.commit()  # Confirmar a operação de inserção

        return True  # Inserção bem-sucedida

    except Exception as e:
        print(f"Erro ao inserir na tabela beta: {e}")
        return False  # Inserção falhou

    finally:
        # Fechar conexão com o banco de dados
        if conn.is_connected():
            cursor.close()
            conn.close()
# Função para excluir uma linha da tabela beta com base no ID de usuário
def excluir_da_tabela_beta(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        
        # Excluir a linha correspondente na tabela beta
        cursor.execute("DELETE FROM beta WHERE id = %s", (id_usuario,))
        conn.commit()  # Confirmar a operação de exclusão

        return True  # Exclusão bem-sucedida

    except Exception as e:
        print(f"Erro ao excluir da tabela beta: {e}")
        return False  # Exclusão falhou

    finally:
        # Fechar conexão com o banco de dados
        if conn.is_connected():
            cursor.close()
            conn.close()

def remover_id_cenouras(message):
    try:
        # Extrair o ID da pessoa e a quantidade de cenouras a ser adicionada
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            print(id_pessoa)
            quantidade_cenouras = int(parts[1])
            print(quantidade_cenouras)
            # Atualizar a quantidade de cenouras na tabela de usuários
            conn, cursor = conectar_banco_dados()

            # Consultar a quantidade atual de cenouras da pessoa
            cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()
            print(result)
            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual - quantidade_cenouras

                # Atualizar o número de cenouras na tabela de usuários
                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()

                # Fechar a conexão com o banco de dados
                fechar_conexao(cursor, conn)

                # Enviar mensagem de confirmação
                bot.send_message(message.chat.id, f"A quantidade de cenouras foi atualizada para {nova_quantidade} para o usuário com ID {id_pessoa}.")
            else:
                bot.send_message(message.chat.id, f"ID de usuário inválido.")

        else:
            bot.send_message(message.chat.id, "Formato incorreto. Envie o ID da pessoa e a quantidade de cenouras a ser adicionada, separados por espaço.")

    except Exception as e:
        print(f"Erro ao obter ID e quantidade de cenouras: {e}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a solicitação.")
                
def remover_id_iscas(message):
    try:
        # Extrair o ID da pessoa e a quantidade de cenouras a ser adicionada
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            quantidade_iscas = int(parts[1])

            # Atualizar a quantidade de cenouras na tabela de usuários
            conn, cursor = conectar_banco_dados()

            # Consultar a quantidade atual de cenouras da pessoa
            cursor.execute("SELECT iscas FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()

            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual - quantidade_iscas

                # Atualizar o número de cenouras na tabela de usuários
                cursor.execute("UPDATE usuarios SET iscas = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()

                # Fechar a conexão com o banco de dados
                fechar_conexao(cursor, conn)

                # Enviar mensagem de confirmação
                bot.send_message(message.chat.id, f"A quantidade de iscas foi atualizada para {nova_quantidade} para o usuário com ID {id_pessoa}.")
            else:
                bot.send_message(message.chat.id, f"ID de usuário inválido.")

        else:
            bot.send_message(message.chat.id, "Formato incorreto. Envie o ID da pessoa e a quantidade de cenouras a ser adicionada, separados por espaço.")

    except Exception as e:
        print(f"Erro ao obter ID e quantidade de cenouras: {e}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a solicitação.")
                    
def obter_id_cenouras(message):
    try:
        # Extrair o ID da pessoa e a quantidade de cenouras a ser adicionada
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            print(id_pessoa)
            quantidade_cenouras = int(parts[1])
            print(quantidade_cenouras)
            # Atualizar a quantidade de cenouras na tabela de usuários
            conn, cursor = conectar_banco_dados()

            # Consultar a quantidade atual de cenouras da pessoa
            cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()
            print(result)
            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual + quantidade_cenouras

                # Atualizar o número de cenouras na tabela de usuários
                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()

                # Fechar a conexão com o banco de dados
                fechar_conexao(cursor, conn)

                # Enviar mensagem de confirmação
                bot.send_message(message.chat.id, f"A quantidade de cenouras foi atualizada para {nova_quantidade} para o usuário com ID {id_pessoa}.")
            else:
                bot.send_message(message.chat.id, f"ID de usuário inválido.")

        else:
            bot.send_message(message.chat.id, "Formato incorreto. Envie o ID da pessoa e a quantidade de cenouras a ser adicionada, separados por espaço.")

    except Exception as e:
        print(f"Erro ao obter ID e quantidade de cenouras: {e}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a solicitação.")
                
def obter_id_iscas(message):
    try:
        # Extrair o ID da pessoa e a quantidade de cenouras a ser adicionada
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            print(id_pessoa)
            quantidade_iscas = int(parts[1])
            print(quantidade_iscas)
            # Atualizar a quantidade de cenouras na tabela de usuários
            conn, cursor = conectar_banco_dados()

            # Consultar a quantidade atual de cenouras da pessoa
            cursor.execute("SELECT iscas FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()
            print(result)
            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual + quantidade_iscas

                # Atualizar o número de cenouras na tabela de usuários
                cursor.execute("UPDATE usuarios SET iscas = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()

                # Fechar a conexão com o banco de dados
                fechar_conexao(cursor, conn)

                # Enviar mensagem de confirmação
                bot.send_message(message.chat.id, f"A quantidade de iscas foi atualizada para {nova_quantidade} para o usuário com ID {id_pessoa}.")
            else:
                bot.send_message(message.chat.id, f"ID de usuário inválido.")

        else:
            bot.send_message(message.chat.id, "Formato incorreto. Envie o ID da pessoa e a quantidade de iscas a ser adicionada, separados por espaço.")

    except Exception as e:
        print(f"Erro ao obter ID e quantidade de cenouras: {e}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a solicitação.")
                                
# Função para obter o ID da pessoa e continuar com o nome
def obter_id_beta(message):
    id_usuario = message.text
    # Solicitar o nome da pessoa
    bot.send_message(message.chat.id, "Por favor, envie o nome da pessoa:")
    bot.register_next_step_handler(message, lambda msg: obter_nome_beta(msg, id_usuario))

# Função para obter o nome da pessoa e inserir na tabela beta
def obter_nome_beta(message, id_usuario):
    nome = message.text
    if inserir_na_tabela_beta(id_usuario, nome):
        bot.reply_to(message, "Usuário adicionado à lista beta com sucesso!")
    else:
        bot.reply_to(message, "Erro ao adicionar usuário à lista beta.")
# Função para obter o nome da pessoa e inserir na tabela beta
def remover_beta(message):
    id_usuario = message.text

    if excluir_da_tabela_beta(id_usuario):
        bot.reply_to(message, "Usuário excluido com sucesso!")
    else:
        bot.reply_to(message, "Erro ao excluir usuário à lista beta.")

@bot.message_handler(commands=['admin'])
def doar(message):
    try:
        id_usuario = message.from_user.id
        if verificar_autorizacao(id_usuario):
            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('👨‍🌾 Beta', callback_data='beta_')
            btn2 = types.InlineKeyboardButton('🐟 Adicionar ou Remover', callback_data='admdar_')
            btn3 = types.InlineKeyboardButton('🚫 Banir', callback_data='banir_')
            btn4 = types.InlineKeyboardButton('GIFS', callback_data='gif_')
            btn_cancelar = types.InlineKeyboardButton('❌ Cancelar', callback_data='pcancelar')
            markup.add(btn1, btn2, btn3)
            markup.add(btn4, btn_cancelar)
            bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)
        else:
            bot.reply_to(message, "Você não está autorizado.")

    except Exception as e:
        import traceback
        traceback.print_exc()
        
def verificar_ban(call):
    try:
        conn, cursor = conectar_banco_dados()
        
        # Consultar a tabela ban para verificar todas as pessoas banidas
        cursor.execute("SELECT nome, motivo FROM ban")
        banidos = cursor.fetchall()

        if banidos:
            # Se houver pessoas banidas, retornar a lista com seus nomes e motivos
            banidos_info = []
            for banido in banidos:
                nome, motivo = banido
                banidos_info.append((nome, motivo))
            return True, banidos_info
        else:
            # Se não houver pessoas banidas
            return False, []

    except Exception as e:
        print(f"Erro ao verificar na tabela ban: {e}")
        return False, []
               
@bot.message_handler(commands=['doar'])
def doar(message):
    try:
        chat_id = message.chat.id
        eu = message.from_user.id
        args = message.text.split()

        if len(args) < 3:
            bot.send_message(chat_id, "Formato incorreto. Use /doar <ID_da_carta>")
            return

        quantidade = int(args[1])  # ID da carta a ser doada
        minhacarta = int(args[2])
        
        # Verificar se o usuário possui a cenoura necessária
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (eu,))
        result = cursor.fetchone()

        if result:
            qnt_cenouras = int(result[0])
        else:
            qnt_cenouras = 0

        # Verificar se o usuário possui cenouras suficientes para fazer a doação
        if qnt_cenouras >= quantidade:
            # Verificar se o usuário possui a carta que deseja doar
            qnt_carta = verifica_inventario_troca(eu, minhacarta)
            if qnt_carta > 0:
                # Capturar o ID do destinatário da doação
                destinatario_id = None
                nome_destinatario = None

                if message.reply_to_message and message.reply_to_message.from_user:
                    destinatario_id = message.reply_to_message.from_user.id
                    nome_destinatario = message.reply_to_message.from_user.first_name

                if not destinatario_id:
                    bot.send_message(chat_id, "Você precisa responder a uma mensagem para doar a carta.")
                    return

                nome_carta = obter_nome(minhacarta)
                qnt_str = f"uma unidade do peixe" if qnt_carta == 1 else f"{qnt_carta} unidades do peixe"
                cen_str = f"cenoura" if quantidade == 1 else f"cenouras"
                print(cen_str)
                # Mensagem de confirmação
                texto = f"Olá, {message.from_user.first_name}!\n\nVocê tem {qnt_cenouras} {cen_str} e {qnt_str}: {minhacarta} — {nome_carta}.\n\n"
                texto += f"Deseja gastar {quantidade} {cen_str} para doar {quantidade} desses peixes para {nome_destinatario}?"

                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.row(
                    telebot.types.InlineKeyboardButton(text="Sim", callback_data=f'confirmar_doacao_{eu}_{minhacarta}_{destinatario_id}_{quantidade}'),
                    telebot.types.InlineKeyboardButton(text="Não", callback_data=f'tcancelar_{eu}')
                )

                bot.send_message(chat_id, texto, reply_markup=keyboard)
            else:
                # Se o usuário não possuir a carta, enviar uma mensagem de aviso
                bot.send_message(chat_id, "Você não pode doar uma carta que não possui.")
        else:
            bot.send_message(chat_id, "Você não possui cenouras suficientes para fazer uma doação.")

    except Exception as e:
        print(f"Erro durante o comando de doação: {e}")

@bot.message_handler(commands=['criar_colagem'])
def criar_colagem(message):
    try:
        cartas_aleatorias = obter_cartas_aleatorias()
        data_atual_str = dt_module.date.today().strftime("%Y-%m-%d") 
        print(data_atual_str)
        if not cartas_aleatorias:
            bot.send_message(message.chat.id, "Não foi possível obter cartas aleatórias.")
            return

        registrar_cartas_loja(cartas_aleatorias, data_atual_str)
        imagens = []
        for carta in cartas_aleatorias:
            img_url = carta.get('imagem', '')
            try:
                if img_url:
                    response = requests.get(img_url)
                    if response.status_code == 200:
                        img = Image.open(io.BytesIO(response.content))
                        img = img.resize((300, 400), Image.LANCZOS)
                    else:
                        img = Image.new('RGB', (300, 400), color='black')
                else:

                    img = Image.new('RGB', (300, 400), color='black')
            except Exception as e:
                print(f"Erro ao abrir a imagem da carta {carta['id']}: {e}")

                img = Image.new('RGB', (300, 400), color='black')
            imagens.append(img)

        altura_total = (len(imagens) // 3) * 400

        colagem = Image.new('RGB', (900, altura_total))  
        coluna_atual = 0
        linha_atual = 0

        for img in imagens:
            colagem.paste(img, (coluna_atual, linha_atual))
            coluna_atual += 300

            if coluna_atual >= 900:
                coluna_atual = 0
                linha_atual += 400

        colagem.save('colagem_cartas.png')
        
        with open('colagem_cartas.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        enviar_mensagem_loja(message, cartas_aleatorias)
    except Exception as e:
        print(f"Erro ao criar colagem: {e}")
        bot.send_message(message.chat.id, "Erro ao criar colagem.")

def enviar_mensagem_loja(message, cartas_aleatorias):
    try:
        mensagem_loja = "🐟 Peixes na vendinha hoje:\n\n"

        for carta in cartas_aleatorias:
            mensagem_loja += f"{carta['emoji']}| {carta['id']} • {carta['nome']} - {carta['subcategoria']}\n"

        mensagem_loja += "\n🥕 Acesse usando o comando /vendinha"
        bot.send_message(message.chat.id, mensagem_loja, reply_to_message_id=message.message_id)

    except Exception as e:
        print(f"Erro ao enviar mensagem da loja: {e}")
        bot.send_message(message.chat.id, f"Erro ao enviar mensagem da loja: {e}", reply_to_message_id=message.message_id)

def manter_proporcoes(imagem, largura_maxima, altura_maxima):
    largura_original, altura_original = imagem.size
    proporcao_original = largura_original / altura_original

    if proporcao_original > 1:
        nova_largura = largura_maxima
        nova_altura = int(largura_maxima / proporcao_original)
    else:
        nova_altura = altura_maxima
        nova_largura = int(altura_maxima * proporcao_original)

    return imagem.resize((nova_largura, nova_altura))

@bot.message_handler(commands=['vendinha'])
def loja(message):
    try:
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        keyboard = telebot.types.InlineKeyboardMarkup()

        keyboard.row(telebot.types.InlineKeyboardButton(text="🎣 Peixes do dia", callback_data='loja_loja'))
        keyboard.row(telebot.types.InlineKeyboardButton(text="🎴 Estou com sorte", callback_data='loja_geral'))
        keyboard.row(telebot.types.InlineKeyboardButton(text="🐰 Lojinha do Bunny", callback_data='loja_compras'))

        image_url = "https://telegra.ph/file/ea116d98a5bd8d6179612.jpg"
        bot.send_photo(message.chat.id, image_url,
                       caption='Olá! Seja muito bem-vindo à vendinha da Mabi. Como posso te ajudar?',
                       reply_markup=keyboard, reply_to_message_id=message.message_id)

    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido, reply_to_message_id=message.message_id)


# Função para atualizar o campo pronome na tabela usuarios
def atualizar_pronome(id_usuario, pronome):
    try:
        conn, cursor = conectar_banco_dados()
        query = "UPDATE usuarios SET pronome = %s WHERE id_usuario = %s"
        cursor.execute(query, (pronome, id_usuario))
        conn.commit()
        print(f"Pronome atualizado para '{pronome}' para o usuário {id_usuario}")
    except Exception as e:
        print(f"Erro ao atualizar o pronome: {e}")
        
# Função para lidar com o comando /peixes
@bot.message_handler(commands=['peixes'])
def verificar_comando_peixes(message):
    try:
        parametros = message.text.split(' ', 2)[1:]  # Obtém os parâmetros do comando
        
        # Se não houver parâmetros, solicita a subcategoria
        if not parametros:
            bot.reply_to(message, "Por favor, forneça a subcategoria.")
            return
        
        subcategoria = " ".join(parametros)  # Une os parâmetros em uma única string
        
        # Se o segundo parâmetro for 'img', envia a imagem do primeiro ID
        if len(parametros) > 1 and parametros[0] == 'img':
            subcategoria = " ".join(parametros[1:])
            enviar_imagem_peixe(message, subcategoria)
        else:
            mostrar_lista_peixes(message, subcategoria)
        
    except Exception as e:
        print(f"Erro ao processar comando /peixes: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")


# Função para criar os botões de página para navegar pelas imagens dos peixes
def criar_botao_pagina_peixes(message, subcategoria, pagina_atual):
    try:
        conn, cursor = conectar_banco_dados()
        
        # Consulta SQL para contar o número total de imagens na subcategoria fornecida
        query_total = "SELECT COUNT(id_personagem) FROM personagens WHERE subcategoria = %s"
        cursor.execute(query_total, (subcategoria,))
        total_imagens = cursor.fetchone()[0]  # Número total de imagens
        
        markup = telebot.types.InlineKeyboardMarkup()

                # Botões na mesma linha
        markup.row(
                    telebot.types.InlineKeyboardButton(text="⏪️", callback_data=f"img_1_{subcategoria}"),
                    telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f"img_{pagina_atual-1}_{subcategoria}"),
                    telebot.types.InlineKeyboardButton(text="➡️", callback_data=f"img_{pagina_atual+1}_{subcategoria}"),
                    telebot.types.InlineKeyboardButton(text="⏩️", callback_data=f"img_{total_imagens}_{subcategoria}")
                )

        return markup
            
    except Exception as e:
        print(f"Erro ao criar botões de página: {e}")

def enviar_imagem_peixe(message, subcategoria, pagina_atual=1):
    try:
        conn, cursor = conectar_banco_dados()
        print(subcategoria)
        # Consulta SQL para encontrar a subcategoria fornecida
        subcategoria_like = f"%{subcategoria}%"
        query_subcategoria = "SELECT subcategoria FROM personagens WHERE subcategoria LIKE %s LIMIT 1"
        cursor.execute(query_subcategoria, (subcategoria_like,))
        subcategoria_encontrada = cursor.fetchone()[0]  # Extrair apenas o valor da subcategoria
        
        print(subcategoria_encontrada)
        
        # Consulta SQL para selecionar a imagem do ID correspondente à página atual na subcategoria fornecida
        query = "SELECT imagem, emoji, nome, id_personagem FROM personagens WHERE subcategoria = %s LIMIT 1 OFFSET %s"
        cursor.execute(query, (subcategoria_encontrada, pagina_atual - 1))
        imagem_info = cursor.fetchone()
        
        # Consulta SQL para selecionar os IDs da subcategoria fornecida
        query_ids = "SELECT id_personagem FROM personagens WHERE subcategoria = %s"
        cursor.execute(query_ids, (subcategoria_encontrada,))
        ids = [id[0] for id in cursor.fetchall()]  # Lista de IDs
        
        total_ids = len(ids)
        
        if imagem_info:
            imagem = imagem_info[0]  # Imagem correspondente à página atual
            emoji = imagem_info[1]   # Emoji correspondente à página atual
            nome = imagem_info[2]    
            id_personagem = imagem_info[3]  # Nome correspondente à página atual
            pagina_atual = 1
            
            # Criação da legenda
            caption = f"Peixes da espécie: <b>{subcategoria_encontrada}</b>\n\n{emoji} {id_personagem} - {nome}\n\nPersonagem {pagina_atual} de {total_ids}"
            
            # Continua com a criação dos botões de página
            markup = criar_botao_pagina_peixes(message, subcategoria_encontrada, pagina_atual)
            
            bot.send_photo(message.chat.id, photo=imagem, caption=caption, reply_markup=markup, parse_mode="HTML")

        else:
            bot.reply_to(message, f"Nenhuma imagem encontrada na subcategoria '{subcategoria_encontrada}'.")

    except Exception as e:
        print(f"Erro ao processar comando /peixes img: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")

# Função para lidar com o callback "img"
def callback_img_peixes(call, pagina_atual, subcategoria):
    try:
        conn, cursor = conectar_banco_dados()
                # Consulta SQL para encontrar a subcategoria fornecida
        subcategoria_like = f"%{subcategoria}%"
        query_subcategoria = "SELECT subcategoria FROM personagens WHERE subcategoria LIKE %s LIMIT 1"
        cursor.execute(query_subcategoria, (subcategoria_like,))
        subcategoria_encontrada = cursor.fetchone()

        # Consulta SQL para selecionar os IDs da subcategoria fornecida
        query = "SELECT id_personagem FROM personagens WHERE subcategoria = %s"
        cursor.execute(query, (subcategoria,))
        ids = [id[0] for id in cursor.fetchall()]  # Lista de IDs
        
        total_ids = len(ids)
        
        # Verifica se a página atual está dentro do intervalo de IDs disponíveis
        if 1 <= pagina_atual <= total_ids:
            id_atual = ids[pagina_atual - 1]  # Obtém o ID correspondente à página atual
            
            # Consulta SQL para selecionar a imagem, o emoji e o nome do ID atual
            query_info = "SELECT imagem, emoji, nome FROM personagens WHERE id_personagem = %s"
            cursor.execute(query_info, (id_atual,))
            info = cursor.fetchone()  # Informações correspondentes ao ID atual
            
            imagem = info[0]  # Imagem correspondente ao ID atual
            emoji = info[1]   # Emoji correspondente ao ID atual
            nome = info[2]    # Nome correspondente ao ID atual
            
            # Criação da legenda
            legenda = f"Peixes da especie: <b>{subcategoria}</b>\n\n{emoji} {id_atual} - {nome}\n\nPersonagem {pagina_atual} de {total_ids}"
            
            # Criação dos botões de página
            markup = criar_botao_pagina_peixes(call.message, subcategoria, pagina_atual)
            
            # Edita a mensagem original para mostrar a nova imagem com a legenda e os botões de página
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=telebot.types.InputMediaPhoto(imagem, caption=legenda,parse_mode="HTML"), reply_markup=markup)
        
        else:
            bot.answer_callback_query(call.id, text="ID não encontrado.")
    
    except Exception as e:
        print(f"Erro ao processar callback 'img' de peixes: {e}")

def mostrar_lista_peixes(message, subcategoria):
    try:
        conn, cursor = conectar_banco_dados()

        # Verifica se há a letra "e" na frente da subcategoria
        if subcategoria.startswith("e"):
            subcategoria_original = subcategoria
            subcategoria = subcategoria[2:]
            subcategoria_like = f"%{subcategoria}%"
            query_subcategoria = "SELECT subcategoria FROM personagens WHERE subcategoria LIKE %s LIMIT 1"
            cursor.execute(query_subcategoria, (subcategoria_like,))
            subcategoria_encontrada = cursor.fetchone()
            # Consulta SQL para encontrar os peixes correspondentes à subcategoria apenas na tabela evento
            query_evento = "SELECT id_personagem, nome, emoji FROM evento WHERE subcategoria = %s"
            cursor.execute(query_evento, subcategoria_encontrada)
            peixes = cursor.fetchall()
        else:
            # Consulta SQL para encontrar os peixes correspondentes à subcategoria na tabela personagens
            query_personagens = "SELECT id_personagem, nome, emoji FROM personagens WHERE subcategoria = %s"
            cursor.execute(query_personagens, (subcategoria,))
            peixes_personagens = cursor.fetchall()

            # Consulta SQL para encontrar os peixes correspondentes à subcategoria na tabela evento
            query_evento = "SELECT id_personagem, nome, emoji FROM evento WHERE subcategoria = %s"
            cursor.execute(query_evento, (subcategoria,))
            peixes_evento = cursor.fetchall()

            # Combine os resultados das duas tabelas
            peixes = peixes_personagens + peixes_evento

        if peixes:
            resposta = f"<i>Peixes da espécie</i> <b>{subcategoria}</b>:\n\n"
            paginas = dividir_em_paginas(peixes, 15)
            pagina_atual = 1

            if pagina_atual in paginas:
                resposta_pagina = ""
                for index, peixe in enumerate(paginas[pagina_atual], start=1):
                    id_personagem, nome, emoji = peixe
                    resposta_pagina += f"{emoji} <code>{id_personagem}</code> - {nome}\n"

                resposta += resposta_pagina

                if len(paginas) > 1:
                    resposta += f"\nPágina <b>{pagina_atual}</b>/{len(paginas)}"
                    markup = criar_markup_peixes(pagina_atual, len(paginas), subcategoria)
                    bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")
                else:
                    bot.send_message(message.chat.id, resposta, parse_mode="HTML")
            else:
                bot.reply_to(message, "Página não encontrada.")
        else:
            bot.reply_to(message, f"Nenhum peixe encontrado na subcategoria '{subcategoria}'.")

    except Exception as e:
        print(f"Erro ao processar comando /peixes: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")


def criar_markup_peixes(pagina_atual, total_paginas, subcategoria):
    markup = telebot.types.InlineKeyboardMarkup()

    # Botões na mesma linha
    markup.row(
        telebot.types.InlineKeyboardButton(text="⏪️", callback_data=f"peixes_1_{subcategoria}"),
        telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f"peixes_{pagina_atual-1}_{subcategoria}"),
        telebot.types.InlineKeyboardButton(text="➡️", callback_data=f"peixes_{pagina_atual+1}_{subcategoria}"),
        telebot.types.InlineKeyboardButton(text="⏩️", callback_data=f"peixes_{total_paginas}_{subcategoria}")
    )

    return markup


def pagina_peixes_callback(call, pagina, subcategoria):
    try:
        print("Subcategoria:", subcategoria)
        print("Página desejada:", pagina)
        
        conn, cursor = conectar_banco_dados()
                
        if subcategoria.startswith("f"):

            query = "SELECT id_personagem, nome, emoji FROM personagens WHERE subcategoria = %s"
            cursor.execute(query, (subcategoria,))
        else:
            # Caso contrário, consulta apenas a tabela personagens
            # Se a subcategoria começar com "f", consulta tanto a tabela personagens quanto a tabela evento
            query = """
                SELECT id_personagem, nome, emoji FROM personagens WHERE subcategoria = %s
                UNION
                SELECT id_personagem, nome, emoji FROM evento WHERE subcategoria = %s
            """
            cursor.execute(query, (subcategoria, subcategoria))
        peixes = cursor.fetchall()
        
        print("Peixes encontrados:", peixes)
        
        paginas = dividir_em_paginas(peixes, 15)
        
        print("Páginas:", paginas)
        
        if pagina in paginas:
            resposta = f"<i>Peixes da espécie</i> <b>{subcategoria}</b>:\n\n"
            for peixe in paginas[pagina]:
                id_personagem, nome, emoji = peixe
                resposta += f"{emoji} <code>{id_personagem}</code> - {nome}\n"
            
            resposta += f"\nPágina <b>{pagina}</b>/{len(paginas)}"
            markup = criar_markup_peixes(pagina, len(paginas), subcategoria)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup,parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, text="Página não encontrada.")
    except Exception as e:
        print(f"Erro ao processar callback de página de peixes: {e}")

# Função para dividir os peixes em páginas
def dividir_em_paginas(lista, tamanho_pagina):
    paginas = {}
    for i in range(0, len(lista), tamanho_pagina):
        paginas[(i // tamanho_pagina) + 1] = lista[i:i + tamanho_pagina]
    return paginas

        
@bot.message_handler(commands=['colagem'])
def criar_colagem(message):
    try:

        if len(message.text.split()) != 7:
            bot.reply_to(message, "Por favor, forneça exatamente 6 IDs de cartas separados por espaços.")
            return
        ids_cartas = message.text.split()[1:]
        imagens = []
        
        for id_carta in ids_cartas:
            img_url = obter_url_imagem_por_id(id_carta)
            if img_url:
                print(id_carta)
                response = requests.get(img_url)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                    img = manter_proporcoes(img, 300, 400)  
                else:
                    img = Image.new('RGB', (300, 400), color='black')
            else:
                img = Image.new('RGB', (300, 400), color='black')
            imagens.append(img)
        
        altura_total = ((len(imagens) - 1) // 3 + 1) * 400
        colagem = Image.new('RGB', (900, altura_total))  
        coluna_atual = 0
        linha_atual = 0

        for img in imagens:
            colagem.paste(img, (coluna_atual, linha_atual))
            coluna_atual += 300

            if coluna_atual >= 900:
                coluna_atual = 0
                linha_atual += 400

        colagem_path = 'colagem_cartas.png'
        colagem.save(colagem_path)

        with open(colagem_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

    except Exception as e:
        print(f"Erro ao criar colagem: {e}")
        bot.reply_to(message, "Erro ao criar colagem.")

def manter_proporcoes(imagem, largura_maxima, altura_maxima):
    largura_original, altura_original = imagem.size
    proporcao_original = largura_original / altura_original

    if proporcao_original > 1:
        nova_largura = largura_maxima
        nova_altura = int(largura_maxima / proporcao_original)
    else:
        nova_altura = altura_maxima
        nova_largura = int(altura_maxima * proporcao_original)

    return imagem.resize((nova_largura, nova_altura))
@bot.message_handler(commands=['enviar_mensagem'])
def enviar_mensagem_privada(message):
    try:
        # Verificar se o comando tem o formato correto
        if len(message.text.split()) < 3:
            bot.reply_to(message, "Formato incorreto. Use /enviar_mensagem <id_usuario> <sua_mensagem>")
            return
        
        # Extrair o ID do usuário e a mensagem a ser enviada
        _, user_id, *mensagem = message.text.split(maxsplit=2)
        user_id = int(user_id)
        mensagem = mensagem[0]
        
        # Enviar a mensagem para o usuário especificado
        bot.send_message(user_id, mensagem)
        
        # Informar ao remetente que a mensagem foi enviada com sucesso
        bot.reply_to(message, f"Mensagem enviada para o usuário {user_id} com sucesso!")
        
    except ValueError:
        bot.reply_to(message, "ID de usuário inválido. Certifique-se de fornecer um número inteiro válido.")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        bot.reply_to(message, "Ocorreu um erro ao enviar a mensagem.")

@bot.message_handler(commands=['enviar_grupo'])
def enviar_mensagem_grupo(message):
    try:
        # Verificar se o comando tem o formato correto
        if len(message.text.split()) < 3:
            bot.reply_to(message, "Formato incorreto. Use /enviar_grupo <id_grupo> <sua_mensagem>")
            return
        
        # Extrair o ID do grupo e a mensagem a ser enviada
        _, group_id, *mensagem = message.text.split(maxsplit=2)
        group_id = int(group_id)
        mensagem = mensagem[0]
        
        # Enviar a mensagem para o grupo especificado
        bot.send_message(group_id, mensagem)
        
        # Informar ao remetente que a mensagem foi enviada com sucesso
        bot.reply_to(message, f"Mensagem enviada para o grupo {group_id} com sucesso!")
        
    except ValueError:
        bot.reply_to(message, "ID de grupo inválido. Certifique-se de fornecer um número inteiro válido.")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o grupo: {e}")
        bot.reply_to(message, "Ocorreu um erro ao enviar a mensagem para o grupo.")


@bot.message_handler(commands=['legenda'])
def gerar_legenda(message):
    try:
        ids_cartas = message.text.split('/legenda')[1].strip().split()
        if len(ids_cartas) < 1:
            bot.send_message(message.chat.id, "Informe pelo menos um ID de carta.")
            return
        mensagem_legenda = "Legenda:\n\n"
        for id_carta in ids_cartas:
            info_carta = obter_info_carta_por_id(id_carta)
            if info_carta:
                mensagem_legenda += f"{info_carta['emoji']} | {info_carta['id']} • {info_carta['nome']} - {info_carta['subcategoria']}\n"
            else:
                mensagem_legenda += f"ID {id_carta} não encontrado.\n"

        bot.send_message(message.chat.id, mensagem_legenda, reply_to_message_id=message.message_id)
    except Exception as e:
        print(f"Erro ao processar comando /legenda: {e}")
              
def get_random_card_valentine(subcategoria):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute(
            "SELECT id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'aniversario' ORDER BY RAND() LIMIT 1",
            (subcategoria,))
        evento_aleatorio = cursor.fetchone()
        if evento_aleatorio:
            chance = random.randint(1, 100)

            if chance <= 100:
                id_personagem, nome, subcategoria, imagem = evento_aleatorio
                evento_formatado = {
                    'id_personagem': id_personagem,
                    'nome': nome,
                    'subcategoria': subcategoria,
                    'imagem': imagem  
                }

                return evento_formatado
            else:
                return None
        else:

            print(f"Erro ao verificar subcategoria na tabela de eventos: {e}")
    except Exception as e:
        return None

def alternar_evento():
    global evento_ativo
    evento_ativo = not evento_ativo

def get_random_subcategories_all_valentine(connection):
    cursor = connection.cursor()
    query = "SELECT DISTINCT subcategoria FROM evento WHERE evento = 'aniversario' ORDER BY RAND() LIMIT 2"
    cursor.execute(query)
    subcategories_valentine = [row[0] for row in cursor.fetchall()]

    cursor.close()
    return subcategories_valentine  
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.chat.type == 'private':
        registrar_mensagens_privadas(message)
    elif (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.chat.id != -1002138195059:
        registrar_mensagem_grupo(message)

def registrar_mensagens_privadas(message):
    try:
        conn, cursor = conectar_banco_dados()
        user_id = message.from_user.id
        message_text = message.text
        cursor.execute("INSERT INTO mensagens_privadas (user_id, message_text) VALUES (%s, %s)", (user_id, message_text))
        conn.commit()
    except Exception as e:
        print(f"Erro ao registrar mensagem privada: {e}")
    finally:
        fechar_conexao(cursor, conn)

def registrar_mensagem_grupo(message):
    try:
        conn, cursor = conectar_banco_dados()
        group_id = message.chat.id
        group_name = message.chat.title
        message_text = message.text
        id_usuario = message.from_user.id
        cursor.execute("INSERT INTO grupos (group_id, group_name, message_text, id_usuario) VALUES (%s, %s, %s, %s)",
                       (group_id, group_name, message_text, id_usuario))
        conn.commit()
    except Exception as e:
        print(f"Erro ao registrar mensagem de grupo: {e}")
    finally:
        fechar_conexao(cursor, conn)
from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *
from inventario import *
from gif import *

def get_random_subcategories_all_valentine(connection):
    cursor = connection.cursor()

    query = "SELECT subcategoria FROM evento WHERE evento = 'aniversario' ORDER BY RAND() LIMIT 2"
    cursor.execute(query)
    subcategories_valentine = [row[0] for row in cursor.fetchall()]

    cursor.close()

    return subcategories_valentine

# Função para verificar e processar os botões
def categoria_handler(message, categoria):
    try:
        conn, cursor = conectar_banco_dados()

        chat_id = message.chat.id 
        evento_ativo = True
                # Gera um número aleatório entre 0 e 1
        chance_evento = random.random()
        if categoria.lower() == 'geral' and chance_evento <= 0.4:
            evento_ativo = True

            if evento_ativo:
                # Caso 1: Envia ambos os botões com duas subcategorias
                subcategories_valentine = get_random_subcategories_all_valentine(conn)
                if len(subcategories_valentine) >= 2:
                    subcategories_aleatorias = random.sample(subcategories_valentine, k=2)
                    image_link = "https://telegra.ph/file/d651e2963427bcc6972e0.jpg"
                    caption = "Parece que a Mabi gostou de você! Você pode escolher qual peixe levar: \n\n"
                    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
                    emoji_numbers = ['🎈', '🎁']
                    row_buttons = []
                    for i, subcategory in enumerate(subcategories_aleatorias):
                        caption += f"{emoji_numbers[i]} - {subcategory} \n"
                        button_text = emoji_numbers[i]
                        row_buttons.append(telebot.types.InlineKeyboardButton(button_text, callback_data=f"subcategory_{subcategory}_valentine"))
                    markup.row(*row_buttons)

                    imagem_url = "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        reply_markup=markup,
                        media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                            caption=caption)
                    )

                                

                else:
                    # Caso 2: Envia um botão só com uma categoria (ou 💖 ou 💐)
                    caption = "Parece que a Mabi não quis comemorar agora... \n\nO que será que você vai levar?\n\n"
                    emoji_numbers = ['🎈', '🎁']
                    subcategoria_aleatoria = random.choice(emoji_numbers)
                    subcategories_valentine = get_random_subcategories_all_valentine(conn)

                    keyboard = telebot.types.InlineKeyboardMarkup()
                    button = telebot.types.InlineKeyboardButton(subcategoria_aleatoria, callback_data=f"subcategory_{subcategories_valentine[emoji_numbers.index(subcategoria_aleatoria)]}_valentine")

                    keyboard.add(button)

                    # Marca o botão como clicado
                    botao_clicado = True

                    imagem_url = "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        reply_markup=keyboard,
                        media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                            caption=caption)
                    )

        else:
            if categoria.lower() == 'geral':   # Se a categoria não for 'Geral', proceda com a lógica normal da tabela de personagens
                subcategorias = buscar_subcategorias(categoria)
                subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]

                if subcategorias:
                    # Envia mensagem de botões
                    resposta_texto = "Poxa, Parece que a Mabi não está afim de comemorar... \nSua isca trouxe esses peixes normais:\n\n"
                    subcategorias_aleatorias = random.sample(subcategorias, min(5, len(subcategorias)))

                    for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                        resposta_texto += f"{i}\uFE0F\u20E3 - {subcategoria}\n"

                    markup = telebot.types.InlineKeyboardMarkup(row_width=5)

                    row_buttons = []
                    for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                        button_text = f"{i}\uFE0F\u20E3"
                        callback_data = f"choose_subcategoria_{subcategoria}"
                        row_buttons.append(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))

                    markup.row(*row_buttons)
                    imagem_url="https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        reply_markup=markup,
                        media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                            caption=resposta_texto)
                    )

                else:
                    bot.send_message(message.chat.id, f"Nenhuma subcategoria encontrada para a categoria '{categoria}'.")
            else:
                            # Se a categoria não for 'Geral', proceda com a lógica normal da tabela de personagens
                subcategorias = buscar_subcategorias(categoria)
                subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]
                #isca texto
                if subcategorias:
                    resposta_texto = "Sua isca atraiu 5 espécies, qual peixe você vai levar?\n\n"
                    subcategorias_aleatorias = random.sample(subcategorias, min(5, len(subcategorias)))

                    for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                        resposta_texto += f"{i}\uFE0F\u20E3 - {subcategoria}\n"

                    markup = telebot.types.InlineKeyboardMarkup(row_width=5)

                    row_buttons = []
                    for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                        button_text = f"{i}\uFE0F\u20E3"
                        callback_data = f"choose_subcategoria_{subcategoria}"
                        row_buttons.append(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))

                    markup.row(*row_buttons)

                    imagem_url = "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        reply_markup=markup,
                        media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                            caption=resposta_texto)
                    )
                
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao buscar subcategorias: {err}")

    finally:
        fechar_conexao(cursor, conn)


def subcategoria_handler(message, subcategoria, cursor, conn, id_personagem):
    id_usuario = message.chat.id  
    try:
        cursor = conn.cursor()
        cartas_disponiveis = obter_cartas_subcateg(subcategoria, conn)
        
        if cartas_disponiveis:
            carta_aleatoria = random.choice(cartas_disponiveis)
            if carta_aleatoria:
                id_personagem_carta, emoji, nome, imagem = carta_aleatoria
                
                
                # Verificar se o limite de cativeiro foi atingido para essa carta e usuário
                quantidade = quantidade_cartas_usuario(id_usuario, id_personagem_carta)
                limite_cativeiro = verifica_limite_cativeiro(id_personagem_carta)
                print(f"Limite - Quantidade: {limite_cativeiro} - {quantidade}")
                Mabi = 1011473517
                if id_usuario == Mabi:
                    send_card_message(message, emoji, id_personagem_carta, nome, subcategoria, imagem)
                    qnt_carta(id_usuario) 
                else:
                    if limite_cativeiro <= quantidade:
                        # Limite de cativeiro alcançado
                        if not verificar_registro_cativeiro(id_usuario, id_personagem_carta):
                            # A pessoa não está registrada no cativeiro desta carta
                            mensagem_aviso = f"<b>⚠️ Você chegou ao limite fora do cativeiro da carta:</b>\n\n{id_personagem_carta} - {nome}\nde {subcategoria}\n\nVocê pode entrar no cativeiro da carta usando o comando <code>/seeds {id_personagem_carta}</code>\n\n🎣 <i>Uma isca foi devolvida ao seu inventario.</i>"
                            bot.send_message(id_usuario, mensagem_aviso,parse_mode="HTML")
                            quantidade = 1
                            conn, cursor = conectar_banco_dados()

                            # Consulta SQL para atualizar o número de iscas para o usuário
                            query_atualizar_iscas = """
                                UPDATE usuarios
                                SET iscas = iscas + %s
                                WHERE id_usuario = %s
                            """
                            cursor.execute(query_atualizar_iscas, (quantidade, id_usuario))
                            conn.commit()

                            print(f"Iscas adicionadas com sucesso para o usuário com ID {id_usuario}")
                        else:
                            # Limite de cativeiro alcançado, enviar aviso ao usuário
                            mensagem_aviso = f"⚠️ Você chegou no limite atual de {limite_cativeiro} cartas para o personagem:\n\n<b>{id_personagem_carta} - {nome}</b>\n\nClique em doar para dar a carta a um campônes aleatório do cativeiro ou pegue sua isca de volta!\n\n<b>❗️Dica:</b> <i>Use o comando <code>/cativeiro {id_personagem_carta}</code> para verificar quem está precisando o andamento dos outros cativeiros.</i>"
                            markup = telebot.types.InlineKeyboardMarkup()
                            primeira_coluna = [
                            telebot.types.InlineKeyboardButton(text="📨 Doar", callback_data=f"doar_{id_personagem_carta}"),
                            telebot.types.InlineKeyboardButton(text="🎣 Pegar isca", callback_data=f"repor_{id_usuario}")]
                            markup.row(*primeira_coluna)
                            bot.send_message(id_usuario, mensagem_aviso, reply_markup=markup,parse_mode="HTML")
                    else:
                        # Limite de cativeiro não foi atingido, enviar a carta ao usuário
                        send_card_message(message, emoji, id_personagem_carta, nome, subcategoria, imagem)
                        qnt_carta(id_usuario)  
     
            else:
                print("Nenhuma carta disponível para esta subcategoria.")
        else:
            print("Nenhuma carta disponível.")

    except Exception as e:
        print(f"Erro durante o processamento: {e}")

    finally:
        fechar_conexao(cursor, conn)
        
def escolher_usuario_para_doar(id_personagem):
    try:
        conn, cursor = conectar_banco_dados()

        # Obter todos os usuários associados ao cativeiro dessa carta
        query_obter_usuarios_cativeiro = """
            SELECT id_usuario
            FROM seeds
            WHERE id_personagem = %s
        """
        cursor.execute(query_obter_usuarios_cativeiro, (id_personagem,))
        usuarios_cativeiro = cursor.fetchall()

        # Embaralhar a lista de usuários para escolher aleatoriamente
        random.shuffle(usuarios_cativeiro)

        # Verificar cada usuário para encontrar um que não atingiu o limite de cativeiro
        for usuario in usuarios_cativeiro:
            id_usuario = usuario[0]
            quantidade_cartas = quantidade_cartas_usuario(id_usuario, id_personagem)
            limite_atual = verifica_limite_cativeiro(id_personagem)

            if quantidade_cartas < limite_atual:
                # Encontrou um usuário que ainda não atingiu o limite, retornar este usuário
                return id_usuario

        # Se nenhum usuário elegível for encontrado, retornar None
        return None

    except mysql.connector.Error as e:
        print(f"Erro ao escolher usuário para doar: {e}")
        return None

    finally:
        fechar_conexao(cursor, conn)
                
def doar_carta_handler(message, id_personagem_carta):
    id_usuario = message.chat.id
    try:
        # Escolher um usuário aleatório do cativeiro dessa carta para doar
        id_usuario_doacao = escolher_usuario_para_doar(id_personagem_carta)
        nome = obter_nome(id_personagem_carta)
        if id_usuario_doacao:
            # Adicionar a carta ao inventário do usuário escolhido para doação
            add_to_inventory(id_usuario_doacao, id_personagem_carta)

            # Enviar mensagem de confirmação para o usuário que recebeu a doação
            quantidade_atual = quantidade_cartas_usuario(id_usuario_doacao, id_personagem_carta)
            mensagem_confirmacao = f"Um peixe apareceu na sua cesta! Alguém do seu cativeiro deve ter deixado ;) \nQuantidade atual do cativeiro para {id_personagem_carta}: {quantidade_atual}"
            bot.send_message(id_usuario_doacao, mensagem_confirmacao)

            # Editar a mensagem original para refletir o envio da carta
            nova_mensagem = f"Sua carta foi enviada para a cesta de outro camponês! Agora ele tem {quantidade_atual} peixes de {nome} para completar o cativeiro!"
            bot.edit_message_text(chat_id=id_usuario, message_id=message.message_id, text=nova_mensagem)

        else:
            # Se não houver usuário disponível para doação, enviar mensagem de aviso
            nova_mensagem = f"Desculpe, não foi possível encontrar um usuário disponível para doação. Sua isca foi devolvida!"
            quantidade = 1
                    # Consulta SQL para atualizar o número de iscas para o usuário
            query_atualizar_iscas = """
                UPDATE usuarios
                SET iscas = iscas + %s
                WHERE id_usuario = %s
            """
            cursor.execute(query_atualizar_iscas, (quantidade, id_usuario))
            conn.commit()

            print(f"Iscas adicionadas com sucesso para o usuário com ID {id_usuario}")
            bot.edit_message_text(chat_id=id_usuario, message_id=message.message_id, text=nova_mensagem)


    except Exception as e:
        print(f"Erro ao processar doação da carta: {e}")


def categoria_handler(message, categoria):
    try:
        conn, cursor = conectar_banco_dados()

        chat_id = message.chat.id 

        if categoria.lower() == 'geral':
            subcategorias = buscar_subcategorias(categoria)
            subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]

            if subcategorias:
                resposta_texto = "Poxa, Parece que a Mabi não está afim de comemorar... \nSua isca trouxe esses peixes normais:\n\n"
                subcategorias_aleatorias = random.sample(subcategorias, min(5, len(subcategorias)))

                for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                    resposta_texto += f"{i}\uFE0F\u20E3 - {subcategoria}\n"

                markup = telebot.types.InlineKeyboardMarkup(row_width=5)

                row_buttons = []
                for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                    button_text = f"{i}\uFE0F\u20E3"
                    callback_data = f"choose_submenu_{subcategoria}"
                    row_buttons.append(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))

                markup.row(*row_buttons)

                imagem_url="https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_markup=markup,
                    media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                        caption=resposta_texto)
                )

            else:
                bot.send_message(message.chat.id, f"Nenhuma subcategoria encontrada para a categoria '{categoria}'.")
        else:
            subcategorias = buscar_subcategorias(categoria)
            subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]

            if subcategorias:
                resposta_texto = "Sua isca atraiu 5 espécies, qual peixe você vai levar?\n\n"
                subcategorias_aleatorias = random.sample(subcategorias, min(5, len(subcategorias)))

                for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                    resposta_texto += f"{i}\uFE0F\u20E3 - {subcategoria}\n"

                markup = telebot.types.InlineKeyboardMarkup(row_width=5)

                row_buttons = []
                for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                    button_text = f"{i}\uFE0F\u20E3"
                    callback_data = f"choose_submenu_{subcategoria}"
                    row_buttons.append(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))

                markup.row(*row_buttons)

                imagem_url = "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_markup=markup,
                    media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                        caption=resposta_texto)
                )
                
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao buscar subcategorias: {err}")

    finally:
        fechar_conexao(cursor, conn)

def buscar_subcategorias_por_submenu(submenu, cursor):
    try:
        cursor.execute("SELECT DISTINCT subcategoria FROM personagens WHERE submenu = %s", (submenu,))
        subcategorias = [row[0] for row in cursor.fetchall()]
        return subcategorias
    except mysql.connector.Error as err:
        print(f"Erro ao buscar subcategorias por submenu: {err}")
        return []

def submenu_handler(message, submenu, cursor, conn):
    try:
        subcategorias = buscar_subcategorias_por_submenu(submenu, cursor)

        if subcategorias:
            # Selecionar duas subcategorias aleatórias para apresentar
            subcategorias_aleatorias = random.sample(subcategorias, min(2, len(subcategorias)))

            resposta_texto = f"Escolha uma subcategoria relacionada a {submenu}:\n\n"
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)

            row_buttons = []
            for subcategoria in subcategorias_aleatorias:
                button_text = subcategoria
                callback_data = f"choose_subcategoria_{subcategoria}"
                row_buttons.append(telebot.types.InlineKeyboardButton(button_text, callback_data=callback_data))

            markup.row(*row_buttons)

            imagem_url = "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
            bot.edit_message_media(
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=markup,
                media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                    caption=resposta_texto)
            )

        else:
            bot.send_message(message.chat.id, f"Nenhuma subcategoria encontrada para o submenu '{submenu}'.")
            
    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao buscar subcategorias por submenu: {err}")

    finally:
        fechar_conexao(cursor, conn)


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_submenu_'))
def choose_submenu_callback(call):
    submenu = call.data.replace('choose_submenu_', '')
    submenu_handler(call.message, submenu, cursor, conn)


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_subcategoria_'))
def choose_subcategoria_callback(call, subcategoria, cursor, conn):
    try:
        categoria_info = ultimo_clique.get(call.message.chat.id, {})
        categoria = categoria_info.get('categoria', '')

        if categoria.lower() == 'geral':
            evento_aleatorio = verificar_subcategoria_evento(subcategoria, cursor)
            if evento_aleatorio:
                send_card_message(call.message, evento_aleatorio)
            else:
                subcategoria_handler(call.message, subcategoria, cursor, conn, None)
        else:
            subcategoria_handler(call.message, subcategoria, cursor, conn, None)

    except Exception as e:
        print(f"Erro durante o processamento: {e}")


   
while True:
    def verificar_e_atualizar_limites():
    # Aguardar 24 horas antes da próxima verificação (86400 segundos)
        time.sleep(60)
                
    try:
        if __name__ == "__main__":
            bot.polling(none_stop=True)
        else:
            bot.polling()
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente