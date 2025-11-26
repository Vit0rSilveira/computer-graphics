from OpenGL.GL import *
from shading.shading_model import ShadingModel


class GouraudShading(ShadingModel):
    """
    Implementação do modelo de iluminação Gouraud Shading.
    
    No Gouraud Shading, a iluminação é calculada nos vértices e
    interpolada linearmente através da face. Produz transições suaves.
    A iluminação é calculada por vértice.
    """
    
    def __init__(self):
        """Inicializa o modelo Gouraud Shading."""
        super().__init__("Gouraud Shading")
    
    def setup(self):
        """Configura o pipeline fixo para Gouraud Shading."""
        pass  # Não requer setup especial
    
    def apply(self):
        """
        Aplica o Gouraud Shading configurando GL_SMOOTH no OpenGL.
        
        Com GL_SMOOTH, a cor é calculada em cada vértice e interpolada
        através da primitiva usando interpolação linear.
        """
        glShadeModel(GL_SMOOTH)
        glUseProgram(0)