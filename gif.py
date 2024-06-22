from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *
from operacoes import *
from inventario import *

def verifica_tempo_ultimo_gif(id_usuario):
    try:
        query_ultimo_gif = f"""
            SELECT MAX(data) AS ultima_data, MAX(horario) AS ultima_hora 
            FROM logs 
            WHERE id_usuario = {id_usuario} AND ação = 'gif'
        """
        conn, cursor = conectar_banco_dados()
        cursor.execute(query_ultimo_gif)
        ultimo_gif = cursor.fetchone()

        if ultimo_gif and ultimo_gif[0]:
            ultima_data_hora_str = f"{ultimo_gif[0]} {ultimo_gif[1]}"
            ultimo_gif_datetime = datetime.strptime(ultima_data_hora_str, "%Y-%m-%d %H:%M:%S")
            
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

def verifica_inventario(id_usuario, id_personagem):
    conn, cursor = conectar_banco_dados()
    query = f"SELECT quantidade FROM inventario WHERE id_usuario = {id_usuario} AND id_personagem = {id_personagem}"
    cursor.execute(query)
    quantidade_total = cursor.fetchone()[0]
    return quantidade_total > 29

def verifica_inventario_troca(id_usuario, id_personagem):
    conn, cursor = conectar_banco_dados()
    query = f"SELECT quantidade FROM inventario WHERE id_usuario = {id_usuario} AND id_personagem = {id_personagem}"
    cursor.execute(query)
    quantidade_total = cursor.fetchone()
    if quantidade_total is None:
        return 0  # Retorna 0 se a quantidade total for nula
    else:
        return quantidade_total[0]

