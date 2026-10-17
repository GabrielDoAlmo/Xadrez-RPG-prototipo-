# main.py
# Responsabilidade: Gerenciar o loop principal, máquina de estados e ecrã completo proporcional.

import os
import math
import random
import asyncio
import pygame
import chess

import config
import utils
import drawing
from game import ChessGame
from engine import ChessEngine

pygame.init()
pygame.display.set_caption("Jogo de Xadrez")

info_monitor = pygame.display.Info()
LARGURA_MONITOR = info_monitor.current_w
ALTURA_MONITOR = info_monitor.current_h

tela_real = None
tela_virtual = pygame.Surface((config.LARGURA_LOGICA, config.ALTURA_LOGICA))
relogio = pygame.time.Clock()

FONTES = {
    "titulo": pygame.font.SysFont("Arial", 80, True),
    "botao": pygame.font.SysFont("Arial", 40, True),
    "final": pygame.font.SysFont("Arial", 50, True, False),
    "reiniciar": pygame.font.SysFont("Arial", 25, True),
    "dialogo": pygame.font.SysFont("Arial", 28, False, True),
    "relogio": pygame.font.SysFont("Arial", 60, True),
    "coordenadas": pygame.font.SysFont("Arial", 16),
}


def calcular_escala_e_posicao(largura_janela, altura_janela):
    escala_x = largura_janela / config.LARGURA_LOGICA
    escala_y = altura_janela / config.ALTURA_LOGICA
    escala = min(escala_x, escala_y)

    largura_render = int(config.LARGURA_LOGICA * escala)
    altura_render = int(config.ALTURA_LOGICA * escala)
    offset_x = (largura_janela - largura_render) // 2
    offset_y = (altura_janela - altura_render) // 2

    return escala, largura_render, altura_render, offset_x, offset_y


def converter_posicao_mouse(pos_mouse, largura_janela, altura_janela):
    _, largura_render, altura_render, offset_x, offset_y = calcular_escala_e_posicao(largura_janela, altura_janela)
    mx, my = pos_mouse

    if not (offset_x <= mx < offset_x + largura_render and offset_y <= my < offset_y + altura_render):
        return None

    x_logico = int((mx - offset_x) * (config.LARGURA_LOGICA / largura_render))
    y_logico = int((my - offset_y) * (config.ALTURA_LOGICA / altura_render))
    return (x_logico, y_logico)


async def obter_jogada_ia_em_background(game, engine, difficulty_name):
    elo_list = config.ELO_BRACKETS.get(difficulty_name)
    if not elo_list and difficulty_name != "DAVID_TUTORIAL":
        difficulty_name = "Fácil"
        elo_list = config.ELO_BRACKETS["Fácil"]

    if difficulty_name == "DAVID_TUTORIAL":
        elo_da_jogada = 100
    else:
        elo_da_jogada = random.choice(elo_list)

    await engine.set_move_elo(elo_da_jogada)
    print_name = "David (Tutorial)" if difficulty_name == "DAVID_TUTORIAL" else difficulty_name
    print(f"IA ({print_name}) está pensando com ELO {elo_da_jogada}...")

    await asyncio.sleep(random.uniform(0.4, 1.2))
    return await game.get_engine_move(engine)


def criar_animacao_movimento(peca, from_sq, to_sq, invertido):
    tam = config.TAMANHO_QUADRADO
    orig_col, orig_lin = utils.square_para_coords_tela(from_sq, invertido)
    dest_col, dest_lin = utils.square_para_coords_tela(to_sq, invertido)
    origem_pos = (orig_col * tam, orig_lin * tam)
    destino_pos = (dest_col * tam, dest_lin * tam)

    return {
        "peca": peca,
        "origem": from_sq,
        "destino": to_sq,
        "pos_atual": origem_pos,
        "pos_final": destino_pos,
        "step_x": (destino_pos[0] - origem_pos[0]) / config.ANIMACAO_FRAMES,
        "step_y": (destino_pos[1] - origem_pos[1]) / config.ANIMACAO_FRAMES,
        "frame_count": 0,
    }


async def encerrar_recursos_ia(task_ia, engine):
    if task_ia:
        task_ia.cancel()
        try:
            await task_ia
        except asyncio.CancelledError:
            pass
    if engine:
        await engine.quit_engine()
    return None, None


async def main():
    global tela_real

    if config.TELA_CHEIA:
        tela_real = pygame.display.set_mode((LARGURA_MONITOR, ALTURA_MONITOR), pygame.FULLSCREEN)
    else:
        tela_real = pygame.display.set_mode((config.LARGURA_LOGICA, config.ALTURA_LOGICA), pygame.RESIZABLE)

    assets = utils.carregar_assets()
    if assets is None:
        print("Falha crítica ao carregar assets. Encerrando.")
        return

    estado_do_jogo = "MENU"
    game = None
    engine = None
    tabuleiro_logica = None

    contexto_partida = {
        "modo_de_jogo": None,
        "cor_jogador": None,
        "origem_da_partida": None,
        "dificuldade_ia_nome": "Médio",
        "skin_tabuleiro_nome": "Médio",
        "tempo_pvp_selecionado": 0,
        "tabuleiro_invertido": False,
        "mensagem_fim_partida": "",
    }

    selecionado = False
    origem_square = None
    movimentos_validos = []
    animacao = None
    jogada_pendente = None
    ia_pensando = False
    task_ia = None
    info_promocao = None
    ui_rects = {}

    tempo_brancas_seg = 0.0
    tempo_pretas_seg = 0.0
    ultimo_tick_relogio = 0

    jogador_rect = pygame.Rect(
        config.POSICAO_INICIAL_JOGADOR[0],
        config.POSICAO_INICIAL_JOGADOR[1],
        assets["story"]["jogador"].get_width(),
        assets["story"]["jogador"].get_height(),
    )
    inimigo_rect = pygame.Rect(
        config.POSICAO_INIMIGO_DAVID[0],
        config.POSICAO_INIMIGO_DAVID[1],
        assets["story"]["inimigo"].get_width(),
        assets["story"]["inimigo"].get_height(),
    )
    dialogo_atual = None
    indice_dialogo_atual = 0
    letras_visiveis = 0
    ultimo_tick_letra = 0
    resultado_batalha = None
    acao_pos_dialogo = None
    raio_transicao = 0
    RAIO_MAXIMO = int(math.hypot(config.LARGURA_LOGICA / 2, config.ALTURA_LOGICA / 2))
    ultima_pagina_dialogo = None

    def avancar_dialogo():
        nonlocal dialogo_atual, indice_dialogo_atual, letras_visiveis, ultimo_tick_letra, acao_pos_dialogo, estado_do_jogo, ultima_pagina_dialogo, raio_transicao
        if dialogo_atual:
            texto_pagina_atual = dialogo_atual[indice_dialogo_atual]["text"]
            if letras_visiveis < len(texto_pagina_atual):
                letras_visiveis = len(texto_pagina_atual)
            else:
                indice_dialogo_atual += 1
                if indice_dialogo_atual >= len(dialogo_atual):
                    if acao_pos_dialogo == "VOLTAR_MENU":
                        acao_pos_dialogo = None
                        dialogo_atual = None
                        estado_do_jogo = "SAINDO_DA_PARTIDA"
                    elif acao_pos_dialogo == "DAVID_VENCIDO_CONTINUAR_EXPLORANDO":
                        inimigo_rect.topleft = (-1000, -1000)
                        acao_pos_dialogo = None
                        dialogo_atual = None
                        estado_do_jogo = "EXPLORANDO_MAPA"
                    else:
                        ultima_pagina_dialogo = dialogo_atual[indice_dialogo_atual - 1]
                        dialogo_atual = None
                        raio_transicao = RAIO_MAXIMO
                        estado_do_jogo = "TRANSICAO_FECHANDO"
                else:
                    letras_visiveis = 0
                    ultimo_tick_letra = pygame.time.get_ticks()

    rodando = True
    while rodando:
        tempo_atual = pygame.time.get_ticks()
        largura_atual_janela, altura_atual_janela = tela_real.get_size()

        if (
            estado_do_jogo == "JOGANDO"
            and contexto_partida["modo_de_jogo"] == "PVP"
            and contexto_partida["tempo_pvp_selecionado"] > 0
        ):
            tempo_passado = (tempo_atual - ultimo_tick_relogio) / 1000.0
            ultimo_tick_relogio = tempo_atual

            if tabuleiro_logica and not tabuleiro_logica.is_game_over():
                if tabuleiro_logica.turn == chess.WHITE:
                    tempo_brancas_seg -= tempo_passado
                else:
                    tempo_pretas_seg -= tempo_passado

                if tempo_brancas_seg <= 0:
                    tempo_brancas_seg = 0
                    contexto_partida["mensagem_fim_partida"] = "Pretas venceram no tempo!"
                    selecionado = False
                    movimentos_validos = []
                    estado_do_jogo = "FIM_DE_JOGO"
                elif tempo_pretas_seg <= 0:
                    tempo_pretas_seg = 0
                    contexto_partida["mensagem_fim_partida"] = "Brancas venceram no tempo!"
                    selecionado = False
                    movimentos_validos = []
                    estado_do_jogo = "FIM_DE_JOGO"

        if estado_do_jogo == "EXPLORANDO_MAPA":
            teclas = pygame.key.get_pressed()
            dir_x = int(teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - int(
                teclas[pygame.K_LEFT] or teclas[pygame.K_a]
            )
            dir_y = int(teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - int(
                teclas[pygame.K_UP] or teclas[pygame.K_w]
            )

            pos_antiga_x, pos_antiga_y = jogador_rect.x, jogador_rect.y

            if dir_x != 0:
                jogador_rect.x += dir_x * config.VELOCIDADE_JOGADOR
                if utils.verificar_colisao(jogador_rect):
                    jogador_rect.x = pos_antiga_x

            if dir_y != 0:
                jogador_rect.y += dir_y * config.VELOCIDADE_JOGADOR
                if utils.verificar_colisao(jogador_rect):
                    jogador_rect.y = pos_antiga_y

            if jogador_rect.colliderect(inimigo_rect):
                jogador_rect.topleft = (pos_antiga_x, pos_antiga_y)
                dialogo_atual = config.DIALOGO_ENCONTRO_PONTE
                indice_dialogo_atual = 0
                letras_visiveis = 0
                ultimo_tick_letra = tempo_atual
                estado_do_jogo = "EXIBINDO_MENSAGEM"
            elif inimigo_rect.x < 0 and jogador_rect.colliderect(config.TELEPORTER_RECT):
                estado_do_jogo = "BETA_FIM"

        if estado_do_jogo == "EXIBINDO_MENSAGEM" and dialogo_atual:
            texto_pagina_atual = dialogo_atual[indice_dialogo_atual]["text"]
            if letras_visiveis < len(texto_pagina_atual):
                if tempo_atual - ultimo_tick_letra > config.VELOCIDADE_TEXTO:
                    letras_visiveis += 1
                    ultimo_tick_letra = tempo_atual

        if estado_do_jogo == "TRANSICAO_FECHANDO":
            raio_transicao -= config.VELOCIDADE_TRANSICAO
            if raio_transicao <= 0:
                raio_transicao = 0
                contexto_partida["modo_de_jogo"] = "PVA"
                contexto_partida["cor_jogador"] = chess.WHITE
                contexto_partida["origem_da_partida"] = "MODO_HISTORIA"
                contexto_partida["dificuldade_ia_nome"] = "DAVID_TUTORIAL"
                contexto_partida["skin_tabuleiro_nome"] = "Fácil"
                contexto_partida["tabuleiro_invertido"] = False

                task_ia, engine = await encerrar_recursos_ia(task_ia, engine)
                game = ChessGame()
                engine = ChessEngine(config.STOCKFISH_PATH)
                await engine.start_engine()
                tabuleiro_logica = game.board
                estado_do_jogo = "TRANSICAO_ABRINDO"

        elif estado_do_jogo == "TRANSICAO_ABRINDO":
            raio_transicao += config.VELOCIDADE_TRANSICAO
            if raio_transicao >= RAIO_MAXIMO:
                raio_transicao = RAIO_MAXIMO
                estado_do_jogo = "JOGANDO"

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_F11:
                    config.TELA_CHEIA = not config.TELA_CHEIA
                    if config.TELA_CHEIA:
                        tela_real = pygame.display.set_mode((LARGURA_MONITOR, ALTURA_MONITOR), pygame.FULLSCREEN)
                    else:
                        tela_real = pygame.display.set_mode((config.LARGURA_LOGICA, config.ALTURA_LOGICA), pygame.RESIZABLE)
                
                elif estado_do_jogo == "EXIBINDO_MENSAGEM" and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    avancar_dialogo()

                elif estado_do_jogo == "FIM_DE_JOGO" and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if contexto_partida["origem_da_partida"] == "MODO_HISTORIA":
                        task_ia, engine = await encerrar_recursos_ia(task_ia, engine)
                        ia_pensando = False
                        if resultado_batalha == "derrota":
                            dialogo_atual = [
                                {
                                    "speaker": "DAVID",
                                    "portrait": "inimigo",
                                    "text": "HAHAHA, como esperado de um lixo! Essa partida foi tão fácil que nem vou contar como oficial.",
                                }
                            ]
                            indice_dialogo_atual = 0
                            letras_visiveis = 0
                            ultimo_tick_letra = tempo_atual
                            acao_pos_dialogo = "VOLTAR_MENU"
                            estado_do_jogo = "EXIBINDO_MENSAGEM"
                        elif resultado_batalha == "vitoria":
                            dialogo_atual = config.DIALOGO_VITORIA_DAVID
                            indice_dialogo_atual = 0
                            letras_visiveis = 0
                            ultimo_tick_letra = tempo_atual
                            acao_pos_dialogo = "DAVID_VENCIDO_CONTINUAR_EXPLORANDO"
                            estado_do_jogo = "EXIBINDO_MENSAGEM"
                    else:
                        estado_do_jogo = "SAINDO_DA_PARTIDA"

                elif estado_do_jogo == "BETA_FIM" and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    estado_do_jogo = "SAINDO_DA_PARTIDA"

            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if estado_do_jogo == "EXIBINDO_MENSAGEM":
                    avancar_dialogo()
                    continue

                pos_logica = converter_posicao_mouse(evento.pos, largura_atual_janela, altura_atual_janela)
                if not pos_logica:
                    continue

                if estado_do_jogo == "MENU":
                    botoes = ui_rects.get("MENU")
                    if botoes:
                        ret_historia, ret_iniciar, ret_sair = botoes
                        if ret_historia.collidepoint(pos_logica):
                            jogador_rect.topleft = config.POSICAO_INICIAL_JOGADOR
                            inimigo_rect.topleft = config.POSICAO_INIMIGO_DAVID
                            estado_do_jogo = "EXPLORANDO_MAPA"
                        elif ret_iniciar.collidepoint(pos_logica):
                            estado_do_jogo = "SELECIONAR_MODO"
                        elif ret_sair.collidepoint(pos_logica):
                            rodando = False

                elif estado_do_jogo == "SELECIONAR_MODO":
                    botoes = ui_rects.get("SELECIONAR_MODO")
                    if botoes:
                        ret_pva, ret_pvp, ret_voltar = botoes
                        if ret_pva.collidepoint(pos_logica):
                            estado_do_jogo = "SELECIONAR_DIFICULDADE_IA"
                        elif ret_pvp.collidepoint(pos_logica):
                            contexto_partida["modo_de_jogo"] = "PVP"
                            estado_do_jogo = "ESCOLHER_TEMPO_PVP"
                        elif ret_voltar.collidepoint(pos_logica):
                            estado_do_jogo = "MENU"

                elif estado_do_jogo == "ESCOLHER_TEMPO_PVP":
                    retangulos = ui_rects.get("ESCOLHER_TEMPO_PVP", {})
                    for tempo, retangulo in retangulos.items():
                        if retangulo.collidepoint(pos_logica):
                            if tempo == "Voltar":
                                estado_do_jogo = "SELECIONAR_MODO"
                            else:
                                contexto_partida["tempo_pvp_selecionado"] = (
                                    0 if tempo == "Sem Tempo" else tempo
                                )
                                contexto_partida["modo_de_jogo"] = "PVP"
                                contexto_partida["cor_jogador"] = None
                                contexto_partida["origem_da_partida"] = "PARTIDA_RAPIDA"
                                contexto_partida["dificuldade_ia_nome"] = "Médio"
                                contexto_partida["skin_tabuleiro_nome"] = "Médio"
                                contexto_partida["tabuleiro_invertido"] = False

                                game = ChessGame()
                                tabuleiro_logica = game.board

                                if contexto_partida["tempo_pvp_selecionado"] > 0:
                                    tempo_brancas_seg = contexto_partida["tempo_pvp_selecionado"] * 60
                                    tempo_pretas_seg = contexto_partida["tempo_pvp_selecionado"] * 60
                                    ultimo_tick_relogio = tempo_atual

                                estado_do_jogo = "JOGANDO"
                            break

                elif estado_do_jogo == "SELECIONAR_DIFICULDADE_IA":
                    retangulos = ui_rects.get("SELECIONAR_DIFICULDADE_IA", {})
                    for nome_dificuldade, retangulo in retangulos.items():
                        if retangulo.collidepoint(pos_logica):
                            if nome_dificuldade == "Voltar":
                                estado_do_jogo = "SELECIONAR_MODO"
                            else:
                                contexto_partida["dificuldade_ia_nome"] = nome_dificuldade
                                contexto_partida["skin_tabuleiro_nome"] = nome_dificuldade
                                estado_do_jogo = "ESCOLHER_COR_IA"
                            break

                elif estado_do_jogo == "ESCOLHER_COR_IA":
                    botoes = ui_rects.get("ESCOLHER_COR_IA")
                    if botoes:
                        ret_brancas, ret_pretas, ret_voltar = botoes
                        if ret_brancas.collidepoint(pos_logica):
                            contexto_partida["cor_jogador"] = chess.WHITE
                            contexto_partida["tabuleiro_invertido"] = False
                            estado_do_jogo = "INICIANDO_PARTIDA"
                        elif ret_pretas.collidepoint(pos_logica):
                            contexto_partida["cor_jogador"] = chess.BLACK
                            contexto_partida["tabuleiro_invertido"] = True
                            estado_do_jogo = "INICIANDO_PARTIDA"
                        elif ret_voltar.collidepoint(pos_logica):
                            estado_do_jogo = "SELECIONAR_DIFICULDADE_IA"

                elif estado_do_jogo == "JOGANDO":
                    if pos_logica[0] >= 800:
                        if drawing.obter_rect_botao_reiniciar().collidepoint(pos_logica):
                            estado_do_jogo = "SAINDO_DA_PARTIDA"
                            continue
                    else:
                        turno_humano = contexto_partida["modo_de_jogo"] == "PVP" or (
                            contexto_partida["modo_de_jogo"] == "PVA"
                            and tabuleiro_logica
                            and tabuleiro_logica.turn == contexto_partida["cor_jogador"]
                        )

                        if not animacao and game and not game.is_game_over() and turno_humano:
                            x, y = pos_logica
                            if 0 <= x < 800 and 0 <= y < 800:
                                coluna = x // config.TAMANHO_QUADRADO
                                linha = y // config.TAMANHO_QUADRADO
                                square_clicado = utils.coords_tela_para_square(
                                    coluna, linha, contexto_partida["tabuleiro_invertido"]
                                )

                                if square_clicado is not None:
                                    peca_clicada = tabuleiro_logica.piece_at(square_clicado)

                                    if peca_clicada and peca_clicada.color == tabuleiro_logica.turn:
                                        selecionado = True
                                        origem_square = square_clicado
                                        movimentos_validos = [
                                            m
                                            for m in tabuleiro_logica.legal_moves
                                            if m.from_square == square_clicado
                                        ]
                                    elif selecionado:
                                        from_square = origem_square
                                        to_square = square_clicado
                                        peca_movendo = tabuleiro_logica.piece_at(from_square)

                                        is_promotion = False
                                        if peca_movendo and peca_movendo.piece_type == chess.PAWN:
                                            rank_destino = chess.square_rank(to_square)
                                            if (
                                                peca_movendo.color == chess.WHITE
                                                and rank_destino == 7
                                            ) or (
                                                peca_movendo.color == chess.BLACK
                                                and rank_destino == 0
                                            ):
                                                if (
                                                    chess.Move(
                                                        from_square,
                                                        to_square,
                                                        promotion=chess.QUEEN,
                                                    )
                                                    in tabuleiro_logica.legal_moves
                                                ):
                                                    is_promotion = True

                                        if is_promotion:
                                            estado_do_jogo = "PROMOVENDO"
                                            info_promocao = {
                                                "from": from_square,
                                                "to": to_square,
                                            }
                                            selecionado = False
                                            movimentos_validos = []
                                            continue

                                        move = chess.Move(from_square, to_square)
                                        if move in tabuleiro_logica.legal_moves:
                                            animacao = criar_animacao_movimento(
                                                peca_movendo,
                                                from_square,
                                                to_square,
                                                contexto_partida["tabuleiro_invertido"],
                                            )
                                            jogada_pendente = move

                                        selecionado = False
                                        movimentos_validos = []

                elif estado_do_jogo == "PROMOVENDO":
                    retangulos_promocao = ui_rects.get("PROMOVENDO", {})
                    for peca_tipo, retangulo in retangulos_promocao.items():
                        if retangulo.collidepoint(pos_logica):
                            from_sq = info_promocao["from"]
                            to_sq = info_promocao["to"]
                            move = chess.Move(from_sq, to_sq, promotion=peca_tipo)

                            if move in tabuleiro_logica.legal_moves:
                                peca_a_animar = tabuleiro_logica.piece_at(from_sq)
                                animacao = criar_animacao_movimento(
                                    peca_a_animar,
                                    from_sq,
                                    to_sq,
                                    contexto_partida["tabuleiro_invertido"],
                                )
                                jogada_pendente = move

                            info_promocao = None
                            estado_do_jogo = "JOGANDO"
                            break

                elif estado_do_jogo == "FIM_DE_JOGO":
                    if contexto_partida["origem_da_partida"] == "MODO_HISTORIA":
                        task_ia, engine = await encerrar_recursos_ia(task_ia, engine)
                        ia_pensando = False
                        if resultado_batalha == "derrota":
                            dialogo_atual = [
                                {
                                    "speaker": "DAVID",
                                    "portrait": "inimigo",
                                    "text": "HAHAHA, como esperado de um lixo! Essa partida foi tão fácil que nem vou contar como oficial.",
                                }
                            ]
                            indice_dialogo_atual = 0
                            letras_visiveis = 0
                            ultimo_tick_letra = tempo_atual
                            acao_pos_dialogo = "VOLTAR_MENU"
                            estado_do_jogo = "EXIBINDO_MENSAGEM"
                        elif resultado_batalha == "vitoria":
                            dialogo_atual = config.DIALOGO_VITORIA_DAVID
                            indice_dialogo_atual = 0
                            letras_visiveis = 0
                            ultimo_tick_letra = tempo_atual
                            acao_pos_dialogo = "DAVID_VENCIDO_CONTINUAR_EXPLORANDO"
                            estado_do_jogo = "EXIBINDO_MENSAGEM"
                    else:
                        estado_do_jogo = "SAINDO_DA_PARTIDA"

                elif estado_do_jogo == "BETA_FIM":
                    estado_do_jogo = "SAINDO_DA_PARTIDA"

        # --- 3. TRANSIÇÕES DE ESTADO E EXECUTÁVEIS ---

        if estado_do_jogo == "INICIANDO_PARTIDA":
            contexto_partida["modo_de_jogo"] = "PVA"
            contexto_partida["origem_da_partida"] = "PARTIDA_RAPIDA"

            task_ia, engine = await encerrar_recursos_ia(task_ia, engine)
            game = ChessGame()
            tabuleiro_logica = game.board
            engine = ChessEngine(config.STOCKFISH_PATH)
            await engine.start_engine()

            estado_do_jogo = "JOGANDO"
            continue

        if estado_do_jogo == "SAINDO_DA_PARTIDA":
            task_ia, engine = await encerrar_recursos_ia(task_ia, engine)

            game = None
            tabuleiro_logica = None
            selecionado = False
            movimentos_validos = []
            animacao = None
            jogada_pendente = None
            ia_pensando = False
            info_promocao = None

            dificuldade_salva = contexto_partida["dificuldade_ia_nome"]
            skin_salva = (
                contexto_partida["skin_tabuleiro_nome"]
                if contexto_partida["skin_tabuleiro_nome"] in config.CORES_TABULEIRO
                else "Médio"
            )
            contexto_partida = {
                "modo_de_jogo": None,
                "cor_jogador": None,
                "origem_da_partida": None,
                "dificuldade_ia_nome": (
                    dificuldade_salva if dificuldade_salva in config.ELO_BRACKETS else "Médio"
                ),
                "skin_tabuleiro_nome": skin_salva,
                "tempo_pvp_selecionado": 0,
                "tabuleiro_invertido": False,
                "mensagem_fim_partida": "",
            }

            estado_do_jogo = "MENU"
            continue

        # --- 4. ANIMAÇÃO DE PEÇAS E TURNO DA IA ---

        if estado_do_jogo == "JOGANDO" and animacao:
            animacao["pos_atual"] = (
                animacao["pos_atual"][0] + animacao["step_x"],
                animacao["pos_atual"][1] + animacao["step_y"],
            )
            animacao["frame_count"] += 1

            if animacao["frame_count"] >= config.ANIMACAO_FRAMES:
                if jogada_pendente:
                    game.make_move(jogada_pendente)
                    jogada_pendente = None
                animacao = None

                if game and game.is_game_over():
                    if tabuleiro_logica.is_checkmate():
                        cor_vencedora = not tabuleiro_logica.turn
                        if contexto_partida["modo_de_jogo"] == "PVP":
                            contexto_partida["mensagem_fim_partida"] = (
                                "Brancas Venceram!"
                                if cor_vencedora == chess.WHITE
                                else "Pretas Venceram!"
                            )
                        elif contexto_partida["modo_de_jogo"] == "PVA":
                            venceu = cor_vencedora == contexto_partida["cor_jogador"]
                            if contexto_partida["origem_da_partida"] == "MODO_HISTORIA":
                                contexto_partida["mensagem_fim_partida"] = (
                                    "Você Venceu!" if venceu else "DAVID VENCEU!"
                                )
                            else:
                                contexto_partida["mensagem_fim_partida"] = (
                                    "Você Venceu!" if venceu else "A IA Venceu!"
                                )
                            resultado_batalha = "vitoria" if venceu else "derrota"
                    else:
                        contexto_partida["mensagem_fim_partida"] = "Empate!"
                        resultado_batalha = (
                            "derrota"
                            if contexto_partida["origem_da_partida"] == "MODO_HISTORIA"
                            else "empate"
                        )
                    estado_do_jogo = "FIM_DE_JOGO"

        if (
            estado_do_jogo == "JOGANDO"
            and contexto_partida["modo_de_jogo"] == "PVA"
            and tabuleiro_logica
            and tabuleiro_logica.turn != contexto_partida["cor_jogador"]
            and not animacao
            and not ia_pensando
            and game
            and not game.is_game_over()
        ):
            ia_pensando = True
            task_ia = asyncio.create_task(
                obter_jogada_ia_em_background(
                    game, engine, contexto_partida["dificuldade_ia_nome"]
                )
            )

        if ia_pensando and task_ia and task_ia.done():
            try:
                engine_move = task_ia.result()
            except asyncio.CancelledError:
                engine_move = None
            ia_pensando = False
            task_ia = None

            if estado_do_jogo != "JOGANDO":
                continue

            if engine_move and tabuleiro_logica and engine_move in tabuleiro_logica.legal_moves:
                peca_a_animar = tabuleiro_logica.piece_at(engine_move.from_square)
                if peca_a_animar:
                    animacao = criar_animacao_movimento(
                        peca_a_animar,
                        engine_move.from_square,
                        engine_move.to_square,
                        contexto_partida["tabuleiro_invertido"],
                    )
                    jogada_pendente = engine_move

        # --- 5. RENDERIZAÇÃO NA TELA VIRTUAL ---

        tela_virtual.fill(config.COR_FUNDO)

        if estado_do_jogo == "MENU":
            ui_rects["MENU"] = drawing.desenhar_menu(tela_virtual, FONTES)

        elif estado_do_jogo == "SELECIONAR_MODO":
            ui_rects["SELECIONAR_MODO"] = drawing.desenhar_menu_modo_jogo(tela_virtual, FONTES)

        elif estado_do_jogo == "SELECIONAR_DIFICULDADE_IA":
            ui_rects["SELECIONAR_DIFICULDADE_IA"] = drawing.desenhar_menu_dificuldade_ia(
                tela_virtual, FONTES
            )

        elif estado_do_jogo == "ESCOLHER_TEMPO_PVP":
            ui_rects["ESCOLHER_TEMPO_PVP"] = drawing.desenhar_menu_tempo_pvp(tela_virtual, FONTES)

        elif estado_do_jogo == "ESCOLHER_COR_IA":
            ui_rects["ESCOLHER_COR_IA"] = drawing.desenhar_menu_escolha_cor(tela_virtual, FONTES)

        elif estado_do_jogo == "EXPLORANDO_MAPA":
            drawing.desenhar_mapa(tela_virtual, assets["story"], jogador_rect, inimigo_rect)

        elif estado_do_jogo in ("JOGANDO", "FIM_DE_JOGO", "PROMOVENDO"):
            skin_nome = contexto_partida["skin_tabuleiro_nome"]
            if skin_nome not in config.CORES_TABULEIRO:
                skin_nome = "Médio"
                contexto_partida["skin_tabuleiro_nome"] = skin_nome
            cor_clara = config.CORES_TABULEIRO[skin_nome]["claro"]
            cor_escura = config.CORES_TABULEIRO[skin_nome]["escuro"]

            drawing.desenhar_tabuleiro(tela_virtual, cor_clara, cor_escura)
            drawing.desenhar_coordenadas(
                tela_virtual, FONTES, cor_clara, cor_escura, contexto_partida["tabuleiro_invertido"]
            )
            drawing.desenhar_botao_reiniciar(tela_virtual, FONTES)

            if game and tabuleiro_logica:
                drawing.desenhar_pecas_capturadas(
                    tela_virtual,
                    assets["pecas_pequenas"],
                    game.pecas_capturadas_brancas,
                    game.pecas_capturadas_pretas,
                )

                if selecionado:
                    drawing.desenhar_movimentos_validos(
                        tela_virtual, movimentos_validos, contexto_partida["tabuleiro_invertido"]
                    )

                drawing.desenhar_pecas(
                    tela_virtual,
                    tabuleiro_logica,
                    assets["pecas"],
                    animacao,
                    contexto_partida["tabuleiro_invertido"],
                )

                if (
                    contexto_partida["modo_de_jogo"] == "PVP"
                    and contexto_partida["tempo_pvp_selecionado"] > 0
                ):
                    drawing.desenhar_relogios_pvp(
                        tela_virtual,
                        FONTES,
                        tempo_brancas_seg,
                        tempo_pretas_seg,
                        tabuleiro_logica.turn,
                    )

                if estado_do_jogo == "FIM_DE_JOGO":
                    drawing.desenhar_mensagem_final(
                        tela_virtual, FONTES, contexto_partida["mensagem_fim_partida"]
                    )
                elif estado_do_jogo == "PROMOVENDO":
                    ui_rects["PROMOVENDO"] = drawing.desenhar_menu_promocao(
                        tela_virtual, FONTES, assets["pecas"], tabuleiro_logica.turn
                    )
            elif estado_do_jogo == "FIM_DE_JOGO":
                drawing.desenhar_mensagem_final(
                    tela_virtual, FONTES, contexto_partida["mensagem_fim_partida"]
                )

        elif estado_do_jogo == "BETA_FIM":
            drawing.desenhar_mapa(tela_virtual, assets["story"], jogador_rect, inimigo_rect)
            drawing.desenhar_tela_beta_fim(tela_virtual, FONTES, config.MENSAGEM_BETA_FIM)

        elif estado_do_jogo == "EXIBINDO_MENSAGEM":
            if dialogo_atual:
                pagina_atual = dialogo_atual[indice_dialogo_atual]
                drawing.desenhar_tela_encontro(
                    tela_virtual,
                    FONTES,
                    assets["story"],
                    pagina_atual["portrait"],
                    pagina_atual["speaker"],
                    pagina_atual["text"],
                    letras_visiveis,
                )

        elif estado_do_jogo == "TRANSICAO_FECHANDO":
            if ultima_pagina_dialogo:
                drawing.desenhar_tela_encontro(
                    tela_virtual,
                    FONTES,
                    assets["story"],
                    ultima_pagina_dialogo["portrait"],
                    ultima_pagina_dialogo["speaker"],
                    ultima_pagina_dialogo["text"],
                    len(ultima_pagina_dialogo["text"]),
                )
            drawing.desenhar_iris_overlay(tela_virtual, raio_transicao)

        elif estado_do_jogo == "TRANSICAO_ABRINDO":
            skin_nome = contexto_partida["skin_tabuleiro_nome"]
            if skin_nome not in config.CORES_TABULEIRO:
                skin_nome = "Médio"
            cor_clara = config.CORES_TABULEIRO[skin_nome]["claro"]
            cor_escura = config.CORES_TABULEIRO[skin_nome]["escuro"]

            if tabuleiro_logica:
                drawing.desenhar_tabuleiro(tela_virtual, cor_clara, cor_escura)
                drawing.desenhar_coordenadas(
                    tela_virtual, FONTES, cor_clara, cor_escura, contexto_partida["tabuleiro_invertido"]
                )
                drawing.desenhar_pecas(
                    tela_virtual,
                    tabuleiro_logica,
                    assets["pecas"],
                    None,
                    contexto_partida["tabuleiro_invertido"],
                )
            drawing.desenhar_iris_overlay(tela_virtual, raio_transicao)

        # --- REDIMENSIONAMENTO E ESCALA NA TELA REAL (LETTERBOXING COM BARRAS PRETAS) ---
        tela_real.fill((0, 0, 0))
        _, largura_render, altura_render, offset_x, offset_y = calcular_escala_e_posicao(
            largura_atual_janela, altura_atual_janela
        )
        
        superficie_escalada = pygame.transform.smoothscale(tela_virtual, (largura_render, altura_render))
        tela_real.blit(superficie_escalada, (offset_x, offset_y))

        pygame.display.flip()
        relogio.tick(config.FPS)
        await asyncio.sleep(0)

    await encerrar_recursos_ia(task_ia, engine)
    pygame.quit()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(main())