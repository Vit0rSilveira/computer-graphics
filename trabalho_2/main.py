"""
Sistema de Visualização 3D com Modelos de Iluminação
Trabalho 2 - SCC 250 - Computação Gráfica

Arquivo principal que inicia a aplicação.

Estrutura do projeto:
trabalho_2/
├── main.py                    # Arquivo principal (este arquivo)
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # Janela principal
│   └── opengl_widget.py       # Widget OpenGL
├── core/
│   ├── __init__.py
│   ├── vector3d.py            # Classe Vector3D
│   ├── light.py               # Classe Light
│   ├── material.py            # Classe Material
│   ├── camera.py              # Classe Camera
│   └── scene.py               # Classe Scene3D
├── shading/
│   ├── __init__.py
│   ├── shading_model.py       # Classe base ShadingModel
│   ├── flat_shading.py        # Flat Shading
│   ├── gouraud_shading.py     # Gouraud Shading
│   └── phong_shading.py       # Phong Shading com shaders GLSL
└── geometry/
    ├── __init__.py
    ├── geometry3d.py          # Classe base Geometry3D
    ├── cube.py                # Cubo
    ├── pyramid.py             # Pirâmide
    ├── cylinder.py            # Cilindro
    └── sphere.py              # Esfera

Requisitos:
- Python 3.8+
- PyQt6
- PyOpenGL
- numpy

Instalação:
    pip install PyQt6 PyOpenGL PyOpenGL_accelerate numpy

Execução:
    python main.py

Autores: Vitor e greff
Data: Novembro 2025
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """
    Função principal da aplicação.
    
    Responsabilidades:
    1. Criar a aplicação Qt (QApplication)
    2. Instanciar a janela principal (MainWindow)
    3. Exibir a janela
    4. Iniciar o loop de eventos
    
    O loop de eventos continua até que o usuário feche a janela,
    momento em que sys.exit() encerra o programa com o código de saída apropriado.
    """
    # Criar aplicação Qt
    app = QApplication(sys.argv)
    
    # Configurar nome da aplicação (aparece no gerenciador de tarefas)
    app.setApplicationName("Trabalho CG - Iluminação 3D")
    app.setOrganizationName("ICMC-USP")
    
    # Criar e exibir janela principal
    window = MainWindow()
    window.show()
    
    # Iniciar loop de eventos e encerrar com código apropriado
    sys.exit(app.exec())


if __name__ == '__main__':
    """
    Ponto de entrada do programa.
    
    Este bloco só é executado quando o arquivo é rodado diretamente
    (python main.py), não quando é importado como módulo.
    """
    main()