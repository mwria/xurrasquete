from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from cestas import *
from tag import *
from gift import *
from evento import *
from callbacks import *
from operacoes import *
from sub import *
from armazem import *
from wish import *
from cenourar import *
from pescar import *
from trocas import *
from gif import *
def loja_geral_callback(call):
    try:
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
        conn, cursor = conectar_banco_dados()
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
                        conn, cursor = conectar_banco_dados()
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

