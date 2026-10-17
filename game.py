# game.py
# Responsabilidade: Gerenciar o estado da partida e histórico de capturas.

import chess


class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.pecas_capturadas_brancas = []
        self.pecas_capturadas_pretas = []

    def make_move(self, move):
        """
        Executa uma jogada no tabuleiro e registra eventuais peças capturadas.
        Chamado após o término da animação visual do movimento.
        """
        if self.board.is_en_passant(move):
            if self.board.turn == chess.WHITE:
                self.pecas_capturadas_pretas.append("p")
            else:
                self.pecas_capturadas_brancas.append("P")
        else:
            captura = self.board.piece_at(move.to_square)
            if captura:
                if captura.color == chess.WHITE:
                    self.pecas_capturadas_brancas.append(captura.symbol())
                else:
                    self.pecas_capturadas_pretas.append(captura.symbol())

        self.board.push(move)

    async def get_engine_move(self, engine):
        """Solicita à engine a melhor jogada para a posição atual."""
        if engine:
            return await engine.get_best_move(self.board)
        return None

    def is_game_over(self):
        """Verifica se a partida foi encerrada por xeque-mate ou empate."""
        return self.board.is_game_over()