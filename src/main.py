import pygame
import moviepy.editor
import random
import time
from os import path

WIN_HEIGHT = 800
WIN_WIDTH = 800
INFO_SIZE = 80
TILES_SIZE = 80

WOOD = 0
ROCK = 0
GROWTHSPEED = 10
timer_lst = {}
SESSION_CUTTREE = 0
base_tree_time = time.perf_counter()

FLAG_MENU = False
FLAG_SEED = False
FLAG_LOGGER = False
FLAG_SAW = False
FLAG_LOAD = False
myfont = None

tree_mat = [[0 for i in range(0, int(WIN_WIDTH / TILES_SIZE))] for j in range(0, int(WIN_WIDTH / TILES_SIZE))]
bot_mat = [[0 for i in range(0, int(WIN_WIDTH / TILES_SIZE))] for j in range(0, int(WIN_WIDTH / TILES_SIZE))]
GLOBAL_TIMER = time.perf_counter()

# TO DO :
# - retenir moment de quit pour quand reload les arbres et bots ont avancés
# - REFACTOR class MVC + réduire les double boucle au max
# - Sounds / music Nota
# - Game menu (save/sound/quit/réseau sociaux/heure de jeu) -> Save dans file préférence
# - Stopper compteur quand on est dans menu
# - Détruire case (clean : bot+item) coute du bois click droit
# - Affichage Nombre > 9999
# - Modifier video intro
# - Faire un installer (https://cyrille.rossant.net/create-a-standalone-windows-installer-for-your-python-application/)
# - Shop icon
# - Changer les prix en fonction du nobre de buche par sec
# - Next page menu en haut à droite fleche > et juste à sa gauche <
# - Systeme de succès (nb de click manuelle)
# - check si il y a de la place sur la mat pour la nouvelle seed/bot


def main():
    global myfont, bot_mat, tree_mat, FLAG_LOAD
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT + INFO_SIZE))
    pygame.display.set_caption("Forest Station")
    ico = pygame.image.load("../data/sprites/tree2.png")
    pygame.display.set_icon(ico)

    pygame.init()

    #  Intro video
    clip = moviepy.editor.VideoFileClip('../data/video/intro.mpg')
    clip = clip.resize((800, 880))
    clip.preview()

    myfont = pygame.font.Font("../data/font/po1.TTF", 25)

    tree_mat = generate_forst(tree_mat)

    if(path.exists("../data/save.txt")):
        FLAG_LOAD = True
        tree_map, bot_mat = load()

    grid(win)
    draw_menu(win)
    pygame.display.update()

    draw_forest(win, tree_mat)
    FLAG_LOAD = False

    mainloop(win, tree_mat)

    save(tree_mat, bot_mat)

    pygame.quit()


def mainloop(win, tree_mat):
    global FLAG_MENU, FLAG_SEED, FLAG_LOGGER, FLAG_SAW, ROCK, WOOD, GROWTHSPEED, TREESEC
    run = True

    old_x = 0
    old_y = 0
    x_focus = 0
    y_focus = 0
    old_x_focus = 0
    old_y_focus = 0

    while(run):
        mouse_pos = pygame.mouse.get_pos()
        event = pygame.event.poll()

        x = mouse_pos[0] // TILES_SIZE
        y = mouse_pos[1] // TILES_SIZE

        if event.type == pygame.MOUSEBUTTONDOWN:
            if(event.button == 1):  # Left click
                checkinput(win, x, y, tree_mat)

        if event.type == pygame.QUIT:
            run = False

        if(not FLAG_MENU):
            tree_mat = check_timer(win, tree_mat)
            tree_mat = check_bot(win, tree_mat)
            draw_menu(win)

        old_x, old_y,  old_x_focus, old_y_focus = focus_mouse(win, x, y, old_x, old_y, x_focus, y_focus, old_x_focus, old_y_focus, tree_mat)

        pygame.display.update()
        pygame.display.flip()


def checkinput(win, x, y, tree_mat):
    global FLAG_MENU, FLAG_SEED, FLAG_LOGGER, FLAG_SAW, ROCK, WOOD, GROWTHSPEED
    if(FLAG_SEED):
        if(x >= 0 and x < WIN_WIDTH/TILES_SIZE):
            if(y >= 0 and y < WIN_HEIGHT/TILES_SIZE):
                if(tree_mat[x][y] not in [1, 10, 2, 20, 11, 12, 13]):
                    tree_mat[x][y] = 10
                    draw_case(win, tree_mat, x, y)
                    FLAG_SEED = False
    elif(FLAG_SAW):
        if(x >= 0 and x < WIN_WIDTH/TILES_SIZE):
            if(y >= 0 and y < WIN_HEIGHT/TILES_SIZE):
                if(tree_mat[x][y] in [1, 10, 11, 12, 13]):
                    if(bot_mat[x][y] not in [1, 2]):
                        bot_mat[x][y] = 2
                        draw_case(win, tree_mat, x, y)
                        FLAG_SAW = False

    elif(FLAG_LOGGER):
        if(x >= 0 and x < WIN_WIDTH/TILES_SIZE):
            if(y >= 0 and y < WIN_HEIGHT/TILES_SIZE):
                if(tree_mat[x][y] in [1, 10, 11, 12, 13]):
                    if(bot_mat[x][y] not in [1, 2]):
                        bot_mat[x][y] = 1
                        draw_case(win, tree_mat, x, y)
                        FLAG_LOGGER = False

    elif(not FLAG_MENU):
        if(x >= 0 and x < WIN_WIDTH/TILES_SIZE):
            if(y >= 0 and y < WIN_HEIGHT/TILES_SIZE):
                tree_mat = cut_tree(tree_mat, win, x, y)
        if(x == (WIN_WIDTH/TILES_SIZE) - 1):  # Open Menu
            if(y == (WIN_HEIGHT/TILES_SIZE)):
                FLAG_MENU = True
                show_menu(win)
    else:  # In Menu
        if(x == (WIN_WIDTH/TILES_SIZE) - 1):
            if(y == (WIN_HEIGHT/TILES_SIZE)):
                close_menu(win, tree_mat)
        if(1 <= y <= 3):
            if(5 <= x <= 7):  # Item 1
                if(WOOD - 50 >= 0):
                    WOOD -= 50
                    tree_mat = generate_forst(tree_mat)
                    close_menu(win, tree_mat)
            elif(7 < x <= 9):  # Item 2
                if(WOOD - 75 >= 0):
                    WOOD -= 75
                    ROCK += 25
                    draw_menu(win)
            else:
                close_menu(win, tree_mat)
        elif(4 <= y <= 6):
            if(5 <= x <= 7):  # Item 3
                if(WOOD - 100 >= 0):
                    WOOD -= 100
                    draw_menu(win)
                    FLAG_LOGGER = True
                    close_menu(win, tree_mat)
            elif(7 < x <= 9):  # Item 4
                if(ROCK - 50 >= 0):
                    ROCK -= 50
                    draw_menu(win)
                    FLAG_SEED = True
                    close_menu(win, tree_mat)
            else:
                close_menu(win, tree_mat)
        elif(7 <= y <= 9):
            if(5 <= x <= 7):  # Item 5
                if(WOOD - 200 >= 0):
                    WOOD -= 200
                    draw_menu(win)
                    FLAG_SAW = True
                    close_menu(win, tree_mat)
            elif(7 < x <= 9):  # Item 6
                if(ROCK - 100 >= 0 and (GROWTHSPEED - GROWTHSPEED*0.5 > 0)):
                    ROCK -= 100
                    GROWTHSPEED -= GROWTHSPEED*0.05
                    draw_menu(win)
            else:
                close_menu(win, tree_mat)
        else:
            close_menu(win, tree_mat)


def close_menu(win, tree_mat):
    global FLAG_MENU
    FLAG_MENU = False
    grid(win)
    draw_forest(win, tree_mat)


def check_bot(win, tree_mat):
    global ROCK
    current = time.perf_counter()
    diff = int(current - GLOBAL_TIMER)
    for i in range(0, len(tree_mat[0])):
        for j in range(0, len(tree_mat[1])):
            if(tree_mat[i][j] == 1):
                if(bot_mat[i][j] == 1):
                    if(diff % 2 == 0):
                        tree_mat = cut_tree(tree_mat, win, i, j)
                        draw_case(win, tree_mat, i, j)
                elif(bot_mat[i][j] == 2):
                    if(diff % 1 == 0):
                        tree_mat = cut_tree(tree_mat, win, i, j)
                        draw_case(win, tree_mat, i, j)
                        ROCK += 1
    return tree_mat


def cut_tree(tree_mat, win, x, y):
    global WOOD, ROCK, TREESEC, SESSION_CUTTREE
    if(tree_mat[x][y] == 1):
        tree_mat[x][y] = 10  # buche
        WOOD += 1
        SESSION_CUTTREE += 1
        grd_tiles = pygame.image.load("../data/sprites/grass.png")
        grd_tiles = pygame.transform.scale(grd_tiles, (TILES_SIZE, TILES_SIZE))
        win.blit(grd_tiles, [x * TILES_SIZE, y*TILES_SIZE])
        tree = pygame.image.load("../data/sprites/log.png")
        tree = pygame.transform.scale(tree, (TILES_SIZE, TILES_SIZE))
        win.blit(tree, [x * TILES_SIZE, y*TILES_SIZE])
        timer_lst[(x, y)] = time.perf_counter() + random.randint(0, 5)
    if(tree_mat[x][y] == 2):
        tree_mat[x][y] = 20  # cailloux
        ROCK += 1
        grd_tiles = pygame.image.load("../data/sprites/grass.png")
        grd_tiles = pygame.transform.scale(grd_tiles, (TILES_SIZE, TILES_SIZE))
        win.blit(grd_tiles, [x * TILES_SIZE, y*TILES_SIZE])
        tree = pygame.image.load("../data/sprites/rock_after.png")
        tree = pygame.transform.scale(tree, (TILES_SIZE, TILES_SIZE))
        win.blit(tree, [x * TILES_SIZE, y*TILES_SIZE])
    return tree_mat


def check_timer(win, tree_mat):
    global GROWTHSPEED
    if(len(timer_lst) != 0):
        for i in range(0, len(tree_mat[0])):
            for j in range(0, len(tree_mat[1])):
                if((i, j) in timer_lst):
                    current = time.perf_counter()
                    if((GROWTHSPEED/4)+1 > (current - timer_lst[(i, j)]) > GROWTHSPEED/4):
                        tree_mat[i][j] = 13
                        draw_case(win, tree_mat, i, j)
                    if((2*GROWTHSPEED/4)+1 > (current - timer_lst[(i, j)]) > 2*GROWTHSPEED/4):
                        tree_mat[i][j] = 12
                        draw_case(win, tree_mat, i, j)
                    if((3*GROWTHSPEED/4)+1 >(current - timer_lst[(i, j)]) > 3*GROWTHSPEED/4):
                        tree_mat[i][j] = 11
                        draw_case(win, tree_mat, i, j)
                    if(current - timer_lst[(i, j)] > GROWTHSPEED):
                        tree_mat[i][j] = 1
                        draw_case(win, tree_mat, i, j)
                        del timer_lst[(i, j)]
    return tree_mat


def generate_forst(tree_mat):
    for i in range(0, len(tree_mat[0])):
        for j in range(0, len(tree_mat[1])):
            tree_mat[i][j] = random.randint(0, 10)
    return tree_mat


def draw_case(win, tree_mat, i, j):
    # Si on a un 3 on met rien
    grd_tiles = pygame.image.load("../data/sprites/grass.png")
    grd_tiles = pygame.transform.scale(grd_tiles, (TILES_SIZE, TILES_SIZE))
    win.blit(grd_tiles, [i * TILES_SIZE, j*TILES_SIZE])
    if(tree_mat[i][j] == 1):
        spri = pygame.image.load("../data/sprites/tree2.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
    elif(tree_mat[i][j] == 10):
        spri = pygame.image.load("../data/sprites/log.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
        timer_lst[(i, j)] = time.perf_counter() + random.randint(0, 5)
    elif(tree_mat[i][j] == 11):
        spri = pygame.image.load("../data/sprites/tree_lil.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
    elif(tree_mat[i][j] == 12):
        spri = pygame.image.load("../data/sprites/tree_lil_lil.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
    elif(tree_mat[i][j] == 13):
        spri = pygame.image.load("../data/sprites/tree_lil_lil_lil.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
    elif(tree_mat[i][j] == 2):
        spri = pygame.image.load("../data/sprites/rock1.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
    elif(tree_mat[i][j] == 20):
        spri = pygame.image.load("../data/sprites/rock_after.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])

    if(bot_mat[i][j] == 1):
        spri = pygame.image.load("../data/sprites/bot_logger.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
    elif(bot_mat[i][j] == 2):
        spri = pygame.image.load("../data/sprites/bot_saw.png")
        spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
        win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])


def draw_forest(win, tree_mat):
    global FLAG_LOAD
    for i in range(0, len(tree_mat[0])):
        for j in range(0, len(tree_mat[1])):
            # Si on a un 3 on met rien
            if(tree_mat[i][j] == 1):
                spri = pygame.image.load("../data/sprites/tree2.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
            elif(tree_mat[i][j] == 10):
                spri = pygame.image.load("../data/sprites/log.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
                timer_lst[(i, j)] = time.perf_counter() + random.randint(0, 5)
            elif(tree_mat[i][j] == 11):
                spri = pygame.image.load("../data/sprites/tree_lil.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
                if(FLAG_LOAD):
                    timer_lst[(i, j)] = time.perf_counter() + random.randint(0, 2)
            elif(tree_mat[i][j] == 12):
                spri = pygame.image.load("../data/sprites/tree_lil_lil.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
                if(FLAG_LOAD):
                    timer_lst[(i, j)] = time.perf_counter() + random.randint(0, 2)
            elif(tree_mat[i][j] == 13):
                spri = pygame.image.load("../data/sprites/tree_lil_lil_lil.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
                if(FLAG_LOAD):
                    timer_lst[(i, j)] = time.perf_counter() + random.randint(0, 2)
            elif(tree_mat[i][j] == 2):
                spri = pygame.image.load("../data/sprites/rock1.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
            elif(tree_mat[i][j] == 20):
                spri = pygame.image.load("../data/sprites/rock_after.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])

            if(bot_mat[i][j] == 1):
                spri = pygame.image.load("../data/sprites/bot_logger.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])
            elif(bot_mat[i][j] == 2):
                spri = pygame.image.load("../data/sprites/bot_saw.png")
                spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
                win.blit(spri, [i * TILES_SIZE, j*TILES_SIZE])


def grid(win):
    grd_tiles = pygame.image.load("../data/sprites/grass.png")
    grd_tiles = pygame.transform.scale(grd_tiles, (TILES_SIZE, TILES_SIZE))
    for i in range(0, int(WIN_WIDTH/TILES_SIZE)):
        for j in range(0, int(WIN_HEIGHT/TILES_SIZE)):
            win.blit(grd_tiles, [i*TILES_SIZE, j*TILES_SIZE])


def focus_mouse(win, x, y, old_x, old_y, x_focus, y_focus, old_x_focus, old_y_focus, tree_mat):
    global FLAG_SEED, FLAG_MENU, FLAG_LOGGER, FLAG_SAW
    nope = pygame.image.load("../data/sprites/nope.png")
    nope = pygame.transform.scale(nope, (TILES_SIZE, TILES_SIZE))
    focus = pygame.image.load("../data/sprites/focus.png")
    focus = pygame.transform.scale(focus, (TILES_SIZE, TILES_SIZE))
    unfocus = pygame.image.load("../data/sprites/unfocus.png")
    unfocus = pygame.transform.scale(unfocus, (TILES_SIZE, TILES_SIZE))
    focus_menu = pygame.image.load("../data/sprites/focus_menu.png")
    unfocus_menu = pygame.image.load("../data/sprites/unfocus_menu.png")

    if(not FLAG_MENU):  # Focus ingame
        if(x == old_x and y == old_y):
            foc = focus
            if((old_x, old_y) != (9, 10)):
                if(old_y < 10):
                    if(bot_mat[x][y] in [1, 2, 11, 12, 13]):
                        draw_case(win, tree_mat, old_x, old_y)

            if(FLAG_SEED):
                if((old_x, old_y) != (9, 10)):
                    if(old_y < 10):
                        if(tree_mat[x][y] in [1, 2, 10, 20, 11, 12, 13]):
                            foc = nope
                        textsurface = myfont.render("Seed", False, (255, 255, 255))
                        win.blit(textsurface, [x * TILES_SIZE + 20, y*TILES_SIZE + 20])
            elif(FLAG_SAW):
                if((old_x, old_y) != (9, 10)):
                    if(old_y < 10):
                        if(tree_mat[x][y] not in [1, 10, 11, 12, 13]):
                            foc = nope
                        if(bot_mat[x][y] in [1, 2]):
                            foc = nope
                        textsurface = myfont.render("Sawmill", False, (255, 255, 255))
                        win.blit(textsurface, [x * TILES_SIZE + 10, y*TILES_SIZE + 20])
            elif(FLAG_LOGGER):
                if((old_x, old_y) != (9, 10)):
                    if(old_y < 10):
                        if(tree_mat[x][y] not in [1, 10, 11, 12, 13]):
                            foc = nope
                        if(bot_mat[x][y] in [1, 2]):
                            foc = nope
                        textsurface = myfont.render("Logger", False, (255, 255, 255))
                        win.blit(textsurface, [x * TILES_SIZE + 15, y*TILES_SIZE + 20])

            if((old_x, old_y) != (9, 10)):
                if(old_y < 10):
                    win.blit(foc, [x * TILES_SIZE, y*TILES_SIZE])
            else:
                win.blit(foc, [x * TILES_SIZE, y*TILES_SIZE])

        else:  # clean old case
            if((old_x, old_y) != (9, 10)):
                if(old_y < 10):
                    if(bot_mat[old_x][old_y] in [1, 2, 11, 12, 13]):
                        draw_case(win, tree_mat, old_x, old_y)
                    else:
                        win.blit(unfocus, [old_x * TILES_SIZE, old_y*TILES_SIZE])

            if(FLAG_SEED or FLAG_SAW or FLAG_LOGGER):
                if((old_x, old_y) != (9, 10)):
                    if(old_y < 10):
                        draw_case(win, tree_mat, old_x, old_y)
        old_x = x
        old_y = y
    else:  # Focus sur menu
        BUTTON_SIZE = 160
        if(1 <= y <= 3):
            if(5 <= x <= 7):  # Item 1
                x_focus = WIN_WIDTH - BUTTON_SIZE - 80 - 130
                y_focus = 120
                win.blit(focus_menu, [x_focus, y_focus])
            if(7 < x <= 9):  # Item 1
                x_focus = WIN_WIDTH - BUTTON_SIZE - 30
                y_focus = 120
                win.blit(focus_menu, [x_focus, y_focus])
        if(4 <= y <= 6):
            if(5 <= x <= 7):  # Item 1
                x_focus = WIN_WIDTH - BUTTON_SIZE - 80 - 130
                y_focus = 200 + BUTTON_SIZE
                win.blit(focus_menu, [x_focus, y_focus])
            if(7 < x <= 9):  # Item 1
                x_focus = WIN_WIDTH - BUTTON_SIZE - 30
                y_focus = 200 + BUTTON_SIZE
                win.blit(focus_menu, [x_focus, y_focus])
        if(7 <= y <= 9):
            if(5 <= x <= 7):  # Item 1
                x_focus = WIN_WIDTH - BUTTON_SIZE - 80 - 130
                y_focus = 280 + BUTTON_SIZE*2
                win.blit(focus_menu, [x_focus, y_focus])
            if(7 < x <= 9):  # Item 1
                x_focus = WIN_WIDTH - BUTTON_SIZE - 30
                y_focus = 280 + BUTTON_SIZE*2
                win.blit(focus_menu, [x_focus, y_focus])
        if(old_x_focus != 0):
            if(x_focus != old_x_focus or y_focus != old_y_focus):
                win.blit(unfocus_menu, [old_x_focus, old_y_focus])
        old_x_focus = x_focus
        old_y_focus = y_focus
    return old_x, old_y, old_x_focus, old_y_focus


def show_menu(win):
    MENU_SIZE = 400
    BUTTON_SIZE = 160
    #  Big Surface
    s = pygame.Surface((MENU_SIZE, WIN_HEIGHT), pygame.SRCALPHA)
    s.fill((25, 25, 25, 200))
    win.blit(s, (WIN_WIDTH - MENU_SIZE, 0))
    #  Title
    s = pygame.Surface((MENU_SIZE, 80), pygame.SRCALPHA)
    s.fill((50, 50, 50, 255))
    win.blit(s, (WIN_WIDTH - MENU_SIZE, 0))
    fontTitle = pygame.font.Font("../data/font/po1.TTF", 50)
    textsurface = fontTitle.render("THE SHOP", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - MENU_SIZE + 20, 5))

    #  Item 1
    spri = pygame.image.load("../data/sprites/button.png")
    spri = pygame.transform.scale(spri, (BUTTON_SIZE, BUTTON_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 80 - 130, 120))
    # Text item 1
    textsurface = myfont.render("New forest", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE - 80 - 130 + 40, 120 + 40 + 10))
    # Prix Item 1
    spri = pygame.image.load("../data/sprites/item_log.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 150, 120 + 90))
    textsurface = myfont.render("50", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE - 160, 120 + 20 + 90))

    #  Item 2
    spri = pygame.image.load("../data/sprites/button.png")
    spri = pygame.transform.scale(spri, (BUTTON_SIZE, BUTTON_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 30, 120))
    # Text item 2
    textsurface = myfont.render("+25", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE + 20, 120 + 40 + 10))
    spri = pygame.image.load("../data/sprites/item_rock.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE + 30, 120 + 30))
    # Prix Item 2
    spri = pygame.image.load("../data/sprites/item_log.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE + 30, 120 + 90))
    textsurface = myfont.render("75", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE + 20, 120 + 20 + 90))

    #  Item 3
    spri = pygame.image.load("../data/sprites/button.png")
    spri = pygame.transform.scale(spri, (BUTTON_SIZE, BUTTON_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 80 - 130, 200 + BUTTON_SIZE))
    pygame.display.update()
    # Text item 3
    textsurface = myfont.render("Logger bot", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE - 80 - 130 + 40, 200 + BUTTON_SIZE + 40 + 10))
    # Prix Item 3
    spri = pygame.image.load("../data/sprites/item_log.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 150, 200 + BUTTON_SIZE + 90))
    textsurface = myfont.render("100", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE - 160, 200 + BUTTON_SIZE + 20 + 90))

    #  Item 4
    spri = pygame.image.load("../data/sprites/button.png")
    spri = pygame.transform.scale(spri, (BUTTON_SIZE, BUTTON_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 30, 200 + BUTTON_SIZE))
    # Text item 4
    textsurface = myfont.render("Tree seed", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE - 30 + 40, 200 + BUTTON_SIZE + 40 + 10))
    # Prix Item 4
    spri = pygame.image.load("../data/sprites/item_rock.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE + 30, 200 + BUTTON_SIZE + 90))
    textsurface = myfont.render("50", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE + 20, 200 + BUTTON_SIZE + 20 + 90))

    #  Item 5
    spri = pygame.image.load("../data/sprites/button.png")
    spri = pygame.transform.scale(spri, (BUTTON_SIZE, BUTTON_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 80 - 130, 280 + BUTTON_SIZE*2))
    pygame.display.update()
    # Text item 5
    textsurface = myfont.render("Sawmill bot", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE - 80 - 130 + 35, 280 + BUTTON_SIZE*2 + 40 + 10))
    # Prix Item 5
    spri = pygame.image.load("../data/sprites/item_log.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 150, 280 + BUTTON_SIZE*2 + 90))
    textsurface = myfont.render("200", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE - 160, 280 + BUTTON_SIZE*2 + 20 + 90))

    #  Item 6
    spri = pygame.image.load("../data/sprites/button.png")
    spri = pygame.transform.scale(spri, (BUTTON_SIZE, BUTTON_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE - 30, 280 + BUTTON_SIZE*2 ))
    # Text item 5
    textsurface = myfont.render("+5%", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE + 30, 280 + BUTTON_SIZE*2 + 35))
    textsurface = myfont.render("Growth speed", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE, 280 + BUTTON_SIZE*2 + 40 + 20))
    # Prix Item 6
    spri = pygame.image.load("../data/sprites/item_rock.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - BUTTON_SIZE + 30, 280 + BUTTON_SIZE*2 + 90))
    textsurface = myfont.render("100", False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH - BUTTON_SIZE + 20, 280 + BUTTON_SIZE*2 + 20 + 90))

    pygame.display.update()


def draw_menu(win):
    global myfont, SESSION_CUTTREE, base_tree_time
    men = pygame.image.load("../data/sprites/grey_tile.png")
    men = pygame.transform.scale(men, (WIN_WIDTH, INFO_SIZE))
    win.blit(men, [0, WIN_HEIGHT])
    pygame.font.init()

    # Wood
    spri = pygame.image.load("../data/sprites/item_log.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (0, WIN_HEIGHT + INFO_SIZE - 80))
    textsurface = myfont.render(str(WOOD), False, (255, 255, 255))
    win.blit(textsurface, (70, WIN_HEIGHT + INFO_SIZE - 60))

    # Rock
    spri = pygame.image.load("../data/sprites/item_rock.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (100, WIN_HEIGHT + INFO_SIZE - 80))
    textsurface = myfont.render(str(ROCK), False, (255, 255, 255))
    win.blit(textsurface, (170, WIN_HEIGHT + INFO_SIZE - 60))

    # Tree by sec
    current = time.perf_counter()
    treesec = str(round(SESSION_CUTTREE/(current - base_tree_time), 2)) + " Tree/sec"
    textsurface = myfont.render(treesec, False, (255, 255, 255))
    win.blit(textsurface, (WIN_WIDTH//2, WIN_HEIGHT + INFO_SIZE - 60))

    # Menu button
    spri = pygame.image.load("../data/sprites/menu.png")
    spri = pygame.transform.scale(spri, (TILES_SIZE, TILES_SIZE))
    win.blit(spri, (WIN_WIDTH - 80, WIN_HEIGHT + INFO_SIZE - 80))


def save(tree_mat, bot_mat):
    f = open("../data/save.txt", "w")
    f.write(str(WOOD) + "\n")
    f.write(str(ROCK) + "\n")
    f.write(str(GROWTHSPEED))
    for i in range(0, len(tree_mat[0])):
        f.write("\n")
        for j in range(0, len(tree_mat[1])):
            f.write(str(tree_mat[i][j]) + " ")
    for i in range(0, len(tree_mat[0])):
        f.write("\n")
        for j in range(0, len(tree_mat[1])):
            f.write(str(bot_mat[i][j]) + " ")
    f.close()


def load():
    global WOOD, ROCK, GROWTHSPEED, bot_mat
    f = open("../data/save.txt", "r")
    WOOD = int(f.readline())
    ROCK = int(f.readline())
    GROWTHSPEED = float(f.readline())
    for i in range(0, len(tree_mat[0])):
        line = (f.readline()).split(" ")
        for j in range(0, len(tree_mat[1])):
            tree_mat[i][j] = int(line[j])
    for i in range(0, len(bot_mat[0])):
        line = (f.readline()).split(" ")
        for j in range(0, len(bot_mat[1])):
            bot_mat[i][j] = int(line[j])
    return tree_mat, bot_mat


if __name__ == '__main__':
    main()
