from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *
from inventario import *
from gif import *

def categoria_handler(message, categoria):
    try:
        conn, cursor = conectar_banco_dados()

        chat_id = message.chat.id

        # Se a categoria for 'Geral', mostrar as subcategorias e esperar escolha
        if categoria.lower() == 'geral':
            subcategorias = buscar_subcategorias(categoria)
            subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]

            if subcategorias:
                resposta_texto = "𝑆𝑢𝑎 𝑖𝑠𝑐𝑎 𝑎𝑡𝑟𝑎𝑖𝑢 5 𝑝𝑒𝑖𝑥𝑒𝑠, 𝑞𝑢𝑎𝑙 𝑑𝑒𝑙𝑒𝑠 𝑣𝑜𝑐𝑒̂ 𝑣𝑎𝑖 𝑙𝑒𝑣𝑎𝑟?\n\n"
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
                    media=telebot.types.InputMediaPhoto(media=imagem_url, caption=resposta_texto))

            else:
                bot.send_message(message.chat.id, f"Nenhuma subcategoria encontrada para a categoria 'Geral'.")
        else:
            subcategorias = buscar_subcategorias(categoria)
            subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]
            #isca texto
            if subcategorias:
                resposta_texto = "𝑆𝑢𝑎 𝑖𝑠𝑐𝑎 𝑎𝑡𝑟𝑎𝑖𝑢 5 𝑝𝑒𝑖𝑥𝑒𝑠, 𝑞𝑢𝑎𝑙 𝑑𝑒𝑙𝑒𝑠 𝑣𝑜𝑐𝑒̂ 𝑣𝑎𝑖 𝑙𝑒𝑣𝑎𝑟?\n\n"
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
                    media=telebot.types.InputMediaPhoto(media=imagem_url, caption=resposta_texto))

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
            id_personagem, emoji, nome, imagem = carta_aleatoria
            send_card_message(message, emoji, id_personagem, nome, subcategoria, imagem)
            qnt_carta(id_usuario)
        else:
            print("Nenhuma carta disponível.")
    except Exception as e:
        print(f"Erro durante o processamento: {e}")
    finally:
        fechar_conexao(cursor, conn)

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

def obter_carta_evento_fixo(conn, subcategoria=None):
    try:
        cursor = conn.cursor(dictionary=True)
        if subcategoria:
            cursor.execute("SELECT emoji, id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'fixo' ORDER BY RAND() LIMIT 1", (subcategoria,))
        else:
            cursor.execute("SELECT emoji, id_personagem, nome, subcategoria, imagem FROM evento WHERE evento = 'fixo' ORDER BY RAND() LIMIT 1")
        evento_aleatorio = cursor.fetchone()
        print(f"Evento fixo aleatório: {evento_aleatorio}")
        return evento_aleatorio

    except mysql.connector.Error as err:
        print(f"Erro ao obter carta de evento fixo: {err}")
        return None
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
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n💐 ∙ {evento_aleatorio['id_personagem']} — {evento_aleatorio['nome']}\nde {subcategoria_display}"
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
            print(args)
            subcategoria_display = subcategoria.split('_')[-1]
            id_usuario = message.chat.id
            # Adicione a carta ao inventário do usuário
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

