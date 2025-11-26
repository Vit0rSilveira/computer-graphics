class ShadingModel:
    """
    Classe base abstrata para modelos de iluminação/sombreamento.
    
    Define a interface comum para todos os modelos de iluminação.
    """
    
    def __init__(self, name):
        """
        Inicializa o modelo de sombreamento.
        
        Args:
            name (str): Nome do modelo
        """
        self.name = name
    
    def setup(self):
        """Configura o modelo de sombreamento. Implementado pelas subclasses."""
        raise NotImplementedError("Subclasses devem implementar setup()")
    
    def apply(self):
        """Aplica o modelo de sombreamento. Implementado pelas subclasses."""
        raise NotImplementedError("Subclasses devem implementar apply()")
    
    def cleanup(self):
        """Limpa recursos do modelo. Implementado pelas subclasses."""
        pass