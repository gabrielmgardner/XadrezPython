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

class Tabuleiro:
    def __init__(self):
        self.tabuleiro = [[None for _ in range(8)] for _ in range(8)]
        self.inicializar_tabuleiro()
        self.turno = 'branco'
        self.historico_movimentos = []

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
