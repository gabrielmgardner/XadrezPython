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
