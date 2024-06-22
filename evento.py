from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *
from inventario import *

from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *
from inventario import *
from gif import *


def comando_evento_s(id_usuario, evento, subcategoria, cursor, usuario):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    
    sql_usuario = """
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        JOIN inventario i ON e.id_personagem = i.id_personagem
        WHERE i.id_usuario = %s AND e.evento = %s
        ORDER BY e.id_personagem ASC
    """
    cursor.execute(sql_usuario, (id_usuario, evento))
    resultados_usuario = cursor.fetchall()
    
    if resultados_usuario:
        lista_cartas = ""
        for carta in resultados_usuario:
            id_carta, emoji_carta, nome_carta, subcategoria_carta = carta[1], carta[0], carta[2], carta[3].title()
            lista_cartas += f"{emoji_carta} {formatar_id(id_carta)} — {nome_carta}\n"
        resposta = f"🌾 | Cartas do evento {evento} no inventário de {usuario}:\n\n{lista_cartas}"
        return subcategoria_carta, resposta
    return f"🌧 Sem cartas de {subcategoria} no evento {evento}! A jornada continua..."

def comando_evento_f(id_usuario, evento, subcategoria, cursor, usuario):
    subcategoria = subcategoria.strip().title()
    def formatar_id(id_personagem):
        return str(id_personagem).zfill(4)
    
    sql_faltantes = """
        SELECT e.emoji, e.id_personagem, e.nome AS nome_personagem, e.subcategoria
        FROM evento e
        WHERE e.evento = %s 
          AND NOT EXISTS (
              SELECT 1
              FROM inventario i
              WHERE i.id_usuario = %s AND i.id_personagem = e.id_personagem
          )
    """
    cursor.execute(sql_faltantes, (evento, id_usuario))
    resultados_faltantes = cursor.fetchall()

    if resultados_faltantes:
        lista_cartas = ""
        for carta in resultados_faltantes:
            id_carta, emoji_carta, nome_carta, subcategoria_carta = carta[1], carta[0], carta[2], carta[3].title()
            lista_cartas += f"{emoji_carta} {formatar_id(id_carta)} — {nome_carta}\n"
        resposta = f"☀️ | Cartas do evento {evento} que não estão no inventário de {usuario}:\n\n{lista_cartas}"
        return subcategoria_carta, resposta
    return f"☀️ Nada como a alegria de ter todas as cartas de {subcategoria} no evento {evento} na cesta!"

bot.polling()
