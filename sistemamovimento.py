class Xadrez:
    def __init__(self):
        self.tabuleiro = Tabuleiro()
        self.jogo_ativo = True

    def movimento_valido(self, origem, destino):
        peca = self.tabuleiro.obter_peca(origem)
        if not peca or peca.cor != self.tabuleiro.turno:
            return False

        destino_linha, destino_coluna = self.tabuleiro.parse_posicao(destino)
        peca_destino = self.tabuleiro.tabuleiro[destino_linha][destino_coluna]

        # Verifica se há uma peça da mesma cor no destino
        if peca_destino and peca_destino.cor == peca.cor:
            return False

        # Implementa regras de movimento específicas para cada peça
        if peca.tipo == 'peao':
            return self.movimento_peao_valido(peca, destino)
        elif peca.tipo == 'torre':
            return self.movimento_torre_valido(peca, destino)
        elif peca.tipo == 'cavalo':
            return self.movimento_cavalo_valido(peca, destino)
        elif peca.tipo == 'bispo':
            return self.movimento_bispo_valido(peca, destino)
        elif peca.tipo == 'rainha':
            return self.movimento_rainha_valido(peca, destino)
        elif peca.tipo == 'rei':
            return self.movimento_rei_valido(peca, destino)

        return False

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

        # Captura
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
