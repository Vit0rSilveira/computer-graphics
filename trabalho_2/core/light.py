from OpenGL.GL import *
from core.vector3d import Vector3D


class Light:
    """
    Classe que representa uma fonte de luz na cena.
    
    Attributes:
        position (Vector3D): Posição da luz no espaço 3D
        ambient (list): Cor da luz ambiente [R, G, B]
        diffuse (list): Cor da luz difusa [R, G, B]
        specular (list): Cor da luz especular [R, G, B]
    """
    
    def __init__(self, position=None):
        """
        Inicializa uma fonte de luz.
        
        Args:
            position (Vector3D, optional): Posição inicial da luz
        """
        self.position = position if position else Vector3D(3.0, 3.0, 3.0)
        self.ambient = [0.2, 0.2, 0.2]
        self.diffuse = [0.8, 0.8, 0.8]
        self.specular = [1.0, 1.0, 1.0]
    
    def apply_fixed_pipeline(self, light_id=GL_LIGHT0):
        """
        Aplica as propriedades da luz ao pipeline fixo do OpenGL.
        Usado para Flat e Gouraud shading.
        
        Args:
            light_id: Identificador da luz OpenGL (GL_LIGHT0, GL_LIGHT1, etc.)
        """
        pos = self.position.to_list() + [1.0]  # w=1 para luz posicional
        glLightfv(light_id, GL_POSITION, pos)
        glLightfv(light_id, GL_AMBIENT, self.ambient + [1.0])
        glLightfv(light_id, GL_DIFFUSE, self.diffuse + [1.0])
        glLightfv(light_id, GL_SPECULAR, self.specular + [1.0])