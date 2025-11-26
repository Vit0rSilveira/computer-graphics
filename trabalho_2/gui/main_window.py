from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QSlider, QComboBox,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt

from gui.opengl_widget import OpenGLWidget


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação de visualização 3D.
    
    Gerencia a interface do usuário, incluindo:
    - Widget OpenGL para renderização 3D
    - Painel de controle com sliders e comboboxes
    - Conexões entre controles da UI e parâmetros de renderização
    - Timer para animação
    
    A janela é dividida em duas seções:
    - Área de visualização 3D (esquerda, 75% da largura)
    - Painel de controles (direita, 25% da largura)
    
    Attributes:
        gl_widget (OpenGLWidget): Widget de renderização OpenGL
        comparison_btn (QPushButton): Botão para alternar modo comparação
        object_combo (QComboBox): Seletor de tipo de objeto
        shading_combo (QComboBox): Seletor de modelo de iluminação
        projection_combo (QComboBox): Seletor de tipo de projeção
        rot_x_slider, rot_y_slider, rot_z_slider (QSlider): Controles de rotação
        scale_slider (QSlider): Controle de escala
        light_x_slider, light_y_slider, light_z_slider (QSlider): Controles de luz
        animate_btn (QPushButton): Botão de animação
    """
    
    def __init__(self):
        """
        Inicializa a janela principal e configura a interface.
        
        Cria o layout principal, instancia o widget OpenGL,
        constrói o painel de controle e estabelece as dimensões da janela.
        """
        super().__init__()
        self.setWindowTitle("Trabalho 2 - Computação Gráfica 3D com Iluminação")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # OpenGL Widget (75% da largura)
        self.gl_widget = OpenGLWidget()
        self.gl_widget.setFocus() 
        main_layout.addWidget(self.gl_widget, 3)
        
        # Painel de controle (25% da largura)
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)
        
    def create_control_panel(self):
        """
        Cria e configura o painel de controle lateral.
        
        Returns:
            QWidget: Painel contendo todos os controles da interface
            
        O painel inclui grupos organizados de controles:
        1. Informações e instruções de uso
        2. Seleção de objeto (cubo, pirâmide, Cone, esfera)
        3. Modelo de iluminação (Flat, Gouraud, Phong)
        4. Botão de modo comparação
        5. Tipo de projeção (perspectiva/ortográfica)
        6. Controles de rotação (X, Y, Z) com sliders
        7. Controle de escala
        8. Controles de posição da luz (X, Y, Z)
        9. Botões de ação (animar, resetar)
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Título
        title = QLabel("Controles 3D")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Instruções
        instructions = QLabel(
            "🖱️ Arraste: Rotacionar câmera\n"
            "🖱️ Scroll: Zoom\n"
            "⬆️⬇️ Setas: Translação no eixo Y\n"
            "⬅️➡️ Setas: Translação no eixo X\n"
            "W / S: Translação no eixo Z\n"
            "✨ Phong usa shaders GLSL"
        )
        instructions.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(instructions)
        
        # GRUPO: SELEÇÃO DE OBJETO
        object_group = QGroupBox("Objeto")
        object_layout = QVBoxLayout()
        
        self.object_combo = QComboBox()
        self.object_combo.addItems(['Cubo', 'Pirâmide', 'Cone', 'Esfera'])
        self.object_combo.currentTextChanged.connect(self.change_object)
        object_layout.addWidget(QLabel("Tipo:"))
        object_layout.addWidget(self.object_combo)
        
        object_group.setLayout(object_layout)
        layout.addWidget(object_group)
        
        # GRUPO: MODELO DE ILUMINAÇÃO
        lighting_group = QGroupBox("Modelo de Iluminação")
        lighting_layout = QVBoxLayout()
        
        self.shading_combo = QComboBox()
        self.shading_combo.addItems(['Flat', 'Gouraud', 'Phong'])
        self.shading_combo.setCurrentIndex(1)  # Gouraud default
        self.shading_combo.currentTextChanged.connect(self.change_shading)
        lighting_layout.addWidget(QLabel("Modelo:"))
        lighting_layout.addWidget(self.shading_combo)
        
        lighting_group.setLayout(lighting_layout)
        layout.addWidget(lighting_group)
        
        # BOTÃO: MODO COMPARAÇÃO
        comparison_btn = QPushButton("🔀 Modo Comparação")
        comparison_btn.setCheckable(True)
        comparison_btn.clicked.connect(self.toggle_comparison_mode)
        comparison_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                font-weight: bold;
                background-color: #2a5a8a;
                color: white;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #3a7abd;
            }
            QPushButton:hover {
                background-color: #356a9a;
            }
        """)
        layout.addWidget(comparison_btn)
        self.comparison_btn = comparison_btn
        
        # GRUPO: TIPO DE PROJEÇÃO
        projection_group = QGroupBox("Projeção")
        projection_layout = QVBoxLayout()
        
        self.projection_combo = QComboBox()
        self.projection_combo.addItems(['Perspectiva', 'Ortográfica'])
        self.projection_combo.currentTextChanged.connect(self.change_projection)
        projection_layout.addWidget(QLabel("Tipo:"))
        projection_layout.addWidget(self.projection_combo)
        
        projection_group.setLayout(projection_layout)
        layout.addWidget(projection_group)
        
        # GRUPO: ROTAÇÃO DO OBJETO
        rotation_group = QGroupBox("Rotação do Objeto")
        rotation_layout = QGridLayout()
        
        self.rot_x_label = QLabel("X: 30°")
        rotation_layout.addWidget(self.rot_x_label, 0, 0)
        self.rot_x_slider = self.create_slider(0, 360, 30, self.update_rotation_x)
        rotation_layout.addWidget(self.rot_x_slider, 0, 1)
        
        self.rot_y_label = QLabel("Y: 45°")
        rotation_layout.addWidget(self.rot_y_label, 1, 0)
        self.rot_y_slider = self.create_slider(0, 360, 45, self.update_rotation_y)
        rotation_layout.addWidget(self.rot_y_slider, 1, 1)
        
        self.rot_z_label = QLabel("Z: 0°")
        rotation_layout.addWidget(self.rot_z_label, 2, 0)
        self.rot_z_slider = self.create_slider(0, 360, 0, self.update_rotation_z)
        rotation_layout.addWidget(self.rot_z_slider, 2, 1)
        
        rotation_group.setLayout(rotation_layout)
        layout.addWidget(rotation_group)
        
        # GRUPO: ESCALA
        scale_group = QGroupBox("Escala")
        scale_layout = QVBoxLayout()
        
        self.scale_label = QLabel("Escala: 1.0x")
        scale_layout.addWidget(self.scale_label)
        self.scale_slider = self.create_slider(10, 200, 100, self.update_scale)
        scale_layout.addWidget(self.scale_slider)
        
        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)
        
        # GRUPO: POSIÇÃO DA LUZ
        light_group = QGroupBox("Posição da Luz")
        light_layout = QGridLayout()
        
        self.light_x_label = QLabel("X: 3.0")
        light_layout.addWidget(self.light_x_label, 0, 0)
        self.light_x_slider = self.create_slider(-50, 50, 30, self.update_light_x)
        light_layout.addWidget(self.light_x_slider, 0, 1)
        
        self.light_y_label = QLabel("Y: 3.0")
        light_layout.addWidget(self.light_y_label, 1, 0)
        self.light_y_slider = self.create_slider(-50, 50, 30, self.update_light_y)
        light_layout.addWidget(self.light_y_slider, 1, 1)
        
        self.light_z_label = QLabel("Z: 3.0")
        light_layout.addWidget(self.light_z_label, 2, 0)
        self.light_z_slider = self.create_slider(-50, 50, 30, self.update_light_z)
        light_layout.addWidget(self.light_z_slider, 2, 1)
        
        light_group.setLayout(light_layout)
        layout.addWidget(light_group)
        
        # BOTÕES DE AÇÃO
        btn_layout = QVBoxLayout()
        
        self.animate_btn = QPushButton("▶ Animar Rotação")
        self.animate_btn.clicked.connect(self.toggle_animation)
        btn_layout.addWidget(self.animate_btn)
        
        reset_btn = QPushButton("🔄 Resetar Vista")
        reset_btn.clicked.connect(self.reset_view)
        btn_layout.addWidget(reset_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return panel
    
    # ========================================================================
    # MÉTODOS AUXILIARES
    # ========================================================================
    
    def create_slider(self, min_val, max_val, default, callback):
        """
        Cria um slider horizontal configurado.
        
        Args:
            min_val (int): Valor mínimo do slider
            max_val (int): Valor máximo do slider
            default (int): Valor inicial do slider
            callback (callable): Função a ser chamada quando o valor muda
            
        Returns:
            QSlider: Slider configurado e conectado ao callback
            
        Função auxiliar para reduzir repetição de código na criação
        de múltiplos sliders com configurações similares.
        """
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default)
        slider.valueChanged.connect(callback)
        return slider
    
    # ========================================================================
    # CALLBACKS DOS CONTROLES
    # ========================================================================
    
    def change_object(self, text):
        """
        Altera o tipo de objeto a ser renderizado.
        
        Args:
            text (str): Nome do objeto em português ('Cubo', 'Pirâmide', 'Cone', 'Esfera')
            
        Converte o texto da interface para o identificador interno
        e atualiza o widget OpenGL.
        """
        obj_map = {
            'Cubo': 'cube', 
            'Pirâmide': 'pyramid', 
            'Cone': 'cone', 
            'Esfera': 'sphere'
        }
        self.gl_widget.scene.current_object = obj_map[text]
        self.gl_widget.update()
    
    def change_shading(self, text):
        """
        Altera o modelo de iluminação/sombreamento.
        
        Args:
            text (str): Nome do modelo ('Flat', 'Gouraud', 'Phong')
            
        Atualiza o modelo de sombreamento usado na renderização.
        - Flat: sombreamento uniforme por face
        - Gouraud: interpolação de cores nos vértices
        - Phong: interpolação de normais (cálculo por pixel com shaders)
        """
        shade_map = {
            'Flat': 'flat', 
            'Gouraud': 'gouraud', 
            'Phong': 'phong'
        }
        self.gl_widget.scene.current_shading = shade_map[text]
        self.gl_widget.update()
    
    def change_projection(self, text):
        """
        Altera o tipo de projeção da cena.
        
        Args:
            text (str): Tipo de projeção ('Perspectiva', 'Ortográfica')
            
        - Perspectiva: objetos mais distantes aparecem menores (realista)
        - Ortográfica: linhas paralelas permanecem paralelas (técnico)
        """
        proj_map = {
            'Perspectiva': 'perspective', 
            'Ortográfica': 'orthographic'
        }
        self.gl_widget.set_projection_type(proj_map[text])
    
    def update_rotation_x(self, value):
        """
        Atualiza a rotação do objeto no eixo X.
        
        Args:
            value (int): Ângulo de rotação em graus (0-360)
            
        Atualiza tanto o objeto OpenGL quanto o label que mostra o valor atual.
        """
        self.gl_widget.rotation_x = value
        self.rot_x_label.setText(f"X: {value}°")
        self.gl_widget.update()
    
    def update_rotation_y(self, value):
        """
        Atualiza a rotação do objeto no eixo Y.
        
        Args:
            value (int): Ângulo de rotação em graus (0-360)
        """
        self.gl_widget.rotation_y = value
        self.rot_y_label.setText(f"Y: {value}°")
        self.gl_widget.update()
    
    def update_rotation_z(self, value):
        """
        Atualiza a rotação do objeto no eixo Z.
        
        Args:
            value (int): Ângulo de rotação em graus (0-360)
        """
        self.gl_widget.rotation_z = value
        self.rot_z_label.setText(f"Z: {value}°")
        self.gl_widget.update()
    
    def update_scale(self, value):
        """
        Atualiza o fator de escala do objeto.
        
        Args:
            value (int): Valor do slider (10-200), convertido para fator (0.1-2.0)
            
        Um valor de 100 corresponde à escala normal (1.0x).
        """
        self.gl_widget.scale_factor = value / 100.0
        self.scale_label.setText(f"Escala: {value/100:.1f}x")
        self.gl_widget.update()
    
    def update_light_x(self, value):
        """
        Atualiza a posição X da fonte de luz.
        
        Args:
            value (int): Valor do slider (-50 a 50), convertido para coordenada (-5.0 a 5.0)
        """
        self.gl_widget.scene.light.position.x = value / 10.0
        self.light_x_label.setText(f"X: {value/10:.1f}")
        self.gl_widget.update()
    
    def update_light_y(self, value):
        """
        Atualiza a posição Y da fonte de luz.
        
        Args:
            value (int): Valor do slider (-50 a 50), convertido para coordenada (-5.0 a 5.0)
        """
        self.gl_widget.scene.light.position.y = value / 10.0
        self.light_y_label.setText(f"Y: {value/10:.1f}")
        self.gl_widget.update()
    
    def update_light_z(self, value):
        """
        Atualiza a posição Z da fonte de luz.
        
        Args:
            value (int): Valor do slider (-50 a 50), convertido para coordenada (-5.0 a 5.0)
        """
        self.gl_widget.scene.light.position.z = value / 10.0
        self.light_z_label.setText(f"Z: {value/10:.1f}")
        self.gl_widget.update()
    
    def toggle_animation(self):
        """
        Alterna o estado da animação automática.
        
        Quando ativada, a animação rotaciona o objeto continuamente
        no eixo Y a ~60 FPS (16ms por frame).
        
        Estados:
        - Desligado: botão mostra "▶ Animar Rotação"
        - Ligado: botão mostra "⏸ Parar Animação"
        """
        if self.gl_widget.animate:
            self.gl_widget.animate = False
            self.gl_widget.timer.stop()
            self.animate_btn.setText("▶ Animar Rotação")
        else:
            self.gl_widget.animate = True
            self.gl_widget.timer.start(16)  # ~60 FPS
            self.animate_btn.setText("⏸ Parar Animação")
            # Conectar o timer ao método de animação
            self.gl_widget.timer.timeout.connect(self.start_animation)
    
    def start_animation(self):
        """
        Incrementa a rotação Y do objeto para criar animação.
        
        Chamado pelo timer a cada frame quando a animação está ativa.
        Incrementa a rotação em 2° por frame e atualiza o slider correspondente.
        """
        if self.gl_widget.animate:
            self.gl_widget.rotation_y = (self.gl_widget.rotation_y + 2) % 360
            self.rot_y_slider.setValue(int(self.gl_widget.rotation_y))
    
    def reset_view(self):
        """
        Reseta todos os parâmetros de visualização para valores padrão.
        
        Restaura:
        - Rotações para valores iniciais (X=30°, Y=45°, Z=0°)
        - Escala para 1.0x
        - Distância da câmera para 8.0 unidades
        - Ângulos da câmera para 0° (vista frontal)
        - Todos os sliders para posições correspondentes
        """
        self.gl_widget.rotation_x = 30
        self.gl_widget.rotation_y = 45
        self.gl_widget.rotation_z = 0
        self.gl_widget.scale_factor = 1.0

        # Resetar translação para a origem
        self.gl_widget.translation_x = 0.0
        self.gl_widget.translation_y = 0.0
        self.gl_widget.translation_z = 0.0

        self.gl_widget.scene.camera.distance = 8.0
        self.gl_widget.scene.camera.angle_x = 0
        self.gl_widget.scene.camera.angle_y = 0
        
        self.rot_x_slider.setValue(30)
        self.rot_y_slider.setValue(45)
        self.rot_z_slider.setValue(0)
        self.scale_slider.setValue(100)
        
        self.gl_widget.update()
    
    def toggle_comparison_mode(self, checked):
        """
        Alterna entre modo normal e modo comparação lado a lado.
        
        Args:
            checked (bool): True se o botão está pressionado (modo comparação ativo)
            
        No modo comparação:
        - Desenha 3 objetos com diferentes modelos de iluminação
        - Câmera se afasta para mostrar os 3 objetos
        - Seletor de modelo de iluminação é desabilitado
        - Botão mostra checkmark (✓)
        
        No modo normal:
        - Desenha um único objeto
        - Câmera volta à distância padrão
        - Seletor de modelo de iluminação é habilitado
        """
        self.gl_widget.comparison_mode = checked
        
        if checked:
            # Ajustar câmera para visualização melhor dos 3 objetos
            self.gl_widget.scene.camera.distance = 12.0
            self.comparison_btn.setText("🔀 Modo Comparação ✓")
            self.shading_combo.setEnabled(False)
        else:
            # Voltar para distância normal
            self.gl_widget.scene.camera.distance = 8.0
            self.comparison_btn.setText("🔀 Modo Comparação")
            self.shading_combo.setEnabled(True)

            self.gl_widget.reset_opengl_state()

        self.gl_widget.update()

    