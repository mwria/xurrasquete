from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *

user_data = {}
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

def encontrar_subcategoria_proxima(subcategoria):
    try:
        subcategoria = verificar_apelido(subcategoria)
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

def encontrar_categoria_proxima(categoria):
    try:
        categoria = verificar_apelido(categoria)
        conn, cursor = conectar_banco_dados()
        query = "SELECT categoria FROM personagens WHERE categoria LIKE %s LIMIT 1"
        cursor.execute(query, (f"%{categoria}%",))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0]
        else:
            return None
    except Exception as e:
        print(f"Erro ao encontrar categoria mais próxima: {e}")
        return None
    finally:
        fechar_conexao(cursor, conn)

def mostrar_pagina_cesta_s(message, subcategoria, id_usuario, pagina_atual, total_paginas, ids_personagens, total_personagens_subcategoria, nome_usuario, call=None):
    try:
        subcategoria = verificar_apelido(subcategoria)
        conn, cursor = conectar_banco_dados()

        cursor.execute("SELECT Imagem FROM subcategorias WHERE subcategoria = %s", (subcategoria,))
        resultado_imagem = cursor.fetchone()
        imagem_subcategoria = resultado_imagem[0] if resultado_imagem else None

        offset = (pagina_atual - 1) * 15
        ids_pagina = sorted(ids_personagens, key=lambda id: consultar_informacoes_personagem(id)[1])[offset:offset + 15]

        resposta = f"☀️ Peixes na cesta de {nome_usuario}! A recompensa de uma jornada dedicada à pesca.\n\n"
        resposta += f"🧺 | {subcategoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {len(ids_personagens)}/{total_personagens_subcategoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome = consultar_informacoes_personagem(id_personagem)
            quantidade_cartas = obter_quantidade_cartas_usuario(id_usuario, id_personagem)
            resposta += f"{emoji} <code>{id_personagem}</code> • {nome} {adicionar_quantidade_cartas(quantidade_cartas)} \n"

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
        subcategoria = verificar_apelido(subcategoria)
        conn, cursor = conectar_banco_dados()

        cursor.execute("SELECT Imagem FROM subcategorias WHERE subcategoria = %s", (subcategoria,))
        resultado_imagem = cursor.fetchone()
        imagem_subcategoria = resultado_imagem[0] if resultado_imagem else None

        offset = (pagina_atual - 1) * 15
        ids_pagina = sorted(ids_personagens_faltantes, key=lambda id: consultar_informacoes_personagem(id)[1])[offset:offset + 15]

        resposta = f"🌧️ A cesta de {nome_usuario} não está completa, mas o rio ainda tem muitos segredos!\n\n"
        resposta += f"🧺 | {subcategoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {total_personagens_subcategoria - len(ids_personagens_faltantes)}/{total_personagens_subcategoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome = consultar_informacoes_personagem(id_personagem)
            resposta += f"{emoji} <code>{id_personagem}</code> • {nome}\n"

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
        categoria = verificar_apelido(categoria)
        conn, cursor = conectar_banco_dados()

        # Ordenar os IDs dos personagens por subcategoria e nome do personagem
        ids_personagens.sort(key=lambda id: (consultar_informacoes_personagem_com_subcategoria(id)[2], consultar_informacoes_personagem_com_subcategoria(id)[1]))

        offset = (pagina_atual - 1) * 15
        ids_pagina = ids_personagens[offset:offset + 15]

        resposta = f"🌧️ A cesta de {nome_usuario} não está completa, mas o rio ainda tem muitos segredos!\n\n"
        resposta += f"🧺 | {categoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {len(ids_personagens)}/{total_personagens_categoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome, subcategoria = consultar_informacoes_personagem_com_subcategoria(id_personagem)
            resposta += f"{emoji} <code>{id_personagem}</code> • {nome} - {subcategoria}\n"

        markup = None
        if total_paginas > 1:
            markup = criar_markup_cesta(pagina_atual, total_paginas, categoria, 'c', id_usuario)

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
        categoria = verificar_apelido(categoria)
        conn, cursor = conectar_banco_dados()

        # Ordenar os IDs dos personagens por subcategoria e nome do personagem
        ids_personagens.sort(key=lambda id: (consultar_informacoes_personagem_com_subcategoria(id)[2], consultar_informacoes_personagem_com_subcategoria(id)[1]))

        offset = (pagina_atual - 1) * 15
        ids_pagina = ids_personagens[offset:offset + 15]

        resposta = f"🌧️ Peixes da espécie {categoria} que faltam na cesta de {nome_usuario}:\n\n"
        resposta += f"🧺 | {categoria}\n"
        resposta += f"📄 | {pagina_atual}/{total_paginas}\n"
        resposta += f"🐟 | {total_personagens_categoria - len(ids_personagens)}/{total_personagens_categoria}\n\n"

        for id_personagem in ids_pagina:
            emoji, nome, subcategoria = consultar_informacoes_personagem_com_subcategoria(id_personagem)
            resposta += f"{emoji}<code> {id_personagem}</code> • {nome} - {subcategoria}\n"

        markup = None
        if total_paginas > 1:
            markup = criar_markup_cesta(pagina_atual, total_paginas, categoria, 'cf', id_usuario)

        if call:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=resposta, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, resposta, reply_markup=markup, parse_mode="HTML")

    except Exception as e:
        print(f"Erro ao mostrar página da cesta: {e}")
    finally:
        fechar_conexao(cursor, conn)

def consultar_informacoes_personagem_com_subcategoria(id_personagem):
    conn, cursor = conectar_banco_dados()
    try:
        query = "SELECT emoji, nome, subcategoria FROM personagens WHERE id_personagem = %s"
        cursor.execute(query, (id_personagem,))
        resultado = cursor.fetchone()
        if not resultado:
            query_evento = "SELECT emoji, nome, subcategoria FROM evento WHERE id_personagem = %s"
            cursor.execute(query_evento, (id_personagem,))
            resultado = cursor.fetchone()
        if not resultado:
            return "❓", "Desconhecido", "Desconhecida"
        return resultado[0], resultado[1], resultado[2]
    except Exception as e:
        print(f"Erro ao consultar informações do personagem: {e}")
        return "❓", "Desconhecido", "Desconhecida"
    finally:
        fechar_conexao(cursor, conn)


def obter_ids_personagens_inventario(id_usuario, subcategoria):
    subcategoria = verificar_apelido(subcategoria)
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
    subcategoria = verificar_apelido(subcategoria)
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
    categoria = verificar_apelido(categoria)
    try:
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
    finally:
        fechar_conexao(cursor, conn)

def obter_total_personagens_categoria(categoria):
    categoria = verificar_apelido(categoria)
    try:
        conn, cursor = conectar_banco_dados()
        query = "SELECT COUNT(*) FROM personagens WHERE categoria = %s"
        cursor.execute(query, (categoria,))
        total_personagens = cursor.fetchone()[0]
        return total_personagens
    finally:
        fechar_conexao(cursor, conn)

def obter_total_personagens_subcategoria(subcategoria):
    subcategoria = verificar_apelido(subcategoria)
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
    subcategoria = verificar_apelido(subcategoria)
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

    # Botões de navegação na mesma linha
    markup.row(
        telebot.types.InlineKeyboardButton(text="⏪️", callback_data=f"cesta_{tipo}_1_{subcategoria}_{id_usuario_original}"),
        telebot.types.InlineKeyboardButton(text="⬅️", callback_data=f"cesta_{tipo}_{pagina_anterior}_{subcategoria}_{id_usuario_original}"),
        telebot.types.InlineKeyboardButton(text="➡️", callback_data=f"cesta_{tipo}_{pagina_proxima}_{subcategoria}_{id_usuario_original}"),
        telebot.types.InlineKeyboardButton(text="⏩️", callback_data=f"cesta_{tipo}_{total_paginas}_{subcategoria}_{id_usuario_original}")
    )

    return markup

def obter_ids_personagens_categoria(id_usuario, categoria):
    categoria = verificar_apelido(categoria)
    try:
        conn, cursor = conectar_banco_dados()
        cursor.execute("SELECT id_personagem FROM inventario WHERE id_usuario = %s AND id_personagem IN (SELECT id_personagem FROM personagens WHERE categoria = %s)", (id_usuario, categoria))
        ids_personagens = [row[0] for row in cursor.fetchall()]
        return ids_personagens
    finally:
        fechar_conexao(cursor, conn)

def obter_total_personagens_categoria(categoria):
    categoria = verificar_apelido(categoria)
    conn, cursor = conectar_banco_dados()
    cursor.execute("SELECT COUNT(*) FROM personagens WHERE categoria = %s", (categoria,))
    total = cursor.fetchone()[0]
    fechar_conexao(cursor, conn)
    return total

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