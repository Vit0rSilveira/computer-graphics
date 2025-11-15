"""
Módulo shading contendo implementações de modelos de iluminação.
"""

from shading.shading_model import ShadingModel
from shading.flat_shading import FlatShading
from shading.gouraud_shading import GouraudShading
from shading.phong_shading import PhongShading

__all__ = ['ShadingModel', 'FlatShading', 'GouraudShading', 'PhongShading']