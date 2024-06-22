import telebot
import mysql.connector
from mysql.connector import pooling
import concurrent.futures
from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *

# Configuração do pool de conexões grande para cenourar cartas
dbconfig_cenoura = {
        'host': '127.0.0.1',
        'database': 'garden',
        'user': 'root',
        'password': '#Folkevermore13',
        'ssl_disabled': True
}

pool_cenoura = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool_cenoura",
                                                           pool_size=32,  # Tamanho maior para lidar com mais conexões simultâneas
                                                           pool_reset_session=True,
                                                           **dbconfig_cenoura)

def conectar_banco_dados_cenoura():
    return pool_cenoura.get_connection()

def enviar_pergunta_cenoura(message, id_usuario, id_personagem, quantidade):
    try:
        texto_pergunta = f"Você deseja mesmo cenourar a carta {id_personagem}?"
        keyboard = telebot.types.InlineKeyboardMarkup()
        sim_button = telebot.types.InlineKeyboardButton(text="Sim", callback_data=f"cenourar_sim_{id_usuario}_{id_personagem}")
        nao_button = telebot.types.InlineKeyboardButton(text="Não", callback_data=f"cenourar_nao_{id_usuario}_{id_personagem}")
        keyboard.row(sim_button, nao_button)
        bot.send_message(message.chat.id, texto_pergunta, reply_markup=keyboard)
    except Exception as e:
        print(f"Erro ao enviar pergunta de cenourar: {e}")

@bot.message_handler(commands=['cenourar'])
def verificar_e_cenourar_carta(message):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(processar_verificar_e_cenourar, message)
        future.result()

def processar_verificar_e_cenourar(message):
    try:
        conn = conectar_banco_dados_cenoura()
        cursor = conn.cursor()
        id_usuario = message.from_user.id
        id_personagem = message.text.replace('/cenourar', '').strip()

        cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s", (id_usuario, id_personagem))
        quantidade_atual = cursor.fetchone()

        if quantidade_atual and quantidade_atual[0] >= 1:
            enviar_pergunta_cenoura(message, id_usuario, id_personagem, quantidade_atual[0])
        else:
            bot.send_message(message.chat.id, "Você não possui essa carta no inventário ou não tem quantidade suficiente.")
    except Exception as e:
        print(f"Erro ao processar o comando de cenourar: {e}")
        bot.send_message(message.chat.id, "Erro ao processar o comando de cenourar.")
    finally:
        cursor.close()
        conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith('cenourar_sim'))
def cenourar_carta(call, id_usuario, id_personagens):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(processar_cenourar_carta, call)
        future.result()

def processar_cenourar_carta(call):
    try:
        data = call.data.split('_')
        id_usuario = int(data[2])
        id_personagens = data[3]

        conn = conectar_banco_dados_cenoura()
        cursor = conn.cursor()
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        cartas_cenouradas = []

        for id_personagem in id_personagens.split(","):
            id_personagem = id_personagem.strip()
            cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s", (id_usuario, id_personagem))
            quantidade_atual = cursor.fetchone()

            if quantidade_atual and quantidade_atual[0] > 0:
                quantidade_atual = int(quantidade_atual[0])
                cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
                cenouras = int(cursor.fetchone()[0])
                
                nova_quantidade = quantidade_atual - 1
                novas_cenouras = cenouras + 1
                cursor.execute("UPDATE inventario SET quantidade = %s WHERE id_usuario = %s AND id_personagem = %s", (nova_quantidade, id_usuario, id_personagem))
                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s", (novas_cenouras, id_usuario))

                conn.commit()
                cartas_cenouradas.append(id_personagem)
                mensagem_progresso = f"🔄 Cenourando carta:\n{id_personagem}\n\n✅ Cartas cenouradas:\n" + "\n 🥕".join(cartas_cenouradas)
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem_progresso)

            else:
                mensagem_erro = f"Erro ao processar a cenoura. A carta {id_personagem} não foi encontrada no inventário ou a quantidade é insuficiente."
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem_erro)
                return

        mensagem_final = "🥕 Cartas cenouradas com sucesso:\n\n" + "\n".join(cartas_cenouradas)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem_final)
    except Exception as e:
        print(f"Erro ao processar cenoura: {e}")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Erro ao processar a cenoura.")
    finally:
        cursor.close()
        conn.close()

def verificar_id_na_tabelabeta(user_id):
    try:
        conn = conectar_banco_dados_cenoura()
        cursor = conn.cursor()
        query = f"SELECT id FROM beta WHERE id = {user_id}"
        cursor.execute(query)
        resultado = cursor.fetchone()
        return resultado is not None
    except Exception as e:
        print(f"Erro ao verificar ID na tabela beta: {e}")
        raise ValueError("Erro ao verificar ID na tabela beta")
    finally:
        cursor.close()
        conn.close()