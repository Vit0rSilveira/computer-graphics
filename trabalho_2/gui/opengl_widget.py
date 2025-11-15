"""
Widget OpenGL para renderização 3D.
"""

import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QPainter, QFont, QColor
from PyQt6.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *

from core.scene import Scene3D
from shading.phong_shading import PhongShading


class OpenGLWidget(QOpenGLWidget):
    """
    Widget OpenGL para renderização 3D de objetos com iluminação.
    
    Esta classe gerencia toda a renderização OpenGL, incluindo:
    - Configuração da cena 3D
    - Desenho de objetos geométricos
    - Aplicação de modelos de iluminação (Flat, Gouraud, Phong com shaders)
    - Controle de câmera orbital
    - Modo de comparação entre modelos de iluminação
    
    Attributes:
        scene (Scene3D): Cena 3D principal
        rotation_x, rotation_y, rotation_z (float): Rotações do objeto em graus
        scale_factor (float): Escala do objeto (1.0 = tamanho normal)
        translation_x, translation_y, translation_z (float): Translação do objeto
        projection_type (str): Tipo de projeção ('perspective' ou 'orthographic')
        comparison_mode (bool): Se True, mostra 3 objetos com diferentes iluminações
        animate (bool): Se True, anima a rotação do objeto
        timer (QTimer): Timer para animação
        last_pos (QPoint): Última posição do mouse (para controle de câmera)
    """
    
    def __init__(self, parent=None):
        """
        Inicializa o widget OpenGL.
        
        Args:
            parent (QWidget, optional): Widget pai. Default é None.
        """
        super().__init__(parent)
        
        # Criar cena 3D
        self.scene = Scene3D()
        
        # Transformações do objeto
        self.rotation_x = 30
        self.rotation_y = 45
        self.rotation_z = 0
        self.scale_factor = 1.0
        self.translation_x = 0
        self.translation_y = 0
        self.translation_z = 0
        
        # Configurações de visualização
        self.projection_type = 'perspective'
        self.comparison_mode = False
        
        # Animação
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.animate = False
        
        # Interação com mouse
        self.last_pos = None
        
    def initializeGL(self):
        """
        Inicializa o contexto OpenGL e configura o estado inicial.
        
        Este método é chamado automaticamente pelo Qt uma vez antes da primeira renderização.
        
        Configura:
        - Cor de fundo da cena
        - Teste de profundidade (Z-buffer) para renderização correta de objetos 3D
        - Sistema de iluminação (pipeline fixo para Flat e Gouraud)
        - Propriedades do material
        - Shaders GLSL para Phong
        """
        # Cor de fundo (azul escuro)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        
        # Habilitar teste de profundidade
        glEnable(GL_DEPTH_TEST)
        
        # Configurar iluminação do pipeline fixo
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_NORMALIZE)  # Normalizar automáticamente as normais
        
        # Aplicar configurações de luz e material (pipeline fixo)
        self.scene.light.apply_fixed_pipeline()
        self.scene.material.apply_fixed_pipeline()
        
        # Compilar shaders para Phong
        self.scene.setup_shaders()
    
    def set_projection_type(self, proj_type):
        """
        Define o tipo de projeção e ajusta a câmera para melhor visualização.
        
        Args:
            proj_type (str): 'perspective' ou 'orthographic'
        """
        self.projection_type = proj_type
        
        # Ajustar distância da câmera para cada tipo de projeção
        if proj_type == 'orthographic':
            # Na ortográfica, aproximar mais para ver melhor
            if not self.comparison_mode:
                self.scene.camera.distance = 10.0
        else:
            # Na perspectiva, usar distância padrão
            if not self.comparison_mode:
                self.scene.camera.distance = 8.0
        
        # Reconfigurar matriz de projeção
        self.makeCurrent()
        self.resizeGL(self.width(), self.height())
        self.update()
        
    def resizeGL(self, w, h):
        """
        Ajusta a viewport e a projeção quando a janela é redimensionada.
        
        Este método é chamado automaticamente pelo Qt quando a janela é redimensionada.
        
        Args:
            w (int): Nova largura da janela em pixels
            h (int): Nova altura da janela em pixels
        """
        if h == 0:
            h = 1
            
        # Configurar viewport para ocupar toda a janela
        glViewport(0, 0, w, h)
        
        # Configurar matriz de projeção
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = w / h
        
        if self.projection_type == 'perspective':
            # Projeção perspectiva: objetos distantes parecem menores
            gluPerspective(45.0,      # Campo de visão vertical (FOV)
                          aspect,     # Aspect ratio (largura/altura)
                          0.1,        # Near clipping plane
                          100.0)      # Far clipping plane
        else:
            # Projeção ortográfica: linhas paralelas permanecem paralelas
            size = 4.0
            glOrtho(-size*aspect, size*aspect,  # Left, right
                    -size, size,                 # Bottom, top
                    0.1, 100.0)                  # Near, far
            
        # Voltar para matriz modelview
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        """
        Renderiza a cena 3D.
        """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Aplicar transformação da câmera
        self.scene.camera.apply()
        
        # Atualizar posição da luz (pipeline fixo)
        self.scene.light.apply_fixed_pipeline()
        
        # IMPORTANTE: Habilitar iluminação para pipeline fixo
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Renderizar baseado no modo
        if self.comparison_mode:
            self.draw_comparison_view()
        else:
            self.draw_normal_view()
        
        # Desenhar visualização da fonte de luz
        self.draw_light_source()
        
        # SEMPRE garantir que shaders estão desativados no final
        glUseProgram(0)
    
    def draw_normal_view(self):
        """
        Desenha a visualização normal com um único objeto.
        """
        self.draw_grid()
        self.draw_axes()
        
        glPushMatrix()
        
        # Aplicar transformações geométricas
        glTranslatef(self.translation_x, self.translation_y, self.translation_z)
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)
        glScalef(self.scale_factor, self.scale_factor, self.scale_factor)
        
        # DEFINIR COR ANTES DE APLICAR O SHADER
        glColor3f(0.3, 0.7, 0.9)
        
        # Obter modelo de iluminação
        shading = self.scene.get_shading()
        
        # Se for Phong, configurar uniforms ANTES de aplicar
        if isinstance(shading, PhongShading) and shading.shader_program:
            shading.apply()
            self._setup_phong_uniforms(shading)
        else:
            # Para Flat e Gouraud, apenas aplicar
            shading.apply()
        
        # Desenhar objeto
        self.scene.get_object().draw()
        
        # SEMPRE desativar shader após desenhar
        glUseProgram(0)
        
        glPopMatrix()
    
    def draw_comparison_view(self):
        """
        Desenha três objetos lado a lado para comparar modelos de iluminação.
        """
        # Desenhar grade e eixos
        self.draw_grid()
        self.draw_axes()
        
        spacing = 3.5
        positions = [-spacing, 0, spacing]
        shading_keys = ['flat', 'gouraud', 'phong']
        colors = [(0.9, 0.3, 0.3), (0.3, 0.9, 0.3), (0.3, 0.3, 0.9)]
        
        for i, (pos_x, shading_key, color) in enumerate(zip(positions, shading_keys, colors)):
            glPushMatrix()
            
            # Posicionar objeto
            glTranslatef(pos_x, 0, 0)
            glRotatef(self.rotation_x, 1, 0, 0)
            glRotatef(self.rotation_y, 0, 1, 0)
            glRotatef(self.rotation_z, 0, 0, 1)
            glScalef(self.scale_factor * 0.8, self.scale_factor * 0.8, self.scale_factor * 0.8)
            
            # DEFINIR COR ANTES DE APLICAR O SHADER
            glColor3f(*color)
            
            # Obter modelo de iluminação
            shading = self.scene.get_shading(shading_key)
            
            # Se for Phong, configurar uniforms ANTES de aplicar
            if isinstance(shading, PhongShading) and shading.shader_program:
                shading.apply()
                self._setup_phong_uniforms(shading)
            else:
                # Para Flat e Gouraud, apenas aplicar
                shading.apply()
            
            # Desenhar objeto
            self.scene.get_object().draw()
            
            # SEMPRE desativar shader após cada objeto
            glUseProgram(0)
            
            glPopMatrix()
    
    def _setup_phong_uniforms(self, phong_shading):
        """
        Configura as variáveis uniform para os shaders do Phong.
        
        Extrai as matrizes do OpenGL e passa para o shader junto com
        as propriedades de luz, material e posição da câmera.
        
        Args:
            phong_shading (PhongShading): Instância do modelo Phong
        """
        # Obter matrizes do OpenGL
        model_matrix = np.array(glGetFloatv(GL_MODELVIEW_MATRIX), dtype=np.float32)
        view_matrix = np.identity(4, dtype=np.float32)  # Já aplicada em modelview
        proj_matrix = np.array(glGetFloatv(GL_PROJECTION_MATRIX), dtype=np.float32)
        
        # Posição da câmera no espaço mundo
        camera_pos = self.scene.camera.get_position()
        
        # Configurar todos os uniforms do shader
        phong_shading.set_uniforms(
            self.scene.light,
            self.scene.material,
            camera_pos,
            model_matrix,
            view_matrix,
            proj_matrix
        )
    
    def draw_light_source(self):
        """
        Desenha uma esfera amarela representando a posição da fonte de luz.
        
        Desabilita iluminação temporariamente para que a esfera apareça
        sempre brilhante, independente da posição da luz.
        """
        glDisable(GL_LIGHTING)
        glUseProgram(0)  # Garantir que não está usando shaders
        glColor3f(1.0, 1.0, 0.0)  # Amarelo
        
        glPushMatrix()
        pos = self.scene.light.position
        glTranslatef(pos.x, pos.y, pos.z)
        
        # Desenhar esfera pequena
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.15, 10, 10)
        gluDeleteQuadric(quadric)
        
        glPopMatrix()
        glEnable(GL_LIGHTING)
    
    def draw_grid(self):
        """
        Desenha uma grade de referência no plano XZ (chão).
        
        A grade consiste em linhas paralelas aos eixos X e Z,
        criando uma malha quadriculada de 10x10 unidades.
        """
        glDisable(GL_LIGHTING)
        glUseProgram(0)
        glColor3f(0.3, 0.3, 0.3)  # Cinza escuro
        
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
        Desenha os eixos de coordenadas 3D coloridos.
        
        - Vermelho: Eixo X (horizontal, esquerda-direita)
        - Verde: Eixo Y (vertical, cima-baixo)
        - Azul: Eixo Z (profundidade, frente-trás)
        """
        glDisable(GL_LIGHTING)
        glUseProgram(0)
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
    
    def paintEvent(self, event):
        """
        Override do evento de pintura para adicionar elementos 2D sobre OpenGL.
        
        Args:
            event (QPaintEvent): Evento de pintura do Qt
            
        Chama o paintEvent do pai (que executa paintGL) e depois desenha
        as legendas usando QPainter quando está no modo comparação.
        """
        super().paintEvent(event)
        
        # Desenhar legendas no modo comparação
        if self.comparison_mode:
            self.draw_labels()
    
    def draw_labels(self):
        """
        Desenha legendas identificando os modelos de iluminação (modo comparação).
        
        Usa QPainter para desenhar texto 2D sobre a renderização OpenGL.
        Cada legenda inclui:
        - Fundo arredondado semi-transparente
        - Texto colorido correspondente ao objeto
        - Posicionamento centralizado acima de cada objeto
        """
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
    
    # ========================================================================
    # EVENTOS DE MOUSE PARA CONTROLE DE CÂMERA
    # ========================================================================
    
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
        """
        if self.last_pos is not None:
            dx = event.position().x() - self.last_pos.x()
            dy = event.position().y() - self.last_pos.y()
            
            self.scene.camera.rotate(dx, dy)
            
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
        """
        delta = event.angleDelta().y()
        self.scene.camera.zoom(delta)
        self.update()