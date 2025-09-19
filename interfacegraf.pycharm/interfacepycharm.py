import pygame
import sys
import os
from pygame.locals import *

# Inicializar o Pygame
pygame.init()

# Cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (200, 200, 200)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
MARROM_CLARO = (222, 184, 135)
MARROM_ESCURO = (139, 69, 19)

# Configurações da janela
LARGURA, ALTURA = 800, 800
TAMANHO_CASA = 80
MARGEM = 50

# Configurações do tabuleiro
LINHAS, COLUNAS = 8, 8

# Criar a janela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Xadrez em Python')

# Carregar imagens das peças
def carregar_imagens():
    imagens = {}
    pecas = ['peao', 'cavalo', 'bispo', 'torre', 'rainha', 'rei']
    cores = ['branco', 'preto']
    
    for cor in cores:
        for peca in pecas:
            try:
                # Tenta carregar a imagem (você precisará ter essas imagens na pasta)
                imagem = pygame.image.load(f'imagens/{peca}_{cor}.png')
                imagem = pygame.transform.scale(imagem, (TAMANHO_CASA - 20, TAMANHO_CASA - 20))
                imagens[f'{peca}_{cor}'] = imagem
            except:
                # Se não encontrar a imagem, desenha uma peça simples
                surf = pygame.Surface((TAMANHO_CASA - 20, TAMANHO_CASA - 20), pygame.SRCALPHA)
                if cor == 'branco':
                    cor_desenho = BRANCO
                else:
                    cor_desenho = PRETO
                
                if peca == 'peao':
                    pygame.draw.ellipse(surf, cor_desenho, (10, 20, 60, 60))
                elif peca == 'cavalo':
                    pygame.draw.polygon(surf, cor_desenho, [(40, 10), (70, 30), (60, 70), (20, 70), (10, 30)])
                elif peca == 'bispo':
                    pygame.draw.polygon(surf, cor_desenho, [(40, 10), (60, 30), (55, 70), (25, 70), (20, 30)])
                elif peca == 'torre':
                    pygame.draw.rect(surf, cor_desenho, (20, 10, 40, 70))
                elif peca == 'rainha':
                    pygame.draw.polygon(surf, cor_desenho, [(40, 10), (60, 30), (50, 70), (30, 70), (20, 30)])
                elif peca == 'rei':
                    pygame.draw.polygon(surf, cor_desenho, [(40, 10), (60, 25), (55, 40), (65, 70), (15, 70), (25, 40), (20, 25)])
                    pygame.draw.rect(surf, cor_desenho, (35, 10, 10, 15))
                
                imagens[f'{peca}_{cor}'] = surf
    
    return imagens

# Classe para representar uma peça de xadrez
class Peca:
    def __init__(self, cor, tipo, posicao):
        self.cor = cor  # 'branco' ou 'preto'
        self.tipo = tipo  # 'rei', 'rainha', 'torre', 'bispo', 'cavalo', 'peao'
        self.posicao = posicao  # (linha, coluna)
        self.movimentos = 0
        self.selecionada = False

    def copiar(self):
        nova_peca = Peca(self.cor, self.tipo, self.posicao)
        nova_peca.movimentos = self.movimentos
        return nova_peca

# Classe para representar o tabuleiro de xadrez
class Tabuleiro:
    def __init__(self):
        self.tabuleiro = [[None for _ in range(8)] for _ in range(8)]
        self.inicializar_tabuleiro()
        self.turno = 'branco'
        self.historico_movimentos = []
        self.rei_branco_pos = (7, 4)
        self.rei_preto_pos = (0, 4)
        self.ultimo_movimento_peao_duplo = None
        self.peca_promocao = None
        self.origem_selecionada = None

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

    def coordenadas_para_posicao(self, x, y):
        """Converte coordenadas de tela para posição no tabuleiro"""
        if x < MARGEM or y < MARGEM or x >= MARGEM + 8*TAMANHO_CASA or y >= MARGEM + 8*TAMANHO_CASA:
            return None
        col = (x - MARGEM) // TAMANHO_CASA
        linha = (y - MARGEM) // TAMANHO_CASA
        return (linha, col)

    def posicao_para_coordenadas(self, linha, coluna):
        """Converte posição no tabuleiro para coordenadas de tela"""
        x = MARGEM + coluna * TAMANHO_CASA
        y = MARGEM + linha * TAMANHO_CASA
        return (x, y)

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

    def desenhar(self, tela, imagens):
        # Desenha o tabuleiro
        for linha in range(8):
            for coluna in range(8):
                x = MARGEM + coluna * TAMANHO_CASA
                y = MARGEM + linha * TAMANHO_CASA
                
                # Alterna as cores das casas
                if (linha + coluna) % 2 == 0:
                    cor = MARROM_CLARO
                else:
                    cor = MARROM_ESCURO
                
                pygame.draw.rect(tela, cor, (x, y, TAMANHO_CASA, TAMANHO_CASA))
                
                # Desenha a peça se houver uma
                peca = self.tabuleiro[linha][coluna]
                if peca:
                    img = imagens[f'{peca.tipo}_{peca.cor}']
                    tela.blit(img, (x + 10, y + 10))
                
                # Destaca a casa selecionada
                if self.origem_selecionada and self.origem_selecionada == (linha, coluna):
                    pygame.draw.rect(tela, AMARELO, (x, y, TAMANHO_CASA, TAMANHO_CASA), 3)
        
        # Desenha as letras e números das bordas
        fonte = pygame.font.SysFont('Arial', 20)
        for i in range(8):
            # Letras (a-h)
            letra = chr(ord('a') + i)
            texto = fonte.render(letra, True, PRETO)
            tela.blit(texto, (MARGEM + i * TAMANHO_CASA + TAMANHO_CASA//2 - 5, ALTURA - MARGEM + 10))
            tela.blit(texto, (MARGEM + i * TAMANHO_CASA + TAMANHO_CASA//2 - 5, MARGEM - 30))
            
            # Números (1-8)
            numero = str(8 - i)
            texto = fonte.render(numero, True, PRETO)
            tela.blit(texto, (MARGEM - 30, MARGEM + i * TAMANHO_CASA + TAMANHO_CASA//2 - 10))
            tela.blit(texto, (LARGURA - MARGEM + 10, MARGEM + i * TAMANHO_CASA + TAMANHO_CASA//2 - 10))
        
        # Desenha informações do jogo
        fonte = pygame.font.SysFont('Arial', 24)
        texto_turno = fonte.render(f"Turno: {self.turno.capitalize()}", True, PRETO)
        tela.blit(texto_turno, (20, 20))

# Classe principal do jogo de xadrez
class Xadrez:
    def __init__(self):
        self.tabuleiro = Tabuleiro()
        self.jogo_ativo = True
        self.estado = "Em andamento"
        self.movimentos_validos = []

    def movimento_valido(self, origem, destino):
        linha_origem, coluna_origem = origem
        linha_destino, coluna_destino = destino
        
        peca = self.tabuleiro.tabuleiro[linha_origem][coluna_origem]
        if not peca or peca.cor != self.tabuleiro.turno:
            return False

        peca_destino = self.tabuleiro.tabuleiro[linha_destino][coluna_destino]

        # Verifica se é um roque
        if peca.tipo == 'rei' and abs(coluna_origem - coluna_destino) == 2:
            return self.roque_valido(peca, (linha_destino, coluna_destino))

        # Verifica se é um en passant
        if peca.tipo == 'peao' and coluna_origem != coluna_destino and not peca_destino:
            return self.en_passant_valido(peca, (linha_destino, coluna_destino))

        # Verifica se há uma peça da mesma cor no destino
        if peca_destino and peca_destino.cor == peca.cor:
            return False

        # Implementa regras de movimento específicas para cada peça
        movimento_valido = False
        if peca.tipo == 'peao':
            movimento_valido = self.movimento_peao_valido(peca, (linha_destino, coluna_destino))
        elif peca.tipo == 'torre':
            movimento_valido = self.movimento_torre_valido(peca, (linha_destino, coluna_destino))
        elif peca.tipo == 'cavalo':
            movimento_valido = self.movimento_cavalo_valido(peca, (linha_destino, coluna_destino))
        elif peca.tipo == 'bispo':
            movimento_valido = self.movimento_bispo_valido(peca, (linha_destino, coluna_destino))
        elif peca.tipo == 'rainha':
            movimento_valido = self.movimento_rainha_valido(peca, (linha_destino, coluna_destino))
        elif peca.tipo == 'rei':
            movimento_valido = self.movimento_rei_valido(peca, (linha_destino, coluna_destino))

        # Verifica se o movimento deixa o próprio rei em xeque
        if movimento_valido:
            tabuleiro_teste = self.tabuleiro.copiar()
            self.executar_movimento_teste(tabuleiro_teste, origem, destino)
            if self.esta_em_xeque(tabuleiro_teste, self.tabuleiro.turno):
                movimento_valido = False

        return movimento_valido

    def movimento_peao_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        linha_destino, coluna_destino = destino
        direcao = -1 if peca.cor == 'branco' else 1

        # Movimento para frente
        if coluna_atual == coluna_destino:
            # Movimento simples
            if linha_destino == linha_atual + direcao and not self.tabuleiro.tabuleiro[linha_destino][coluna_destino]:
                return True
            # Primeiro movimento (duas casas)
            if (peca.movimentos == 0 and linha_destino == linha_atual + 2 * direcao and 
                not self.tabuleiro.tabuleiro[linha_atual + direcao][coluna_atual] and 
                not self.tabuleiro.tabuleiro[linha_destino][coluna_destino]):
                return True

        # Captura normal
        elif abs(coluna_atual - coluna_destino) == 1 and linha_destino == linha_atual + direcao:
            peca_destino = self.tabuleiro.tabuleiro[linha_destino][coluna_destino]
            if peca_destino and peca_destino.cor != peca.cor:
                return True

        return False

    def movimento_cavalo_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        linha_destino, coluna_destino = destino
        
        dx = abs(linha_destino - linha_atual)
        dy = abs(coluna_destino - coluna_atual)
        
        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)

    def movimento_rei_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        linha_destino, coluna_destino = destino
        
        dx = abs(linha_destino - linha_atual)
        dy = abs(coluna_destino - coluna_atual)
        
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
        linha_destino, coluna_destino = destino
        
        if linha_atual != linha_destino and coluna_atual != coluna_destino:
            return False
        
        return self.caminho_livre(linha_atual, coluna_atual, linha_destino, coluna_destino)

    def movimento_diagonal_valido(self, peca, destino):
        linha_atual, coluna_atual = peca.posicao
        linha_destino, coluna_destino = destino
        
        if abs(linha_destino - linha_atual) != abs(coluna_destino - coluna_atual):
            return False
        
        return self.caminho_livre(linha_atual, coluna_atual, linha_destino, coluna_destino)

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
        linha_origem, coluna_origem = origem
        linha_destino, coluna_destino = destino
        
        peca = tabuleiro_teste.tabuleiro[linha_origem][coluna_origem]
        
        # Atualiza posição do rei se necessário
        if peca.tipo == 'rei':
            tabuleiro_teste.atualizar_posicao_rei(peca.cor, (linha_destino, coluna_destino))
        
        # Executa movimento
        peca.movimentos += 1
        peca.posicao = (linha_destino, coluna_destino)
        tabuleiro_teste.tabuleiro[linha_destino][coluna_destino] = peca
        tabuleiro_teste.tabuleiro[linha_origem][coluna_origem] = None

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
                    if self.pode_capturar_rei(peca, (i, j), (rei_linha, rei_coluna), tabuleiro):
                        return True
        
        return False

    def pode_capturar_rei(self, peca, posicao_peca, posicao_rei, tabuleiro):
        linha_peca, coluna_peca = posicao_peca
        linha_rei, coluna_rei = posicao_rei
        
        if peca.tipo == 'peao':
            direcao = -1 if peca.cor == 'branco' else 1
            return (abs(coluna_peca - coluna_rei) == 1 and 
                    linha_rei == linha_peca + direcao)
        
        elif peca.tipo == 'cavalo':
            dx = abs(linha_rei - linha_peca)
            dy = abs(coluna_rei - coluna_peca)
            return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)
        
        elif peca.tipo == 'rei':
            dx = abs(linha_rei - linha_peca)
            dy = abs(coluna_rei - coluna_peca)
            return dx <= 1 and dy <= 1
        
        elif peca.tipo == 'torre':
            if linha_peca != linha_rei and coluna_peca != coluna_rei:
                return False
            return self.caminho_livre_teste(tabuleiro, linha_peca, coluna_peca, linha_rei, coluna_rei)
        
        elif peca.tipo == 'bispo':
            if abs(linha_rei - linha_peca) != abs(coluna_rei - coluna_peca):
                return False
            return self.caminho_livre_teste(tabuleiro, linha_peca, coluna_peca, linha_rei, coluna_rei)
        
        elif peca.tipo == 'rainha':
            if (linha_peca != linha_rei and coluna_peca != coluna_rei and 
                abs(linha_rei - linha_peca) != abs(coluna_rei - coluna_peca)):
                return False
            return self.caminho_livre_teste(tabuleiro, linha_peca, coluna_peca, linha_rei, coluna_rei)
        
        return False

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
                    for x in range(8):
                        for y in range(8):
                            if self.movimento_valido((i, j), (x, y)):
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
            return False
        
        linha_atual, coluna_atual = rei.posicao
        linha_destino, coluna_destino = destino
        
        direcao = 1 if coluna_destino > coluna_atual else -1
        torre_col = 7 if direcao == 1 else 0
        
        torre = self.tabuleiro.tabuleiro[linha_atual][torre_col]
        if not torre or torre.tipo != 'torre' or torre.movimentos > 0:
            return False
        
        passo = direcao
        col = coluna_atual + passo
        while col != torre_col:
            if self.tabuleiro.tabuleiro[linha_atual][col]:
                return False
            col += passo
        
        for col_test in [coluna_atual, coluna_atual + direcao, coluna_atual + 2 * direcao]:
            if self.esta_em_xeque_em_posicao(rei.cor, linha_atual, col_test):
                return False
        
        return True

    def esta_em_xeque_em_posicao(self, cor, linha, coluna):
        tabuleiro_teste = self.tabuleiro.copiar()
        
        rei_linha_atual, rei_coluna_atual = tabuleiro_teste.rei_branco_pos if cor == 'branco' else tabuleiro_teste.rei_preto_pos
        tabuleiro_teste.tabuleiro[rei_linha_atual][rei_coluna_atual] = None
        
        rei = Peca(cor, 'rei', (linha, coluna))
        tabuleiro_teste.tabuleiro[linha][coluna] = rei
        
        if cor == 'branco':
            tabuleiro_teste.rei_branco_pos = (linha, coluna)
        else:
            tabuleiro_teste.rei_preto_pos = (linha, coluna)
        
        return self.esta_em_xeque(tabuleiro_teste, cor)

    def en_passant_valido(self, peao, destino):
        linha_atual, coluna_atual = peao.posicao
        linha_destino, coluna_destino = destino
        
        if abs(coluna_atual - coluna_destino) != 1:
            return False
        
        direcao = -1 if peao.cor == 'branco' else 1
        if linha_destino != linha_atual + direcao:
            return False
        
        if not self.tabuleiro.ultimo_movimento_peao_duplo:
            return False
        
        ultimo_linha, ultimo_coluna = self.tabuleiro.ultimo_movimento_peao_duplo
        peao_adversario = self.tabuleiro.tabuleiro[ultimo_linha][ultimo_coluna]
        
        if (peao_adversario and peao_adversario.tipo == 'peao' and 
            peao_adversario.cor != peao.cor and ultimo_coluna == coluna_destino and
            abs(ultimo_linha - linha_atual) == 1):
            return True
        
        return False

    def executar_movimento(self, origem, destino):
        linha_origem, coluna_origem = origem
        linha_destino, coluna_destino = destino
        
        peca = self.tabuleiro.tabuleiro[linha_origem][coluna_origem]
        peca_destino = self.tabuleiro.tabuleiro[linha_destino][coluna_destino]
        
        # Verifica se é um roque
        if peca.tipo == 'rei' and abs(coluna_origem - coluna_destino) == 2:
            self.executar_roque(peca, destino)
            return
        
        # Verifica se é um en passant
        if peca.tipo == 'peao' and coluna_origem != coluna_destino and not peca_destino:
            self.executar_en_passant(peca, destino)
            return
        
        # Registra movimento de peão duas casas para en passant
        if peca.tipo == 'peao' and abs(linha_origem - linha_destino) == 2:
            self.tabuleiro.ultimo_movimento_peao_duplo = (linha_destino, coluna_destino)
        else:
            self.tabuleiro.ultimo_movimento_peao_duplo = None
        
        # Registra movimento no histórico
        self.tabuleiro.historico_movimentos.append(
            (peca, peca.posicao, (linha_destino, coluna_destino), peca_destino)
        )
        
        # Atualiza posição do rei se necessário
        if peca.tipo == 'rei':
            self.tabuleiro.atualizar_posicao_rei(peca.cor, (linha_destino, coluna_destino))
        
        # Executa movimento
        peca.movimentos += 1
        peca.posicao = (linha_destino, coluna_destino)
        self.tabuleiro.tabuleiro[linha_destino][coluna_destino] = peca
        self.tabuleiro.tabuleiro[linha_origem][coluna_origem] = None
        
        # Verifica promoção de peão
        if peca.tipo == 'peao' and self.tabuleiro.verificar_promocao(peca, linha_destino):
            self.tabuleiro.peca_promocao = (linha_destino, coluna_destino)
        
        # Verifica xeque e xeque-mate
        adversario = 'preto' if self.tabuleiro.turno == 'branco' else 'branco'
        
        if self.esta_em_xeque(self.tabuleiro, adversario):
            if self.verificar_xeque_mate():
                self.estado = "Xeque-mate"
                self.jogo_ativo = False
            else:
                self.estado = "Xeque"
        else:
            self.estado = "Em andamento"
        
        # Muda o turno (a menos que haja uma promoção pendente)
        if not self.tabuleiro.peca_promocao:
            self.tabuleiro.turno = adversario

    def executar_roque(self, rei, destino):
        linha_atual, coluna_atual = rei.posicao
        linha_destino, coluna_destino = destino
        
        direcao = 1 if coluna_destino > coluna_atual else -1
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

    def executar_en_passant(self, peao, destino):
        linha_origem, coluna_origem = peao.posicao
        linha_destino, coluna_destino = destino
        
        # Move o peão
        peao.movimentos += 1
        peao.posicao = (linha_destino, coluna_destino)
        self.tabuleiro.tabuleiro[linha_destino][coluna_destino] = peao
        self.tabuleiro.tabuleiro[linha_origem][coluna_origem] = None
        
        # Captura o peão adversário (que está na mesma linha de origem)
        peao_adversario = self.tabuleiro.tabuleiro[linha_origem][coluna_destino]
        self.tabuleiro.tabuleiro[linha_origem][coluna_destino] = None
        
        # Registra movimento no histórico
        self.tabuleiro.historico_movimentos.append(
            (peao, (linha_origem, coluna_origem), (linha_destino, coluna_destino), peao_adversario)
        )
        
        # Verifica promoção de peão
        if peao.tipo == 'peao' and self.tabuleiro.verificar_promocao(peao, linha_destino):
            self.tabuleiro.peca_promocao = (linha_destino, coluna_destino)
        else:
            # Muda o turno
            self.tabuleiro.turno = 'preto' if self.tabuleiro.turno == 'branco' else 'branco'

    def promover_peao(self, nova_peca):
        """Promove um peão a uma nova peça"""
        if self.tabuleiro.peca_promocao:
            linha, coluna = self.tabuleiro.peca_promocao
            self.tabuleiro.promover_peao(linha, coluna, nova_peca)
            # Muda o turno após a promoção
              def promover_peao(self, nova_peca):
        """Promove um peão a uma nova peça"""
        if self.tabuleiro.peca_promocao:
            linha, coluna = self.tabuleiro.peca_promocao
            self.tabuleiro.promover_peao(linha, coluna, nova_peca)
            # Muda o turno após a promoção
            self.tabuleiro.turno = 'preto' if self.tabuleiro.turno == 'branco' else 'branco'

# Função para mostrar menu de promoção
def mostrar_menu_promocao(tela, x, y):
    pygame.draw.rect(tela, BRANCO, (x, y, 200, 200))
    pygame.draw.rect(tela, PRETO, (x, y, 200, 200), 2)
    
    fonte = pygame.font.SysFont('Arial', 20)
    texto = fonte.render("Escolha uma peça:", True, PRETO)
    tela.blit(texto, (x + 10, y + 10))
    
    opcoes = [
        ("Q - Rainha", "rainha"),
        ("R - Torre", "torre"),
        ("B - Bispo", "bispo"),
        ("N - Cavalo", "cavalo")
    ]
    
    for i, (texto_opcao, _) in enumerate(opcoes):
        texto = fonte.render(texto_opcao, True, PRETO)
        tela.blit(texto, (x + 20, y + 50 + i * 30))
    
    pygame.display.update()
    return opcoes

# Função principal
def main():
    xadrez = Xadrez()
    imagens = carregar_imagens()
    clock = pygame.time.Clock()
    
    # Fonte para texto
    fonte = pygame.font.SysFont('Arial', 24)
    
    # Variáveis de controle
    executando = True
    origem_selecionada = None
    movimentos_validos = []
    
    while executando:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                executando = False
            
            elif evento.type == MOUSEBUTTONDOWN and evento.button == 1:
                # Verifica se há promoção pendente
                if xadrez.tabuleiro.peca_promocao:
                    x, y = evento.pos
                    linha, coluna = xadrez.tabuleiro.peca_promocao
                    pos_tela = xadrez.tabuleiro.posicao_para_coordenadas(linha, coluna)
                    
                    # Mostra menu de promoção
                    opcoes = mostrar_menu_promocao(tela, pos_tela[0], pos_tela[1] - 100)
                    
                    # Verifica a escolha do usuário
                    for i, (_, peca) in enumerate(opcoes):
                        if pos_tela[0] <= x <= pos_tela[0] + 200 and pos_tela[1] - 100 + 50 + i * 30 <= y <= pos_tela[1] - 100 + 50 + i * 30 + 20:
                            xadrez.promover_peao(peca)
                            break
                
                else:
                    # Processa movimento normal
                    pos = xadrez.tabuleiro.coordenadas_para_posicao(*evento.pos)
                    if pos:
                        linha, coluna = pos
                        
                        if origem_selecionada:
                            # Tentativa de movimento
                            if (linha, coluna) in movimentos_validos:
                                xadrez.executar_movimento(origem_selecionada, (linha, coluna))
                                origem_selecionada = None
                                movimentos_validos = []
                            else:
                                # Seleciona nova peça
                                peca = xadrez.tabuleiro.tabuleiro[linha][coluna]
                                if peca and peca.cor == xadrez.tabuleiro.turno:
                                    origem_selecionada = (linha, coluna)
                                    xadrez.tabuleiro.origem_selecionada = origem_selecionada
                                    # Calcula movimentos válidos
                                    movimentos_validos = []
                                    for i in range(8):
                                        for j in range(8):
                                            if xadrez.movimento_valido(origem_selecionada, (i, j)):
                                                movimentos_validos.append((i, j))
                                else:
                                    origem_selecionada = None
                                    movimentos_validos = []
                        else:
                            # Seleciona peça
                            peca = xadrez.tabuleiro.tabuleiro[linha][coluna]
                            if peca and peca.cor == xadrez.tabuleiro.turno:
                                origem_selecionada = (linha, coluna)
                                xadrez.tabuleiro.origem_selecionada = origem_selecionada
                                # Calcula movimentos válidos
                                movimentos_validos = []
                                for i in range(8):
                                    for j in range(8):
                                        if xadrez.movimento_valido(origem_selecionada, (i, j)):
                                            movimentos_validos.append((i, j))
            
            elif evento.type == KEYDOWN:
                if evento.key == K_r:  # Tecla R para reiniciar
                    xadrez = Xadrez()
                    origem_selecionada = None
                    movimentos_validos = []
        
        # Limpa a tela
        tela.fill(CINZA)
        
        # Desenha o tabuleiro e as peças
        xadrez.tabuleiro.desenhar(tela, imagens)
        
        # Destaca movimentos válidos
        for linha, coluna in movimentos_validos:
            x, y = xadrez.tabuleiro.posicao_para_coordenadas(linha, coluna)
            pygame.draw.rect(tela, VERDE, (x, y, TAMANHO_CASA, TAMANHO_CASA), 3)
        
        # Mostra informações do jogo
        texto_turno = fonte.render(f"Turno: {xadrez.tabuleiro.turno.capitalize()}", True, PRETO)
        texto_estado = fonte.render(f"Estado: {xadrez.estado}", True, PRETO)
        texto_instrucoes = fonte.render("Pressione R para reiniciar", True, PRETO)
        
        tela.blit(texto_turno, (LARGURA - 200, 20))
        tela.blit(texto_estado, (LARGURA - 200, 50))
        tela.blit(texto_instrucoes, (LARGURA - 250, 80))
        
        # Verifica se o jogo terminou
        if not xadrez.jogo_ativo:
            texto_fim = fonte.render("Jogo terminado! Pressione R para reiniciar", True, VERMELHO)
            tela.blit(texto_fim, (LARGURA // 2 - 200, ALTURA // 2))
        
        # Atualiza a tela
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
            self.tabuleiro.t
