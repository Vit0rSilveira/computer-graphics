import pygame
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

# Estrutura para representar uma aresta
class Edge:
    def __init__(self, y_min, y_max, x, slope_inv):
        self.y_min = y_min
        self.y_max = y_max
        self.x = x  # x na y_min (valor atual de x)
        self.slope_inv = slope_inv  # 1/m (inverso da inclinação)
    
    def __lt__(self, other):
        return self.x < other.x

# Variáveis globais
current_polygon = []
polygons = []
drawing_mode = True
line_thickness = 2
fill_color = [0.0, 0.0, 1.0]  # Azul
window_width, window_height = 800, 600

def create_et(points):
    """Cria a Tabela de Lados (Edge Table)"""
    et = []
    n = len(points)
    
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
        
        # Ignora arestas horizontais
        if p1[1] == p2[1]:
            continue
        
        # Garante que p1.y <= p2.y
        if p1[1] > p2[1]:
            p1, p2 = p2, p1
        
        y_min = p1[1]
        y_max = p2[1]
        x = p1[0]
        slope_inv = (p2[0] - p1[0]) / (p2[1] - p1[1])
        
        et.append(Edge(y_min, y_max, x, slope_inv))
    
    # Ordena a ET por y_min
    et.sort(key=lambda edge: edge.y_min)
    return et

def fill_polygon(points):
    """Preenche o polígono usando o algoritmo de coerência de arestas"""
    if len(points) < 3:
        return
    
    # Cria a ET
    et = create_et(points)
    
    # Encontra y_min e y_max do polígono
    y_min = min(p[1] for p in points)
    y_max = max(p[1] for p in points)
    
    # Inicializa a AET
    aet = []
    
    # Configurações OpenGL para desenho de pontos
    glDisable(GL_LINE_SMOOTH)
    glPointSize(1.0)
    glColor3f(fill_color[0], fill_color[1], fill_color[2])
    glBegin(GL_POINTS)
    
    # Para cada linha de varredura
    for y in range(int(y_min), int(y_max) + 1):
        # Adiciona à AET as arestas que começam em y
        i = 0
        while i < len(et):
            if et[i].y_min == y:
                aet.append(et[i])
                et.pop(i)
            else:
                i += 1
        
        # Remove da AET as arestas que terminam em y
        aet = [edge for edge in aet if edge.y_max > y]
        
        # Ordena a AET por x
        aet.sort()
        
        # Preenche entre pares de arestas
        for i in range(0, len(aet), 2):
            if i + 1 < len(aet):
                x_start = int(aet[i].x)
                x_end = int(aet[i + 1].x)
                
                # Desenha pontos na linha horizontal
                for x in range(x_start, x_end + 1):
                    glVertex2i(x, y)
        
        # Atualiza x para próxima linha
        for edge in aet:
            edge.x += edge.slope_inv
    
    glEnd()
    glEnable(GL_LINE_SMOOTH)

def draw_polygon(points):
    """Desenha o contorno do polígono"""
    if len(points) < 2:
        return
    
    # Desenha o contorno
    glLineWidth(line_thickness)
    glColor3f(0.0, 0.0, 0.0)  # Preto
    glBegin(GL_LINE_LOOP)
    for p in points:
        glVertex2i(p[0], p[1])
    glEnd()
    
    # Desenha pontos de controle
    glPointSize(5.0)
    glColor3f(1.0, 0.0, 0.0)  # Vermelho
    glBegin(GL_POINTS)
    for p in points:
        glVertex2i(p[0], p[1])
    glEnd()

def draw_text(x, y, text):
    """Desenha texto na tela"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(0.0, 0.0, 0.0)
    glRasterPos2f(x, y)
    
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_interface():
    """Desenha a interface do usuário"""
    # Fundo da interface
    glColor3f(0.8, 0.8, 0.8)
    glBegin(GL_QUADS)
    glVertex2i(0, window_height)
    glVertex2i(window_width, window_height)
    glVertex2i(window_width, window_height - 40)
    glVertex2i(0, window_height - 40)
    glEnd()
    
    # Botões
    glColor3f(1.0, 1.0, 1.0)
    
    # Botão Desenhar
    glBegin(GL_QUADS)
    glVertex2i(10, window_height - 10)
    glVertex2i(90, window_height - 10)
    glVertex2i(90, window_height - 30)
    glVertex2i(10, window_height - 30)
    glEnd()
    
    # Botão Preencher
    glBegin(GL_QUADS)
    glVertex2i(100, window_height - 10)
    glVertex2i(180, window_height - 10)
    glVertex2i(180, window_height - 30)
    glVertex2i(100, window_height - 30)
    glEnd()
    
    # Botão Limpar
    glBegin(GL_QUADS)
    glVertex2i(190, window_height - 10)
    glVertex2i(270, window_height - 10)
    glVertex2i(270, window_height - 30)
    glVertex2i(190, window_height - 30)
    glEnd()
    
    # Botão Espessura
    glBegin(GL_QUADS)
    glVertex2i(280, window_height - 10)
    glVertex2i(360, window_height - 10)
    glVertex2i(360, window_height - 30)
    glVertex2i(280, window_height - 30)
    glEnd()
    
    # Botão Cor
    glBegin(GL_QUADS)
    glVertex2i(370, window_height - 10)
    glVertex2i(450, window_height - 10)
    glVertex2i(450, window_height - 30)
    glVertex2i(370, window_height - 30)
    glEnd()
    
    # Textos dos botões
    glColor3f(0.0, 0.0, 0.0)
    draw_text(15, window_height - 25, "Desenhar")
    draw_text(105, window_height - 25, "Preencher")
    draw_text(195, window_height - 25, "Limpar")
    draw_text(285, window_height - 25, f"Espessura: {line_thickness}")
    
    color_name = "Azul"
    if fill_color == [1.0, 0.0, 0.0]:
        color_name = "Vermelho"
    elif fill_color == [0.0, 1.0, 0.0]:
        color_name = "Verde"
    
    draw_text(375, window_height - 25, f"Cor: {color_name}")
    
    # Instruções
    draw_text(500, window_height - 25, "Clique para adicionar pontos. Pressione Enter para finalizar.")

def init_gl():
    """Inicializa as configurações do OpenGL"""
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Fundo branco
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

def handle_mouse_click(x, y):
    """Processa cliques do mouse"""
    global current_polygon, drawing_mode, polygons, line_thickness, fill_color
    
    # Ajusta coordenada y (OpenGL tem origem no canto inferior)
    y_adj = window_height - y
    
    # Verifica se clique foi na interface
    if y_adj < 40:
        # Botão Desenhar
        if 10 <= x <= 90:
            drawing_mode = True
            if current_polygon:
                polygons.append(current_polygon.copy())
            current_polygon = []
        
        # Botão Preencher
        elif 100 <= x <= 180:
            drawing_mode = False
            if current_polygon:
                polygons.append(current_polygon.copy())
                current_polygon = []
        
        # Botão Limpar
        elif 190 <= x <= 270:
            current_polygon = []
            polygons = []
        
        # Botão Espessura
        elif 280 <= x <= 360:
            line_thickness = (line_thickness % 5) + 1
        
        # Botão Cor
        elif 370 <= x <= 450:
            if fill_color == [0.0, 0.0, 1.0]:  # Azul
                fill_color = [1.0, 0.0, 0.0]   # Vermelho
            elif fill_color == [1.0, 0.0, 0.0]: # Vermelho
                fill_color = [0.0, 1.0, 0.0]   # Verde
            else:
                fill_color = [0.0, 0.0, 1.0]   # Azul
    
    # Adiciona ponto ao polígono se estiver no modo desenho
    elif drawing_mode and y_adj >= 40:
        current_polygon.append((x, y_adj))

def main():
    global current_polygon, polygons, drawing_mode, line_thickness, fill_color
    
    # Inicializa Pygame
    pygame.init()
    pygame.display.set_mode((window_width, window_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Preenchimento de Polígonos - Algoritmo de Coerência de Arestas")
    
    # Inicializa OpenGL
    init_gl()
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Botão esquerdo do mouse
                    x, y = event.pos
                    handle_mouse_click(x, y)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and drawing_mode and len(current_polygon) >= 3:
                    polygons.append(current_polygon.copy())
                    current_polygon = []
        
        # Limpa a tela
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Desenha todos os polígonos
        for polygon in polygons:
            if len(polygon) >= 3:
                fill_polygon(polygon)
                draw_polygon(polygon)
        
        # Desenha o polígono atual
        if current_polygon:
            if len(current_polygon) >= 3:
                fill_polygon(current_polygon)
            draw_polygon(current_polygon)
        
        # Desenha a interface
        draw_interface()
        
        # Atualiza a tela
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()