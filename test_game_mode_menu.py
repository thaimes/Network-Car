import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((850, 550))
pygame.display.set_caption("Test Game Mode Menu")
font = pygame.font.SysFont("Consolas", 40)

modes = ["Easy", "Medium", "Hard", "Free Drive"]
selected = 0

clock = pygame.time.Clock()

def draw_menu():
    screen.fill((0, 0, 0))
    title = font.render("Select Game Mode", True, (255, 255, 255))
    screen.blit(title, (250, 50))

    for i, mode in enumerate(modes):
        color = (0, 255, 0) if i == selected else (255, 255, 255)
        text = font.render(mode, True, color)
        screen.blit(text, (300, 150 + i * 60))

    pygame.display.update()

while True:
    draw_menu()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(modes)
            elif event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(modes)
            elif event.key == pygame.K_RETURN:
                print(f"Selected mode: {modes[selected]}")
                pygame.quit()
                sys.exit()

    clock.tick(30)
