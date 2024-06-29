import random
from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *
from inventario import *
from gif import *
from cachetools import cached, TTLCache

# Configuração da pool de conexões
dbconfig = {
        'host': '127.0.0.1',
        'database': 'garden',
        'user': 'root',
        'password': '#Folkevermore13',
        'ssl_disabled': True
}
cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=32, **dbconfig)

cache = TTLCache(maxsize=1000, ttl=600)  # Cache com 100 entradas e TTL de 300 segundos

@cached(cache)
def buscar_subcategorias(categoria):
    try:
        if categoria=="geral":
            conn = cnxpool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT subcategoria FROM personagens")
            subcategorias = cursor.fetchall()
            # Utilizando um conjunto para garantir unicidade
            subcategorias_unicas = {subcategoria[0] for subcategoria in subcategorias}
            return list(subcategorias_unicas)
        else:
            conn = cnxpool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT subcategoria FROM personagens WHERE categoria = %s", (categoria,))
            subcategorias = cursor.fetchall()
            # Utilizando um conjunto para garantir unicidade
            subcategorias_unicas = {subcategoria[0] for subcategoria in subcategorias}
            return list(subcategorias_unicas)
    except mysql.connector.Error as err:
        print(f"Erro ao buscar subcategorias: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 
def get_random_subcategories_all_valentine(connection):
    cursor = connection.cursor()

    query = "SELECT subcategoria FROM evento WHERE evento = 'aniversario' ORDER BY RAND() LIMIT 2"
    cursor.execute(query)
    subcategories_valentine = [row[0] for row in cursor.fetchall()]

    cursor.close()

    return subcategories_valentine


@cached(cache)
def buscar_subcategorias(categoria):
    conn, cursor = cnxpool.get_connection(), None
    try:
        cursor = conn.cursor()
        if categoria == "geral":
            cursor.execute("SELECT DISTINCT subcategoria FROM personagens")
        else:
            cursor.execute("SELECT DISTINCT subcategoria FROM personagens WHERE categoria = %s", (categoria,))
        subcategorias = cursor.fetchall()
        subcategorias_unicas = {subcategoria[0] for subcategoria in subcategorias}
        return list(subcategorias_unicas)
    except mysql.connector.Error as err:
        print(f"Erro ao buscar subcategorias: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def subcategoria_handler(message, subcategoria, cursor, conn, categoria,chat_id,message_id):
    id_usuario = message.chat.id
    try:
        cursor = conn.cursor()
        if verificar_se_subcategoria_tem_submenu(cursor, subcategoria):
            submenus = obter_submenus_para_subcategoria(cursor, subcategoria)
            if submenus:
                submenu_opcoes = random.sample(submenus, 2)
                enviar_opcoes_submenu(message, submenu_opcoes, subcategoria,chat_id,message_id)
                return
        cartas_disponiveis = obter_cartas_subcateg(subcategoria, conn)
        if cartas_disponiveis:
            carta_aleatoria = random.choice(cartas_disponiveis)
            if carta_aleatoria:
                id_personagem_carta, emoji, nome, imagem = carta_aleatoria
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

def verificar_se_subcategoria_tem_submenu(cursor, subcategoria):
    try:
        cursor.execute("SELECT COUNT(*) FROM subcategoria_submenu WHERE subcategoria = %s", (subcategoria,))
        return cursor.fetchone()[0] > 0
    except mysql.connector.Error as err:
        print(f"Erro ao verificar submenu da subcategoria: {err}")
        return False

def obter_submenus_para_subcategoria(cursor, subcategoria):
    try:
        cursor.execute("SELECT submenu FROM subcategoria_submenu WHERE subcategoria = %s", (subcategoria,))
        resultados = cursor.fetchall()
        return [submenu[0] for submenu in resultados]
    except mysql.connector.Error as err:
        print(f"Erro ao obter submenus da subcategoria: {err}")
        return []

def enviar_opcoes_submenu(message, submenu_opcoes, subcategoria,chat_id,message_id):
    try:
        opcoes = [telebot.types.InlineKeyboardButton(text=opcao, callback_data=f"submenu_{subcategoria}_{opcao}") for opcao in submenu_opcoes]
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        markup.add(*opcoes)
        
        # Editar a mensagem original para apresentar as opções de submenu
        bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=f"A espécie <b>{subcategoria}</b> possuí variedades, qual dessas você deseja levar?", parse_mode="HTML",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Erro ao enviar opções de submenu: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('submenu_'))
def callback_submenu_handler(call):
    try:
        data = call.data.split('_')
        subcategoria = data[1]
        submenu = data[2]

        conn = conectar_banco_dados()
        cursor = conn.cursor()
        carta = obter_carta_por_submenu(cursor, subcategoria, submenu)

        if carta:
            id_personagem, emoji, nome, imagem = carta
            send_card_message(call.message, emoji, id_personagem, nome, f"{subcategoria}_{submenu}", imagem)
        else:
            bot.send_message(call.message.chat.id, "Nenhuma carta encontrada para a combinação de subcategoria e submenu.")

    except Exception as e:
        print(f"Erro ao processar callback do submenu: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def obter_carta_por_submenu(cursor, subcategoria, submenu):
    try:
        cursor.execute("SELECT id_personagem, emoji, nome, imagem FROM personagens WHERE subcategoria = %s AND submenu = %s ORDER BY RAND() LIMIT 1", (subcategoria, submenu))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Erro ao obter carta por submenu: {err}")
        return None

def send_card_message(message, *args, cursor=None, conn=None):
    try:
        if len(args) == 1 and isinstance(args[0], dict):
            evento_aleatorio = args[0]
            subcategoria_display = evento_aleatorio['subcategoria'].split('_')[-1]
            id_usuario = message.chat.id
            id_personagem = evento_aleatorio['id_personagem']
            nome = evento_aleatorio['nome']
            subcategoria = evento_aleatorio['subcategoria']
            add_to_inventory(id_usuario, id_personagem)
            quantidade = verifica_inventario_troca(id_usuario, id_personagem)
            quantidade_display = "☀" if quantidade == 1 else "☀ 𖡩"

            if evento_aleatorio['imagem'] is None:
                imagem = "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n🪴 {evento_aleatorio['id_personagem']} - {evento_aleatorio['nome']}\nde {subcategoria_display}\n\n{quantidade_display}"
                try:
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        media=telebot.types.InputMediaPhoto(media=imagem, caption=text))
                except Exception:
                    bot.send_photo(chat_id=message.chat.id, photo=imagem, caption=text)
            else:
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n🪴 ∙ {evento_aleatorio['id_personagem']} — {evento_aleatorio['nome']}\nde {subcategoria_display}\n{quantidade_display}"
                imagem = evento_aleatorio['imagem']
                try:
                    if imagem.lower().endswith(('.jpg', '.jpeg', '.png')):
                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            media=telebot.types.InputMediaPhoto(media=imagem, caption=text))
                    elif imagem.lower().endswith(('.mp4', '.gif')):
                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            media=telebot.types.InputMediaVideo(media=imagem, caption=text))
                except Exception:
                    if imagem.lower().endswith(('.jpg', '.jpeg', '.png')):
                        bot.send_photo(chat_id=message.chat.id, photo=imagem, caption=text)
                    elif imagem.lower().endswith(('.mp4', '.gif')):
                        bot.send_video(chat_id=message.chat.id, video=imagem, caption=text)
            register_card_history(id_usuario, id_personagem)
        elif len(args) == 5:
            emoji_categoria, id_personagem, nome, subcategoria, imagem = args
            subcategoria_display = subcategoria.split('_')[-1]
            id_usuario = message.chat.id
            add_to_inventory(id_usuario, id_personagem)
            quantidade = verifica_inventario_troca(id_usuario, id_personagem)
            if imagem is None:
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n{emoji_categoria} {id_personagem} - {nome}\nde {subcategoria_display}\nQuantidade de cartas: {quantidade}"
                imagem_url = "https://telegra.ph/file/8a50bf408515b52a36734.jpg"
                try:
                    bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=message.message_id,
                        media=telebot.types.InputMediaPhoto(media=imagem_url, caption=text)
                    )
                except Exception:
                    bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=text)
            else:
                text = f"🎣 Parabéns! Sua isca era boa e você recebeu:\n\n{emoji_categoria} {id_personagem} - {nome}\nde {subcategoria_display}\n\n☀ | {quantidade}⤫"
                try:
                    if imagem.lower().endswith(('.jpg', '.jpeg', '.png')):
                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            media=telebot.types.InputMediaPhoto(media=imagem, caption=text))
                    elif imagem.lower().endswith(('.mp4', '.gif')):
                        bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=message.message_id,
                            media=telebot.types.InputMediaVideo(media=imagem, caption=text))
                except Exception:
                    if imagem.lower().endswith(('.jpg', '.jpeg', '.png')):
                        bot.send_photo(chat_id=message.chat.id, photo=imagem, caption=text)
                    elif imagem.lower().endswith(('.mp4', '.gif')):
                        bot.send_video(chat_id=message.chat.id, video=imagem, caption=text)
            register_card_history(id_usuario, id_personagem)
            if quantidade == 30:
                bot.send_message(id_usuario, "🎉 Parabéns! Você alcançou 30 cartas do personagem, pode pedir um gif usando o comando /setgif!")
        else:
            print("Número incorreto de argumentos.")
    except Exception as e:
        print(f"Erro ao enviar a mensagem da carta: {e}")

def verificar_se_subcategoria_tem_submenu(cursor, subcategoria):
    try:
        cursor.execute("SELECT COUNT(*) FROM subcategoria_submenu WHERE subcategoria = %s", (subcategoria,))
        return cursor.fetchone()[0] > 0
    except mysql.connector.Error as err:
        print(f"Erro ao verificar submenu da subcategoria: {err}")
        return False

def obter_submenus_para_subcategoria(cursor, subcategoria):
    try:
        cursor.execute("SELECT submenu FROM subcategoria_submenu WHERE subcategoria = %s", (subcategoria,))
        resultados = cursor.fetchall()
        return [submenu[0] for submenu in resultados]
    except mysql.connector.Error as err:
        print(f"Erro ao obter submenus da subcategoria: {err}")
        return []



def obter_cartas_por_subcategoria_e_submenu(subcategoria, submenu, cursor):
    try:
        cursor.execute("SELECT id_personagem, emoji, nome, imagem FROM personagens WHERE subcategoria = %s AND submenu = %s", (subcategoria, submenu))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erro ao obter cartas por subcategoria e submenu: {err}")
        return []

def obter_cartas_subcateg(subcategoria, conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_personagem, emoji, nome, imagem FROM personagens WHERE subcategoria = %s", (subcategoria,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Erro ao obter cartas da subcategoria: {err}")
        return []
    finally:
        cursor.close()


def verificar_subcategoria_evento(subcategoria, cursor):
    try:
        cursor.execute(
            "SELECT id_personagem, nome, subcategoria, imagem FROM evento WHERE subcategoria = %s AND evento = 'fixo' ORDER BY RAND() LIMIT 1",
            (subcategoria,))
        evento_aleatorio = cursor.fetchone()
        if evento_aleatorio:
            chance = random.randint(1, 100)

            if chance <= 40:
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
            return

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
        return evento_aleatorio

    except mysql.connector.Error as err:
        print(f"Erro ao obter carta de evento fixo: {err}")
        return None
    finally:
        fechar_conexao(cursor, conn) 


def register_card_history(id_usuario, id_carta):
    try:
        conn = cnxpool.get_connection()
        cursor = conn.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO historico_cartas_giradas (id_usuario, id_carta, data_hora) VALUES (%s, %s, %s)",
                       (id_usuario, id_carta, data_hora))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao registrar o histórico da carta: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
