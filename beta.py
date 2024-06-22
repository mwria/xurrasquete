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
from PIL import Image
import io
from io import BytesIO
from telebot import types
import functools
import json

bot = telebot.TeleBot("6723799817:AAFmSoj3IixvhZQuhSuai6VWNIpGXEviit8")
# mabi
#bot = telebot.TeleBot("6405224208:AAEPH9c37lTGcFpFVxfIwU4zjthdcLkzZJc")

def db_config():
    return {
        'host': '127.0.0.1',
        'database': 'garden',
        'user': 'root',
        'password': '#Folkevermore13'
    }

# Dicionário para armazenar o horário da última interação por chat ID
ultima_interacao = {}
armazem_info = {}
cartas_legenda = {}
# Dicionário temporário para armazenar informações sobre o último clique de botão por usuário
ultimo_clique = {}
# Fora da função principal, antes de qualquer função
categoria_escolhida = {}
mensagens_editaveis = []
cesta_info = []
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

def verificar_giros(id_pessoa):
    try:
        conn, cursor = conectar_banco_dados()

        try:
            # Consulta SQL para obter a quantidade de iscas para um usuário específico
            query = f"SELECT iscas FROM usuarios WHERE id_usuario = {id_pessoa}"

            # Executar a consulta
            cursor.execute(query)

            # Obter o resultado da consulta
            resultado = cursor.fetchone()

            if resultado:
                # O resultado é uma tupla, e o valor desejado está na primeira posição
                qtd_iscas = int(resultado[0])
                return qtd_iscas
            else:
                return 0

        except Exception as e:
            print(f"Erro ao executar a consulta de verificação de giros: {e}")

    finally:
            # Fechar o cursor e a conexão
            cursor.close()
            conn.close()

def verificar_id_na_tabela(id_pessoa, tabela, coluna_iduser):
    try:
        conn, cursor = conectar_banco_dados()

        # Execute a consulta para verificar se o ID da pessoa está na tabela na coluna especificada
        cursor.execute(f"SELECT COUNT(*) FROM {tabela} WHERE {coluna_iduser} = %s", (id_pessoa,))

        # Obtenha o resultado da contagem
        resultado_contagem = cursor.fetchone()[0]

        # Se a contagem for maior que 0, o ID está presente, retorne um erro
        if resultado_contagem > 0:
            raise ValueError(f"ID {id_pessoa} já está na tabela '{tabela}' na coluna '{coluna_iduser}'")

    except mysql.connector.Error as err:
        print(f"Erro ao verificar ID {id_pessoa} na tabela '{tabela}': {err}")

    finally:
        fechar_conexao(cursor, conn)


@bot.message_handler(commands=['iduser'])
def handle_iduser_command(message):

    if message.reply_to_message:
        idusuario = message.reply_to_message.from_user.id
        bot.send_message(chat_id=message.chat.id, text=f"Seu ID é {idusuario}")

@bot.message_handler(commands=['idchat'])
def handle_idchat_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"O ID deste chat é {chat_id}")


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

# Função para verificar se um valor existe em uma coluna da tabela 'usuarios'
def verificar_valor_existente(coluna, valor):
    try:
        conn, cursor = conectar_banco_dados()

        # Verificar se o valor existe na coluna especificada da tabela 'usuarios'
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
    # Extrair o nome de usuário do comando
    command_parts = message.text.split()

    if len(command_parts) != 2:
        bot.send_message(message.chat.id,
                         "Formato incorreto. Use /setuser seguido do nome desejado, por exemplo: /setuser novouser.")
        return

    nome_usuario = command_parts[1].strip()

    try:
        conn = mysql.connector.connect(**db_config())
        cursor = conn.cursor()

        # Verificar se o ID do usuário já existe na tabela 'usuarios'
        if verificar_valor_existente("id_usuario", message.from_user.id):
            # Atualizar a coluna 'nome_usuario' com o novo nome fornecido
            query = "UPDATE usuarios SET nome_usuario = %s WHERE id_usuario = %s"
            cursor.execute(query, (nome_usuario, message.from_user.id))
            conn.commit()

            bot.send_message(message.chat.id, f"O nome de usuário foi alterado para '{nome_usuario}'.")
        else:
            # Caso o ID não exista, registrar um novo usuário
            query = "INSERT INTO usuarios (id_usuario, nome_usuario) VALUES (%s, %s)"
            cursor.execute(query, (message.from_user.id, nome_usuario))
            conn.commit()

            bot.send_message(message.chat.id, f"O nome de usuário '{nome_usuario}' foi registrado com sucesso.")

    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao processar comando /setuser: {err}")

    finally:
        fechar_conexao(cursor, conn)


# Função para processar o nome de usuário digitado pelo usuário
def processar_nome_usuario(message):
    nome_usuario = message.text.strip()

    # Verificar se o nome de usuário já existe na tabela 'usuarios'
    if verificar_valor_existente("nome_usuario", nome_usuario):
        bot.send_message(message.chat.id, "O nome de usuário já está em uso.")
        bot.send_message(message.chat.id, "Por favor, escolha um nome de usuário diferente:")
        bot.register_next_step_handler(message, processar_nome_usuario)
    else:
        try:
            conn = mysql.connector.connect(**db_config())
            cursor = conn.cursor()

            # Atualizar a coluna 'nome_usuario' com o nome fornecido
            query = "UPDATE usuarios SET nome_usuario = %s WHERE id_usuario = %s"
            cursor.execute(query, (nome_usuario, message.from_user.id))
            conn.commit()

            bot.send_message(message.chat.id, f"O nome de usuário '{nome_usuario}' foi registrado com sucesso.")

        except mysql.connector.Error as err:
            bot.send_message(message.chat.id, f"Erro ao registrar nome de usuário: {err}")

        finally:
            fechar_conexao(cursor, conn)

def registrar_usuario(id_usuario, nome_usuario, username):
    try:
        conn, cursor = conectar_banco_dados()

        # Verificar se o usuário já existe na tabela 'usuarios'
        if verificar_valor_existente("id_usuario", id_usuario):
            print(f"O usuário com ID {id_usuario} já existe na tabela. Nenhum novo registro é necessário.")
            return

        # Inserir novo registro na tabela 'usuarios'
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

        # Verificar se o usuário já existe na tabela
        if not verificar_valor_existente("id_usuario", id_usuario):
            # Se não existir, inserir um novo registro com valores padrão 0
            query = f"INSERT INTO usuarios (id_usuario, {coluna}, qntcartas, cenouras, iscas, pp) VALUES (%s, %s, 0, 0, 0, 0)"
            cursor.execute(query, (id_usuario, valor))
            conn.commit()
            print(f"Novo registro adicionado para o ID do usuário {id_usuario}")

        else:
            # Se o usuário existir, atualizar o valor na coluna especificada
            query = f"UPDATE usuarios SET {coluna} = %s WHERE id_usuario = %s"
            cursor.execute(query, (valor, id_usuario))
            conn.commit()
            print(f"Valor {valor} registrado na coluna {coluna} para o ID do usuário {id_usuario}")

    except mysql.connector.Error as err:
        print(f"Erro ao registrar {coluna}: {err}")

    finally:
        fechar_conexao(cursor, conn)
# Função para registrar o ID do usuário na tabela 'usuarios'

@bot.message_handler(commands=['start'])
def start_comando(message):
    user_id = message.from_user.id
    nome_usuario = message.from_user.first_name  # Obtém o nome do usuário
    username = message.chat.username
    print(f"Comando /start recebido. ID do usuário: {user_id} - {nome_usuario}")

    # Verifica se o ID já está na tabela `ban`
    try:
        verificar_id_na_tabela(user_id, "ban", "iduser")
        print("ID não encontrado na tabela `ban`. Pode prosseguir.")

        # Verifica se o ID está na tabela `beta`
        if verificar_id_na_tabelabeta(message.from_user.id):
            # Registra o usuário e o nome
            registrar_usuario(user_id, nome_usuario, username)

            # Atualiza o nome do usuário na tabela
            registrar_valor("nome_usuario", nome_usuario, user_id)

            keyboard = telebot.types.InlineKeyboardMarkup()
            image_path = "jungk.jpg"
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo,
                               caption='Seja muito bem-vindo ao MabiGarden! Entre, busque uma sombra e aproveite a estadia.',
                               reply_markup=keyboard)
        else:
            # Usuário não está na tabela `beta`, envia mensagem de visitante não convidado
            bot.send_message(message.chat.id, "Ei visitante, você não foi convidado! 😡")


    except ValueError as e:
        print(f"Erro: {e}")
        # Se o ID já está na tabela `ban`, envia a mensagem de banimento
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)


def buscar_cartas_usuario(id_usuario, id_personagem):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta SQL para buscar os IDs das cartas relacionadas ao ID do usuário
        query = "SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s"
        cursor.execute(query, (id_usuario, id_personagem))
        resultado = cursor.fetchone()

        return resultado[0] if resultado else 0

    except mysql.connector.Error as err:
        print(f"Erro ao buscar cartas {id_personagem} do usuário {id_usuario}: {err}")

    finally:
        fechar_conexao(cursor, conn)



@bot.message_handler(commands=['setfav'])
def set_fav_command(message):
    # Extrai o ID do personagem do comando
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2 and command_parts[1].isdigit():
        id_personagem = int(command_parts[1])
        print(id_personagem)

        # Obtém o ID do usuário da mensagem
        id_usuario = message.from_user.id
        nome_personagem = obter_nome(id_personagem)
        print(nome_personagem)
        # Verifica a quantidade de cartas do personagem no inventário do usuário
        qtd_cartas = buscar_cartas_usuario(id_usuario, id_personagem)

        if qtd_cartas > 0:
            # O usuário possui o personagem no inventário
            atualizar_coluna_usuario(id_usuario, 'fav', id_personagem)
            bot.send_message(message.chat.id, f"❤ {id_personagem} — {nome_personagem} definido como favorito.")
        else:
            # O usuário não possui o personagem no inventário
            bot.send_message(message.chat.id, f"Você não possui {id_personagem} no seu inventário, que tal ir pescar?")


# Comando /setnome
@bot.message_handler(commands=['setnome'])
def set_nome_command(message):
    # Extrai os parâmetros do comando
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) == 2:
        novo_nome = command_parts[1]

        # Obtém o ID do usuário da mensagem
        id_usuario = message.from_user.id

        # Atualiza a coluna 'nome' na tabela 'usuarios'
        atualizar_coluna_usuario(id_usuario, 'nome', novo_nome)

        # Envia uma confirmação ao usuário
        bot.send_message(message.chat.id, f"Nome atualizado para: {novo_nome}")
    else:
        bot.send_message(message.chat.id,
                         "Formato incorreto. Use /setnome seguido do novo nome, por exemplo: /setnome Maria Hashi")


@bot.message_handler(commands=['eu'])
def me_command(message):
    # Obtém o ID do usuário da mensagem
    id_usuario = message.from_user.id

    # Consulta SQL para verificar se o usuário existe na tabela
    query_verificar_usuario = "SELECT 1 FROM usuarios WHERE id_usuario = %s"

    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_verificar_usuario, (id_usuario,))
        usuario_existe = cursor.fetchone()

        if usuario_existe:
            # Chama a função para atualizar a quantidade de cartas
            qnt_carta(id_usuario)

            # Consulta SQL para obter o perfil do usuário, incluindo o personagem favorito da tabela 'personagens' ou 'evento'
            query_obter_perfil = """
                SELECT 
                    u.nome, u.nome_usuario, u.fav, u.qntcartas, u.cenouras, u.iscas, u.bio, u.musica, u.pp,
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
                nome, nome_usuario, fav, qntcartas, cenouras, iscas, bio, musica, link_pp, nome_fav, imagem_fav = perfil

                # Monta a resposta com os dados do perfil, incluindo a foto do personagem favorito
                resposta = f"<b>Perfil de {nome_usuario}</b>\n\n" \
                           f"✨ Fav: {fav} — {nome_fav}\n\n" \
                           f"‍🧑‍🌾 Camponês: {nome}\n" \
                           f"🐟 Peixes: {qntcartas}\n" \
                           f"🥕 Cenouras: {cenouras}\n" \
                           f"🪝 Iscas: {iscas}\n\n" \
                           f"BIO ♡: {bio}\n\n" \
                           f"🎧 #NP: {musica}"

                # Envia a resposta ao usuário com a mídia e a legenda
                enviar_perfil(message.chat.id, resposta, link_pp, imagem_fav)


            else:
                bot.send_message(message.chat.id, "Perfil não encontrado.")

        else:
            # Se o usuário não existir, solicita que inicie o bot
            bot.send_message(message.chat.id, "Você ainda não iniciou o bot. Use /start para começar.")

    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao verificar perfil: {err}")

    finally:
        fechar_conexao(cursor, conn)

def enviar_perfil(chat_id, legenda, link_pp, imagem_fav):
    # Adicione a formatação HTML apenas para a linha "Perfil de mariahashi"


    if link_pp:
        # Verifica se a foto do perfil é um arquivo multimídia (foto, vídeo ou gif)
        if link_pp.startswith(('http://', 'https://')):
            if link_pp.lower().endswith(('.mp4', '.gif')):
                bot.send_animation(chat_id, link_pp, caption=legenda, parse_mode="HTML")
            else:
                bot.send_photo(chat_id, link_pp, caption=legenda, parse_mode="HTML")
        else:
            with open(link_pp, 'rb') as media:
                if link_pp.lower().endswith(('.jpg', '.jpeg', '.png')):
                    bot.send_photo(chat_id, media, caption=legenda, parse_mode="HTML")
                elif link_pp.lower().endswith(('.mp4', '.gif')):
                    bot.send_animation(chat_id, media, caption=legenda, parse_mode="HTML")

    if imagem_fav:
        # Verifica se a foto do personagem favorito é um arquivo multimídia (foto, vídeo ou gif)
        if imagem_fav.startswith(('http://', 'https://')):
            if imagem_fav.lower().endswith(('.mp4', '.gif')):
                bot.send_animation(chat_id, imagem_fav, caption=legenda, parse_mode="HTML")
            else:
                bot.send_photo(chat_id, imagem_fav, caption=legenda, parse_mode="HTML")
        else:
            with open(imagem_fav, 'rb') as media_fav:
                if imagem_fav.lower().endswith(('.jpg', '.jpeg', '.png')):
                    bot.send_photo(chat_id, media_fav, caption=legenda, parse_mode="HTML")
                elif imagem_fav.lower().endswith(('.mp4', '.gif')):
                    bot.send_animation(chat_id, media_fav, caption=legenda, parse_mode="HTML")
    elif legenda:
        bot.send_message(chat_id, legenda, parse_mode="HTML")


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
def qnt_carta(id_usuario):
    try:
        conn, cursor= conectar_banco_dados()

        # Consulta SQL para calcular e atualizar a quantidade total de cartas do usuário
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
        # Extrair o ID do personagem da chamada de callback
        id_personagem = int(call.data.split('_')[1])

        # Adapte aqui a lógica para obter a quantidade da tabela cartas
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT rodados FROM cartas WHERE id_personagem = %s", (id_personagem,))
        quantidade_personagem = cursor.fetchone()

        if quantidade_personagem is not None and quantidade_personagem[0] >= 0:
            # Se a quantidade é maior ou igual a zero, enviar a notificação
            bot.answer_callback_query(call.id, f"Esta carta foi rodada {quantidade_personagem[0]} vezes!")
        else:
            # Se a quantidade é nula ou negativa, informar que a carta não foi rodada ainda
            bot.answer_callback_query(call.id, f"Esta carta não foi rodada ainda :(!")
            bot.answer_callback_query(call.id, "Erro ao obter a quantidade da carta.")

    except Exception as e:
        print(f"Erro ao lidar com o callback: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
            conn.close()



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

        # Salvar informações sobre a lista de mensagens para uso posterior
        user_id = chat_id  # Use chat_id como user_id apenas para exemplo
        save_user_state(user_id, 'gnomes', mensagens, chat_id)

    else:
        bot.send_message(chat_id, "Não há mais personagens disponíveis.")
        # Limpar as informações temporárias da base de dados após o uso
        clear_user_state(chat_id, 'gnomes') 



@bot.message_handler(commands=['gnome'])
def gnomes(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    conn, cursor = conectar_banco_dados()

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

        if resultados_personagens:
            # Criar uma lista de mensagens
            mensagens = []
            for resultado_personagem in resultados_personagens:
                id_personagem, nome, subcategoria, categoria, quantidade_usuario, imagem_url = resultado_personagem
                mensagem = f"💌 | Personagem: \n\n{id_personagem} • {nome}\nde {subcategoria}"

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

            # Salvar temporariamente as informações na base de dados
            save_user_state(user_id, 'gnomes', mensagens, chat_id)

            # Enviar a primeira mensagem com botões
            send_message_with_buttons(chat_id, mensagens)
        else:
            bot.send_message(chat_id, f"Nenhum resultado encontrado para o nome '{nome}'.")
    finally:
        cursor.close()
        conn.close()

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


def send_message_with_buttons(chat_id, mensagens, current_index=0):
    total_count = len(mensagens)

    if current_index < total_count:
        media_url, mensagem = mensagens[current_index]
        markup = create_navigation_markup(current_index, total_count)  # Remova o terceiro argumento

        if media_url:
            bot.send_photo(chat_id, media_url, caption=mensagem, reply_markup=markup)
        else:
            bot.send_message(chat_id, mensagem, reply_markup=markup)

        # Salvar informações sobre a lista de mensagens para uso posterior
        user_id = chat_id  # Use chat_id como user_id apenas para exemplo
        save_user_state(user_id, 'gnomes', mensagens, chat_id)

    else:
        bot.send_message(chat_id, "Não há mais personagens disponíveis.")
        # Limpar as informações temporárias da base de dados após o uso
        clear_user_state(chat_id, 'gnomes')


# Funções para manipulação do estado do usuário
def save_user_state(user_id, command, data, chat_id):
    # Modificar conforme a estrutura da sua base de dados
    # Este é apenas um exemplo
    conn, cursor = conectar_banco_dados()

    try:
        cursor.execute("REPLACE INTO user_state (user_id, command, data, chat_id) VALUES (%s, %s, %s, %s)",
                       (user_id, command, json.dumps(data), chat_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def load_user_state(user_id, command):
    # Modificar conforme a estrutura da sua base de dados
    # Este é apenas um exemplo
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
        cursor.close()
        conn.close()

def clear_user_state(user_id, command):
    # Modificar conforme a estrutura da sua base de dados
    # Este é apenas um exemplo
    conn, cursor = conectar_banco_dados()

    try:
        cursor.execute("DELETE FROM user_state WHERE user_id = %s AND command = %s", (user_id, command))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def create_navigation_markup(current_index, total_count):
    markup = types.InlineKeyboardMarkup()

    buttons = []

    # Botão Anterior
    if current_index == 0:
        prev_button_text = f"⬅"
        prev_button_callback = f"prev_button_{total_count}_{total_count}"
        buttons.append(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))

        print("poo")
        
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
        
    # Botão Próximo
    if current_index < total_count - 1:
        next_button_text = f"➡️"
        next_button_callback = f"next_button_{current_index}_{total_count}"

        buttons.append(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))
        print(next_button_text, next_button_callback)
    else:
        # Se estiver na última mensagem, adicione botão para a primeira mensagem
        next_button_text = f"➡️"
        next_button_callback = f"next_button_-1_{total_count}"
        buttons.append(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))
        print(next_button_text, next_button_callback)

    markup.add(*buttons)
    return markup

# Callback para tratar a navegação entre mensagens
@bot.callback_query_handler(func=lambda call: call.data.startswith(('next_button', 'prev_button')))
def navigate_messages(call):
    try:
        chat_id = call.message.chat.id

        # Extrair valores do callback_data
        data_parts = call.data.split('_')

        if len(data_parts) == 4 and data_parts[0] in ('next', 'prev'):
            direction, current_index, total_count = data_parts[0], int(data_parts[2]), int(data_parts[3])
        else:
            raise ValueError("Callback_data com número incorreto de partes ou formato inválido.")

        # Recuperar a lista de mensagens do estado do usuário
        user_id = call.from_user.id
        mensagens, _ = load_user_state(user_id, 'gnomes')

        # Atualizar o índice para a próxima página
        if direction == 'next':
            current_index += 1
        elif direction == 'prev':
            current_index -= 1
        print(current_index)

        # Enviar a mensagem com botões e editar a mensagem existente
        media_url, mensagem = mensagens[current_index]
        markup = create_navigation_markup(current_index, len(mensagens))

        # Adicionar um caractere especial ao texto para evitar o erro "message is not modified"
        mensagem = f"{mensagem}."

        if media_url:
            media = InputMediaPhoto(media=media_url, caption=mensagem)
            bot.edit_message_media(chat_id=chat_id, message_id=call.message.message_id, media=media, reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=mensagem, reply_markup=markup)

    except Exception as e:
        print("Erro ao processar callback dos botões de navegação:", str(e))

# Função para lidar com o comando /gnomes
@bot.message_handler(commands=['gnomes'])
def gnomes(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(processar_comando_gnomes, chat_id, user_id, message)
        future.result()

def processar_comando_gnomes(chat_id, user_id, message):
    conn, cursor = conectar_banco_dados()
    try:
        nome = message.text.split('/gnomes', 1)[1].strip()

        if nome.startswith("e "):
            nome_evento = nome[1:].strip()
            sql_eventos_exatas = """
                SELECT
                    e.id_personagem,
                    e.nome,
                    e.subcategoria,
                    e.categoria,
                    NULL AS quantidade_usuario,
                    e.imagem
                FROM evento e
                WHERE e.nome = %s
            """
            sql_eventos_parciais = """
                SELECT
                    e.id_personagem,
                    e.nome,
                    e.subcategoria,
                    e.categoria,
                    NULL AS quantidade_usuario,
                    e.imagem
                FROM evento e
                WHERE e.nome LIKE %s AND e.nome <> %s
            """
            values_eventos_exatas = (nome_evento,)
            values_eventos_parciais = (f"%{nome_evento}%", nome_evento)

            cursor.execute(sql_eventos_exatas, values_eventos_exatas)
            resultados_exatos = cursor.fetchall()

            cursor.execute(sql_eventos_parciais, values_eventos_parciais)
            resultados_parciais = cursor.fetchall()

            resultados_personagens = resultados_exatos + resultados_parciais
        else:
            sql_personagens_exatas = """
                SELECT
                    p.id_personagem,
                    p.nome,
                    p.subcategoria,
                    p.categoria,
                    i.quantidade AS quantidade_usuario,
                    p.imagem
                FROM personagens p
                LEFT JOIN inventario i ON p.id_personagem = i.id_personagem AND i.id_usuario = %s
                WHERE p.nome = %s
            """
            sql_personagens_parciais = """
                SELECT
                    p.id_personagem,
                    p.nome,
                    p.subcategoria,
                    p.categoria,
                    i.quantidade AS quantidade_usuario,
                    p.imagem
                FROM personagens p
                LEFT JOIN inventario i ON p.id_personagem = i.id_personagem AND i.id_usuario = %s
                WHERE p.nome LIKE %s AND p.nome <> %s
            """
            values_personagens_exatas = (user_id, nome)
            values_personagens_parciais = (user_id, f"%{nome}%", nome)

            cursor.execute(sql_personagens_exatas, values_personagens_exatas)
            resultados_exatos = cursor.fetchall()

            cursor.execute(sql_personagens_parciais, values_personagens_parciais)
            resultados_parciais = cursor.fetchall()

            resultados_personagens = resultados_exatos + resultados_parciais

        if len(resultados_personagens) == 0:
            bot.send_message(chat_id, "Nenhum personagem encontrado.", reply_to_message_id=message.message_id)
            return

        total_paginas = (len(resultados_personagens) + 14) // 15
        user_messages[f"{chat_id}_{nome}"] = {
            'mensagens': resultados_personagens,
            'total_paginas': total_paginas
        }

        enviar_pagina_gnomes(chat_id, resultados_personagens, 1, total_paginas, nome, message.message_id)

    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()

def enviar_pagina_gnomes(chat_id, mensagens, pagina_atual, total_paginas, nome_pesquisa, reply_to_message_id=None):
    total_count = len(mensagens)
    offset = (pagina_atual - 1) * 15
    mensagens_pagina = mensagens[offset:offset + 15]

    resposta = f"🐠 Peixes de nome '{nome_pesquisa}', página {pagina_atual}/{total_paginas}:\n\n"
    for msg in mensagens_pagina:
        id_personagem, nome, subcategoria, categoria, quantidade_usuario, imagem_url = msg
        resposta += f"☁️ {id_personagem} • {nome}\nde {subcategoria}\n"

    markup = criar_marcacao_navegacao_gnomes(pagina_atual, total_paginas, nome_pesquisa)

    bot.send_message(chat_id, resposta, reply_markup=markup, parse_mode="HTML", reply_to_message_id=reply_to_message_id)

def criar_marcacao_navegacao_gnomes(pagina_atual, total_paginas, nome_pesquisa):
    markup = types.InlineKeyboardMarkup()
    prev_button_text = "⬅"
    next_button_text = "➡️"
    prev_button_callback = f"gnomes_{pagina_atual}_prev_{nome_pesquisa}"
    next_button_callback = f"gnomes_{pagina_atual}_next_{nome_pesquisa}"

    buttons = []
    if pagina_atual > 1:
        buttons.append(types.InlineKeyboardButton(text=prev_button_text, callback_data=prev_button_callback))
    if pagina_atual < total_paginas:
        buttons.append(types.InlineKeyboardButton(text=next_button_text, callback_data=next_button_callback))

    markup.add(*buttons)
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('gnomes'))
def navigate_gnomes(call):
    try:
        chat_id = call.message.chat.id
        data_parts = call.data.split('_')

        if len(data_parts) == 4:
            direction = data_parts[2]
            pagina_atual = int(data_parts[1])
            nome_pesquisa = data_parts[3]
        else:
            raise ValueError("Callback_data com número incorreto de partes ou formato inválido.")

        mensagens_data = user_messages.get(f"{chat_id}_{nome_pesquisa}", {})
        mensagens = mensagens_data.get('mensagens', [])
        total_paginas = mensagens_data.get('total_paginas', 1)

        if direction == 'next':
            pagina_atual = (pagina_atual % total_paginas) + 1
        elif direction == 'prev':
            pagina_atual = (pagina_atual - 2 + total_paginas) % total_paginas + 1

        enviar_pagina_gnomes(chat_id, mensagens, pagina_atual, total_paginas, nome_pesquisa, reply_to_message_id=call.message.message_id)

    except Exception as e:
        print("Erro ao processar callback dos botões de navegação:", str(e))
def obter_gif_url(id_personagem, id_usuario):
    conn, cursor = conectar_banco_dados()

    try:
        # Verificar se há um GIF associado ao personagem ou usuário na tabela gif
        sql_gif = """
            SELECT link
            FROM gif
            WHERE id_personagem = %s AND id_usuario = %s
        """
        values_gif = (id_personagem, id_usuario)
        print(values_gif)
        cursor.execute(sql_gif, values_gif)

        resultado_gif = cursor.fetchall()  # Use fetchall() para garantir que todos os resultados sejam lidos

        # Iterar sobre todos os resultados (embora só haja um)
        for gif in resultado_gif:
            print(gif)

        return resultado_gif[0][0] if resultado_gif else None
    finally:
        cursor.close()
        conn.close()



def verificar_evento(cursor, id_pesquisa):

    # Consulta ao banco de dados para verificar se o ID pertence a uma carta de evento
    sql = "SELECT 1 FROM evento WHERE id_personagem = %s OR nome = %s"
    cursor.execute(sql, (id_pesquisa, id_pesquisa))
    resultado = cursor.fetchone()

    return resultado is not None



@bot.message_handler(commands=['gid'])
def obter_id_e_enviar_info_com_imagem(message):
    conn, cursor = conectar_banco_dados()
    chat_id = message.chat.id

    # Extrair o ID do comando
    command_parts = message.text.split()
    if len(command_parts) == 2 and command_parts[1].isdigit():
        id_pesquisa = command_parts[1]

        # Verificar se o ID pertence a uma carta de evento
        is_evento = verificar_evento(cursor, id_pesquisa)

        if is_evento:
            # Consultar o banco de dados para obter as informações da carta de evento
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

                # Enviar informações textuais
                mensagem = f"💌 | Personagem: \n\n{id_personagem} • {nome}\nde {subcategoria}"

                # Adicionar as opções de tempo (sol, chuva) com base na quantidade de cartas do usuário
                if quantidade_usuario == None:
                    mensagem += f"\n\n🌧 | Tempo fechado..."
                elif quantidade_usuario == 1:
                    mensagem += f"\n\n{'☀  '}"
                else:
                    mensagem += f"\n\n{'☀ 𖡩'}"

                print("Verificando GIF URL...")
                # Verificar se há um vídeo associado ao personagem ou usuário na tabela gif
                gif_url = obter_gif_url(id_personagem, message.from_user.id)
                print("GIF URL:", gif_url)  # Adicionado print para verificar a URL do GIF
                if gif_url:
                    print("Enviando vídeo de teste...")
                    bot.send_video(chat_id, gif_url, caption=mensagem)
                elif imagem_url:
                    print("Enviando imagem de teste...")
                    bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=mensagem)
                else:
                    print("Enviando mensagem de teste...")
                    bot.send_message(chat_id, mensagem)
            else:
                bot.send_message(chat_id, f"Nenhum resultado encontrado para o ID '{id_pesquisa}'.")
        else:
            # Se não for um evento, continuar com o código original para cartas normais
            # Consultar o banco de dados para obter as informações, o link da imagem e a quantidade de cartas do usuário
            sql_normal = """
                SELECT
                    p.id_personagem,
                    p.nome,
                    p.subcategoria,
                    p.categoria,
                    i.quantidade AS quantidade_usuario,
                    p.imagem
                FROM personagens p
                LEFT JOIN inventario i ON p.id_personagem = i.id_personagem AND i.id_usuario = %s
                WHERE p.id_personagem = %s
            """
            values_normal = (message.from_user.id, id_pesquisa)

            cursor.execute(sql_normal, values_normal)
            resultado_normal = cursor.fetchone()

            if resultado_normal:
                id_personagem, nome, subcategoria, categoria, quantidade_usuario, imagem_url = resultado_normal

                # Enviar informações textuais
                mensagem = f"💌 | Personagem: \n\n{id_personagem} • {nome}\nde {subcategoria}"

                # Adicionar a quantidade de cartas do usuário se for maior que 1
                if quantidade_usuario is not None and quantidade_usuario > 0:
                    mensagem += f"\n\n☀ | {quantidade_usuario}⤫"
                else:
                    mensagem += f"\n\n🌧 | Tempo fechado..."

                print("Verificando GIF URL...")
                # Verificar se há um vídeo associado ao personagem ou usuário na tabela gif
                gif_url = obter_gif_url(id_personagem, message.from_user.id)
                print("GIF URL:", gif_url)  # Adicionado print para verificar a URL do GIF
                if gif_url:
                    print("Enviando vídeo de teste...")
                    bot.send_video(chat_id, gif_url, caption=mensagem)
                elif imagem_url:
                    print("Enviando imagem de teste...")
                    bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=mensagem)
                else:
                    print("Enviando mensagem de teste...")
                    bot.send_message(chat_id, mensagem)
            else:
                bot.send_message(chat_id, f"Nenhum resultado encontrado para o ID '{id_pesquisa}'.")
    else:
        bot.send_message(chat_id, "Formato incorreto. Use /gid seguido do ID desejado, por exemplo: /gid 123")

@bot.message_handler(commands=['gcateg'])
def pesquisar_cartas_por_categoria(message):
    chat_id = message.chat.id
    conn = mysql.connector.connect(**db_config())
    cursor = conn.cursor()

    # Extrair a categoria do comando
    command_parts = message.text.split()
    if len(command_parts) == 2:
        categoria_pesquisa = command_parts[1]

        # Usar a função de pesquisa_cartas_por_campo para realizar a consulta
        pesquisar_cartas_por_campo("categoria", categoria_pesquisa, "Resultados da pesquisa por Categoria:\n", chat_id)

    else:
        bot.send_message(chat_id, "Formato incorreto. Use /gcateg seguido da categoria desejada, por exemplo: /gcateg Acao")

def consultar_personagem_por_nome(nome):
    try:
        query = "SELECT id_personagem, nome, imagem FROM personagens WHERE nome LIKE %s"
        cursor.execute(query, (f"%{nome}%",))
        result = cursor.fetchone()

            # Descartar resultados não lidos
        cursor.fetchall()

        if result:
            id, nome, imagem = result
            return f"ID: {id}\nNome: {nome}\n", imagem

        else:
            return "Nenhum resultado encontrado para o nome fornecido."

    except mysql.connector.Error as err:
        return f"Erro ao executar a consulta: {err}"

    finally:
        if 'cursor' in locals():
            cursor.close()

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

        # Extrair a subcategoria da mensagem
        subcategoria = message.text.split('/cesta ', 1)[1].strip().lower() if len(message.text.split('/cesta ', 1)) > 1 else None

        if subcategoria:
            # Verificar se o comando é /cesta s, /cesta f ou /cesta fn
            if message.text.startswith('/cesta s'):
                resposta_completa = comando_cesta_s(id_usuario, subcategoria, cursor)
                if isinstance(resposta_completa, tuple):
                    subcategoria_pesquisada, lista = resposta_completa
                    foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
                    if foto_subcategoria:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        bot.send_photo(message.chat.id, foto_subcategoria, caption=resposta)
                    else:
                        resposta = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        bot.send_message(message.chat.id, resposta)
                else:
                    bot.send_message(message.chat.id, resposta_completa)

            elif message.text.startswith('/cesta f') or message.text.startswith('/cesta fn'):
                if message.text.startswith('/cesta fn'):
                    resposta_completa = comando_cesta_fn(id_usuario, subcategoria, cursor)
                    if isinstance(resposta_completa, tuple):
                        subcategoria_pesquisada, lista = resposta_completa
                        foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
                        if foto_subcategoria:
                            bot.send_photo(message.chat.id, foto_subcategoria, caption=lista)
                        else:
                            bot.send_message(message.chat.id, lista)
                    else:
                        bot.send_message(message.chat.id, resposta_completa)
                else:
                    resposta_completa = comando_cesta_f(id_usuario, subcategoria, cursor)
                    if isinstance(resposta_completa, tuple):
                        subcategoria_pesquisada, lista = resposta_completa
                        foto_subcategoria = obter_foto_subcategoria(subcategoria_pesquisada, cursor)
                        if foto_subcategoria:
                            resposta = f"🌧 | Cartas de {subcategoria_pesquisada} faltantes na cesta de {usuario}:\n\n{lista}"
                            bot.send_photo(message.chat.id, foto_subcategoria, caption=resposta)
                        else:
                            resposta = f"🌧 | Cartas de {subcategoria_pesquisada} faltantes na cesta de {usuario}:\n\n{lista}"
                            bot.send_message(message.chat.id, resposta)
                    else:
                        bot.send_message(message.chat.id, resposta_completa)

            elif message.text.startswith('/cesta c'):
                resposta_completa = comando_cesta_cs(id_usuario, subcategoria, cursor)
                if isinstance(resposta_completa, tuple):
                    categoria_pesquisada, lista = resposta_completa
                    foto_categoria = obter_foto_categoria(categoria_pesquisada, cursor)
                    if foto_categoria:
                        resposta = f"📬 | Cartas da categoria {categoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        bot.send_photo(message.chat.id, foto_categoria, caption=resposta)
                    else:
                        resposta = f"📬 | Cartas da categoria {categoria_pesquisada} na cesta de {usuario}:\n\n{lista}"
                        bot.send_message(message.chat.id, resposta)
                else:
                    bot.send_message(message.chat.id, resposta_completa)

            else:
                resposta = "Comando inválido. Use /cesta s <subcategoria>, /cesta f <subcategoria>, /cesta fn <subcategoria> ou /cesta c <categoria>."
                bot.send_message(message.chat.id, resposta)
        else:
            bot.send_message(message.chat.id, "Subcategoria não especificada. Use /cesta s <subcategoria>, /cesta f <subcategoria>, /cesta fn <subcategoria> ou /cesta c <categoria>.")

    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)

    finally:
        fechar_conexao(cursor, conn)

def obter_foto_subcategoria(subcategoria, cursor):
    sql = "SELECT imagem FROM subcategorias WHERE nomesub = %s"
    cursor.execute(sql, (subcategoria,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def obter_foto_categoria(categoria, cursor):
    sql = "SELECT imagem FROM categoria WHERE nomesub = %s"
    cursor.execute(sql, (categoria,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def comando_cesta_s(id_usuario, subcategoria, cursor):
    subcategoria = subcategoria.split(' ', 1)[1].strip().title()
    # Função para adicionar zeros à esquerda para tornar o id_personagem com 4 dígitos
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    # Consulta SQL para buscar as cartas na cesta do usuário
    sql = f"""
        SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria, i.quantidade
        FROM personagens p
        JOIN inventario i ON p.id_personagem = i.id_personagem
        WHERE i.id_usuario = {id_usuario} AND (p.subcategoria LIKE '{subcategoria}%' OR p.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
        UNION ALL
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria, i.quantidade
        FROM evento e
        JOIN inventario i ON e.id_personagem = i.id_personagem
        WHERE i.id_usuario = {id_usuario} AND (e.subcategoria LIKE '{subcategoria}%' OR e.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
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
            quantidade_carta = carta[4]
            # Mapear a quantidade para as letras correspondentes com espaçamento
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
            lista_cartas += f"{emoji_carta} {id_carta} — {nome_carta} {letra_quantidade}\n"
        # Retornar a subcategoria e a lista de cartas
        return subcategoria_carta, lista_cartas
    else:
        return f"🌧️ Sem cartas de {subcategoria} na cesta! A jornada continua..."

def comando_cesta_f(id_usuario, subcategoria, cursor):
    subcategoria = subcategoria.split(' ', 1)[1].strip().title()
    # Função para adicionar zeros à esquerda para tornar o id_personagem com 4 dígitos
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    # SQL para buscar as cartas que faltam ao usuário em uma subcategoria específica
    sql = f"""
        SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria
        FROM personagens p
        WHERE (p.subcategoria LIKE '{subcategoria}%' OR p.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
            AND NOT EXISTS (
                SELECT 1
                FROM inventario i
                WHERE i.id_usuario = {id_usuario} AND i.id_personagem = p.id_personagem
            )
        UNION ALL
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        WHERE (e.subcategoria LIKE '{subcategoria}%' OR e.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
            AND NOT EXISTS (
                SELECT 1
                FROM inventario i
                WHERE i.id_usuario = {id_usuario} AND i.id_personagem = e.id_personagem
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


def comando_cesta_fn(id_usuario, subcategoria, cursor):
    subcategoria = subcategoria.split(' ', 1)[1].strip().title()
    # Função para adicionar zeros à esquerda para tornar o id_personagem com 4 dígitos
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    # SQL para buscar as cartas que faltam ao usuário em uma subcategoria específica, excluindo eventos
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
    categoria = categoria.split(' ', 1)[1].strip().title()
    sql = f"""
        SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria
        FROM personagens p
        JOIN inventario i ON p.id_personagem = i.id_personagem
        WHERE i.id_usuario = {id_usuario} AND (p.categoria LIKE '{categoria}%' OR p.categoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{categoria}' AND tipo = 'Categoria'))
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
    


@bot.message_handler(commands=['sub'])
def sub_command(message):
    try:
        conn, cursor = conectar_banco_dados()

        # Extrair a subcategoria da mensagem
        sub_pesquisada = message.text.replace('/sub', '').strip()

        # Consultar o ID e o nome da subcategoria com base no nome
        cursor.execute("SELECT idsubcategorias, nomesub, Imagem FROM subcategorias WHERE nomesub = %s", (sub_pesquisada,))
        subcategoria_info = cursor.fetchone()

        if subcategoria_info:
            id_subcategoria, nome_sub_pesquisada, imagem_subcategoria = subcategoria_info

            # Consultar os personagens associados à subcategoria
            sql_personagens_sub = """
                SELECT p.emoji, p.id_personagem, p.nome, p.subcategoria
                FROM associacao_pessoa_subcategoria a
                JOIN personagens p ON a.id_personagem = p.id_personagem
                WHERE a.id_subcategoria = %s
            """

            cursor.execute(sql_personagens_sub, (id_subcategoria,))
            resultados = cursor.fetchall()

            if resultados:
                # Formata a lista de personagens associados
                personagens_formatados = "\n".join(f"{emoji} {id_personagem} • {nome} - {subcategoria}" for emoji, id_personagem, nome, subcategoria in resultados)

                # Envia a foto com as informações como legenda
                bot.send_photo(message.chat.id, imagem_subcategoria, caption=f"📩 | Personagens de {nome_sub_pesquisada}:\n\n{personagens_formatados}")
            else:
                bot.send_message(message.chat.id, f"Não há personagens associados à Sub {nome_sub_pesquisada}.")

        else:
            bot.send_message(message.chat.id, f"A subcategoria '{sub_pesquisada}' não foi encontrada.")

    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a consulta no banco de dados.")
        conn, cursor = conectar_banco_dados()

    finally:
        fechar_conexao(cursor, conn)

def pesquisar_cartas_por_campo(campo, valor, mensagem_resultado, chat_id, limite=5, pagina=1):
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(**db_config())
        cursor = conn.cursor()

        sql = f"SELECT id_personagem, nome, subcategoria, categoria, submenu FROM personagens WHERE {campo} LIKE %s LIMIT %s OFFSET %s"
        value = (f"%{valor}%", limite, (pagina - 1) * limite)

        cursor.execute(sql, value)
        resultados = cursor.fetchall()

        if resultados:
            mensagem = mensagem_resultado
            for resultado in resultados:
                id_personagem, nome, subcategoria, categoria, submenu = resultado
                mensagem += f"ID: {id_personagem}, Nome: {nome}, Subcategoria: {subcategoria}, Categoria: {categoria}, Submenu: {submenu}\n"
            bot.send_message(chat_id, mensagem)
        else:
            bot.send_message(chat_id, f"Nenhum resultado encontrado para o {campo} '{valor}' na página {pagina}.")
    except mysql.connector.Error as err:
        bot.send_message(chat_id, f"Erro ao executar a consulta: {err}")
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def obter_quantidade_total_cartas(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()

        # Consultar a tabela 'inventario' para obter a quantidade total de cartas do usuário
        cursor.execute("SELECT COUNT(DISTINCT id_personagem) FROM inventario WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            return 0

    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['amz'])
@bot.message_handler(commands=['armazém'])
@bot.message_handler(commands=['armazem'])
def armazem_command(message):
    try:
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        print("Usuário não está banido. Pode acessar o armazém.")

        conn, cursor = conectar_banco_dados()
        qnt_carta(message.from_user.id)

        id_usuario = message.from_user.id
        user = message.from_user
        usuario = user.first_name

        # Armazenar informações do armazém no dicionário
        armazem_info[id_usuario] = {'id_usuario': id_usuario, 'usuario': usuario}

        # Paginação
        pagina = 1  # Página inicial
        resultados_por_pagina = 15  # Número de resultados por página

        # Consulta SQL para obter a carta favorita do usuário
        query_fav_usuario = f"""
            SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, 0 AS quantidade, p.categoria
            FROM personagens p
            WHERE p.id_personagem = (
                SELECT fav
                FROM usuarios
                WHERE id_usuario = {id_usuario}
            )
        """

        # Consulta SQL principal para obter as cartas do armazém do usuário
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

        if resultados:
            markup = telebot.types.InlineKeyboardMarkup()

            # Botões de paginação
            buttons_row = [
                telebot.types.InlineKeyboardButton("◀️", callback_data=f"armazem_anterior_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("▶️", callback_data=f"armazem_proxima_{pagina}_{id_usuario}")
            ]
            markup.row(*buttons_row)
            media_fav = obter_imagem_carta(id_usuario)
            nome_fav = obter_nome_carta(id_usuario)
            quantidade_total_cartas = obter_quantidade_total_cartas(id_usuario)
            resposta = f"💌 | Cartas no armazém de {usuario}:\n\n❤️ Fav: {nome_fav}\n\n"

            for carta in resultados:
                id_carta = carta[0]
                emoji_carta = carta[1]
                nome_carta = carta[2]
                subcategoria_carta = carta[3]
                quantidade_carta = carta[4]


                    # Verificação da quantidade
                if quantidade_carta is None:
                    quantidade_carta = 0
                else:
                        # Se quantidade_carta não é nula, tenta converter para inteiro
                    quantidade_carta = int(quantidade_carta)

                # Mapear a quantidade para as letras correspondentes com espaçamento
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

                resposta += f" {emoji_carta} {id_carta} • {nome_carta} - {subcategoria_carta} {letra_quantidade}\n"

            # Adiciona a mensagem com os resultados e botões de paginação
            mensagem = bot.send_photo(message.chat.id, media_fav, caption=resposta, reply_markup=markup)
            # Adiciona o ID da mensagem à lista de mensagens editáveis para uso posterior
            mensagens_editaveis.append(mensagem.id)
        else:
            bot.send_message(message.chat.id, "Você não possui cartas no armazém.")

    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a consulta no banco de dados.")
        # Adicione qualquer outra lógica de tratamento de erro que você julgar apropriada
        # Se você quiser reiniciar a conexão com o banco de dados, pode fazer algo assim:
        conn, cursor = conectar_banco_dados()

    except ValueError as e:

        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)

    except telebot.apihelper.ApiHTTPException as e:
        print(f"Erro na API do Telegram: {e}")


    finally:
        fechar_conexao(cursor, conn)
def obter_nome(id_personagem):
    try:
        # Consulta SQL para obter o nome da carta favorita do usuário na tabela de personagens
        query_fav_usuario_personagens = f"""
            SELECT p.nome AS nome_personagem
            FROM personagens p
            WHERE p.id_personagem = {id_personagem}
        """

        # Consulta SQL para obter o nome da carta favorita do usuário na tabela de eventos
        query_fav_usuario_eventos = f"""
            SELECT e.nome AS nome_personagem
            FROM evento e
            WHERE e.id_personagem = {id_personagem}
        """

        conn, cursor = conectar_banco_dados()

        # Tentar obter o nome da carta favorita da tabela personagens
        cursor.execute(query_fav_usuario_personagens)
        resultado_fav_personagens = cursor.fetchone()

        # Se a carta favorita for encontrada na tabela personagens, obter o nome
        if resultado_fav_personagens:
            nome_carta = resultado_fav_personagens[0]  # Índice 0 representa o nome_personagem na consulta
            return nome_carta

        # Se a carta favorita não for encontrada na tabela personagens, tentar obter da tabela eventos
        cursor.execute(query_fav_usuario_eventos)
        resultado_fav_eventos = cursor.fetchone()

        # Se a carta favorita for encontrada na tabela eventos, obter o nome
        if resultado_fav_eventos:
            nome_carta = resultado_fav_eventos[0]  # Índice 0 representa o nome_personagem na consulta
            return nome_carta

        # Se nenhum nome for encontrado, retornar None
        return None

    except Exception as e:
        print(f"Erro ao obter nome da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)

    try:
        # Consulta SQL para obter a carta favorita do usuário na tabela de personagens
        query_fav_usuario_personagens = f"""
            SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, 0 AS quantidade, p.categoria, p.imagem
            FROM personagens p
            WHERE p.id_personagem = {id_personagem}
        """

        # Consulta SQL para obter a carta favorita do usuário na tabela de eventos
        query_fav_usuario_eventos = f"""
            SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria, e.imagem
            FROM evento e
            WHERE e.id_personagem = {id_personagem}
"""
        conn, cursor = conectar_banco_dados()

        # Tentar obter o nome da carta favorita da tabela personagens
        cursor.execute(query_fav_usuario_personagens)
        resultado_fav_personagens = cursor.fetchone()

        # Se a carta favorita for encontrada na tabela personagens, obter o nome
        if resultado_fav_personagens:
            nome_carta = resultado_fav_personagens[2]  # Índice 2 representa o nome_personagem na consulta
            return nome_carta

        # Se a carta favorita não for encontrada na tabela personagens, tentar obter da tabela eventos
        cursor.execute(query_fav_usuario_eventos)
        resultado_fav_eventos = cursor.fetchone()

        # Se a carta favorita for encontrada na tabela eventos, obter o nome
        if resultado_fav_eventos:
            nome_carta = resultado_fav_eventos[2]  # Índice 2 representa o nome_personagem na consulta
            return nome_carta

        # Se nenhum nome for encontrado, retornar None
        return None

    except Exception as e:
        print(f"Erro ao obter nome da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)

def obter_imagem_carta(id_usuario):
    try:
        # Consulta SQL para obter a carta favorita do usuário (personagens)
        query_fav_usuario_personagens = f"""
            SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, 0 AS quantidade, p.categoria, p.imagem
            FROM personagens p
            WHERE p.id_personagem = (
                SELECT fav
                FROM usuarios
                WHERE id_usuario = {id_usuario}
            )
        """

        # Consulta SQL para obter a carta favorita do usuário (eventos)
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

        # Tentar obter a imagem da carta favorita da tabela personagens
        cursor.execute(query_fav_usuario_personagens)
        resultado_fav_personagens = cursor.fetchone()

        # Se a carta favorita for encontrada na tabela personagens, obter a imagem
        if resultado_fav_personagens:
            id_carta_personagens = resultado_fav_personagens[0]
            query_obter_imagem_personagens = "SELECT imagem FROM personagens WHERE id_personagem = %s"
            cursor.execute(query_obter_imagem_personagens, (id_carta_personagens,))
            imagem_carta_personagens = cursor.fetchone()

            if imagem_carta_personagens:
                return imagem_carta_personagens[0]

        # Se a carta favorita não for encontrada na tabela personagens, tentar obter da tabela eventos
        cursor.execute(query_fav_usuario_eventos)
        resultado_fav_eventos = cursor.fetchone()

        # Se a carta favorita for encontrada na tabela eventos, obter a imagem
        if resultado_fav_eventos:
            id_carta_eventos = resultado_fav_eventos[0]
            query_obter_imagem_eventos = "SELECT imagem FROM evento WHERE id_personagem = %s"
            cursor.execute(query_obter_imagem_eventos, (id_carta_eventos,))
            imagem_carta_eventos = cursor.fetchone()

            if imagem_carta_eventos:
                return imagem_carta_eventos[0]

        # Se nenhuma imagem for encontrada, retornar None
        return None

    except Exception as e:
        print(f"Erro ao obter imagem da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)



@bot.callback_query_handler(func=lambda call: call.data.startswith(('armazem_anterior_', 'armazem_proxima_')))
def callback_paginacao_armazem(call):
    conn, cursor = conectar_banco_dados()
    chat_id = call.message.chat.id
    _, direcao, pagina_str, id_usuario = call.data.split('_')

    pagina = int(pagina_str)

    # Recuperar informações do armazém do dicionário
    info_armazem = armazem_info.get(int(id_usuario), {})
    id_usuario = info_armazem.get('id_usuario', '')
    usuario = info_armazem.get('usuario', '')

    # Paginação
    resultados_por_pagina = 15
    offset = (pagina - 1) * resultados_por_pagina

    # Verificar a quantidade total de cartas
    quantidade_total_cartas = obter_quantidade_total_cartas(id_usuario)
    total_paginas = quantidade_total_cartas // resultados_por_pagina + 1
    limite = resultados_por_pagina

    if pagina == 1 and call.data.startswith("armazem_anterior_"):
        # Se estiver na primeira página e clicar em anterior, ir para a última página
        pagina = total_paginas
        offset = (pagina - 1) * resultados_por_pagina
        limite = quantidade_total_cartas % resultados_por_pagina or resultados_por_pagina

    elif pagina == total_paginas and call.data.startswith("armazem_proxima_"):
        # Se estiver na última página e clicar em próxima, ir para a primeira página
        pagina = 1
        offset = 0
        limite = min(quantidade_total_cartas, resultados_por_pagina)

    else:
        # Se não estiver em nenhum dos casos anteriores, calcular a próxima página
        if call.data.startswith("armazem_anterior_"):
            pagina -= 1
        elif call.data.startswith("armazem_proxima_"):
            pagina += 1
        offset = (pagina - 1) * resultados_por_pagina

    # Consultar o banco de dados para obter os resultados da página atual
    # Consultar o banco de dados para obter os resultados da página atual
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

        # Se a quantidade total for maior que 10, adicionar botões de paginação
        if quantidade_total_cartas > 10:
            # Botões de paginação
            buttons_row = [
                telebot.types.InlineKeyboardButton("◀️", callback_data=f"armazem_anterior_{pagina}_{id_usuario}"),
                telebot.types.InlineKeyboardButton("▶️", callback_data=f"armazem_proxima_{pagina}_{id_usuario}")
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

            # Verificação da quantidade
            if quantidade_carta is None:
                quantidade_carta = 0
            else:
                # Se quantidade_carta não é nula, tenta converter para inteiro
                quantidade_carta = int(quantidade_carta)

            # Mapear a quantidade para as letras correspondentes com espaçamento
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

            resposta += f" {emoji_carta} {id_carta} • {nome_carta} - {subcategoria_carta} {letra_quantidade}\n"

        # Adicionar informação sobre a página
        resposta += f"\n{pagina}/{total_paginas}"

        # Editar a mensagem original com os novos resultados e botões de paginação
        bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption=resposta, reply_markup=markup)

    else:
        # Em caso de nenhum resultado encontrado, enviar mensagem informativa
        bot.answer_callback_query(callback_query_id=call.id, text="Nenhuma carta encontrada.")

def obter_nome_carta(id_usuario):
    try:
        # Consulta SQL para obter a carta favorita do usuário
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
            nome_carta = resultado_fav[2]  # Índice 2 representa o nome_personagem na consulta
            return nome_carta
        else:
            return None

    except Exception as e:
        print(f"Erro ao obter nome da carta: {e}")
    finally:
        fechar_conexao(cursor, conn)


# Atualização na função callback_handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        print("Callback detectado:", call.data)
        message = call.message
        conn, cursor = conectar_banco_dados()
        chat_id = call.message.chat.id

        if call.message:
            chat_id = call.message.chat.id

            # Verifica se passaram 30 segundos desde a última interação
            if not verificar_tempo_passado(chat_id):
                print(
                    f"Tempo insuficiente passado desde a última interação para o chat ID {chat_id}. Ignorando callback.")
                return
            else:
                # Marca o botão como clicado
                ultima_interacao[chat_id] = datetime.now()

            if call.data.startswith('pescar_'):
                categoria = call.data.replace('pescar_', '')
                # Registra temporariamente a categoria do último clique para este usuário
                ultimo_clique[message.chat.id] = {'categoria': categoria}
                categoria_handler(call.message, categoria)

            elif call.data.startswith('gmusica'):
                subcategoria = call.data.replace('gmusica_', '')
                # Restaura temporariamente a categoria do último clique para este usuário
                categoria_info = ultimo_clique.get(message.chat.id, {})
                categoria = categoria_info.get('categoria', '')
                id_personagem_query = "SELECT id_personagem FROM personagens WHERE subcategoria = %s"
                cursor.execute(id_personagem_query, (subcategoria,))
                results = cursor.fetchall()
                id_personagem = results[0][0]

                # Adicione uma verificação para determinar se é um evento fixo
                if categoria.lower() == 'geral':
                    evento_aleatorio = obter_carta_evento_fixo(conn)
                    if evento_aleatorio:
                        send_card_message(message, evento_aleatorio)
                    else:
                        bot.send_message(message.chat.id, "Nenhum evento disponível.")
                else:
                    subcategoria_handler(message, subcategoria, cursor, conn, id_personagem)


            elif call.data.startswith('choose_subcategoria_'):
                # Marca o botão como clicado
                subcategoria = call.data.replace('choose_subcategoria_', '')
                print("Subcategoria escolhida:", subcategoria)
                choose_subcategoria_callback(call, subcategoria, cursor, conn)

            elif call.data.startswith('loja_geral'):
                try:

                    conn, cursor = conectar_banco_dados()
                    # Consultar a tabela 'usuarios' para obter a quantidade de cenouras do usuário
                    id_usuario = call.from_user.id
                    cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                    result = cursor.fetchone()

                    if result:
                        qnt_cenouras = int(result[0])
                    else:
                        qnt_cenouras = 0
                    if qnt_cenouras >= 3:
                        # Se o usuário tiver pelo menos 5 cenouras, exibir a mensagem de compra
                        mensagem = f"Você tem {qnt_cenouras} cenouras. Deseja usar 3 para ganhar um peixe aleatório?"

                        # Adicionar os botões à mensagem
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        keyboard.row(
                            telebot.types.InlineKeyboardButton(text="Sim",
                                                               callback_data=f'geral_compra_{id_usuario}'),
                            telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')

                        )
                        imagem_url = "https://telegra.ph/file/d4d5d0af60ec66f35e29c.jpg"
                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            reply_markup=keyboard,
                            media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                                caption=mensagem)
                        )
                except Exception as e:
                    print(f"Erro ao processar a compra: {e}")

            elif call.data.startswith("geral_compra_"):
                print(call.data)

                try:
                    conn, cursor = conectar_banco_dados()

                            # Consulta SQL para obter uma carta aleatória
                    query = "SELECT * FROM personagens ORDER BY RAND() LIMIT 1"
                    cursor.execute(query)
                    carta_aleatoria = cursor.fetchone()

                    if carta_aleatoria:
                        id_personagem, nome, subcategoria, emoji, categoria, imagem, submenu, cr = carta_aleatoria[:8]
                                # Obtém o ID do usuário da mensagem
                        id_usuario = call.from_user.id
                        valor = 3
                        add_to_inventory(id_usuario,id_personagem)
                        diminuir_cenouras(id_usuario, valor)
                                # Monta a resposta com os dados da carta aleatória
                        resposta = f"🎴 Os mares trazem para sua rede:\n\n" \
                                           f"{emoji} • {id_personagem} - {nome} \nde {subcategoria}\n\nVolte sempre!" \


                                # Envia a resposta ao usuário com a mídia e a legenda
                        if imagem:
                            bot.edit_message_media(
                                chat_id=message.chat.id,
                                message_id=message.message_id,
                                media=telebot.types.InputMediaPhoto(media=imagem,
                                                                    caption=resposta)

                            )
                        else:
                            resposta1 = f"🎴 Os mares trazem para sua rede:\n\n {emoji} • {id_personagem} - {nome} \nde {subcategoria}\n\n (A carta não possui foto ainda :()"

                            imagem_url = "https://telegra.ph/file/d4d5d0af60ec66f35e29c.jpg"
                            bot.edit_message_media(
                                    chat_id=message.chat.id,
                                    message_id=message.message_id,
                                    media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                                        caption=resposta1)

                                )
                    else:
                        bot.send_message(message.chat.id, "Não foi possível encontrar uma carta aleatória.")

                except mysql.connector.Error as err:
                    bot.send_message(message.chat.id, f"Erro ao sortear carta: {err}")

                finally:
                    fechar_conexao(cursor, conn)

            elif call.data.startswith('aprovar_'):
                data = call.data.replace('aprovar_', '').strip().split('_')
                data_atual = datetime.now().strftime("%Y-%m-%d")  
                hora_atual = datetime.now().strftime("%H:%M:%S")

                if len(data) == 2:  
                    id_usuario, id_personagem = data
                    # Consultar o banco de dados para verificar se a chave única existe
                    sql_temp_select = "SELECT valor FROM temp_data WHERE id_usuario = %s AND id_personagem = %s"
                    values_temp_select = (id_usuario, id_personagem)
                    cursor.execute(sql_temp_select, values_temp_select)
                    link_gif = cursor.fetchone()

                    if link_gif:
                        # Instrução SQL para inserir os dados na tabela gif
                        sql = "INSERT INTO gif (id_personagem, id_usuario, link) VALUES (%s, %s, %s)"
                        values = (id_personagem, id_usuario, link_gif[0])

                        # Instrução SQL para inserir os dados na tabela logs
                        sql_logs = "INSERT INTO logs (id_usuario, nome_usuario, ação, horario, data, aprovado, adm) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        values_logs = (id_usuario, obter_nome_usuario_por_id(id_usuario), 'gif', hora_atual, data_atual, 'sim', call.from_user.username if call.from_user.username else call.from_user.first_name)

                        try:
                            # Executar as instruções SQL
                            cursor.execute(sql, values)
                            cursor.execute(sql_logs, values_logs)

                            # Commit para salvar as alterações no banco de dados
                            conn.commit()

                            print("Dados inseridos com sucesso.")
                            mensagem = f"Seu gif para o personagem {id_personagem} foi aceito!"
                            bot.send_message(id_usuario, mensagem)

                            # Enviar mensagem para o grupo informando a aprovação
                            grupo_id = -1002082934455  # Substitua pelo ID do seu grupo
                            nome_usuario = obter_nome_usuario_por_id(id_usuario)
                            mensagem_grupo = f"🎉 O GIF para o personagem {id_personagem} de {nome_usuario} foi aprovado! 🎉"
                            bot.send_message(grupo_id, mensagem_grupo)



                        except Exception as e:
                                                # Se ocorrer um erro, fazer rollback
                            conn.rollback()
                            print("Erro ao inserir dados:", str(e))
                        else:
                            print("Chave única não encontrada no banco de dados.")
                    else:
                        print("Formato de callback incorreto. Esperado: 'aprovar_id_usuario_id_personagem'.")



            elif call.data.startswith('reprovar_'):
                data = call.data.replace('reprovar_', '').strip().split('_')
                if len(data) == 2:  # Deve haver apenas dois elementos agora: id_usuario e id_personagem
                    id_usuario, id_personagem = data
                    mensagem = f"Seu gif para o personagem {id_personagem} foi recusado"
                    bot.send_message(id_usuario, mensagem)
                            # Enviar mensagem para o grupo informando a aprovação
                    grupo_id = -1002082934455  # Substitua pelo ID do seu grupo
                    nome_usuario = obter_nome_usuario_por_id(id_usuario)
                    mensagem_grupo = f"O GIF para o personagem {id_personagem} de {nome_usuario} foi reprovado... 😐"
                    bot.send_message(grupo_id, mensagem_grupo)
                    
                else:
                    print("Formato de callback incorreto. Esperado: 'reprovar_id_usuario_id_personagem'")

            elif call.data.startswith('loja_loja'):

                message_data = call.data.replace('loja_', '')
                print(message_data)
                if message_data == "loja":
                    try:

                        data_atual = dt_module.date.today().strftime("%Y-%m-%d")  # Usar dt_module para se referir ao módulo renomeado
                        print(data_atual)
                        cartas_loja = obter_ids_loja_do_dia(data_atual)
                        id_usuario = call.from_user.id

                        # Montar a string de placeholders para a cláusula IN
                        placeholders = ', '.join(['%s' for _ in cartas_loja])

                        # Consultar as informações das cartas na tabela personagens usando a cláusula IN
                        cursor.execute(
                            f"SELECT id_personagem, emoji, nome, subcategoria FROM personagens WHERE id_personagem IN ({placeholders})",
                            tuple(cartas_loja))
                        resultado = cursor.fetchall()

                        # Substitua 'URL_DA_SUA_IMAGEM' pela URL real da sua imagem
                        imagem_url = 'https://telegra.ph/file/a4c194082eab84886cbd4.jpg'
                        original_message_id = call.message.message_id
                        # Criar os botões
                        keyboard = telebot.types.InlineKeyboardMarkup()

                        # Primeira coluna
                        primeira_coluna = [
                            telebot.types.InlineKeyboardButton(text="☁️", callback_data=f'compra_musica_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🍰", callback_data=f'compra_filmes_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🧶", callback_data=f'compra_jogos_{id_usuario}_{original_message_id}')
                        ]

                        # Segunda coluna
                        segunda_coluna = [
                            telebot.types.InlineKeyboardButton(text="🌷", callback_data=f'compra_animanga_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🍄", callback_data=f'compra_series_{id_usuario}_{original_message_id}'),
                            telebot.types.InlineKeyboardButton(text="🍂", callback_data=f'compra_miscelanea_{id_usuario}_{original_message_id}')
                        ]

                        keyboard.row(*primeira_coluna)
                        keyboard.row(*segunda_coluna)

                        # Montar a mensagem com as cartas disponíveis
                        resultado = obter_informacoes_loja(obter_ids_loja_do_dia(data_atual))
                        mensagem = "Ah, olá! Você chegou na hora certa! Nosso pescador acabou de chegar com os peixes fresquinhos de hoje:\n\n"

                        for carta in resultado:
                            id_personagem, emoji, nome, subcategoria = carta
                            mensagem += f"{emoji} - {nome} de {subcategoria}\n"
                        original_message_id = call.message.message_id
                        # Enviar a foto com a legenda e os botões
                        bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=mensagem, reply_markup=keyboard)

                    except Exception as e:
                         print(f"Erro ao processar comando: {e}")

            elif call.data.startswith('compra_'):

                try:

                    chat_id = call.message.chat.id
                    message_data = call.data
                    parts = message_data.split('_')
                    categoria = parts[1]
                    id_usuario = parts[2]
                    original_message_id = parts[3]

                    # Obter o ID do usuário a partir da mensagem ou de onde você o obtém
                    conn, cursor = conectar_banco_dados()
                    # Consultar a tabela 'usuarios' para obter a quantidade de cenouras do usuário

                    cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                    result = cursor.fetchone()

                    if result:
                        qnt_cenouras = int(result[0])
                    else:
                        qnt_cenouras = 0
                    if qnt_cenouras >= 5:
                        # Se o usuário tiver pelo menos 5 cenouras, exibir a mensagem de compra
                        mensagem = f"Você tem {qnt_cenouras} cenouras. Deseja usar 5 para comprar um peixe da categoria {categoria}?"

                        # Adicionar os botões à mensagem
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        keyboard.row(
                            telebot.types.InlineKeyboardButton(text="Sim",
                                                               callback_data=f'confirmar_compra_{categoria}_{id_usuario}'),
                            telebot.types.InlineKeyboardButton(text="Não", callback_data='cancelar_compra')

                        )
                        imagem_url = "https://telegra.ph/file/d4d5d0af60ec66f35e29c.jpg"
                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            reply_markup= keyboard,
                            media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                                caption=mensagem)
                        )
                except Exception as e:
                    print(f"Erro ao processar a compra: {e}")


                finally:
                    fechar_conexao(cursor, conn)

            elif call.data.startswith("confirmar_compra_"):
                try:
                    data_atual = dt_module.date.today().strftime("%Y-%m-%d")  # Usar dt_module para se referir ao módulo renomeado

                    parts = call.data.split('_')
                    categoria = parts[2]
                    id_usuario = parts[3]

                    # Consultar a tabela 'loja' para obter uma carta da categoria específica e do dia atual
                    cursor.execute(
                        "SELECT id_personagem FROM loja WHERE categoria = %s AND data = %s ORDER BY RAND() LIMIT 1",
                        (categoria, data_atual)
                    )
                    carta_comprada = cursor.fetchone()

                    if carta_comprada:
                        # Aqui você pode processar a carta comprada conforme necessário
                        id_personagem = carta_comprada[0]
                        print(f"{id_usuario} comprou a carta com ID {id_personagem} da categoria {categoria}.")
                        add_to_inventory(id_usuario, id_personagem)
                        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                        quantidade = cursor.fetchone()
                        res = functools.reduce(lambda sub, ele: sub * 10 + ele, quantidade)
                        valor = 5
                        diminuir_cenouras(id_usuario, valor)

                        imagem_url = "https://telegra.ph/file/961684eb161b24dc534e0.jpg"
                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                                caption=f"Você comprou a carta com ID {id_personagem} da categoria {categoria}.")
                        )
                    else:
                        print(f"Nenhuma carta disponível para compra na categoria {categoria} hoje.")

                except Exception as e:
                    print(f"Erro ao processar a compra: {e}")

                finally:
                    fechar_conexao(cursor, conn)
                    
                    
            elif call.data.startswith('troca_'):
                try:
                    # Remova o prefixo 'troca_sim_' ou 'troca_nao_'
                    message_data = call.data.replace('troca_sim_', '').replace('troca_nao_', '')

                    # Separe os dados usando o caractere '_'
                    parts = message_data.split('_')

                    # Verifique se há pelo menos cinco partes
                    if len(parts) >= 5:
                        eu, voce, minhacarta, suacarta, message = parts
                        chat_id = call.message.chat.id if call.message else None
                        user_id = call.from_user.id if call.from_user else None
                        print(f"eu: {eu}, voce: {voce}, user_id: {user_id}, call.from_user.id: {call.from_user.id}")

                        # Converta os IDs para inteiros
                        eu = int(eu)
                        voce = int(voce)

                        # Verifique se o usuário que pressionou o botão é o mesmo que enviou o comando
                        if user_id in [eu, voce]:
                            if call.data.startswith('troca_sim_'):
                                # Caso "Sim"
                                if eu != user_id:
                                    if int(voce) == 6127981599:
                                        bot.edit_message_caption(chat_id=chat_id,
                                                                caption="Você não pode fazer trocas com a Mabi :(")
                                    elif voce == eu:
                                        bot.edit_message_caption(chat_id=chat_id,
                                                                caption="Você não pode fazer trocas consigo mesmo!")
                                    else:
                                        # Se não for o mesmo usuário, prossiga com a troca
                                        realizar_troca(call.message, eu, voce, minhacarta, suacarta, chat_id)
                                else:
                                    bot.answer_callback_query(callback_query_id=call.id,
                                                            text="Você não pode aceitar seu próprio lanche.")

                            elif call.data.startswith('troca_nao_'):
                                if chat_id and call.message:
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
                    print(f"Erro ao processar botão inline: {e}")
                    chat_id = call.message.chat.id if call.message else None
                    bot.edit_message_caption(chat_id=chat_id,
                                            message_id=call.message.message_id,
                                            caption="Alguém não tem o lanche enviado.\nQue tal olhar sua cesta novamente?")

                finally:
                                fechar_conexao(cursor, conn)
            elif call.data.startswith('cenourar_sim_'):
                print(call.data)
                novo = call.data.replace('cenourar_sim_', '').strip()
                print("novo:", novo)
                id_usuario, id_personagem = novo.split('_')
                update_cartas_counters(id_personagem)
                print("id usuario", id_usuario, "id", id_personagem)
                cenourar_carta(message, cursor, id_usuario, id_personagem)

            elif call.data.startswith('cenourar_nao_'):
                id_usuario, id_personagem = call.data.split('_')
                bot.send_message(message.chat.id, "Você escolheu não cenourar a carta.")

            fechar_conexao(cursor, conn)

    except Exception as e:
        print(f"Erro ao processar botão inline: {e}")


def send_notification(chat_id, message_text):
    try:
        # Enviar mensagem com o método send_message da API do Telegram
        bot.send_message(chat_id, message_text)
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")

def diminuir_cenouras(id_usuario, valor):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta para obter a quantidade atual de cenouras do usuário
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            cenouras_atuais = int(resultado[0])  # Convertendo para inteiro
            # Verifica se há cenouras suficientes para diminuir
            if cenouras_atuais >= valor:
                # Atualiza a quantidade de cenouras no banco de dados
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

        # Consulta para obter a quantidade atual de iscas do usuário
        cursor.execute("SELECT iscas FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            iscas_atuais = int(resultado[0])  # Convertendo para inteiro

            # Verifica se há iscas suficientes para diminuir
            if iscas_atuais >= quantidade:
                # Atualiza a quantidade de iscas no banco de dados
                nova_quantidade = iscas_atuais - quantidade
                cursor.execute("UPDATE usuarios SET iscas = %s WHERE id_usuario = %s", (nova_quantidade, id_usuario))
                print(f"Iscas diminuídas para o usuário {id_usuario}.")
                conn.commit()
            else:
                print("Erro: Não há iscas suficientes para diminuir.")
        else:
            print("Erro: Usuário não encontrado.")

    except Exception as e:
        print(f"Erro ao diminuir iscas: {e}")

    finally:
        fechar_conexao(cursor, conn)


# Função para verificar se passaram 30 segundos desde a última interação
def verificar_tempo_passado(chat_id):
    if chat_id in ultima_interacao:
        tempo_passado = datetime.now() - ultima_interacao[chat_id]
        return tempo_passado.total_seconds() >=2
    else:
        return True  # Permite o processamento se não houve interação anterior

@bot.message_handler(commands=['wishlist'])
def verificar_cartas(message):
    try:
        conn, cursor = conectar_banco_dados()

        id_usuario = message.from_user.id

        # Consulta SQL para verificar se há correspondências entre as cartas na wishlist e no inventário
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

                # Verificar se a carta da wishlist existe no inventário
                cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (id_usuario, id_personagem_wishlist))
                existing_inventory_count = cursor.fetchone()[0]
                inventory_exists = existing_inventory_count > 0

                if inventory_exists:
                    # Remover a carta da wishlist que também está no inventário
                    cursor.execute("DELETE FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                                   (id_usuario, id_personagem_wishlist))
                    cartas_removidas.append(
                        f"{emoji_carta_wishlist} {id_carta_wishlist} - {nome_carta_wishlist} de {subcategoria_carta_wishlist}")

            # Consulta SQL para obter a lista atualizada da wishlist
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

                bot.send_message(message.chat.id, lista_wishlist_atualizada)
            else:
                bot.send_message(message.chat.id, "Seu armazém está vazio.")

            if cartas_removidas:
                resposta = f"Algumas cartas foram removidas do armazém porque já estão no inventário:\n{', '.join(map(str, cartas_removidas))}"
                bot.send_message(message.chat.id, resposta)

        else:
            bot.send_message(message.chat.id, "Seu armazém está vazio.")

    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a consulta no banco de dados.")

    finally:
        conn.commit()  # Commit para efetivar as alterações
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['addw'])
def add_to_wish(message):
    try:
        chat_id = message.chat.id
        id_usuario = message.from_user.id
        # Extrair a categoria do comando
        command_parts = message.text.split()
        if len(command_parts) == 2:
            id_personagem = command_parts[1]

            conn, cursor = conectar_banco_dados()

            # Verificar se a carta já existe na wishlist
            cursor.execute("SELECT COUNT(*) FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                           (id_usuario, id_personagem))
            existing_wishlist_count = cursor.fetchone()[0]
            wishlist_exists = existing_wishlist_count > 0

            if wishlist_exists:
                bot.send_message(chat_id, "Você já possui essa carta na wishlist!")
            else:
                # Verificar se a carta já existe no inventário
                cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (id_usuario, id_personagem))
                existing_inventory_count = cursor.fetchone()[0]
                inventory_exists = existing_inventory_count > 0

                if inventory_exists:
                    bot.send_message(chat_id, "Você já possui essa carta no inventário!")
                else:
                    # Se a carta não existe na wishlist nem no inventário, inserir na wishlist
                    cursor.execute("INSERT INTO wishlist (id_personagem, id_usuario) VALUES (%s, %s)",
                                   (id_personagem, id_usuario))
                    bot.send_message(chat_id, "Carta adicionada à sua wishlist!\nBoa sorte!")

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

        # Extrair a categoria do comando
        command_parts = message.text.split()
        if len(command_parts) == 2:
            id_personagem = command_parts[1]

        # Print relevant information for debugging
        print(f"ID do usuário: {id_usuario}")
        print(f"ID da carta: {id_personagem}")

        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT COUNT(*) FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                       (id_usuario, id_personagem))
        existing_carta_count = cursor.fetchone()[0]

        # Verificar se a carta existe na wishlist (se count for maior que zero)
        if existing_carta_count > 0:
            # Se a carta existe, removê-la da wishlist
            cursor.execute("DELETE FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                           (id_usuario, id_personagem))
            bot.send_message(chat_id=chat_id, text="Carta removida da sua wishlist!")
        else:
            bot.send_message(chat_id=chat_id, text="Você não possui essa carta na wishlist.")

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao remover carta da wishlist: {err}")

    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['cenourar'])
def cenoura(message):
    try:
        conn, cursor = conectar_banco_dados()

        # Verifica se o usuário está banido antes de permitir a pesca
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        print("Usuário não está banido. Pode cenourar.")
        id_usuario = message.from_user.id
        id_personagem = message.text.replace('/cenourar', '').strip()
        print(id_personagem)

        cursor.execute(
            "SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
            (id_usuario, id_personagem)) # Substitua 'subcategoria' pela subcategoria correta
        quantidade = cursor.fetchall()

        if quantidade:
            # Se a quantidade existir no inventário, envia a pergunta
            verificar_e_cenourar_carta(message)
        else:
            # Se a quantidade não existir no inventário, informa ao usuário
            bot.send_message(message.chat.id, "Você não possui essa carta no inventário.")

    except Exception as e:
        print(f"Erro ao processar o comando de cenourar: {e}")
        chat = message.chat.id
        bot.send_message(chat_id=chat, text="Erro ao processar o comando de cenourar.")

# Adicione esta função para enviar a pergunta de cenourar
def enviar_pergunta_cenoura(message, id_usuario, id_personagem, quantidade):
    try:
        # Envia a pergunta sobre cenourar a carta
        texto_pergunta = f"Você deseja mesmo cenourar a carta {id_personagem}?"
        keyboard = telebot.types.InlineKeyboardMarkup()
        sim_button = telebot.types.InlineKeyboardButton(text="Sim",
                                                         callback_data=f"cenourar_sim_{id_usuario}_{id_personagem}")
        nao_button = telebot.types.InlineKeyboardButton(text="Não",
                                                         callback_data=f"cenourar_nao_{id_usuario}_{id_personagem}")
        keyboard.row(sim_button, nao_button)

        # Envia a mensagem com os botões "Sim" e "Não"
        bot.send_message(message.chat.id, texto_pergunta, reply_markup=keyboard)

    except Exception as e:
        print(f"Erro ao enviar pergunta de cenourar: {e}")


# Dentro da função verificar_e_cenourar_carta
def verificar_e_cenourar_carta(message):
    try:
        conn, cursor = conectar_banco_dados()

        # Obtém informações do usuário e personagem a partir da mensagem
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

            # Verifica se há cenouras suficientes para diminuir
            if res >= 1:

                # Diminuir a quantidade de cenouras no inventário
                nova_quantidade = res - 1
                cursor.execute(
                    "UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s",
                    (nova_quantidade, id_usuario, id_personagem)
                )

                # Enviar a pergunta sobre cenourar a carta
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
        if 'cursor' in locals() and cursor:
            cursor.close()
            conn.close()

def update_cartas_counters(id_personagem):
    try:
        conn, cursor = conectar_banco_dados()

        # Atualizar as colunas cenourados e rodados na tabela cartas
        cursor.execute("UPDATE cartas SET cenourados = cenourados + 1 WHERE id_personagem = %s",
                       (id_personagem,))

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar as colunas cenourados e rodados na tabela cartas: {err}")

    finally:
        fechar_conexao(cursor, conn)

def cenourar_carta(message, cursor, id_usuario, id_personagem, sim=True):
    try:
        conn, cursor = conectar_banco_dados()  # Alterei o nome para evitar conflitos

        # Verifica a quantidade atual da carta no inventário
        cursor.execute(
            "SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
            (id_usuario, id_personagem))
        quantidade_atual = cursor.fetchone()

        if int(quantidade_atual[0]) > 1:

            # Verifica se não é None antes de prosseguir
            quantidade_atual = int(quantidade_atual[0])  # Convertendo para inteiro

            cursor.execute(
                "SELECT cenouras FROM usuarios WHERE id_usuario = %s",
                (id_usuario,))

            cenouras = int(cursor.fetchone()[0])  # Ajustei para pegar o valor correto

            # Verifica se há cenouras suficientes para diminuir
            if quantidade_atual >= 2:
                # Atualiza a quantidade de iscas no banco de dados
                nova_quantidade = quantidade_atual - 1
                novas_cenouras = cenouras + 1
                cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s",
                               (nova_quantidade, id_usuario, id_personagem))
                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s",
                               (novas_cenouras, id_usuario))
                texto = f"Carta {id_personagem} apagada. Nova quantidade: {nova_quantidade}. Cenouras: {novas_cenouras}"
                # Edita a mensagem existente
                update_cartas_counters(id_personagem)
                bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=texto)
                conn.commit()
            else:
                # Se a quantidade for 1, apaga a linha do inventário
                cursor.execute(
                    "DELETE FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                    (id_usuario, id_personagem))
                update_cartas_counters(id_personagem)
                bot.send_message(message.chat.id, "A carta foi cenourada com sucesso! 😢")
        elif int(quantidade_atual[0]) == 1:
            cursor.execute(
                "SELECT cenouras FROM usuarios WHERE id_usuario = %s",
                (id_usuario,))

            update_cartas_counters(id_personagem)
            cenouras = int(cursor.fetchone()[0])  # Ajustei para pegar o valor correto
            novas_cenouras = cenouras + 1
            cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s",
                           (novas_cenouras, id_usuario))
            cursor.execute(
                "DELETE FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                (id_usuario, id_personagem))
            texto = "A carta foi cenourada com sucesso! 😢"
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=texto)
            conn.commit()
            print(cursor)

        else:
            bot.send_message(message.chat.id, "Erro ao processar a cenoura. A carta não foi encontrada no inventário.")

    except Exception as e:
        print(f"Erro ao processar cenoura: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()  # Usei o nome local_cursor para fechar a conexão


def verificar_id_na_tabelabeta(user_id):
    try:
        # Conecte ao banco de dados
        conn, cursor = conectar_banco_dados()  # Alterei o nome para evitar conflitos

        # Execute a consulta SQL
        query = f"SELECT id FROM beta WHERE id = {user_id}"
        cursor.execute(query)

        # Verifique se o ID está na tabela
        resultado = cursor.fetchone()

        # Feche a conexão com o banco de dados
        cursor.close()
        conn.close()

        return resultado is not None

    except Exception as e:
        print(f"Erro ao verificar ID na tabela beta: {e}")
        raise ValueError("Erro ao verificar ID na tabela beta")
    
@bot.message_handler(commands=['pesca'])
@bot.message_handler(commands=['pescar'])
def pescar(message):
    try:
        nome = message.from_user.first_name
        # Verifica se o usuário está banido antes de permitir a pesca
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        print("Usuário não está banido. Pode pescar.")
        qtd_iscas = verificar_giros(message.from_user.id)
        if qtd_iscas == 0:
            mensagem_iscas = "Você está sem iscas."
            bot.send_message(message.chat.id, mensagem_iscas)
        else:
            # Verifica se passaram 30 segundos desde a última interação
            if not verificar_tempo_passado(message.chat.id):
                print("Tempo insuficiente passado desde a última interação. Aguarde a próxima rodada.")
                return
            else:
                # Marca o botão como clicado
                ultima_interacao[message.chat.id] = datetime.now()

            if verificar_id_na_tabelabeta(message.from_user.id):
                diminuir_giros(message.from_user.id, 1)
                keyboard = telebot.types.InlineKeyboardMarkup()

                # Primeira coluna
                primeira_coluna = [
                    telebot.types.InlineKeyboardButton(text="☁  Música", callback_data='pescar_musica'),
                    telebot.types.InlineKeyboardButton(text="🌷 Anime", callback_data='pescar_animanga'),
                    telebot.types.InlineKeyboardButton(text="🧶  Jogos", callback_data='pescar_jogos')
                ]

                # Segunda coluna
                segunda_coluna = [
                    telebot.types.InlineKeyboardButton(text="🍰  Filmes", callback_data='pescar_filmes'),
                    telebot.types.InlineKeyboardButton(text="🍄  Séries", callback_data='pescar_series'),
                    telebot.types.InlineKeyboardButton(text="🍂  Misc", callback_data='pescar_miscelanea')
                ]

                keyboard.add(*primeira_coluna)
                keyboard.add(*segunda_coluna)

                # Botão "Geral"
                keyboard.row(telebot.types.InlineKeyboardButton(text="🫧  Geral", callback_data='pescar_geral'))

                # Imagem

                photo = "https://telegra.ph/file/b3e6d2a41b68c2ceec8e5.jpg"
                bot.send_photo(message.chat.id, photo=photo, caption=f'Olá! {nome}, \nVocê tem disponivel: {qtd_iscas} iscas. \nBoa pesca!\n\nSelecione uma categoria:', reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, "Ei visitante, você não foi convidado! 😡")

    except ValueError as e:
        print(f"Erro: {e}")
        # Se o usuário está banido, envia a mensagem de banimento
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)

# Atualização na função callback_query_handler
# Atualização na função callback_query_handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('pescar_'))
def escolher_categoria_pescar(call):
    try:
        # Permitir o processamento imediato para o primeiro callback após pressionar "Pescar"
        # e bloquear subsequentes se não tiverem passado 30 segundos desde a última interação
        if verificar_tempo_passado(call.message.chat.id):
            categoria_escolhida[call.message.chat.id] = call.data.replace('pescar_', '')

            # Adiciona o evento ao inventário
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text=f"Você escolheu a categoria: {categoria_escolhida[call.message.chat.id]}")
        else:
            print(f"Tempo insuficiente passado desde a última interação. Ignorando callback.")

    except Exception as e:
        print(f"Erro durante o processamento: {e}")
def obter_cartas_subcateg(subcategoria, conn):
    try:
        # Ajuste para remover qualquer prefixo desnecessário (por exemplo, "musica_")
        subcategoria = subcategoria.split('_')[-1].lower()

        cursor = conn.cursor()
        cursor.execute("SELECT id_personagem, emoji, nome, imagem FROM personagens WHERE subcategoria = %s", (subcategoria,))
        cartas = cursor.fetchall()
        return cartas

    except mysql.connector.Error as err:
        print(f"Erro ao obter cartas da subcategoria: {err}")
        return None

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()


# Dentro da função categoria_handler
# Variável global para rastrear botões clicados
botao_clicado = False

# Função para verificar e processar os botões
# Variável global para rastrear botões clicados
botao_clicado = False

# Função para verificar e processar os botões
def categoria_handler(message, categoria):
    try:
        conn, cursor = conectar_banco_dados()

        chat_id = message.chat.id


        # Se a categoria for 'Geral', mostrar as subcategorias e esperar escolha
        if categoria.lower() == 'geral':
            subcategorias = buscar_subcategorias(categoria)
            subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]

            if subcategorias:
                # Envia mensagem de botões
                resposta_botoes = "E o universo sorteou:\n\n"
                subcategorias_aleatorias = random.sample(subcategorias, min(4, len(subcategorias)))

                keyboard = telebot.types.InlineKeyboardMarkup()

                for i in range(0, len(subcategorias_aleatorias)):
                    button = telebot.types.InlineKeyboardButton(text=subcategorias_aleatorias[i],
                                                                callback_data=f"choose_subcategoria_{subcategorias_aleatorias[i]}")
                    keyboard.add(button)

                imagem_url="https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_markup=keyboard,
                    media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                        caption=resposta_botoes)
                )


                # Marca o botão como clicado
                botao_clicado = True


            else:
                bot.send_message(message.chat.id, f"Nenhuma subcategoria encontrada para a categoria 'Geral'.")
        else:
            # Se a categoria não for 'Geral', proceda com a lógica normal da tabela de personagens
            subcategorias = buscar_subcategorias(categoria)
            subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]

            if subcategorias:
                # Envia mensagem de botões
                resposta_botoes = "E o universo sorteou:\n\n"
                subcategorias_aleatorias = random.sample(subcategorias, min(4, len(subcategorias)))

                keyboard = telebot.types.InlineKeyboardMarkup()

                for i in range(0, len(subcategorias_aleatorias)):
                    button = telebot.types.InlineKeyboardButton(text=subcategorias_aleatorias[i],
                                                                callback_data=f"choose_subcategoria_{subcategorias_aleatorias[i]}")
                    keyboard.add(button)


                # Marca o botão como clicado
                botao_clicado = True

                imagem_url="https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    reply_markup=keyboard,
                    media=telebot.types.InputMediaPhoto(media=imagem_url,
                                                        caption=resposta_botoes)
                )

            else:
                bot.send_message(message.chat.id, f"Nenhuma subcategoria encontrada para a categoria '{categoria}'.")

    except mysql.connector.Error as err:
        bot.send_message(message.chat.id, f"Erro ao buscar subcategorias: {err}")

    finally:
        fechar_conexao(cursor, conn)



def subcategoria_handler(message, subcategoria, cursor, conn, id_personagem):
    id_usuario = message.chat.id  # Obtém o ID do usuário da mensagem

    try:
        # Marca o botão como clicado
        botao_clicado = True


        # Criar o cursor dentro do bloco try para garantir que esteja conectado ao banco de dados
        cursor = conn.cursor()

        # Verifica se a subcategoria clicada é 'Geral'
        if subcategoria.lower() == 'geral':
            # Adicione este print para verificar se está entrando nesta condição
            print("Verificando chance de evento fixo.")
            # Chance de 20% de obter um evento fixo
            if random.randint(1, 100) <= 20:
                evento_aleatorio = obter_carta_evento_fixo(conn, subcategoria)
                if evento_aleatorio:
                    # Adicione este print para verificar se está entrando nesta condição
                    print("Evento fixo encontrado. Enviando carta aleatória.")
                    # Diretamente chama a função send_card_message
                    send_card_message(message, evento_aleatorio, cursor=cursor, conn=conn)
                    return
            # Adicione este print para verificar se está entrando nesta condição
            print("Nenhum evento fixo. Procedendo com a lógica normal.")
        else:
            # Procede com a lógica normal de obter uma carta da subcategoria na tabela de personagens
            cartas_disponiveis = obter_cartas_subcateg(subcategoria, conn)

            if cartas_disponiveis:
                carta_aleatoria = random.choice(cartas_disponiveis)
                id_personagem, emoji, nome, imagem = carta_aleatoria

                # Adicione este print para verificar se está entrando nesta condição
                print("Enviando carta normal.")
                # Chama a função send_card_message diretamente
                send_card_message(message, emoji, id_personagem, nome, subcategoria, imagem)
                qnt_carta(id_usuario)
            else:
                # Adicione este print para verificar se está entrando nesta condição
                print("Nenhuma carta disponível.")

    except Exception as e:
        print(f"Erro durante o processamento: {e}")

    finally:
        # Adicione este print para verificar se está entrando nesta condição
        print("Fechando conexão.")
        # Fecha a conexão apenas no final do bloco finally
        cursor.close()


def verificar_subcategoria_evento(subcategoria, cursor):
    try:
        # Obtém um evento fixo aleatório da subcategoria
        cursor.execute(
            "SELECT id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'fixo' ORDER BY RAND() LIMIT 1",
            (subcategoria,))
        evento_aleatorio = cursor.fetchone()
        if evento_aleatorio:
            print(f"Evento fixo aleatório: {evento_aleatorio}")
            # Chance de 20% de obter um evento fixo
            chance = random.randint(1, 100)

            if chance <= 50:
                # Certifique-se de que o evento retornado está no formato desejado para uso posterior
                id_personagem, nome, subcategoria, imagem = evento_aleatorio
                evento_formatado = {
                    'id_personagem': id_personagem,
                    'nome': nome,
                    'subcategoria': subcategoria,
                    'imagem': imagem  # Adicionado o campo 'imagem'
                    # Adicione outros campos conforme necessário
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

def obter_carta_evento_fixo(conn, subcategoria=None):
    try:
        cursor = conn.cursor(dictionary=True)

        if subcategoria:
            # Obtém um evento fixo aleatório da subcategoria específica
            cursor.execute("SELECT emoji, id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'fixo' ORDER BY RAND() LIMIT 1", (subcategoria,))
        else:
            # Obtém um evento fixo aleatório geral
            cursor.execute("SELECT emoji, id_personagem, nome, subcategoria, imagem FROM evento WHERE evento = 'fixo' ORDER BY RAND() LIMIT 1")

        evento_aleatorio = cursor.fetchone()

        print(f"Evento fixo aleatório: {evento_aleatorio}")

        return evento_aleatorio

    except mysql.connector.Error as err:
        print(f"Erro ao obter carta de evento fixo: {err}")
        return None

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

def choose_subcategoria_handler(call, subcategoria, cursor, conn, message):
    try:
        chat_id = message.chat.id
        # Verifica se passaram 30 segundos desde a última interação
        if not verificar_tempo_passado(chat_id):
            print(f"Tempo insuficiente passado desde a última interação para o chat ID {chat_id}. Ignorando callback.")
            return
        else:
            # Marca o botão como clicado
            ultima_interacao[chat_id] = datetime.datetime.now()
        # Verifica se a subcategoria clicada é 'Geral'
        if subcategoria.lower() == 'geral':
            evento_aleatorio = obter_carta_evento_fixo(conn, subcategoria)
            if evento_aleatorio:
                print("Evento fixo encontrado. Enviando carta aleatória.")
                send_card_message(call.message, evento_aleatorio, cursor=cursor, conn=conn)
            else:
                print("Nenhum evento disponível.")
        else:
            # Separa a subcategoria
            _, subcategoria_nome = subcategoria.split('_')
            print(f"Procedendo com a lógica normal. Subcategoria: {subcategoria_nome}")
            subcategoria_handler(call.message, subcategoria_nome, cursor, conn, None)

    except Exception as e:
        print(f"Erro durante o processamento: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('choose_subcategoria_'))
def choose_subcategoria_callback(call, subcategoria, cursor, conn):
    try:
        # Verifica se há eventos fixos para a subcategoria escolhida
        categoria_info = ultimo_clique.get(call.message.chat.id, {})
        categoria = categoria_info.get('categoria', '')

        if categoria.lower() == 'geral':
            evento_aleatorio = verificar_subcategoria_evento(subcategoria, cursor)
            if evento_aleatorio:
                print("Evento fixo encontrado. Enviando carta aleatória.")
                # Se há eventos fixos, envia uma carta aleatória
                send_card_message(call.message, evento_aleatorio)
            else:
                print("Nenhum evento fixo encontrado. Procedendo com lógica normal.")
                # Se não há eventos fixos, procede com a lógica normal
                subcategoria_handler(call.message, subcategoria, cursor, conn, None)
        else:
            print("Procedendo com a lógica normal.")
            subcategoria_handler(call.message, subcategoria, cursor, conn, None)

    except Exception as e:
        print(f"Erro durante o processamento: {e}")


def send_card_message(message, *args, cursor=None, conn=None):
    try:
        if len(args) == 1 and isinstance(args[0], dict):
            evento_aleatorio = args[0]

            # Remova o prefixo "musica_" da subcategoria para exibição
            subcategoria_display = evento_aleatorio['subcategoria'].split('_')[-1]

            if evento_aleatorio['imagem'] is None:
                imagem= "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n🪴 {evento_aleatorio['id_personagem']} - {evento_aleatorio['nome']}\nde {subcategoria_display}"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    media=telebot.types.InputMediaPhoto(media=imagem,
                                                        caption=text))
            else:
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n🪴 {evento_aleatorio['id_personagem']} - {evento_aleatorio['nome']}\nde {subcategoria_display}"
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
            # Adiciona o evento ao inventário
            id_usuario = message.chat.id
            id_personagem = evento_aleatorio['id_personagem']
            nome = evento_aleatorio['nome']
            subcategoria = evento_aleatorio['subcategoria']
            add_to_inventory(id_usuario, id_personagem)

        elif len(args) == 5:
            emoji_categoria, id_personagem, nome, subcategoria, imagem = args
            print(args)
            # Remova o prefixo "musica_" da subcategoria para exibição
            subcategoria_display = subcategoria.split('_')[-1]
            id_usuario = message.chat.id
            add_to_inventory(id_usuario, id_personagem)
            if imagem is None:
                print(imagem)
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
            # Adiciona a carta normal ao inventário


        else:
            print("Número incorreto de argumentos.")
    except Exception as e:
        print(f"Erro ao enviar a mensagem da carta: {e}")


def add_to_inventory(id_usuario, id_personagem):
    try:
        # Print relevant information for debugging
        print(f"ID do usuário: {id_usuario}")
        print(f"ID da carta: {id_personagem}")

        conn, cursor = conectar_banco_dados()
        # Verificar se a carta já existe no inventário do usuário
        cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                       (id_usuario, id_personagem))
        existing_carta = cursor.fetchone()

        if existing_carta:
            # Se a carta já existe, atualizar a quantidade
            nova_quantidade = existing_carta[0] + 1
            cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s",
                           (nova_quantidade, id_usuario, id_personagem))

        else:
            # Se a carta não existe, inserir uma nova entrada no inventário
            cursor.execute("INSERT INTO inventario (id_personagem, id_usuario, quantidade) VALUES (%s, %s, 1)",
                           (id_personagem, id_usuario))

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao adicionar carta ao inventário: {err}")

    finally:
        fechar_conexao(cursor, conn)


def atualizar_coluna_usuario(id_usuario, coluna, novo_valor):
    try:
        conn, cursor = conectar_banco_dados()

        # Consulta SQL para atualizar a coluna na tabela 'usuarios'
        query = f"UPDATE usuarios SET {coluna} = %s WHERE id_usuario = %s"
        cursor.execute(query, (novo_valor, id_usuario))
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Erro ao atualizar {coluna}: {err}")

    finally:
        fechar_conexao(cursor, conn)

# Comando /setbio
@bot.message_handler(commands=['setbio'])
def set_bio_command(message):
    # Obtém o ID do usuário da mensagem
    id_usuario = message.from_user.id

    # Extrair a nova bio do comando
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        nova_bio = command_parts[1].strip()

        # Atualiza a bio na tabela 'usuarios'
        atualizar_coluna_usuario(id_usuario, 'bio', nova_bio)

        # Envia uma confirmação ao usuário
        bot.send_message(message.chat.id, f"Bio atualizada para: {nova_bio}")
    else:
        bot.send_message(message.chat.id, "Formato incorreto. Use /setbio seguido da nova bio desejada, por exemplo: /setbio Nova bio incrível.")




def verifica_tempo_ultimo_gif(id_usuario):
    try:
        # Consulta SQL para obter o último registro de gif para o usuário
        query_ultimo_gif = f"""
            SELECT MAX(data) AS ultima_data, MAX(horario) AS ultima_hora 
            FROM logs 
            WHERE id_usuario = {id_usuario} AND ação = 'gif'
        """
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_ultimo_gif)
        ultimo_gif = cursor.fetchone()

        if ultimo_gif and ultimo_gif[0]:  # Verifica se a data não é nula ou vazia
            # Combine a data e a hora
            ultima_data_hora_str = f"{ultimo_gif[0]} {ultimo_gif[1]}"
            
            # Converte a string combinada para um objeto datetime
            ultimo_gif_datetime = datetime.strptime(ultima_data_hora_str, "%Y-%m-%d %H:%M:%S")
            
            # Se a data for de hoje, ajuste a data para a data atual
            if ultimo_gif_datetime.date() == datetime.now().date():
                ultimo_gif_datetime = ultimo_gif_datetime.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
            
            # Calcula a diferença entre agora e o último gif
            diferenca_tempo = datetime.now() - ultimo_gif_datetime
            
            # Se a diferença for menor que 60 minutos, retorna o tempo restante
            if diferenca_tempo.total_seconds() < 3600:
                tempo_restante = timedelta(seconds=(3600 - diferenca_tempo.total_seconds()))
                return tempo_restante
            else:
                return None
        else:
            # Se não houver registros anteriores ou a data for nula/vazia, retorna None
            return None

    except Exception as e:
        print(f"Erro ao verificar tempo do último gif: {e}")
    finally:
        fechar_conexao(cursor, conn)



@bot.message_handler(commands=['setgif'])
def enviargif(message):
    # Obtém a lista de palavras após a divisão e pega o primeiro elemento
    id_personagem = message.text.split('/setgif ', 1)[1].strip().lower()
    id_usuario = message.from_user.id

    # Verifica a quantidade de cartas no inventário
    quantidade_cartas = verifica_inventario(id_usuario, id_personagem)
    
    if quantidade_cartas > 0:
        # Verifica o tempo desde o último gif registrado
        tempo_restante = verifica_tempo_ultimo_gif(id_usuario)
        
        if tempo_restante:
            # Se houver tempo restante, informa ao usuário
            bot.send_message(message.chat.id, f"Você já enviou um gif recentemente. Aguarde {tempo_restante} antes de enviar outro.")
        else:
            # Se não houver tempo restante, continua com o processo
            bot.send_message(message.chat.id, "Eba! Você pode escolher um gif!\nEnvie o link do gif gerado pelo @UploadTelegraphBot:")
            # Armazena o ID do personagem como chave
            links_gif[id_usuario] = id_personagem
            # Configura a função para lidar com o próximo passo
            bot.register_next_step_handler(message, receber_link_gif, id_personagem)
    else:
        bot.send_message(message.chat.id, text="Você não pode escolher gif para essa carta, pois não possui cartas suficientes!")

# Dentro da função receber_link_gif
# Crie um dicionário temporário para armazenar os dados do callback
callbacks_temp = {}
estados = {}

# Variável para armazenar o link do GIF
links_gif = {}
motivos_reprovacao = {}


# Dentro da função receber_link_gif
# Dentro da função receber_link_gif
def receber_link_gif(message, id_personagem):
    id_usuario = message.from_user.id
    if id_usuario:
        link_gif = message.text
        id_personagem = links_gif.get(id_usuario)

        if id_personagem:
            # Extrai apenas o número do id_personagem
            numero_personagem = id_personagem.split('_')[0]

            # Consultar o banco de dados para obter informações do usuário
            sql_usuario = "SELECT nome_usuario, nome FROM usuarios WHERE id_usuario = %s"
            values_usuario = (id_usuario,)
            cursor.execute(sql_usuario, values_usuario)
            resultado_usuario = cursor.fetchone()
            # Obter o username do usuário que acionou o comando
            username_usuario = message.from_user.username

            # Consultar o banco de dados para obter informações do personagem
            sql_personagem = "SELECT nome, subcategoria FROM personagens WHERE id_personagem = %s"
            values_personagem = (numero_personagem,)
            cursor.execute(sql_personagem, values_personagem)
            resultado_personagem = cursor.fetchone()

            if resultado_usuario and resultado_personagem:
                nome_usuario = resultado_usuario[0]
                nome_personagem = resultado_personagem[0]
                subcategoria_personagem = resultado_personagem[1]

                # Consultar o banco de dados para obter a data e a hora atuais
                data_atual = datetime.now().strftime("%Y-%m-%d")
                hora_atual = datetime.now().strftime("%H:%M:%S")

                # Inserir os dados temporários no banco de dados
                sql_temp_insert = "INSERT INTO temp_data (id_usuario, chave, valor, id_personagem) VALUES (%s, %s, %s, %s)"
                values_temp_insert = (id_usuario, f"{id_usuario}_{numero_personagem}", link_gif, numero_personagem)
                cursor.execute(sql_temp_insert, values_temp_insert)
                conn.commit()

                # Cria botões para chamar o callback
                keyboard = telebot.types.InlineKeyboardMarkup()

                # Botão "Aprovar"
                btn_aprovar = telebot.types.InlineKeyboardButton(text="✔️ Aprovar", callback_data=f"aprovar_{id_usuario}_{numero_personagem}")

                # Botão "Reprovar"
                btn_reprovar = telebot.types.InlineKeyboardButton(text="❌ Reprovar", callback_data=f"reprovar_{id_usuario}_{numero_personagem}")

                # Adiciona os botões à linha do teclado
                keyboard.row(btn_aprovar, btn_reprovar)

                # Encaminha a mensagem para o grupo com ID -1002082934455 com os botões
                bot.forward_message(chat_id=-1002082934455, from_chat_id=message.chat.id, message_id=message.message_id)

                # Construir a mensagem com as informações do pedido de aprovação
                mensagem = f"Pedido de aprovação de GIF:\n\n"
                mensagem += f"ID Personagem: {numero_personagem}\n"
                mensagem += f"{nome_personagem} de {subcategoria_personagem}\n\n"
                mensagem += f"Usuário: @{username_usuario}\n"
                mensagem += f"Nome: {nome_usuario}\n"

                # Envia a mensagem com os botões para o grupo
                bot.send_message(-1002082934455, mensagem, reply_markup=keyboard)

                # Limpa a entrada do usuário
                bot.send_message(message.chat.id, "Link do GIF registrado com sucesso. Aguardando aprovação.")
            else:
                bot.send_message(message.chat.id, "Erro ao obter informações do usuário ou do personagem.")
        else:
            bot.send_message(message.chat.id, "Erro ao processar o link do GIF. Por favor, use o comando /setgif novamente.")
    else:
        bot.send_message(message.chat.id, "Erro ao processar o link do GIF. ID de usuário inválido.")



@bot.message_handler(func=lambda message: estados.get(message.from_user.id) == "aguardando_motivo_reprovacao")
def receber_motivo_reprovacao(message):
    id_usuario = message.from_user.id
    motivo = message.text

    # Obtemos o ID do personagem associado a esse motivo
    id_personagem = motivos_reprovacao.get(id_usuario)

    if id_personagem:
        # Limpa o estado e os dados temporários
        estados.pop(id_usuario)
        motivos_reprovacao.pop(id_usuario)

        # Envia a mensagem ao usuário informando o motivo da reprovação
        bot.send_message(id_usuario, f"Seu GIF para o personagem {id_personagem} foi reprovado pelos seguintes motivos:\n{motivo}")
    else:
        # Caso não seja possível identificar o ID do personagem, envie uma mensagem padrão
        bot.send_message(id_usuario, "Ocorreu um erro ao processar sua solicitação. Tente novamente.")

def verifica_inventario(id_usuario, id_personagem):
    query = f"SELECT quantidade FROM inventario WHERE id_usuario = {id_usuario} AND id_personagem = {id_personagem}"
    cursor.execute(query)
    quantidade_total = cursor.fetchone()[0]
    print(quantidade_total)
    return quantidade_total > 29

def obter_nome_usuario_por_id(id_usuario):
    try:
        # Consulta SQL para obter o nome do usuário pelo id_usuario
        query = "SELECT nome_usuario FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]  # Retorna o nome do usuário
        else:
            return "Nome de Usuário Desconhecido"  # Ou qualquer valor padrão que você desejar

    except Exception as e:
        print(f"Erro ao obter nome do usuário: {e}")
        return "Nome de Usuário Desconhecido"  # Em caso de erro, retorna um valor padrão



# Comando /setmusica
@bot.message_handler(commands=['setmusica'])
def set_musica_command(message):
    # Extrair a nova música do comando
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        nova_musica = command_parts[1].strip()

        # Obtém o ID do usuário da mensagem
        id_usuario = message.from_user.id

        # Atualiza a música na tabela 'usuarios'
        atualizar_coluna_usuario(id_usuario, 'musica', nova_musica)

        # Envia uma confirmação ao usuário
        bot.send_message(message.chat.id, f"Música atualizada para: {nova_musica}")
    else:
        bot.send_message(message.chat.id, "Formato incorreto. Use /setmusica seguido da nova música, por exemplo: /setmusica nova_musica.")



def obter_informacoes_carta(card_id):
    # Consulta SQL para obter informações da carta
    conn, cursor = conectar_banco_dados()

    # Tente buscar na tabela personagens
    cursor.execute("SELECT id_personagem, emoji, nome, subcategoria FROM personagens WHERE id_personagem = %s", (card_id,))
    result_personagens = cursor.fetchone()

    if result_personagens:
        return result_personagens

    # Se não encontrou na tabela personagens, tente buscar na tabela evento
    cursor.execute("SELECT id_personagem, emoji, nome, subcategoria FROM evento WHERE id_personagem = %s", (card_id,))
    result_evento = cursor.fetchone()

    return result_evento

@bot.message_handler(commands=['picnic'])
@bot.message_handler(commands=['trocar'])
@bot.message_handler(commands=['troca'])
def trade(message):
    try:
        # Obtém o ID do usuário que acionou o comando
        call = message
        chat_id = message.chat.id
        eu = call.from_user.id
        voce = message.reply_to_message.from_user.id
        seunome = message.reply_to_message.from_user.first_name
        meunome = message.from_user.first_name
        message = message
        bot_id = 6405224208
        categoria = call.text.replace('/troca', '')
        # Obtém os dados da mensagem (cartas escolhidas)
        minhacarta = call.text.split()[1]
        suacarta = call.text.split()[2]


        # Verifica se a troca não é com o ID do bot antes de prosseguir
        if voce == bot_id:
            bot.send_message(chat_id, "Você não pode fazer trocas com a Mabi :(")
            return

        # Obtém informações das cartas
        info_minhacarta = obter_informacoes_carta(minhacarta)
        info_suacarta = obter_informacoes_carta(suacarta)

        # Extraindo informações formatadas
        emojiminhacarta, idminhacarta, nomeminhacarta, subcategoriaminhacarta = info_minhacarta
        emojisuacarta, idsuacarta, nomesuacarta, subcategoriasuacarta = info_suacarta
        # Construindo a mensagem formatada
        texto = (
            f"🥪 | Hora do picnic!\n\n"
            f"{meunome} oferece de lanche:\n"
            f" {idminhacarta} {emojiminhacarta}  —  {nomeminhacarta} de {subcategoriaminhacarta}\n\n"
            f"E {seunome} oferece de lanche:\n"
            f" {idsuacarta} {emojisuacarta}  —  {nomesuacarta} de {subcategoriasuacarta}\n\n"
            f"Podemos começar a comer, {seunome}?"
        )

        keyboard = telebot.types.InlineKeyboardMarkup()

        # Adiciona os botões apenas se a troca não for com o bot
        if voce != bot_id:
            primeiro = [
                telebot.types.InlineKeyboardButton(text="✅",
                                                   callback_data=f'troca_sim_{eu}_{voce}_{minhacarta}_{suacarta}_{chat_id}'),
                telebot.types.InlineKeyboardButton(text="❌", callback_data=f'troca_nao_{eu}_{voce}_{minhacarta}_{suacarta}_{chat_id}'),
            ]
            keyboard.add(*primeiro)

        # Enviando a mensagem
        image_url = "https://telegra.ph/file/8672c8f91c8e77bcdad45.jpg"
        bot.send_photo(message.chat.id, image_url, caption=texto, reply_markup=keyboard)

    except Exception as e:
        print(f"Erro durante a troca: {e}")

    finally:
        print("teste")



def realizar_troca(message,eu, voce, minhacarta, suacarta,chatid):
    try:

            conn, cursor = conectar_banco_dados()
            # Verificar se o usuário de origem tem a carta
            cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                           (eu, minhacarta))

            qntminha = cursor.fetchone()
            print(qntminha)
            print(cursor.fetchone())
            # Verificar se o usuário de destino tem a carta
            cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                           (voce, suacarta))
            qntsua = cursor.fetchone()
            qntminha = functools.reduce(lambda sub, ele: sub * 10 + ele, qntminha)
            qntsua = functools.reduce(lambda sub, ele: sub * 10 + ele, qntsua)

            if qntminha > 0 and qntsua > 0:  # se nós dois temos
                # Remover a carta do meu inventario

                cursor.execute(
                    "UPDATE inventario SET quantidade = %s - 1 WHERE id_usuario = %s AND id_personagem = %s",
                    (qntminha, eu, minhacarta))
                (print("tirar carta minha"))

                # Remover a carta do seu  inventario
                cursor.execute(
                    "UPDATE inventario SET quantidade = %s - 1 WHERE id_usuario = %s AND id_personagem = %s",
                    (qntsua, voce, suacarta))
                (print("tirar carta sua"))

                # Verificar se a minha carta já existe no inventario dele
                cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (voce, minhacarta))
                qnt = cursor.fetchone()

                if qnt:
                    # Incrementar a quantidade se a carta sua já existir no inventário do usuário de destino
                    cursor.execute(
                        "UPDATE inventario SET quantidade = quantidade + 1 WHERE id_usuario = %s AND id_personagem = %s",
                        (voce, minhacarta))
                else:
                    # Inserir uma nova linha no inventário do vc se a carta sua não existir
                    cursor.execute("INSERT INTO inventario (id_usuario, id_personagem, quantidade) VALUES (%s, %s, 1)",
                                   (voce, minhacarta,))

                # Verificar se a sua carta já existe no meu inventario
                cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (eu, suacarta))
                existe = cursor.fetchone()

                if existe:
                    existe = functools.reduce(lambda sub, ele: sub * 10 + ele, existe)
                    # Incrementar a quantidade se a carta de destino já existir no inventário do usuário de destino
                    cursor.execute(
                        "UPDATE inventario SET quantidade = %s + 1 WHERE id_usuario = %s AND id_personagem = %s",
                        (existe, eu, suacarta))
                else:
                    # Inserir uma nova linha no inventário do usuário de destino se a carta de destino não existir
                    cursor.execute("INSERT INTO inventario (id_usuario, id_personagem, quantidade) VALUES (%s, %s, 1)",
                                   (eu, suacarta,))

                # Confirmar as alterações no banco de dados
                conn.commit()
                image_url = "https://telegra.ph/file/8672c8f91c8e77bcdad45.jpg"
                bot.edit_message_media(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    media=telebot.types.InputMediaPhoto(media=image_url,
                                                        caption="Troca realizada com sucesso. Até a proxima!")
                )

    except mysql.connector.Error as err:
        bot.edit_message_caption(chat_id=message.chat.id,caption="Houve um problema com a troca, tente novamente!")

def obter_ids_loja_do_dia(data_atual):
    try:

        conn, cursor = conectar_banco_dados()

        # Consultar a tabela loja para obter os IDs correspondentes ao dia de hoje
        cursor.execute("SELECT id_personagem FROM loja WHERE data = %s", (data_atual,))
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

        # Obter cartas aleatórias de categorias distintas
        categorias = ['Música', 'Séries', 'Filmes', 'Miscelanêa', 'Jogos', 'Animangá']
        cartas_aleatorias = []

        for categoria in categorias:
            while True:
                # Obter uma carta aleatória da categoria
                cursor.execute(
                    "SELECT id_personagem, nome, subcategoria, imagem, emoji FROM personagens WHERE categoria = %s AND imagem IS NOT NULL ORDER BY RAND() LIMIT 1",
                    (categoria,))
                carta_aleatoria = cursor.fetchone()

                if carta_aleatoria and carta_aleatoria[0]:  # Verificar se a carta e o id existem
                    id_personagem = carta_aleatoria[0]

                    # Verificar se o id já está na tabela 'loja'
                    if not id_ja_registrado_na_loja(cursor, id_personagem):
                        # Se o id não estiver na tabela 'loja', adicionar a carta à lista
                        cartas_dict = {
                            "id": id_personagem,
                            "nome": carta_aleatoria[1],
                            "subcategoria": carta_aleatoria[2],
                            "imagem": carta_aleatoria[3],
                            "emoji": carta_aleatoria[4],
                            "categoria": categoria  # Adiciona a categoria à carta
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
            categoria = carta['categoria']  # Obtem a categoria da carta

            # Verificar se a carta já está registrada na tabela 'loja' para a data atual
            cursor.execute(
                "SELECT COUNT(*) FROM loja WHERE id_personagem = %s AND data = %s",
                (id_personagem, data_atual)
            )
            count = cursor.fetchone()[0]

            if count == 0:
                # Se a carta não estiver registrada, registrar na tabela 'loja'
                cursor.execute(
                    "INSERT INTO loja (id_personagem, data, categoria) VALUES (%s, %s, %s)",
                    (id_personagem, data_atual, categoria)  # Inclui a categoria na inserção
                )

        # Commit das alterações no banco de dados
        conn.commit()

    except Exception as e:
        print(f"Erro ao registrar cartas na loja: {e}")

    finally:
        fechar_conexao(cursor, conn)


def id_ja_registrado_na_loja(cursor, id_personagem):
    # Verifica se o id_personagem já está na tabela 'loja'
    cursor.execute("SELECT COUNT(*) FROM loja WHERE id_personagem = %s", (id_personagem,))
    count = cursor.fetchone()[0]
    return count > 0

@bot.message_handler(commands=['criar_colagem'])
def criar_colagem(message):
    try:
        # Obter as 6 cartas aleatórias
        cartas_aleatorias = obter_cartas_aleatorias()
        data_atual_str = dt_module.date.today().strftime("%Y-%m-%d")  # Usar dt_module para se referir ao módulo renomeado
        print(data_atual_str)
        if not cartas_aleatorias:
            bot.send_message(message.chat.id, "Não foi possível obter cartas aleatórias.")
            return
        
        # Verificar e registrar as cartas na tabela 'loja'
        registrar_cartas_loja(cartas_aleatorias, data_atual_str)
        # Criar a colagem
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
                        # Se houver um problema ao baixar a imagem, criar uma imagem preta
                        img = Image.new('RGB', (300, 400), color='black')
                else:
                    # Se a URL da imagem estiver vazia ou nula, criar uma imagem preta
                    img = Image.new('RGB', (300, 400), color='black')
            except Exception as e:
                print(f"Erro ao abrir a imagem da carta {carta['id']}: {e}")
                # Em caso de erro, criar uma imagem preta
                img = Image.new('RGB', (300, 400), color='black')
            imagens.append(img)

        # Calcular a altura total necessária para as imagens
        altura_total = (len(imagens) // 3) * 400

        # Criar a colagem com altura total
        colagem = Image.new('RGB', (900, altura_total))  # Largura proporcional a 3x4 (300x400)
        coluna_atual = 0
        linha_atual = 0

        for img in imagens:
            colagem.paste(img, (coluna_atual, linha_atual))
            coluna_atual += 300

            if coluna_atual >= 900:
                coluna_atual = 0
                linha_atual += 400

        # Salvar a colagem
        colagem.save('colagem_cartas.png')

        # Enviar a colagem
        with open('colagem_cartas.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        # Enviar a mensagem com os personagens na loja
        enviar_mensagem_loja(message, cartas_aleatorias)

    except Exception as e:
        print(f"Erro ao criar colagem: {e}")
        bot.send_message(message.chat.id, "Erro ao criar colagem.")

def enviar_mensagem_loja(message, cartas_aleatorias):
    try:
        # Mensagem com os personagens na loja
        mensagem_loja = "🐟 Peixes na vendinha hoje:\n\n"

        for carta in cartas_aleatorias:
            mensagem_loja += f"{carta['emoji']}| {carta['id']} • {carta['nome']} - {carta['subcategoria']}\n"

        mensagem_loja += "\n🥕 Acesse usando o comando /vendinha"
        bot.send_message(message.chat.id, mensagem_loja)

    except Exception as e:
        print(f"Erro ao enviar mensagem da loja: {e}")
        bot.send_message(message.chat.id, f"Erro ao enviar mensagem da loja: {e}")


def manter_proporcoes(imagem, largura_maxima, altura_maxima):
    largura_original, altura_original = imagem.size
    proporcao_original = largura_original / altura_original

    if proporcao_original > 1:
        # A imagem é mais larga do que alta
        nova_largura = largura_maxima
        nova_altura = int(largura_maxima / proporcao_original)
    else:
        # A imagem é mais alta do que larga
        nova_altura = altura_maxima
        nova_largura = int(altura_maxima * proporcao_original)

    return imagem.resize((nova_largura, nova_altura))


@bot.message_handler(commands=['vendinha'])
def loja(message):
    try:
        # Verifica se o usuário está banido antes de permitir a compra
        verificar_id_na_tabela(message.from_user.id, "ban", "iduser")
        print("Usuário não está banido. Pode pescar.")

        keyboard = telebot.types.InlineKeyboardMarkup()
        conn, cursor = conectar_banco_dados()
        # Botão "Geral"
        keyboard.row(telebot.types.InlineKeyboardButton(text="Peixes do dia", callback_data='loja_loja'))
        keyboard.row(telebot.types.InlineKeyboardButton(text="Estou com sorte", callback_data='loja_geral'))
        keyboard.row(telebot.types.InlineKeyboardButton(text="Comprar iscas", callback_data='loja_compras'))

        # Imagem
        image_url = "https://telegra.ph/file/ea116d98a5bd8d6179612.jpg"
        bot.send_photo(message.chat.id, image_url,
                       caption='Olá! Seja muito bem-vindo à vendinha da Mabi. Como posso te ajudar?',
                       reply_markup=keyboard)

    except ValueError as e:
        print(f"Erro: {e}")
# Se o usuário está banido, envia a mensagem de banimento
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)


# Comando /emoji

while True:
    try:
        if __name__ == "__main__":
            bot.polling(none_stop=True)
        else:
            bot.polling()

    except Exception as e:
        print(f"Erro: {e}")
        time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente