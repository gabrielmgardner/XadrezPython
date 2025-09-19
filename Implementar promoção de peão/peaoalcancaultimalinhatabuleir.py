# Implementando Promoção de Peão no Xadrez

Vou implementar a promoção de peão, que ocorre quando um peão alcança a última linha do tabuleiro e pode ser promovido a uma rainha, torre, bispo ou cavalo.

```python
class Peca:
    def __init__(self, cor, tipo, posicao):
        self.cor = cor  # 'branco' ou 'preto'
        self.tipo = tipo  # 'rei', 'rainha', 'torre', 'bispo', 'cavalo', 'peao'
        self.posicao = posicao  # (linha, coluna)
        self.movimentos = 0

    def __str__(self):
        simbolos = {
            'rei': 'K', 'rainha': 'Q', 'torre': 'R',
            'bispo': 'B', 'cavalo': 'N', 'peao': 'P'
        }
        return simbolos[self.tipo] if self.cor == 'branco' else simbolos[self.tipo].lower()

    def copiar(self):
        nova_peca = Peca(self.cor, self.tipo, self.posicao)
        nova_peca.movimentos = self.movimentos
        return nova_peca


class Tabuleiro:
    def __init__(self):
        self.tabuleiro = [[None for _ in range(8)] for _ in range(8)]
        self.inicializar_tabuleiro()
        self.turno = 'branco'
        self.historico_movimentos = []
        self.rei_branco_pos = (7, 4)
        self.rei_preto_pos = (0, 4)
        self.ultimo_movimento_peao_duplo = None  # Para en passant
        self.peca_promocao = None  # Para controle de promoção

    def copiar(self):
        novoTabuleiro = Tabuleiro()
        novoTabuleiro.tabuleiro = [[None for _ in range(8)] for _ in range(8)]
        
        for i in range(8):
            for j in range(8):
                if self.tabuleiro[i][j]:
                    novoTabuleiro.tabuleiro[i][j] = self.tabuleiro[i][j].copiar()
        
        novoTabuleiro.turno = self.turno
        novoTabuleiro.rei_branco_pos = self.rei_branco_pos
        novoTabuleiro.rei_preto_pos = self.rei_preto_pos
        novoTabuleiro.ultimo_movimento_peao_duplo = self.ultimo_movimento_peao_duplo
        novoTabuleiro.peca_promocao = self.peca_promocao
        return novoTabuleiro

    def inicializar_tabuleiro(self):
        # Peões
        for col in range(8):
            self.tabuleiro[1][col] = Peca('preto', 'peao', (1, col))
            self.tabuleiro[6][col] = Peca('branco', 'peao', (6, col))

        # Peças principais
        pecas_linha = ['torre', 'cavalo', 'bispo', 'rainha', 'rei', 'bispo', 'cavalo', 'torre']
        
        for col, tipo in enumerate(pecas_linha):
            self.tabuleiro[0][col] = Peca('preto', tipo, (0, col))
            self.tabuleiro[7][col] = Peca('branco', tipo, (7, col))

    def mostrar_tabuleiro(self):
        print("  a b c d e f g h")
        print(" +-----------------+")
        for i in range(8):
            print(f"{8-i}|", end="")
            for j in range(8):
                peca = self.tabuleiro[i][j]
                print(f"{peca if peca else '. '}", end="")
            print(f"|{8-i}")
        print(" +-----------------+")
        print("  a b c d e f g h")

    def obter_peca(self, posicao):
        linha, coluna = self.parse_posicao(posicao)
        if 0 <= linha < 8 and 0 <= coluna < 8:
            return self.tabuleiro[linha][coluna]
        return None

    def parse_posicao(self, posicao):
        """Converte notação de xadrez (ex: 'e4') para coordenadas (linha, coluna)"""
        coluna = ord(posicao[0].lower()) - ord('a')
        linha = 8 - int(posicao[1])
        return linha, coluna

    def posicao_para_notacao(self, linha, coluna):
        """Converte coordenadas para notação de xadrez"""
        return f"{chr(ord('a') + coluna)}{8 - linha}"

    def atualizar_posicao_rei(self, cor, nova_posicao):
        if cor == 'branco':
            self.rei_branco_pos = nova_posicao
        else:
            self.rei_preto_pos = nova_posicao

    def verificar_promocao(self, peao, destino_linha):
        """Verifica se um peão chegou à última linha para promoção"""
        if peao.tipo == 'peao':
            if (peao.cor == 'branco' and destino_linha == 0) or (peao.cor == 'preto' and destino_linha == 7):
                return True
        return False

    def promover_peao(self, linha, coluna, nova_peca):
        """Promove um peão a uma nova peça"""
        cor = self.tabuleiro[linha][coluna].cor
        self.tabuleiro[linha][coluna] = Peca(cor, nova_peca, (linha, coluna))
        self.peca_promocao = None
        print(f"Peão promovido a {nova_peca}!")


class Xadrez:
    def __init__(self):
        self.tabuleiro = Tabuleiro()
        self.jogo_ativo = True
        self.estado = "Em andamento"  # "Em andamento", "Xeque", "Xeque-mate", "Empate"

    def movimento_valido(self, origem, destino):
        peca = self.tabuleiro.obter_peca(origem)
        if not peca or peca.cor != self.tabuleiro.turno:
            return False

        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        peca_destino = self.tabuleiro.tabuleiro[destino_linha][destino_coluna]

        # Verifica se é um roque
        if peca.tipo == 'rei' and abs(peca.posicao[1] - destino_coluna) == 2:
            return self.roque_valido(peca, destino)

        # Verifica se é um en passant
        if peca.tipo == 'peao' and peca.posicao[1] != destino_coluna and not peca_destino:
            return self.en_passant_valido(peca, destino)

        # Verifica se há uma peça da mesma cor no destino
        if peca_destino and peca_destino.cor == peca.cor:
            return False

        # Implementa regras de movimento específicas para cada peça
        movimento_valido = False
        if peca.tipo == 'peao':
            movimento_valido = self.movimento_peao_valido(peca, destino)
        elif peca.tipo == 'torre':
            movimento_valido = self.movimento_torre_valido(peca, destino)
        elif peca.tipo == 'cavalo':
            movimento_valido = self.movimento_cavalo_valido(peca, destino)
        elif peca.tipo == 'bispo':
            movimento_valido = self.movimento_bispo_valido(peca, destino)
        elif peca.tipo == 'rainha':
            movimento_valido = self.movimento_rainha_valido(peca, destino)
        elif peca.tipo == 'rei':
            movimento_valido = self.movimento_rei_valido(peca, destino)

        # Verifica se o movimento deixa o próprio rei em xeque
        if movimento_valido:
            # Cria uma cópia do tabuleiro para testar o movimento
            tabuleiro_teste = self.tabuleiro.copiar()
            self.executar_movimento_teste(tabuleiro_teste, origem, destino)
            
            # Verifica se o rei ficaria em xeque após o movimento
            if self.esta_em_xeque(tabuleiro_teste, self.tabuleiro.turno):
                movimento_valido = False

        return movimento_valido

    def movimento_peao_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        direcao = -1 if peca.cor == 'branco' else 1

        # Movimento para frente
        if coluna_atual == destino_coluna:
            # Movimento simples
            if destino_linha == linha_atual + direcao and not self.tabuleiro.tabuleiro[destino_linha][destino_coluna]:
                return True
            # Primeiro movimento (duas casas)
            if (peca.movimentos == 0 and destino_linha == linha_atual + 2 * direcao and 
                not self.tabuleiro.tabuleiro[linha_atual + direcao][coluna_atual] and 
                not self.tabuleiro.tabuleiro[destino_linha][destino_coluna]):
                return True

        # Captura normal
        elif abs(coluna_atual - destino_coluna) == 1 and destino_linha == linha_atual + direcao:
            peca_destino = self.tabuleiro.tabuleiro[destino_linha][destino_coluna]
            if peca_destino and peca_destino.cor != peca.cor:
                return True

        return False

    def movimento_cavalo_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        
        dx = abs(destino_linha - linha_atual)
        dy = abs(destino_coluna - coluna_atual)
        
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def movimento_rei_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        
        dx = abs(destino_linha - linha_atual)
        dy = abs(destino_coluna - coluna_atual)
        
        return dx <= 1 and dy <= 1

    def movimento_torre_valido(self, peca, destino):
        return self.movimento_linha_reta_valido(peca, destino)

    def movimento_bispo_valido(self, peca, destino):
        return self.movimento_diagonal_valido(peca, destino)

    def movimento_rainha_valido(self, peca, destino):
        return (self.movimento_linha_reta_valido(peca, destino) or 
                self.movimento_diagonal_valido(peca, destino))

    def movimento_linha_reta_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        
        if linha_atual != destino_linha and coluna_atual != destino_coluna:
            return False
        
        return self.caminho_livre(linha_atual, coluna_atual, destino_linha, destino_coluna)

    def movimento_diagonal_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        
        if abs(destino_linha - linha_atual) != abs(destino_coluna - coluna_atual):
            return False
        
        return self.caminho_livre(linha_atual, coluna_atual, destino_linha, destino_coluna)

    def caminho_livre(self, linha_origem, coluna_origem, linha_destino, coluna_destino):
        passo_linha = 1 if linha_destino > linha_origem else -1 if linha_destino < linha_origem else 0
        passo_coluna = 1 if coluna_destino > coluna_origem else -1 if coluna_destino < coluna_origem else 0
        
        linha, coluna = linha_origem + passo_linha, coluna_origem + passo_coluna
        
        while linha != linha_destino or coluna != coluna_destino:
            if self.tabuleiro.tabuleiro[linha][coluna]:
                return False
            linha += passo_linha
            coluna += passo_coluna
            
        return True

    def executar_movimento_teste(self, tabuleiro_teste, origem, destino):
        origem_linha, origem_coluna = tabuleiro_teste.parse_posicao(origem)
        destino_linha, destino_coluna = tabuleiro_teste.parse_posicao(destino)
        
        peca = tabuleiro_teste.tabuleiro[origem_linha][origem_coluna]
        
        # Atualiza posição do rei se necessário
        if peca.tipo == 'rei':
            tabuleiro_teste.atualizar_posicao_rei(peca.cor, (destino_linha, destino_coluna))
        
        # Executa movimento
        peca.movimentos += 1
        peca.posicao = (destino_linha, destino_coluna)
        tabuleiro_teste.tabuleiro[destino_linha][destino_coluna] = peca
        tabuleiro_teste.tabuleiro[origem_linha][origem_coluna] = None

    def esta_em_xeque(self, tabuleiro, cor):
        # Encontra a posição do rei
        rei_pos = tabuleiro.rei_branco_pos if cor == 'branco' else tabuleiro.rei_preto_pos
        rei_linha, rei_coluna = rei_pos
        
        # Verifica se alguma peça adversária pode capturar o rei
        for i in range(8):
            for j in range(8):
                peca = tabuleiro.tabuleiro[i][j]
                if peca and peca.cor != cor:
                    # Verifica se esta peça pode capturar o rei
                    destino = tabuleiro.posicao_para_notacao(rei_linha, rei_coluna)
                    origem = tabuleiro.posicao_para_notacao(i, j)
                    
                    if peca.tipo == 'peao':
                        if self.movimento_peao_valido_teste(tabuleiro, peca, destino):
                            return True
                    elif peca.tipo == 'cavalo':
                        if self.movimento_cavalo_valido_teste(peca, destino):
                            return True
                    elif peca.tipo == 'rei':
                        if self.movimento_rei_valido_teste(peca, destino):
                            return True
                    elif peca.tipo == 'torre':
                        if self.movimento_linha_reta_valido_teste(tabuleiro, peca, destino):
                            return True
                    elif peca.tipo == 'bispo':
                        if self.movimento_diagonal_valido_teste(tabuleiro, peca, destino):
                            return True
                    elif peca.tipo == 'rainha':
                        if (self.movimento_linha_reta_valido_teste(tabuleiro, peca, destino) or 
                            self.movimento_diagonal_valido_teste(tabuleiro, peca, destino)):
                            return True
        
        return False

    # Versões de teste dos métodos de movimento (sem verificar xeque)
    def movimento_peao_valido_teste(self, tabuleiro, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = tabuleiro.parse_posicao(destino)
        direcao = -1 if peca.cor == 'branco' else 1

        # Captura (para verificar xeque)
        if abs(coluna_atual - destino_coluna) == 1 and destino_linha == linha_atual + direcao:
            peca_destino = tabuleiro.tabuleiro[destino_linha][destino_coluna]
            if peca_destino and peca_destino.tipo == 'rei':
                return True

        return False

    def movimento_cavalo_valido_teste(self, peca, destino):
        return self.movimento_cavalo_valido(peca, destino)

    def movimento_rei_valido_teste(self, peca, destino):
        return self.movimento_rei_valido(peca, destino)

    def movimento_linha_reta_valido_teste(self, tabuleiro, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = tabuleiro.parse_posicao(destino)
        
        if linha_atual != destino_linha and coluna_atual != destino_coluna:
            return False
        
        return self.caminho_livre_teste(tabuleiro, linha_atual, coluna_atual, destino_linha, destino_coluna)

    def movimento_diagonal_valido_teste(self, tabuleiro, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        destino_linha, destino_coluna = tabuleiro.parse_posicao(destino)
        
        if abs(destino_linha - linha_atual) != abs(destino_coluna - coluna_atual):
            return False
        
        return self.caminho_livre_teste(tabuleiro, linha_atual, coluna_atual, destino_linha, destino_coluna)

    def caminho_livre_teste(self, tabuleiro, linha_origem, coluna_origem, linha_destino, coluna_destino):
        passo_linha = 1 if linha_destino > linha_origem else -1 if linha_destino < linha_origem else 0
        passo_coluna = 1 if coluna_destino > coluna_origem else -1 if coluna_destino < coluna_origem else 0
        
        linha, coluna = linha_origem + passo_linha, coluna_origem + passo_coluna
        
        while linha != linha_destino or coluna != coluna_destino:
            if tabuleiro.tabuleiro[linha][coluna]:
                return False
            linha += passo_linha
            coluna += passo_coluna
            
        return True

    def tem_movimentos_validos(self, cor):
        # Verifica se existem movimentos válidos para o jogador
        for i in range(8):
            for j in range(8):
                peca = self.tabuleiro.tabuleiro[i][j]
                if peca and peca.cor == cor:
                    origem = self.tabuleiro.posicao_para_notacao(i, j)
                    
                    # Testa todos os movimentos possíveis para esta peça
                    for x in range(8):
                        for y in range(8):
                            destino = self.tabuleiro.posicao_para_notacao(x, y)
                            if self.movimento_valido(origem, destino):
                                return True
        return False

    def verificar_xeque_mate(self):
        # Verifica se o jogador atual está em xeque-mate
        if self.esta_em_xeque(self.tabuleiro, self.tabuleiro.turno):
            if not self.tem_movimentos_validos(self.tabuleiro.turno):
                return True
        return False

    def roque_valido(self, rei, destino):
        if rei.movimentos > 0:
            return False  # Rei já se moveu, não pode fazer roque
        
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        linha_atual, coluna_atual = rei.posicao
        
        # Determina a direção do roque (curto ou longo)
        direcao = 1 if destino_coluna > coluna_atual else -1
        torre_col = 7 if direcao == 1 else 0
        
        # Verifica se a torre existe e não se moveu
        torre = self.tabuleiro.tabuleiro[linha_atual][torre_col]
        if not torre or torre.tipo != 'torre' or torre.movimentos > 0:
            return False
        
        # Verifica se o caminho está livre
        passo = direcao
        col = coluna_atual + passo
        while col != torre_col:
            if self.tabuleiro.tabuleiro[linha_atual][col]:
                return False  # Há uma peça no caminho
            col += passo
        
        # Verifica se o rei não está em xeque nem passa por casas em xeque
        for col_test in [coluna_atual, coluna_atual + direcao, coluna_atual + 2 * direcao]:
            if self.esta_em_xeque_em_posicao(rei.cor, linha_atual, col_test):
                return False
        
        return True

    def esta_em_xeque_em_posicao(self, cor, linha, coluna):
        """
        Verifica se o rei estaria em xeque em uma posição específica.
        Útil para verificar movimentos como o roque, onde o rei não pode passar por casas em xeque.
        """
        # Cria uma cópia do tabuleiro para teste
        tabuleiro_teste = self.tabuleiro.copiar()
        
        # Remove o rei da posição atual (se existir)
        rei_linha_atual, rei_coluna_atual = tabuleiro_teste.rei_branco_pos if cor == 'branco' else tabuleiro_teste.rei_preto_pos
        tabuleiro_teste.tabuleiro[rei_linha_atual][rei_coluna_atual] = None
        
        # Coloca o rei na nova posição
        rei = Peca(cor, 'rei', (linha, coluna))
        tabuleiro_teste.tabuleiro[linha][coluna] = rei
        
        # Atualiza a posição do rei no tabuleiro de teste
        if cor == 'branco':
            tabuleiro_teste.rei_branco_pos = (linha, coluna)
        else:
            tabuleiro_teste.rei_preto_pos = (linha, coluna)
        
        # Verifica se está em xeque
        return self.esta_em_xeque(tabuleiro_teste, cor)

    def en_passant_valido(self, peao, destino):
        linha_atual, coluna_atual = peao.posicao
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        
        # Verifica se é um movimento de peão válido para en passant
        if abs(coluna_atual - destino_coluna) != 1:
            return False
        
        direcao = -1 if peao.cor == 'branco' else 1
        if destino_linha != linha_atual + direcao:
            return False
        
        # Verifica se há um peão adversário que moveu duas casas no último movimento
        if not self.tabuleiro.ultimo_movimento_peao_duplo:
            return False
        
        ultimo_linha, ultimo_coluna = self.tabuleiro.ultimo_movimento_peao_duplo
        peao_adversario = self.tabuleiro.tabuleiro[ultimo_linha][ultimo_coluna]
        
        # Verifica se o peão adversário está na coluna correta e moveu duas casas
        if (peao_adversario and peao_adversario.tipo == 'peao' and 
            peao_adversario.cor != peao.cor and ultimo_coluna == destino_coluna and
            abs(ultimo_linha - linha_atual) == 1):
            return True
        
        return False

    def executar_movimento(self, origem, destino):
        origem_linha, origem_coluna = self.tabuleiro.parse_posicao(origem)
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        
        peca = self.tabuleiro.tabuleiro[origem_linha][origem_coluna]
        peca_destino = self.tabuleiro.tabuleiro[destino_linha][destino_coluna]
        
        # Verifica se é um roque
        if peca.tipo == 'rei' and abs(peca.posicao[1] - destino_coluna) == 2:
            self.executar_roque(peca, destino)
            return
        
        # Verifica se é um en passant
        if peca.tipo == 'peao' and peca.posicao[1] != destino_coluna and not peca_destino:
            self.executar_en_passant(peca, destino)
            return
        
        # Registra movimento de peão duas casas para en passant
        if peca.tipo == 'peao' and abs(origem_linha - destino_linha) == 2:
            self.tabuleiro.ultimo_movimento_peao_duplo = (destino_linha, destino_coluna)
        else:
            self.tabuleiro.ultimo_movimento_peao_duplo = None
        
        # Registra movimento no histórico
        self.tabuleiro.historico_movimentos.append(
            (peca, peca.posicao, (destino_linha, destino_coluna), peca_destino)
        )
        
        # Atualiza posição do rei se necessário
        if peca.tipo == 'rei':
            self.tabuleiro.atualizar_posicao_rei(peca.cor, (destino_linha, destino_coluna))
        
        # Executa movimento
        peca.movimentos += 1
        peca.posicao = (destino_linha, destino_coluna)
        self.tabuleiro.tabuleiro[destino_linha][destino_coluna] = peca
        self.tabuleiro.tabuleiro[origem_linha][origem_coluna] = None
        
        # Verifica promoção de peão
        if peca.tipo == 'peao' and self.tabuleiro.verificar_promocao(peca, destino_linha):
            self.tabuleiro.peca_promocao = (destino_linha, destino_coluna)
            print("Peão chegou à última linha! Escolha uma peça para promoção:")
            print("Q - Rainha, R - Torre, B - Bispo, N - Cavalo")
            # A promoção será tratada no loop principal
        
        # Verifica xeque e xeque-mate
        adversario = 'preto' if self.tabuleiro.turno == 'branco' else 'branco'
        
        if self.esta_em_xeque(self.tabuleiro, adversario):
            if self.verificar_xeque_mate():
                self.estado = "Xeque-mate"
                self.jogo_ativo = False
                print(f"Xeque-mate! {self.tabuleiro.turno.capitalize()} vence!")
            else:
                self.estado = "Xeque"
                print(f"Xeque! {adversario.capitalize()} está em xeque.")
        else:
            self.estado = "Em andamento"
        
        # Muda o turno (a menos que haja uma promoção pendente)
        if not self.tabuleiro.peca_promocao:
            self.tabuleiro.turno = adversario

    def executar_roque(self, rei, destino):
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        linha_atual, coluna_atual = rei.posicao
        
        # Determina a direção do roque (curto ou longo)
        direcao = 1 if destino_coluna > coluna_atual else -1
        torre_col = 7 if direcao == 1 else 0
        nova_coluna_rei = coluna_atual + 2 * direcao
        nova_coluna_torre = coluna_atual + direcao
        
        # Move o rei
        rei.movimentos += 1
        rei.posicao = (linha_atual, nova_coluna_rei)
        self.tabuleiro.tabuleiro[linha_atual][nova_coluna_rei] = rei
        self.tabuleiro.tabuleiro[linha_atual][coluna_atual] = None
        self.tabuleiro.atualizar_posicao_rei(rei.cor, (linha_atual, nova_coluna_rei))
        
        # Move a torre
        torre = self.tabuleiro.tabuleiro[linha_atual][torre_col]
        torre.movimentos += 1
        torre.posicao = (linha_atual, nova_coluna_torre)
        self.tabuleiro.tabuleiro[linha_atual][nova_coluna_torre] = torre
        self.tabuleiro.tabuleiro[linha_atual][torre_col] = None
        
        # Registra movimento no histórico
        self.tabuleiro.historico_movimentos.append(
            (rei, (linha_atual, coluna_atual), (linha_atual, nova_coluna_rei), None)
        )
        
        # Muda o turno
        self.tabuleiro.turno = 'preto' if self.tabuleiro.turno == 'branco' else 'branco'
        print(f"Roque {'curto' if direcao == 1 else 'longo'} executado!")

    def executar_en_passant(self, peao, destino):
        origem_linha, origem_coluna = peao.posicao
        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        
        # Move o peão
        peao.movimentos += 1
        peao.posicao = (destino_linha, destino_coluna)
        self.tabuleiro.tabuleiro[destino_linha][destino_coluna] = peao
        self.tabuleiro.tabuleiro[origem_linha][origem_coluna] = None
        
        # Captura o peão adversário (que está na mesma linha de origem)
        peao_adversario = self.tabuleiro.tabuleiro[origem_linha][destino_coluna]
        self.tabuleiro.tabuleiro[origem_linha][destino_coluna] = None
        
        # Registra movimento no histórico
        self.tabuleiro.historico_movimentos.append(
            (peao, (origem_linha, origem_coluna), (destino_linha, destino_coluna), peao_adversario)
        )
        
        # Verifica promoção de peão
        if peao.tipo == 'peao' and self.tabuleiro.verificar_promocao(peao, destino_linha):
            self.tabuleiro.peca_promocao = (destino_linha, destino_coluna)
            print("Peão chegou à última linha! Escolha uma peça para promoção:")
            print("Q - Rainha, R - Torre, B - Bispo, N - Cavalo")
        else:
            # Muda o turno
            self.tabuleiro.turno = 'preto' if self.tabuleiro.turno == 'branco' else 'branco'
        
        print("En passant executado!")

    def promover_peao(self, nova_peca):
        """Promove um peão a uma nova peça"""
        if self.tabuleiro.peca_promocao:
            linha, coluna = self.tabuleiro.peca_promocao
            self.tabuleiro.promover_peao(linha, coluna, nova_peca)
            # Muda o turno após a promoção
            self.tabuleiro.turno = 'preto' if self.tabuleiro.turno == 'branco' else 'branco'


class JogoXadrez:
    def __init__(self):
        self.xadrez = Xadrez()

    def jogar(self):
        print("Bem-vindo ao Xadrez em Python!")
        print("Use notação de xadrez (ex: 'e2 e4')")
        print("Roque: 'e1 g1' (curto) ou 'e1 c1' (longo)")
        print("En passant: mova o peão para capturar como se o peão adversário tivesse avançado apenas uma casa")
        
        while self.xadrez.jogo_ativo:
            self.xadrez.tabuleiro.mostrar_tabuleiro()
            print(f"Turno: {self.xadrez.tabuleiro.turno.capitalize()}")
            print(f"Estado: {self.xadrez.estado}")
            
            # Verifica se há uma promoção pendente
            if self.xadrez.tabuleiro.peca_promocao:
                self.tratar_promocao()
                continue
            
            movimento = input("Digite seu movimento (ex: e2 e4) ou 'sair' para terminar: ")
            
            if movimento.lower() == 'sair':
                break
                
            try:
                origem, destino = movimento.split()
                if self.xadrez.movimento_valido(origem, destino):
                    self.xadrez.executar_movimento(origem, destino)
                else:
                    print("Movimento inválido! Tente novamente.")
            except ValueError:
                print("Formato inválido! Use: 'origem destino' (ex: e2 e4)")

    def tratar_promocao(self):
        """Trata a promoção de um peão"""
        opcoes = {'Q': 'rainha', 'R': 'torre', 'B': 'bispo', 'N': 'cavalo'}
        
        while True:
            escolha = input("Escolha a peça para promoção (Q, R, B, N): ").upper()
            if escolha in opcoes:
                self.xadrez.promover_peao(opcoes[escolha])
                break
            else:
                print("Opção inválida! Escolha Q, R, B ou N.")

if __name__ == "__main__":
    jogo = JogoXadrez()
    jogo.jogar()
