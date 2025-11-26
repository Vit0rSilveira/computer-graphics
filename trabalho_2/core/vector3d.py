import math


class Vector3D:
    """
    Classe para representar e manipular vetores 3D.
    
    Attributes:
        x (float): Componente X do vetor
        y (float): Componente Y do vetor
        z (float): Componente Z do vetor
    """
    
    def __init__(self, x=0.0, y=0.0, z=0.0):
        """
        Inicializa um vetor 3D.
        
        Args:
            x (float): Componente X
            y (float): Componente Y
            z (float): Componente Z
        """
        self.x = x
        self.y = y
        self.z = z
    
    def normalize(self):
        """
        Normaliza o vetor (transforma em vetor unitário).
        
        Returns:
            Vector3D: Vetor normalizado
        """
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length > 0:
            return Vector3D(self.x/length, self.y/length, self.z/length)
        return Vector3D(0, 0, 0)
    
    def dot(self, other):
        """
        Calcula o produto escalar com outro vetor.
        
        Args:
            other (Vector3D): Outro vetor
            
        Returns:
            float: Produto escalar
        """
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        """
        Calcula o produto vetorial com outro vetor.
        
        Args:
            other (Vector3D): Outro vetor
            
        Returns:
            Vector3D: Vetor resultante do produto vetorial
        """
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )
    
    def subtract(self, other):
        """
        Subtrai outro vetor deste vetor.
        
        Args:
            other (Vector3D): Vetor a subtrair
            
        Returns:
            Vector3D: Vetor resultante
        """
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def to_list(self):
        """Converte o vetor para lista [x, y, z]."""
        return [self.x, self.y, self.z]