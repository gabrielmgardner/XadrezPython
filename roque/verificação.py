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
