from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *

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
    