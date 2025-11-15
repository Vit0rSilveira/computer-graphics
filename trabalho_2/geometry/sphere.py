"""
Implementação de uma esfera 3D.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from geometry.geometry3d import Geometry3D


class Sphere(Geometry3D):
    """
    Implementação de uma esfera 3D usando GLU.
    
    Esfera com raio 1.2 e subdivisões suaves.
    Usa quadrics do GLU para gerar geometria suave.
    """
    
    def __init__(self):
        """Inicializa a esfera."""
        super().__init__("Sphere")
    
    def draw(self, use_shaders=False):
        """
        Renderiza a esfera usando GLU quadrics.
        
        Args:
            use_shaders (bool): Não usado para GLU quadrics
        """
        quadric = gluNewQuadric()
        gluQuadricNormals(quadric, GLU_SMOOTH)
        gluSphere(quadric, 1.2, 32, 32)
        gluDeleteQuadric(quadric)