import sys
import pygame
import random

pygame.init()

speed = 10
rectangle_dimension = 100
border_size = 10
board_size = 4
size = board_size * rectangle_dimension + (board_size + 1) * border_size
left_top_edge = border_size
right_bottom_edge = 3 * rectangle_dimension + 4 * border_size
block_difference = border_size + rectangle_dimension

game_screen = pygame.display.set_mode((size, size))

pygame.display.set_caption('2048')

clock = pygame.time.Clock()


# create the actual game board w/ grid coordinates
def get_sq_coords():
    # square_coords are the coordinates of each block
    square_coords = []

    for y_coords in range(board_size):
        row_coords = []
        for x_coords in range(board_size):
            row_coords.append((border_size + x_coords * (border_size + rectangle_dimension),
                               border_size + y_coords * (border_size + rectangle_dimension)))
        square_coords.append(row_coords)

    return square_coords


# get block colors for given number
def block_colors():

    # first value is block color, second is text color
    dark_text = (114, 104, 95)
    white = (255, 255, 255)

    color_list = {2: [(236, 226, 216), dark_text], 4: [(237, 222, 201), dark_text],
                  8: [(241, 175, 115), white], 16: [(241, 150, 105), white],
                  32: [(247, 122, 94), white], 64: [(230, 90, 55), white],
                  128: [(230, 90, 55), white], 256: [(246, 215, 109), white],
                  512: [(228, 192, 42), white], 1024: [(239, 196, 65), white],
                  2048: [(236, 196, 0), white]}

    return color_list


# display text over block
def text_objects(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def draw_grid(square_coords, width=rectangle_dimension, height=rectangle_dimension):
    grid_color = (202, 192, 180)
    border_color = (187, 170, 160)
    pygame.draw.rect(game_screen, border_color, (0, 0, size, size))
    for rows in square_coords:
        for cols in rows:
            pygame.draw.rect(game_screen, grid_color, (cols[0], cols[1], width, height))


# draw individual blocks
def draw_blocks(number, x, y, width=rectangle_dimension, height=rectangle_dimension):
    colors = block_colors()
    pygame.draw.rect(game_screen, colors[number][0], (x, y, width, height))

    small_text = pygame.font.Font("freesansbold.ttf", 40)
    text_surf, text_rect = text_objects(str(number), small_text, colors[number][1])
    text_rect.center = ((x + (width / 2)), (y + (height / 2)))
    game_screen.blit(text_surf, text_rect)


def check_blocks_moving(block_stats):
    for block in block_stats:
        if block[3] != 0 or block[4] != 0:
            return True


def block_direction(event, block_stats):
    """
    # gets blocks in line with speed_x, speed_y
    """
    if check_blocks_moving(block_stats):
        pass
    else:
        for block in block_stats:
            if event.key == pygame.K_LEFT:
                block[3] = -speed
            elif event.key == pygame.K_RIGHT:
                block[3] = speed
            elif event.key == pygame.K_UP:
                block[4] = -speed
            elif event.key == pygame.K_DOWN:
                block[4] = speed


# changes either x or y coordinate with every tick
def modify_block_stats(block_stats, coordinates_combined):

    for block in block_stats:
        edge_detection(block)

        # gets blocks in line with speed_x, speed_y
        aligned_blocks = show_aligned_blocks(block_stats, block[1], block[2], block[3], block[4])

        # if not at edge, move block by speed
        if block[3] != 0:
            block[1] += block[3]  # speed_x
        elif block[4] != 0:
            block[2] += block[4]  # speed_y

        # sees if block collides with closest_block
        block_collision = collide_block(aligned_blocks, block[1], block[2], block[3], block[4])

        handle_collisions(block_stats, block, block_collision, coordinates_combined)

    return block_stats


# finds out if block is going to collide in the direction of movement,
# return block stats if that is the case, else returns None
def collide_block(aligned_blocks, block_x, block_y, speed_x, speed_y):
    collide_block_stats = []
    if speed_x > 0:
        collide_coord = block_x + block_difference
        for block in aligned_blocks:
            if block_x < block[1] <= collide_coord:
                collide_block_stats = block
    elif speed_x < 0:
        collide_coord = block_x - block_difference
        for block in aligned_blocks:
            if block_x > block[1] > collide_coord:
                collide_block_stats = block
    elif speed_y > 0:
        collide_coord = block_y + block_difference
        for block in aligned_blocks:
            if block_y < block[2] <= collide_coord:
                collide_block_stats = block
    elif speed_y < 0:
        collide_coord = block_y - block_difference
        for block in aligned_blocks:
            if block_y > block[2] > collide_coord:
                collide_block_stats = block
    else:
        return None

    return collide_block_stats


# Check ahead of time if closest block's number matches, if not, flag is False
def handle_collisions(block_stats, block, block_collision, coordinates_combined):
    if block_collision:
        print("COLLIDE")
        # check if values are the same
        if same_block_number(block, block_collision) and block_collision not in coordinates_combined:
            # if so, run combine function
            combine_blocks(block_stats, block, block_collision, coordinates_combined)
        # else, stop block and correct position
        else:
            stop_block(block, block_collision)


def closest_block_changed(block_stats, coordinates_combined):
    if not check_blocks_moving(block_stats):
        coordinates_combined = []


# Edge detection
def edge_detection(block):
    if block[3] < 0:
        if block[1] - speed <= left_top_edge:
            block[1] = left_top_edge
            block[3] = 0
            pass
    elif block[3] > 0:
        if block[1] + speed >= right_bottom_edge:
            block[1] = right_bottom_edge
            block[3] = 0
            pass
    elif block[4] < 0:
        if block[2] - speed <= left_top_edge:
            block[2] = left_top_edge
            block[4] = 0
            pass
    elif block[4] > 0:
        if block[2] + speed >= right_bottom_edge:
            block[2] = right_bottom_edge
            block[4] = 0
            pass


# finds blocks in line with direction of movement to given block
def show_aligned_blocks(block_stats, block_x, block_y, speed_x, speed_y):
    aligned_blocks = []
    up_down = False
    left_right = False

    if speed_x != 0:
        left_right = True
    elif speed_y != 0:
        up_down = True

    if left_right:
        for blocks in block_stats:
            if blocks[2] == block_y:
                aligned_blocks.append(blocks)
    elif up_down:
        for blocks in block_stats:
            if blocks[1] == block_x:
                aligned_blocks.append(blocks)
    return aligned_blocks


# Stops block when collided with other stationary block
def stop_block(block, block_collision):
    if block[3] > 0 and block_collision[3] == 0:
        block[3] = 0
        block[1] = block_collision[1] - block_difference
    elif block[3] < 0 and block_collision[3] == 0:
        block[3] = 0
        block[1] = block_collision[1] + block_difference
    elif block[4] > 0 and block_collision[4] == 0:
        block[4] = 0
        block[2] = block_collision[2] - block_difference
    elif block[4] < 0 and block_collision[4] == 0:
        block[4] = 0
        block[2] = block_collision[2] + block_difference


def same_block_number(block, block_collision):
    if block[0] == block_collision[0]:
        return True
    else:
        return False


def combine_blocks(block_stats, block, block_collision, coordinates_combined):
    if block[3] > 0:
        if abs(block[1] - block_collision[1]) <= speed:
            block[0] *= 2
            block[1] = block_collision[1]
            block[3] = 0
            block_stats.remove(block_collision)
            coordinates_combined.append(block)
        else:
            pass
    elif block[3] < 0:
        if abs(block[1] - block_collision[1]) <= speed:
            block[0] *= 2
            block[1] = block_collision[1]
            block[3] = 0
            block_stats.remove(block_collision)
            coordinates_combined.append(block)
        else:
            pass
    elif block[4] > 0:
        if abs(block[2] - block_collision[2]) <= speed:
            block[0] *= 2
            block[2] = block_collision[2]
            block[4] = 0
            block_stats.remove(block_collision)
            coordinates_combined.append(block)
        else:
            pass
    elif block[4] < 0:
        if abs(block[2] - block_collision[2]) <= speed:
            block[0] *= 2
            block[2] = block_collision[2]
            block[4] = 0
            block_stats.remove(block_collision)
            coordinates_combined.append(block)
        else:
            pass


def generate_block(square_coords, block_stats):
    block_coords = []
    for block in block_stats:
        block_coords.append((block[1], block[2]))

    random_pos = random.sample(square_coords[random.randint(0, board_size - 1)], 1)
    while random_pos[0] in block_coords:
        random_pos = random.sample(square_coords[random.randint(0, board_size - 1)], 1)

    random_number = random.randrange(2, 5, 2)

    block_stats.append([random_number, random_pos[0][0], random_pos[0][1], 0, 0])


def moves_possible(block_stats):
    for block in block_stats:
        for n in [-1, 1]:
            aligned_blocks = show_aligned_blocks(block_stats, block[1], block[2], n, 0)
            # sees if block collides with closest_block
            block_collision = collide_block(aligned_blocks, block[1], block[2], n, 0)

            if block_collision and same_block_number(block, block_collision):
                return True

        for n in [-1, 1]:
            aligned_blocks = show_aligned_blocks(block_stats, block[1], block[2], 0, n)
            # sees if block collides with closest_block
            block_collision = collide_block(aligned_blocks, block[1], block[2], 0, n)

            if block_collision and same_block_number(block, block_collision):
                return True

    return False


def check_game_over(block_stats):
    if len(block_stats) == 16 and not moves_possible(block_stats):
        return True
    else:
        return False


def check_game_won(block_stats):
    for block in block_stats:
        if block[0] == 2048:
            return True
        else:
            return False


def game_end(block_stats):
    if check_game_over(block_stats):
        text = "GAME OVER"
    elif check_game_won(block_stats):
        text = "YOU WIN!"

    large_text = pygame.font.SysFont("freesansbold.ttf", 100)
    text_surf, text_rect = text_objects(text, large_text, (0, 0, 0))
    text_rect.center = ((size / 2), (size / 2.3))
    game_screen.blit(text_surf, text_rect)

    small_text = pygame.font.SysFont("freesansbold.ttf", 40)
    text_surf, text_rect = text_objects("Press any key to play again", small_text, (0, 0, 0))
    text_rect.center = ((size / 2), (size / 1.6))
    game_screen.blit(text_surf, text_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                main()

        pygame.display.update()
        clock.tick(15)


def quit_game():
    pygame.quit()
    sys.exit()


def main():
    square_coords = get_sq_coords()
    # block stats takes format [number, x, y, x_dir, y_dir] w/ len = total num blocks
    # block_stats = [[2, 120, 120, 0, 0], [4, 340, 120, 0, 0]]
    block_stats = [[2, 10, 10, 0, 0], [4, 120, 10, 0, 0], [8, 230, 10, 0, 0], [16, 340, 10, 0, 0]]
    # block_stats = [[2, 10, 10, 0, 0], [4, 230, 10, 0, 0], [4, 340, 10, 0, 0]]
    previous_block_stats = [] # compares previous block stats with current block stats
    coordinates_combined = [] # adds coordinates of "combined" blocks
    key_pressed = False  # flag to indicate key is pressed

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT or
                        event.key == pygame.K_UP or event.key == pygame.K_DOWN):
                    block_direction(event, block_stats)
                    key_pressed = True # flag to indicate key is pressed
                    previous_block_stats = [x[:3] for x in block_stats]
        block_stats = modify_block_stats(block_stats, coordinates_combined)
        if key_pressed:
            block_x_y = [x[:3] for x in block_stats]
            if not check_blocks_moving(block_stats) and block_x_y != previous_block_stats:
                generate_block(square_coords, block_stats)
                key_pressed = False
                coordinates_combined = []
        draw_grid(square_coords, width=rectangle_dimension, height=rectangle_dimension)
        # for loop to draw squares
        for block in block_stats:
            draw_blocks(block[0], block[1], block[2])
        pygame.display.update()
        if check_game_won(block_stats) or check_game_over(block_stats):
            game_end(block_stats)

        clock.tick(120)


main()