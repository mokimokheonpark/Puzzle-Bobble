import os
import pygame
import random

import bubble
import constants as cons
import shooter



pygame.init()
pygame.display.set_caption("Puzzle Bobble")
screen = pygame.display.set_mode((cons.SCREEN_WIDTH, cons.SCREEN_HEIGHT))

map = []
bubble_group = pygame.sprite.Group()

def setup():
    global map
    map = [
        list("RRYYBBGG"),
        list("RRYYBBG/"),
        list("BBGGRRYY"),
        list("BGGRRYY/"),
        list("........"),
        list("......./"),
        list("........"),
        list("......./"),
        list("........"),
        list("......./"),
        list("........")
    ]

    for row_idx, row in enumerate(map):
        for col_idx, col in enumerate(row):
            if col in [".", "/"]:
                continue
            position = get_bubble_position(row_idx, col_idx)
            image = get_bubble_image(col)
            bubble_group.add(bubble.Bubble(image, col, position, row_idx, col_idx))

wall_height = 0

def get_bubble_position(row_idx, col_idx):
    pos_x = col_idx * cons.CELL_SIZE + (cons.BUBBLE_WIDTH // 2)
    pos_y = row_idx * cons.CELL_SIZE + (cons.BUBBLE_HEIGHT // 2) + wall_height
    if row_idx % 2 == 1:
        pos_x += cons.CELL_SIZE // 2
    return pos_x, pos_y

current_path = os.path.dirname(__file__)
bubble_images = [
    pygame.image.load(os.path.join(current_path, "red.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "yellow.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "blue.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "green.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "purple.png")).convert_alpha(),
    pygame.image.load(os.path.join(current_path, "black.png")).convert_alpha()
]

def get_bubble_image(color):
    if color == "R":
        return bubble_images[0]
    elif color == "Y":
        return bubble_images[1]
    elif color == "B":
        return bubble_images[2]
    elif color == "G":
        return bubble_images[3]
    elif color == "P":
        return bubble_images[4]
    else:
        return bubble_images[-1]



curr_bubble = None
next_bubble = None

def prepare_bubbles():
    global curr_bubble, next_bubble
    if next_bubble:
        curr_bubble = next_bubble
    else:
        curr_bubble = create_bubble()
    
    curr_bubble.set_rect((cons.SCREEN_WIDTH // 2, 624))
    next_bubble = create_bubble()
    next_bubble.set_rect((cons.SCREEN_WIDTH // 4, 688))

def create_bubble():
    color = get_random_bubble_color()
    image = get_bubble_image(color)
    return bubble.Bubble(image, color)

def get_random_bubble_color():
    colors = []
    for row in map:
        for col in row:
            if col not in colors and col not in [".", "/"]:
                colors.append(col)
    return random.choice(colors)



fire = False
curr_fire_count = cons.FIRE_COUNT

def process_collision():
    global curr_bubble, fire, curr_fire_count
    hit_bubble = pygame.sprite.spritecollideany(curr_bubble, bubble_group, pygame.sprite.collide_mask)
    if hit_bubble or curr_bubble.rect.top <= wall_height:
        row_idx, col_idx = get_map_index(*curr_bubble.rect.center)
        place_bubble(curr_bubble, row_idx, col_idx)
        remove_adjacent_bubbles(row_idx, col_idx, curr_bubble.color)
        curr_bubble = None
        fire = False
        curr_fire_count -= 1

def get_map_index(x, y):
    row_idx = (y - wall_height) // cons.CELL_SIZE
    col_idx = x // cons.CELL_SIZE
    if row_idx % 2 == 1:
        col_idx = (x - (cons.CELL_SIZE // 2)) // cons.CELL_SIZE
        if col_idx < 0:
            col_idx = 0
        elif col_idx > cons.MAP_COLUMN_COUNT - 2:
            col_idx = cons.MAP_COLUMN_COUNT - 2
    return row_idx, col_idx

def place_bubble(bubble, row_idx, col_idx):
    map[row_idx][col_idx] = bubble.color
    position = get_bubble_position(row_idx, col_idx)
    bubble.set_rect(position)
    bubble.set_map_index(row_idx, col_idx)
    bubble_group.add(bubble)

visited = []

def remove_adjacent_bubbles(row_idx, col_idx, color):
    visited.clear()
    visit(row_idx, col_idx, color)
    if len(visited) >= 3:
        remove_visited_bubbles()
        remove_hanging_bubbles()

def visit(row_idx, col_idx, color = None):
    if row_idx < 0 or row_idx >= cons.MAP_ROW_COUNT or col_idx < 0 or col_idx >= cons.MAP_COLUMN_COUNT:
        return
    if color and map[row_idx][col_idx] != color:
        return
    if map[row_idx][col_idx] in [".", "/"]:
        return
    if (row_idx, col_idx) in visited:
        return
    visited.append((row_idx, col_idx))

    rows = [0, -1, -1, 0, 1, 1]
    cols = [-1, -1, 0, 1, 0, -1]
    if row_idx % 2 == 1:
        rows = [0, -1, -1, 0, 1, 1]
        cols = [-1, 0, 1, 1, 1, 0]
    
    for i in range(len(rows)):
        visit(row_idx + rows[i], col_idx + cols[i], color)

def remove_visited_bubbles():
    bubbles_to_remove = [b for b in bubble_group if (b.row_idx, b.col_idx) in visited]
    for bubble in bubbles_to_remove:
        map[bubble.row_idx][bubble.col_idx] = "."
        bubble_group.remove(bubble)

def remove_hanging_bubbles():
    visited.clear()
    for col_idx in range(cons.MAP_COLUMN_COUNT):
        if map[0][col_idx] != ".":
            visit(0, col_idx)
    remove_not_visited_bubbles()

def remove_not_visited_bubbles():
    bubbles_to_remove = [b for b in bubble_group if (b.row_idx, b.col_idx) not in visited]
    for bubble in bubbles_to_remove:
        map[bubble.row_idx][bubble.col_idx] = "."
        bubble_group.remove(bubble)



def drop_wall():
    global wall_height, curr_fire_count
    wall_height += cons.CELL_SIZE
    for bubble in bubble_group:
        bubble.drop_downward(cons.CELL_SIZE)
    curr_fire_count = cons.FIRE_COUNT

def get_lowest_bubble_bottom():
    bubble_bottoms = [bubble.rect.bottom for bubble in bubble_group]
    return max(bubble_bottoms)

def change_bubble_image(image):
    for bubble in bubble_group:
        bubble.image = image

def draw_bubbles():
    to_x = None
    if curr_fire_count == 2:
        to_x = random.randint(-1, 1)
    elif curr_fire_count == 1:
        to_x = random.randint(-4, 4)
    
    for bubble in bubble_group:
        bubble.draw(screen, to_x)

game_font = pygame.font.SysFont("arialrounded", 40)

def display_game_over():
    txt_game_over = game_font.render(game_result, True, cons.WHITE)
    rect_game_over = txt_game_over.get_rect(center = (cons.SCREEN_WIDTH // 2, cons.SCREEN_HEIGHT // 2))
    screen.blit(txt_game_over, rect_game_over)



running = True
clock = pygame.time.Clock()

to_angle_left = 0
to_angle_right = 0

pointer_image = pygame.image.load(os.path.join(current_path, "pointer.png"))
pointer = shooter.Shooter(pointer_image, (cons.SCREEN_WIDTH // 2, 624), 90)

game_result = None
is_game_over = False

background = pygame.image.load(os.path.join(current_path, "background.png"))
wall = pygame.image.load(os.path.join(current_path, "wall.png"))

setup()

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                to_angle_left += cons.ANGLE_SPEED
            elif event.key == pygame.K_RIGHT:
                to_angle_right -= cons.ANGLE_SPEED
            elif event.key == pygame.K_SPACE:
                if curr_bubble and not fire:
                    fire = True
                    curr_bubble.set_angle(pointer.angle)
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                to_angle_left = 0
            elif event.key == pygame.K_RIGHT:
                to_angle_right = 0
    
    if not curr_bubble:
        prepare_bubbles()
    
    if fire:
        process_collision()
    
    if curr_fire_count == 0:
        drop_wall()
    
    if not bubble_group:
        game_result = "Mission Complete"
        is_game_over = True
    elif get_lowest_bubble_bottom() > len(map) * cons.CELL_SIZE:
        game_result = "Game Over"
        is_game_over = True
        change_bubble_image(bubble_images[-1])

    screen.blit(background, (0, 0))
    screen.blit(wall, (0, wall_height - cons.SCREEN_HEIGHT))

    draw_bubbles()
    pointer.rotate(to_angle_left + to_angle_right)
    pointer.draw(screen)
    if curr_bubble:
        if fire:
            curr_bubble.move()
        curr_bubble.draw(screen)

    if next_bubble:
        next_bubble.draw(screen)
    
    if is_game_over:
        display_game_over()
        running = False
    
    pygame.display.update()

pygame.time.delay(2000)
pygame.quit()