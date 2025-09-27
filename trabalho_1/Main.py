import sys
from MainWindow import MainWindow
from PyQt6.QtWidgets import QApplication

"""
Trabalho 1 — Preenchimento de Polígono (ET/AET) com Qt + OpenGL
=================================================================

Este programa permite desenhar polígonos clicando na tela, fechá-los e preenchê-los
usando o algoritmo de Edge Table (ET) e Active Edge Table (AET).  

Funcionalidades:
- Adicionar vértices com clique esquerdo.
- Alternar exibição dos vértices com clique direito.
- Fechar polígono e preencher com cor escolhida.
- Ajustar espessura do contorno.
- Carregar exemplos de polígonos.

Requisitos:
-------------
- Python 3.10 ou superior
- PyQt6
- PyOpenGL

Instalação e execução
--------------------

**1. Criar e ativar ambiente virtual**

Windows (CMD):
    python -m venv venv
    .\venv\Scripts\activate.bat

Windows (PowerShell):
    python -m venv venv
    .\venv\Scripts\Activate.ps1

Linux/macOS:
    python3 -m venv venv
    source venv/bin/activate

**2. Instalar dependências**
    
Windows/Linux/macOS (com venv ativo):
    pip install PyQt6 PyOpenGL

**3. Executar o programa**

Windows:
    python Main.py

Linux/macOS:
    python3 Main.py

Observações:
-------------
- No Windows PowerShell, caso dê erro de execução de scripts, use:
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

- O programa funciona em sistemas Windows, Linux e macOS.
"""

class Main():
    """ 
    Função principal da aplicação. 
    Cria o QApplication, instancia a janela principal e inicia o loop da interface. 
    """
    def execute(self):
        app = QApplication(sys.argv)
        w = MainWindow()
        w.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    Main().execute()