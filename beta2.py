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
import re
from loja import *
from pescar import *
from cenourar import *
from pesquisas import *
from bd import *
from cestas import *

#bot = telebot.TeleBot("6322486327:AAGwLIYN0HMUCgOLHNo7Qz_zWpmvoUT28to")
# mabi
bot = telebot.TeleBot("7088149058:AAEnXEEGhCwU6-BlNcTgghAbtK0L-HWB2J4")

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
# Diretório para o cache de imagens
CACHE_DIR = "cache_imagens"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
       
@bot.message_handler(commands=['iduser'])
def handle_iduser_command(message):
    if message.reply_to_message:
        idusuario = message.reply_to_message.from_user.id
        bot.send_message(chat_id=message.chat.id, text=f"O ID do usuário é <code>{idusuario}</code>", reply_to_message_id=message.message_id,parse_mode="HTML")

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
                if message.text.startswith('/cesta fn'):
                    resposta_completa = comando_cesta_fn(id_usuario, subcategoria, cursor)
                    paginas_registradas = registrar_cartas(id_usuario, subcategoria, resposta_completa, modo='f')
                    print("Total de páginas registradas:", paginas_registradas)
                    if paginas_registradas >= 2:
                        subcategoria_pesquisada, lista = resposta_completa
                        enviar_faltante_inicial(message.chat.id, resposta_completa, paginas_registradas, subcategoria_pesquisada, id_usuario)
                else:
                    resposta_completa = comando_cesta_f(id_usuario, subcategoria, cursor)
                    paginas_registradas = registrar_cartas_cesta_f(id_usuario, subcategoria, resposta_completa, modo='s')
                    print("Total de páginas registradas:", paginas_registradas)
                    
                if paginas_registradas >= 2:
                    subcategoria_pesquisada, lista = resposta_completa
                    foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
                    print(foto_subcategoria)
                    if foto_subcategoria:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        enviar_faltante_inicial(message.chat.id, resposta, paginas_registradas, subcategoria_pesquisada, id_usuario,message)
                    else:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        enviar_faltante_inicial(message.chat.id, resposta, paginas_registradas, subcategoria_pesquisada, id_usuario,message)
                else:
                    lista, subcategoria_pesquisada = resposta_completa
                    foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
                    print(foto_subcategoria)
                    if foto_subcategoria:
                        # nome_usuario = obter_nome_do_usuario(id_usuario)
                        # nova_resposta = f"🧺 | Cartas de {subcategoria_pesquisada} faltantes na cesta de {nome_usuario}:\n\n{lista}"

                        # print(nova_resposta)
                        # #bot.send_photo(message.chat.id, photo=foto_subcategoria, caption=nova_resposta, reply_to_message_id=message.message_id, parse_mode="HTML")          
                        enviar_faltante_inicial(message.chat.id, resposta, paginas_registradas, subcategoria_pesquisada, id_usuario,message)
                    else:
                        print("oi")
                        
                        nome_usuario = obter_nome_do_usuario(id_usuario)
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {nome_usuario}:\n\n{lista}"
                        #bot.send_message(message.chat.id, resposta, reply_to_message_id=message.message_id, parse_mode="HTML")  
                        enviar_faltante_inicial(message.chat.id, resposta, paginas_registradas, subcategoria_pesquisada, id_usuario,message)
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
            else:
                bot.send_message(message.chat.id, "Comando inválido. Use /cesta s (pesquisa), /cesta f (pesquisa), /cesta fn (pesquisa) ou /cesta c (pesquisa). Exemplo: /cesta s Stray Kids", reply_to_message_id=message.message_id)

    except ValueError as e:
        print(f"Erro: {e}")
        if verificar_id_na_tabela(message.from_user.id, "ban", "iduser"):
            mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
            bot.send_message(message.chat.id, mensagem_banido,reply_to_message_id=message.message_id)
        else:
            mensagem = "Um erro ocorreu."
            bot.send_message(message.chat.id, mensagem,reply_to_message_id=message.message_id)
    finally:
        fechar_conexao(cursor, conn)
             
@bot.message_handler(commands=['tag'])
def listar_tags_usuario(message):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = message.from_user.id
        command_parts = message.text.split()
        if len(command_parts) == 1:
            cursor.execute("SELECT DISTINCT nometag FROM tags WHERE id_usuario = %s", (id_usuario,))
            resultado = cursor.fetchall()

            if resultado:
                tags_formatadas = "\n".join([f"- {row[0]}" for row in resultado])
                mensagem = f"Suas tags:\n{tags_formatadas}"
                bot.reply_to(message, mensagem)
            else:
                bot.reply_to(message, "Você não possui tags associadas.")
        else:
            nometag = command_parts[1]
            cursor.execute("SELECT DISTINCT nometag FROM tags WHERE id_usuario = %s AND nometag = %s", (id_usuario, nometag))
            resultado = cursor.fetchone()

            if resultado:
                mensagem = f"Peixes na tag <b>{nometag}</b>:\n\n"
                cursor.execute("""
                    SELECT p.emoji, p.subcategoria, p.id_personagem, p.nome, t.nometag
                    FROM personagens p
                    LEFT JOIN tags t ON p.id_personagem = t.id_personagem
                    WHERE t.id_usuario = %s AND t.nometag = %s
                """, (id_usuario, nometag))
                cartas_formatadas = [f"{'☀️' if inventario_existe(id_usuario, row[2]) else '🌧️'} | {row[0]} ⭑ {row[2]} - {row[3]} de {row[1]}" for row in cursor.fetchall()]
                mensagem += "\n".join(cartas_formatadas)
                bot.reply_to(message, mensagem, parse_mode="HTML")
            else:
                bot.reply_to(message, f"A tag '{nometag}' não foi encontrada.")
    except Exception as e:
        print(f"Erro ao listar tags ou cartas por tag: {e}")
    finally:
        fechar_conexao(cursor, conn)
        
@bot.message_handler(commands=['addtag'])
def adicionar_tag(message):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = message.from_user.id
        args = message.text.split()[1:]

        if len(args) >= 1:
            tag_info = args[-1]
            tag_parts = tag_info.split('|')
            if len(tag_parts) == 2:
                nometag = tag_parts[1].strip()
                ids_personagens = [id_personagem.strip() for id_personagem in tag_parts[0].split(',')]
                cursor.execute("SELECT idtags FROM tags WHERE id_usuario = %s AND nometag = %s", (id_usuario, nometag))
                tag_existente = cursor.fetchone()

                if tag_existente:
                    idtag_existente = tag_existente[0]
                    for id_personagem in ids_personagens:
                        cursor.execute("INSERT IGNORE INTO tags (id_usuario, id_personagem, nometag) VALUES (%s, %s, %s)",
                                       (id_usuario, id_personagem, nometag))

                    conn.commit()
                    bot.reply_to(message, f"A tag '{nometag}' foi atualizada com sucesso.")
                else:
                    for id_personagem in ids_personagens:
                        cursor.execute("INSERT INTO tags (id_usuario, id_personagem, nometag) VALUES (%s, %s, %s)",
                                       (id_usuario, id_personagem, nometag))
                    conn.commit()
                    bot.reply_to(message, f"A tag '{nometag}' foi adicionada com sucesso.")
            else:
                bot.reply_to(message, "Formato incorreto. Use /addtag id1,id2,... | nometag")
        else:
            bot.reply_to(message, "Formato incorreto. Use /addtag id1,id2,... | nometag")

    except Exception as e:
        print(f"Erro ao adicionar tag: {e}")
    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['deltag'])
def remover_tag(message):
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = message.from_user.id
        args = message.text.split()[1:]
        if len(args) == 1:
            nometag = args[0]
            cursor.execute("DELETE FROM tags WHERE id_usuario = %s AND nometag = %s", (id_usuario, nometag))
            conn.commit()
            bot.reply_to(message, f"A tag '{nometag}' foi removida com sucesso.")
        else:
            bot.reply_to(message, "Formato incorreto. Use /deltag nomedatag")
    except Exception as e:
        print(f"Erro ao remover tag: {e}")
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
@bot.message_handler(commands=['doar'])
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
    for _ in range(quantity):
        conn, cursor = conectar_banco_dados()
        query = "SELECT * FROM inventario WHERE id_personagem = %s AND id_usuario = %s"
        cursor.execute(query, (card_id, user_id))
        existing_card = cursor.fetchone()

        if existing_card:
            new_quantity = int(existing_card[3]) + 1
            update_query = "UPDATE inventario SET quantidade = %s WHERE id_personagem = %s AND id_usuario = %s"
            cursor.execute(update_query, (new_quantity, card_id, user_id))
        else:
            insert_query = "INSERT INTO inventario (id_personagem, id_usuario, quantidade) VALUES (%s, %s, 1)"
            cursor.execute(insert_query, (card_id, user_id))

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

@bot.message_handler(commands=['armazém'])
@bot.message_handler(commands=['armazem'])
@bot.message_handler(commands=['amz'])
def armazem_command(message):
    try:
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        
        conn, cursor = conectar_banco_dados()
        qnt_carta(message.from_user.id)
        id_usuario = message.from_user.id
        user = message.from_user
        usuario = user.first_name
        armazem_info[id_usuario] = {'id_usuario': id_usuario, 'usuario': usuario}
        pagina = 1
        resultados_por_pagina = 15

        query_fav_usuario = f"""
            SELECT id_personagem, emoji, nome_personagem, subcategoria, 0 AS quantidade, categoria
            FROM (
                SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, 0 AS quantidade, p.categoria
                FROM personagens p
                WHERE p.id_personagem = (
                    SELECT fav
                    FROM usuarios
                    WHERE id_usuario = {id_usuario}
                )

                UNION ALL

                SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria
                FROM evento e
                WHERE e.id_personagem = (
                    SELECT fav
                    FROM usuarios
                    WHERE id_usuario = {id_usuario}
                ) AND (SELECT fav FROM usuarios WHERE id_usuario = {id_usuario}) < 1000
            ) AS combined
        """

        cursor.execute(query_fav_usuario)
        resultado_fav_usuario = cursor.fetchone()


        sql = f"""
            SELECT id_personagem, emoji, nome_personagem, subcategoria, quantidade, categoria
            FROM (
                {query_fav_usuario}

                UNION ALL

                SELECT i.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, i.quantidade, p.categoria
                FROM inventario i
                JOIN personagens p ON i.id_personagem = p.id_personagem
                WHERE i.id_usuario = {id_usuario} AND i.quantidade > 0

                UNION ALL

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
        if resultado_fav_usuario:
            id_fav_usuario = resultado_fav_usuario[0]
            gif_url_fav = obter_gif_url(id_usuario, id_fav_usuario)
        if resultados:
            markup = telebot.types.InlineKeyboardMarkup()
            buttons_row = [
                telebot.types.InlineKeyboardButton("⏪️", callback_data=f"armazem_primeira_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("◀️", callback_data=f"armazem_anterior_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("▶️", callback_data=f"armazem_proxima_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("⏩️", callback_data=f"armazem_ultima_{pagina}_{id_usuario}")
            ]
            markup.row(*buttons_row)
            media_fav = obter_imagem_carta(id_usuario)
            nome_fav = obter_nome_carta(id_usuario)
            quantidade_total_cartas = obter_quantidade_total_cartas(id_usuario)
            total_paginas = (quantidade_total_cartas + resultados_por_pagina - 1) // resultados_por_pagina
            resposta = f"💌 | Cartas no armazém de {usuario}:\n\n❤️ Fav: {nome_fav}\n\n"
            print("id fav", id_fav_usuario)
            gif_url_fav = obter_gif_url(id_fav_usuario,id_usuario)
            print(gif_url_fav)
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
                elif 50 <= quantidade_carta:
                    letra_quantidade = "👑"
                else:
                    letra_quantidade = ""

                resposta += f" {emoji_carta} <code>{id_carta}</code> • {nome_carta} - {subcategoria_carta} {letra_quantidade}\n"

            resposta += f"\n{pagina}/{total_paginas}"
        
        if gif_url_fav:
            if gif_url_fav.lower().endswith(('.gif')):
                bot.send_animation(chat_id=message.chat.id, animation=gif_url_fav, caption=resposta, reply_to_message_id=message.message_id, reply_markup=markup, parse_mode="HTML")
            elif gif_url_fav.lower().endswith(('.mp4')):
                bot.send_video(chat_id=message.chat.id, video=gif_url_fav, caption=resposta, reply_to_message_id=message.message_id, reply_markup=markup, parse_mode="HTML")    
            elif gif_url_fav.lower().endswith(('.jpg', '.jpeg', '.png')):
                bot.send_photo(chat_id=message.chat.id, photo=gif_url_fav, caption=resposta, reply_to_message_id=message.message_id, reply_markup=markup, parse_mode="HTML")
        elif media_fav:
            if media_fav.lower().endswith(('.gif')):
                mensagem = bot.send_animation(chat_id=message.chat.id, animation=media_fav, caption=resposta, reply_to_message_id=message.message_id, reply_markup=markup, parse_mode="HTML")
            elif media_fav.lower().endswith(('.mp4')):
                mensagem = bot.send_video(chat_id=message.chat.id, video=media_fav, caption=resposta, reply_to_message_id=message.message_id, reply_markup=markup, parse_mode="HTML")    
            elif media_fav.lower().endswith(('.jpg', '.jpeg', '.png')):
                mensagem = bot.send_photo(chat_id=message.chat.id, photo=media_fav, caption=resposta, reply_to_message_id=message.message_id, reply_markup=markup, parse_mode="HTML")
            mensagens_editaveis.append(mensagem.id)
        else:
            bot.send_message(chat_id=message.chat.id, text="Você não possui cartas no armazém.", reply_to_message_id=message.message_id)

    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a consulta no banco de dados.")
        conn, cursor = conectar_banco_dados()
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

        print("Página atual:", pagina)
        print("Total de páginas:", total_paginas)
        print("Offset:", offset)

            
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
                        emoji = "💐"
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
                print("Subcategoria escolhida:", subcategoria)
                choose_subcategoria_callback(call, subcategoria, cursor, conn)
            elif call.data.startswith('loja_geral'):
                loja_geral_callback(call)
            elif call.data.startswith("geral_compra_"):
                geral_compra_callback(call)
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
                            telebot.types.InlineKeyboardButton(text="Comprar Iscas", callback_data=f'c_isca_{id_usuario}_{original_message_id}')
                            ]

                        segunda_coluna = [
                            telebot.types.InlineKeyboardButton(text="Doar Cenouras", callback_data=f'doar_cenoura_{id_usuario}_{original_message_id}')
                                              ]

                        keyboard.row(*primeira_coluna)
                        keyboard.row(*segunda_coluna)

                        if result:
                            qnt_cenouras = int(result[0])
                        else:
                            qnt_cenouras = 0
                        mensagem = "Bem vindo a nossa lojinha. O que você quer levar?\n\nSaldo Atual:\n {qnt_cenouras} 🥕"
                        bot.edit_message_caption(chat_id=message.chat.id, message_id=original_message_id,caption=mensagem, reply_markup=keyboard)

                    except Exception as e:
                         print(f"Erro ao processar comando: {e}")
            elif call.data.startswith('compras_iscas_'):
                compras_iscas_callback(call)
            elif call.data.startswith("isca_"):
                isca_callback(call)
            elif call.data.startswith('aprovar_'):
                aprovar_callback(call)
            elif call.data.startswith('reprovar_'):
                reprovar_callback(call)
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
                      
def categoria_callback(call):
    try:
        categoria = call.data.replace('pescar_', '')
        ultimo_clique[call.message.chat.id] = {'categoria': categoria}
        categoria_handler(call.message, categoria)
    except Exception as e:
        print(f"Erro ao processar categoria_callback: {e}")

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

def choose_subcategoria_callback(call, subcategoria, cursor, conn):
    try:
        categoria_info = ultimo_clique.get(call.message.chat.id, {})
        categoria = categoria_info.get('categoria', '')

        if categoria.lower() == 'geral':
            evento_aleatorio = verificar_subcategoria_evento(subcategoria, cursor)
            if evento_aleatorio:
                print("Evento fixo encontrado.")
                send_card_message(call.message, evento_aleatorio)
            else:
                print("Nenhum evento fixo encontrado")
                subcategoria_handler(call.message, subcategoria, cursor, conn, None)
        else:
            print("Procedendo com a lógica normal.")
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

# Função para calcular a Distância de Levenshtein entre duas strings
def calcula_distancia_levenshtein(str1, str2):
    return Levenshtein.distance(str1, str2)
# Variável para controlar se a resposta foi dada ou não
resposta_dada = False

# Variável para controlar o temporizador
temporizador = None

# Variável para controlar o cooldown
cooldown_ativo = False

# Variável para controlar o último momento em que o comando /advinha foi ativado
ultimo_advinha = {}

import hashlib

# Função para gerar um hash único baseado no nome da subcategoria
def calcular_hash(nome_subcategoria):
    return hashlib.sha256(nome_subcategoria.encode()).hexdigest()[:8]  # Use os primeiros 8 caracteres do hash como parte do nome do arquivo

@bot.message_handler(commands=['adivinha'])
def enviar_carta_adivinhacao(message):
    global id_personagem, nome, subcategoria, resposta_dada, temporizador, cooldown_ativo
    conn, cursor = conectar_banco_dados()
    
    # Verificar se o cooldown de 10 segundos passou desde a última ativação do comando para o mesmo usuário
    agora = time.time()
    if message.from_user.id in ultimo_advinha and agora - ultimo_advinha[message.from_user.id] < 10:
        bot.reply_to(message, "Aguarde alguns segundos antes de usar este comando novamente.")
        return
    
    # Registrar o momento atual como o último momento em que o comando foi ativado para o usuário atual
    ultimo_advinha[message.from_user.id] = agora
    
    # Inserir um novo registro na tabela comandos_acionados
    query_insert = "INSERT INTO comandos_acionados (comando, usuario) VALUES (%s, %s)"
    cursor.execute(query_insert, ("advinha", message.from_user.id))
    conn.commit()
    
    # Limpar variáveis globais
    id_personagem = None
    nome = None
    subcategoria = None
    resposta_dada = False
    
    try:
        # Selecionar aleatoriamente uma carta da tabela 'personagens'
        query_personagens = "SELECT id_personagem, nome, subcategoria, emoji, categoria, imagem, cr FROM personagens ORDER BY RAND() LIMIT 1"
        cursor.execute(query_personagens)
        carta_personagem = cursor.fetchone()

        # Verificar se há uma carta de personagem
        if carta_personagem:
            id_personagem, nome, subcategoria, emoji, categoria, imagem_url, cr = carta_personagem
            categoria = categoria.capitalize()  # Ajustando a categoria para ficar em maiúsculas

            # Nome do arquivo no cache
            hash_subcategoria = calcular_hash(subcategoria)
            cache_filename = f"{id_personagem}_{nome}_{hash_subcategoria}.png"
            cache_path = os.path.join(CACHE_DIR, cache_filename)

            print("Preparando imagem...")

            # Obter a imagem do URL
            response = requests.get(imagem_url)
            if response.status_code == 200:
                # Carregar a imagem
                imagem_carta = Image.open(BytesIO(response.content))

                # Redimensionar a imagem para um tamanho menor
                tamanho = (imagem_carta.width // 2, imagem_carta.height // 2)
                imagem_carta_resized = imagem_carta.resize(tamanho)

                # Aplicar o efeito de desfoque
                imagem_carta_blurred = imagem_carta_resized.filter(ImageFilter.GaussianBlur(radius=4))

                # Salvar a imagem no cache
                imagem_carta_blurred.save(cache_path)

                print("Imagem preparada.")
                
                # Enviar a carta com efeito de desfoque
                with open(cache_path, "rb") as img_file:
                    sent_message = bot.send_photo(message.chat.id, img_file, caption=f"Qual é o nome deste personagem da categoria {categoria}?")
                    # Registrar o manipulador de próxima etapa antes do tempo limite
                    bot.register_next_step_handler(sent_message, verificar_resposta)

                print("Iniciando temporizador de 30 segundos...")
                
                # Iniciar uma nova thread para controlar o tempo limite
                temporizador = threading.Timer(30, tempo_esgotado, [message])
                temporizador.start()

                # Imprimir o tempo restante até o cancelamento do temporizador
                for i in range(30):
                    if temporizador.is_alive():
                        print(f"Tempo restante: {30 - i} segundos")
                        time.sleep(1)
                    else:
                        print("Temporizador cancelado.")
                        break
                
                # Definir o cooldown como ativo
                cooldown_ativo = True
                
                return
    except Exception as e:
        print(f"Erro ao processar o comando /advinha: {e}")

    # Em caso de falha, limpar as variáveis globais e informar ao usuário
    id_personagem = None
    nome = None
    subcategoria = None
    resposta_dada = False
    bot.reply_to(message, "Ocorreu um erro ao processar o comando. Por favor, tente novamente mais tarde.")

    # Definir o cooldown como ativo mesmo em caso de falha
    cooldown_ativo = True

# Função para verificar a resposta do usuário
def verificar_resposta(message):
    global resposta_dada, temporizador
    if not resposta_dada:
        resposta_dada = True
        if temporizador and temporizador.is_alive():
            temporizador.cancel()  # Cancelar o temporizador se ainda estiver ativo
        
        resposta_correta = nome.lower()  # Obter a resposta correta em minúsculas
        resposta_usuario = message.text.strip().lower()  # Obter a resposta do usuário em minúsculas
        
        # Exibir a contabilidade da distância de Levenshtein
        distancia = calcula_distancia_levenshtein(resposta_correta, resposta_usuario)
        print(f"Distância de Levenshtein entre '{resposta_usuario}' e '{resposta_correta}': {distancia}")
        
        # Verificar se a resposta do usuário contém pelo menos uma palavra da resposta correta
        palavras_corretas = resposta_correta.split()  # Dividir a resposta correta em palavras
        palavras_usuario = resposta_usuario.split()  # Dividir a resposta do usuário em palavras
        resposta_correta_presente = any(palavra_correta in palavras_usuario for palavra_correta in palavras_corretas)
        
        # Verificar a compatibilidade da resposta usando a Distância de Levenshtein
        if resposta_correta_presente or distancia <= 3:
            id_usuario = message.from_user.id
            valor = 3
            add_to_inventory(id_usuario, id_personagem)
            diminuir_cenouras(id_usuario, valor)
            # Definir a reação de emoji (👍) na mensagem do usuário
            set_reaction(message.chat.id, message.message_id, "👍")
            bot.reply_to(message, f"Parabéns! Você acertou o nome. A carta:\n\n{id_personagem} - {nome} \nde {subcategoria}\n\nfoi adicionada ao seu inventário.")
        else:
            bot.reply_to(message, f"Você errou... a carta era:\n\n{id_personagem} - {nome} \nde {subcategoria}.\n\nBoa sorte na próxima.")

# Função para lidar com o tempo esgotado
def tempo_esgotado(message):
    global resposta_dada
    if not resposta_dada:
        resposta_dada = True
        bot.reply_to(message, f"Tempo esgotado!\n\n A carta era {id_personagem} - {nome} \nde {subcategoria}.\n\nBoa sorte na próxima.")
        bot.clear_step_handler_by_chat_id(message.chat.id)

        # Definir o cooldown como inativo quando o tempo esgotar
        cooldown_ativo = False
        
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
        
        
def compras_iscas_callback(call):
    try:
        chat_id = call.message.chat.id
        message_data = call.data
        parts = message_data.split('_')
        categoria = parts[1]
        id_usuario = parts[2]
        original_message_id = parts[3]
        conn, cursor = conectar_banco_dados()
        id_usuario = call.from_user.id
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        if result:
            qnt_cenouras = int(result[0])
        else:
            qnt_cenouras = 0
        if qnt_cenouras >= 5:
            mensagem = f"Você tem {qnt_cenouras} cenouras. Deseja usar 5 para comprar iscas?"
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton(text="Sim", callback_data=f'confirmar_compra_iscas_{id_usuario}_{original_message_id}'),
                telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')
            )
            imagem_url = "URL_DA_SUA_IMAGEM"
            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=original_message_id,
                reply_markup=keyboard,
                media=telebot.types.InputMediaPhoto(media=imagem_url, caption=mensagem)
            )
        else:
            bot.send_message(call.message.chat.id, "Você não tem cenouras suficientes para comprar iscas.")
    
    except Exception as e:
        print(f"Erro ao processar compras_iscas_callback: {e}")

def isca_callback(call):
    try:
        chat_id = call.message.chat.id
        message_data = call.data
        parts = message_data.split('_')
        id_usuario = parts[1]
        original_message_id = parts[2]

        conn, cursor = conectar_banco_dados()
        id_usuario = call.from_user.id
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        if result:
            qnt_cenouras = int(result[0])
        else:
            qnt_cenouras = 0
        if qnt_cenouras >= 5:
            mensagem = f"Você tem {qnt_cenouras} cenouras. Deseja usar 5 para comprar uma isca?"
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton(text="Sim", callback_data=f'confirmar_compra_isca_{id_usuario}_{original_message_id}'),
                telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')
            )
            imagem_url = "URL_DA_SUA_IMAGEM"
            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=original_message_id,
                reply_markup=keyboard,
                media=telebot.types.InputMediaPhoto(media=imagem_url, caption=mensagem)
            )
        else:
            bot.send_message(call.message.chat.id, "Você não tem cenouras suficientes para comprar uma isca.")
    
    except Exception as e:
        print(f"Erro ao processar isca_callback: {e}")
        
def aprovar_callback(call):
    try:
        data = call.data.replace('aprovar_', '').strip().split('_')
        data_atual = datetime.now().strftime("%Y-%m-%d")
        hora_atual = datetime.now().strftime("%H:%M:%S")
        
        # Adicione instruções de debug para todas as variáveis relevantes
        print("Data:", data)
        print("Data atual:", data_atual)
        print("Hora atual:", hora_atual)
        print(len(data))
        if len(data) == 2:
            conn, cursor = conectar_banco_dados()
            id_usuario, id_personagem = data
            
            # Adicione instruções de debug para variáveis do banco de dados
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
            print(f"eu: {eu}, voce: {voce}, user_id: {user_id}, call.from_user.id: {call.from_user.id}")

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

def diminuir_cenouras(id_usuario, valor):
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
                print(f"Iscas diminuídas para o usuário {id_usuario} ({nome_usuario}).")
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
            SELECT w.id_personagem, p.id_personagem, p.nome AS nome_personagem, p.subcategoria, p.emoji
            FROM wishlist w
            JOIN personagens p ON w.id_personagem = p.id_personagem
            WHERE w.id_usuario = {id_usuario}
        """

        cursor.execute(sql_wishlist)
        cartas_wishlist = cursor.fetchall()

        if cartas_wishlist:
            cartas_removidas = []

            for carta_wishlist in cartas_wishlist:
                id_personagem_wishlist = carta_wishlist[0]
                id_carta_wishlist = carta_wishlist[1]
                nome_carta_wishlist = carta_wishlist[2]
                subcategoria_carta_wishlist = carta_wishlist[3]
                emoji_carta_wishlist = carta_wishlist[4]
                cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (id_usuario, id_personagem_wishlist))
                existing_inventory_count = cursor.fetchone()[0]
                inventory_exists = existing_inventory_count > 0

                if inventory_exists:
                    cursor.execute("DELETE FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                                   (id_usuario, id_personagem_wishlist))
                    cartas_removidas.append(
                        f"{emoji_carta_wishlist} {id_carta_wishlist} - {nome_carta_wishlist} de {subcategoria_carta_wishlist}")

            sql_atualizada = f"""
                SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria
                FROM personagens p
                JOIN wishlist w ON p.id_personagem = w.id_personagem
                WHERE w.id_usuario = {id_usuario}
            """

            cursor.execute(sql_atualizada)
            cartas_atualizadas = cursor.fetchall()

            if cartas_atualizadas:
                lista_wishlist_atualizada = f"⭐️ | Cartas no armazem de {message.from_user.first_name}:\n\n"
                for carta_atualizada in cartas_atualizadas:
                    emoji_carta = carta_atualizada[0]
                    id_carta = carta_atualizada[1]
                    nome_carta = carta_atualizada[2]
                    subcategoria_carta = carta_atualizada[3]
                    lista_wishlist_atualizada += f"{emoji_carta} {id_carta} - {nome_carta} de {subcategoria_carta}\n"

                bot.send_message(message.chat.id, lista_wishlist_atualizada, reply_to_message_id=message.message_id)
            else:
                bot.send_message(message.chat.id, "Sua Wishlist está vazia :)", reply_to_message_id=message.message_id)

            if cartas_removidas:
                resposta = f"Algumas cartas foram removidas da wishlist porque já estão no inventário:\n{', '.join(map(str, cartas_removidas))}"
                bot.send_message(message.chat.id, resposta, reply_to_message_id=message.message_id)

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

@bot.message_handler(commands=['removew'])
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
        print("Usuário não está banido. Pode pescar.")
        qtd_iscas = verificar_giros(message.from_user.id)
        if qtd_iscas == 0:
            mensagem_iscas = "Você está sem iscas."
            bot.send_message(message.chat.id, mensagem_iscas, reply_to_message_id=message.message_id)
        else:
            if not verificar_tempo_passado(message.chat.id):
                print("Tempo insuficiente passado desde a última interação. Aguarde a próxima rodada.")
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
        print(f"Carta {id_personagem} adicionada ao inventario de {id_usuario}")
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
        call = message
        chat_id = message.chat.id
        eu = call.from_user.id
        voce = message.reply_to_message.from_user.id
        seunome = message.reply_to_message.from_user.first_name
        meunome = message.from_user.first_name
        message = message
        bot_id = 6405224208
        categoria = call.text.replace('/troca', '')
        minhacarta = call.text.split()[1]
        suacarta = call.text.split()[2]

        if voce == bot_id:
            bot.send_message(chat_id, "Você não pode fazer trocas com a Mabi :(", reply_to_message_id=message.message_id)
            return
        
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

        keyboard = telebot.types.InlineKeyboardMarkup()

        if voce != bot_id:
            primeiro = [
                telebot.types.InlineKeyboardButton(text="✅",
                                                   callback_data=f'troca_sim_{eu}_{voce}_{minhacarta}_{suacarta}_{chat_id}'),
                telebot.types.InlineKeyboardButton(text="❌", callback_data=f'troca_nao_{eu}_{voce}_{minhacarta}_{suacarta}_{chat_id}'),
            ]
            keyboard.add(*primeiro)

        image_url = "https://telegra.ph/file/8672c8f91c8e77bcdad45.jpg"
        bot.send_photo(chat_id, image_url, caption=texto, reply_markup=keyboard, reply_to_message_id=message.reply_to_message.message_id)
    except Exception as e:
        print(f"Erro durante a troca: {e}")
    finally:
        print("teste")

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
            "SELECT id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'amor' ORDER BY RAND() LIMIT 1",
            (subcategoria,))
        evento_aleatorio = cursor.fetchone()
        if evento_aleatorio:
            print(f"Evento fixo aleatório: {evento_aleatorio}")
            chance = random.randint(1, 100)

            if chance <= 100:
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
      
while True:
    try:
        if __name__ == "__main__":
            bot.polling(none_stop=True)
        else:
            bot.polling()
    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente