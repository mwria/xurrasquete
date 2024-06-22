from pesquisas import *
from user import *
from bd import *
from loja import *
from gnome import *

# Função para verificar se um ID de usuário está na tabela ban
def verificar_ban(id_usuario):
    try:
        conn, cursor = conectar_banco_dados()
        
        # Consultar a tabela ban para verificar se o ID está presente
        cursor.execute("SELECT * FROM ban WHERE iduser = %s", (str(id_usuario),))
        ban_info = cursor.fetchone()

        if ban_info:
            # Se o ID estiver na tabela ban, informar motivo e nome
            motivo = ban_info[3]
            nome = ban_info[2]
            return True, motivo, nome
        else:
            # Se o ID não estiver na tabela ban
            return False, None, None

    except Exception as e:
        print(f"Erro ao verificar na tabela ban: {e}")
        return False, None, None                    
    finally:
        fechar_conexao(cursor, conn)
        
 
