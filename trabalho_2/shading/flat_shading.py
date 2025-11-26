from OpenGL.GL import *
from shading.shading_model import ShadingModel


class FlatShading(ShadingModel):
    """
    Implementação do modelo de iluminação Flat Shading.
    
    No Flat Shading, cada face do polígono tem uma cor uniforme,
    calculada usando a normal da face. Produz aparência facetada.
    A iluminação é calculada uma vez por primitiva.
    """
    
    def __init__(self):
        """Inicializa o modelo Flat Shading."""
        super().__init__("Flat Shading")
    
    def setup(self):
        """Configura o pipeline fixo para Flat Shading."""
        pass  # Não requer setup especial
    
    def apply(self):
        """
        Aplica o Flat Shading configurando GL_FLAT no OpenGL.
        
        Com GL_FLAT, a cor é calculada apenas uma vez por primitiva,
        usando a normal do primeiro vértice (provoking vertex).
        """
        glShadeModel(GL_FLAT)
        glUseProgram(0)