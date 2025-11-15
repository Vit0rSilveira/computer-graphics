"""
Implementação do modelo Phong Shading usando shaders GLSL.

Este arquivo contém a implementação completa do algoritmo de Phong,
incluindo os shaders de vértice e fragmento escritos em GLSL.
"""

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from shading.shading_model import ShadingModel


# ============================================================================
# SHADERS GLSL PARA PHONG SHADING
# ============================================================================

# Vertex Shader para Phong Shading
PHONG_VERTEX_SHADER = """
#version 120

// Variáveis uniformes (transformações)
uniform mat4 model_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;
uniform mat3 normal_matrix;

// Variáveis de saída para o fragment shader
varying vec3 frag_position;  // Posição do fragmento no espaço mundo
varying vec3 frag_normal;    // Normal do fragmento no espaço mundo

void main()
{
    // Calcular posição no espaço mundo
    vec4 world_pos = model_matrix * gl_Vertex;
    frag_position = world_pos.xyz;
    
    // Transformar normal para espaço mundo
    frag_normal = normalize(normal_matrix * gl_Normal);
    
    // Posição final do vértice
    gl_Position = projection_matrix * view_matrix * world_pos;
}
"""

# Fragment Shader para Phong Shading
PHONG_FRAGMENT_SHADER = """
#version 120

// Variáveis de entrada do vertex shader
varying vec3 frag_position;
varying vec3 frag_normal;

// Propriedades da luz
uniform vec3 light_position;
uniform vec3 light_ambient;
uniform vec3 light_diffuse;
uniform vec3 light_specular;

// Propriedades do material
uniform vec3 material_ambient;
uniform vec3 material_diffuse;
uniform vec3 material_specular;
uniform float material_shininess;

// Posição da câmera
uniform vec3 view_position;

void main()
{
    // Normalizar a normal (pode ter sido interpolada)
    vec3 normal = normalize(frag_normal);
    
    // Vetor da superfície até a luz
    vec3 light_dir = normalize(light_position - frag_position);
    
    // Vetor da superfície até a câmera
    vec3 view_dir = normalize(view_position - frag_position);
    
    // Vetor de reflexão (usado no modelo de Phong)
    vec3 reflect_dir = reflect(-light_dir, normal);
    
    // ========================================================================
    // ALGORITMO DE PHONG - COMPONENTES DE ILUMINAÇÃO
    // ========================================================================
    
    // --- COMPONENTE AMBIENTE (aumentada significativamente) ---
    vec3 ambient = light_ambient * material_ambient * 2.0;
    
    // --- COMPONENTE DIFUSA (Lei de Lambert) ---
    float diff = max(dot(normal, light_dir), 0.0);
    vec3 diffuse = light_diffuse * (diff * material_diffuse) * 1.2;
    
    // --- COMPONENTE ESPECULAR (Modelo de Phong) ---
    float spec = 0.0;
    if (diff > 0.0) {
        spec = pow(max(dot(view_dir, reflect_dir), 0.0), material_shininess);
    }
    vec3 specular = light_specular * (spec * material_specular) * 0.8;
    
    // ========================================================================
    // COR FINAL = AMBIENTE + DIFUSA + ESPECULAR
    // ========================================================================
    vec3 result = ambient + diffuse + specular;
    
    // Garantir que a cor não exceda 1.0
    result = clamp(result, 0.0, 1.0);
    
    gl_FragColor = vec4(result, 1.0);
}
"""


class PhongShading(ShadingModel):
    """
    Implementação do modelo de iluminação Phong Shading usando shaders GLSL.
    """
    
    def __init__(self):
        """Inicializa o modelo Phong Shading."""
        super().__init__("Phong Shading")
        self.shader_program = None
        self.vertex_shader = None
        self.fragment_shader = None
    
    def setup(self):
        """
        Compila e linka os shaders GLSL para Phong Shading.
        """
        try:
            # Compilar vertex shader
            self.vertex_shader = shaders.compileShader(
                PHONG_VERTEX_SHADER, 
                GL_VERTEX_SHADER
            )
            
            # Compilar fragment shader
            self.fragment_shader = shaders.compileShader(
                PHONG_FRAGMENT_SHADER, 
                GL_FRAGMENT_SHADER
            )
            
            # Linkar programa
            self.shader_program = shaders.compileProgram(
                self.vertex_shader, 
                self.fragment_shader
            )
            
            print(f"✓ Shaders Phong compilados com sucesso! Program ID: {self.shader_program}")
            
        except Exception as e:
            print(f"✗ Erro ao compilar shaders Phong: {e}")
            self.shader_program = None
    
    def apply(self):
        """
        Ativa o shader program do Phong Shading.
        """
        if self.shader_program:
            glUseProgram(self.shader_program)
        else:
            # Fallback para Gouraud se shaders não disponíveis
            glShadeModel(GL_SMOOTH)
            glUseProgram(0)
    
    def set_uniforms(self, light, material, camera_pos, model_matrix, view_matrix, proj_matrix):
        """
        Define as variáveis uniform dos shaders.
        
        Args:
            light (Light): Fonte de luz da cena
            material (Material): Material do objeto
            camera_pos (Vector3D): Posição da câmera
            model_matrix (np.array): Matriz modelo (4x4)
            view_matrix (np.array): Matriz view (4x4)
            proj_matrix (np.array): Matriz projeção (4x4)
        """
        if not self.shader_program:
            return
        
        # ====================================================================
        # MATRIZES DE TRANSFORMAÇÃO
        # ====================================================================
        
        model_loc = glGetUniformLocation(self.shader_program, "model_matrix")
        view_loc = glGetUniformLocation(self.shader_program, "view_matrix")
        proj_loc = glGetUniformLocation(self.shader_program, "projection_matrix")
        
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_matrix)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_matrix)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, proj_matrix)
        
        # Matriz de normais
        try:
            normal_matrix = np.linalg.inv(model_matrix[:3, :3]).T
            normal_matrix = normal_matrix.astype(np.float32)
        except:
            normal_matrix = np.identity(3, dtype=np.float32)
        
        normal_loc = glGetUniformLocation(self.shader_program, "normal_matrix")
        glUniformMatrix3fv(normal_loc, 1, GL_FALSE, normal_matrix)
        
        # ====================================================================
        # PROPRIEDADES DA LUZ
        # ====================================================================
        
        light_pos_loc = glGetUniformLocation(self.shader_program, "light_position")
        light_amb_loc = glGetUniformLocation(self.shader_program, "light_ambient")
        light_diff_loc = glGetUniformLocation(self.shader_program, "light_diffuse")
        light_spec_loc = glGetUniformLocation(self.shader_program, "light_specular")
        
        glUniform3f(light_pos_loc, light.position.x, light.position.y, light.position.z)
        glUniform3fv(light_amb_loc, 1, light.ambient)
        glUniform3fv(light_diff_loc, 1, light.diffuse)
        glUniform3fv(light_spec_loc, 1, light.specular)
        
        # ====================================================================
        # PROPRIEDADES DO MATERIAL - USAR COR DO OPENGL
        # ====================================================================
        
        # Pegar cor atual do OpenGL (glColor)
        current_color = glGetFloatv(GL_CURRENT_COLOR)
        color_rgb = [current_color[0], current_color[1], current_color[2]]
        
        mat_amb_loc = glGetUniformLocation(self.shader_program, "material_ambient")
        mat_diff_loc = glGetUniformLocation(self.shader_program, "material_diffuse")
        mat_spec_loc = glGetUniformLocation(self.shader_program, "material_specular")
        mat_shin_loc = glGetUniformLocation(self.shader_program, "material_shininess")
        
        # Componente ambiente: 30% da cor
        ambient_color = [c * 0.3 for c in color_rgb]
        glUniform3f(mat_amb_loc, ambient_color[0], ambient_color[1], ambient_color[2])
        
        # Componente difusa: cor completa
        glUniform3f(mat_diff_loc, color_rgb[0], color_rgb[1], color_rgb[2])
        
        # Componente especular: branco
        glUniform3f(mat_spec_loc, 1.0, 1.0, 1.0)
        
        # Brilho
        glUniform1f(mat_shin_loc, material.shininess)
        
        # ====================================================================
        # POSIÇÃO DA CÂMERA
        # ====================================================================
        
        view_pos_loc = glGetUniformLocation(self.shader_program, "view_position")
        glUniform3f(view_pos_loc, camera_pos.x, camera_pos.y, camera_pos.z)
        
        # Debug: imprimir valores
        print(f"DEBUG Phong:")
        print(f"  Cor do objeto: {color_rgb}")
        print(f"  Luz posição: ({light.position.x:.1f}, {light.position.y:.1f}, {light.position.z:.1f})")
        print(f"  Câmera posição: ({camera_pos.x:.1f}, {camera_pos.y:.1f}, {camera_pos.z:.1f})")
    
    def cleanup(self):
        """Libera recursos dos shaders."""
        if self.shader_program:
            glDeleteProgram(self.shader_program)
        if self.vertex_shader:
            glDeleteShader(self.vertex_shader)
        if self.fragment_shader:
            glDeleteShader(self.fragment_shader)