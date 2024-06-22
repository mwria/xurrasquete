from bd import *

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
        