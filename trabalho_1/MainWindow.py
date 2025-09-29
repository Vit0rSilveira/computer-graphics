from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QColorDialog, QMessageBox, 
    QLabel, QSpinBox, QComboBox
)
from PyQt6.QtCore import Qt
from GlCanvas import GLCanvas
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):
    """ 
    Janela principal da aplicação. Contém o canvas OpenGL e as ferramentas de interação (toolbar e menu). 
    
    Atributos: 
    
    canvas (GLCanvas): área de desenho principal. 
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trabalho 1: Preencher Polígono com (ET/AET)")
        self.resize(1000, 700)

        self.canvas = GLCanvas()
        self.setCentralWidget(self.canvas)

        self._make_toolbar()
        self._make_menubar()

    def _make_toolbar(self):
        """ 
        Cria a barra de ferramentas com botões de: 
        
        • fechar polígono 
        
        • preencher 
        
        • limpar 
        
        • escolher cor 
        
        • ajustar espessura 
        
        • escolher exemplos 
        """

        tb = QToolBar("Tools")
        tb.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, tb)

        # Close polygon
        act_close = QAction("Close Polygon", self)
        act_close.triggered.connect(self.canvas.close_polygon)
        tb.addAction(act_close)

        # Fill
        act_fill = QAction("Fill", self)
        act_fill.triggered.connect(self.canvas.fill)
        tb.addAction(act_fill)

        # Clear
        act_clear = QAction("Clear", self)
        act_clear.triggered.connect(self.canvas.clear)
        tb.addAction(act_clear)

        tb.addSeparator()

        # Fill color
        act_color = QAction("Fill Color", self)
        act_color.triggered.connect(self.pick_color)
        tb.addAction(act_color)

        # Stroke width spinner
        tb.addSeparator()
        tb.addWidget(QLabel("Stroke Width:"))
        spin = QSpinBox()
        spin.setRange(1, 20)
        spin.setValue(self.canvas.stroke_width)
        spin.valueChanged.connect(self.canvas.set_stroke_width)
        tb.addWidget(spin)

        # Example dropdown
        tb.addSeparator()
        tb.addWidget(QLabel("Examples:"))
        combo = QComboBox()
        combo.addItems(["(choose)", "Convex pentagon", "Concave arrow"])
        combo.currentTextChanged.connect(self._on_example)
        tb.addWidget(combo)

    def _make_menubar(self):
        """ 
        Cria a barra de menus com: 
        
        • File (sair) 
        
        • Examples (carregar exemplos) 
        
        • Help (sobre o programa) 
        """

        mb = self.menuBar()
        file_m = mb.addMenu("&File")
        act_exit = QAction("Exit", self)
        act_exit.triggered.connect(self.close)
        file_m.addAction(act_exit)

        ex_m = mb.addMenu("&Examples")
        for name in ["Convex pentagon", "Concave arrow", "Complex concave"]:
            act = QAction(name, self)
            act.triggered.connect(lambda checked=False, n=name: self.canvas.load_example(n))
            ex_m.addAction(act)

        help_m = mb.addMenu("&Help")
        act_about = QAction("About", self)
        act_about.triggered.connect(self._about)
        help_m.addAction(act_about)

        act_duo = QAction("Integrantes", self)
        act_duo.triggered.connect(self._show_duo)
        help_m.addAction(act_duo)

    def _about(self):
        """ 
        Exibe uma janela de informação com instruções de uso do programa. 
        """

        QMessageBox.information(self, "Sobre", (
            "Preenchimento de polígonos usando Edge Table (ET) e Active Edge Table (AET)\n\n"
            "• Adicione vértices com o clique esquerdo. Clique direito alterna a exibição dos vértices.\n"
            "• Feche o polígono e depois clique em Preencher.\n"
            "• Esta implementação desenha os spans por scanline usando GL_LINES.\n"
            "• Projetado para polígonos simples/concavos (não auto-intersectantes)."
        ))

    def pick_color(self):
        """ 
        Abre diálogo para o usuário escolher a cor de preenchimento. 
        """

        c = QColorDialog.getColor(self.canvas.fill_color, self, "Choose Fill Color",
                                  QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if c.isValid():
            self.canvas.set_fill_color(c)

    def _on_example(self, text: str):
        """ 
        Carrega polígono de exemplo quando selecionado no dropdown. 
        """

        if text and text != "(choose)":
            self.canvas.load_example(text)

    def _show_duo(self):
        QMessageBox.information(
            self,
            "Dupla",
            "Integrantes:\n\n"
            "Lucas Greff Meneses 13671615\n"
            "Vitor da Silveira Paula 10689651"
        )