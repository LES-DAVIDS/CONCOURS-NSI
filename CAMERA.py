import pygame
import sys

pygame.init()

# Taille de la fenêtre
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Caméra qui suit")

# Charger la map
map_image = pygame.image.load("ma_map.png")
map_width = map_image.get_width()
map_height = map_image.get_height()

# Position du personnage (dans le monde, pas l'écran)
player_x = 400
player_y = 300
player_speed = 5

# Position de la caméra (coin supérieur gauche visible)
camera_x = 0
camera_y = 0

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Déplacement du personnage
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    if keys[pygame.K_UP]:
        player_y -= player_speed
    if keys[pygame.K_DOWN]:
        player_y += player_speed

    # Centrer la caméra sur le personnage
    camera_x = player_x - SCREEN_WIDTH // 2
    camera_y = player_y - SCREEN_HEIGHT // 2

    # Limiter la caméra aux bords de la map
    camera_x = max(0, min(camera_x, map_width - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, map_height - SCREEN_HEIGHT))

    # Afficher la map avec le décalage de la caméra
    screen.blit(map_image, (-camera_x, -camera_y))

    # Afficher le personnage (position écran = position monde - caméra)
    player_screen_x = player_x - camera_x
    player_screen_y = player_y - camera_y
    pygame.draw.circle(screen, (255, 0, 0), (player_screen_x, player_screen_y), 10)

    pygame.display.flip()
    clock.tick(60)