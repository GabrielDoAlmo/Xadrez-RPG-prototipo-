# engine.py
# Responsabilidade: Gerenciar a comunicação UCI com o motor Stockfish de forma oculta.

import sys
import os
import subprocess
import chess.engine


class ChessEngine:
    def __init__(self, stockfish_path):
        self.stockfish_path = stockfish_path
        self.engine = None
        self.transport = None
        self.limite_atual = chess.engine.Limit(time=0.5)

    async def start_engine(self):
        """Inicia o processo do Stockfish de forma totalmente oculta (sem janela de prompt)."""
        try:
            await self.quit_engine()

            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            self.transport, self.engine = await chess.engine.popen_uci(
                self.stockfish_path, startupinfo=startupinfo
            )
            print("Stockfish iniciado com sucesso (modo oculto).")
        except Exception as e:
            print(f"Erro ao iniciar o Stockfish: {e}")
            self.engine = None
            self.transport = None

    async def quit_engine(self):
        """Encerra o processo do Stockfish com segurança."""
        if self.engine:
            try:
                await self.engine.quit()
                print("Stockfish encerrado.")
            except Exception:
                pass
            finally:
                self.engine = None
                self.transport = None

    async def set_move_elo(self, elo_alvo):
        """Configura a força da IA com suporte a ELO ou Skill Level."""
        if not self.engine:
            return

        try:
            opcoes = self.engine.options
            min_elo_uci = opcoes["UCI_Elo"].min if "UCI_Elo" in opcoes else 1320
            max_elo_uci = opcoes["UCI_Elo"].max if "UCI_Elo" in opcoes else 3190

            if elo_alvo < min_elo_uci:
                if elo_alvo <= 150:
                    skill = 0
                    profundidade = 1
                elif elo_alvo <= 500:
                    skill = max(0, min(2, elo_alvo // 200))
                    profundidade = 2
                else:
                    skill = max(3, min(6, (elo_alvo - 500) // 150 + 2))
                    profundidade = 4

                config_dict = {}
                if "UCI_LimitStrength" in opcoes:
                    config_dict["UCI_LimitStrength"] = False
                if "Skill Level" in opcoes:
                    config_dict["Skill Level"] = skill

                if config_dict:
                    await self.engine.configure(config_dict)
                self.limite_atual = chess.engine.Limit(depth=profundidade, time=0.3)
            else:
                elo_valido = max(min_elo_uci, min(max_elo_uci, int(elo_alvo)))
                config_dict = {}
                if "UCI_LimitStrength" in opcoes:
                    config_dict["UCI_LimitStrength"] = True
                if "UCI_Elo" in opcoes:
                    config_dict["UCI_Elo"] = elo_valido

                if config_dict:
                    await self.engine.configure(config_dict)
                self.limite_atual = chess.engine.Limit(time=0.5)

        except Exception as e:
            print(f"Erro ao configurar força da IA ({elo_alvo}): {e}")
            self.limite_atual = chess.engine.Limit(time=0.5)

    async def get_best_move(self, board):
        """Retorna a melhor jogada do Stockfish para o estado atual do tabuleiro."""
        if not self.engine:
            print("Stockfish não está rodando.")
            return None

        try:
            result = await self.engine.play(board, self.limite_atual)
            return result.move
        except Exception as e:
            print(f"Erro ao obter a jogada do Stockfish: {e}")
            return None