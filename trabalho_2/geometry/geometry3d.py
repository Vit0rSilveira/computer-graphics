"""
Classe base abstrata para objetos geométricos 3D.
"""


class Geometry3D:
    """
    Classe base abstrata para objetos geométricos 3D.
    
    Define a interface comum para todos os objetos 3D renderizáveis.
    """
    
    def __init__(self, name):
        """
        Inicializa a geometria.
        
        Args:
            name (str): Nome do objeto geométrico
        """
        self.name = name
    
    def draw(self, use_shaders=False):
        """
        Desenha o objeto 3D.
        Deve ser implementado pelas subclasses.
        
        Args:
            use_shaders (bool): Se True, usa atributos de shader ao invés de pipeline fixo
        """
        raise NotImplementedError("Subclasses devem implementar draw()")