import telebot
import mysql.connector
import random
import requests
import time
import datetime
from math import ceil

from telebot.types import InputMediaPhoto
import datetime as dt_module  
from datetime import datetime, timedelta
import re
from datetime import date
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
import threading
from album import *
from pescar import *
import diskcache as dc
# Sinalizador global para controlar o processamento de callbacks
processing_lock = threading.Lock()

# garden
bot = telebot.TeleBot("6723799817:AAFmSoj3IixvhZQuhSuai6VWNIpGXEviit8")

# Lista de IDs proibidos
ids_proibidos = {164, 165, 163, 174, 192, 214, 215, 216}
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

# Configurando o scheduler
scheduler = BackgroundScheduler(timezone=utc)
scheduler.start()
# Configurar as credenciais do Spotify
SPOTIFY_CLIENT_ID = '804047efa98c4d1d81da250b0770c05d'
SPOTIFY_CLIENT_SECRET = '6deb00cb4cea42f79abe41cc4da05f13'
ALBUM_PATH = 'album.png'
BACKGROUND_URL = 'https://i.pinimg.com/564x/19/a5/b0/19a5b0b149cd1a26f3fa7766061e902c.jpg'
BORDER_COLOR = '#DE3163'
CACHE_DIR = 'sticker_cache'
import diskcache as dc
# Verifique se o diretório de cache existe
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
# Configurar autenticação do Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))
cache = dc.Cache('./cache')  # Configuração do caminho do cache
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
load_state = {}
phrases = [
    "Você abre seu diário e escreve sobre como acordou com o som suave dos pássaros, e a brisa fresca da manhã trouxe consigo o perfume das flores do campo.",
    "Você abre seu diário e escreve sobre a tarde que passou colhendo flores silvestres e sentindo a grama macia sob seus pés descalços. Há algo de mágico na simplicidade da natureza.",
    "Você abre seu diário e escreve sobre o momento em que preparava o chá com ervas frescas do seu jardim, percebendo a beleza dos pequenos detalhes que tornam a vida tão especial.",
    "Você abre seu diário e escreve sobre a luz do sol filtrada pelas árvores, criando sombras dançantes no chão da floresta, lembrando-lhe que a beleza pode ser encontrada nas coisas mais simples.",
    "Você abre seu diário e escreve sobre a serenidade de bordar à beira da lareira, sentindo uma profunda conexão com as tradições antigas e o estilo de vida rural.",
    "Você abre seu diário e escreve sobre como cuidar do jardim é terapêutico. Cada planta que floresce é um lembrete da paciência e do cuidado que cultivamos em nossas vidas.",
    "Você abre seu diário e escreve sobre como os dias são mais doces quando preenchidos com atividades simples, como fazer pão caseiro e ouvir o canto dos pássaros.",
    "Você abre seu diário e escreve sobre as noites na cabana, acolhedoras e tranquilas. O crepitar do fogo na lareira é a melodia perfeita para um coração em paz.",
    "Você abre seu diário e escreve sobre o momento em que se sentou à sombra de um carvalho antigo, lendo um livro enquanto a natureza sussurrava seus segredos ao seu redor.",
    "Você abre seu diário e escreve sobre como a vida no campo ensina a valorizar a calma e a beleza que existem no presente. Cada momento é um presente a ser apreciado.",
    "Você abre seu diário e escreve sobre como passou a manhã fazendo geleia de frutas frescas, sentindo o doce aroma se espalhar pela cozinha.",
    "Você abre seu diário e escreve sobre a caminhada pelo bosque, onde encontrou um riacho cristalino que parecia sussurrar segredos antigos.",
    "Você abre seu diário e escreve sobre a tarde que passou tricotando uma manta macia, cada ponto representando uma memória querida.",
    "Você abre seu diário e escreve sobre a visita ao mercado local, onde encontrou produtos frescos e artesanatos únicos.",
    "Você abre seu diário e escreve sobre o momento em que se sentou no alpendre, observando o pôr do sol tingir o céu de tons dourados e rosados.",
    "Você abre seu diário e escreve sobre o prazer de ler um livro clássico à sombra de uma árvore frondosa, ouvindo o som suave das folhas ao vento.",
    "Você abre seu diário e escreve sobre o aroma da lavanda que plantou no jardim, trazendo um senso de calma e serenidade.",
    "Você abre seu diário e escreve sobre o prazer de fazer uma torta caseira, desde amassar a massa até saborear o resultado final.",
    "Você abre seu diário e escreve sobre como decorou a casa com flores silvestres, enchendo os cômodos de cores vibrantes e vida.",
    "Você abre seu diário e escreve sobre a alegria de alimentar os animais da fazenda, sentindo a conexão com cada ser vivo.",
    "Você abre seu diário e escreve sobre a manhã passada ajudando os vizinhos a colher maçãs no pomar comunitário, compartilhando risadas e histórias antigas.",
    "Você abre seu diário e escreve sobre o piquenique à beira do lago com outros camponeses, onde cada um trouxe um prato caseiro para compartilhar.",
    "Você abre seu diário e escreve sobre a feira de trocas na aldeia, onde artesãos e agricultores se reuniram para trocar seus produtos e habilidades.",
    "Você abre seu diário e escreve sobre a tarde em que ajudou um vizinho a construir uma cerca, aprendendo novas habilidades e fortalecendo amizades.",
    "Você abre seu diário e escreve sobre a festa da colheita, onde dançou ao som de músicas tradicionais e celebrou a abundância com os outros moradores.",
    "Você abre seu diário e escreve sobre a reunião ao redor da fogueira, onde ouviu histórias de tempos passados e compartilhou risadas com amigos.",
    "Você abre seu diário e escreve sobre a visita à feira de artesanato local, onde conheceu artesãos talentosos e aprendeu sobre suas técnicas.",
    "Você abre seu diário e escreve sobre o mutirão para plantar árvores na praça da aldeia, sentindo a alegria de contribuir para o futuro da comunidade.",
    "Você abre seu diário e escreve sobre a tarde em que preparou um chá para os vizinhos, desfrutando de uma conversa agradável e fortalecendo laços.",
    "Você abre seu diário e escreve sobre a caminhada com outros camponeses pelas trilhas da floresta, apreciando a natureza e a companhia um do outro."
]

# Lista de sortes do dia
fortunes = [
    "Sorte do dia: Hoje você encontrará paz nos sons da natureza.",
    "Sorte do dia: Pequenos momentos trarão grandes alegrias hoje.",
    "Sorte do dia: A simplicidade será sua maior aliada.",
    "Sorte do dia: Beleza inesperada surgirá em seu caminho.",
    "Sorte do dia: Conexões profundas enriquecerão seu dia.",
    "Sorte do dia: Sua paciência será recompensada hoje.",
    "Sorte do dia: Encontre doçura nas tarefas simples.",
    "Sorte do dia: A tranquilidade estará ao seu alcance.",
    "Sorte do dia: A sabedoria chegará até você em momentos de quietude.",
    "Sorte do dia: Aprecie cada momento, pois eles são únicos.",
    "Sorte do dia: Hoje, você saboreará os frutos do seu trabalho.",
    "Sorte do dia: Novas descobertas trarão alegria ao seu dia.",
    "Sorte do dia: Seus esforços de hoje criarão conforto para o futuro.",
    "Sorte do dia: Conexões locais enriquecerão sua vida hoje.",
    "Sorte do dia: A beleza do entardecer trará paz ao seu coração.",
    "Sorte do dia: Encontre inspiração nas palavras dos sábios de antigamente.",
    "Sorte do dia: Aromas calmantes irão transformar seu ambiente.",
    "Sorte do dia: A satisfação estará nos detalhes das suas criações.",
    "Sorte do dia: A natureza trará alegria e cor ao seu espaço.",
    "Sorte do dia: A interação com os animais trará momentos de pura felicidade.",
    "Sorte do dia: A colaboração trará alegria e união ao seu dia.",
    "Sorte do dia: O compartilhamento de alimentos fortalecerá os laços de amizade.",
    "Sorte do dia: Novas conexões trarão oportunidades valiosas.",
    "Sorte do dia: Ajudar os outros trará uma sensação de realização e comunidade.",
    "Sorte do dia: Celebrações comunitárias encherão seu coração de alegria.",
    "Sorte do dia: As histórias compartilhadas fortalecerão os vínculos de amizade.",
    "Sorte do dia: Aprender com os outros enriquecerá sua perspectiva.",
    "Sorte do dia: Seus esforços comunitários trarão benefícios duradouros.",
    "Sorte do dia: Pequenos gestos de hospitalidade criarão grandes memórias.",
    "Sorte do dia: A camaradagem ao ar livre renovará seu espírito."
]


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
# Dicionário para armazenar os estados baseados no chat_id
state_data = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("change_page_"))
def handle_page_change(call):
    page_index = int(call.data.split("_")[2])
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    data = state_data.get(chat_id)
    if not data:
        bot.answer_callback_query(call.id, "Dados não encontrados.")
        return

    if isinstance(data, list):
        mensagens = data
    else:
        bot.answer_callback_query(call.id, "Erro no formato dos dados.")
        return

    total_count = len(mensagens)
    if 0 <= page_index < total_count:
        media_url, mensagem = mensagens[page_index]
        markup = create_navigation_markup(page_index, total_count)

        try:
            update_message_media(media_url, mensagem, chat_id, message_id, markup)
            bot.answer_callback_query(call.id)
        except Exception as e:
            bot.answer_callback_query(call.id, "Falha ao atualizar a mensagem.")
    else:
        bot.answer_callback_query(call.id, "Índice de página inválido.")

def update_message_media(media_url, mensagem, chat_id, message_id, markup):
    if media_url.lower().endswith(".gif"):
        bot.edit_message_media(media=types.InputMediaAnimation(media_url, caption=mensagem,parse_mode="HTML"), chat_id=chat_id, message_id=message_id, reply_markup=markup)
    elif media_url.lower().endswith(".mp4"):
        bot.edit_message_media(media=types.InputMediaVideo(media_url, caption=mensagem,parse_mode="HTML"), chat_id=chat_id, message_id=message_id, reply_markup=markup)
    elif media_url.lower().endswith((".jpeg", ".jpg", ".png")):
        bot.edit_message_media(media=types.InputMediaPhoto(media_url, caption=mensagem,parse_mode="HTML"), chat_id=chat_id, message_id=message_id, reply_markup=markup)
    else:
        bot.edit_message_text(text=mensagem, chat_id=chat_id, message_id=message_id, reply_markup=markup,parse_mode="HTML")

def save_user_state(chat_id, data):
    state_data[chat_id] = data
@bot.callback_query_handler(func=lambda call: call.data.startswith('submenu_'))
def callback_submenu(call):
    _, subcategoria, submenu_selecionado = call.data.split('_')
    conn, cursor = conectar_banco_dados()
    try:
        cartas_disponiveis = obter_cartas_por_subcategoria_e_submenu(subcategoria, submenu_selecionado, cursor)
        if cartas_disponiveis:
            carta_aleatoria = random.choice(cartas_disponiveis)
            if carta_aleatoria:
                id_personagem_carta, emoji, nome, imagem = carta_aleatoria
                send_card_message(call.message, emoji, id_personagem_carta, nome, subcategoria, imagem)
                qnt_carta(call.message.chat.id)
            else:
                bot.send_message(call.message.chat.id, "Nenhuma carta disponível para esta combinação de subcategoria e submenu.")
        else:
            bot.send_message(call.message.chat.id, "Nenhuma carta disponível para esta combinação de subcategoria e submenu.")
    finally:
        cursor.close()
        conn.close()       

@bot.callback_query_handler(func=lambda call: call.data == "add_note")
def handle_add_note_callback(call):
    markup = telebot.types.InlineKeyboardMarkup()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Por favor, envie sua anotação para o diário.", reply_markup=markup)
    bot.register_next_step_handler(call.message, receive_note)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_note")
def handle_cancel_note_callback(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Tudo bem, até amanhã!")
@bot.callback_query_handler(func=lambda call: call.data.startswith('help_'))
def callback_help(call):
    if call.data == 'help_cartas':
        help_text = (
            "<b>Aqui estão os comandos relacionados a Cartas:</b>\n\n"
            "<b>/armazem, /armazém, /amz </b> - Olhe os peixes (cartas) que você possui.\n"
            "<b>"
            
            
            
            
        )
    elif call.data == 'help_trocas':
        help_text = "Aqui estão os comandos relacionados a Trocas:\n\n"
        # Adicione a descrição dos comandos relacionados a Trocas
        help_text += "/troca - Comando de troca (detalhes do comando de troca).\n"
    elif call.data == 'help_eventos':
        help_text = "Aqui estão os comandos relacionados a Eventos:\n\n"
        # Adicione a descrição dos comandos relacionados a Eventos
        help_text += "<b>/evento (f ou s para faltantes ou possuidos) </b>- Comando ver os peixes de eventos. ex: /evento s amor. \n"

    elif call.data == 'help_bugs':
        help_text = "Aqui estão os comandos relacionados a Usuários:\n\n"
        # Adicione a descrição dos comandos relacionados a Bugs
        help_text += ("/setuser - Comando para definir seu usuário. ex: /setuser maria\n"
                      "/setfav - Comando para definir seu peixe favorito, que aparece no seu armazem e perfil. ex: /setfav 10150"
                      "/removefav - Comando para remover seu peixe favorito. ex: /removefav 10150"
                      )
    elif call.data == 'help_tudo':
        help_text = (
            "Aqui estão todos os comandos disponíveis:\n\n"
            "/armazem, /armazém, /amz - Olhe os peixes (cartas) que você possui.\n"
            "/evento evento <subcategoria> - Comando para interagir com eventos. Use /evento s para subcategoria e /evento f para favoritos.\n"
            "/troca - Comando de troca (detalhes do comando de troca).\n"
            "/reportar_bug - Comando para reportar bugs.\n"
        )
    
    bot.edit_message_text(help_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lembrete_"))
def callback_query_lembrete(call):
    data_parts = call.data.split('_')
    tipo = data_parts[1]
    id_usuario = int(data_parts[2])
    ativar = data_parts[3] == 'True'
    
    conn, cursor = conectar_banco_dados()
    
    if tipo == "fonte":
        cursor.execute("UPDATE lembretes SET fonte = %s WHERE id_usuario = %s", (ativar, id_usuario))
    elif tipo == "gif":
        cursor.execute("UPDATE lembretes SET gif = %s WHERE id_usuario = %s", (ativar, id_usuario))
        if ativar:
            verifica_tempo_ultimo_gif(id_usuario)
    elif tipo == "diary":
        cursor.execute("UPDATE lembretes SET diary = %s WHERE id_usuario = %s", (ativar, id_usuario))
    
    conn.commit()
    fechar_conexao(cursor, conn)
    
    # Retrieve the updated preferences to display
    lembrete_command(call)  # Adjusted to pass 'call' directly
    
@bot.message_handler(commands=['casar'])
def processar_comando_casar(message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            bot.reply_to(message, "Por favor, forneça o ID do personagem no formato '/casar id_personagem'.")
            return

        id_personagem = command_parts[1]

        # Verificar se o ID do personagem está na lista proibida
        if int(id_personagem) in ids_proibidos:
            bot.reply_to(message, "Você não pode se casar com esse personagem.")
            return

        conn, cursor = conectar_banco_dados()
        query = "SELECT nome, evento FROM evento WHERE id_personagem = %s"
        cursor.execute(query, (id_personagem,))
        resultado = cursor.fetchone()

        if resultado and resultado[1] == 'amor':
            nome = resultado[0]

            user_id = message.from_user.id

            # Verificar se o usuário já está casado ou já foi rejeitado pelo personagem
            cursor.execute("SELECT estado FROM casamentos WHERE user_id = %s AND id_personagem = %s", (user_id, id_personagem))
            casamento = cursor.fetchone()

            if casamento:
                if casamento[0] == 'casado':
                    bot.reply_to(message, "Você já está casado com este personagem.")
                    fechar_conexao(cursor, conn)
                    return
                elif casamento[0] == 'divorciado':
                    bot.reply_to(message, "Este personagem já te rejeitou uma vez. Você não pode pedir novamente.")
                    fechar_conexao(cursor, conn)
                    return

            # Verificar se o usuário já está casado com outro personagem
            cursor.execute("SELECT COUNT(*) FROM casamentos WHERE user_id = %s AND estado = 'casado'", (user_id,))
            ja_casado = cursor.fetchone()[0]

            if ja_casado > 0:
                bot.reply_to(message, "Você já está casado. Não pode se casar novamente.")
                fechar_conexao(cursor, conn)
                return

            # Perguntar ao usuário se deseja casar
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Sim", callback_data=f"casar_sim_{id_personagem}_{nome}"),
                       InlineKeyboardButton("Não", callback_data="casar_nao"))

            bot.reply_to(message, f"Na alegria e na tristeza, na saúde e na doença, todos os dias da sua vida! Tem certeza que deseja se casar com {id_personagem} - {nome}?", reply_markup=markup)

        else:
            bot.reply_to(message, "Personagem não encontrado ou não é do tipo 'amor'.")

        fechar_conexao(cursor, conn)

    except Exception as e:
        bot.reply_to(message, f"Erro ao processar o comando /casar: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('casar_'))
def callback_casar(call):
    try:
        if call.data.startswith("casar_sim"):
            _, _, id_personagem, nome = call.data.split('_')
            user_id = call.from_user.id

            if random.random() < 0.7:
                # Sucesso no casamento
                conn, cursor = conectar_banco_dados()
                query = "INSERT INTO casamentos (user_id, id_personagem, estado) VALUES (%s, %s, 'casado')"
                cursor.execute(query, (user_id, id_personagem))
                conn.commit()
                fechar_conexao(cursor, conn)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Parabéns! Você agora está casado com {nome}!")
            else:
                # Falha no casamento
                conn, cursor = conectar_banco_dados()
                query = "INSERT INTO casamentos (user_id, id_personagem, estado) VALUES (%s, %s, 'divorciado')"
                cursor.execute(query, (user_id, id_personagem))
                conn.commit()
                fechar_conexao(cursor, conn)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Infelizmente, {nome} rejeitou seu pedido de casamento.")
        elif call.data == "casar_nao":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Pedido de casamento cancelado.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Erro ao processar o callback de casamento: {e}")

@bot.message_handler(commands=['divorciar'])
def processar_comando_divorciar(message):
    try:
        user_id = message.from_user.id

        conn, cursor = conectar_banco_dados()

        # Verificar se o usuário está casado
        cursor.execute("SELECT id_personagem FROM casamentos WHERE user_id = %s AND estado = 'casado'", (user_id,))
        casamento = cursor.fetchone()

        if casamento:
            id_personagem = casamento[0]

            # Verificar se já se divorciou uma vez
            cursor.execute("SELECT COUNT(*) FROM casamentos WHERE user_id = %s AND estado = 'divorciado'", (user_id,))
            divorcios = cursor.fetchone()[0]

            if divorcios > 0:
                bot.reply_to(message, "Você já se divorciou uma vez e não pode se divorciar novamente.")
            else:
                # Atualizar estado para divorciado
                cursor.execute("UPDATE casamentos SET estado = 'divorciado' WHERE user_id = %s AND id_personagem = %s", (user_id, id_personagem))
                conn.commit()
                bot.reply_to(message, f"Você se divorciou de {id_personagem}. Agora você pode casar novamente.")

        else:
            bot.reply_to(message, "Você não está casado.")

        fechar_conexao(cursor, conn)

    except Exception as e:
        bot.reply_to(message, f"Erro ao processar o comando /divorciar: {e}")

def notificar_usuario_sobre_gif(id_usuario):
    bot.send_message(id_usuario, "Você já pode pedir gif!")

def agendar_notificacao_de_gif(id_usuario):
    # Calcula quando enviar a notificação (1 hora após o último gif)
    proxima_notificacao = datetime.now() + timedelta(hours=1)
    scheduler.add_job(notificar_usuario_sobre_gif, 'date', run_date=proxima_notificacao, args=[id_usuario])

def enviar_lembrete_diary():
    conn, cursor = conectar_banco_dados()
    
    # Seleciona todos os usuários que ativaram o lembrete 'diary'
    cursor.execute("SELECT id_usuario FROM lembretes WHERE diary = TRUE")
    usuarios = cursor.fetchall()
    
    for usuario in usuarios:
        user_id = usuario[0]
        try:
            bot.send_message(user_id, "Não esqueça de registrar seu diário hoje! Use o comando /diary.")
        except Exception as e:
            print(f"Não foi possível enviar a mensagem para o usuário {user_id}: {e}")
    
    fechar_conexao(cursor, conn)

# Agendando a tarefa para ser executada todos os dias à meia-noite
scheduler.add_job(enviar_lembrete_diary, 'cron', hour=0, minute=0)     
def verifica_tempo_ultimo(id_usuario):
    conn, cursor = conectar_banco_dados()
    try:
        # Verifica se a configuração de gif está ativada
        cursor.execute("SELECT gif FROM lembretes WHERE id_usuario = %s", (id_usuario,))
        config = cursor.fetchone()

        if config and config[0] == 1:
            cursor.execute("SELECT MAX(timestamp) FROM gif WHERE id_usuario = %s", (id_usuario,))
            ultimo_gif = cursor.fetchone()

            if ultimo_gif and ultimo_gif[0]:
                ultimo_gif_datetime = ultimo_gif[0]
                diferenca_tempo = datetime.now() - ultimo_gif_datetime

                if diferenca_tempo.total_seconds() >= 3600:
                    notificar_usuario_sobre_gif(id_usuario)
                else:
                    tempo_restante = 3600 - diferenca_tempo.total_seconds()
                    # Agendar notificação para quando completar 1 hora
                    scheduler.add_job(notificar_usuario_sobre_gif, 'date', run_date=datetime.now() + timedelta(seconds=tempo_restante), args=[id_usuario])

    except Exception as e:
        print(f"Erro ao verificar tempo do último gif: {e}")
    finally:
        fechar_conexao(cursor, conn)
   
@bot.message_handler(commands=['trade'])
def trade_stickers(message):
    user_id = message.from_user.id
    reply_to_message = message.reply_to_message

    if not reply_to_message:
        bot.send_message(message.chat.id, "Você deve responder a uma mensagem da pessoa com quem deseja trocar figurinhas.")
        return

    other_user_id = reply_to_message.from_user.id
    trade_info = message.text.split()[1:]

    if len(trade_info) != 2:
        bot.send_message(message.chat.id, "Formato inválido. Use /trade luv{seu_numero} luv{numero_outro_usuario}")
        return

    try:
        user_sticker_id = int(''.join(filter(str.isdigit, trade_info[0])))
        other_sticker_id = int(''.join(filter(str.isdigit, trade_info[1])))
    except ValueError:
        bot.send_message(message.chat.id, "Os IDs das figurinhas devem conter números. Use /trade luv{seu_numero} luv{numero_outro_usuario}")
        return

    # Verifique se ambos os usuários têm as figurinhas repetidas
    if not has_repeated_sticker(user_id, user_sticker_id):
        bot.send_message(message.chat.id, "Essa figurinha já foi colada e não pode ser trocada.")
        return

    if not has_repeated_sticker(other_user_id, other_sticker_id):
        bot.send_message(message.chat.id, "Essa figurinha do outro usuário já foi colada e não pode ser trocada.")
        return

    # Criar botões para a outra pessoa aceitar ou recusar a troca
    markup = types.InlineKeyboardMarkup()
    accept_button = types.InlineKeyboardButton("Aceitar Troca", callback_data=f"accept_trade_{user_sticker_id}_{other_sticker_id}_{user_id}_{other_user_id}")
    decline_button = types.InlineKeyboardButton("Recusar Troca", callback_data=f"decline_trade_{user_sticker_id}_{other_sticker_id}_{user_id}_{other_user_id}")
    markup.add(accept_button, decline_button)

    bot.send_message(reply_to_message.chat.id, f"{reply_to_message.from_user.first_name}, {message.from_user.first_name} quer trocar a figurinha {user_sticker_id} pela sua figurinha {other_sticker_id}.", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_trade_'))
def accept_trade(call):
    data = call.data.split('_')
    user_sticker_id = int(data[2])
    other_sticker_id = int(data[3])
    requester_id = int(data[4])
    accepter_id = int(data[5])

    if call.from_user.id != accepter_id:
        bot.answer_callback_query(call.id, "Você não tem permissão para aceitar essa troca.")
        return

    # Realizar a troca
    try:
        if execute_trade(requester_id, accepter_id, user_sticker_id, other_sticker_id):
            bot.send_message(call.message.chat.id, "Troca realizada com sucesso!")
        else:
            bot.send_message(call.message.chat.id, "Erro ao realizar a troca. Tente novamente mais tarde.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Erro ao realizar a troca: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('decline_trade_'))
def decline_trade(call):
    data = call.data.split('_')
    user_sticker_id = int(data[2])
    other_sticker_id = int(data[3])
    requester_id = int(data[4])
    accepter_id = int(data[5])

    if call.from_user.id != accepter_id:
        bot.answer_callback_query(call.id, "Você não tem permissão para recusar essa troca.")
        return

    bot.send_message(call.message.chat.id, "Troca recusada.")
@bot.callback_query_handler(func=lambda call: call.data == "lembretes")
def lembrete_command(call):
    id_usuario = call.from_user.id
    
    conn, cursor = conectar_banco_dados()
    
    # Verificar se o usuário já tem registros na tabela de lembretes
    cursor.execute("SELECT fonte, gif, diary FROM lembretes WHERE id_usuario = %s", (id_usuario,))
    lembretes = cursor.fetchone()
    
    if not lembretes:
        # Se não existir, criar um novo registro com valores padrão desativados
        cursor.execute("INSERT INTO lembretes (id_usuario, fonte, gif, diary) VALUES (%s, %s, %s, %s)", (id_usuario, False, False, False))
        conn.commit()
        lembretes = (False, False, False)
    
    fonte, gif, diary = lembretes

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"Fonte {'✅' if fonte else '❌'}", callback_data=f"lembrete_fonte_{id_usuario}_{not fonte}"))
    markup.add(InlineKeyboardButton(f"GIF {'✅' if gif else '❌'}", callback_data=f"lembrete_gif_{id_usuario}_{not gif}"))
    markup.add(InlineKeyboardButton(f"Diary {'✅' if diary else '❌'}", callback_data=f"lembrete_diary_{id_usuario}_{not diary}"))
    
    bot.edit_message_text("Escolha suas preferências de lembrete:", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    
    fechar_conexao(cursor, conn)


def has_repeated_sticker(user_id, sticker_id):
    conn, cursor = conectar_banco_dados()
    cursor.execute('''
        SELECT quantity 
        FROM inventariofig 
        WHERE user_id = %s AND sticker_id = %s
    ''', (user_id, sticker_id))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result and result[0] > 1

def execute_trade(requester_id, accepter_id, requester_sticker_id, accepter_sticker_id):
    conn, cursor = conectar_banco_dados()

    try:
        # Verificar novamente se ambos têm mais de uma unidade das figurinhas
        cursor.execute('''
            SELECT quantity 
            FROM inventariofig 
            WHERE user_id = %s AND sticker_id = %s
        ''', (requester_id, requester_sticker_id))
        requester_quantity = cursor.fetchone()[0]

        cursor.execute('''
            SELECT quantity 
            FROM inventariofig 
            WHERE user_id = %s AND sticker_id = %s
        ''', (accepter_id, accepter_sticker_id))
        accepter_quantity = cursor.fetchone()[0]

        if requester_quantity < 2 or accepter_quantity < 2:
            raise Exception("Uma das figurinhas não é repetida e não pode ser trocada.")

        # Remover uma figurinha do solicitante
        cursor.execute('''
            UPDATE inventariofig 
            SET quantity = quantity - 1 
            WHERE user_id = %s AND sticker_id = %s
        ''', (requester_id, requester_sticker_id))

        # Adicionar a figurinha ao solicitante
        cursor.execute('''
            INSERT INTO inventariofig (user_id, sticker_id, quantity)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE
            quantity = quantity + 1
        ''', (requester_id, accepter_sticker_id))

        # Remover uma figurinha do aceito
        cursor.execute('''
            UPDATE inventariofig 
            SET quantity = quantity - 1 
            WHERE user_id = %s AND sticker_id = %s
        ''', (accepter_id, accepter_sticker_id))

        # Adicionar a figurinha ao aceito
        cursor.execute('''
            INSERT INTO inventariofig (user_id, sticker_id, quantity)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE
            quantity = quantity + 1
        ''', (accepter_id, requester_sticker_id))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao realizar a troca: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
        
@bot.message_handler(commands=['album'])
def send_album(message):
    user_id = message.from_user.id
    page = 1  # Página inicial

    
    album_path = create_album(user_id, page)
    if album_path:
        with open(album_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, reply_markup=get_navigation_markup(page))
    else:
        bot.send_message(message.chat.id, "Houve um erro ao gerar o álbum. Tente novamente mais tarde.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def callback_page(call):
    user_id = call.from_user.id
    page = int(call.data.split('_')[1])
    album_path = create_album(user_id, page)
    
    if album_path:
        with open(album_path, 'rb') as photo:
            bot.edit_message_media(media=telebot.types.InputMediaPhoto(photo), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_navigation_markup(page))
    else:
        bot.send_message(call.message.chat.id, "Houve um erro ao atualizar o álbum. Tente novamente mais tarde.")

@bot.message_handler(commands=['figurinhas'])
def send_random_stickers(message):
    try:
        user_id = message.from_user.id
        conn, cursor = conectar_banco_dados()

        # Selecionar 5 figurinhas aleatórias, permitindo repetidas
        cursor.execute('SELECT id, image_path FROM stickers')
        all_stickers = cursor.fetchall()
        random_stickers = [random.choice(all_stickers) for _ in range(5)]

        # Verificar quais figurinhas o usuário já possui
        cursor.execute('SELECT sticker_id FROM inventariofig WHERE user_id = %s', (user_id,))
        user_stickers = {row[0] for row in cursor.fetchall()}

        # Adicionar as figurinhas ao inventário do usuário e determinar bordas
        sticker_borders = []
        for sticker_id, sticker_url in random_stickers:
            if sticker_id in user_stickers:
                # Figurinha repetida
                border_color = 'black'
                border_width = 2
                cursor.execute('UPDATE inventariofig SET quantity = quantity + 1 WHERE user_id = %s AND sticker_id = %s', (user_id, sticker_id))
            else:
                # Figurinha nova
                border_color = 'gold'
                border_width = 5
                cursor.execute('INSERT INTO inventariofig (user_id, sticker_id, quantity) VALUES (%s, %s, 1)', (user_id, sticker_id))
                user_stickers.add(sticker_id)
            sticker_borders.append((sticker_url, border_color, border_width))
        
        conn.commit()
        cursor.close()
        conn.close()

        # Baixar a imagem de fundo
        background_url = 'https://telegra.ph/file/33879a99c60ca9d11e60c.png'
        response = requests.get(background_url)
        background = Image.open(BytesIO(response.content))

        # Definir tamanho e layout da imagem final (quadrada)
        width, height = background.size
        sticker_width, sticker_height = 140, 210  # Tamanho das figurinhas
        padding = 20  # Espaço entre figurinhas

        # Redimensionar fundo para um quadrado se necessário
        background = background.resize((width, width))

        # Criar uma nova imagem com o fundo
        img = Image.new('RGB', (width, width))
        img.paste(background, (0, 0))

        draw = ImageDraw.Draw(img)

        # Coordenadas das 5 figurinhas (3-2 centralizado)
        start_x = (width - 3 * sticker_width - 2 * padding) // 2
        start_y = (width - 2 * sticker_height - padding) // 2

        coordinates = [
            (start_x, start_y),
            (start_x + sticker_width + padding, start_y),
            (start_x + 2 * (sticker_width + padding), start_y),
            (start_x + (sticker_width // 2) + (padding // 2), start_y + sticker_height + padding),
            (start_x + sticker_width + (padding // 2) + (sticker_width // 2) + padding, start_y + sticker_height + padding)
        ]

        # Adicionar as figurinhas à imagem
        for (sticker_url, border_color, border_width), coord in zip(sticker_borders, coordinates):
            response = requests.get(sticker_url)
            sticker_image = Image.open(BytesIO(response.content))
            sticker_image = sticker_image.resize((sticker_width, sticker_height))
            
            # Adicionar borda à figurinha
            bordered_sticker = ImageOps.expand(sticker_image, border=border_width, fill=border_color)
            
            # Colar a figurinha na posição correta
            img.paste(bordered_sticker, coord)

        # Salvar a imagem final
        result_image_path = 'random_stickers.png'
        img.save(result_image_path)

        # Enviar a imagem das figurinhas sorteadas
        with open(result_image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)

        bot.reply_to(message, "5 figurinhas aleatórias foram adicionadas ao seu inventário!")
    except Exception as e:
        bot.reply_to(message, f"Houve um erro ao adicionar as figurinhas: {e}")
@bot.message_handler(commands=['albf'])
def send_missing_album_list(message):
    user_id = message.from_user.id
    page = 1
    stickers_per_page = 9
    missing_stickers, total_missing = get_missing_stickers(user_id, page, stickers_per_page)
    total_pages = (total_missing + stickers_per_page - 1) // stickers_per_page

    if not missing_stickers:
        bot.reply_to(message, "Você já possui todas as figurinhas.")
        return

    user_name = message.from_user.first_name
    album_text = '\n'.join([f"luv{sticker[0]} - {sticker[1]}" for sticker in missing_stickers])
    markup = get_missing_album_markup(page, total_pages)
    bot.send_message(message.chat.id, f"Álbum de figurinhas faltantes de {user_name}:\n\n{total_missing}/40\n\n{album_text}", reply_markup=markup)
@bot.message_handler(commands=['fig'])
def send_sticker(message):
    try:
        args = message.text.split()
        if len(args) != 2:
            bot.reply_to(message, "Uso: /fig <id>")
            return
        
        sticker_id = int(args[1].replace('luv', ''))
        sticker = get_sticker_by_id(sticker_id)

        if not sticker:
            bot.reply_to(message, "Figurinha não encontrada.")
            return

        sticker_id, name, image_path = sticker

        caption = f"ID: luv{sticker_id}\nNome: {name}"

        # Enviar a imagem da figurinha diretamente pelo caminho fornecido
        bot.send_photo(message.chat.id, image_path, caption=caption)

    except Exception as e:
        bot.reply_to(message, f"Houve um erro ao buscar a figurinha: {e}")

@bot.message_handler(commands=['alb'])
def send_album_list(message):
    user_id = message.from_user.id
    page = 1
    stickers = get_user_stickers(user_id, page)
    total_pages = get_total_pages(user_id)
    total_stickers = get_total_stickers(user_id)

    if not stickers:
        bot.reply_to(message, "Você não possui figurinhas.")
        return

    user_name = message.from_user.first_name
    album_text = '\n'.join([f"luv{sticker[0]} - {sticker[1]}" + (f" (x{sticker[3]})" if sticker[3] > 1 else "") for sticker in stickers])
    markup = get_album_markup(page, total_pages)
    bot.send_message(message.chat.id, f"Álbum de figurinhas de {user_name}:\n\n{total_stickers}/40\n\n{album_text}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('prev_') or call.data.startswith('next_'))
def callback_page(call):
    user_id = call.from_user.id
    page = int(call.data.split('_')[1])
    stickers = get_user_stickers(user_id, page)
    total_pages = get_total_pages(user_id)
    total_stickers = get_total_stickers(user_id)

    if not stickers:
        bot.answer_callback_query(call.id, "Nenhuma figurinha nesta página.")
        return

    user_name = call.from_user.first_name
    album_text = '\n'.join([f"luv{sticker[0]} - {sticker[1]}" + (f" (x{sticker[3]})" if sticker[3] > 1 else "") for sticker in stickers])
    markup = get_album_markup(page, total_pages)
    bot.edit_message_text(f"Álbum de figurinhas de {user_name}:\n\n{total_stickers}/40\n\n{album_text}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)
@bot.callback_query_handler(func=lambda call: call.data.startswith('missing_prev_') or call.data.startswith('missing_next_'))
def callback_page_missing(call):
    user_id = call.from_user.id
    page = int(call.data.split('_')[2])
    stickers_per_page = 9
    missing_stickers, total_missing = get_missing_stickers(user_id, page, stickers_per_page)
    total_pages = (total_missing + stickers_per_page - 1) // stickers_per_page

    if not missing_stickers:
        bot.answer_callback_query(call.id, "Nenhuma figurinha faltante nesta página.")
        return

    user_name = call.from_user.first_name
    album_text = '\n'.join([f"luv{sticker[0]} - {sticker[1]}" for sticker in missing_stickers])
    markup = get_missing_album_markup(page, total_pages)
    bot.edit_message_text(f"Álbum de figurinhas faltantes de {user_name}:\n\n{total_missing}/40\n\n{album_text}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("submenus_"))
def callback_submenus(call):
    try:
        parts = call.data.split('_')
        pagina = int(parts[1])
        subcategoria = parts[2]

        conn, cursor = conectar_banco_dados()
        query_total = "SELECT COUNT(DISTINCT submenu) FROM personagens WHERE subcategoria = %s"
        cursor.execute(query_total, (subcategoria,))
        total_registros = cursor.fetchone()[0]
        total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)

        editar_mensagem_submenus(call, subcategoria, pagina, total_paginas)

    except Exception as e:
        print(f"Erro ao processar callback de página para submenus: {e}")
        
@bot.callback_query_handler(func=lambda call: call.data.startswith("especies_"))
def callback_especies(call):
    try:
        parts = call.data.split('_')
        pagina = int(parts[1])
        categoria = parts[2]

        conn, cursor = conectar_banco_dados()
        query_total = "SELECT COUNT(DISTINCT subcategoria) FROM personagens WHERE categoria = %s"
        cursor.execute(query_total, (categoria,))
        total_registros = cursor.fetchone()[0]
        total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)

        editar_mensagem_especies(call, categoria, pagina, total_paginas)

    except Exception as e:
        print(f"Erro ao processar callback de página para espécies: {e}")

def create_wish_buttons():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Fazer pedido", callback_data="fazer_pedido"))
    markup.add(InlineKeyboardButton(text="Cancelar", callback_data="pedido_cancelar"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('poço_dos_desejos'))
def handle_poco_dos_desejos(call):
    usuario = call.from_user.first_name
    image_url = "https://telegra.ph/file/94c9c66af4ca4d6f0a3e5.jpg"
    caption = (f"<i>Enquanto os demais camponeses estavam distraídos com suas pescas, {usuario} caminhava para um lugar mais distante, até que encontrou uma floresta mágica.\n\n</i>"
               "<i>Já havia escutado seus colegas falando da mesma mas sempre duvidou que era real.</i>\n\n"
               "⛲: <i><b>Oh! Olá camponês, imagino que a dona do jardim tenha te mandado pra cá, certo?</b></i>\n\n"
               "<i>Apesar da confusão com a voz repentina, perguntou a fonte o que aquilo significava.\n\n</i>"
               "⛲: <i><b>Sou uma fonte dos desejos! você tem direito a fazer um pedido, em troca eu peço apenas algumas cenouras. Se os peixes que você deseja estiverem disponíveis e a sorte ao seu favor eles irão aparecer no seu armazém. Se não, volte mais tarde com outras cenouras.</b></i>")
    media = InputMediaPhoto(image_url, caption=caption, parse_mode="HTML")
    bot.edit_message_media(media, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=create_wish_buttons())

@bot.callback_query_handler(func=lambda call: call.data.startswith('fazer_pedido'))
def handle_fazer_pedido(call):
    image_url = "https://telegra.ph/file/94c9c66af4ca4d6f0a3e5.jpg"
    caption = "<b>⛲: Para pedir os seus peixes é simples!</b> \n\nMe envie até <b>5 IDs</b> dos peixes e a quantidade de cenouras que você quer doar \n(eu aceito qualquer quantidade entre 10 e 20 cenouras...) \n\n<i>exemplo: ID1 ID2 ID3 ID4 ID5 cenouras</i>"
    media = InputMediaPhoto(image_url, caption=caption, parse_mode="HTML")
    bot.edit_message_media(media, chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.register_next_step_handler(call.message, process_wish)

def process_wish(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        command_parts = message.text.split()
        id_cartas = list(map(int, command_parts[:-1]))[:5]  # Limita a 5 cartas
        quantidade_cenouras = int(command_parts[-1])

        if quantidade_cenouras < 10 or quantidade_cenouras > 20:
            bot.send_message(chat_id, "A quantidade de cenouras deve ser entre 10 e 20.")
            return

        can_make_wish, time_remaining = check_wish_time(user_id)
        if not can_make_wish:
            hours, remainder = divmod(time_remaining.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            image_url = "https://telegra.ph/file/94c9c66af4ca4d6f0a3e5.jpg"
            caption = (f"<b>Você já fez um pedido recentemente.</b> Por favor, aguarde {int(hours)} horas e {int(minutes)} minutos "
                       "para fazer um novo pedido.")
            media = InputMediaPhoto(image_url, caption=caption, parse_mode="HTML")
            bot.edit_message_media(media, chat_id=message.chat.id, message_id=message.message_id, reply_markup=create_wish_buttons())
            return

        results = []
        debug_info = []
        diminuir_cenouras(user_id, quantidade_cenouras)
        for id_carta in id_cartas:
            chance = random.randint(1, 100)
            if chance <= 10:  # 10% de chance
                results.append(id_carta)
                update_inventory(user_id, id_carta)
            debug_info.append(f"ID da carta: {id_carta}, Chance: {chance}, Resultado: {'Ganhou' if chance <= 10 else 'Não ganhou'}")

        if results:
            bot.send_message(chat_id, f"<i>As águas da fonte começam a circular em uma velocidade assutadora, mas antes que você possa reagir, aparece na sua cesta os seguintes peixes:<b> {', '.join(map(str, results))}.</b>\n\nA fonte então desaparece. Quem sabe onde ele estará daqui 6 horas?</i>", parse_mode="HTML")
        else:
            bot.send_message(chat_id, "<i>A fonte nem se move ao receber suas cenouras, elas apenas desaparecem no meio da água calma. Talvez você deva tentar novamente mais tarde... </i>", parse_mode="HTML")


        log_wish_attempt(user_id, id_cartas, quantidade_cenouras, results)
                # Agendar a próxima verificação
        if lembrete_ativo("fonte", user_id):
            scheduler.add_job(send_font_reminder, 'date', run_date=datetime.now() + timedelta(hours=6), args=[user_id])

    except Exception as e:
        bot.send_message(message.chat.id, f"Ocorreu um erro: {e}")
        
def lembrete_ativo(tipo, id_usuario):
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("SELECT %s FROM lembretes WHERE id_usuario = %s", (tipo, id_usuario))
        result = cursor.fetchone()
        return result and result[0]
    finally:
        fechar_conexao(cursor, conn)
                
def send_font_reminder(user_id):
    bot.send_message(user_id, "Você já pode fazer um novo pedido na fonte dos desejos!")

def edit_wishing_well_message(message):
    image_url = "https://telegra.ph/file/365f89b484f9de0005e75.png"
    caption = ("Enquanto os demais camponeses estavam distraídos com suas pescas, *usuário* caminhava para um lugar mais distante, até que encontrou uma floresta mágica.\n\n"
               "Já havia escutado seus colegas falando da mesma mas sempre duvidou que era real.\n\n"
               "⛲: Oh! Olá camponês, imagino que a dona do jardim tenha te mandado pra cá, certo?\n\n"
               "Assustado e confuso com a voz repentina, perguntou a voz o que aquilo significava.\n\n"
               "⛲: Sou uma fonte dos desejos! você tem direito a fazer um pedido, em troca eu peço apenas algumas cenouras. Se o peixe que você deseja estiver disponível e a sorte ao seu favor ele irá aparecer no seu armazém. senão, volte mais tarde com outras cenouras.")
    media = InputMediaPhoto(image_url, caption=caption)
    bot.edit_message_media(media, chat_id=message.chat.id, message_id=message.message_id, reply_markup=create_wish_buttons())

# Função para buscar cartas com 30 ou mais unidades, ordenadas por categoria e quantidade
def buscar_cartas_trintadas(user_id, offset):
    conn, cursor = conectar_banco_dados()
    query = """
        SELECT p.emoji, p.nome, i.quantidade, p.subcategoria, p.id_personagem, p.categoria 
        FROM inventario i
        JOIN personagens p ON i.id_personagem = p.id_personagem
        WHERE i.id_usuario = %s AND i.quantidade >= 30
        ORDER BY p.categoria, i.quantidade DESC
        LIMIT 15 OFFSET %s
    """
    cursor.execute(query, (user_id, offset))
    cartas = cursor.fetchall()
    cursor.close()
    conn.close()
    return cartas

# Função para buscar todas as cartas trintadas para pegar uma imagem aleatória
def buscar_todas_cartas_trintadas(user_id):
    conn, cursor = conectar_banco_dados()
    query = """
        SELECT p.imagem 
        FROM inventario i
        JOIN personagens p ON i.id_personagem = p.id_personagem
        WHERE i.id_usuario = %s AND i.quantidade >= 30
    """
    cursor.execute(query, (user_id,))
    imagens = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return imagens

# Função para contar o total de cartas com 30 ou mais unidades
def contar_cartas_trintadas(user_id):
    conn, cursor = conectar_banco_dados()
    query = """
        SELECT COUNT(*)
        FROM inventario
        WHERE id_usuario = %s AND quantidade >= 30
    """
    cursor.execute(query, (user_id,))
    total_cartas = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total_cartas

# Função para criar a mensagem das cartas trintadas
def criar_mensagem_trintadas(cartas, pagina_atual, total_paginas, total_cartas, nome_usuario):
    resposta = f"🐝 Cartas trintadas pelo camponês {nome_usuario}:\n\n"
    for carta in cartas:
        emoji, nome, quantidade, subcategoria, id_personagem, categoria = carta
        resposta += f"{emoji} {id_personagem} • {nome}\nde {subcategoria} - {quantidade}⤫\n"
    resposta += f"\n📄 {pagina_atual}/{total_paginas}"
    return resposta

# Função para criar os botões de navegação
def criar_markup_trintadas(pagina_atual, total_paginas, user_id_inicial, nome_usuario_inicial):
    markup = InlineKeyboardMarkup()
    if pagina_atual > 1:
        markup.add(InlineKeyboardButton("⬅️", callback_data=f"trintadas_{user_id_inicial}_{pagina_atual - 1}_{nome_usuario_inicial}"))
    if pagina_atual < total_paginas:
        markup.add(InlineKeyboardButton("➡️", callback_data=f"trintadas_{user_id_inicial}_{pagina_atual + 1}_{nome_usuario_inicial}"))
    return markup

# Função para enviar a mensagem inicial de trintadas
def enviar_mensagem_trintadas(message, pagina_atual):
    user_id = message.from_user.id
    nome_usuario = message.from_user.first_name
    imagens = buscar_todas_cartas_trintadas(user_id)
    if not imagens:
        bot.send_message(message.chat.id, "Você não possui cartas com 30 ou mais unidades.")
        return

    imagem_aleatoria = random.choice(imagens)
    offset = (pagina_atual - 1) * 15
    cartas = buscar_cartas_trintadas(user_id, offset)
    total_cartas = contar_cartas_trintadas(user_id)
    total_paginas = (total_cartas + 14) // 15

    resposta = criar_mensagem_trintadas(cartas, pagina_atual, total_paginas, total_cartas, nome_usuario)
    markup = criar_markup_trintadas(pagina_atual, total_paginas, user_id, nome_usuario)

    bot.send_photo(message.chat.id, photo=imagem_aleatoria, caption=resposta, reply_markup=markup, parse_mode="HTML")

# Função para editar a mensagem de trintadas ao navegar pelas páginas
def editar_mensagem_trintadas(call, user_id_inicial, pagina_atual, nome_usuario_inicial):
    imagens = buscar_todas_cartas_trintadas(user_id_inicial)
    if not imagens:
        bot.send_message(call.message.chat.id, "Você não possui cartas com 30 ou mais unidades.")
        return

    imagem_aleatoria = random.choice(imagens)
    offset = (pagina_atual - 1) * 15
    cartas = buscar_cartas_trintadas(user_id_inicial, offset)
    total_cartas = contar_cartas_trintadas(user_id_inicial)
    total_paginas = (total_cartas + 14) // 15

    resposta = criar_mensagem_trintadas(cartas, pagina_atual, total_paginas, total_cartas, nome_usuario_inicial)
    markup = criar_markup_trintadas(pagina_atual, total_paginas, user_id_inicial, nome_usuario_inicial)

    media = InputMediaPhoto(media=imagem_aleatoria, caption=resposta, parse_mode="HTML")
    bot.edit_message_media(media=media, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

# Comando /trintadas para mostrar as cartas com 30 ou mais unidades
@bot.message_handler(commands=['trintadas', 'abelhadas', 'abelhas'])
def handle_trintadas(message):
    enviar_mensagem_trintadas(message, pagina_atual=1)

# Callback para navegar entre as páginas das cartas trintadas
@bot.callback_query_handler(func=lambda call: call.data.startswith('trintadas_'))
def callback_trintadas(call):
    data = call.data.split('_')
    user_id_inicial = int(data[1])
    pagina_atual = int(data[2])
    nome_usuario_inicial = data[3]
    editar_mensagem_trintadas(call, user_id_inicial, pagina_atual, nome_usuario_inicial)


def check_wish_time(user_id):
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("SELECT MAX(timestamp) FROM wish_log WHERE id_usuario = %s", (user_id,))
        last_wish = cursor.fetchone()[0]

        if last_wish:
            time_since_last_wish = datetime.now() - last_wish
            if time_since_last_wish.total_seconds() < 21600:  # 6 horas em segundos
                return False, timedelta(seconds=21600) - time_since_last_wish
            return True, None
        return True, None
    except Exception as e:
        print(f"Erro ao verificar o tempo do último desejo: {e}")
        return False, None
    finally:
        fechar_conexao(cursor, conn)

def update_inventory(user_id, id_carta):
    conn, cursor = conectar_banco_dados()
    cursor = conn.cursor()
    query = "SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s"
    cursor.execute(query, (user_id, id_carta))
    result = cursor.fetchone()
    if result:
        query = "UPDATE inventario SET quantidade = quantidade + 1 WHERE id_usuario = %s AND id_personagem = %s"
    else:
        query = "INSERT INTO inventario (id_usuario, id_personagem, quantidade) VALUES (%s, %s, 1)"
    cursor.execute(query, (user_id, id_carta))
    conn.commit()
    cursor.close()
    conn.close()

def log_wish_attempt(user_id, id_cartas, quantidade_cenouras, results):
    conn, cursor = conectar_banco_dados()
    cursor = conn.cursor()
    for id_carta in id_cartas:
        success = id_carta in results
        query = "INSERT INTO wish_log (id_usuario, id_personagem, quantidade_cenouras, sucesso, timestamp) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (user_id, id_carta, quantidade_cenouras, success, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()
@bot.callback_query_handler(func=lambda call: call.data.startswith('fazer_pedido'))
def handle_fazer_pedido(call):
    image_url = "https://telegra.ph/file/94c9c66af4ca4d6f0a3e5.jpg"
    caption = "<b>⛲: Para pedir os seus peixes é simples!</b> \n\nMe envie até <b>5 IDs</b> dos peixes e a quantidade de cenouras que você quer doar \n(eu aceito qualquer quantidade entre 10 e 20 cenouras...) \n\n<i>exemplo: ID1 ID2 ID3 ID4 ID5 cenouras</i>"
    media = InputMediaPhoto(image_url, caption=caption, parse_mode="HTML")
    bot.edit_message_media(media, chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.register_next_step_handler(call.message, process_wish)
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

@bot.callback_query_handler(func=lambda call: call.data.startswith("cesta_"))
def callback_query_cesta(call):
    global processing_lock

    if not processing_lock.acquire(blocking=False):
        return

    try:
        parts = call.data.split('_')
        tipo = parts[1]
        pagina = int(parts[2])
        categoria = parts[3]
        id_usuario_original = int(parts[4])
        nome_usuario = bot.get_chat(id_usuario_original).first_name

        if tipo == 's':
            ids_personagens = obter_ids_personagens_inventario(id_usuario_original, categoria)
            ids_personagens_evento = obter_ids_personagens_evento(id_usuario_original, categoria, incluir=False)
            ids_personagens.extend(ids_personagens_evento)
            total_personagens_subcategoria = obter_total_personagens_subcategoria(categoria)
            total_registros = len(ids_personagens)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_s(call.message, categoria, id_usuario_original, pagina, total_paginas, ids_personagens, total_personagens_subcategoria, nome_usuario, call=call)
            else:
                bot.reply_to(call.message, f"Nenhum personagem encontrado na cesta '{categoria}'.")

        elif tipo == 'f':
            ids_personagens_faltantes = obter_ids_personagens_faltantes(id_usuario_original, categoria)
            ids_personagens_evento = obter_ids_personagens_evento(id_usuario_original, categoria, incluir=True)
            ids_personagens_faltantes.extend(ids_personagens_evento)
            total_personagens_subcategoria = obter_total_personagens_subcategoria(categoria)
            total_registros = len(ids_personagens_faltantes)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_f(call.message, categoria, id_usuario_original, pagina, total_paginas, ids_personagens_faltantes, total_personagens_subcategoria, nome_usuario, call=call)
            else:
                bot.reply_to(call.message, f"Todos os personagens na subcategoria '{categoria}' estão no seu inventário.")

        elif tipo == 'c':
            ids_personagens = obter_ids_personagens_categoria(id_usuario_original, categoria)
            total_personagens_categoria = obter_total_personagens_categoria(categoria)
            total_registros = len(ids_personagens)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_c(call.message, categoria, id_usuario_original, pagina, total_paginas, ids_personagens, total_personagens_categoria, nome_usuario, call=call)
            else:
                bot.reply_to(call.message, f"Nenhum personagem encontrado na categoria '{categoria}'.")

        elif tipo == 'cf':
            ids_personagens_faltantes = obter_ids_personagens_faltantes_categoria(id_usuario_original, categoria)
            total_personagens_categoria = obter_total_personagens_categoria(categoria)
            total_registros = len(ids_personagens_faltantes)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_cf(call.message, categoria, id_usuario_original, pagina, total_paginas, ids_personagens_faltantes, total_personagens_categoria, nome_usuario, call=call)
            else:
                bot.reply_to(call.message, f"Você possui todos os personagens na categoria '{categoria}'.")

        elif tipo == 'se':
            ids_personagens = obter_ids_personagens_inventario(id_usuario_original, categoria)
            ids_personagens_evento = obter_ids_personagens_evento(id_usuario_original, categoria, incluir=True)
            ids_personagens.extend(ids_personagens_evento)
            total_personagens_evento = len(ids_personagens_evento)
            total_personagens_com_evento = obter_total_personagens_subcategoria(categoria) + total_personagens_evento
            total_registros = len(ids_personagens)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_s(call.message, categoria, id_usuario_original, pagina, total_paginas, ids_personagens, total_personagens_com_evento, nome_usuario, call=call)
            else:
                bot.reply_to(call.message, f"Nenhum personagem encontrado na cesta '{categoria}'.")

        elif tipo == 'fe':
            ids_personagens_faltantes = obter_ids_personagens_faltantes(id_usuario_original, categoria)
            ids_personagens_evento = obter_ids_personagens_evento(id_usuario_original, categoria, incluir=True)
            ids_personagens_faltantes.extend(ids_personagens_evento)
            total_personagens_subcategoria = obter_total_personagens_subcategoria(categoria)
            total_registros = len(ids_personagens_faltantes)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_f(call.message, categoria, id_usuario_original, pagina, total_paginas, ids_personagens_faltantes, total_personagens_subcategoria, nome_usuario, call=call)
            else:
                bot.reply_to(call.message, f"Todos os personagens na subcategoria '{categoria}' estão no seu inventário.")

    except Exception as e:
        print(f"Erro ao processar callback da cesta: {e}")
    finally:
        processing_lock.release()
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

                pagina -= 1
            elif call.data.startswith("armazem_ultima_"):

                pagina += 5 
            elif call.data.startswith("armazem_primeira_"):

                pagina -= 5
            elif call.data.startswith("armazem_proxima_"):

                pagina += 1
            offset = (pagina - 1) * resultados_por_pagina

            
        sql = f"""
            SELECT id_personagem, emoji, nome_personagem, subcategoria, quantidade, categoria, evento
            FROM (
                SELECT i.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, i.quantidade, p.categoria, '' AS evento
                FROM inventario i
                JOIN personagens p ON i.id_personagem = p.id_personagem
                WHERE i.id_usuario = {id_usuario} AND i.quantidade > 0

                UNION

                SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria, e.evento
                FROM evento e
                WHERE e.id_personagem IN (
                    SELECT id_personagem
                    FROM inventario
                    WHERE id_usuario = {id_usuario} AND quantidade > 0
                )
            ) AS combined
            ORDER BY 
                CASE WHEN categoria = 'evento' THEN 0 ELSE 1 END, 
                categoria, 
                CAST(id_personagem AS UNSIGNED) ASC
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

            # Obter favorito do usuário
            id_fav_usuario, emoji_fav, nome_fav, imagem_fav = obter_favorito(id_usuario)

            if id_fav_usuario is not None:
                resposta = f"💌 | Cartas no armazém de {usuario}:\n\nFav: {emoji_fav} {id_fav_usuario} — {nome_fav}\n\n"

            for carta in resultados:
                id_carta = carta[0]
                emoji_carta = carta[1]
                nome_carta = carta[2]
                subcategoria_carta = carta[3]
                quantidade_carta = carta[4]
                categoria_carta = carta[5]
                evento_carta = carta[6]

                if quantidade_carta is None:
                    quantidade_carta = 0
                else:
                    quantidade_carta = int(quantidade_carta)

                if categoria_carta == 'evento':
                    emoji_carta = obter_emoji_evento(evento_carta)

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

                repetida = " [+]" if quantidade_carta > 1 and categoria_carta == 'evento' else ""

                resposta += f" {emoji_carta} <code>{id_carta}</code> • {nome_carta} - {subcategoria_carta} {letra_quantidade}{repetida}\n"

            resposta += f"\n{pagina}/{total_paginas}"
            bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption=resposta, reply_markup=markup, parse_mode="HTML")

        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Nenhuma carta encontrada.")
    except mysql.connector.Error as err:
        print(f"Erro de SQL: {err}")
    finally:
        fechar_conexao(cursor, conn)

@bot.callback_query_handler(func=lambda call: call.data.startswith('peixes_'))
def callback_peixes(call):
    try:
        parts = call.data.split('_')
        pagina = int(parts[1])
        subcategoria = parts[2]
        
        pagina_peixes_callback(call, pagina, subcategoria)
    except Exception as e:
        print(f"Erro ao processar callback de peixes: {e}")
@bot.callback_query_handler(func=lambda call: call.data.startswith('pescar_'))
def callback_pescar(call):
    try:
        categoria_callback(call)
    except Exception as e:
        print(f"Erro ao processar callback de pescar: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('subcategory_'))
def callback_subcategory(call):
    try:
        subcategory_data = call.data.split("_")
        subcategory = subcategory_data[1]
        is_valentine = len(subcategory_data) > 2 and subcategory_data[2] == "valentine"
        if is_valentine:
            card = get_random_card_valentine(subcategory)
        else:
            categoria_handler(call.message, subcategory)
        if card:
            evento_aleatorio = card
            send_card_message(call.message, evento_aleatorio)
        else:
            bot.reply_to(call.message, "Desculpe, não foi possível encontrar uma carta para essa subcategoria.")
    except Exception as e:
        print(f"Erro ao processar callback de subcategoria: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('cenourar_sim_'))
def callback_cenourar(call):
    try:
        data_parts = call.data.split("_")
        acao = data_parts[1]
        id_usuario = int(data_parts[2])
        id_personagens = data_parts[3] if len(data_parts) > 3 else ""

        if acao == "sim":
            cenourar_carta(call, id_usuario, id_personagens)
        elif acao == "nao":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Operação de cenoura cancelada.")
    except Exception as e:
        print(f"Erro ao processar callback de cenoura: {e}")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Erro ao processar a cenoura.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('loja_geral'))
def callback_loja_geral(call):
    try:
        loja_geral_callback(call)
    except Exception as e:
        print(f"Erro ao processar callback de loja geral: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('img_'))
def callback_img_peixes_handler(call):
    try:
        dados = call.data.split('_')
        pagina = int(dados[-2])
        subcategoria = dados[-1]
        callback_img_peixes(call, pagina, subcategoria)
    except Exception as e:
        print(f"Erro ao processar callback 'img' de peixes: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('peixes_'))
def callback_peixes(call):
    try:
        dados = call.data.split('_')
        pagina = int(dados[-2])
        subcategoria = dados[-1]
        pagina_peixes_callback(call, pagina, subcategoria)
    except Exception as e:
        print(f"Erro ao processar callback de peixes: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("tag_"))
def callback_tag(call):
    try:
        parts = call.data.split('_')
        pagina = int(parts[1])
        nometag = parts[2]
        total_paginas = int(parts[3])
        id_usuario = call.from_user.id
        print(parts,pagina,nometag,total_paginas,id_usuario)
        editar_mensagem_tag(call.message, nometag, pagina, id_usuario,total_paginas)
    except Exception as e:
        print(f"Erro ao processar callback de página para a tag: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('loja_compras'))
def callback_loja_compras(call):
    try:
        message_data = call.data.replace('loja_', '')
        if message_data:
            conn, cursor = conectar_banco_dados()
            id_usuario = call.from_user.id
            cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            result = cursor.fetchone()

            imagem_url = 'https://telegra.ph/file/a4c194082eab84886cbd4.jpg'
            original_message_id = call.message.message_id

            keyboard = telebot.types.InlineKeyboardMarkup()
            primeira_coluna = [
                telebot.types.InlineKeyboardButton(text="🐟 Comprar Iscas", callback_data='compras_iscas_callback')
            ]
            segunda_coluna = [
                telebot.types.InlineKeyboardButton(text="🥕 Doar Cenouras", callback_data=f'doar_cenoura_{id_usuario}_{original_message_id}')
            ]
            keyboard.row(*primeira_coluna)
            keyboard.row(*segunda_coluna)

            if result:
                qnt_cenouras = int(result[0])
            else:
                qnt_cenouras = 0

            mensagem = f"🐇 Bem vindo a nossa lojinha. O que você quer levar?\n\n🥕 Saldo Atual: {qnt_cenouras}"
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=original_message_id, caption=mensagem, reply_markup=keyboard)
        else:
            bot.reply_to(call.message, "Erro ao processar comando.")
    except Exception as e:
        print(f"Erro ao processar comando: {e}")
    finally:
        cursor.close()
        conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith('compras_iscas_'))
def callback_compras_iscas(call):
    try:
        compras_iscas_callback(call)
    except Exception as e:
        print(f"Erro ao processar callback de compras iscas: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('tcancelar'))
def callback_tcancelar(call):
    try:
        data = call.data.split('_')
        destinatario_id = int(data[1])
        if destinatario_id == call.from_user.id:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(callback_query_id=call.id, text="Você não pode aceitar esta doação.")
    except Exception as e:
        print(f"Erro ao processar callback de cancelar: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirmar_doacao_'))
def callback_confirmar_doacao(call):
    try:
        data = call.data.split('_')
        if len(data) >= 6:
            destinatario_id = int(data[4])
            if destinatario_id != call.from_user.id:
                eu = int(data[2])
                minhacarta = int(data[3])
                destinatario_id = int(data[4])
                qnt = int(data[5])
                confirmar_doacao(eu, minhacarta, destinatario_id, call.message.chat.id, call.message.message_id, qnt)
            else:
                bot.answer_callback_query(callback_query_id=call.id, text="Você não pode aceitar esta doação.")
        else:
            bot.send_message(call.message.chat.id, "O formato da mensagem de confirmação está incorreto.")
    except Exception as e:
        print(f"Erro ao processar callback de confirmação de doação: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('aprovar_'))
def callback_aprovar(call):
    try:
        aprovar_callback(call)
    except Exception as e:
        print(f"Erro ao processar callback de aprovação: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reprovar_'))
def callback_reprovar(call):
    try:
        reprovar_callback(call)
    except Exception as e:
        print(f"Erro ao processar callback de reprovação: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('repor_'))
def callback_repor(call):
    try:
        quantidade = 1
        message_data = call.data
        parts = message_data.split('_')
        id_usuario = parts[1]
        adicionar_iscas(id_usuario, quantidade, call.message)
    except Exception as e:
        print(f"Erro ao processar callback de reposição: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('loja_loja'))
def callback_loja_loja(call):
    try:
        message_data = call.data.replace('loja_', '')
        if message_data == "loja":
            data_atual = datetime.today().strftime("%Y-%m-%d")
            id_usuario = call.from_user.id
            ids_do_dia = obter_ids_loja_do_dia(data_atual)
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
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=keyboard,
                media=telebot.types.InputMediaPhoto(media=imagem_url, caption=mensagem)
            )
    except Exception as e:
        print(f"Erro ao processar loja_loja_callback: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('compra_'))
def callback_compra(call):
    try:
        chat_id = call.message.chat.id
        parts = call.data.split('_')
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
                (categoria, datetime.today().strftime("%Y-%m-%d"))
            )
            carta_comprada = cursor.fetchone()

            if carta_comprada:
                id_personagem, nome, subcategoria, emoji = carta_comprada
                mensagem = f"Você tem {qnt_cenouras} cenouras. \nDeseja usar 5 para comprar o seguinte peixe: \n\n{emoji} {id_personagem} - {nome} \nde {subcategoria}?"
                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.row(
                    telebot.types.InlineKeyboardButton(text="Sim", callback_data=f'confirmar_compra_{categoria}_{id_usuario}'),
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

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirmar_compra_'))
def callback_confirmar_compra(call):
    try:
        parts = call.data.split('_')
        categoria = parts[2]
        id_usuario = parts[3]
        data_atual = datetime.today().strftime("%Y-%m-%d")
        conn, cursor = conectar_banco_dados()
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
            add_to_inventory(id_usuario, id_personagem)
            diminuir_cenouras(id_usuario, 5)

            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=telebot.types.InputMediaPhoto(media=imagem, caption=mensagem)
            )
        else:
            print(f"Nenhuma carta disponível para compra na categoria {categoria} hoje.")
    except Exception as e:
        print(f"Erro ao processar a compra: {e}")
    finally:
        fechar_conexao(cursor, conn)
        

@bot.message_handler(commands=['setmusica'])
def set_musica_command(message):
    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2:
        link_spotify = command_parts[1].strip()
        id_usuario = message.from_user.id

        # Extrair o ID da música do link do Spotify
        try:
            track_id = link_spotify.split("/")[-1].split("?")[0]
            track_info = sp.track(track_id)
            nome_musica = track_info['name']
            artista = track_info['artists'][0]['name']
            nova_musica = f"{nome_musica} - {artista}"

            # Atualizar a coluna 'musica' no banco de dados
            atualizar_coluna_usuario(id_usuario, 'musica', nova_musica)
            bot.send_message(message.chat.id, f"Música atualizada para: {nova_musica}")
        except Exception as e:
            bot.send_message(message.chat.id, f"Erro ao processar o link do Spotify: {e}")
    else:
        bot.send_message(message.chat.id, "Formato incorreto. Use /setmusica seguido do link do Spotify, por exemplo: /setmusica https://open.spotify.com/track/xxxx.")

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
            resposta_completa = comando_evento_s(id_usuario, evento, subcategoria, cursor, usuario)
        elif message.text.startswith('/evento f'):
            resposta_completa = comando_evento_f(id_usuario, evento, subcategoria, cursor, usuario)
        else:
            resposta = "Comando inválido. Use /evento s <evento> <subcategoria> ou /evento f <evento> <subcategoria>."
            bot.send_message(message.chat.id, resposta)
            return

        if isinstance(resposta_completa, tuple):
            subcategoria_pesquisada, lista, total_pages = resposta_completa
            resposta = f"{lista}\n\nPágina 1 de {total_pages}"

            markup = InlineKeyboardMarkup()
            if total_pages > 1:
                markup.add(InlineKeyboardButton("Próxima", callback_data=f"evento_next_{evento}_{subcategoria_pesquisada}_2"))

            bot.send_message(message.chat.id, resposta, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, resposta_completa)
    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido)
    finally:
        fechar_conexao(cursor, conn)

@bot.callback_query_handler(func=lambda call: call.data.startswith("evento_"))
def callback_query_evento(call):
    data_parts = call.data.split('_')
    action = data_parts[1]
    evento = data_parts[2]
    subcategoria = data_parts[3]
    page = int(data_parts[4])
    
    try:
        conn, cursor = conectar_banco_dados()
        id_usuario = call.from_user.id
        usuario = call.from_user.first_name

        if action == "prev":
            page -= 1
        elif action == "next":
            page += 1

        if call.message.text.startswith('🌾'):
            resposta_completa = comando_evento_s(id_usuario, evento, subcategoria, cursor, usuario, page)
        else:
            resposta_completa = comando_evento_f(id_usuario, evento, subcategoria, cursor, usuario, page)

        if isinstance(resposta_completa, tuple):
            subcategoria_pesquisada, lista, total_pages = resposta_completa
            resposta = f"{lista}\n\nPágina {page} de {total_pages}"

            markup = InlineKeyboardMarkup()
            if page > 1:
                markup.add(InlineKeyboardButton("Anterior", callback_data=f"evento_prev_{evento}_{subcategoria_pesquisada}_{page}"))
            if page < total_pages:
                markup.add(InlineKeyboardButton("Próxima", callback_data=f"evento_next_{evento}_{subcategoria_pesquisada}_{page}"))

            bot.edit_message_text(resposta, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        else:
            bot.edit_message_text(resposta_completa, chat_id=call.message.chat.id, message_id=call.message.message_id)
    except mysql.connector.Error as err:
        bot.send_message(call.message.chat.id, f"Erro ao buscar perfil: {err}")
    finally:
        fechar_conexao(cursor, conn)


def comando_evento_s(id_usuario, evento, subcategoria, cursor, usuario, page=1):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    
    items_per_page = 15
    offset = (page - 1) * items_per_page
    
    sql_usuario = f"""
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        JOIN inventario i ON e.id_personagem = i.id_personagem
        WHERE i.id_usuario = {id_usuario} AND e.evento = '{evento}'
        ORDER BY e.id_personagem ASC
        LIMIT {items_per_page} OFFSET {offset};
    """
    cursor.execute(sql_usuario)
    resultados_usuario = cursor.fetchall()

    sql_total = f"""
        SELECT COUNT(*)
        FROM evento e
        JOIN inventario i ON e.id_personagem = i.id_personagem
        WHERE i.id_usuario = {id_usuario} AND e.evento = '{evento}';
    """
    cursor.execute(sql_total)
    total_items = cursor.fetchone()[0]
    total_pages = ceil(total_items / items_per_page)
    
    if resultados_usuario:
        lista_cartas = ""

        for carta in resultados_usuario:
            id_carta = carta[1]
            emoji_carta = carta[0]
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas += f"{emoji_carta} {formatar_id(id_carta)} — {nome_carta}\n"
        if lista_cartas:
            resposta = f"🌾 | Cartas do evento {evento} no inventario de {usuario}:\n\n{lista_cartas}"
            return subcategoria_carta, resposta, total_pages
    return f"🌧 Sem cartas de {subcategoria} no evento {evento}! A jornada continua..."

def comando_evento_f(id_usuario, evento, subcategoria, cursor, usuario, page=1):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    
    items_per_page = 15
    offset = (page - 1) * items_per_page
    
    sql_faltantes = f"""
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        WHERE e.evento = '{evento}' 
            AND NOT EXISTS (
                SELECT 1
                FROM inventario i
                WHERE i.id_usuario = {id_usuario} AND i.id_personagem = e.id_personagem
            )
        ORDER BY e.id_personagem ASC
        LIMIT {items_per_page} OFFSET {offset};
    """
    cursor.execute(sql_faltantes)
    resultados_faltantes = cursor.fetchall()

    sql_total = f"""
        SELECT COUNT(*)
        FROM evento e
        WHERE e.evento = '{evento}' 
            AND NOT EXISTS (
                SELECT 1
                FROM inventario i
                WHERE i.id_usuario = {id_usuario} AND i.id_personagem = e.id_personagem
            );
    """
    cursor.execute(sql_total)
    total_items = cursor.fetchone()[0]
    total_pages = ceil(total_items / items_per_page)

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
            return subcategoria_carta, resposta, total_pages
    return f"☀️ Nada como a alegria de ter todas as cartas de {subcategoria} no evento {evento} na cesta!"

        
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
            return None

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

def registrar_grupo(chat_id, chat_title):
    conn, cursor = conectar_banco_dados()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT OR IGNORE INTO grupos_registrados (chat_id, title, timestamp)
    VALUES (?, ?, ?)
    ''', (chat_id, chat_title, timestamp))
    conn.commit()
    conn.close()
@bot.message_handler(commands=['help'])
def help_command(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("Cartas", callback_data="help_cartas"),
        telebot.types.InlineKeyboardButton("Trocas", callback_data="help_trocas")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("Eventos", callback_data="help_eventos"),
        telebot.types.InlineKeyboardButton("Usuário", callback_data="help_bugs")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("Outros", callback_data="help_tudo"),
        telebot.types.InlineKeyboardButton("Sobre o Beta", callback_data="help_beta")
    )
    
    markup.row(
        telebot.types.InlineKeyboardButton("⚠️ IMPORTANTE! ⚠️", callback_data="help_imp")
    )
    
    
    bot.send_message(message.chat.id, "Selecione uma categoria para obter ajuda:", reply_markup=markup)

@bot.message_handler(commands=['iduser'])
def handle_iduser_command(message):
    if message.reply_to_message:
        idusuario = message.reply_to_message.from_user.id
        bot.send_message(chat_id=message.chat.id, text=f"O ID do usuário é <code>{idusuario}</code>", reply_to_message_id=message.message_id,parse_mode="HTML")

@bot.message_handler(commands=['sair'])
def sair_grupo(message):
    try:
        id_grupo = message.text.split(' ', 1)[1]
        bot.leave_chat(id_grupo)
        bot.reply_to(message, f"O bot saiu do grupo com ID {id_grupo}.")

    except IndexError:
        bot.reply_to(message, "Por favor, forneça o ID do grupo após o comando, por exemplo: /sair 123456789.")

    except Exception as e:
        print(f"Erro ao processar comando /sair: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")

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
        bot.send_message(message.chat.id, "Formato incorreto. Use /setuser seguido do user desejado, por exemplo: /setuser novouser.", reply_to_message_id=message.message_id)
        return

    nome_usuario = command_parts[1].strip()

    if not re.match("^[a-zA-Z0-9_]{1,20}$", nome_usuario):
        bot.send_message(message.chat.id, "Nome de usuário inválido. Use apenas letras, números e '_' e não ultrapasse 20 caracteres.", reply_to_message_id=message.message_id)
        return

    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT 1 FROM usuarios WHERE user = %s", (nome_usuario,))
        if cursor.fetchone():
            bot.send_message(message.chat.id, "O nome de usuário já está em uso. Escolha outro nome de usuário.", reply_to_message_id=message.message_id)
            return

        cursor.execute("SELECT 1 FROM usuarios_banidos WHERE id_usuario = %s", (nome_usuario,))
        if cursor.fetchone():
            bot.send_message(message.chat.id, "O nome de usuário já está em uso. Escolha outro nome de usuário.", reply_to_message_id=message.message_id)
            return

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

def usuario_registrado_no_grupo(user_id, chat_id):
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT * FROM grupos WHERE user_id = %s AND chat_id = %s", (user_id, chat_id))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

def registrar_usuario_no_grupo(user_id, user_name, chat_id, chat_title):
    conn, cursor = conectar_banco_dados()
    cursor.execute("INSERT INTO grupos (user_id, user_name, chat_id, chat_title) VALUES (%s, %s, %s, %s)",
                   (user_id, user_name, chat_id, chat_title))
    conn.commit()
    conn.close()

def registrar_mensagem_privada(user_id):
    conn, cursor = conectar_banco_dados()
    cursor.execute("INSERT INTO mensagens_privadas (user_id) VALUES (%s)", (user_id,))
    conn.commit()
    conn.close()

def registrar_mensagem(message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        user_name = message.from_user.username
        chat_type = message.chat.type
        chat_title = message.chat.title if hasattr(message.chat, 'title') else None

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

    conn, cursor = conectar_banco_dados()
    cursor.execute("UPDATE usuarios SET fav = NULL WHERE id_usuario = %s", (id_usuario,))
    conn.commit()

    bot.send_message(message.chat.id, "Favorito removido com sucesso.", reply_to_message_id=message.message_id)

           
@bot.message_handler(commands=['setfav'])
def set_fav_command(message):

    command_parts = message.text.split(maxsplit=1)
    if len(command_parts) == 2 and command_parts[1].isdigit():
        id_personagem = int(command_parts[1])
        id_usuario = message.from_user.id
        nome_personagem = obter_nome(id_personagem)
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
        usuario_existe = cursor.fetchone()[0]  

        if usuario_existe > 0: 
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

            # Consulta SQL para obter o estado de casamento
            query_obter_casamento = """
                SELECT c.id_personagem, COALESCE(p.nome, e.nome) AS nome_parceiro
                FROM casamentos c
                LEFT JOIN personagens p ON c.id_personagem = p.id_personagem
                LEFT JOIN evento e ON c.id_personagem = e.id_personagem
                WHERE c.user_id = %s AND c.estado = 'casado'
            """
            cursor.execute(query_obter_casamento, (id_usuario,))
            casamento = cursor.fetchone()

            if perfil:
                nome, nome_usuario, fav, adm, qntcartas, cenouras, iscas, bio, musica, pronome, privado, user, beta, nome_fav, imagem_fav = perfil

                resposta = f"<b>Perfil de {nome}</b>\n\n" \
                        f"✨ Fav: {fav} — {nome_fav}\n\n"
                
                if casamento:
                    parceiro_id, parceiro_nome = casamento
                    resposta += f"💍 Casado(a) com {parceiro_nome}\n\n"

                if adm:
                    resposta += f"🌈 Adm: {adm.capitalize()}\n\n"
                if beta:
                    resposta += f"🍀 Usuario Beta\n\n"
                resposta += f"‍🧑‍🌾 Camponês: {user}\n" \
                            f"🐟 Peixes: {qntcartas}\n" \
                            f"🥕 Cenouras: {cenouras}\n" \
                            f"🪝 Iscas: {iscas}\n"

                if pronome:
                    resposta += f"🌺 Pronomes: {pronome}\n\n"

                resposta += f"✍ {bio}\n\n" \
                            f"🎧: {musica}"

                enviar_perfil(message.chat.id, resposta, imagem_fav, fav, id_usuario, message)
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
def mostrar_primeira_pagina_submenus(message, subcategoria):
    try:
        conn, cursor = conectar_banco_dados()
        query_total = "SELECT COUNT(DISTINCT submenu) FROM personagens WHERE subcategoria = %s"
        cursor.execute(query_total, (subcategoria,))
        total_registros = cursor.fetchone()[0]
        total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)

        if total_registros == 0:
            bot.reply_to(message, f"Nenhum submenu encontrado para a subcategoria '{subcategoria}'.")
            return

        query = "SELECT DISTINCT submenu FROM personagens WHERE subcategoria = %s LIMIT 15"
        cursor.execute(query, (subcategoria,))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Submenus na subcategoria {subcategoria}:\n\n"
            for resultado in resultados:
                submenu = resultado[0]
                resposta += f"• {submenu}\n"

            markup = None
            if total_paginas > 1:
                markup = criar_markup_submenus(1, total_paginas, subcategoria)
            bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.reply_to(message, f"Nenhum submenu encontrado para a subcategoria '{subcategoria}'.")

    except Exception as e:
        print(f"Erro ao processar comando /submenus: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")

def editar_mensagem_submenus(call, subcategoria, pagina_atual, total_paginas):
    try:
        conn, cursor = conectar_banco_dados()

        offset = (pagina_atual - 1) * 15
        query = "SELECT DISTINCT submenu FROM personagens WHERE subcategoria = %s LIMIT 15 OFFSET %s"
        cursor.execute(query, (subcategoria, offset))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Submenus na subcategoria {subcategoria}, página {pagina_atual}/{total_paginas}:\n\n"
            for resultado in resultados:
                submenu = resultado[0]
                resposta += f"• {submenu}\n"

            markup = criar_markup_submenus(pagina_atual, total_paginas, subcategoria)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.reply_to(call.message, f"Nenhum submenu encontrado para a subcategoria '{subcategoria}'.")

    except Exception as e:
        print(f"Erro ao editar mensagem de submenus: {e}")
        bot.reply_to(call.message, "Ocorreu um erro ao processar sua solicitação.")

def criar_markup_submenus(pagina_atual, total_paginas, subcategoria):
    markup = telebot.types.InlineKeyboardMarkup()

    if pagina_atual > 1:
        btn_anterior = telebot.types.InlineKeyboardButton("⬅️", callback_data=f"submenus_{pagina_atual-1}_{subcategoria}")
        markup.add(btn_anterior)
    
    if pagina_atual < total_paginas:
        btn_proxima = telebot.types.InlineKeyboardButton("➡️", callback_data=f"submenus_{pagina_atual+1}_{subcategoria}")
        markup.add(btn_proxima)

    return markup

        
def mostrar_primeira_pagina_especies(message, categoria):
    try:
        conn, cursor = conectar_banco_dados()

        query_total = "SELECT COUNT(DISTINCT subcategoria) FROM personagens WHERE categoria = %s"
        cursor.execute(query_total, (categoria,))
        total_registros = cursor.fetchone()[0]

        total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)

        if total_registros == 0:
            bot.reply_to(message, f"Nenhuma subcategoria encontrada para a categoria '{categoria}'.")
            return

        query = "SELECT DISTINCT subcategoria FROM personagens WHERE categoria = %s LIMIT 15"
        cursor.execute(query, (categoria,))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Subcategorias na categoria {categoria}:\n\n"
            for resultado in resultados:
                subcategoria = resultado[0]
                resposta += f"• {subcategoria}\n"

            markup = None
            if total_paginas > 1:
                markup = criar_markup_especies(1, total_paginas, categoria)
            bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.reply_to(message, f"Nenhuma subcategoria encontrada para a categoria '{categoria}'.")

    except Exception as e:
        print(f"Erro ao processar comando /especies: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")

def editar_mensagem_especies(call, categoria, pagina_atual, total_paginas):
    try:
        conn, cursor = conectar_banco_dados()

        offset = (pagina_atual - 1) * 15
        query = "SELECT DISTINCT subcategoria FROM personagens WHERE categoria = %s LIMIT 15 OFFSET %s"
        cursor.execute(query, (categoria, offset))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Subcategorias na categoria {categoria}, página {pagina_atual}/{total_paginas}:\n\n"
            for resultado in resultados:
                subcategoria = resultado[0]
                resposta += f"• {subcategoria}\n"

            markup = criar_markup_especies(pagina_atual, total_paginas, categoria)

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.reply_to(call.message, f"Nenhuma subcategoria encontrada para a categoria '{categoria}'.")

    except Exception as e:
        print(f"Erro ao editar mensagem de espécies: {e}")
        bot.reply_to(call.message, "Ocorreu um erro ao processar sua solicitação.")


def criar_markup_especies(pagina_atual, total_paginas, categoria):
    markup = telebot.types.InlineKeyboardMarkup()

    if pagina_atual > 1:
        btn_anterior = telebot.types.InlineKeyboardButton("⬅️ Anterior", callback_data=f"especies_{pagina_atual-1}_{categoria}")
        markup.add(btn_anterior)
    
    if pagina_atual < total_paginas:
        btn_proxima = telebot.types.InlineKeyboardButton("Próxima ➡️", callback_data=f"especies_{pagina_atual+1}_{categoria}")
        markup.add(btn_proxima)

    return markup

@bot.message_handler(commands=['especies'])
def verificar_comando_especies(message):
    try:
        parametros = message.text.split(' ', 1)[1:]  

        if not parametros:
            bot.reply_to(message, "Por favor, forneça a categoria.")
            return

        categoria = parametros[0]


        mostrar_primeira_pagina_especies(message, categoria)

    except Exception as e:
        print(f"Erro ao processar comando /especies: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")
        
@bot.message_handler(commands=['gperfil'])
def gperfil_command(message):

    if len(message.text.split()) != 2:
        bot.send_message(message.chat.id, "Formato incorreto. Use /gperfil seguido do nome de usuário desejado.")
        return

    username = message.text.split()[1].strip()

    try:
        conn, cursor = conectar_banco_dados()

        query_verificar_usuario = "SELECT 1 FROM usuarios WHERE user = %s"
        cursor.execute(query_verificar_usuario, (username,))
        usuario_existe = cursor.fetchone()

        if usuario_existe:

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


                if beta == 1:
                    usuario_beta = True
                else:
                    usuario_beta = False
                if privado == 1:
                    resposta = f"<b>Perfil de {username}</b>\n\n" \
                               f"✨ Fav: {fav} — {nome_fav}\n\n"
                    if usuario_beta:
                        resposta += f"🍀 Usuario Beta\n\n"         
                    if adm:
                        resposta += f"🌈 Adm: {adm.capitalize()}\n\n"
                    if pronome:
                        resposta += f"🌺 Pronomes: {pronome.capitalize()}\n\n" 
                          
                    resposta += f"🔒 Perfil Privado"
                else:
                    resposta = f"<b>Perfil de {nome_usuario}</b>\n\n" \
                               f"✨ Fav: {fav} — {nome_fav}\n\n" \
                      
                    if usuario_beta:
                        resposta += f"🍀 <b>Usuario Beta</b>\n\n" 
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

def create_wish_buttons():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Fazer pedido", callback_data="fazer_pedido"))
    markup.add(InlineKeyboardButton(text="Cancelar", callback_data="pedido_cancelar"))
    return markup

       
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
        
def create_next_button_markup(current_index, total_count):
    markup = types.InlineKeyboardMarkup()
    button_text = f"Próximo ({current_index}/{total_count})"
    button_callback = f"next_button_{current_index}_{total_count}"
    markup.add(types.InlineKeyboardButton(text=button_text, callback_data=button_callback))
    return markup
def send_message_without_buttons(chat_id, mensagens, current_index=0):
    total_count = len(mensagens)


    media_url, mensagem = mensagens[current_index]


    if media_url:
        bot.send_photo(chat_id, media_url, caption=mensagem)
    else:
        bot.send_message(chat_id, mensagem)
            
    user_id = chat_id 
    save_user_state(user_id, 'gnomes', mensagens, chat_id)


        
@bot.message_handler(commands=['config'])
def handle_config(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Pronomes', callback_data='bpronomes_')
    btn2 = types.InlineKeyboardButton('Privacidade', callback_data='privacy')
    btn3 = types.InlineKeyboardButton('Lembretes', callback_data='lembretes')
    btn_cancelar = types.InlineKeyboardButton('❌ Cancelar', callback_data='pcancelar')
    markup.add(btn1, btn2)
    markup.add(btn3, btn_cancelar)
    bot.send_message(message.chat.id, "Escolha uma opção:", reply_markup=markup)

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
            return bool(resultado[0])  
        else:
            return False
    except Exception as e:
        print("Erro ao obter status de privacidade do perfil:", e)
        return False  


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
    if status_perfil:  
        btn_alterar = types.InlineKeyboardButton('🔐 Abrir perfil', callback_data='open_profile')
    else:  
        btn_alterar = types.InlineKeyboardButton('🔒 Fechar perfil', callback_data='lock_profile')

    btn_cancelar = types.InlineKeyboardButton('❌ Cancelar', callback_data='pcancelar')
    markup.add(btn_alterar, btn_cancelar)
    
    mensagem = construir_mensagem_privacidade(nome_usuario, status_perfil)

    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem, reply_markup=markup)

@bot.message_handler(commands=['gnome'])
def gnome(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    idmens = message.message_id
    try:
        partes = message.text.split()
        if 'e' in partes:
            # Se "e" está no comando, procura na tabela evento
            nome = ' '.join(partes[2:])  # Pega todos os termos após "gnome e"
            sql_personagens = """
                SELECT
                    e.id_personagem,
                    e.nome,
                    e.subcategoria,
                    e.categoria,
                    i.quantidade AS quantidade_usuario,
                    e.imagem
                FROM evento e
                LEFT JOIN inventario i ON e.id_personagem = i.id_personagem AND i.id_usuario = %s
                WHERE e.nome LIKE %s
            """
        else:
            # Senão, procura na tabela personagens
            nome = ' '.join(partes[1:])  # Pega todos os termos após "gnome"
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
        conn, cursor = conectar_banco_dados()
        cursor.execute(sql_personagens, values_personagens)
        resultados_personagens = cursor.fetchall()

        if len(resultados_personagens) == 1:

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
                    bot.send_animation(chat_id, imagem_url, caption=mensagem,parse_mode="HTML")                  
                elif imagem_url.lower().endswith(".mp4"):
                    bot.send_video(chat_id, imagem_url, caption=mensagem,parse_mode="HTML") 
                elif imagem_url.lower().endswith((".jpeg", ".jpg", ".png")):
                    bot.send_photo(chat_id, imagem_url, caption=mensagem,parse_mode="HTML")                
                else:
                    send_message_with_buttons(chat_id, idmens, [(None, mensagem)], reply_to_message_id=message.message_id)
            else:
                if  imagem_url.lower().endswith(".gif"):
                    bot.send_animation(chat_id, imagem_url, caption=mensagem,parse_mode="HTML")                  
                elif imagem_url.lower().endswith(".mp4"):
                    bot.send_video(chat_id, imagem_url, caption=mensagem,parse_mode="HTML") 
                elif imagem_url.lower().endswith((".jpeg", ".jpg", ".png")):
                    bot.send_photo(chat_id, imagem_url, caption=mensagem,parse_mode="HTML")                
                else:
                    send_message_with_buttons(chat_id, idmens, [(None, mensagem)], reply_to_message_id=message.message_id)
                
            user_id = chat_id
            save_user_state(chat_id, [mensagem])  

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

            save_user_state(chat_id, mensagens)
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

        
def load_user_state(chat_id, command):
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("SELECT data FROM user_state WHERE chat_id = %s AND command = %s", (chat_id, command))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0]), chat_id
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

    if current_index > 0:
        prev_button = types.InlineKeyboardButton(text="⬅", callback_data=f"change_page_{current_index-1}")
        buttons.append(prev_button)
    
    if current_index < total_count - 1:
        next_button = types.InlineKeyboardButton(text="➡", callback_data=f"change_page_{current_index+1}")
        buttons.append(next_button)
    
    markup.add(*buttons)
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
    else:
        bot.send_message(chat_id, "Não há mais personagens disponíveis.")
        clear_user_state(chat_id, 'gnomes')

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
            total_paginas = -(-total_resultados // resultados_por_pagina)  
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

                mensagem = f"💌 | Personagem: \n\n<code>{id_personagem}</code> • {nome}\nde {subcategoria}"

                if quantidade_usuario == None:
                    mensagem += f"\n\n🌧 | Tempo fechado..."
                elif quantidade_usuario == 1:
                    mensagem += f"\n\n{'☀  '}"
                else:
                    mensagem += f"\n\n{'☀ 𖡩'}"

                try:
                    if imagem_url.lower().endswith(('.jpg', '.jpeg', '.png')):
                        bot.send_photo(chat_id=message.chat.id, photo=imagem_url, caption=mensagem, reply_to_message_id=message.message_id,parse_mode="HTML")
                    elif imagem_url.lower().endswith(('.mp4', '.gif')):
                        bot.send_video(chat_id=message.chat.id, video=imagem_url, caption=mensagem, reply_to_message_id=message.message_id,parse_mode="HTML")
                except Exception as e:
                    bot.send_message(chat_id, mensagem, reply_to_message_id=message.message_id,parse_mode="HTML")
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

@bot.message_handler(commands=['cesta'])
def verificar_cesta(message):
    try:
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            bot.reply_to(message, "Por favor, forneça o tipo ('s', 'f', 'c', 'se', 'fe' ou 'cf') e a subcategoria após o comando, por exemplo: /cesta s bts")
            return

        tipo = parts[1].strip()
        subcategoria = parts[2].strip()

        id_usuario = message.from_user.id
        nome_usuario = message.from_user.first_name

        if tipo in ['s', 'se']:
            subcategoria_proxima = encontrar_subcategoria_proxima(subcategoria)
            if not subcategoria_proxima:
                bot.reply_to(message, "Espécie não identificada. Você digitou certo? 🤭")
                return

            ids_personagens = obter_ids_personagens_inventario(id_usuario, subcategoria_proxima)
            if 'e' in tipo:
                ids_personagens += obter_ids_personagens_evento(id_usuario, subcategoria_proxima, incluir=False)
            total_personagens_subcategoria = obter_total_personagens_subcategoria(subcategoria_proxima)
            total_registros = len(ids_personagens)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_s(message, subcategoria_proxima, id_usuario, 1, total_paginas, ids_personagens, total_personagens_subcategoria, nome_usuario)
            else:
                bot.reply_to(message, f"🌧️ Sem peixes de {subcategoria_proxima} na cesta... a jornada continua.")

        elif tipo in ['f', 'fe']:
            subcategoria_proxima = encontrar_subcategoria_proxima(subcategoria)
            if not subcategoria_proxima:
                bot.reply_to(message, "Espécie não identificada. Você digitou certo? 🤭")
                return

            ids_personagens_faltantes = obter_ids_personagens_faltantes(id_usuario, subcategoria_proxima)
            if 'e' in tipo:
                ids_personagens_faltantes += obter_ids_personagens_evento(id_usuario, subcategoria_proxima, incluir=True)
            total_personagens_subcategoria = obter_total_personagens_subcategoria(subcategoria_proxima)
            total_registros = len(ids_personagens_faltantes)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_f(message, subcategoria_proxima, id_usuario, 1, total_paginas, ids_personagens_faltantes, total_personagens_subcategoria, nome_usuario)
            else:
                bot.reply_to(message, f"☀️ Nada como a alegria de ter todos os peixes de {subcategoria_proxima} na cesta!")

        elif tipo == 'c':
            subcategoria_proxima = encontrar_categoria_proxima(subcategoria)
            if not subcategoria_proxima:
                bot.reply_to(message, "Espécie não identificada. Você digitou certo? 🤭")
                return

            ids_personagens = obter_ids_personagens_categoria(id_usuario, subcategoria_proxima)
            total_personagens_categoria = obter_total_personagens_categoria(subcategoria_proxima)
            total_registros = len(ids_personagens)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_c(message, subcategoria_proxima, id_usuario, 1, total_paginas, ids_personagens, total_personagens_categoria, nome_usuario)
            else:
                bot.reply_to(message, f"🌧️ Sem peixes de {subcategoria_proxima} na cesta... a jornada continua.")

        elif tipo == 'cf':
            subcategoria_proxima = encontrar_categoria_proxima(subcategoria)
            if not subcategoria_proxima:
                bot.reply_to(message, "Espécie não identificada. Você digitou certo? 🤭")
                return

            ids_personagens_faltantes = obter_ids_personagens_faltantes_categoria(id_usuario, subcategoria_proxima)
            total_personagens_categoria = obter_total_personagens_categoria(subcategoria_proxima)
            total_registros = len(ids_personagens_faltantes)

            if total_registros > 0:
                total_paginas = (total_registros // 15) + (1 if total_registros % 15 > 0 else 0)
                mostrar_pagina_cesta_cf(message, subcategoria_proxima, id_usuario, 1, total_paginas, ids_personagens_faltantes, total_personagens_categoria, nome_usuario)
            else:
                bot.reply_to(message, f"☀️ Nada como a alegria de ter todos os peixes de {subcategoria_proxima} na cesta!")

        else:
            bot.reply_to(message, "Tipo inválido. Use 's' para os personagens que você possui, 'f' para os que você não possui, 'c' para uma categoria completa ou 'cf' para faltantes na categoria.")

    except IndexError:
        bot.reply_to(message, "Por favor, forneça o tipo ('s', 'f', 'c', 'se', 'fe' ou 'cf') e a subcategoria desejada após o comando, por exemplo: /cesta s bts")

    except Exception as e:
        print(f"Erro ao processar comando /cesta: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")
        
@bot.message_handler(commands=['submenus'])
def submenus_command(message):
    try:
        parts = message.text.split(' ', 1)
        conn, cursor = conectar_banco_dados()

        if len(parts) == 1:
            # Nenhuma subcategoria fornecida, mostrar todos os submenus paginados
            pagina = 1
            submenus_por_pagina = 15

            query_todos_submenus = """
            SELECT subcategoria, submenu
            FROM personagens
            WHERE submenu IS NOT NULL AND submenu != ''
            GROUP BY subcategoria, submenu
            ORDER BY subcategoria, submenu
            LIMIT %s OFFSET %s
            """
            offset = (pagina - 1) * submenus_por_pagina
            cursor.execute(query_todos_submenus, (submenus_por_pagina, offset))
            submenus = cursor.fetchall()

            # Obter o total de submenus para paginação
            cursor.execute("SELECT COUNT(DISTINCT subcategoria, submenu) FROM personagens WHERE submenu IS NOT NULL AND submenu != ''")
            total_submenus = cursor.fetchone()[0]
            total_paginas = (total_submenus // submenus_por_pagina) + (1 if total_submenus % submenus_por_pagina > 0 else 0)

            if submenus:
                mensagem = "<b>📂 Todos os Submenus:</b>\n\n"
                for subcategoria, submenu in submenus:
                    mensagem += f"🍎 {subcategoria} - {submenu}\n"
                mensagem += f"\nPágina {pagina}/{total_paginas}"

                # Criar botões de navegação
                markup = InlineKeyboardMarkup()
                if total_paginas > 1:
                    markup.row(
                        InlineKeyboardButton("⬅️", callback_data=f"navigate_submenus_{pagina - 1 if pagina > 1 else total_paginas}"),
                        InlineKeyboardButton("➡️", callback_data=f"navigate_submenus_{pagina + 1 if pagina < total_paginas else 1}")
                    )

                bot.send_message(message.chat.id, mensagem, parse_mode="HTML", reply_to_message_id=message.message_id, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Não foram encontrados submenus.", parse_mode="HTML", reply_to_message_id=message.message_id)

        else:
            # Subcategoria fornecida, mostrar submenus específicos da subcategoria
            subcategoria = parts[1].strip()
            query_submenus = """
            SELECT DISTINCT submenu
            FROM personagens
            WHERE subcategoria = %s AND submenu IS NOT NULL AND submenu != ''
            """
            cursor.execute(query_submenus, (subcategoria,))
            submenus = [row[0] for row in cursor.fetchall()]

            if submenus:
                mensagem = f"<b>📂 Submenus na subcategoria '{subcategoria.title()}':</b>\n\n"
                for submenu in submenus:
                    mensagem += f"🍎 {subcategoria} - {submenu}\n"
            else:
                mensagem = f"Não foram encontrados submenus para a subcategoria '{subcategoria.title()}'."

            bot.send_message(message.chat.id, mensagem, parse_mode="HTML", reply_to_message_id=message.message_id)

    except Exception as e:
        print(f"Erro ao processar comando /submenus: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")
    finally:
        fechar_conexao(cursor, conn)

# Handler para callback da navegação de páginas
@bot.callback_query_handler(func=lambda call: call.data.startswith('navigate_submenus_'))
def callback_navegacao_submenus(call):
    try:
        data = call.data.split('_')
        pagina_str = data[-1]
        pagina = int(pagina_str)
        submenus_por_pagina = 15

        conn, cursor = conectar_banco_dados()

        query_todos_submenus = """
        SELECT subcategoria, submenu
        FROM personagens
        WHERE submenu IS NOT NULL AND submenu != ''
        GROUP BY subcategoria, submenu
        ORDER BY subcategoria, submenu
        LIMIT %s OFFSET %s
        """
        offset = (pagina - 1) * submenus_por_pagina
        cursor.execute(query_todos_submenus, (submenus_por_pagina, offset))
        submenus = cursor.fetchall()

        # Obter o total de submenus para paginação
        cursor.execute("SELECT COUNT(DISTINCT subcategoria, submenu) FROM personagens WHERE submenu IS NOT NULL AND submenu != ''")
        total_submenus = cursor.fetchone()[0]
        total_paginas = (total_submenus // submenus_por_pagina) + (1 if total_submenus % submenus_por_pagina > 0 else 0)

        if submenus:
            mensagem = "<b>📂 Todos os Submenus</b>\n\n"
            for subcategoria, submenu in submenus:
                mensagem += f"🍎 {subcategoria} - {submenu}\n"
            mensagem += f"\nPágina {pagina}/{total_paginas}"

            # Criar botões de navegação
            markup = InlineKeyboardMarkup()
            if total_paginas > 1:
                markup.row(
                    InlineKeyboardButton("⬅️ Anterior", callback_data=f"navigate_submenus_{pagina - 1 if pagina > 1 else total_paginas}"),
                    InlineKeyboardButton("➡️ Próxima", callback_data=f"navigate_submenus_{pagina + 1 if pagina < total_paginas else 1}")
                )

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=mensagem, parse_mode="HTML", reply_markup=markup)

    except Exception as e:
        print(f"Erro ao processar callback de navegação: {e}")
        bot.answer_callback_query(call.id, "Ocorreu um erro ao processar sua solicitação.")
    finally:
        fechar_conexao(cursor, conn)

        
@bot.message_handler(commands=['submenu'])
def submenu_command(message):
    try:
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            bot.reply_to(message, "Por favor, forneça o tipo ('s' ou 'f') e o nome do submenu após o comando, por exemplo: /submenu s bts")
            return

        tipo = parts[1].strip()
        submenu = parts[2].strip()

        id_usuario = message.from_user.id
        nome_usuario = message.from_user.first_name

        conn, cursor = conectar_banco_dados()

        # Verifica os personagens que o usuário possui na subcategoria especificada
        query_possui = """
        SELECT per.id_personagem, per.nome, per.subcategoria
        FROM inventario inv
        JOIN personagens per ON inv.id_personagem = per.id_personagem
        WHERE inv.id_usuario = %s AND per.submenu = %s
        """
        cursor.execute(query_possui, (id_usuario, submenu))
        personagens_possui = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

        # Verifica todos os personagens na subcategoria especificada
        query_todos = """
        SELECT id_personagem, nome, subcategoria
        FROM personagens
        WHERE submenu = %s
        """
        cursor.execute(query_todos, (submenu,))
        todos_personagens = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}

        if tipo == 's':
            # Mostrar os personagens que o usuário possui
            mensagem = f"🌧️ A cesta de {nome_usuario} não está completa, mas o rio ainda tem muitos segredos!\n\n"
            mensagem += f"🧺 | {list(personagens_possui.values())[0][1]} - {submenu.title()}\n" if personagens_possui else f"🧺 | Subcategoria Desconhecida - {submenu.title()}\n"
            mensagem += f"📄 | 1/1\n"  # Paginação fixa para simplificação
            mensagem += f"🐟 | {len(personagens_possui)}/{len(todos_personagens)}\n\n"
            if personagens_possui:
                for id_personagem, (nome, subcategoria) in personagens_possui.items():
                    mensagem += f"{id_personagem} - {nome}\n"
            else:
                mensagem += "Você não possui nenhum personagem nesta subcategoria."

        elif tipo == 'f':
            # Mostrar os personagens que o usuário não possui
            personagens_faltantes = {id_personagem: (nome, subcategoria) for id_personagem, (nome, subcategoria) in todos_personagens.items() if id_personagem not in personagens_possui}
            mensagem = f"🌧️ A cesta de {nome_usuario} não está completa, mas o rio ainda tem muitos segredos!\n\n"
            mensagem += f"🧺 | {list(todos_personagens.values())[0][1]} - {submenu.title()}\n" if todos_personagens else f"🧺 | Subcategoria Desconhecida - {submenu.title()}\n"
            mensagem += f"📄 | 1/1\n"  # Paginação fixa para simplificação
            mensagem += f"🐟 | {len(todos_personagens) - len(personagens_faltantes)}/{len(todos_personagens)}\n\n"
            if personagens_faltantes:
                for id_personagem, (nome, subcategoria) in personagens_faltantes.items():
                    mensagem += f"{id_personagem} - {nome}\n"
            else:
                mensagem += "Você possui todos os personagens nesta subcategoria."

        else:
            bot.reply_to(message, "Tipo inválido. Use 's' para os personagens que você possui e 'f' para os que você não possui.")
            return

        bot.send_message(message.chat.id, mensagem, parse_mode="HTML", reply_to_message_id=message.message_id)

    except Exception as e:
        print(f"Erro ao processar comando /submenu: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")
    finally:
        fechar_conexao(cursor, conn)
        
def obter_historico_trocas(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
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

@bot.message_handler(commands=['hist'])
def command_historico(message):
    id_usuario = message.chat.id  
    tipo_historico = message.text.split()[-1].lower()  

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

            bot.send_message(id_usuario, historico_mensagem)
        else:
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

            bot.send_message(id_usuario, historico_mensagem)
        else:
            bot.send_message(id_usuario, "Nenhuma pesca encontrada para este usuário.")

def user(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        query_obter_user = "SELECT user FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query_obter_user, (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            nome_usuario = resultado[0]
            return nome_usuario
        else:
            return "Usuário não encontrado"  

    except mysql.connector.Error as e:
        print(f"Erro ao obter o nome de usuário: {e}")
        return None  

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def editar_mensagem_tag(message, nometag, pagina_atual, id_usuario, total_paginas):
    try:
        conn, cursor = conectar_banco_dados()
        offset = (pagina_atual - 1) * 10
        query = "SELECT id_personagem FROM tags WHERE nometag = %s LIMIT 10 OFFSET %s"
        cursor.execute(query, (nometag, offset))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Cartas na tag {nometag}:\n\n"
            for resultado in resultados:
                id_personagem = resultado[0]
                
                cursor.execute("SELECT emoji, nome FROM personagens WHERE id_personagem = %s", (id_personagem,))
                carta_info_personagens = cursor.fetchone()

                cursor.execute("SELECT emoji, nome FROM evento WHERE id_personagem = %s", (id_personagem,))
                carta_info_evento = cursor.fetchone()

                if carta_info_personagens:
                    emoji, nome = carta_info_personagens
                elif carta_info_evento:
                    emoji, nome = carta_info_evento
                else:
                    resposta += f"ℹ️ | Carta não encontrada para ID: {id_personagem}\n"
                    continue

                emoji_status = '☀️' if inventario_existe(id_usuario, id_personagem) else '🌧️'
                resposta += f"{emoji_status} | {emoji} ⭑ {id_personagem} - {nome}\n"

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

def criar_markup_tag(pagina_atual, total_paginas, nometag):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_anterior = telebot.types.InlineKeyboardButton("⬅️", callback_data=f"tag_{pagina_atual-1}_{nometag}_{total_paginas}")
    btn_proxima = telebot.types.InlineKeyboardButton("➡️", callback_data=f"tag_{pagina_atual+1}_{nometag}_{total_paginas}")
    markup.row(btn_anterior, btn_proxima)

    return markup

def mostrar_primeira_pagina_tag(message, nometag, id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        query_total = "SELECT COUNT(id_personagem) FROM tags WHERE nometag = %s AND id_usuario = %s"
        cursor.execute(query_total, (nometag, id_usuario))
        total_registros = cursor.fetchone()[0]

        total_paginas = (total_registros // 10) + (1 if total_registros % 10 > 0 else 0)

        if total_registros == 0:
            bot.reply_to(message, f"Nenhum registro encontrado para a tag '{nometag}'.")
            return

        query = "SELECT id_personagem FROM tags WHERE nometag = %s AND id_usuario = %s LIMIT 10"
        cursor.execute(query, (nometag, id_usuario))
        resultados = cursor.fetchall()

        if resultados:
            resposta = f"🔖| Cartas na tag {nometag}:\n\n"
            for resultado in resultados:
                id_personagem = resultado[0]
                
                cursor.execute("SELECT emoji, nome FROM personagens WHERE id_personagem = %s", (id_personagem,))
                carta_info_personagens = cursor.fetchone()

                cursor.execute("SELECT emoji, nome FROM evento WHERE id_personagem = %s", (id_personagem,))
                carta_info_evento = cursor.fetchone()

                if carta_info_personagens:
                    emoji, nome = carta_info_personagens
                elif carta_info_evento:
                    emoji, nome = carta_info_evento
                else:
                    resposta += f"ℹ️ | Carta não encontrada para ID: {id_personagem}\n"
                    continue

                emoji_status = '☀️' if inventario_existe(id_usuario, id_personagem) else '🌧️'

                resposta += f"{emoji_status} | {emoji} ⭑ {id_personagem} - {nome}\n"

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

@bot.message_handler(commands=['tag'])
def verificar_comando_tag(message):
    try:
        parametros = message.text.split(' ', 1)[1:] 

        if not parametros:
            conn, cursor = conectar_banco_dados()
            id_usuario = message.from_user.id
            cursor.execute("SELECT DISTINCT nometag FROM tags WHERE id_usuario = %s", (id_usuario,))
            tags = cursor.fetchall()
            if tags:
                resposta = "🔖| Suas tags:\n\n"
                for tag in tags:
                    resposta += f"• {tag[0]}\n"
                bot.reply_to(message, resposta)
            else:
                bot.reply_to(message, "Você não possui nenhuma tag.")
            fechar_conexao(cursor, conn)
            return

        nometag = parametros[0] 
        id_usuario = message.from_user.id
        mostrar_primeira_pagina_tag(message, nometag, id_usuario)

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
                
                if ids_personagens_str and nometag:
                    ids_personagens = [id_personagem.strip() for id_personagem in ids_personagens_str.split(',')]
                    
                    for id_personagem in ids_personagens:
                        cursor.execute(
                            "INSERT INTO tags (id_usuario, id_personagem, nometag) VALUES (%s, %s, %s)", 
                            (id_usuario, id_personagem, nometag)
                        )
                    
                    conn.commit()
                    bot.reply_to(message, f"Tag '{nometag}' adicionada com sucesso.")
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
        
        if len(args) == 2:
            tag_info = args[1].strip()

            if '|' in tag_info:
                id_list, nometag = [part.strip() for part in tag_info.split('|')]
                ids_personagens = [id.strip() for id in id_list.split(',')]

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
    if message.from_user.id != 5532809878:
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

def obter_emoji_evento(evento):
    if evento == 'fixo':
        return '🪴'
    elif evento == 'amor':
        return '💐'
    elif evento == 'aniversario':
        return '🎁'
    return '🪴'        
@bot.message_handler(commands=['rev'])
def handle_rev_cards(message):
    if message.from_user.id != 5532809878:
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

def obter_favorito(id_usuario):
    try:
        query_fav_usuario = f"""
            SELECT p.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, p.categoria, p.imagem, 'personagens' AS origem
            FROM personagens p
            WHERE p.id_personagem = (
                SELECT fav
                FROM usuarios
                WHERE id_usuario = {id_usuario}
            )
            UNION
            SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, e.categoria, e.imagem, 'evento' AS origem
            FROM evento e
            WHERE e.id_personagem = (
                SELECT fav
                FROM usuarios
                WHERE id_usuario = {id_usuario}
            )
        """
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_fav_usuario)
        resultado_fav = cursor.fetchone()

        if resultado_fav:
            id_personagem = resultado_fav[0]
            emoji = resultado_fav[1]
            nome_carta = resultado_fav[2]
            imagem = resultado_fav[5]
            return id_personagem, emoji, nome_carta, imagem
        else:
            return None, None, None, None
    except Exception as e:
        print(f"Erro ao obter nome da carta: {e}")
        return None, None, None, None
    finally:
        fechar_conexao(cursor, conn)

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
        
        id_fav_usuario, emoji_fav, nome_fav, imagem_fav = obter_favorito(id_usuario)

        if id_fav_usuario is not None:
            print(id_fav_usuario)
            resposta = f"💌 | Cartas no armazém de {usuario}:\n\nFav: {emoji_fav} {id_fav_usuario} — {nome_fav}\n\n"

            sql = f"""
                SELECT id_personagem, emoji, nome_personagem, subcategoria, quantidade, categoria, evento
                FROM (
                    SELECT i.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, i.quantidade, p.categoria, '' AS evento
                    FROM inventario i
                    JOIN personagens p ON i.id_personagem = p.id_personagem
                    WHERE i.id_usuario = {id_usuario} AND i.quantidade > 0

                    UNION

                    SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria, e.evento
                    FROM evento e
                    WHERE e.id_personagem IN (
                        SELECT id_personagem
                        FROM inventario
                        WHERE id_usuario = {id_usuario} AND quantidade > 0
                    )
                ) AS combined
                ORDER BY 
                    CASE WHEN categoria = 'evento' THEN 0 ELSE 1 END, 
                    categoria, 
                    CAST(id_personagem AS UNSIGNED) ASC
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
                    id_carta, emoji_carta, nome_carta, subcategoria_carta, quantidade_carta, categoria_carta, evento_carta = carta
                    quantidade_carta = int(quantidade_carta) if quantidade_carta is not None else 0

                    if categoria_carta == 'evento':
                        emoji_carta = obter_emoji_evento(evento_carta)

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

                    repetida = " [+]" if quantidade_carta > 1 and categoria_carta != 'evento' else ""

                    resposta += f" {emoji_carta} <code>{id_carta}</code> • {nome_carta} - {subcategoria_carta} {letra_quantidade}{repetida}\n"

                quantidade_total_cartas = obter_quantidade_total_cartas(id_usuario)
                total_paginas = (quantidade_total_cartas + resultados_por_pagina - 1) // resultados_por_pagina
                resposta += f"\n{pagina}/{total_paginas}"
                gif_url = obter_gif_url(id_fav_usuario, id_usuario)
                print("gif", gif_url)
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
            return

        resposta = f"💌 | Cartas no armazém de {usuario}:\n\n"

        sql = f"""
            SELECT id_personagem, emoji, nome_personagem, subcategoria, quantidade, categoria, evento
            FROM (
                -- Consulta para cartas no inventário do usuário
                SELECT i.id_personagem, p.emoji, p.nome AS nome_personagem, p.subcategoria, i.quantidade, p.categoria, '' AS evento
                FROM inventario i
                JOIN personagens p ON i.id_personagem = p.id_personagem
                WHERE i.id_usuario = {id_usuario} AND i.quantidade > 0

                UNION ALL

                -- Consulta para cartas de evento que o usuário possui
                SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria, e.evento
                FROM evento e
                WHERE e.id_personagem IN (
                    SELECT id_personagem
                    FROM inventario
                    WHERE id_usuario = {id_usuario} AND quantidade > 0
                )
            ) AS combined
            ORDER BY 
                CASE WHEN categoria = 'evento' THEN 0 ELSE 1 END, 
                categoria, 
                CAST(id_personagem AS UNSIGNED) ASC
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
                id_carta, emoji_carta, nome_carta, subcategoria_carta, quantidade_carta, categoria_carta, evento_carta = carta
                quantidade_carta = int(quantidade_carta) if quantidade_carta is not None else 0

                if categoria_carta == 'evento':
                    emoji_carta = obter_emoji_evento(evento_carta)

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

                repetida = " [+]" if quantidade_carta > 1 and evento_carta else ""

                resposta += f" {emoji_carta} <code>{id_carta}</code> • {nome_carta} - {subcategoria_carta} {letra_quantidade}{repetida}\n"

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
        mensagem_banido = "Um erro ocorreu ao abrir seu armazém... Tente trocar seu fav usando o </code>comando /setfav</code>. Caso não resolva, entre em contato com o suporte."
        bot.send_message(message.chat.id, mensagem_banido)
    except telebot.apihelper.ApiHTTPException as e:
        print(f"Erro na API do Telegram: {e}")
    finally:
        fechar_conexao(cursor, conn)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:

        message = call.message
        conn, cursor = conectar_banco_dados()
        chat_id = call.message.chat.id

        if call.message:
            chat_id = call.message.chat.id
            if not verificar_tempo_passado(chat_id):
                return
            else:
                ultima_interacao[chat_id] = datetime.now()

            if call.data.startswith('pescar_'):
                categoria_callback(call)
            elif call.data.startswith('choose_subcategoria_'):
                data = call.data.split('_')
                subcategoria = data[2]
                chat_id = call.message.chat.id
                message_id = call.message.message_id
                choose_subcategoria_callback(call, subcategoria, cursor, conn,chat_id,message_id)    
            elif call.data.startswith("geral_compra_"):
                geral_compra_callback(call)
            elif call.data.startswith('confirmar_iscas'):
                message_id = call.message.message_id
                confirmar_iscas(call,message_id)
            elif call.data.startswith('doar_cenoura'):
                message_id = call.message.message_id
                doar_cenoura(call,message_id)    
            elif call.data.startswith("bpronomes_"):
                try:
                    mostrar_opcoes_pronome(call.message.chat.id, call.message.message_id)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            elif call.data.startswith("liberar_beta"):
                try:

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
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("🥕 Liberar Usuario", callback_data=f"liberar_beta")
                    btn_iscas = types.InlineKeyboardButton("🐟 Remover Usuario", callback_data=f"remover_beta")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_5)

                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Escolha o que deseja fazer:",reply_markup=markup)                    
                   
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    
            elif call.data.startswith("liberar_beta"):
                try:
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
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id
                    
                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("🚫 Banir", callback_data=f"banir_{id_usuario}")
                    btn_iscas = types.InlineKeyboardButton("🔍 Verificar Banimento", callback_data=f"verificarban_{id_usuario}")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_5)

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
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("Alterar gif", callback_data=f"novogif")
                    btn_iscas = types.InlineKeyboardButton("Deletar Gif", callback_data=f"delgif")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_5)

                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Escolha o que deseja fazer:",reply_markup=markup)                    
                   
                except Exception as e:
                    import traceback
                    traceback.print_exc()    
            elif call.data.startswith("tag"):
                    try:
                        parts = call.data.split('_')
                        pagina = int(parts[1])
                        nometag = parts[2]
                        id_usuario = call.from_user.id 
                        editar_mensagem_tag(message, nometag, pagina,id_usuario)
                    except Exception as e:
                        print(f"Erro ao processar callback de página para a tag: {e}")
            
            elif call.data.startswith("admdar_"):
                
                try:
                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

                    markup = types.InlineKeyboardMarkup()
                    btn_cenoura = types.InlineKeyboardButton("🥕 Dar Cenouras", callback_data=f"dar_cenoura_{id_usuario}")
                    btn_iscas = types.InlineKeyboardButton("🐟 Dar Iscas", callback_data=f"dar_iscas_{id_usuario}")
                    btn_1 = types.InlineKeyboardButton("🥕 Tirar Cenouras", callback_data=f"tirar_cenoura_{id_usuario}")
                    btn_2 = types.InlineKeyboardButton("🐟 Tirar Iscas", callback_data=f"tirar_isca_{id_usuario}")
                    btn_5 = types.InlineKeyboardButton("❌ Cancelar", callback_data=f"pcancelar")
                    markup.row(btn_cenoura, btn_iscas)
                    markup.row(btn_1, btn_2)
                    markup.row(btn_5)

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

                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa junto da quantidade de cenouras a adicionar:")                    
                    bot.register_next_step_handler(message, obter_id_cenouras)

                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")
                    
            elif call.data.startswith("dar_iscas"):
                try:

                    message_id = call.message.message_id
                    usuario = call.message.chat.first_name
                    id_usuario = call.message.chat.id

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

                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Por favor, envie o ID da pessoa junto da quantidade de iscas a retirar:")
                    bot.register_next_step_handler(message, remover_id_iscas)

                except Exception as e:
                    bot.reply_to(message, f"Ocorreu um erro: {e}")    
                        
            elif call.data.startswith("privacy"):
                message_id = call.message.message_id
                usuario = call.message.chat.first_name
                id_usuario = call.message.chat.id

                status_perfil = obter_privacidade_perfil(id_usuario)

                editar_mensagem_privacidade(call.message.chat.id, message_id, usuario, id_usuario, status_perfil)

            elif call.data == 'open_profile':
                atualizar_privacidade_perfil(call.message.chat.id, privacidade=False)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Perfil alterado para aberto.")

            elif call.data == 'lock_profile':
                atualizar_privacidade_perfil(call.message.chat.id, privacidade=True)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="Perfil alterado para trancado.")
            elif call.data == 'pcancelar':
                bot.delete_message(call.message.chat.id, call.message.message_id)     
         
            elif call.data.startswith("pronomes_"):
                pronome = call.data.replace('pronomes_', '')  
                print(pronome)
                if pronome == 'remove':
                    pronome = None 
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

def callback_pagina_tag(call):
    try:
        parts = call.data.split('_')
        pagina_atual = int(parts[1])
        nometag = parts[2]
        total_paginas = parts[3]
        id_usuario = call.from_user.id 
        if pagina_atual < 1:
            bot.answer_callback_query(call.id, text="Página inválida.")
            return

        editar_mensagem_tag(call.message, nometag, pagina_atual,id_usuario,total_paginas)

    except Exception as e:
        print(f"Erro ao processar callback de tag: {e}")
        bot.answer_callback_query(call.id, text="Ocorreu um erro ao processar a consulta.")
        

def verificar_ban(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()

        cursor.execute("SELECT * FROM ban WHERE iduser = %s", (str(id_usuario),))
        ban_info = cursor.fetchone()

        if ban_info:
            motivo = ban_info[3]
            nome = ban_info[2]
            return True, motivo, nome
        else:
            return False, None, None

    except Exception as e:
        print(f"Erro ao verificar na tabela ban: {e}")
        return False, None, None    
    
@bot.message_handler(commands=['youcompat'])
def youcompat_command(message):
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Você precisa usar este comando em resposta a uma mensagem de outro usuário.")
            return

        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Uso: /youcompat <subcategoria>")
            return
        
        subcategoria = ' '.join(args[1:])
        subcategoria = verificar_apelido(subcategoria)
        subcategoria_titulo = subcategoria.title()
        
        id_usuario_1 = message.from_user.id
        nome_usuario_1 = message.from_user.first_name
        id_usuario_2 = message.reply_to_message.from_user.id
        nome_usuario_2 = message.reply_to_message.from_user.first_name

        conn, cursor = conectar_banco_dados()

        query = """
        SELECT inv.id_personagem, per.nome
        FROM inventario inv
        JOIN personagens per ON inv.id_personagem = per.id_personagem
        WHERE inv.id_usuario = %s AND per.subcategoria = %s
        """
        cursor.execute(query, (id_usuario_1, subcategoria))
        personagens_usuario_1 = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(query, (id_usuario_2, subcategoria))
        personagens_usuario_2 = {row[0]: row[1] for row in cursor.fetchall()}

        diferenca = set(personagens_usuario_1.keys()) - set(personagens_usuario_2.keys())
        mensagem = f"<b>🎀 COMPATIBILIDADE 🎀 \n\n</b>🍎 | <b><i>{subcategoria_titulo}</i></b>\n🧺 |<b> Cesta de:</b> {nome_usuario_1} \n⛈️ | <b>Faltantes de:</b> {nome_usuario_2} \n\n"

        if diferenca:
            for id_personagem in diferenca:
                mensagem += f"{id_personagem} - {personagens_usuario_1.get(id_personagem)}\n"
        else:
            mensagem = "Parece que não temos um match. Tente outra espécie!"

        bot.send_message(message.chat.id, mensagem, parse_mode="HTML", reply_to_message_id=message.id)

    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro ao processar o comando: {e}")

    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['mecompat'])
def mecompat_command(message):
    conn, cursor = conectar_banco_dados()
    try:
        if not message.reply_to_message:
            bot.reply_to(message, "Você precisa usar este comando em resposta a uma mensagem de outro usuário.")
            return

        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Uso: /mecompat <subcategoria>")
            return
        
        subcategoria = ' '.join(args[1:])
        subcategoria = verificar_apelido(subcategoria)
        subcategoria_titulo = subcategoria.title()
        
        id_usuario_1 = message.from_user.id
        nome_usuario_1 = message.from_user.first_name
        id_usuario_2 = message.reply_to_message.from_user.id
        nome_usuario_2 = message.reply_to_message.from_user.first_name

        query = """
        SELECT inv.id_personagem, per.nome
        FROM inventario inv
        JOIN personagens per ON inv.id_personagem = per.id_personagem
        WHERE inv.id_usuario = %s AND per.subcategoria = %s
        """
        cursor.execute(query, (id_usuario_1, subcategoria))
        personagens_usuario_1 = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(query, (id_usuario_2, subcategoria))
        personagens_usuario_2 = {row[0]: row[1] for row in cursor.fetchall()}

        diferenca = set(personagens_usuario_2.keys()) - set(personagens_usuario_1.keys())
        mensagem = f"<b>🎀 COMPATIBILIDADE 🎀 \n\n</b>🍎 | <b><i>{subcategoria_titulo}</i></b>\n🧺 |<b> Cesta de:</b> {nome_usuario_2} \n⛈️ | <b>Faltantes de:</b> {nome_usuario_1} \n\n"

        if diferenca:
            for id_personagem in diferenca:
                mensagem += f"{id_personagem} - {personagens_usuario_2.get(id_personagem)}\n"
        else:
            mensagem = "Parece que não temos um match."

        bot.send_message(message.chat.id, mensagem, parse_mode="HTML", reply_to_message_id=message.id)

    except Exception as e:
        bot.reply_to(message, f"Ocorreu um erro ao processar o comando: {e}")
    finally:
        fechar_conexao(cursor, conn)
        
def verificar_apelido(subcategoria):
    try:
        conn, cursor = conectar_banco_dados()
        query = "SELECT nome_certo FROM apelidos WHERE apelido = %s AND tipo = 'subcategoria'"
        cursor.execute(query, (subcategoria,))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        return subcategoria
    except Exception as e:
        print(f"Erro ao verificar apelido: {e}")
        return subcategoria
    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['diary'])
def diary_command(message):
    user_id = message.from_user.id
    today = date.today()
    
    conn, cursor = conectar_banco_dados()
    
    try:
        cursor.execute("SELECT ultimo_diario, dias_consecutivos FROM diario WHERE id_usuario = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            ultimo_diario, dias_consecutivos = result

            if ultimo_diario == today:
                bot.send_message(message.chat.id, "Você já recebeu suas cenouras hoje. Volte amanhã!")
                return

            if ultimo_diario == today - timedelta(days=1):
                dias_consecutivos += 1
            else:
                dias_consecutivos = 1

            if dias_consecutivos <= 10:
                cenouras = dias_consecutivos * 10
            else:
                cenouras = 100

            cursor.execute("UPDATE diario SET ultimo_diario = %s, dias_consecutivos = %s WHERE id_usuario = %s", (today, dias_consecutivos, user_id))
            cursor.execute("UPDATE usuarios SET cenouras = cenouras + %s WHERE id_usuario = %s", (cenouras, user_id))
            conn.commit()
        else:

            cenouras = 10
            dias_consecutivos = 1
            cursor.execute("INSERT INTO diario (id_usuario, ultimo_diario, dias_consecutivos) VALUES (%s, %s, %s)", (user_id, today, dias_consecutivos))
            cursor.execute("UPDATE usuarios SET cenouras = cenouras + %s WHERE id_usuario = %s", (cenouras, user_id))
            conn.commit()

        phrase = random.choice(phrases)
        fortune = random.choice(fortunes)
        bot.send_message(message.chat.id, f"<i>{phrase}</i>\n\n<b>{fortune}</b>\n\nVocê recebeu <i>{cenouras} cenouras</i>!\n\n <b>Dias consecutivos:</b> <i>{dias_consecutivos}</i>\n\n",parse_mode="HTML")

        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text="Sim", callback_data="add_note"))
        markup.add(telebot.types.InlineKeyboardButton(text="Não", callback_data="cancael_note"))
        bot.send_message(message.chat.id, "Deseja anotar algo nesse dia especial?", reply_markup=markup)

    except mysql.connector.Error as err:
        print(f"Erro ao processar o comando /diary: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao tentar registrar seu diário. Tente novamente mais tarde.")
    finally:
        fechar_conexao(cursor, conn)

def receive_note(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    note = message.text
    today = date.today()

    conn, cursor = conectar_banco_dados()

    try:
        cursor.execute("INSERT INTO anotacoes (id_usuario, data, nome_usuario, anotacao) VALUES (%s, %s, %s, %s)",
                       (user_id, today, user_name, note))
        conn.commit()
        bot.send_message(message.chat.id, "Sua anotação foi registrada com sucesso!")

    except mysql.connector.Error as err:
        print(f"Erro ao registrar anotação: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao tentar registrar sua anotação. Tente novamente mais tarde.")
    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['pages'])
def pages_command(message):
    user_id = message.from_user.id

    conn, cursor = conectar_banco_dados()

    try:
        cursor.execute("SELECT data, anotacao FROM anotacoes WHERE id_usuario = %s ORDER BY data DESC", (user_id,))
        anotacoes = cursor.fetchall()

        if not anotacoes:
            bot.send_message(message.chat.id, "Você ainda não tem anotações no diário.")
            return

        response = ""
        for i, (data, anotacao) in enumerate(anotacoes, 1):
            response += f"Dia {i} - {data.strftime('%d/%m/%Y')}\n"
        
        bot.send_message(message.chat.id, response)

    except mysql.connector.Error as err:
        print(f"Erro ao obter anotações: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao tentar obter suas anotações. Tente novamente mais tarde.")
    finally:
        fechar_conexao(cursor, conn)

@bot.message_handler(commands=['page'])
def page_command(message):
    user_id = message.from_user.id
    params = message.text.split(' ', 1)[1:]
    if len(params) < 1:
        bot.send_message(message.chat.id, "Uso: /page <número_da_página>")
        return
    page_number = int(params[0])

    conn, cursor = conectar_banco_dados()

    try:
        cursor.execute("SELECT data, anotacao FROM anotacoes WHERE id_usuario = %s ORDER BY data DESC", (user_id,))
        anotacoes = cursor.fetchall()

        if not anotacoes:
            bot.send_message(message.chat.id, "Você ainda não tem anotações no diário.")
            return

        if page_number < 1 or page_number > len(anotacoes):
            bot.send_message(message.chat.id, "Número de página inválido.")
            return

        data, anotacao = anotacoes[page_number - 1]
        response = f"Mabigarden, dia {data.strftime('%d/%m/%Y')}\n\nQuerido diário... {anotacao}"
        
        bot.send_message(message.chat.id, response)

    except mysql.connector.Error as err:
        print(f"Erro ao obter anotação: {err}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao tentar obter sua anotação. Tente novamente mais tarde.")
    finally:
        fechar_conexao(cursor, conn)                      
def categoria_callback(call):
    try:
        categoria = call.data.replace('pescar_', '')
        
        if call.message and call.message.chat and call.message.chat.id:
            chat_id = call.message.chat.id
            message_id = call.message.message_id
            ultimo_clique[chat_id] = {'categoria': categoria}
            categoria_handler(call.message, categoria)
        else:
            print("Invalid message or chat data in the callback query.")
    except Exception as e:
        print(f"Erro ao processar categoria_callback: {e}")

def adicionar_atualizar_gif(id_personagem, id_usuario, link):
    try:
        conn, cursor = conectar_banco_dados()

        query_select = "SELECT idgif FROM gif WHERE id_personagem = %s AND id_usuario = %s"
        cursor.execute(query_select, (id_personagem, id_usuario))
        gif_existente = cursor.fetchone()

        if gif_existente:
            query_update = "UPDATE gif SET link = %s WHERE id_personagem = %s AND id_usuario = %s"
            cursor.execute(query_update, (link, id_personagem, id_usuario))
            conn.commit()
            return "GIF atualizado com sucesso!"
        else:
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
        bot.register_next_step_handler(message, obter_dados_gif)

    except Exception as e:
        bot.reply_to(message, f"Erro ao processar comando /gif: {e}")

def deletar_gif(id_personagem, id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        query_select = "SELECT idgif FROM gif WHERE id_personagem = %s AND id_usuario = %s"
        cursor.execute(query_select, (id_personagem, id_usuario))
        gif_existente = cursor.fetchone()

        if gif_existente:
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

def choose_subcategoria_callback(call, subcategoria, cursor, conn,chat_id,message_id):
    try:
        categoria_info = ultimo_clique.get(call.message.chat.id, {})
        categoria = categoria_info.get('categoria', '')
        if categoria.lower() == 'geral':
            evento_aleatorio = verificar_subcategoria_evento(subcategoria, cursor)
            if evento_aleatorio:
                send_card_message(call.message, evento_aleatorio)
            else:
                subcategoria_handler(call.message, subcategoria, cursor, conn, None,chat_id,message_id)
        else:
            subcategoria_handler(call.message, subcategoria, cursor, conn, None,chat_id,message_id)
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

def geral_compra_callback(call):
    try:
        conn, cursor = conectar_banco_dados()

        query_personagens = "SELECT id_personagem, nome, subcategoria,  emoji, categoria,  imagem, cr FROM personagens ORDER BY RAND() LIMIT 1"
        cursor.execute(query_personagens)
        carta_personagem = cursor.fetchone()
        chance = random.choices([True, False], weights=[5, 95])[0]
        if chance:
            query_evento = "SELECT id_personagem, nome, subcategoria, categoria, evento, emoji, cr, imagem FROM evento ORDER BY RAND() LIMIT 1"
            cursor.execute(query_evento)
            carta_evento = cursor.fetchone()
        else:
            carta_evento = None
        if carta_personagem or carta_evento:
            if carta_evento:
                id_personagem, nome, subcategoria, categoria, evento, emoji, cr, imagem = carta_evento
                categoria = "Evento"
            else:
                id_personagem, nome, subcategoria,  emoji, categoria,  imagem, cr = carta_personagem
                evento = ""
                categoria = categoria.capitalize() 

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

def answer_callback_query(bot, callback_query_id, text):
    bot.answer_callback_query(callback_query_id, text)
    
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

        if result and len(result) > 0: 
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
        if result and len(result) > 0:
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

        if result and len(result) > 0:  
            qnt_cenouras = int(result[0])
            if qnt_cenouras >= 1:
                mensagem = f"Você tem {qnt_cenouras} cenouras. \n\nPara doar, digite o usuário do Garden e a quantidade. \n\nExemplo: user1 100"
                bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=mensagem
                )


                @bot.message_handler(func=lambda message: message.chat.id == chat_id and message.from_user.id == id_usuario)
                def processar_resposta(message):
                    try:
                        conn, cursor = conectar_banco_dados()
                        resposta = message.text
                        
                        usuario_destino, quantidade = resposta.split()

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

        conn, cursor = conectar_banco_dados()
        if len(data) == 3:
            id_usuario, id_personagem, message_id = data

            sql_temp_select = "SELECT valor FROM temp_data WHERE id_usuario = %s AND id_personagem = %s"
            values_temp_select = (id_usuario, id_personagem)
            cursor.execute(sql_temp_select, values_temp_select)
            link_gif = cursor.fetchone()
            cursor.fetchall()  

            if link_gif:
                sql_check_gif = "SELECT idgif FROM gif WHERE id_usuario = %s AND id_personagem = %s"
                cursor.execute(sql_check_gif, (id_usuario, id_personagem))
                existing_gif = cursor.fetchone()

                if existing_gif:
                    sql_update_gif = "UPDATE gif SET link = %s, timestamp = NOW() WHERE idgif = %s"
                    cursor.execute(sql_update_gif, (link_gif[0], existing_gif[0]))
                else:
                    sql_insert_gif = "INSERT INTO gif (id_personagem, id_usuario, link, timestamp) VALUES (%s, %s, %s, NOW())"
                    cursor.execute(sql_insert_gif, (id_personagem, id_usuario, link_gif[0]))

                conn.commit()
                mensagem = f"Seu GIF para o personagem {id_personagem} foi atualizado!"
                bot.send_message(id_usuario, mensagem)

                grupo_id = -1002144134360 
                nome_usuario = obter_nome_usuario_por_id(id_usuario)
                mensagem_grupo = f"🎉 O GIF para o personagem {id_personagem} de {nome_usuario} foi aprovado! 🎉"

                try:
                    bot.edit_message_text(mensagem_grupo, chat_id=grupo_id, message_id=int(message_id))
                except telebot.apihelper.ApiTelegramException as e:
                    if "message to edit not found" in str(e):
                        bot.send_message(grupo_id, mensagem_grupo)
                    else:
                        raise e
            else:
                print("Link do GIF não encontrado.")
                bot.send_message(call.message.chat.id, "Erro ao aprovar o GIF. Link não encontrado.")
        else:
            print("Formato de callback incorreto. Esperado: 'aprovar_id_usuario_id_personagem_message_id'.")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        fechar_conexao(cursor, conn)

def reprovar_callback(call):
    try:
        data = call.data.replace('reprovar_', '').strip().split('_')
        if len(data) == 3:
            id_usuario, id_personagem, message_id = data
            mensagem = f"Seu gif para o personagem {id_personagem} foi recusado"
            bot.send_message(id_usuario, mensagem)

            grupo_id = -1002144134360
            nome_usuario = obter_nome_usuario_por_id(id_usuario)
            mensagem_grupo = f"O GIF para o personagem {id_personagem} de {nome_usuario} foi reprovado... 😐"
            bot.edit_message_text(mensagem_grupo, chat_id=grupo_id, message_id=int(message_id))
        else:
            print("Formato de callback incorreto. Esperado: 'reprovar_id_usuario_id_personagem_message_id'")
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

                cursor.execute("SELECT COUNT(*) FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                               (id_usuario, id_personagem_wishlist))
                existing_inventory_count = cursor.fetchone()[0]
                inventory_exists = existing_inventory_count > 0

                if inventory_exists:
                    cursor.execute("DELETE FROM wishlist WHERE id_usuario = %s AND id_personagem = %s",
                                   (id_usuario, id_personagem_wishlist))
                    cartas_removidas.append(f"{emoji_carta_wishlist} - {nome_carta_wishlist} de {subcategoria_carta_wishlist}")

            if cartas_removidas:
                resposta = f"Algumas cartas foram removidas da wishlist porque já estão no seu inventário:\n{', '.join(map(str, cartas_removidas))}"
                bot.send_message(message.chat.id, resposta, reply_to_message_id=message.message_id)

            lista_wishlist_atualizada = f"🤞 | Cartas na wishlist de {message.from_user.first_name}:\n\n"
            for carta_atualizada in cartas_wishlist:
                id_carta = carta_atualizada[0]
                emoji_carta = carta_atualizada[3]
                nome_carta = carta_atualizada[1]
                subcategoria_carta = carta_atualizada[2]
                lista_wishlist_atualizada += f"{emoji_carta} ∙ {id_carta} - {nome_carta} de {subcategoria_carta}\n"

            bot.send_message(message.chat.id, lista_wishlist_atualizada, reply_to_message_id=message.message_id)
        else:
            bot.send_message(message.chat.id, "Sua wishlist está vazia! Devo te desejar parabéns?", reply_to_message_id=message.message_id)

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


@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time() 

    bot.reply_to(message, "🏓 Pong")
    
    end_time = time.time() 
    elapsed_time = end_time - start_time 

    rps = 1 / elapsed_time if elapsed_time > 0 else float('inf')

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
        id_usuario = message.from_user.id
        print("Usuário não está banido. Pode cenourar.")

        ids_personagem = message.text.replace('/cenourar', '').strip().split(',')
        ids_personagem = [id.strip() for id in ids_personagem if id.strip()]

        if ids_personagem:
            ids_formatados = ', '.join(ids_personagem)
            confirmacao = f"Deseja cenourar as cartas:\n\n{ids_formatados}?"
            keyboard = telebot.types.InlineKeyboardMarkup()
            sim_button = telebot.types.InlineKeyboardButton(text="Sim", callback_data=f"cenourar_sim_{id_usuario}_{','.join(ids_personagem)}")
            nao_button = telebot.types.InlineKeyboardButton(text="Não", callback_data=f"cenourar_nao_{id_usuario}")
            keyboard.row(sim_button, nao_button)
            bot.send_message(message.chat.id, confirmacao, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Nenhum ID de personagem fornecido.")
    except Exception as e:
        print(f"Erro ao processar o comando de cenourar: {e}")
        bot.send_message(message.chat.id, "Erro ao processar o comando de cenourar.")
    finally:
        fechar_conexao(cursor, conn)


@bot.message_handler(commands=['pesca'])
@bot.message_handler(commands=['pescar'])
def pescar(message):
    try:

        nome = message.from_user.first_name
        id = message.from_user.id

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
        # Consulta para obter o timestamp mais recente do gif enviado pelo usuário
        query_ultimo_gif = f"""
            SELECT MAX(timestamp) AS ultima_hora 
            FROM gif 
            WHERE id_usuario = {id_usuario}
        """
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_ultimo_gif)
        ultimo_gif = cursor.fetchone()

        if ultimo_gif and ultimo_gif[0]:
            ultimo_gif_datetime = ultimo_gif[0]
            
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
        
        

@bot.message_handler(commands=['setgif'])
def enviar_gif(message):
    try:
        comando = message.text.split('/setgif', 1)[1].strip().lower()
        partes_comando = comando.split(' ')
        id_personagem = partes_comando[0]
        id_usuario = message.from_user.id

        conn, cursor = conectar_banco_dados()
        # Verificar se o lembrete para GIF está ativado
        cursor.execute("SELECT gif FROM lembretes WHERE id_usuario = %s", (id_usuario,))
        lembrete_gif_ativado = cursor.fetchone()
        if lembrete_gif_ativado and not lembrete_gif_ativado[0]:
            bot.send_message(message.chat.id, "Você não ativou o lembrete para GIFs.")
            fechar_conexao(cursor, conn)
            return

        # Verificar se o usuário possui 30 unidades da carta
        cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s", (id_usuario, id_personagem))
        resultado = cursor.fetchone()
        if not resultado or resultado[0] < 30:
            bot.send_message(message.chat.id, "Você precisa ter pelo menos 30 unidades dessa carta para enviar um gif.")
            fechar_conexao(cursor, conn)
            return

        if 'eusoqueriasernormal' not in partes_comando:
            tempo_restante = verifica_tempo_ultimo_gif(id_usuario)
            if tempo_restante:
                bot.send_message(message.chat.id, f"Você já enviou um gif recentemente. Aguarde {tempo_restante} antes de enviar outro.")
                fechar_conexao(cursor, conn)
                return

        # Inserir novo gif na tabela e agendar notificação para uma hora depois
        data_atual = datetime.now()
        cursor.execute("INSERT INTO gif (id_usuario, id_personagem, timestamp) VALUES (%s, %s, %s)", (id_usuario, id_personagem, data_atual))
        conn.commit()

        scheduler.add_job(notificar_usuario_sobre_gif, 'date', run_date=data_atual + timedelta(hours=1), args=[id_usuario], replace_existing=True)

        bot.send_message(message.chat.id, "Eba! Você pode escolher um gif!\nEnvie o link do gif gerado pelo @UploadTelegraphBot:")
        links_gif[message.from_user.id] = id_personagem
        bot.register_next_step_handler(message, receber_link_gif, id_personagem)

        fechar_conexao(cursor, conn)

    except IndexError:
        bot.send_message(message.chat.id, "Por favor, forneça o ID do personagem.")
    except Exception as e:
        print(f"Erro ao processar o comando /setgif: {e}")
        fechar_conexao(cursor, conn)

def receber_link_gif(message, id_personagem):
    id_usuario = message.from_user.id

    if id_usuario:
        link_gif = message.text

        if not re.match(r'^https?://\S+$', link_gif):
            bot.send_message(message.chat.id, "Por favor, envie <b>apenas</b> o <b>link</b> do GIF.", parse_mode="HTML")
            return

        id_personagem = links_gif.get(id_usuario)

        if id_personagem:
            numero_personagem = id_personagem.split('_')[0]
            conn, cursor = conectar_banco_dados()

            sql_usuario = "SELECT nome_usuario, nome FROM usuarios WHERE id_usuario = %s"
            cursor.execute(sql_usuario, (id_usuario,))
            resultado_usuario = cursor.fetchone()

            sql_personagem = "SELECT nome, subcategoria FROM personagens WHERE id_personagem = %s"
            cursor.execute(sql_personagem, (numero_personagem,))
            resultado_personagem = cursor.fetchone()

            if resultado_usuario and resultado_personagem:
                nome_usuario = resultado_usuario[0]
                nome_personagem = resultado_personagem[0]
                subcategoria_personagem = resultado_personagem[1]

                sql_temp_insert = """
                    INSERT INTO temp_data (id_usuario, id_personagem, chave, valor)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE valor = VALUES(valor), chave = VALUES(chave)
                """
                chave = f"{id_usuario}_{numero_personagem}"
                cursor.execute(sql_temp_insert, (id_usuario, numero_personagem, chave, link_gif))
                conn.commit()
                fechar_conexao(cursor, conn)
                
                keyboard = telebot.types.InlineKeyboardMarkup()
                btn_aprovar = telebot.types.InlineKeyboardButton(text="✔️ Aprovar", callback_data=f"aprovar_{id_usuario}_{numero_personagem}_{message.message_id}")
                btn_reprovar = telebot.types.InlineKeyboardButton(text="❌ Reprovar", callback_data=f"reprovar_{id_usuario}_{numero_personagem}_{message.message_id}")

                keyboard.row(btn_aprovar, btn_reprovar)
                bot.forward_message(chat_id=-1002144134360, from_chat_id=message.chat.id, message_id=message.message_id)
                chat_id = -1002144134360
                mensagem = f"Pedido de aprovação de GIF:\n\n"
                mensagem += f"ID Personagem: {numero_personagem}\n"
                mensagem += f"{nome_personagem} de {subcategoria_personagem}\n\n"
                mensagem += f"Usuário: @{message.from_user.username}\n"
                mensagem += f"Nome: {nome_usuario}\n"

                sent_message = bot.send_message(chat_id, mensagem, reply_markup=keyboard)
                bot.send_message(message.chat.id, "Link do GIF registrado com sucesso. Aguardando aprovação.")
                return sent_message.message_id
            else:
                fechar_conexao(cursor, conn)
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
        return 0 
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

        if verifica_inventario_troca(eu, minhacarta) == 0:
            bot.send_message(chat_id, f"🌦️ ་  {meunome}, você não possui o peixe {minhacarta} para trocar.", reply_to_message_id=message.message_id)
            return
        
        if verifica_inventario_troca(voce, suacarta) == 0:
            bot.send_message(chat_id, f"🌦️ ་  Parece que {seunome} não possui o peixe {suacarta} para trocar.", reply_to_message_id=message.message_id)
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

        keyboard = types.InlineKeyboardMarkup()

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
            sql_insert = "INSERT INTO historico_trocas (id_usuario1, id_usuario2, quantidade_cartas_antes_usuario1, quantidade_cartas_depois_usuario1, quantidade_cartas_antes_usuario2, quantidade_cartas_depois_usuario2, id_carta_usuario1, id_carta_usuario2, aceita) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (eu, voce, qntminha_antes, qntminha_depois, qntsua_antes, qntsua_depois, minhacarta, suacarta, True)
            cursor.execute(sql_insert, val)

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

        qnt_carta = verifica_inventario_troca(eu, minhacarta)
        valor = qnt
        diminuir_cenouras(eu, valor)
        if qnt_carta > 0:
            cursor.execute("UPDATE inventario SET quantidade = quantidade - %s WHERE id_usuario = %s AND id_personagem = %s",
                           (qnt, eu, minhacarta))

            cursor.execute("SELECT quantidade FROM inventario WHERE id_usuario = %s AND id_personagem = %s",
                           (destinatario_id, minhacarta))
            qnt_destinatario = cursor.fetchone()

            if qnt_destinatario:
                cursor.execute("UPDATE inventario SET quantidade = quantidade + %s WHERE id_usuario = %s AND id_personagem = %s",
                               (qnt, destinatario_id, minhacarta))
            else:
                cursor.execute("INSERT INTO inventario (id_usuario, id_personagem, quantidade) VALUES (%s, %s, %s)",
                               (destinatario_id, minhacarta,qnt))

            conn.commit()
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Doação realizada com sucesso!")
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="Você não pode doar uma carta que não possui.")

    except mysql.connector.Error as err:
        print(f"Erro durante a doação: {err}")
        bot.send_message(chat_id, "Houve um erro ao processar a doação. Tente novamente.")

def verificar_autorizacao(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT adm FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        result = cursor.fetchone()

        if result and result[0] is not None:
            return True  
        else:
            return False  
    except Exception as e:
        print(f"Erro ao verificar autorização: {e}")
        return False  

    finally:
   
        if conn.is_connected():
            cursor.close()
            conn.close()

def inserir_na_tabela_beta(id_usuario, nome):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("INSERT INTO beta (id, nome) VALUES (%s, %s)", (id_usuario, nome))
        conn.commit()  

        return True  

    except Exception as e:
        print(f"Erro ao inserir na tabela beta: {e}")
        return False  

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            

def excluir_da_tabela_beta(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("DELETE FROM beta WHERE id = %s", (id_usuario,))
        conn.commit()  

        return True  

    except Exception as e:
        print(f"Erro ao excluir da tabela beta: {e}")
        return False  #
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def remover_id_cenouras(message):
    try:
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            quantidade_cenouras = int(parts[1])
            conn, cursor = conectar_banco_dados()

            cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()
            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual - quantidade_cenouras

                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()
                fechar_conexao(cursor, conn)

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
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            quantidade_iscas = int(parts[1])

            conn, cursor = conectar_banco_dados()

            cursor.execute("SELECT iscas FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()

            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual - quantidade_iscas

                cursor.execute("UPDATE usuarios SET iscas = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()

                fechar_conexao(cursor, conn)

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
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            quantidade_cenouras = int(parts[1])
            conn, cursor = conectar_banco_dados()

            cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()

            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual + quantidade_cenouras

                cursor.execute("UPDATE usuarios SET cenouras = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()

                fechar_conexao(cursor, conn)

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
        parts = message.text.split()
        if len(parts) == 2:
            id_pessoa = int(parts[0])
            quantidade_iscas = int(parts[1])

            conn, cursor = conectar_banco_dados()

            cursor.execute("SELECT iscas FROM usuarios WHERE id_usuario = %s", (id_pessoa,))
            result = cursor.fetchone()

            if result:
                quantidade_atual = result[0]
                nova_quantidade = quantidade_atual + quantidade_iscas

                cursor.execute("UPDATE usuarios SET iscas = %s WHERE id_usuario = %s", (nova_quantidade, id_pessoa))
                conn.commit()

                fechar_conexao(cursor, conn)

                bot.send_message(message.chat.id, f"A quantidade de iscas foi atualizada para {nova_quantidade} para o usuário com ID {id_pessoa}.")
            else:
                bot.send_message(message.chat.id, f"ID de usuário inválido.")

        else:
            bot.send_message(message.chat.id, "Formato incorreto. Envie o ID da pessoa e a quantidade de iscas a ser adicionada, separados por espaço.")

    except Exception as e:
        print(f"Erro ao obter ID e quantidade de cenouras: {e}")
        bot.send_message(message.chat.id, "Ocorreu um erro ao processar a solicitação.")

def obter_id_beta(message):
    id_usuario = message.text
    bot.send_message(message.chat.id, "Por favor, envie o nome da pessoa:")
    bot.register_next_step_handler(message, lambda msg: obter_nome_beta(msg, id_usuario))

def obter_nome_beta(message, id_usuario):
    nome = message.text
    if inserir_na_tabela_beta(id_usuario, nome):
        bot.reply_to(message, "Usuário adicionado à lista beta com sucesso!")
    else:
        bot.reply_to(message, "Erro ao adicionar usuário à lista beta.")

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

        cursor.execute("SELECT nome, motivo FROM ban")
        banidos = cursor.fetchall()

        if banidos:
            banidos_info = []
            for banido in banidos:
                nome, motivo = banido
                banidos_info.append((nome, motivo))
            return True, banidos_info
        else:
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

        quantidade = int(args[1]) 
        minhacarta = int(args[2])
        
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT cenouras FROM usuarios WHERE id_usuario = %s", (eu,))
        result = cursor.fetchone()

        if result:
            qnt_cenouras = int(result[0])
        else:
            qnt_cenouras = 0

        if qnt_cenouras >= quantidade:
            qnt_carta = verifica_inventario_troca(eu, minhacarta)
            if qnt_carta > 0:
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
                texto = f"Olá, {message.from_user.first_name}!\n\nVocê tem {qnt_cenouras} {cen_str} e {qnt_str}: {minhacarta} — {nome_carta}.\n\n"
                texto += f"Deseja gastar {quantidade} {cen_str} para doar {quantidade} desses peixes para {nome_destinatario}?"

                keyboard = telebot.types.InlineKeyboardMarkup()
                keyboard.row(
                    telebot.types.InlineKeyboardButton(text="Sim", callback_data=f'confirmar_doacao_{eu}_{minhacarta}_{destinatario_id}_{quantidade}'),
                    telebot.types.InlineKeyboardButton(text="Não", callback_data=f'tcancelar_{eu}')
                )

                bot.send_message(chat_id, texto, reply_markup=keyboard)
            else:
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
        keyboard.row(telebot.types.InlineKeyboardButton(text="⛲ Fonte dos Desejos", callback_data='fazer_pedido'))

        image_url = "https://telegra.ph/file/ea116d98a5bd8d6179612.jpg"
        bot.send_photo(message.chat.id, image_url,
                       caption='Olá! Seja muito bem-vindo à vendinha da Mabi. Como posso te ajudar?',
                       reply_markup=keyboard, reply_to_message_id=message.message_id)

    except ValueError as e:
        print(f"Erro: {e}")
        mensagem_banido = "Você foi banido permanentemente do garden. Entre em contato com o suporte caso haja dúvidas."
        bot.send_message(message.chat.id, mensagem_banido, reply_to_message_id=message.message_id)

def atualizar_pronome(id_usuario, pronome):
    try:
        conn, cursor = conectar_banco_dados()
        query = "UPDATE usuarios SET pronome = %s WHERE id_usuario = %s"
        cursor.execute(query, (pronome, id_usuario))
        conn.commit()
        print(f"Pronome atualizado para '{pronome}' para o usuário {id_usuario}")
    except Exception as e:
        print(f"Erro ao atualizar o pronome: {e}")
        
@bot.message_handler(commands=['peixes'])
def verificar_comando_peixes(message):
    try:
        parametros = message.text.split(' ', 2)[1:]  

        if not parametros:
            bot.reply_to(message, "Por favor, forneça a subcategoria.")
            return
        
        subcategoria = " ".join(parametros)  
        
        if len(parametros) > 1 and parametros[0] == 'img':
            subcategoria = " ".join(parametros[1:])
            enviar_imagem_peixe(message, subcategoria)
        else:
            mostrar_lista_peixes(message, subcategoria)
        
    except Exception as e:
        print(f"Erro ao processar comando /peixes: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")


def criar_botao_pagina_peixes(message, subcategoria, pagina_atual):
    try:
        conn, cursor = conectar_banco_dados()
        query_total = "SELECT COUNT(id_personagem) FROM personagens WHERE subcategoria = %s"
        cursor.execute(query_total, (subcategoria,))
        total_imagens = cursor.fetchone()[0]  
        markup = telebot.types.InlineKeyboardMarkup()
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
        subcategoria_like = f"%{subcategoria}%"
        query_subcategoria = "SELECT subcategoria FROM personagens WHERE subcategoria LIKE %s LIMIT 1"
        cursor.execute(query_subcategoria, (subcategoria_like,))
        subcategoria_encontrada = cursor.fetchone()[0]  
        
        query = "SELECT imagem, emoji, nome, id_personagem FROM personagens WHERE subcategoria = %s LIMIT 1 OFFSET %s"
        cursor.execute(query, (subcategoria_encontrada, pagina_atual - 1))
        imagem_info = cursor.fetchone()
        
        query_ids = "SELECT id_personagem FROM personagens WHERE subcategoria = %s"
        cursor.execute(query_ids, (subcategoria_encontrada,))
        ids = [id[0] for id in cursor.fetchall()] 
        
        total_ids = len(ids)
        
        if imagem_info:
            imagem = imagem_info[0]  
            emoji = imagem_info[1]  
            nome = imagem_info[2]    
            id_personagem = imagem_info[3]  
            pagina_atual = 1
            
            caption = f"Peixes da espécie: <b>{subcategoria_encontrada}</b>\n\n{emoji} {id_personagem} - {nome}\n\nPersonagem {pagina_atual} de {total_ids}"
            
            markup = criar_botao_pagina_peixes(message, subcategoria_encontrada, pagina_atual)
            
            bot.send_photo(message.chat.id, photo=imagem, caption=caption, reply_markup=markup, parse_mode="HTML")

        else:
            bot.reply_to(message, f"Nenhuma imagem encontrada na subcategoria '{subcategoria_encontrada}'.")

    except Exception as e:
        print(f"Erro ao processar comando /peixes img: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")


def callback_img_peixes(call, pagina_atual, subcategoria):
    try:
        conn, cursor = conectar_banco_dados()

        subcategoria_like = f"%{subcategoria}%"
        query_subcategoria = "SELECT subcategoria FROM personagens WHERE subcategoria LIKE %s LIMIT 1"
        cursor.execute(query_subcategoria, (subcategoria_like,))
        subcategoria_encontrada = cursor.fetchone()

        query = "SELECT id_personagem FROM personagens WHERE subcategoria = %s"
        cursor.execute(query, (subcategoria,))
        ids = [id[0] for id in cursor.fetchall()] 
        
        total_ids = len(ids)

        if 1 <= pagina_atual <= total_ids:
            id_atual = ids[pagina_atual - 1]  
            

            query_info = "SELECT imagem, emoji, nome FROM personagens WHERE id_personagem = %s"
            cursor.execute(query_info, (id_atual,))
            info = cursor.fetchone()  
            
            imagem = info[0] 
            emoji = info[1]  
            nome = info[2]  
            
            legenda = f"Peixes da especie: <b>{subcategoria}</b>\n\n{emoji} {id_atual} - {nome}\n\nPersonagem {pagina_atual} de {total_ids}"
            
            markup = criar_botao_pagina_peixes(call.message, subcategoria, pagina_atual)
            
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=telebot.types.InputMediaPhoto(imagem, caption=legenda,parse_mode="HTML"), reply_markup=markup)
        
        else:
            bot.answer_callback_query(call.id, text="ID não encontrado.")
    
    except Exception as e:
        print(f"Erro ao processar callback 'img' de peixes: {e}")

def mostrar_lista_peixes(message, subcategoria):
    try:
        conn, cursor = conectar_banco_dados()

        subcategoria_like = f"%{subcategoria}%"
        query_subcategoria = "SELECT subcategoria FROM personagens WHERE subcategoria LIKE %s LIMIT 1"
        cursor.execute(query_subcategoria, (subcategoria_like,))
        subcategoria_encontrada = cursor.fetchone()

        if subcategoria_encontrada:
            subcategoria = subcategoria_encontrada[0]
            
            query_personagens = "SELECT id_personagem, nome, emoji FROM personagens WHERE subcategoria = %s"
            cursor.execute(query_personagens, (subcategoria,))
            peixes_personagens = cursor.fetchall()

            query_evento = "SELECT id_personagem, nome, emoji FROM evento WHERE subcategoria = %s"
            cursor.execute(query_evento, (subcategoria,))
            peixes_evento = cursor.fetchall()

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
        else:
            bot.reply_to(message, f"Nenhuma subcategoria correspondente encontrada para '{subcategoria}'.")

    except Exception as e:
        print(f"Erro ao processar comando /peixes: {e}")
        bot.reply_to(message, "Ocorreu um erro ao processar sua solicitação.")

def criar_markup_peixes(pagina_atual, total_paginas, subcategoria):
    markup = telebot.types.InlineKeyboardMarkup()

    markup.row(
        telebot.types.InlineKeyboardButton(text="⏪️", callback_data=f"peixes_1_{subcategoria}"),
        telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f"peixes_{pagina_atual-1}_{subcategoria}"),
        telebot.types.InlineKeyboardButton(text="➡️", callback_data=f"peixes_{pagina_atual+1}_{subcategoria}"),
        telebot.types.InlineKeyboardButton(text="⏪️", callback_data=f"peixes_{total_paginas}_{subcategoria}")
    )

    return markup

def pagina_peixes_callback(call, pagina, subcategoria):
    try:
        conn, cursor = conectar_banco_dados()
        
        query_personagens = "SELECT id_personagem, nome, emoji FROM personagens WHERE subcategoria = %s"
        cursor.execute(query_personagens, (subcategoria,))
        peixes_personagens = cursor.fetchall()

        query_evento = "SELECT id_personagem, nome, emoji FROM evento WHERE subcategoria = %s"
        cursor.execute(query_evento, (subcategoria,))
        peixes_evento = cursor.fetchall()

        peixes = peixes_personagens + peixes_evento
        paginas = dividir_em_paginas(peixes, 15)
        
        if pagina in paginas:
            resposta = f"<i>Peixes da espécie</i> <b>{subcategoria}</b>:\n\n"
            for peixe in paginas[pagina]:
                id_personagem, nome, emoji = peixe
                resposta += f"{emoji} <code>{id_personagem}</code> - {nome}\n"
            
            resposta += f"\nPágina <b>{pagina}</b>/{len(paginas)}"
            markup = criar_markup_peixes(pagina, len(paginas), subcategoria)
            
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, text="Página não encontrada.")
    except Exception as e:
        print(f"Erro ao processar callback de página de peixes: {e}")

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

        if len(message.text.split()) < 3:
            bot.reply_to(message, "Formato incorreto. Use /enviar_mensagem <id_usuario> <sua_mensagem>")
            return

        _, user_id, *mensagem = message.text.split(maxsplit=2)
        user_id = int(user_id)
        mensagem = mensagem[0]

        bot.send_message(user_id, mensagem)
        
        bot.reply_to(message, f"Mensagem enviada para o usuário {user_id} com sucesso!")
        
    except ValueError:
        bot.reply_to(message, "ID de usuário inválido. Certifique-se de fornecer um número inteiro válido.")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        bot.reply_to(message, "Ocorreu um erro ao enviar a mensagem.")

@bot.message_handler(commands=['enviar_grupo'])
def enviar_mensagem_grupo(message):
    try:

        if len(message.text.split()) < 3:
            bot.reply_to(message, "Formato incorreto. Use /enviar_grupo <id_grupo> <sua_mensagem>")
            return
        
        _, group_id, *mensagem = message.text.split(maxsplit=2)
        group_id = int(group_id)
        mensagem = mensagem[0]

        bot.send_message(group_id, mensagem)

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

            print(f"Erro ao verificar subcategoria na tabela de eventos: {e}")
    except Exception as e:
        return None



def get_random_subcategories_all_valentine(connection):
    cursor = connection.cursor()
    query = "SELECT DISTINCT subcategoria FROM evento WHERE evento = 'amor' ORDER BY RAND() LIMIT 2"
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

def verificar_e_cenourar_carta(message):
    try:
        conn, cursor = conectar_banco_dados()
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
        fechar_conexao(cursor, conn)


def cenourar_carta(call, id_usuario, id_personagens):
    try:
        conn, cursor = conectar_banco_dados()
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
user_data = {}
def encontrar_subcategoria_proxima(subcategoria):
    try:
        conn, cursor = conectar_banco_dados()

        query = "SELECT subcategoria FROM personagens WHERE subcategoria LIKE %s LIMIT 1"
        cursor.execute(query, (f"%{subcategoria}%",))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            return None

    except Exception as e:
        print(f"Erro ao encontrar subcategoria mais próxima: {e}")
        return None

    finally:
        fechar_conexao(cursor, conn)
        
def get_random_subcategories_all_valentine(connection):
    cursor = connection.cursor()

    query = "SELECT subcategoria FROM evento WHERE evento = 'amor' ORDER BY RAND() LIMIT 2"
    cursor.execute(query)
    subcategories_valentine = [row[0] for row in cursor.fetchall()]

    cursor.close()

    return subcategories_valentine

def categoria_handler(message, categoria):
    try:
        conn, cursor = conectar_banco_dados()

        chat_id = message.chat.id 
        evento_ativo = False
        chance_evento = random.random()

        if categoria.lower() == 'geral':   # Se a categoria não for 'Geral', proceda com a lógica normal da tabela de personagens
            subcategorias = buscar_subcategorias(categoria)
            subcategorias = [subcategoria for subcategoria in subcategorias if subcategoria]

            if subcategorias:
                resposta_texto = "Sua isca atraiu 6 espécies, qual peixe você vai levar?\n\n"
                subcategorias_aleatorias = random.sample(subcategorias, min(6, len(subcategorias)))

                for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                        resposta_texto += f"{i}\uFE0F\u20E3 - {subcategoria}\n"

                markup = telebot.types.InlineKeyboardMarkup(row_width=6)

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
                resposta_texto = "Sua isca atraiu 6 espécies, qual peixe você vai levar?\n\n"
                subcategorias_aleatorias = random.sample(subcategorias, min(6, len(subcategorias)))

                for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                    resposta_texto += f"{i}\uFE0F\u20E3 - {subcategoria}\n"

                markup = telebot.types.InlineKeyboardMarkup(row_width=6)

                row_buttons = []
                for i, subcategoria in enumerate(subcategorias_aleatorias, start=1):
                    button_text = f"{i}\uFE0F\u20E3"
                    chat_id=message.chat.id
                    message_id=message.message_id
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
            return None

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
        conn, cursor = conectar_banco_dados()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO historico_cartas_giradas (id_usuario, id_carta, data_hora) VALUES (%s, %s, %s)",
                       (id_usuario, id_carta, data_hora))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao registrar o histórico da carta: {err}")
    finally:
        fechar_conexao(cursor, conn)

        
def encontrar_categoria_proxima(subcategoria):
    try:
        conn, cursor = conectar_banco_dados()

        query = "SELECT categoria FROM personagens WHERE categoria LIKE %s LIMIT 1"
        cursor.execute(query, (f"%{subcategoria}%",))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]
        else:
            return None

    except Exception as e:
        print(f"Erro ao encontrar subcategoria mais próxima: {e}")
        return None

    finally:
        fechar_conexao(cursor, conn)


def mostrar_pagina_cesta_s(message, subcategoria, id_usuario, pagina_atual, total_paginas, ids_personagens, total_personagens_subcategoria, nome_usuario, call=None):
    try:
        conn, cursor = conectar_banco_dados()

        ids_personagens = sorted([str(id) for id in ids_personagens], key=int)
        cursor.execute("SELECT Imagem FROM subcategorias WHERE subcategoria = %s", (subcategoria,))
        resultado_imagem = cursor.fetchone()
        imagem_subcategoria = resultado_imagem[0] if resultado_imagem else None
        offset = (pagina_atual - 1) * 15
        ids_pagina = ids_personagens[offset:offset + 15]

        resposta = f"☀️ Peixes na cesta de {nome_usuario}! A recompensa de uma jornada dedicada à pesca.\n\n"
        resposta += f"🧺 | {subcategoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {len(ids_personagens)}/{total_personagens_subcategoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome = consultar_informacoes_personagem(id_personagem)
            quantidade_cartas = obter_quantidade_cartas_usuario(id_usuario, id_personagem)
            resposta += f"{emoji} {id_personagem} • {nome} {adicionar_quantidade_cartas(quantidade_cartas)} \n"

        markup = None
        if total_paginas > 1:
            markup = criar_markup_cesta(pagina_atual, total_paginas, subcategoria, 's', id_usuario)

        if call:
            if imagem_subcategoria:
                bot.edit_message_media(media=telebot.types.InputMediaPhoto(imagem_subcategoria, caption=resposta, parse_mode="HTML"), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            if imagem_subcategoria:
                bot.send_photo(message.chat.id, imagem_subcategoria, caption=resposta, reply_markup=markup, parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

    except Exception as e:
        print(f"Erro ao mostrar página da cesta: {e}")
    finally:
        fechar_conexao(cursor, conn)


def mostrar_pagina_cesta_f(message, subcategoria, id_usuario, pagina_atual, total_paginas, ids_personagens_faltantes, total_personagens_subcategoria, nome_usuario, call=None):
    try:
        conn, cursor = conectar_banco_dados()
        ids_personagens_faltantes = sorted([str(id) for id in ids_personagens_faltantes], key=int)
        cursor.execute("SELECT Imagem FROM subcategorias WHERE subcategoria = %s", (subcategoria,))
        resultado_imagem = cursor.fetchone()
        imagem_subcategoria = resultado_imagem[0] if resultado_imagem else None

        offset = (pagina_atual - 1) * 15
        ids_pagina = ids_personagens_faltantes[offset:offset + 15]

        resposta = f"🌧️ A cesta de {nome_usuario} não está completa, mas o rio ainda tem muitos segredos!\n\n"
        resposta += f"🧺 | {subcategoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {total_personagens_subcategoria - len(ids_personagens_faltantes)}/{total_personagens_subcategoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome = consultar_informacoes_personagem(id_personagem)
            resposta += f"{emoji} {id_personagem} • {nome}\n"

        markup = None
        if total_paginas > 1:
            markup = criar_markup_cesta(pagina_atual, total_paginas, subcategoria, 'f', id_usuario)

        if call:
            if imagem_subcategoria:
                bot.edit_message_media(media=telebot.types.InputMediaPhoto(imagem_subcategoria, caption=resposta, parse_mode="HTML"), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            if imagem_subcategoria:
                bot.send_photo(message.chat.id, imagem_subcategoria, caption=resposta, reply_markup=markup, parse_mode="HTML")
            else:
                bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

    except Exception as e:
        print(f"Erro ao mostrar página da cesta: {e}")
    finally:
        fechar_conexao(cursor, conn)


def mostrar_pagina_cesta_c(message, categoria, id_usuario, pagina_atual, total_paginas, ids_personagens, total_personagens_categoria, nome_usuario, call=None):
    try:
        conn, cursor = conectar_banco_dados()

        ids_personagens.sort()

        offset = (pagina_atual - 1) * 15
        ids_pagina = ids_personagens[offset:offset + 15]

        resposta = f"🌧️ A cesta de {nome_usuario} não está completa, mas o rio ainda tem muitos segredos!\n\n"
        resposta += f"🧺 | {categoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {len(ids_personagens)}/{total_personagens_categoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome = consultar_informacoes_personagem(id_personagem)
            resposta += f"{emoji} {id_personagem} • {nome}\n"

        markup = None
        if total_paginas > 1:
            markup = criar_markup_cesta(pagina_atual, total_paginas, categoria, 'c',id_usuario)

        if call:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

    except Exception as e:
        print(f"Erro ao mostrar página da cesta: {e}")
    finally:
        fechar_conexao(cursor, conn)

def mostrar_pagina_cesta_cf(message, categoria, id_usuario, pagina_atual, total_paginas, ids_personagens, total_personagens_categoria, nome_usuario, call=None):
    try:
        conn, cursor = conectar_banco_dados()

        ids_personagens.sort()

        offset = (pagina_atual - 1) * 15
        ids_pagina = ids_personagens[offset:offset + 15]

        resposta = f"🌧️ Peixes da espécie {categoria} que faltam na cesta de {nome_usuario}:\n\n"
        resposta += f"🧺 | {categoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {total_personagens_categoria - len(ids_personagens)}/{total_personagens_categoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome = consultar_informacoes_personagem(id_personagem)
            resposta += f"{emoji} {id_personagem} • {nome}\n"

        markup = None
        if total_paginas > 1:
            markup = criar_markup_cesta(pagina_atual, total_paginas, categoria, 'cf',id_usuario)

        if call:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

    except Exception as e:
        print(f"Erro ao mostrar página da cesta: {e}")

    finally:
        fechar_conexao(cursor, conn)


def obter_ids_personagens_inventario(id_usuario, subcategoria):
    conn, cursor = conectar_banco_dados()
    try:
        query = """
        SELECT inv.id_personagem
        FROM inventario inv
        JOIN personagens per ON inv.id_personagem = per.id_personagem
        WHERE inv.id_usuario = %s AND per.subcategoria = %s
        """
        cursor.execute(query, (id_usuario, subcategoria))
        ids_personagens = [row[0] for row in cursor.fetchall()]
        return ids_personagens
    finally:
        fechar_conexao(cursor, conn)


def obter_ids_personagens_faltantes(id_usuario, subcategoria):
    conn, cursor = conectar_banco_dados()
    try:
        query = """
        SELECT per.id_personagem
        FROM personagens per
        WHERE per.subcategoria = %s AND per.id_personagem NOT IN (
            SELECT inv.id_personagem
            FROM inventario inv
            WHERE inv.id_usuario = %s
        )
        """
        cursor.execute(query, (subcategoria, id_usuario))
        ids_personagens_faltantes = [row[0] for row in cursor.fetchall()]
        return ids_personagens_faltantes
    finally:
        fechar_conexao(cursor, conn)


def obter_ids_personagens_faltantes_categoria(id_usuario, categoria):
    conn, cursor = conectar_banco_dados()
    query = """
    SELECT id_personagem 
    FROM personagens 
    WHERE categoria = %s AND id_personagem NOT IN (
        SELECT id_personagem 
        FROM inventario 
        WHERE id_usuario = %s
    )
    """
    cursor.execute(query, (categoria, id_usuario))
    ids_personagens = [row[0] for row in cursor.fetchall()]
    fechar_conexao(cursor, conn)
    return ids_personagens

def obter_total_personagens_categoria(categoria):
    conn, cursor = conectar_banco_dados()
    query = "SELECT COUNT(*) FROM personagens WHERE categoria = %s"
    cursor.execute(query, (categoria,))
    total_personagens = cursor.fetchone()[0]
    fechar_conexao(cursor, conn)
    return total_personagens

def obter_total_personagens_subcategoria(subcategoria):
    conn, cursor = conectar_banco_dados()
    try:
        query = """
        SELECT COUNT(*)
        FROM personagens
        WHERE subcategoria = %s
        """
        cursor.execute(query, (subcategoria,))
        total_personagens = cursor.fetchone()[0]
        return total_personagens
    finally:
        fechar_conexao(cursor, conn)


def obter_ids_personagens_evento(id_usuario, subcategoria, incluir=True):
    conn, cursor = conectar_banco_dados()
    try:
        if incluir:
            query = """
            SELECT ev.id_personagem 
            FROM evento ev
            WHERE ev.subcategoria = %s AND ev.id_personagem NOT IN (
                SELECT inv.id_personagem 
                FROM inventario inv
                WHERE inv.id_usuario = %s
            )
            """
        else:
            query = """
            SELECT ev.id_personagem 
            FROM evento ev
            WHERE ev.subcategoria = %s AND ev.id_personagem IN (
                SELECT inv.id_personagem 
                FROM inventario inv
                WHERE inv.id_usuario = %s
            )
            """
        cursor.execute(query, (subcategoria, id_usuario))
        ids_personagens = [row[0] for row in cursor.fetchall()]
        return ids_personagens
    finally:
        fechar_conexao(cursor, conn)

def criar_markup_cesta(pagina_atual, total_paginas, subcategoria, tipo, id_usuario_original):
    markup = telebot.types.InlineKeyboardMarkup()

    # Navegação circular
    pagina_anterior = total_paginas if pagina_atual == 1 else pagina_atual - 1
    pagina_proxima = 1 if pagina_atual == total_paginas else pagina_atual + 1


    markup.row(
        telebot.types.InlineKeyboardButton(text="⏪️", callback_data=f"cesta_{tipo}_1_{subcategoria}_{id_usuario_original}"),
        telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f"cesta_{tipo}_{pagina_anterior}_{subcategoria}_{id_usuario_original}"),
        telebot.types.InlineKeyboardButton(text="➡️", callback_data=f"cesta_{tipo}_{pagina_proxima}_{subcategoria}_{id_usuario_original}"),
        telebot.types.InlineKeyboardButton(text="⏩️", callback_data=f"cesta_{tipo}_{total_paginas}_{subcategoria}_{id_usuario_original}")
    )

    return markup

def obter_ids_personagens_categoria(id_usuario, categoria):
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT id_personagem FROM inventario WHERE id_usuario = %s AND id_personagem IN (SELECT id_personagem FROM personagens WHERE categoria = %s)", (id_usuario, categoria))
    ids_personagens = [row[0] for row in cursor.fetchall()]
    fechar_conexao(cursor, conn)
    return ids_personagens

def obter_total_personagens_categoria(categoria):
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT COUNT(*) FROM personagens WHERE categoria = %s", (categoria,))
    total = cursor.fetchone()[0]
    fechar_conexao(cursor, conn)
    return total

def encontrar_categoria_proxima(categoria):
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT DISTINCT categoria FROM personagens WHERE categoria LIKE %s", (f"%{categoria}%",))
    resultado = cursor.fetchone()
    fechar_conexao(cursor, conn)
    return resultado[0] if resultado else None

def consultar_informacoes_personagem(id_personagem):
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT emoji, nome FROM personagens WHERE id_personagem = %s", (id_personagem,))
    resultado = cursor.fetchone()
    fechar_conexao(cursor, conn)
    return resultado if resultado else ("", "Desconhecido")

def consultar_informacoes_personagem(id_personagem):
    conn, cursor = conectar_banco_dados()
    try:

        query = "SELECT emoji, nome FROM personagens WHERE id_personagem = %s"
        cursor.execute(query, (id_personagem,))
        resultado = cursor.fetchone()

        if not resultado:
            query_evento = "SELECT emoji, nome FROM evento WHERE id_personagem = %s"
            cursor.execute(query_evento, (id_personagem,))
            resultado = cursor.fetchone()


        if not resultado:
            return "❓", "Desconhecido"
        
        return resultado[0], resultado[1]
    except Exception as e:
        print(f"Erro ao consultar informações do personagem: {e}")
        return "❓", "Desconhecido"
    finally:
        fechar_conexao(cursor, conn)

def adicionar_quantidade_cartas(quantidade_carta):
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
    elif quantidade_carta >= 50:
        letra_quantidade = "👑"
    else:
        letra_quantidade = ""
    
    return letra_quantidade
def obter_quantidade_cartas_usuario(id_usuario, id_personagem):
    try:
        conn, cursor = conectar_banco_dados()

        query = """
        SELECT quantidade 
        FROM inventario 
        WHERE id_usuario = %s AND id_personagem = %s
        """
        cursor.execute(query, (id_usuario, id_personagem))
        resultado = cursor.fetchone()

        if resultado:
            quantidade = resultado[0]
        else:
            quantidade = 0

    except Exception as e:
        print(f"Erro ao obter quantidade de cartas: {e}")
        quantidade = 0

    finally:
        fechar_conexao(cursor, conn)

    return quantidade
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
            UNION
            SELECT e.id_personagem, e.emoji, e.nome AS nome_personagem, e.subcategoria, 0 AS quantidade, e.categoria, e.imagem
            FROM evento e
            WHERE e.id_personagem = (
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
        conn = mysql.connector.connect(**db_config())  
        cursor = conn.cursor()

        query = "SELECT nome FROM usuarios WHERE id_usuario = %s"
        cursor.execute(query, (id_usuario,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]  
        else:
            return None  

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
        return subcategorias_similares[0] if subcategorias_similares else None 
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
        return True  
    
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

        
def adicionar_iscas(id_usuario, quantidade,message):

    try:
        conn, cursor = conectar_banco_dados()

        query_atualizar_iscas = """
            UPDATE usuarios
            SET iscas = iscas + %s
            WHERE id_usuario = %s
        """
        cursor.execute(query_atualizar_iscas, (quantidade, id_usuario))
        conn.commit()

        print(f"Iscas adicionadas com sucesso para o usuário com ID {id_usuario}")
        nova_mensagem = f"🎣  A isca pulou de volta pra sua cesta, boa pesca!"
        bot.edit_message_text(chat_id=id_usuario, message_id=message.message_id, text=nova_mensagem)
    except mysql.connector.Error as e:
        print(f"Erro ao adicionar iscas para o usuário: {e}")

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
     
while True:          
    try:
        if __name__ == "__main__":
            bot.polling(none_stop=True)
        else:
            bot.polling()
    except Exception as e:
        import traceback
        traceback.print_exc()
        time.sleep(5)  
