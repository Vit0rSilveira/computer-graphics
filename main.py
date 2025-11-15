"""
Sistema de Visualização 3D com Modelos de Iluminação
Trabalho 2 - SCC 250 - Computação Gráfica

Este programa implementa um visualizador 3D interativo que permite:
- Visualizar objetos 3D (cubo, pirâmide, cilindro, esfera)
- Aplicar diferentes modelos de iluminação (Flat, Gouraud, Phong)
- Alternar entre projeções perspectiva e ortográfica
- Comparar os 3 modelos de iluminação lado a lado
- Controlar transformações geométricas (rotação, escala, translação)
- Manipular a posição da fonte de luz

Autores: [Nomes dos alunos]
Data: Novembro 2025
"""

import sys
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QComboBox,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QPainter, QFont, QColor
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class OpenGLWidget(QOpenGLWidget):
    """
    Widget OpenGL para renderização 3D de objetos com iluminação.
    
    Esta classe gerencia toda a renderização OpenGL, incluindo:
    - Configuração da cena 3D
    - Desenho de objetos geométricos
    - Aplicação de modelos de iluminação
    - Controle de câmera orbital
    - Modo de comparação entre modelos de iluminação
    
    Attributes:
        rotation_x (float): Rotação do objeto no eixo X (em graus)
        rotation_y (float): Rotação do objeto no eixo Y (em graus)
        rotation_z (float): Rotação do objeto no eixo Z (em graus)
        scale_factor (float): Fator de escala do objeto (1.0 = tamanho normal)
        translation_x (float): Translação no eixo X
        translation_y (float): Translação no eixo Y
        translation_z (float): Translação no eixo Z
        camera_distance (float): Distância da câmera até a origem
        camera_angle_x (float): Ângulo vertical da câmera (em graus)
        camera_angle_y (float): Ângulo horizontal da câmera (em graus)
        shading_model (str): Modelo de iluminação atual ('flat', 'gouraud', 'phong')
        light_pos (list): Posição da luz [x, y, z, w] onde w=1 para luz posicional
        object_type (str): Tipo de objeto a renderizar ('cube', 'pyramid', 'cylinder', 'sphere')
        projection_type (str): Tipo de projeção ('perspective', 'orthographic')
        comparison_mode (bool): Se True, mostra 3 objetos com diferentes iluminações
        animate (bool): Se True, anima a rotação do objeto
        last_pos (QPoint): Última posição do mouse (para controle de câmera)
    """
    
    def __init__(self, parent=None):
        """
        Inicializa o widget OpenGL.
        
        Args:
            parent (QWidget, optional): Widget pai. Default é None.
        """
        super().__init__(parent)
        self.rotation_x = 30
        self.rotation_y = 45
        self.rotation_z = 0
        self.scale_factor = 1.0
        self.translation_x = 0
        self.translation_y = 0
        self.translation_z = 0
        
        # Configurações de câmera
        self.camera_distance = 8.0
        self.camera_angle_x = 0
        self.camera_angle_y = 0
        
        # Configurações de iluminação
        self.shading_model = 'gouraud'  # flat, gouraud, phong
        self.light_pos = [3.0, 3.0, 3.0, 1.0]
        self.object_type = 'cube'  # cube, pyramid, cylinder, sphere
        self.projection_type = 'perspective'  # perspective, orthographic
        self.comparison_mode = False  # Modo de comparação lado a lado
        
        # Timer para animação
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.animate = False
        
        # Mouse interaction
        self.last_pos = None
        
    def initializeGL(self):
        """
        Inicializa o contexto OpenGL e configura o estado inicial.
        
        Configura:
        - Cor de fundo da cena
        - Teste de profundidade (Z-buffer)
        - Sistema de iluminação (luz ambiente, difusa, especular)
        - Propriedades do material (reflexão, brilho)
        - Normalização automática de vetores normais
        
        Este método é chamado automaticamente pelo Qt uma vez antes da primeira renderização.
        """
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_NORMALIZE)
        
        # Configuração da luz
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        
        # Propriedades do material
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)
        
    def resizeGL(self, w, h):
        """
        Ajusta a viewport e a projeção quando a janela é redimensionada.
        
        Args:
            w (int): Nova largura da janela em pixels
            h (int): Nova altura da janela em pixels
            
        Configura a matriz de projeção de acordo com o tipo selecionado
        (perspectiva ou ortográfica) mantendo a proporção correta (aspect ratio).
        
        Este método é chamado automaticamente pelo Qt quando a janela é redimensionada.
        """
        if h == 0:
            h = 1
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = w / h
        if self.projection_type == 'perspective':
            gluPerspective(45.0, aspect, 0.1, 100.0)
        else:
            size = 4.0
            glOrtho(-size*aspect, size*aspect, -size, size, 0.1, 100.0)
            
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        """
        Renderiza a cena 3D.
        
        Responsabilidades:
        - Limpar buffers de cor e profundidade
        - Posicionar a câmera usando coordenadas esféricas
        - Atualizar a posição da luz
        - Desenhar grade de referência e eixos (modo normal)
        - Renderizar objeto(s) com transformações aplicadas
        - Desenhar visualização da fonte de luz
        
        No modo normal: desenha um objeto com o modelo de iluminação selecionado
        No modo comparação: desenha três objetos lado a lado com diferentes modelos
        
        Este método é chamado automaticamente pelo Qt sempre que a cena precisa ser redesenhada.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Posicionar câmera
        cam_x = self.camera_distance * math.sin(math.radians(self.camera_angle_y)) * math.cos(math.radians(self.camera_angle_x))
        cam_y = self.camera_distance * math.sin(math.radians(self.camera_angle_x))
        cam_z = self.camera_distance * math.cos(math.radians(self.camera_angle_y)) * math.cos(math.radians(self.camera_angle_x))
        
        gluLookAt(cam_x, cam_y, cam_z,  # Posição da câmera
                  0, 0, 0,               # Olhando para origem
                  0, 1, 0)               # Vetor up
        
        # Atualizar posição da luz no espaço mundial
        glLightfv(GL_LIGHT0, GL_POSITION, self.light_pos)
        
        if self.comparison_mode:
            # Modo comparação: desenhar 3 objetos lado a lado
            self.draw_comparison_view()
        else:
            # Modo normal: desenhar um objeto
            # Desenhar grade de referência
            self.draw_grid()
            
            # Desenhar eixos de coordenadas
            self.draw_axes()
            
            # Aplicar transformações ao objeto
            glPushMatrix()
            glTranslatef(self.translation_x, self.translation_y, self.translation_z)
            glRotatef(self.rotation_x, 1, 0, 0)
            glRotatef(self.rotation_y, 0, 1, 0)
            glRotatef(self.rotation_z, 0, 0, 1)
            glScalef(self.scale_factor, self.scale_factor, self.scale_factor)
            
            # Configurar modelo de sombreamento
            if self.shading_model == 'flat':
                glShadeModel(GL_FLAT)
            else:
                glShadeModel(GL_SMOOTH)
                
            # Desenhar objeto
            glColor3f(0.3, 0.7, 0.9)
            self.draw_current_object()
                
            glPopMatrix()
        
        # Desenhar fonte de luz
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 0.0)
        glPushMatrix()
        glTranslatef(self.light_pos[0], self.light_pos[1], self.light_pos[2])
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.15, 10, 10)
        gluDeleteQuadric(quadric)
        glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def paintEvent(self, event):
        """
        Override do evento de pintura para adicionar elementos 2D sobre OpenGL.
        
        Args:
            event (QPaintEvent): Evento de pintura do Qt
            
        Chama o paintEvent do pai (que executa paintGL) e depois desenha
        as legendas usando QPainter quando está no modo comparação.
        """
        super().paintEvent(event)
        
        # Desenhar legendas no modo comparação após renderizar OpenGL
        if self.comparison_mode:
            self.draw_labels()
        
    def draw_grid(self):
        """
        Desenha uma grade de referência no plano XZ (chão).
        
        A grade consiste em linhas paralelas aos eixos X e Z,
        criando uma malha quadriculada de 10x10 unidades.
        Útil para ter noção de escala e posição dos objetos no espaço.
        """
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        size = 5
        for i in range(-size, size + 1):
            # Linhas paralelas ao eixo X
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
            # Linhas paralelas ao eixo Z
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
        glEnd()
        glEnable(GL_LIGHTING)
        
    def draw_axes(self):
        """
        Desenha os eixos de coordenadas 3D.
        
        Desenha três linhas coloridas representando os eixos:
        - Vermelho: Eixo X (horizontal, esquerda-direita)
        - Verde: Eixo Y (vertical, cima-baixo)
        - Azul: Eixo Z (profundidade, frente-trás)
        
        Cada eixo tem 2 unidades de comprimento a partir da origem.
        """
        glDisable(GL_LIGHTING)
        glLineWidth(3)
        glBegin(GL_LINES)
        # Eixo X (vermelho)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(2, 0, 0)
        # Eixo Y (verde)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 2, 0)
        # Eixo Z (azul)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 2)
        glEnd()
        glLineWidth(1)
        glEnable(GL_LIGHTING)
        
    def draw_cube(self):
        """
        Desenha um cubo centrado na origem com lado de 2 unidades.
        
        O cubo é definido por 8 vértices e 6 faces quadriláteras.
        Cada face tem sua normal corretamente definida para iluminação.
        Usa coordenadas de vértices hardcoded e arrays para faces e normais.
        """
        vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Traseira
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Frontal
        ]
        
        faces = [
            [0, 1, 2, 3],  # Traseira
            [4, 5, 6, 7],  # Frontal
            [0, 1, 5, 4],  # Inferior
            [2, 3, 7, 6],  # Superior
            [0, 3, 7, 4],  # Esquerda
            [1, 2, 6, 5]   # Direita
        ]
        
        normals = [
            [0, 0, -1],   # Traseira
            [0, 0, 1],    # Frontal
            [0, -1, 0],   # Inferior
            [0, 1, 0],    # Superior
            [-1, 0, 0],   # Esquerda
            [1, 0, 0]     # Direita
        ]
        
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glNormal3fv(normals[i])
            for vertex_idx in face:
                glVertex3fv(vertices[vertex_idx])
        glEnd()
        
    def draw_pyramid(self):
        """
        Desenha uma pirâmide de base quadrada.
        
        A pirâmide tem:
        - Vértice superior (apex) em y=1.5
        - Base quadrada em y=-0.5 com lado de 2 unidades
        - 4 faces triangulares laterais
        - 1 face quadrada na base
        
        As normais são calculadas dinamicamente usando produto vetorial
        para garantir iluminação correta em todas as faces.
        """
        apex = [0, 1.5, 0]
        base = [
            [-1, -0.5, 1],
            [1, -0.5, 1],
            [1, -0.5, -1],
            [-1, -0.5, -1]
        ]
        
        # Função para calcular normal
        def calc_normal(p1, p2, p3):
            v1 = [p2[i] - p1[i] for i in range(3)]
            v2 = [p3[i] - p1[i] for i in range(3)]
            normal = [
                v1[1]*v2[2] - v1[2]*v2[1],
                v1[2]*v2[0] - v1[0]*v2[2],
                v1[0]*v2[1] - v1[1]*v2[0]
            ]
            length = math.sqrt(sum(n*n for n in normal))
            return [n/length for n in normal]
        
        # Faces laterais
        glBegin(GL_TRIANGLES)
        for i in range(4):
            next_i = (i + 1) % 4
            normal = calc_normal(apex, base[i], base[next_i])
            glNormal3fv(normal)
            glVertex3fv(apex)
            glVertex3fv(base[i])
            glVertex3fv(base[next_i])
        glEnd()
        
        # Base
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        for vertex in reversed(base):
            glVertex3fv(vertex)
        glEnd()
        
    def draw_cylinder(self):
        """
        Desenha um cilindro usando primitivas GLU (OpenGL Utility Library).
        
        O cilindro consiste em:
        - Corpo cilíndrico: raio 1, altura 2, 32 subdivisões
        - Tampa inferior: disco com raio 1
        - Tampa superior: disco com raio 1
        
        Usa gluQuadric para gerar automaticamente as normais suaves (GLU_SMOOTH),
        resultando em melhor iluminação nos modelos Gouraud e Phong.
        """
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluQuadricDrawStyle(quadric, GLU_FILL)
        
        glPushMatrix()
        glTranslatef(0, -1, 0)
        
        # Corpo do cilindro
        gluCylinder(quadric, 1.0, 1.0, 2.0, 32, 32)
        
        # Tampa inferior
        glPushMatrix()
        glRotatef(180, 1, 0, 0)
        gluDisk(quadric, 0, 1.0, 32, 1)
        glPopMatrix()
        
        # Tampa superior
        glPushMatrix()
        glTranslatef(0, 0, 2.0)
        gluDisk(quadric, 0, 1.0, 32, 1)
        glPopMatrix()
        
        glPopMatrix()
        gluDeleteQuadric(quadric)
        
    def draw_sphere(self):
        """
        Desenha uma esfera usando primitivas GLU.
        
        Esfera com raio de 1.2 unidades e 32 subdivisões em latitude e longitude.
        As normais são geradas automaticamente (GLU_SMOOTH) para iluminação suave.
        """
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, 1.2, 32, 32)
        gluDeleteQuadric(quadric)
        
    def draw_current_object(self):
        """
        Desenha o objeto atualmente selecionado pelo usuário.
        
        Serve como função auxiliar que chama o método de desenho apropriado
        baseado no atributo self.object_type.
        
        Returns:
            None - desenha diretamente na cena OpenGL
        """
        if self.object_type == 'cube':
            self.draw_cube()
        elif self.object_type == 'pyramid':
            self.draw_pyramid()
        elif self.object_type == 'cylinder':
            self.draw_cylinder()
        elif self.object_type == 'sphere':
            self.draw_sphere()
    
    def draw_comparison_view(self):
        """
        Desenha três objetos lado a lado para comparar modelos de iluminação.
        
        Posiciona três instâncias do objeto atual em uma linha horizontal,
        cada uma com um modelo de iluminação diferente:
        - Esquerda: Flat Shading (vermelho)
        - Centro: Gouraud Shading (verde)
        - Direita: Phong Shading (azul)
        
        Os objetos são levemente reduzidos (80% do tamanho normal) para caber
        melhor na tela. Cores diferentes ajudam a diferenciar visualmente.
        """
        spacing = 3.5
        positions = [-spacing, 0, spacing]
        shading_models = ['flat', 'gouraud', 'phong']
        
        for i, (pos_x, shading) in enumerate(zip(positions, shading_models)):
            glPushMatrix()
            
            # Posicionar objeto
            glTranslatef(pos_x, 0, 0)
            glRotatef(self.rotation_x, 1, 0, 0)
            glRotatef(self.rotation_y, 0, 1, 0)
            glRotatef(self.rotation_z, 0, 0, 1)
            glScalef(self.scale_factor * 0.8, self.scale_factor * 0.8, self.scale_factor * 0.8)
            
            # Configurar modelo de sombreamento
            if shading == 'flat':
                glShadeModel(GL_FLAT)
            else:
                glShadeModel(GL_SMOOTH)
            
            # Desenhar objeto com cor variada para diferenciação
            colors = [(0.9, 0.3, 0.3), (0.3, 0.9, 0.3), (0.3, 0.3, 0.9)]
            glColor3f(*colors[i])
            
            self.draw_current_object()
            
            glPopMatrix()
    
    def draw_labels(self):
        """
        Desenha legendas identificando os modelos de iluminação (modo comparação).
        
        Usa QPainter para desenhar texto 2D sobre a renderização OpenGL.
        Cada legenda inclui:
        - Fundo arredondado semi-transparente
        - Texto colorido correspondente ao objeto
        - Posicionamento centralizado acima de cada objeto
        
        As cores das legendas correspondem às cores dos objetos:
        vermelho (Flat), verde (Gouraud), azul (Phong).
        """
        # Usar QPainter para desenhar texto sobre OpenGL
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Configurar fonte
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Desenhar legendas
        labels = ['FLAT SHADING', 'GOURAUD SHADING', 'PHONG SHADING']
        colors = [QColor(230, 80, 80), QColor(80, 230, 80), QColor(80, 80, 230)]
        
        for i, (label, color) in enumerate(zip(labels, colors)):
            x_pos = int((i + 0.5) * self.width() / 3)
            y_pos = 40
            
            # Desenhar fundo
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(20, 20, 30, 200))
            painter.drawRoundedRect(x_pos - 75, y_pos - 15, 150, 35, 5, 5)
            
            # Desenhar texto
            painter.setPen(color)
            painter.drawText(x_pos - 70, y_pos - 15, 140, 35, 
                           Qt.AlignmentFlag.AlignCenter, label)
        
        painter.end()
        
    def mousePressEvent(self, event):
        """
        Captura o evento de pressionar o botão do mouse.
        
        Args:
            event (QMouseEvent): Evento do mouse contendo posição e botão
            
        Armazena a posição inicial para calcular o movimento de arrasto.
        """
        self.last_pos = event.position()
        
    def mouseMoveEvent(self, event):
        """
        Controla a rotação orbital da câmera através do arrasto do mouse.
        
        Args:
            event (QMouseEvent): Evento do mouse contendo posição atual
            
        Calcula o deslocamento do mouse desde a última posição e ajusta
        os ângulos da câmera proporcionalmente:
        - Movimento horizontal: rotação em torno do eixo Y
        - Movimento vertical: rotação em torno do eixo X
        
        O ângulo vertical é limitado entre -89° e +89° para evitar gimbal lock.
        """
        if self.last_pos is not None:
            dx = event.position().x() - self.last_pos.x()
            dy = event.position().y() - self.last_pos.y()
            
            self.camera_angle_y += dx * 0.5
            self.camera_angle_x += dy * 0.5
            
            # Limitar ângulo vertical
            self.camera_angle_x = max(-89, min(89, self.camera_angle_x))
            
            self.last_pos = event.position()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """
        Finaliza o arrasto do mouse.
        
        Args:
            event (QMouseEvent): Evento de liberação do mouse
            
        Reseta a última posição para None, indicando que não há mais arrasto ativo.
        """
        self.last_pos = None
        
    def wheelEvent(self, event):
        """
        Controla o zoom através da roda do mouse.
        
        Args:
            event (QWheelEvent): Evento da roda do mouse
            
        Ajusta a distância da câmera baseado no delta da roda:
        - Rolar para cima: aproxima a câmera (zoom in)
        - Rolar para baixo: afasta a câmera (zoom out)
        
        A distância é limitada entre 2 e 20 unidades para evitar
        valores extremos que tornariam a visualização inútil.
        """
        delta = event.angleDelta().y()
        self.camera_distance -= delta * 0.01
        self.camera_distance = max(2, min(20, self.camera_distance))
        self.update()

class MainWindow(QMainWindow):
    """
    Janela principal da aplicação de visualização 3D.
    
    Gerencia a interface do usuário, incluindo:
    - Widget OpenGL para renderização 3D
    - Painel de controle com sliders e comboboxes
    - Conexões entre controles da UI e parâmetros de renderização
    - Timer para animação
    
    A janela é dividida em duas seções:
    - Área de visualização 3D (esquerda, 75% da largura)
    - Painel de controles (direita, 25% da largura)
    
    Attributes:
        gl_widget (OpenGLWidget): Widget de renderização OpenGL
        comparison_btn (QPushButton): Botão para alternar modo comparação
        object_combo (QComboBox): Seletor de tipo de objeto
        shading_combo (QComboBox): Seletor de modelo de iluminação
        projection_combo (QComboBox): Seletor de tipo de projeção
        rot_x_slider, rot_y_slider, rot_z_slider (QSlider): Controles de rotação
        scale_slider (QSlider): Controle de escala
        light_x_slider, light_y_slider, light_z_slider (QSlider): Controles de posição da luz
        animate_btn (QPushButton): Botão de animação
    """
    
    def __init__(self):
        """
        Inicializa a janela principal e configura a interface.
        
        Cria o layout principal, instancia o widget OpenGL,
        constrói o painel de controle e estabelece as dimensões da janela.
        """
        super().__init__()
        self.setWindowTitle("Trabalho 2 - Computação Gráfica 3D com Iluminação")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # OpenGL Widget
        self.gl_widget = OpenGLWidget()
        main_layout.addWidget(self.gl_widget, 3)
        
        # Painel de controle
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
    def create_control_panel(self):
        """
        Cria e configura o painel de controle lateral.
        
        Returns:
            QWidget: Painel contendo todos os controles da interface
            
        O painel inclui grupos organizados de controles:
        1. Informações e instruções de uso
        2. Seleção de objeto (cubo, pirâmide, cilindro, esfera)
        3. Modelo de iluminação (Flat, Gouraud, Phong)
        4. Botão de modo comparação
        5. Tipo de projeção (perspectiva/ortográfica)
        6. Controles de rotação (X, Y, Z) com sliders
        7. Controle de escala
        8. Controles de posição da luz (X, Y, Z)
        9. Botões de ação (animar, resetar)
        
        Cada controle é conectado ao método apropriado que atualiza
        os parâmetros do widget OpenGL.
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título
        title = QLabel("Controles 3D")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Instruções
        instructions = QLabel("🖱️ Arraste: Rotacionar câmera\n🖱️ Scroll: Zoom")
        instructions.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(instructions)
        
        # Grupo de Objeto
        object_group = QGroupBox("Objeto")
        object_layout = QVBoxLayout()
        
        self.object_combo = QComboBox()
        self.object_combo.addItems(['Cubo', 'Pirâmide', 'Cilindro', 'Esfera'])
        self.object_combo.currentTextChanged.connect(self.change_object)
        object_layout.addWidget(QLabel("Tipo:"))
        object_layout.addWidget(self.object_combo)
        
        object_group.setLayout(object_layout)
        layout.addWidget(object_group)
        
        # Grupo de Iluminação
        lighting_group = QGroupBox("Modelo de Iluminação")
        lighting_layout = QVBoxLayout()
        
        self.shading_combo = QComboBox()
        self.shading_combo.addItems(['Flat', 'Gouraud', 'Phong'])
        self.shading_combo.setCurrentIndex(1)  # Gouraud default
        self.shading_combo.currentTextChanged.connect(self.change_shading)
        lighting_layout.addWidget(QLabel("Modelo:"))
        lighting_layout.addWidget(self.shading_combo)
        
        lighting_group.setLayout(lighting_layout)
        layout.addWidget(lighting_group)
        
        # Botão de modo comparação
        comparison_btn = QPushButton("🔀 Modo Comparação")
        comparison_btn.setCheckable(True)
        comparison_btn.clicked.connect(self.toggle_comparison_mode)
        comparison_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #2a5a8a;
                color: white;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #3a7abd;
            }
            QPushButton:hover {
                background-color: #356a9a;
            }
        """)
        layout.addWidget(comparison_btn)
        self.comparison_btn = comparison_btn
        
        # Grupo de Projeção
        projection_group = QGroupBox("Projeção")
        projection_layout = QVBoxLayout()
        
        self.projection_combo = QComboBox()
        self.projection_combo.addItems(['Perspectiva', 'Ortográfica'])
        self.projection_combo.currentTextChanged.connect(self.change_projection)
        projection_layout.addWidget(QLabel("Tipo:"))
        projection_layout.addWidget(self.projection_combo)
        
        projection_group.setLayout(projection_layout)
        layout.addWidget(projection_group)
        
        # Grupo de Rotação do Objeto
        rotation_group = QGroupBox("Rotação do Objeto")
        rotation_layout = QGridLayout()
        
        self.rot_x_label = QLabel("X: 30°")
        rotation_layout.addWidget(self.rot_x_label, 0, 0)
        self.rot_x_slider = self.create_slider(0, 360, 30, self.update_rotation_x)
        rotation_layout.addWidget(self.rot_x_slider, 0, 1)
        
        self.rot_y_label = QLabel("Y: 45°")
        rotation_layout.addWidget(self.rot_y_label, 1, 0)
        self.rot_y_slider = self.create_slider(0, 360, 45, self.update_rotation_y)
        rotation_layout.addWidget(self.rot_y_slider, 1, 1)
        
        self.rot_z_label = QLabel("Z: 0°")
        rotation_layout.addWidget(self.rot_z_label, 2, 0)
        self.rot_z_slider = self.create_slider(0, 360, 0, self.update_rotation_z)
        rotation_layout.addWidget(self.rot_z_slider, 2, 1)
        
        rotation_group.setLayout(rotation_layout)
        layout.addWidget(rotation_group)
        
        # Grupo de Escala
        scale_group = QGroupBox("Escala")
        scale_layout = QVBoxLayout()
        
        self.scale_label = QLabel("Escala: 1.0x")
        scale_layout.addWidget(self.scale_label)
        self.scale_slider = self.create_slider(10, 200, 100, self.update_scale)
        scale_layout.addWidget(self.scale_slider)
        
        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)
        
        # Grupo de Posição da Luz
        light_group = QGroupBox("Posição da Luz")
        light_layout = QGridLayout()
        
        self.light_x_label = QLabel("X: 3.0")
        light_layout.addWidget(self.light_x_label, 0, 0)
        self.light_x_slider = self.create_slider(-50, 50, 30, self.update_light_x)
        light_layout.addWidget(self.light_x_slider, 0, 1)
        
        self.light_y_label = QLabel("Y: 3.0")
        light_layout.addWidget(self.light_y_label, 1, 0)
        self.light_y_slider = self.create_slider(-50, 50, 30, self.update_light_y)
        light_layout.addWidget(self.light_y_slider, 1, 1)
        
        self.light_z_label = QLabel("Z: 3.0")
        light_layout.addWidget(self.light_z_label, 2, 0)
        self.light_z_slider = self.create_slider(-50, 50, 30, self.update_light_z)
        light_layout.addWidget(self.light_z_slider, 2, 1)
        
        light_group.setLayout(light_layout)
        layout.addWidget(light_group)
        
        # Botões de ação
        btn_layout = QVBoxLayout()
        
        self.animate_btn = QPushButton("▶ Animar Rotação")
        self.animate_btn.clicked.connect(self.toggle_animation)
        btn_layout.addWidget(self.animate_btn)
        
        reset_btn = QPushButton("🔄 Resetar Vista")
        reset_btn.clicked.connect(self.reset_view)
        btn_layout.addWidget(reset_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return panel
    
    def create_slider(self, min_val, max_val, default, callback):
        """
        Cria um slider horizontal configurado.
        
        Args:
            min_val (int): Valor mínimo do slider
            max_val (int): Valor máximo do slider
            default (int): Valor inicial do slider
            callback (callable): Função a ser chamada quando o valor muda
            
        Returns:
            QSlider: Slider configurado e conectado ao callback
            
        Função auxiliar para reduzir repetição de código na criação
        de múltiplos sliders com configurações similares.
        """
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        return slider
    
    def change_object(self, text):
        """
        Altera o tipo de objeto a ser renderizado.
        
        Args:
            text (str): Nome do objeto em português ('Cubo', 'Pirâmide', 'Cilindro', 'Esfera')
            
        Converte o texto da interface para o identificador interno
        e atualiza o widget OpenGL.
        """
        obj_map = {'Cubo': 'cube', 'Pirâmide': 'pyramid', 
                   'Cilindro': 'cylinder', 'Esfera': 'sphere'}
        self.gl_widget.object_type = obj_map[text]
        self.gl_widget.update()
    
    def change_shading(self, text):
        """
        Altera o modelo de iluminação/sombreamento.
        
        Args:
            text (str): Nome do modelo ('Flat', 'Gouraud', 'Phong')
            
        Atualiza o modelo de sombreamento usado na renderização.
        Flat = sombreamento uniforme por face
        Gouraud = interpolação de cores nos vértices
        Phong = interpolação de normais (aproximado com GL_SMOOTH)
        """
        shade_map = {'Flat': 'flat', 'Gouraud': 'gouraud', 'Phong': 'phong'}
        self.gl_widget.shading_model = shade_map[text]
        self.gl_widget.update()
    
    def change_projection(self, text):
        """
        Altera o tipo de projeção da cena.
        
        Args:
            text (str): Tipo de projeção ('Perspectiva', 'Ortográfica')
            
        Perspectiva: objetos mais distantes aparecem menores (realista)
        Ortográfica: linhas paralelas permanecem paralelas (técnico)
        
        Reexecuta resizeGL para aplicar a nova matriz de projeção.
        """
        proj_map = {'Perspectiva': 'perspective', 'Ortográfica': 'orthographic'}
        self.gl_widget.projection_type = proj_map[text]
        self.gl_widget.resizeGL(self.gl_widget.width(), self.gl_widget.height())
        self.gl_widget.update()
    
    def update_rotation_x(self, value):
        """
        Atualiza a rotação do objeto no eixo X.
        
        Args:
            value (int): Ângulo de rotação em graus (0-360)
            
        Atualiza tanto o objeto OpenGL quanto o label que mostra o valor atual.
        """
        self.gl_widget.rotation_x = value
        self.rot_x_label.setText(f"X: {value}°")
        self.gl_widget.update()
    
    def update_rotation_y(self, value):
        """
        Atualiza a rotação do objeto no eixo Y.
        
        Args:
            value (int): Ângulo de rotação em graus (0-360)
        """
        self.gl_widget.rotation_y = value
        self.rot_y_label.setText(f"Y: {value}°")
        self.gl_widget.update()
    
    def update_rotation_z(self, value):
        """
        Atualiza a rotação do objeto no eixo Z.
        
        Args:
            value (int): Ângulo de rotação em graus (0-360)
        """
        self.gl_widget.rotation_z = value
        self.rot_z_label.setText(f"Z: {value}°")
        self.gl_widget.update()
    
    def update_scale(self, value):
        """
        Atualiza o fator de escala do objeto.
        
        Args:
            value (int): Valor do slider (10-200), convertido para fator (0.1-2.0)
            
        Um valor de 100 corresponde à escala normal (1.0x).
        """
        self.gl_widget.scale_factor = value / 100.0
        self.scale_label.setText(f"Escala: {value/100:.1f}x")
        self.gl_widget.update()
    
    def update_light_x(self, value):
        """
        Atualiza a posição X da fonte de luz.
        
        Args:
            value (int): Valor do slider (-50 a 50), convertido para coordenada (-5.0 a 5.0)
        """
        self.gl_widget.light_pos[0] = value / 10.0
        self.light_x_label.setText(f"X: {value/10:.1f}")
        self.gl_widget.update()
    
    def update_light_y(self, value):
        """
        Atualiza a posição Y da fonte de luz.
        
        Args:
            value (int): Valor do slider (-50 a 50), convertido para coordenada (-5.0 a 5.0)
        """
        self.gl_widget.light_pos[1] = value / 10.0
        self.light_y_label.setText(f"Y: {value/10:.1f}")
        self.gl_widget.update()
    
    def update_light_z(self, value):
        """
        Atualiza a posição Z da fonte de luz.
        
        Args:
            value (int): Valor do slider (-50 a 50), convertido para coordenada (-5.0 a 5.0)
        """
        self.gl_widget.light_pos[2] = value / 10.0
        self.light_z_label.setText(f"Z: {value/10:.1f}")
        self.gl_widget.update()
    
    def toggle_animation(self):
        """
        Alterna o estado da animação automática.
        
        Quando ativada, a animação rotaciona o objeto continuamente
        no eixo Y a ~60 FPS (16ms por frame).
        
        Estados:
        - Desligado: botão mostra "▶ Animar Rotação"
        - Ligado: botão mostra "⏸ Parar Animação"
        """
        if self.gl_widget.animate:
            self.gl_widget.animate = False
            self.gl_widget.timer.stop()
            self.animate_btn.setText("▶ Animar Rotação")
        else:
            self.gl_widget.animate = True
            self.gl_widget.timer.start(16)  # ~60 FPS
            self.animate_btn.setText("⏸ Parar Animação")
    
    def start_animation(self):
        if self.gl_widget.animate:
            self.gl_widget.rotation_y = (self.gl_widget.rotation_y + 2) % 360
            self.rot_y_slider.setValue(int(self.gl_widget.rotation_y))
    
    def reset_view(self):
        """
        Reseta todos os parâmetros de visualização para valores padrão.
        
        Restaura:
        - Rotações para valores iniciais (X=30°, Y=45°, Z=0°)
        - Escala para 1.0x
        - Distância da câmera para 8.0 unidades
        - Ângulos da câmera para 0° (vista frontal)
        - Todos os sliders para posições correspondentes
        """
        self.gl_widget.rotation_x = 30
        self.gl_widget.rotation_y = 45
        self.gl_widget.rotation_z = 0
        self.gl_widget.scale_factor = 1.0
        self.gl_widget.camera_distance = 8.0
        self.gl_widget.camera_angle_x = 0
        self.gl_widget.camera_angle_y = 0
        
        self.rot_x_slider.setValue(30)
        self.rot_y_slider.setValue(45)
        self.rot_z_slider.setValue(0)
        self.scale_slider.setValue(100)
        
        self.gl_widget.update()
    
    def toggle_comparison_mode(self, checked):
        """
        Alterna entre modo normal e modo comparação lado a lado.
        
        Args:
            checked (bool): True se o botão está pressionado (modo comparação ativo)
            
        No modo comparação:
        - Desenha 3 objetos com diferentes modelos de iluminação
        - Câmera se afasta para mostrar os 3 objetos
        - Seletor de modelo de iluminação é desabilitado
        - Botão mostra checkmark (✓)
        
        No modo normal:
        - Desenha um único objeto
        - Câmera volta à distância padrão
        - Seletor de modelo de iluminação é habilitado
        """
        self.gl_widget.comparison_mode = checked
        
        if checked:
            # Ajustar câmera para visualização melhor dos 3 objetos
            self.gl_widget.camera_distance = 12.0
            self.comparison_btn.setText("🔀 Modo Comparação ✓")
            self.shading_combo.setEnabled(False)
        else:
            # Voltar para distância normal
            self.gl_widget.camera_distance = 8.0
            self.comparison_btn.setText("🔀 Modo Comparação")
            self.shading_combo.setEnabled(True)
        
        self.gl_widget.update()

if __name__ == '__main__':
    """
    Ponto de entrada da aplicação.
    
    Cria a aplicação Qt, instancia a janela principal,
    exibe a interface e inicia o loop de eventos.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())