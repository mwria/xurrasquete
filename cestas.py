from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *

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

def enviar_resultados_pagina_c(chat_id, message_id, mensagem, pagina_atual, total_paginas, categoria, id_usuario, modo):
    print("passo 5")
    conn, cursor = conectar_banco_dados()
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem, reply_markup=criar_teclado_paginacao_c(pagina_atual, total_paginas, message_id, categoria, id_usuario))


    print("passo 6")
    if modo == 'c':
        mensagem = f"🧺 | Cartas da categoria {categoria} na cesta de {id_usuario}:\n\n"
    else:
        mensagem = ""

    for resultado in resultados_pagina:
        mensagem += resultado[0] + "\n"  # Assumindo que o resultado é uma tupla e o texto está na primeira posição
    
    return mensagem

def criar_teclado_paginacao_c(pagina_atual, total_paginas, mensagem_id, categoria, id_usuario):
    
    markup = telebot.types.InlineKeyboardMarkup()
    botoes = []
    print("passo 3")
    if pagina_atual >1:
        botoes.append(telebot.types.InlineKeyboardButton("⬅️", callback_data=f"vemc_{pagina_atual}_{total_paginas}_{mensagem_id}_{categoria}_{id_usuario}"))
    if pagina_atual < total_paginas:
        botoes.append(telebot.types.InlineKeyboardButton("➡️", callback_data=f"vaic_{pagina_atual}_{total_paginas}_{mensagem_id}_{categoria}_{id_usuario}"))
    markup.row(*botoes)
    return markup

def enviar_resultados_pagina_cesta_c(chat_id, message_id, mensagem, pagina_atual, total_paginas, categoria, id_usuario, modo):
    print("passo 7")
    if mensagem:  # Verifica se a mensagem não está vazia
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem, reply_markup=criar_teclado_paginacao_c(pagina_atual, total_paginas, message_id, categoria, id_usuario, modo))
        except Exception as e:
            print("Erro ao enviar resultados da página:", e)
    else:
        print("Erro: Mensagem vazia. Não foi possível enviar os resultados da página.")
  #conn, cursor = conectar_banco_dados()      
import json

def registrar_cartas_cesta_f(usuario, subcategoria, resposta_completa, modo='f'):
    conn, cursor = conectar_banco_dados()      

    # Ajustar a subcategoria para buscar subcategorias semelhantes na tabela personagens
    subcategoria_palavras = subcategoria.strip().split(' ')
    print(subcategoria_palavras)
    subcategoria_pesquisada = ' '.join(subcategoria_palavras[1:]).title()
    subcategoria_excluir = ' '.join(subcategoria_palavras[:]).title()
    subcategoria_like = f'{modo} {subcategoria_pesquisada}'
    print(subcategoria_like)

    # Excluir os registros existentes para o usuário e subcategoria
    sql_excluir_cartas = """
        DELETE FROM temp_cartas
        WHERE id_usuario = %s AND subcategoria = %s
    """
    try:
        cursor.execute(sql_excluir_cartas, (usuario, subcategoria_excluir))
        conn.commit()
        print("Registros antigos excluídos com sucesso.")
    except Exception as e:
        print("Erro ao excluir registros antigos:", e)
    
    # Consultar a tabela personagens para encontrar subcategorias semelhantes
    sql_consultar_subcategorias = """
        SELECT DISTINCT(subcategoria)
        FROM personagens
        WHERE subcategoria LIKE %s
    """
    try:
        cursor.execute(sql_consultar_subcategorias, (f'%{subcategoria_pesquisada}%',))
        subcategorias_similares = cursor.fetchall()
        print("Subcategorias similares encontradas:", subcategorias_similares)
    except Exception as e:
        print("Erro ao consultar subcategorias:", e)
        subcategorias_similares = []

    # Inserir os registros na tabela temp_cartas usando subcategorias similares
    for sub in subcategorias_similares:
        subcategoria_like = f'{"f"} {sub[0]}'
        print(subcategoria_like)
        cartas = resposta_completa
        print(cartas)
        paginas = [cartas[i:i+15] for i in range(0, len(cartas), 15)]

        for i, pagina in enumerate(paginas, start=1):
            cartas_formatadas = [f"🌼 {carta['id']} — {carta['nome']}" for carta in pagina]
            cartas_texto = '\n'.join(cartas_formatadas)
            pagina_registro = i

            # Verificar se já existe um registro com a mesma chave única na tabela
            sql_verificar_existencia = """
                SELECT COUNT(*)
                FROM temp_cartas
                WHERE id_usuario = %s AND subcategoria = %s AND pagina = %s
            """
            cursor.execute(sql_verificar_existencia, (usuario, subcategoria_like, pagina_registro))
            count = cursor.fetchone()[0]
            if count == 0:
                # Inserir o registro apenas se não existir um registro com a mesma chave única
                sql_inserir_cartas = """
                    INSERT INTO temp_cartas (id_usuario, subcategoria, cartas_json, pagina)
                    VALUES (%s, %s, %s, %s)
                """
                try:
                    cursor.execute(sql_inserir_cartas, (usuario, subcategoria_like, cartas_texto, pagina_registro))
                    print("Página registrada para subcategoria:", subcategoria_like, "-", pagina_registro)
                    conn.commit()
                except Exception as e:
                    print("Erro ao registrar página:", e)

    return len(paginas)

def construir_mensagem_f(cartas, subcategoria_pesquisada, idusuario, modo='f'):
    if not cartas:
        return None

    mensagem = ""
    for carta in cartas:
        cartas_json = carta['cartas_json']
        cartas_decodificadas = json.loads(cartas_json)
        for carta_info in cartas_decodificadas:
            emoji_carta = carta_info['emoji']
            id_carta = carta_info['id']
            nome_carta = carta_info['nome']
            mensagem += f"{emoji_carta} {id_carta} — {nome_carta}\n"

    return mensagem

def enviar_faltante_inicial(chat_id, mensagem, total_paginas, subcategoria_pesquisada, nome_usuario, message):
    conn, cursor = conectar_banco_dados()
    subcategoria = subcategoria_pesquisada
    idusuario = nome_usuario
    pagina_atual = 1
    mensagem_id = gerar_id_unico()
    foto_subcategoria = obter_foto_subcategoria(subcategoria, cursor)
    user_data[mensagem_id] = {"texto": mensagem, "chat_id": chat_id}
    resultados_pagina = obter_resultados_pagina_f(subcategoria, pagina_atual, idusuario)
    print("resultado", resultados_pagina)

    texto_formatado = construir_mensagem_f(resultados_pagina, subcategoria_pesquisada, idusuario, modo='f')
    print(texto_formatado)
    if not texto_formatado:  # Verifica se o texto formatado está vazio
        print("Nenhum resultado encontrado.")
        return  # Não envia a mensagem se não houver resultados

    mensagem_legenda = f"🧺 | Cartas de {subcategoria_pesquisada} na cesta de {nome_usuario}:\n\n{texto_formatado}"

    if foto_subcategoria:
        bot.send_photo(chat_id, foto_subcategoria, caption=mensagem_legenda,
                       reply_markup=criar_teclado_paginacao(pagina_atual, total_paginas, mensagem_id, subcategoria,
                                                            nome_usuario, modo='s'))
    else:
        bot.send_message(chat_id, mensagem_legenda,
                         reply_markup=criar_teclado_paginacao(pagina_atual, total_paginas, mensagem_id, subcategoria,
                                                              nome_usuario, modo='s'),
                         reply_to_message_id=message.message_id, parse_mode="HTML")

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
        
def obter_resultados_faltante(subcategoria, numero_pagina, id_usuario):
    subcategoria_com_prefixo = "f " + subcategoria
    conn, cursor = conectar_banco_dados()
    try:
        cursor.execute("SELECT cartas_json FROM temp_cartas WHERE subcategoria = %s AND pagina = %s AND id_usuario = %s", (subcategoria_com_prefixo, numero_pagina, id_usuario))
        resultados = cursor.fetchall()
        return resultados
    finally:
        fechar_conexao(cursor, conn)
        
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

def enviar_resultados_pagina_c(chat_id, message_id, mensagem, pagina_atual, total_paginas, categoria, id_usuario, modo):
    print("passo 5")
    conn, cursor = conectar_banco_dados()
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem, reply_markup=criar_teclado_paginacao_c(pagina_atual, total_paginas, message_id, categoria, id_usuario))

def construir_mensagem_cesta_c(resultados_pagina, categoria, id_usuario, modo):
    print("passo 6")
    if modo == 'c':
        mensagem = f"🧺 | Cartas da categoria {categoria} na cesta de {id_usuario}:\n\n"
    else:
        mensagem = ""

    for resultado in resultados_pagina:
        mensagem += resultado[0] + "\n"  # Assumindo que o resultado é uma tupla e o texto está na primeira posição
    
    return mensagem
def criar_teclado_paginacao_c(pagina_atual, total_paginas, mensagem_id, categoria, id_usuario):
    
    markup = telebot.types.InlineKeyboardMarkup()
    botoes = []
    print("passo 3")
    if pagina_atual >1:
        botoes.append(telebot.types.InlineKeyboardButton("⬅️", callback_data=f"vemc_{pagina_atual}_{total_paginas}_{mensagem_id}_{categoria}_{id_usuario}"))
    if pagina_atual < total_paginas:
        botoes.append(telebot.types.InlineKeyboardButton("➡️", callback_data=f"vaic_{pagina_atual}_{total_paginas}_{mensagem_id}_{categoria}_{id_usuario}"))
    markup.row(*botoes)
    return markup

def enviar_resultados_pagina_cesta_c(chat_id, message_id, mensagem, pagina_atual, total_paginas, categoria, id_usuario, modo):
    print("passo 7")
    if mensagem:  # Verifica se a mensagem não está vazia
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=mensagem, reply_markup=criar_teclado_paginacao_c(pagina_atual, total_paginas, message_id, categoria, id_usuario, modo))
        except Exception as e:
            print("Erro ao enviar resultados da página:", e)
    else:
        print("Erro: Mensagem vazia. Não foi possível enviar os resultados da página.")
        
def enviar_mensagem_inicial_cesta_c(chat_id, mensagem, total_paginas, categoria_pesquisada, id_usuario):
    conn, cursor = conectar_banco_dados()
    categoria = categoria_pesquisada
    numero_pagina = 1
    mensagem_id = gerar_id_unico()
    pagina_atual = 1
    user_data[mensagem_id] = {"texto": mensagem, "chat_id": chat_id}
    resultados_pagina = obter_resultados_pagina_c(categoria, numero_pagina, id_usuario)
    print(resultados_pagina)
    modo = "c"
    texto_formatado = construir_mensagem_cesta_c(resultados_pagina, categoria, id_usuario, modo)  # Modo 's' para categoria
    print(texto_formatado)
    print("passo 2")
    if not texto_formatado:  # Verifica se o texto formatado está vazio
        print("Nenhum resultado encontrado.")
        return  # Não envia a mensagem se não houver resultados
    else:
        mensagem_texto = f"\n\n{texto_formatado}"
        bot.send_message(chat_id, mensagem_texto, reply_markup=criar_teclado_paginacao_c(pagina_atual, total_paginas, mensagem_id, categoria, id_usuario))  # Modo 'c' para categoria

def obter_resultados_pagina_c(categoria, numero_pagina, id_usuario):
    print("passo nao sei ")
    conn, cursor = conectar_banco_dados()
    try:
        print(categoria,id_usuario,numero_pagina)
        cursor.execute("SELECT cartas_json FROM temp_categorias WHERE subcategoria = %s AND pagina = %s AND id_usuario = %s", (categoria, numero_pagina, id_usuario))
        resultados = cursor.fetchall()
        return resultados
    finally:
        fechar_conexao(cursor, conn)

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

    # Excluir os registros existentes para o usuário e subcategoria
    sql_excluir_cartas = """
        DELETE FROM temp_cartas
        WHERE id_usuario = %s AND subcategoria LIKE %s
    """
    try:
        cursor.execute(sql_excluir_cartas, (usuario, f'%{subcategoria_like}%'))
        conn.commit()
        print("Registros antigos excluídos com sucesso.")
    except Exception as e:
        print("Erro ao excluir registros antigos:", e)
    
    # Definir subnova antes de acessá-la
    subnova = subcategoria_like.split(' ', 1)[1].strip().title()
    print(subnova)

    # Consultar a tabela personagens para encontrar subcategorias semelhantes
    sql_consultar_subcategorias = """
        SELECT DISTINCT(subcategoria)
        FROM personagens
        WHERE subcategoria LIKE %s
    """
    try:
        cursor.execute(sql_consultar_subcategorias, (f'%{subnova}%',))
        subcategorias_similares = cursor.fetchall()
        print("Subcategorias similares encontradas:", subcategorias_similares)
    except Exception as e:
        print("Erro ao consultar subcategorias:", e)
        subcategorias_similares = []

    # Inserir os registros na tabela temp_cartas usando subcategorias similares
    for sub in subcategorias_similares:
        subcategoria_like = f'{modo} {sub[0]}'
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
                cursor.execute(sql_inserir_cartas, (usuario, subcategoria_like, cartas_json, pagina_registro))
                print("Página registrada para subcategoria:", subcategoria_like, "-", pagina_registro)
                conn.commit()
            except Exception as e:
                print("Erro ao registrar página:", e)

    return len(paginas)

def comando_cesta_s(id_usuario, subcategoria, cursor):
    subcategoria = subcategoria.split(' ', 1)[1].strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    sql = f"""
        SELECT * FROM (
            SELECT p.emoji, p.id_personagem, p.nome AS nome_personagem, p.subcategoria, i.quantidade
            FROM personagens p
            JOIN inventario i ON p.id_personagem = i.id_personagem
            WHERE i.id_usuario = {id_usuario} AND (p.subcategoria LIKE '{subcategoria}%' OR p.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
            UNION ALL
            SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria, i.quantidade
            FROM evento e
            JOIN inventario i ON e.id_personagem = i.id_personagem
            WHERE i.id_usuario = {id_usuario} AND (e.subcategoria LIKE '{subcategoria}%' OR e.subcategoria IN (SELECT nome_certo FROM apelidos WHERE apelido = '{subcategoria}' AND tipo = 'Subcategoria'))
        ) AS combined
        ORDER BY nome_personagem
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

def comando_cesta_f(id_usuario, subcategoria, cursor):
    subcategoria = subcategoria.split(' ', 1)[1].strip().title()
    print("Subcategoria:", subcategoria)  # Log: Verifica o valor da subcategoria recebida

    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)

    sql = f"""
        SELECT * FROM (
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
        ) AS combined
        ORDER BY id_personagem DESC
    """

    cursor.execute(sql)
    resultados = cursor.fetchall()

    if resultados:
        lista_cartas = []
        for carta in resultados:
            emoji_carta = carta[0]
            id_carta = formatar_id(carta[1])  # Formata o id_personagem
            nome_carta = carta[2]
            subcategoria_carta = carta[3].title()
            lista_cartas.append({"emoji": emoji_carta, "id": id_carta, "nome": nome_carta})

        print("Cartas encontradas:", lista_cartas)  # Log: Lista as cartas encontradas
        registrar_cartas_cesta_f(id_usuario, subcategoria, lista_cartas, modo='f')
        return lista_cartas, subcategoria
    
    else:
        mensagem = f"☀️ Nada como a alegria de ter todos os peixes de {subcategoria} na cesta!"
        print("Mensagem:", mensagem)  # Log: Exibe a mensagem quando não há cartas encontradas
        return mensagem


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
