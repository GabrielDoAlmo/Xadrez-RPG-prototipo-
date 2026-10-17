# drawing.py
# Responsabilidade: Conter todas as funções de renderização gráfica e layout de botões.

import pygame
import chess
import config
import utils

# Cache de superfícies translúcidas para evitar realocação a cada frame (60 FPS)
_SURFACES_CACHE = {}


def _obter_surface_translucida(largura, altura, cor_rgba):
    chave = (largura, altura, cor_rgba)
    if chave not in _SURFACES_CACHE:
        surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
        surf.fill(cor_rgba)
        _SURFACES_CACHE[chave] = surf
    return _SURFACES_CACHE[chave]


# --- Funções de Desenho do Tabuleiro e Partida ---

def desenhar_tabuleiro(tela, cor_clara, cor_escura):
    """Desenha as 64 casas do tabuleiro 8x8."""
    tam = config.TAMANHO_QUADRADO
    for linha in range(8):
        for coluna in range(8):
            cor = cor_clara if (linha + coluna) % 2 == 0 else cor_escura
            pygame.draw.rect(tela, cor, (coluna * tam, linha * tam, tam, tam))


def desenhar_pecas(tela, tabuleiro_logica, pecas_imagens, animacao_info=None, invertido=False):
    """Desenha as peças no tabuleiro e renderiza a peça animada por cima."""
    if not tabuleiro_logica:
        return

    tam = config.TAMANHO_QUADRADO
    origem_animada = animacao_info["origem"] if animacao_info else None

    for square in chess.SQUARES:
        if square == origem_animada:
            continue
        peca_obj = tabuleiro_logica.piece_at(square)
        if peca_obj:
            peca_img = pecas_imagens.get(peca_obj.symbol())
            if peca_img:
                col, row = utils.square_para_coords_tela(square, invertido)
                tela.blit(peca_img, (col * tam, row * tam))

    if animacao_info:
        peca_img = pecas_imagens.get(animacao_info["peca"].symbol())
        if peca_img:
            tela.blit(peca_img, animacao_info["pos_atual"])


def desenhar_movimentos_validos(tela, movimentos_validos, invertido=False):
    """Destaca as casas de destino válidas usando uma única superfície em cache."""
    tam = config.TAMANHO_QUADRADO
    quadrado_verde = _obter_surface_translucida(tam, tam, (0, 255, 0, 100))

    for move in movimentos_validos:
        col, row = utils.square_para_coords_tela(move.to_square, invertido)
        tela.blit(quadrado_verde, (col * tam, row * tam))


def desenhar_pecas_capturadas(
    tela,
    pecas_pequenas_imagens,
    pecas_capturadas_brancas,
    pecas_capturadas_pretas,
):
    """Desenha as peças capturadas na barra lateral utilizando as miniaturas pré-carregadas."""
    espaco_lateral_x = 800
    passo = config.TAMANHO_QUADRADO // 2
    limite_x = config.LARGURA_JANELA - passo

    pos_x = espaco_lateral_x + 20
    pos_y_brancas = 120
    for peca in pecas_capturadas_brancas:
        img_pequena = pecas_pequenas_imagens.get(peca)
        if img_pequena:
            tela.blit(img_pequena, (pos_x, pos_y_brancas))
            pos_x += passo
            if pos_x > limite_x:
                pos_x = espaco_lateral_x + 20
                pos_y_brancas += passo

    pos_x = espaco_lateral_x + 20
    pos_y_pretas = config.ALTURA_JANELA - 120 - passo
    for peca in pecas_capturadas_pretas:
        img_pequena = pecas_pequenas_imagens.get(peca)
        if img_pequena:
            tela.blit(img_pequena, (pos_x, pos_y_pretas))
            pos_x += passo
            if pos_x > limite_x:
                pos_x = espaco_lateral_x + 20
                pos_y_pretas -= passo


def desenhar_relogios_pvp(tela, fontes, tempo_brancas, tempo_pretas, turno_atual):
    """Desenha os cronômetros dos jogadores no modo PvP."""
    cor_bg_preto = (80, 80, 80) if turno_atual == chess.BLACK else (40, 40, 40)
    retangulo_preto = pygame.Rect(820, 10, 160, 100)
    pygame.draw.rect(tela, cor_bg_preto, retangulo_preto, border_radius=10)

    texto_tempo_preto = fontes["relogio"].render(
        utils.formatar_tempo(tempo_pretas), True, (255, 255, 255)
    )
    tela.blit(texto_tempo_preto, texto_tempo_preto.get_rect(center=retangulo_preto.center))

    cor_bg_branco = (220, 220, 220) if turno_atual == chess.WHITE else (180, 180, 180)
    retangulo_branco = pygame.Rect(820, config.ALTURA_JANELA - 110, 160, 100)
    pygame.draw.rect(tela, cor_bg_branco, retangulo_branco, border_radius=10)

    texto_tempo_branco = fontes["relogio"].render(
        utils.formatar_tempo(tempo_brancas), True, (0, 0, 0)
    )
    tela.blit(texto_tempo_branco, texto_tempo_branco.get_rect(center=retangulo_branco.center))


def desenhar_coordenadas(tela, fontes, cor_clara_atual, cor_escura_atual, invertido=False):
    """
    Desenha as coordenadas (a-h, 1-8) nas bordas do tabuleiro com uma única
    renderização por coordenada e respeitando a orientação invertida.
    """
    fonte_coord = fontes["coordenadas"]
    tam = config.TAMANHO_QUADRADO
    arquivos = "abcdefgh"
    ranks = "12345678"

    linha_visual_letra = 0 if invertido else 7
    coluna_visual_num = 7 if invertido else 0

    for i in range(8):
        # Coordenadas de Coluna (a-h)
        letra = arquivos[7 - i] if invertido else arquivos[i]
        e_casa_clara_letra = (linha_visual_letra + i) % 2 == 0
        cor_texto_letra = cor_escura_atual if e_casa_clara_letra else cor_clara_atual
        letra_surf = fonte_coord.render(letra, True, cor_texto_letra)

        pos_x_letra = i * tam + tam - letra_surf.get_width() - 5
        pos_y_letra = linha_visual_letra * tam + tam - letra_surf.get_height() - 5
        tela.blit(letra_surf, (pos_x_letra, pos_y_letra))

        # Coordenadas de Linha (1-8)
        rank_num = ranks[i] if invertido else ranks[7 - i]
        e_casa_clara_num = (i + coluna_visual_num) % 2 == 0
        cor_texto_num = cor_escura_atual if e_casa_clara_num else cor_clara_atual
        rank_surf = fonte_coord.render(rank_num, True, cor_texto_num)

        pos_x_num = coluna_visual_num * tam + 5
        pos_y_num = i * tam + 5
        tela.blit(rank_surf, (pos_x_num, pos_y_num))


# --- Funções de Menus e Interface ---

def desenhar_menu(tela, fontes):
    """Desenha o menu inicial e retorna os retângulos dos botões."""
    tela.fill((0, 0, 0))
    titulo = fontes["titulo"].render("Xadrez", True, (255, 255, 255))
    tela.blit(
        titulo,
        titulo.get_rect(center=(config.LARGURA_JANELA // 2, config.ALTURA_JANELA // 4 - 20)),
    )

    pos_y_inicial = config.ALTURA_JANELA // 2 - 100
    espacamento_y = 100
    centro_x = config.LARGURA_JANELA // 2

    ret_historia = pygame.Rect(0, 0, 300, 80)
    ret_historia.center = (centro_x, pos_y_inicial)
    pygame.draw.rect(tela, (255, 255, 255), ret_historia, border_radius=10)
    txt_historia = fontes["botao"].render("Modo História", True, (0, 0, 0))
    tela.blit(txt_historia, txt_historia.get_rect(center=ret_historia.center))

    ret_iniciar = pygame.Rect(0, 0, 300, 80)
    ret_iniciar.center = (centro_x, pos_y_inicial + espacamento_y)
    pygame.draw.rect(tela, (255, 255, 255), ret_iniciar, border_radius=10)
    txt_iniciar = fontes["botao"].render("Partida Rápida", True, (0, 0, 0))
    tela.blit(txt_iniciar, txt_iniciar.get_rect(center=ret_iniciar.center))

    ret_sair = pygame.Rect(0, 0, 300, 80)
    ret_sair.center = (centro_x, pos_y_inicial + 2 * espacamento_y)
    pygame.draw.rect(tela, (100, 100, 100), ret_sair, border_radius=10)
    txt_sair = fontes["botao"].render("Sair", True, (255, 255, 255))
    tela.blit(txt_sair, txt_sair.get_rect(center=ret_sair.center))

    return ret_historia, ret_iniciar, ret_sair


def desenhar_menu_modo_jogo(tela, fontes):
    """Desenha o menu de escolha de modo (PvA vs PvP)."""
    tela.fill((0, 0, 0))
    centro_x = config.LARGURA_JANELA // 2
    meio_y = config.ALTURA_JANELA // 2

    titulo = fontes["final"].render("Escolha o Modo", True, (255, 255, 255))
    tela.blit(titulo, titulo.get_rect(center=(centro_x, config.ALTURA_JANELA // 4)))

    txt_pva = fontes["botao"].render("Jogador vs. IA", True, (0, 0, 0))
    ret_pva = pygame.Rect(0, 0, txt_pva.get_width() + 40, 80)
    ret_pva.center = (centro_x, meio_y - 100)
    pygame.draw.rect(tela, (255, 255, 255), ret_pva, border_radius=10)
    tela.blit(txt_pva, txt_pva.get_rect(center=ret_pva.center))

    txt_pvp = fontes["botao"].render("Jogador vs. Jogador", True, (0, 0, 0))
    ret_pvp = pygame.Rect(0, 0, txt_pvp.get_width() + 40, 80)
    ret_pvp.center = (centro_x, meio_y)
    pygame.draw.rect(tela, (255, 255, 255), ret_pvp, border_radius=10)
    tela.blit(txt_pvp, txt_pvp.get_rect(center=ret_pvp.center))

    txt_voltar = fontes["botao"].render("Voltar", True, (0, 0, 0))
    ret_voltar = pygame.Rect(0, 0, 200, 80)
    ret_voltar.center = (centro_x, meio_y + 100)
    pygame.draw.rect(tela, (200, 200, 200), ret_voltar, border_radius=10)
    tela.blit(txt_voltar, txt_voltar.get_rect(center=ret_voltar.center))

    return ret_pva, ret_pvp, ret_voltar


def desenhar_menu_dificuldade_ia(tela, fontes):
    """Desenha o menu de seleção de dificuldade da IA."""
    tela.fill((0, 0, 0))
    centro_x = config.LARGURA_JANELA // 2
    meio_y = config.ALTURA_JANELA // 2

    titulo = fontes["final"].render("Escolha a Dificuldade", True, (255, 255, 255))
    tela.blit(titulo, titulo.get_rect(center=(centro_x, config.ALTURA_JANELA // 5)))

    retangulos_botoes = {}
    for i, nome in enumerate(config.DIFFICULTY_NAMES):
        texto_botao = fontes["botao"].render(nome, True, (0, 0, 0))
        cor_clara = config.CORES_TABULEIRO[nome]["claro"]

        ret_botao = pygame.Rect(0, 0, 300, 70)
        ret_botao.center = (centro_x, meio_y - 135 + (i * 90))
        pygame.draw.rect(tela, cor_clara, ret_botao, border_radius=10)
        tela.blit(texto_botao, texto_botao.get_rect(center=ret_botao.center))
        retangulos_botoes[nome] = ret_botao

    txt_voltar = fontes["botao"].render("Voltar", True, (0, 0, 0))
    ret_voltar = pygame.Rect(0, 0, 200, 70)
    ret_voltar.center = (centro_x, meio_y + 225)
    pygame.draw.rect(tela, (200, 200, 200), ret_voltar, border_radius=10)
    tela.blit(txt_voltar, txt_voltar.get_rect(center=ret_voltar.center))
    retangulos_botoes["Voltar"] = ret_voltar

    return retangulos_botoes


def desenhar_menu_tempo_pvp(tela, fontes):
    """Desenha o menu de escolha de tempo para partidas PvP."""
    tela.fill((0, 0, 0))
    centro_x = config.LARGURA_JANELA // 2
    meio_y = config.ALTURA_JANELA // 2

    titulo = fontes["final"].render("Escolha o Tempo", True, (255, 255, 255))
    tela.blit(titulo, titulo.get_rect(center=(centro_x, config.ALTURA_JANELA // 5)))

    retangulos_botoes = {}
    tempos = config.TEMPOS_PVP + ["Sem Tempo"]
    for i, tempo in enumerate(tempos):
        texto = f"{tempo} min" if isinstance(tempo, int) else "Sem Tempo"
        texto_botao = fontes["botao"].render(texto, True, (0, 0, 0))

        ret_botao = pygame.Rect(0, 0, 250, 70)
        ret_botao.center = (centro_x, meio_y - 180 + (i * 90))
        pygame.draw.rect(tela, (255, 255, 255), ret_botao, border_radius=10)
        tela.blit(texto_botao, texto_botao.get_rect(center=ret_botao.center))
        retangulos_botoes[tempo] = ret_botao

    txt_voltar = fontes["botao"].render("Voltar", True, (0, 0, 0))
    ret_voltar = pygame.Rect(0, 0, 200, 70)
    ret_voltar.center = (centro_x, meio_y + 270)
    pygame.draw.rect(tela, (200, 200, 200), ret_voltar, border_radius=10)
    tela.blit(txt_voltar, txt_voltar.get_rect(center=ret_voltar.center))
    retangulos_botoes["Voltar"] = ret_voltar

    return retangulos_botoes


def desenhar_menu_escolha_cor(tela, fontes):
    """Desenha o menu de escolha de cor das peças (Brancas ou Pretas)."""
    tela.fill((0, 0, 0))
    centro_x = config.LARGURA_JANELA // 2
    meio_y = config.ALTURA_JANELA // 2

    titulo = fontes["final"].render("Jogar como:", True, (255, 255, 255))
    tela.blit(titulo, titulo.get_rect(center=(centro_x, config.ALTURA_JANELA // 4)))

    txt_brancas = fontes["botao"].render("Brancas", True, (0, 0, 0))
    ret_brancas = pygame.Rect(0, 0, 200, 80)
    ret_brancas.center = (centro_x, meio_y - 100)
    pygame.draw.rect(tela, (238, 238, 210), ret_brancas, border_radius=10)
    tela.blit(txt_brancas, txt_brancas.get_rect(center=ret_brancas.center))

    txt_pretas = fontes["botao"].render("Pretas", True, (255, 255, 255))
    ret_pretas = pygame.Rect(0, 0, 200, 80)
    ret_pretas.center = (centro_x, meio_y)
    pygame.draw.rect(tela, (118, 150, 86), ret_pretas, border_radius=10)
    tela.blit(txt_pretas, txt_pretas.get_rect(center=ret_pretas.center))

    txt_voltar = fontes["botao"].render("Voltar", True, (0, 0, 0))
    ret_voltar = pygame.Rect(0, 0, 200, 80)
    ret_voltar.center = (centro_x, meio_y + 100)
    pygame.draw.rect(tela, (200, 200, 200), ret_voltar, border_radius=10)
    tela.blit(txt_voltar, txt_voltar.get_rect(center=ret_voltar.center))

    return ret_brancas, ret_pretas, ret_voltar


def desenhar_menu_promocao(tela, fontes, pecas_imagens, cor_jogador):
    """Desenha o modal de escolha de peça para promoção de peão."""
    overlay = _obter_surface_translucida(
        config.LARGURA_JANELA, config.ALTURA_JANELA, (0, 0, 0, 180)
    )
    tela.blit(overlay, (0, 0))

    tam = config.TAMANHO_QUADRADO
    largura_caixa = 4 * tam + 50
    altura_caixa = tam + 40
    pos_x_caixa = (config.LARGURA_JANELA - largura_caixa) // 2
    pos_y_caixa = (config.ALTURA_JANELA - altura_caixa) // 2

    pygame.draw.rect(
        tela,
        config.COR_FUNDO,
        (pos_x_caixa, pos_y_caixa, largura_caixa, altura_caixa),
        border_radius=15,
    )

    texto = fontes["botao"].render("Promover para:", True, (255, 255, 255))
    tela.blit(texto, (pos_x_caixa + 20, pos_y_caixa - 50))

    pecas_promocao = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    simbolos = ["Q", "R", "B", "N"] if cor_jogador == chess.WHITE else ["q", "r", "b", "n"]
    retangulos_clique = {}

    for i, peca in enumerate(pecas_promocao):
        img_peca = pecas_imagens.get(simbolos[i])
        if img_peca:
            pos_x = pos_x_caixa + 25 + i * tam
            pos_y = pos_y_caixa + 20
            retangulo = pygame.Rect(pos_x, pos_y, tam, tam)
            tela.blit(img_peca, retangulo.topleft)
            retangulos_clique[peca] = retangulo

    return retangulos_clique


def obter_rect_botao_reiniciar():
    """Retorna o retângulo do botão 'Menu' lateral sem precisar redesenhá-lo."""
    return pygame.Rect(840, config.ALTURA_JANELA // 2 - 25, 120, 50)


def desenhar_botao_reiniciar(tela, fontes):
    """Desenha o botão 'Menu' na barra lateral durante a partida."""
    retangulo_botao = obter_rect_botao_reiniciar()
    pygame.draw.rect(tela, (200, 50, 50), retangulo_botao, border_radius=5)
    texto_botao = fontes["reiniciar"].render("Menu", True, (255, 255, 255))
    tela.blit(texto_botao, texto_botao.get_rect(center=retangulo_botao.center))
    return retangulo_botao


def desenhar_mensagem_final(tela, fontes, texto_final):
    """Desenha o overlay de encerramento de partida."""
    overlay = _obter_surface_translucida(
        config.LARGURA_JANELA, config.ALTURA_JANELA, (0, 0, 0, 128)
    )
    tela.blit(overlay, (0, 0))

    texto_surf = fontes["final"].render(texto_final, True, (255, 255, 255))
    tela.blit(
        texto_surf,
        texto_surf.get_rect(center=(config.LARGURA_JANELA // 2, config.ALTURA_JANELA // 2)),
    )


# --- Funções de Desenho do Modo História ---

def desenhar_mapa(tela, assets_story, jogador_rect, inimigo_rect):
    """Renderiza o cenário de exploração e os personagens ativos."""
    tela.blit(assets_story["mapa_fundo"], (0, 0))
    if inimigo_rect.x >= 0:
        tela.blit(assets_story["inimigo"], inimigo_rect.topleft)
    tela.blit(assets_story["jogador"], jogador_rect.topleft)


def desenhar_caixa_dialogo(tela, fontes, speaker, texto, letras_visiveis):
    """Desenha a caixa de diálogo estilo RPG com efeito de máquina de escrever."""
    altura_caixa = 150
    caixa_rect = pygame.Rect(
        50,
        config.ALTURA_JANELA - altura_caixa - 50,
        config.LARGURA_JANELA - 100,
        altura_caixa,
    )

    pygame.draw.rect(tela, (0, 0, 0), caixa_rect, border_radius=10)
    pygame.draw.rect(tela, (255, 255, 255), caixa_rect, width=3, border_radius=10)

    if speaker:
        speaker_surface = fontes["reiniciar"].render(speaker, True, (0, 0, 0))
        speaker_rect = pygame.Rect(
            caixa_rect.x + 30,
            caixa_rect.y - 30,
            speaker_surface.get_width() + 20,
            speaker_surface.get_height(),
        )
        pygame.draw.rect(tela, (255, 255, 255), speaker_rect, border_radius=5)
        tela.blit(speaker_surface, (speaker_rect.x + 10, speaker_rect.y))

    margem = 20
    largura_max_texto = caixa_rect.width - (margem * 2)
    palavras = texto.split(" ")
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        teste_linha = linha_atual + palavra + " "
        if fontes["dialogo"].size(teste_linha)[0] < largura_max_texto:
            linha_atual = teste_linha
        else:
            linhas.append(linha_atual)
            linha_atual = palavra + " "
    linhas.append(linha_atual)

    y_texto = caixa_rect.y + margem
    letras_renderizadas = 0

    for linha in linhas:
        if letras_renderizadas >= letras_visiveis:
            break

        letras_restantes = letras_visiveis - letras_renderizadas
        texto_a_mostrar = linha[: min(len(linha), letras_restantes)]

        texto_surface = fontes["dialogo"].render(texto_a_mostrar, True, (255, 255, 255))
        tela.blit(texto_surface, (caixa_rect.x + margem, y_texto))

        y_texto += fontes["dialogo"].get_linesize()
        letras_renderizadas += len(texto_a_mostrar)

    if letras_visiveis >= len(texto):
        indicador = fontes["reiniciar"].render("Pressione Enter...", True, (200, 200, 200))
        pos_ind = (
            caixa_rect.right - indicador.get_width() - 15,
            caixa_rect.bottom - indicador.get_height() - 10,
        )
        tela.blit(indicador, pos_ind)


def desenhar_tela_encontro(
    tela, fontes, assets_story, portrait_id, speaker, texto, letras_visiveis
):
    """Desenha a cena de diálogo com retrato do personagem em destaque."""
    tela.blit(assets_story["mapa_fundo"], (0, 0))
    overlay = _obter_surface_translucida(
        config.LARGURA_JANELA, config.ALTURA_JANELA, (0, 0, 0, 150)
    )
    tela.blit(overlay, (0, 0))

    portrait = (
        assets_story["portrait_inimigo"]
        if portrait_id == "inimigo"
        else assets_story["portrait_jogador"]
    )
    portrait_rect = portrait.get_rect(
        center=(config.LARGURA_JANELA // 2, config.ALTURA_JANELA // 2)
    )
    tela.blit(portrait, portrait_rect)

    desenhar_caixa_dialogo(tela, fontes, speaker, texto, letras_visiveis)


def desenhar_iris_overlay(tela, raio):
    """Desenha o efeito de transição circular de abertura/fechamento de batalha."""
    if "iris_surface" not in _SURFACES_CACHE:
        surf = pygame.Surface((config.LARGURA_JANELA, config.ALTURA_JANELA))
        surf.set_colorkey((1, 2, 3))
        _SURFACES_CACHE["iris_surface"] = surf

    overlay = _SURFACES_CACHE["iris_surface"]
    overlay.fill((0, 0, 0))
    if raio > 0:
        centro_tela = (config.LARGURA_JANELA // 2, config.ALTURA_JANELA // 2)
        pygame.draw.circle(overlay, (1, 2, 3), centro_tela, int(raio))
    tela.blit(overlay, (0, 0))


def desenhar_tela_beta_fim(tela, fontes, mensagem):
    """Desenha a tela final de encerramento da demonstração do Modo História."""
    overlay = _obter_surface_translucida(
        config.LARGURA_JANELA, config.ALTURA_JANELA, (0, 0, 0, 180)
    )
    tela.blit(overlay, (0, 0))

    centro_x = config.LARGURA_JANELA // 2
    meio_y = config.ALTURA_JANELA // 2

    txt_principal = fontes["final"].render(mensagem, True, (255, 255, 255))
    tela.blit(txt_principal, txt_principal.get_rect(center=(centro_x, meio_y - 30)))

    txt_instrucao = fontes["reiniciar"].render(
        "Pressione Enter ou Clique para voltar ao Menu", True, (200, 200, 200)
    )
    tela.blit(txt_instrucao, txt_instrucao.get_rect(center=(centro_x, meio_y + 30)))