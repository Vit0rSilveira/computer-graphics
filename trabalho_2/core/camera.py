import math
from OpenGL.GLU import *
from core.vector3d import Vector3D


class Camera:
    """
    Classe que gerencia a câmera orbital 3D.
    
    Implementa uma câmera que orbita ao redor da origem usando
    coordenadas esféricas (distância, ângulo horizontal, ângulo vertical).
    
    Attributes:
        distance (float): Distância da câmera até a origem
        angle_x (float): Ângulo vertical em graus (-89 a 89)
        angle_y (float): Ângulo horizontal em graus (0 a 360)
    """
    
    def __init__(self, distance=8.0):
        """
        Inicializa a câmera.
        
        Args:
            distance (float): Distância inicial da câmera
        """
        self.distance = distance
        self.angle_x = 0  # Vertical
        self.angle_y = 0  # Horizontal
    
    def get_position(self):
        """
        Calcula a posição atual da câmera em coordenadas cartesianas.
        
        Returns:
            Vector3D: Posição da câmera
        """
        rad_x = math.radians(self.angle_x)
        rad_y = math.radians(self.angle_y)
        
        x = self.distance * math.sin(rad_y) * math.cos(rad_x)
        y = self.distance * math.sin(rad_x)
        z = self.distance * math.cos(rad_y) * math.cos(rad_x)
        
        return Vector3D(x, y, z)
    
    def apply(self):
        """
        Aplica a transformação da câmera usando gluLookAt.
        
        Converte coordenadas esféricas em cartesianas para posicionar
        a câmera e configura a matriz de visualização do OpenGL.
        """
        pos = self.get_position()
        gluLookAt(pos.x, pos.y, pos.z,  # Posição da câmera
                  0, 0, 0,               # Olhando para origem
                  0, 1, 0)               # Vetor up
    
    def rotate(self, delta_x, delta_y):
        """
        Rotaciona a câmera baseado no movimento do mouse.
        
        Args:
            delta_x (float): Movimento horizontal do mouse
            delta_y (float): Movimento vertical do mouse
        """
        self.angle_y += delta_x * 0.5
        self.angle_x += delta_y * 0.5
        
        # Limitar ângulo vertical para evitar gimbal lock
        self.angle_x = max(-89, min(89, self.angle_x))
    
    def zoom(self, delta):
        """
        Ajusta a distância da câmera (zoom).
        
        Args:
            delta (float): Valor de ajuste da distância
        """
        self.distance -= delta * 0.01
        self.distance = max(2, min(20, self.distance))