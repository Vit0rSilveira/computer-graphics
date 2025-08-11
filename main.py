import pygame
import sys

def midpoint_line(x1, y1, x2, y2):
    pixels = []
    dx = x2 - x1
    dy = y2 - y1

    # Linha vertical
    if dx == 0:
        y_step = 1 if y2 > y1 else -1
        for y in range(y1, y2 + y_step, y_step):
            pixels.append((x1, y))
        return pixels

    # Linha horizontal
    if dy == 0:
        x_step = 1 if x2 > x1 else -1
        for x in range(x1, x2 + x_step, x_step):
            pixels.append((x, y1))
        return pixels

    # Direção
    x_step = 1 if dx > 0 else -1
    y_step = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx >= dy:
        # Itera pelo X
        d = 2 * dy - dx
        x, y = x1, y1
        pixels.append((x, y))
        for _ in range(dx):
            if d <= 0:
                d += 2 * dy
            else:
                d += 2 * (dy - dx)
                y += y_step
            x += x_step
            pixels.append((x, y))
    else:
        # Itera pelo Y
        d = 2 * dx - dy
        x, y = x1, y1
        pixels.append((x, y))
        for _ in range(dy):
            if d <= 0:
                d += 2 * dx
            else:
                d += 2 * (dx - dy)
                x += x_step
            y += y_step
            pixels.append((x, y))
    
    return pixels

def to_screen_coords(x, y, origin_x, origin_y):
    """
    Converte coordenadas do mundo (com origem no centro)
    para coordenadas de tela do Pygame (origem no canto superior esquerdo).
    """
    return origin_x + x, origin_y - y

def main():
    """
    Função principal usando Pygame para renderização.
    """
    pygame.init()
    
    width, height = 1000, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Algoritmo do Ponto Médio com Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30) 
    legendas = [
        ("Vitor da Silveira Paula - 10689651", (255, 255, 255)),
        ("Lucas Greff Meneses   - 13671615", (255, 255, 255)),
        ("Linha 1 (Branca)", (255, 255, 255)),
        ("Linha 2 (Verde)", (0, 255, 0)),
        ("Linha 3 (Vermelha)", (255, 0, 0)),
        ("Linha 4 (Amarela)", (255, 255, 0)),
        ("Linha 5 (Branca)", (255, 255, 255)),
        ("Linha 6 (Rosa)", (255, 0, 255)),
    ]
    running = True
    origin_x, origin_y = width // 2, height // 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Converte para coordenadas de tela
        line1_points = [to_screen_coords(x, y, origin_x, origin_y) for x, y in midpoint_line(-200, -200, 200, 200)]
        line2_points = [to_screen_coords(x, y, origin_x, origin_y) for x, y in midpoint_line(200, -200, -200, 200)]
        line3_points = [to_screen_coords(x, y, origin_x, origin_y) for x, y in midpoint_line(-100, -200, -100, 200)]
        line4_points = [to_screen_coords(x, y, origin_x, origin_y) for x, y in midpoint_line(100, -200, 100, 200)]
        line5_points = [to_screen_coords(x, 100, origin_x, origin_y) for x, y in midpoint_line(-150, 100, 150, 100)]
        line6_points = [to_screen_coords(x, -100, origin_x, origin_y) for x, y in midpoint_line(-150, -100, 150, -100)]

        # Desenha as linhas
        for x, y in line1_points: pygame.draw.rect(screen, (255, 255, 255), (x, y, 2, 2))
        for x, y in line2_points: pygame.draw.rect(screen, (0, 255, 0), (x, y, 2, 2))
        for x, y in line3_points: pygame.draw.rect(screen, (255, 0, 0), (x, y, 2, 2))
        for x, y in line4_points: pygame.draw.rect(screen, (255, 255, 0), (x, y, 2, 2))
        for x, y in line5_points: pygame.draw.rect(screen, (0, 255, 255), (x, y, 2, 2))
        for x, y in line6_points: pygame.draw.rect(screen, (255, 0, 255), (x, y, 2, 2))

        # Desenha legendas no canto
        y_offset = 10
        for texto, cor in legendas:
            superficie_texto = font.render(texto, True, cor)
            screen.blit(superficie_texto, (10, y_offset))
            y_offset += 25

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()