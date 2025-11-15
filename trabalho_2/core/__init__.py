"""
Módulo core contendo classes fundamentais da cena 3D.
"""

from core.vector3d import Vector3D
from core.light import Light
from core.material import Material
from core.camera import Camera
from core.scene import Scene3D

__all__ = ['Vector3D', 'Light', 'Material', 'Camera', 'Scene3D']