# config.py
# Responsabilidade: Armazenar todas as constantes e dados estáticos do jogo.

import sys
import os
import pygame

# --- Configurações da Janela e Resolução Virtual ---
LARGURA_LOGICA = 1000
ALTURA_LOGICA = 800

# Apelidos de compatibilidade para funções de desenho antigas
LARGURA_JANELA = LARGURA_LOGICA
ALTURA_JANELA = ALTURA_LOGICA

FPS = 60
COR_FUNDO = (40, 40, 40)

# Mude para True se quiser que o jogo abra diretamente em tela cheia com barras pretas nas bordas
TELA_CHEIA = False 

# --- Configurações do Tabuleiro ---
TAMANHO_QUADRADO = 800 // 8
TEMPOS_PVP = [5, 10, 15, 20]  # Minutos disponíveis para o modo PvP

# --- Caminhos de Arquivos (Dinâmicos e Portáteis com Suporte a Executável) ---
if getattr(sys, 'frozen', False):
    DIRETORIO_BASE = os.path.dirname(sys.executable)
else:
    DIRETORIO_BASE = os.path.dirname(os.path.abspath(__file__))

DIRETORIO_PECAS = os.path.join(DIRETORIO_BASE, "image")
DIRETORIO_STORY = os.path.join(DIRETORIO_BASE, "story_assets")


def localizar_stockfish():
    """Localiza automaticamente o executável do Stockfish na pasta 'stockfish'."""
    pasta_sf = os.path.join(DIRETORIO_BASE, "stockfish")
    caminho_padrao = os.path.join(pasta_sf, "stockfish-windows-x86-64-avx2.exe")
    if os.path.exists(caminho_padrao):
        return caminho_padrao

    if os.path.isdir(pasta_sf):
        for nome in os.listdir(pasta_sf):
            if nome.lower().startswith("stockfish") and (
                nome.lower().endswith(".exe") or "." not in nome
            ):
                return os.path.join(pasta_sf, nome)
    return caminho_padrao


STOCKFISH_PATH = localizar_stockfish()

# --- Cores das Skins de Tabuleiro ---
CORES_TABULEIRO = {
    "Médio": {
        "claro": (238, 238, 210),
        "escuro": (118, 150, 86),
    },
    "Fácil": {
        "claro": (230, 240, 255),
        "escuro": (170, 200, 230),
    },
    "Difícil": {
        "claro": (210, 220, 230),
        "escuro": (85, 120, 150),
    },
    "Insano": {
        "claro": (255, 170, 0),
        "escuro": (180, 50, 0),
    },
}

# --- Configurações de Dificuldade (ELO) ---
ELO_BRACKETS = {
    "Fácil":   [100, 200, 300, 400, 500],
    "Médio":   [900, 1000, 1100, 1200, 1300],
    "Difícil": [1700, 1800, 1900, 2000],
    "Insano":  [2100, 2200, 2300, 2400, 2500],
}
DIFFICULTY_NAMES = ["Fácil", "Médio", "Difícil", "Insano"]

# --- Configurações do Modo História ---
TAMANHO_TILE = 32
TAMANHO_PERSONAGEM = (70, 70)
TAMANHO_PORTRAIT = (400, 400)
VELOCIDADE_JOGADOR = 4
VELOCIDADE_TEXTO = 40
ANIMACAO_FRAMES = 10
VELOCIDADE_TRANSICAO = 35

POSICAO_INICIAL_JOGADOR = (90, 600)
POSICAO_INIMIGO_DAVID = (450, 460)

mapa_colisao = [
    [1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

DIALOGO_ENCONTRO_PONTE = [
    {"speaker": "Guardião da Ponte", "portrait": "inimigo", "text": "O que um moleque como você faz por aqui? Cai fora antes que eu te dê uma surra!"},
    {"speaker": "Aventureiro", "portrait": "jogador", "text": "Me deixe passar logo, seu saco de banha! Você não quer ver o quão forte eu sou."},
    {"speaker": "Guardião da Ponte", "portrait": "inimigo", "text": "HAHAHAHAHA! Você me tirou uma boa risada, menino."},
    {"speaker": "Guardião da Ponte", "portrait": "inimigo", "text": "Você não deve saber com quem está falando..."},
    {"speaker": "Aventureiro", "portrait": "jogador", "text": "E eu deveria saber quem você é?"},
    {"speaker": "Guardião da Ponte", "portrait": "inimigo", "text": "EU SOU O GRANDE DAVID!"},
    {"speaker": "DAVID", "portrait": "inimigo", "text": "DETENTOR DO TÍTULO DE GUARDIÃO DA PONTE, INVICTO EM 89 PARTIDAS!"},
    {"speaker": "DAVID", "portrait": "inimigo", "text": "EU NUNCA FUI DERROTADO! Você deveria ir para casa antes de se machucar."},
    {"speaker": "Aventureiro", "portrait": "jogador", "text": "Não tô nem aí pra quem você é. Eu vou te derrotar e passar por cima do lixo que você é!"},
]

DIALOGO_VITORIA_DAVID = [
    {"speaker": "DAVID", "portrait": "inimigo", "text": "Impossível! Como você me venceu?"},
    {"speaker": "DAVID", "portrait": "inimigo", "text": "Pode passar... mas não pense que este é o fim..."},
]

TELEPORTER_RECT = pygame.Rect(450, 550, 50, 50)
MENSAGEM_BETA_FIM = "Obrigado por jogar a versão Beta!"