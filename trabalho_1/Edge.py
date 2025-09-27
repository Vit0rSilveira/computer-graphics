from dataclasses import dataclass

@dataclass
class Edge:
    """ 
    Representa uma aresta usada no algoritmo de preenchimento com ET/AET. 
    
    Atributos:

    ymax (int): linha Y máxima onde a aresta é válida.

    x (float): coordenada X inicial (na linha de início da aresta).

    inv_slope (float): inverso da inclinação da aresta (dx/dy), usado para atualizar X a cada varredura de linha. 
    
    """
    
    ymax: int
    x: float
    inv_slope: float