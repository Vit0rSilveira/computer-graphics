"""
Classe Scene3D para gerenciar a cena 3D completa.
"""

from core.camera import Camera
from core.light import Light
from core.material import Material
from geometry.cube import Cube
from geometry.pyramid import Pyramid
from geometry.cylinder import Cylinder
from geometry.sphere import Sphere
from shading.flat_shading import FlatShading
from shading.gouraud_shading import GouraudShading
from shading.phong_shading import PhongShading


class Scene3D:
    """
    Classe que gerencia a cena 3D completa.
    
    Responsável por coordenar todos os elementos da cena:
    objetos, luz, câmera, e renderização.
    
    Attributes:
        camera (Camera): Câmera da cena
        light (Light): Fonte de luz
        material (Material): Material dos objetos
        objects (dict): Dicionário de objetos 3D disponíveis
        shading_models (dict): Dicionário de modelos de iluminação
        current_object (str): Chave do objeto atual
        current_shading (str): Chave do modelo de iluminação atual
    """
    
    def __init__(self):
        """Inicializa a cena 3D."""
        self.camera = Camera()
        self.light = Light()
        self.material = Material()
        
        # Criar objetos disponíveis
        self.objects = {
            'cube': Cube(),
            'pyramid': Pyramid(),
            'cylinder': Cylinder(),
            'sphere': Sphere()
        }
        
        # Criar modelos de iluminação
        self.shading_models = {
            'flat': FlatShading(),
            'gouraud': GouraudShading(),
            'phong': PhongShading()
        }
        
        self.current_object = 'cube'
        self.current_shading = 'gouraud'
    
    def setup_shaders(self):
        """Inicializa os shaders (especialmente Phong)."""
        self.shading_models['phong'].setup()
    
    def get_object(self, key=None):
        """
        Retorna o objeto geométrico.
        
        Args:
            key (str, optional): Chave do objeto. Se None, usa current_object
            
        Returns:
            Geometry3D: Objeto geométrico
        """
        if key is None:
            key = self.current_object
        return self.objects.get(key)
    
    def get_shading(self, key=None):
        """
        Retorna o modelo de iluminação.
        
        Args:
            key (str, optional): Chave do modelo. Se None, usa current_shading
            
        Returns:
            ShadingModel: Modelo de iluminação
        """
        if key is None:
            key = self.current_shading
        return self.shading_models.get(key)