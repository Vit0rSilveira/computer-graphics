"""
Classe Material para propriedades de materiais.
"""

from OpenGL.GL import *


class Material:
    """
    Classe que representa as propriedades de material de um objeto.
    
    Attributes:
        ambient (list): Reflexão ambiente [R, G, B]
        diffuse (list): Reflexão difusa [R, G, B]
        specular (list): Reflexão especular [R, G, B]
        shininess (float): Expoente de brilho especular (0-128)
    """
    
    def __init__(self):
        """Inicializa um material com propriedades padrão."""
        self.ambient = [0.2, 0.2, 0.2]
        self.diffuse = [0.8, 0.8, 0.8]
        self.specular = [1.0, 1.0, 1.0]
        self.shininess = 50.0
    
    def apply_fixed_pipeline(self):
        """
        Aplica as propriedades do material ao pipeline fixo do OpenGL.
        Usado para Flat e Gouraud shading.
        """
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient + [1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.diffuse + [1.0])
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular + [1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)