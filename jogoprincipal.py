class JogoXadrez:
    def __init__(self):
        self.xadrez = Xadrez()

    def jogar(self):
        print("Bem-vindo ao Xadrez em Python!")
        print("Use notação de xadrez (ex: 'e2 e4')")
        
        while self.xadrez.jogo_ativo:
            self.xadrez.tabuleiro.mostrar_tabuleiro()
            print(f"Turno: {self.xadrez.tabuleiro.turno.capitalize()}")
            
            movimento = input("Digite seu movimento (ex: e2 e4) ou 'sair' para terminar: ")
            
            if movimento.lower() == 'sair':
                break
                
            try:
                origem, destino = movimento.split()
                if self.xadrez.movimento_valido(origem, destino):
                    self.executar_movimento(origem, destino)
                    self.xadrez.tabuleiro.turno = 'preto' if self.xadrez.tabuleiro.turno == 'branco' else 'branco'
                else:
                    print("Movimento inválido! Tente novamente.")
            except ValueError:
                print("Formato inválido! Use: 'origem destino' (ex: e2 e4)")

    def executar_movimento(self, origem, destino):
        origem_linha, origem_coluna = self.xadrez.tabuleiro.parse_posicao(origem)
        destino_linha, destino_coluna = self.xadrez.tabuleiro.parse_posicao(destino)
        
        peca = self.xadrez.tabuleiro.tabuleiro[origem_linha][origem_coluna]
        peca_destino = self.xadrez.tabuleiro.tabuleiro[destino_linha][destino_coluna]
        
        # Registra movimento no histórico
        self.xadrez.tabuleiro.historico_movimentos.append(
            (peca, peca.posicao, (destino_linha, destino_coluna), peca_destino)
        )
        
        # Executa movimento
        peca.movimentos += 1
        peca.posicao = (destino_linha, destino_coluna)
        self.xadrez.tabuleiro.tabuleiro[destino_linha][destino_coluna] = peca
        self.xadrez.tabuleiro.tabuleiro[origem_linha][origem_coluna] = None
        
        # Verifica se é xeque-mate
        if peca_destino and peca_destino.tipo == 'rei':
            print(f"Xeque-mate! {peca.cor.capitalize()} vence!")
            self.xadrez.jogo_ativo = False

# Executar o jogo
if __name__ == "__main__":
    jogo = JogoXadrez()
    jogo.jogar()
