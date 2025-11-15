"""
Implementação de uma pirâmide 3D.
"""

from OpenGL.GL import *
from geometry.geometry3d import Geometry3D
from core.vector3d import Vector3D


class Pyramid(Geometry3D):
    """
    Implementação de uma pirâmide 3D de base quadrada.
    
    Pirâmide com vértice superior e base quadrada,
    composta por 4 faces triangulares e 1 base quadrada.
    """
    
    def __init__(self):
        """Inicializa a pirâmide."""
        super().__init__("Pyramid")
        self._setup_geometry()
    
    def _setup_geometry(self):
        """Define os vértices e faces da pirâmide."""
        self.apex = [0, 1.5, 0]
        self.base = [
            [-1, -0.5, 1],
            [1, -0.5, 1],
            [1, -0.5, -1],
            [-1, -0.5, -1]
        ]
    
    def _calculate_normal(self, p1, p2, p3):
        """
        Calcula a normal de um triângulo usando produto vetorial.
        
        Args:
            p1, p2, p3 (list): Vértices do triângulo
            
        Returns:
            list: Vetor normal normalizado
        """
        v1 = Vector3D(p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2])
        v2 = Vector3D(p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2])
        normal = v1.cross(v2).normalize()
        return normal.to_list()
    
    def draw(self, use_shaders=False):
        """
        Renderiza a pirâmide usando OpenGL.
        
        Args:
            use_shaders (bool): Não usado para geometria simples
        """
        # Faces laterais triangulares
        glBegin(GL_TRIANGLES)
        for i in range(4):
            next_i = (i + 1) % 4
            normal = self._calculate_normal(self.apex, self.base[i], self.base[next_i])
            glNormal3fv(normal)
            glVertex3fv(self.apex)
            glVertex3fv(self.base[i])
            glVertex3fv(self.base[next_i])
        glEnd()
        
        # Base quadrada
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        for vertex in reversed(self.base):
            glVertex3fv(vertex)
        glEnd()