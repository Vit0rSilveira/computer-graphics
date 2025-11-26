import math
from OpenGL.GL import *
from geometry.geometry3d import Geometry3D


class Cone(Geometry3D):
    """
    Implementação de um cone 3D (pirâmide circular).
    
    Cone com base circular e ápice superior.
    Compatível com shaders GLSL.
    """
    
    def __init__(self):
        """Inicializa o cone."""
        super().__init__("Cone")
        self.segments = 32  # Número de segmentos ao redor
        self.radius = 1.0
        self.height = 2.0
    
    def draw(self, use_shaders=False):
        """
        Renderiza o cone manualmente com vértices.
        
        Args:
            use_shaders (bool): Não usado
        """

        self._draw_body()
        

        self._draw_base()
    
    def _draw_body(self):
        """Desenha o corpo cônico (lateral) com normais por vértice (suavizadas)."""
        apex = [0.0, self.height, 0.0]  # Topo do cone

        glBegin(GL_TRIANGLES)

        for i in range(self.segments):
            # ângulos atual e próximo
            angle1 = (i / self.segments) * 2.0 * math.pi
            angle2 = ((i + 1) / self.segments) * 2.0 * math.pi

            # pontos na base
            x1 = math.cos(angle1) * self.radius
            z1 = math.sin(angle1) * self.radius
            x2 = math.cos(angle2) * self.radius
            z2 = math.sin(angle2) * self.radius

            base1 = [x1, 0.0, z1]
            base2 = [x2, 0.0, z2]

            # ---- Normal suavizada para base1 ----
            nx1 = x1 * (self.height / self.radius)
            ny1 = self.radius
            nz1 = z1 * (self.height / self.radius)
            len1 = math.sqrt(nx1*nx1 + ny1*ny1 + nz1*nz1)
            if len1 > 0.0:
                nx1 /= len1
                ny1 /= len1
                nz1 /= len1

            # ---- Normal suavizada para base2 ----
            nx2 = x2 * (self.height / self.radius)
            ny2 = self.radius
            nz2 = z2 * (self.height / self.radius)
            len2 = math.sqrt(nx2*nx2 + ny2*ny2 + nz2*nz2)
            if len2 > 0.0:
                nx2 /= len2
                ny2 /= len2
                nz2 /= len2

            # ---- Normal para o ápice ----
            # o ápice é singular; usar vetor médio/para cima costuma ficar bem
            # aqui uso uma normal voltada para cima (pode ajustar se quiser outro efeito)
            na = [0.0, 1.0, 0.0]

            # Escrever triângulo (cada vértice com sua normal)
            glNormal3f(nx1, ny1, nz1)
            glVertex3fv(base1)

            glNormal3f(nx2, ny2, nz2)
            glVertex3fv(base2)

            glNormal3f(na[0], na[1], na[2])
            glVertex3fv(apex)

        glEnd()

    
    def _draw_base(self):
        """Desenha a base circular do cone."""
        glBegin(GL_TRIANGLE_FAN)
        
        # Normal apontando para baixo
        glNormal3f(0, -1, 0)
        
        # Centro da base
        glVertex3f(0, 0, 0)
        
        # Vértices ao redor da base (invertido para face correta)
        for i in range(self.segments + 1):
            angle = (i / self.segments) * 2 * math.pi
            x = math.cos(angle) * self.radius
            z = math.sin(angle) * self.radius
            glVertex3f(x, 0, -z)  # -z para inverter winding
        
        glEnd()