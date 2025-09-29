from __future__ import annotations

from typing import List, Tuple, Optional

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import (
    QWidget, QMessageBox
)

from PyQt6.QtGui import QColor

from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from Edge import Edge

# PyOpenGL
from OpenGL.GL import (
    glClearColor, glClear, GL_COLOR_BUFFER_BIT,
    glMatrixMode, GL_PROJECTION, GL_MODELVIEW, glLoadIdentity,
    glOrtho, glBegin, glEnd, glVertex2f, GL_LINES, GL_LINE_LOOP,
    glLineWidth, glColor4f, glEnable, GL_BLEND, glBlendFunc,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_POINT_SMOOTH,
    GL_LINE_SMOOTH, glPointSize
)



class GLCanvas(QOpenGLWidget):

    """ 
    Widget OpenGL responsável por desenhar o polígono e realizar o preenchimento por meio do algoritmo ET/AET. 
    
    Atributos: 
    
    points (List[QPointF]): lista de pontos (vértices) do polígono. 
    
    closed (bool): indica se o polígono foi fechado. 
    
    fill_color (QColor): cor usada para preencher. 
    
    stroke_color (QColor): cor do contorno do polígono. 
    
    stroke_width (int): espessura da linha de contorno. 
    
    filled_spans (List[Tuple[int,float,float]]): spans calculados para preenchimento (cada tupla é (y, x_esquerda, x_direita)). 
    
    hover_pos (Optional[QPointF]): posição do mouse para visualização. 
    
    bg_color (QColor): cor de fundo da tela. 
    
    show_vertices (bool): exibe ou não os marcadores dos vértices. 
    
    snap_preview (bool): ativa visualização de aresta até o cursor. 
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.points: List[QPointF] = []  # current polygon points
        self.closed: bool = False
        self.fill_color: QColor = QColor(0, 128, 255, 180)
        self.stroke_color: QColor = QColor(30, 30, 30)
        self.stroke_width: int = 2
        self.filled_spans: List[Tuple[int, float, float]] = []  # (y, x_left, x_right)
        self.hover_pos: Optional[QPointF] = None
        self.bg_color = QColor(245, 246, 248)
        self.show_vertices: bool = True
        self.snap_preview: bool = True

    # ---------- OpenGL lifecycle ----------
    def initializeGL(self):
        """ 
        Configurações iniciais do OpenGL, como cor de fundo, blending 
        para transparência e suavização de pontos e linhas. 
        """

        glClearColor(self.bg_color.redF(), self.bg_color.greenF(), self.bg_color.blueF(), 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)

    def resizeGL(self, w: int, h: int):
        """ 
        Ajusta a projeção ortográfica do OpenGL quando a janela é redimensionada. 
        Define origem no canto superior esquerdo. 
        """

        # 2D orthographic projection: origin top-left
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """ 
        Responsável por desenhar na tela: 
            • preenchimento do polígono (se calculado); 
            • contorno do polígono (fechado ou em construção); 
            • vértices como cruzes; 
            • linha de pré-visualização até o cursor do mouse. 
        """

        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()

        # Draw filled spans (if available)
        if self.filled_spans:
            r, g, b, a = self.fill_color.redF(), self.fill_color.greenF(), self.fill_color.blueF(), self.fill_color.alphaF()
            glColor4f(r, g, b, a)
            glLineWidth(1)
            glBegin(GL_LINES)
            for y, x1, x2 in self.filled_spans:
                glVertex2f(x1, float(y) + 0.5)
                glVertex2f(x2, float(y) + 0.5)
            glEnd()

        # Draw polygon outline
        if len(self.points) >= 2:
            glColor4f(self.stroke_color.redF(), self.stroke_color.greenF(), self.stroke_color.blueF(), 1.0)
            glLineWidth(float(self.stroke_width))
            glBegin(GL_LINE_LOOP if self.closed else GL_LINES)
            if self.closed:
                for p in self.points:
                    glVertex2f(p.x(), p.y())
            else:
                # draw path as segments in input order
                for i in range(len(self.points) - 1):
                    p1, p2 = self.points[i], self.points[i + 1]
                    glVertex2f(p1.x(), p1.y())
                    glVertex2f(p2.x(), p2.y())
            glEnd()

        # Draw vertices and hover preview
        if self.show_vertices and self.points:
            glPointSize(6)
            glColor4f(0.1, 0.1, 0.1, 1.0)
            glBegin(GL_LINES)  # we will draw little crosses using lines for each vertex
            s = 4
            for p in self.points:
                x, y = p.x(), p.y()
                glVertex2f(x - s, y)
                glVertex2f(x + s, y)
                glVertex2f(x, y - s)
                glVertex2f(x, y + s)
            glEnd()

        if self.hover_pos and (not self.closed) and self.points:
            # Preview segment from last point to cursor
            glColor4f(0.15, 0.15, 0.15, 0.35)
            glLineWidth(1.0)
            glBegin(GL_LINES)
            last = self.points[-1]
            glVertex2f(last.x(), last.y())
            glVertex2f(self.hover_pos.x(), self.hover_pos.y())
            glEnd()

    # ---------- Interaction ----------
    def mousePressEvent(self, event):
        """ 
        Gerencia cliques do mouse: 
            • Botão esquerdo adiciona novo vértice ao polígono. 
            • Botão direito alterna exibição dos vértices. 
        """

        if event.button() == Qt.MouseButton.LeftButton and not self.closed:
            self.points.append(QPointF(event.position().x(), event.position().y()))
            self.filled_spans.clear()
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            # right-click toggles vertex display for clarity
            self.show_vertices = not self.show_vertices
            self.update()

    def mouseMoveEvent(self, event):
        """ 
        Atualiza a posição atual do cursor (hover_pos) e solicita redesenho. 
        """

        self.hover_pos = QPointF(event.position().x(), event.position().y())
        self.update()

    # ---------- Public operations ----------
    def set_stroke_width(self, w: int):
        """ 
        Ajusta a espessura do traço do polígono. 
        """

        self.stroke_width = max(1, int(w))
        self.update()

    def set_fill_color(self, c: QColor):
        """ 
        Define a cor de preenchimento do polígono. 
        """

        self.fill_color = c
        self.update()

    def clear(self):
        """ 
        Limpa todos os pontos e reseta o canvas. 
        """

        self.points.clear()
        self.closed = False
        self.filled_spans.clear()
        self.update()

    def close_polygon(self):
        """ 
        Fecha o polígono caso tenha pelo menos 3 vértices. Caso contrário, exibe mensagem de aviso. 
        """

        if len(self.points) >= 3:
            self.closed = True
            self.filled_spans.clear()
            self.update()
        else:
            QMessageBox.information(self, "Info", "Adicione pelo menos 3 pontos antes de fechar o polígono.")

    def fill(self):
        """ 
        Executa o algoritmo de preenchimento ET/AET no polígono fechado e armazena os spans resultantes para desenho. 
        """

        if not self.closed:
            QMessageBox.information(self, "Info", "Feche o polígono antes de preencher.")
            return
        spans = self.compute_scanline_spans([(p.x(), p.y()) for p in self.points], int(self.height()))
        self.filled_spans = spans
        self.update()

    # ---------- ET / AET implementation ----------
    @staticmethod
    def build_edge_table(vertices: List[Tuple[float, float]], height: int) -> List[List[Edge]]:
        """ 
        Constrói a Tabela de Arestas (ET). 
        Cada linha Y da tela possui uma lista de arestas que começam nela. 
        
        Args: 
        
        vertices: lista de vértices (x, y) do polígono. 
        
        height: altura da tela. 
        
        Returns: ET (lista de listas de Edge). 
        """

        n = len(vertices)
        ET: List[List[Edge]] = [[] for _ in range(height + 1)]

        # iterate over edges (v_i, v_{i+1})
        for i in range(n):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % n]

            # Ignore horizontal edges
            if int(round(y1)) == int(round(y2)):
                continue

            if y1 < y2:
                ymin, ymax = y1, y2
                x_at_ymin = x1
                dy = y2 - y1
                dx = x2 - x1
            else:
                ymin, ymax = y2, y1
                x_at_ymin = x2
                dy = y1 - y2
                dx = x1 - x2

            inv_slope = dx / dy  # 1/m

            # Ceiling of ymin as first scanline
            y_start = int(max(0, int(round(min(ymin, height)))))
            y_end = int(min(height, int(round(max(0, ymax) - 1))))  # ymax is exclusive

            # Compute x at the first scanline (y = y_start)
            # Adjust x to the precise intersection with the first integer scanline
            if dy != 0:
                # Move from ymin to y_start
                y_offset = (y_start + 0.0) - ymin
                x_int = x_at_ymin + inv_slope * y_offset
            else:
                x_int = x_at_ymin

            if 0 <= y_start <= height and y_start <= y_end:
                ET[y_start].append(Edge(ymax=y_end, x=x_int, inv_slope=inv_slope))

        return ET

    @staticmethod
    def compute_scanline_spans(vertices: List[Tuple[float, float]], height: int) -> List[Tuple[int, float, float]]:
        """ 
        Calcula os spans horizontais para preenchimento do polígono usando ET (Edge Table) e AET (Active Edge Table). 
        
        Args: 
        
        vertices: lista de vértices (x, y) do polígono. 
        
        height: altura da tela. 
        
        Returns: Lista de tuplas (y, x_esquerda, x_direita). 
        """

        ET = GLCanvas.build_edge_table(vertices, height)
        AET: List[Edge] = []
        spans: List[Tuple[int, float, float]] = []

        for y in range(0, height + 1):
            # Add edges starting at this scanline
            for e in ET[y]:
                AET.append(e)
            # Remove edges for which y > ymax
            AET = [e for e in AET if y <= e.ymax]

            # Sort AET by current x, then by inv_slope
            AET.sort(key=lambda e: (e.x, e.inv_slope))

            # Pair up intersections to generate spans
            it = iter(AET)
            pairs = []
            try:
                while True:
                    e1 = next(it)
                    e2 = next(it)
                    x_left = e1.x
                    x_right = e2.x
                    if x_left > x_right:
                        x_left, x_right = x_right, x_left
                    pairs.append((x_left, x_right))
            except StopIteration:
                pass

            for x_left, x_right in pairs:
                if x_right - x_left > 1e-6:
                    spans.append((y, x_left, x_right))

            # Increment x for each active edge
            for e in AET:
                e.x += e.inv_slope

        return spans

    # ---------- Example polygons ----------
    def load_example(self, name: str):
        """ 
        Carrega polígonos de exemplo predefinidos (convexo, côncavo, etc.) 
        já fechados e prontos para preenchimento. 
        """
        
        w, h = self.width(), self.height()
        examples = {
            "Convex pentagon": [
                QPointF(0.25 * w, 0.2 * h), QPointF(0.75 * w, 0.25 * h),
                QPointF(0.8 * w, 0.65 * h), QPointF(0.5 * w, 0.85 * h),
                QPointF(0.2 * w, 0.6 * h)
            ],
            "Concave arrow": [
                QPointF(0.2 * w, 0.2 * h), QPointF(0.7 * w, 0.2 * h),
                QPointF(0.7 * w, 0.05 * h), QPointF(0.95 * w, 0.35 * h),
                QPointF(0.7 * w, 0.65 * h), QPointF(0.7 * w, 0.5 * h),
                QPointF(0.2 * w, 0.5 * h)
            ],
        }
        if name in examples:
            self.points = examples[name]
            self.closed = True
            self.filled_spans.clear()
            self.update()
