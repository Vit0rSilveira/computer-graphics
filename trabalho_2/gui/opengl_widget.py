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

        # Passo de translação (unidades por pressão de tecla)
        self.translation_step = 0.2

        # Permitir que o widget receba eventos de teclado (setas, etc.)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Configurações de visualização
        self.projection_type = 'perspective'
        
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
            self.scene.camera.distance = 10.0
        else:
            # Na perspectiva, usar distância padrão
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
    

    def _build_model_matrix(self, extra_translation=(0.0, 0.0, 0.0), extra_scale=1.0):
        """
        Constrói a matriz modelo (apenas transformações do objeto),
        na mesma ordem dos glTranslatef/glRotatef/glScalef usados no desenho.
        """
        tx = self.translation_x + extra_translation[0]
        ty = self.translation_y + extra_translation[1]
        tz = self.translation_z + extra_translation[2]
        s = self.scale_factor * extra_scale

        rx = np.radians(self.rotation_x)
        ry = np.radians(self.rotation_y)
        rz = np.radians(self.rotation_z)

        # Translação
        T = np.array([
            [1.0, 0.0, 0.0, tx],
            [0.0, 1.0, 0.0, ty],
            [0.0, 0.0, 1.0, tz],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=np.float32)

        # Rotações (X depois Y depois Z — mesma ordem do código OpenGL)
        cx, sx = np.cos(rx), np.sin(rx)
        cy, sy = np.cos(ry), np.sin(ry)
        cz, sz = np.cos(rz), np.sin(rz)

        Rx = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, cx, -sx, 0.0],
            [0.0, sx,  cx, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=np.float32)

        Ry = np.array([
            [ cy, 0.0, sy, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-sy, 0.0, cy, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=np.float32)

        Rz = np.array([
            [cz, -sz, 0.0, 0.0],
            [sz,  cz, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=np.float32)

        # Escala uniforme
        S = np.array([
            [s,   0.0, 0.0, 0.0],
            [0.0, s,   0.0, 0.0],
            [0.0, 0.0, s,   0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=np.float32)

        # Mesma composição que no OpenGL (T * Rx * Ry * Rz * S)
        return T @ Rx @ Ry @ Rz @ S

    def _build_view_matrix(self):
        """
        Constrói a matriz de visualização (view) equivalente ao gluLookAt da câmera orbital.
        """
        cam_pos = self.scene.camera.get_position()
        eye = np.array([cam_pos.x, cam_pos.y, cam_pos.z], dtype=np.float32)
        center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

        f = center - eye
        f = f / np.linalg.norm(f)
        u = up / np.linalg.norm(up)
        s = np.cross(f, u)
        s = s / np.linalg.norm(s)
        u = np.cross(s, f)

        view = np.identity(4, dtype=np.float32)
        view[0, 0:3] = s
        view[1, 0:3] = u
        view[2, 0:3] = -f
        view[0, 3] = -np.dot(s, eye)
        view[1, 3] = -np.dot(u, eye)
        view[2, 3] =  np.dot(f, eye)
        return view

    
    def _setup_phong_uniforms(self, phong_shading,
                              extra_translation=(0.0, 0.0, 0.0),
                              extra_scale=1.0):
        """
        Configura as variáveis uniform para os shaders do Phong.
        
        Extrai as matrizes do OpenGL e passa para o shader junto com
        as propriedades de luz, material e posição da câmera.
        
        Args:
            phong_shading (PhongShading): Instância do modelo Phong
        """
        # Matriz modelo: transformações do objeto no mundo
        model_matrix = self._build_model_matrix(extra_translation, extra_scale)

        # Matriz de visualização da câmera
        view_matrix = self._build_view_matrix()

        # Matriz de projeção atual
        proj_matrix = np.array(glGetFloatv(GL_PROJECTION_MATRIX), dtype=np.float32)

        # Posição da câmera em mundo
        camera_pos = self.scene.camera.get_position()

        # Configura todos os uniforms no shader
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
        as legendas usando QPainter quando está no .
        """
        super().paintEvent(event)




    # EVENTOS DE TECLADO (TRANSLACAO DO OBJETO)
    def keyPressEvent(self, event):
        """
        Traduz o objeto 3D usando teclado.

        ← e → movem no eixo X;
        ↑ e ↓ movem no eixo Y;
        W e S movem no eixo Z.
        """
        key = event.key()
        moved = False

        if key == Qt.Key.Key_Left:
            self.translation_x -= self.translation_step
            moved = True
        elif key == Qt.Key.Key_Right:
            self.translation_x += self.translation_step
            moved = True
        elif key == Qt.Key.Key_Up:
            self.translation_y += self.translation_step
            moved = True
        elif key == Qt.Key.Key_Down:
            self.translation_y -= self.translation_step
            moved = True
        elif key == Qt.Key.Key_W:
            # Aproxima o objeto da câmera (Z+)
            self.translation_z += self.translation_step
            moved = True
        elif key == Qt.Key.Key_S:
            # Afasta o objeto da câmera (Z-)
            self.translation_z -= self.translation_step
            moved = True

        if moved:
            self.update()
        else:
            super().keyPressEvent(event)



    
    # EVENTOS DE MOUSE PARA CONTROLE DE CÂMERA
    
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

    def reset_opengl_state(self):
        """
        Reseta o estado do OpenGL para padrões seguros.
        
        Útil ao alternar entre modos de renderização.
        """
        self.makeCurrent()
        
        # Desativar todos os shaders
        glUseProgram(0)
        
        # Restaurar shading model padrão
        glShadeModel(GL_SMOOTH)
        
        # Garantir que iluminação está habilitada
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        
        # Reconfigurar luz e material
        self.scene.light.apply_fixed_pipeline()
        self.scene.material.apply_fixed_pipeline()
        
        # Forçar atualização
        self.update()