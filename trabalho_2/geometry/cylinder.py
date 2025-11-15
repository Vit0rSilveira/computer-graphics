"""
Implementação de um cilindro 3D.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from geometry.geometry3d import Geometry3D


class Cylinder(Geometry3D):
    """
    Implementação de um cilindro 3D usando GLU.
    
    Cilindro com raio 1 e altura 2, incluindo tampas superior e inferior.
    Usa quadrics do GLU para gerar geometria suave.
    """
    
    def __init__(self):
        """Inicializa o cilindro."""
        super().__init__("Cylinder")
    
    def draw(self, use_shaders=False):
        """
        Renderiza o cilindro usando GLU quadrics.
        
        Args:
            use_shaders (bool): Não usado para GLU quadrics
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