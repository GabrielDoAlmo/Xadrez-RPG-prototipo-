# ♟️ Xadrez RPG: O Despertar da Tática

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.1-orange?style=for-the-badge&logo=pygame&logoColor=white)](https://www.pygame.org/)
[![Stockfish](https://img.shields.io/badge/Engine-Stockfish_UCI-green?style=for-the-badge&logo=chess&logoColor=white)](https://stockfishchess.org/)
[![Status](https://img.shields.io/badge/Status-Beta_Demo-yellow?style=for-the-badge)](https://github.com/GabrielDoAlmo/Xadrez-RPG-protótipo-/releases)

</div>

---

> **"Onde o xadrez tradicional encontra o RPG tático, diálogos marcantes e a inteligência implacável do Stockfish."**

---

## 🎮 Baixar e Jogar (Versão Pronta para Windows)

Não quer configurar o código-fonte? Pode descarregar a versão portátil completa (com o motor Stockfish, gráficos e assets embutidos). Basta extrair a pasta e executar o jogo!

<div align="center">
  <a href="https://github.com/GabrielDoAlmo/Xadrez-RPG-protótipo-/releases/latest">
    <img src="https://img.shields.io/badge/🎮%20BAIXAR%20XADREZ%20RPG%20(ZIP%20PRONTO)-Download%20Versão%20Portátil%20v1.0-brightgreen?style=for-the-badge&logo=windows&logoColor=white" alt="Download Xadrez RPG" width="480"/>
  </a>
</div>

---

## 🌟 Sobre o Projeto

O **Xadrez RPG** nasceu como um projeto ambicioso para transformar o clássico jogo de tabuleiro em uma experiência imersiva de progressão e narrativa. Desenvolvido em **Python** com **Pygame** e integrado ao motor profissional **Stockfish** via protocolo UCI, o jogo combina partidas táticas rigorosas com elementos de exploração de mapas, diálogos dinâmicos estilo RPG e uma arquitetura limpa preparada para futuras mecânicas caóticas e "poderes especiais" (trapaças táticas dentro do grid de 64 casas).

---

## 🕹️ Modos de Jogo

1. **Modo História (Demo Beta):**
   - Explore o cenário, movimente o seu personagem usando as teclas WASD ou as Setas do Teclado.
   - Encontre o infame David, o Guardião da Ponte, invicto em 89 partidas.
   - Supere os diálogos interativos (pressione Enter ou clique para avançar) e vença a partida de xadrez para desbloquear o caminho!
2. **Partida Rápida (PvA - Jogador vs. IA):**
   - Escolha o seu nível de dificuldade (Fácil, Médio, Difícil ou Insano) com diferentes brackets de ELO e Skill Levels geridos pelo Stockfish.
   - Jogue de Brancas ou de Pretas com tabuleiro invertido dinâmico e coordenadas nas bordas.
3. **Partida Rápida (PvP - Jogador vs. Jogador):**
   - Desafie um amigo localmente com cronômetros configuráveis por tempo de partida.

---

## ✨ Principais Funcionalidades Técnicas

- **Motor Oculto em Segundo Plano:** O Stockfish executa de forma totalmente invisível (sem janelas de prompt irritantes a saltar no Windows).
- **Renderização Virtual & Letterboxing:** Resolução lógica nativa de 1000x800 com suporte a ecrã cheio adaptativo e barras pretas automáticas. Pressione F11 a qualquer momento para alternar entre janela e tela cheia.
- **Sistema de Animação e Cache:** Movimentação interpolada das peças a 60 FPS estáveis, com miniaturas de peças capturadas pré-renderizadas para máxima eficiência de memória.
- **Arquitetura Modular:** Código desacoplado em main.py, drawing.py, engine.py, game.py, utils.py e config.py.

---

## 🛠️ Como Executar o Código-Fonte (Para Desenvolvedores)

Se preferir clonar o repositório e rodar o projeto diretamente pelo interpretador Python:

1. **Pré-requisitos:** Certifique-se de ter o Python 3.13+ instalado.
2. **Clone o repositório:**
   git clone https://github.com/GabrielDoAlmo/Xadrez-RPG-protótipo-.git
   cd Xadrez-RPG-protótipo-
3. **Instale as dependências:**
   pip install pygame python-chess
4. **Adicione o Stockfish:**
   Descarregue o executável do Stockfish e coloque-o dentro da pasta stockfish/ do projeto.
5. **Execute o jogo:**
   python main.py

---

## 🗺️ Roadmap / Futuras Atualizações

- [ ] Sistema de "Trapaças e Poderes Especiais" (ex: teletransporte de Dama, Cavalo com alcance estendido, reviver peças capturadas).
- [ ] IA capaz de calcular estrategicamente o uso dos poderes especiais utilizando simulações de FEN com o Stockfish.
- [ ] Novos chefes com baralhos de habilidades únicos no Modo História.

---

## 📄 Licença e Termos de Uso

Este projeto é desenvolvido com fins educacionais, de portfólio e com **lançamento comercial futuro planejado (ex: Steam)**. 

### ⚖️ Diretrizes de Uso:
1. **Código-Fonte (Fins Educacionais e de Estudo):** O código-fonte base disponibilizado neste repositório pode ser livremente estudado, modificado e utilizado por estudantes e desenvolvedores para fins de aprendizado e projetos pessoais.
2. **Propriedade Intelectual e Comercial:** O título, a identidade visual, o enredo e o conceito comercial de **Xadrez RPG** são de propriedade exclusiva do autor. 
3. **Restrições:** É **estritamente proibido** a terceiros publicar, distribuir ou lançar comercialmente qualquer jogo, build ou cópia utilizando o mesmo nome (**Xadrez RPG**) ou uma identidade visual idêntica que possa induzir os jogadores ao erro, visando proteger a propriedade intelectual para o lançamento oficial na Steam.
