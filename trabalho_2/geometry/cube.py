"""
Implementação de um cubo 3D.
"""

from OpenGL.GL import *
from geometry.geometry3d import Geometry3D


class Cube(Geometry3D):
    """
    Implementação de um cubo 3D.
    
    Cubo centrado na origem com lado de 2 unidades,
    definido por 8 vértices e 6 faces quadriláteras.
    """
    
    def __init__(self):
        """Inicializa o cubo."""
        super().__init__("Cube")
        self._setup_geometry()
    
    def _setup_geometry(self):
        """Define os vértices, faces e normais do cubo."""
        self.vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # Traseira
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # Frontal
        ]
        
        self.faces = [
            [0, 1, 2, 3],  # Traseira
            [4, 5, 6, 7],  # Frontal
            [0, 1, 5, 4],  # Inferior
            [2, 3, 7, 6],  # Superior
            [0, 3, 7, 4],  # Esquerda
            [1, 2, 6, 5]   # Direita
        ]
        
        self.normals = [
            [0, 0, -1],   # Traseira
            [0, 0, 1],    # Frontal
            [0, -1, 0],   # Inferior
            [0, 1, 0],    # Superior
            [-1, 0, 0],   # Esquerda
            [1, 0, 0]     # Direita
        ]
    
    def draw(self, use_shaders=False):
        """
        Renderiza o cubo usando OpenGL.
        
        Args:
            use_shaders (bool): Não usado para geometria simples
        """
        glBegin(GL_QUADS)
        for i, face in enumerate(self.faces):
            glNormal3fv(self.normals[i])
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()