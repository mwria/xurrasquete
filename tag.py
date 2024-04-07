from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from sub import get_personagem_by_id

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