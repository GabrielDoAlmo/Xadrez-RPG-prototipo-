# utils.py
# Responsabilidade: Funções utilitárias de carregamento de assets, colisões e conversões.

import os
import pygame
import chess
import config


def carregar_assets():
    """
    Carrega todas as imagens do jogo e pré-renderiza as versões reduzidas
    das peças capturadas para evitar redimensionamentos durante o loop de 60 FPS.
    """
    assets = {
        "pecas": {},
        "pecas_pequenas": {},
        "story": {},
    }

    tamanho_pequeno = (config.TAMANHO_QUADRADO // 2, config.TAMANHO_QUADRADO // 2)

    try:
        for nome_arquivo in os.listdir(config.DIRETORIO_PECAS):
            if nome_arquivo.lower().endswith(".png"):
                peca = os.path.splitext(nome_arquivo)[0].strip()
                caminho_completo = os.path.join(config.DIRETORIO_PECAS, nome_arquivo)
                img_original = pygame.image.load(caminho_completo).convert_alpha()

                assets["pecas"][peca] = pygame.transform.smoothscale(
                    img_original, (config.TAMANHO_QUADRADO, config.TAMANHO_QUADRADO)
                )
                assets["pecas_pequenas"][peca] = pygame.transform.smoothscale(
                    img_original, tamanho_pequeno
                )

        if not assets["pecas"]:
            print(f"Nenhuma imagem de peça encontrada em '{config.DIRETORIO_PECAS}'")
            return None
        print(f"Carregadas {len(assets['pecas'])} imagens de peças.")
    except Exception as e:
        print(f"Erro ao carregar imagens de peças: {e}")
        return None

    try:
        assets["story"]["mapa_fundo"] = pygame.image.load(
            os.path.join(config.DIRETORIO_STORY, "mapa.png")
        ).convert()

        img_original_jogador = pygame.image.load(
            os.path.join(config.DIRETORIO_STORY, "jogador.png")
        ).convert_alpha()
        assets["story"]["jogador"] = pygame.transform.smoothscale(
            img_original_jogador, config.TAMANHO_PERSONAGEM
        )
        assets["story"]["portrait_jogador"] = pygame.transform.smoothscale(
            img_original_jogador, config.TAMANHO_PORTRAIT
        )

        img_original_inimigo = pygame.image.load(
            os.path.join(config.DIRETORIO_STORY, "inimigo.png")
        ).convert_alpha()
        assets["story"]["inimigo"] = pygame.transform.smoothscale(
            img_original_inimigo, config.TAMANHO_PERSONAGEM
        )
        assets["story"]["portrait_inimigo"] = pygame.transform.smoothscale(
            img_original_inimigo, config.TAMANHO_PORTRAIT
        )

        print("Carregados assets do modo história.")
    except Exception as e:
        print(f"Erro ao carregar assets do modo história: {e}")
        return None

    return assets


def verificar_colisao(rect):
    """
    Verifica a colisão do retângulo do jogador contra a matriz mapa_colisao.
    Checa todos os tiles cobertos pelo retângulo para evitar atravessar quinas.
    """
    if rect.left < 0 or rect.right > 800 or rect.top < 0 or rect.bottom > 800:
        return True

    col_inicio = rect.left // config.TAMANHO_TILE
    col_fim = (rect.right - 1) // config.TAMANHO_TILE
    lin_inicio = rect.top // config.TAMANHO_TILE
    lin_fim = (rect.bottom - 1) // config.TAMANHO_TILE

    max_linhas = len(config.mapa_colisao)
    max_colunas = len(config.mapa_colisao[0])

    for tile_y in range(lin_inicio, lin_fim + 1):
        for tile_x in range(col_inicio, col_fim + 1):
            if 0 <= tile_y < max_linhas and 0 <= tile_x < max_colunas:
                if config.mapa_colisao[tile_y][tile_x] == 1:
                    return True
            else:
                return True
    return False


def square_para_coords_tela(square, invertido):
    """Converte uma casa do python-chess (ex: chess.E4) para (coluna, linha) na tela."""
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    if invertido:
        return 7 - file, rank
    return file, 7 - rank


def coords_tela_para_square(col, row, invertido):
    """Converte (coluna, linha) da tela para uma casa do python-chess."""
    if invertido:
        file = 7 - col
        rank = row
    else:
        file = col
        rank = 7 - row
    if 0 <= file <= 7 and 0 <= rank <= 7:
        return chess.square(file, rank)
    return None


def formatar_tempo(tempo_em_segundos):
    """Converte segundos (float) para string formatada M:SS."""
    total_segundos = max(0, int(round(tempo_em_segundos)))
    minutos = total_segundos // 60
    segundos = total_segundos % 60
    return f"{minutos}:{segundos:02d}"