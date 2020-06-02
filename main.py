import random
import tkinter as tk
import pygame # pylint: disable=unused-import
import const
from tkinter import simpledialog
from tkinter.filedialog import askopenfilename
# from pygame.locals import *

def update(mainscreen, canvas, grid_main, width, height):
    for i in range(0, const.GRID_SIZE * const.GRID_SIZE):
        horizontal_pos = (i % const.GRID_SIZE) * width / const.GRID_SIZE
        vertical_pos = int(int(i / const.GRID_SIZE) * height / const.GRID_SIZE)
        canvas.blit(grid_main[i], (horizontal_pos, vertical_pos))
    mainscreen.blit(canvas, (0, 0))
    pygame.display.flip()

def jumble(grid_main, grid_count, blank_index):
    # jumble the chopped array. 
    for i in range(0, 1):
        swap_from = grid_main[i % grid_count]
        swap_random = 2
        while swap_random == i % grid_count:
            swap_random = random.randrange(0, grid_count)
        if swap_random == blank_index:
            blank_index = i
        elif i == blank_index:
            blank_index = swap_random
        grid_main[i] = grid_main[swap_random]
        grid_main[swap_random] = swap_from
    return blank_index

def swap_tile(blank_pos, tile_pos, grid_main):
    # Function to swap tiles in grid_main.
    blank_grid_pos = (blank_pos[0] * const.GRID_SIZE) + blank_pos[1]
    tile_grid_pos = (tile_pos[0] * const.GRID_SIZE) + tile_pos[1]
    swap_blank = grid_main[blank_grid_pos]
    grid_main[blank_grid_pos] = grid_main[tile_grid_pos]
    grid_main[tile_grid_pos] = swap_blank
    return tile_grid_pos

def is_valid_move(mouse_pos, width, height, blank_index):
    # To check if its a valid move, we need to see if the click happened in one of the neighbours 
    # If the blank_index is at position i, then its neighbours are located as follows
    # top -> i - GRID_SIZE, right -> i + 1, bottom -> i + GRID_SIZE, left -> i - 1
    blank_pos = [blank_index // const.GRID_SIZE, blank_index % const.GRID_SIZE]
    horizontal_pos = vertical_pos = - 1
    mouse_horizontal = mouse_pos[0]
    mouse_vertical = mouse_pos[1]
    while mouse_horizontal > 0:
        mouse_horizontal = mouse_horizontal - (width / const.GRID_SIZE)
        horizontal_pos = horizontal_pos + 1
    while mouse_vertical > 0:
        mouse_vertical = mouse_vertical - (height / const.GRID_SIZE)
        vertical_pos = vertical_pos + 1
    clicked_grid_pos = [vertical_pos, horizontal_pos]
    valid_move_pos = ([blank_pos[0], blank_pos[1] - 1],
                      [blank_pos[0], blank_pos[1] + 1],
                      [blank_pos[0] - 1, blank_pos[1]],
                      [blank_pos[0] + 1, blank_pos[1]])
    # return a set that contains the coordinates to the blank pos and the 
    # clicked position
    if clicked_grid_pos in valid_move_pos:
        return (True, blank_pos, clicked_grid_pos)
    else:
        return (False, blank_pos, clicked_grid_pos)

def fill_blank(grid_main):
    blank_img = pygame.Rect((0, 0), (const.img_width / const.GRID_SIZE, const.img_height / const.GRID_SIZE))
    blank_canvas = pygame.Surface(blank_img.size)
    blank_canvas.fill(const.white)
    blank_index = random.randrange(0, const.GRID_SIZE * const.GRID_SIZE)
    grid_main[blank_index] = blank_canvas
    return blank_index

def gameloop(grid_main, grid_copy, blank_index):
    running = True
    clock = pygame.time.Clock()
    while running:
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                running = False
            if events.type == pygame.MOUSEBUTTONUP:
                move_info = is_valid_move(pygame.mouse.get_pos(), 
                                          const.img_width, 
                                          const.img_height, 
                                          blank_index)
                if move_info[0]:
                    blank_index = swap_tile(move_info[1], move_info[2], grid_main)
                    update(screen, background, grid_main, const.img_width, const.img_height)
                if grid_copy == grid_main:
                    screen.fill(const.black)
            if events.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                # print(pressed)
                if pressed[pygame.K_ESCAPE]:
                    running = False
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

def init_game_vars():
    window = tk.Tk()
    window.withdraw()
    value = simpledialog.askinteger("Grid Size", "Enter Grid Size between 3-8")
    while value > 8 or value < 3:
        value = simpledialog.askinteger("Grid Size", "Enter Grid Size between 3-8")
    window.destroy()
    print(value)
    const.GRID_SIZE = value
    return "pics/jhin.jpg"

def main():
    global screen, background
    pygame.init()
    file_name = init_game_vars()
    # Initialize images
    char_image = pygame.image.load(file_name)
    const.img_height = char_image.get_rect().size[1]
    const.img_width = char_image.get_rect().size[0]

    # resize image by a few pixels, so that pixel division by GRID_SIZE results
    #    in an integer and cannot go out of bounds and 
    if const.img_width % const.GRID_SIZE != 0:
        while const.img_width % const.GRID_SIZE != 0:
            const.img_width = const.img_width - 1
    if const.img_height % const.GRID_SIZE != 0:
        while const.img_height % const.GRID_SIZE != 0:
            const.img_height = const.img_height - 1
    print("new width - " + str(const.img_width) + ", new height - " + str(const.img_height))
    # end resizing

    # set screen display to the adjusted image height
    screen = pygame.display.set_mode((const.img_width, const.img_height))    
    pygame.display.set_caption('Slide Puzzle')

    # Create a model that will store a temporary surface that will be outputted to the screen.
    background = pygame.Surface(screen.get_size())
    char_rect = pygame.Rect((0, 0), (const.img_width, const.img_height))            
    char_image = pygame.transform.scale(char_image, char_rect.size)
    char_image = char_image.convert()

    # Below crops the center of a 3x3 evenly distributed grid of an image.
    grid_main = [None] * (const.GRID_SIZE * const.GRID_SIZE)
    grid_count = 0
    for vert in range(0, const.GRID_SIZE):
        for hor in range(0, const.GRID_SIZE):
            chop_width = hor * const.img_width / const.GRID_SIZE
            chop_height = vert * const.img_height / const.GRID_SIZE
            grid_main[grid_count] = pygame.Surface.subsurface(
                char_image,
                (chop_width,
                 chop_height,
                 const.img_width / const.GRID_SIZE,
                 const.img_height / const.GRID_SIZE))
            grid_count = grid_count + 1
    # end chopping

    # choose one random position of test_chop to be a white rectangle of similar size
    blank_index = fill_blank(grid_main)
    grid_copy = grid_main[:]
    # end removal

    # jumble the chopped array
    blank_index = jumble(grid_main, grid_count, blank_index)
    # end jumble

    update(screen, background, grid_main, const.img_width, const.img_height)

    gameloop(grid_main, grid_copy, blank_index)

if __name__ == "__main__":
    main()
