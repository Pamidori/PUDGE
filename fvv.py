import pygame
import sys
import random
import copy

from pygame.examples.go_over_there import running
from pygame.examples.moveit import WIDTH

WHITE = (216, 255, 254)
BLACK = (0, 0, 0)
GREEN_BLUE = (0, 153, 153)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)
block_size = 50
left_margin = 5 * block_size
upper_margin = 2 * block_size
size = (left_margin + 30 * block_size, upper_margin + 15 * block_size)
LETTERS = "АБВГДЕЖЗИК"
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("МОРСКОЙ БОЙ")
font_size = int(block_size / 1.5)
font = pygame.font.SysFont('notosans', font_size)
game_over_font_size=3*block_size
game_over_font=pygame.font.SysFont('notosans',game_over_font_size)
computer_available_to_fire_set = {(x, y)
for x in range(16, 26) for y in range(1, 11)}
around_last_computer_hit_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
hit_blocks = set()
dotted_set = set()
destroyed_computer_ships = []

class Grid:
    def __init__(self, title, offset):
        self.title = title
        self.offset = offset
        self.__draw_grid()
        self.__add_nums_letters_to_grid()
        self.__sign_grid()

    def __draw_grid(self):

        for i in range(11):
            my_image = pygame.image.load("DOSHECHKA.png").convert_alpha()
            vert = pygame.transform.rotate(my_image, 360)
            scaled_image = pygame.transform.scale(vert, (715, 605))
            scaled_image.set_colorkey((255, 255, 255))
            screen.blit(scaled_image, (-10+3*block_size, 0))
            screen.blit(scaled_image, (-10+18 * block_size, 0))
            for i in range(11):
                pygame.draw.line(screen, BLACK, (left_margin, upper_margin + i * block_size),
                                 (left_margin + 10 * block_size, upper_margin + i * block_size), 1)
                pygame.draw.line(screen, BLACK, (left_margin + i * block_size, upper_margin),
                                 (left_margin + i * block_size, upper_margin + 10 * block_size), 1)
                pygame.draw.line(screen, BLACK, (left_margin + 15 * block_size, upper_margin +
                                                 i * block_size),
                                 (left_margin + 25 * block_size, upper_margin + i * block_size), 1)
                pygame.draw.line(screen, BLACK, (left_margin + (i + 15) * block_size, upper_margin),
                                 (left_margin + (i + 15) * block_size, upper_margin + 10 * block_size), 1)

    def __add_nums_letters_to_grid(self):
        for i in range(10):
            num_ver = font.render(str(i + 1), True, BLACK)
            letters_hor = font.render(LETTERS[i], True, BLACK)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()
            screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2) + self.offset * block_size,
                                  upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
            screen.blit(letters_hor, (left_margin + i * block_size + (block_size // 2 -
                                                                      letters_hor_width // 2) + self.offset * block_size, upper_margin + 10 * block_size))

    def __sign_grid(self):
        player = font.render(self.title, True, BLACK)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + 5 * block_size - sign_width // 2 +
                             self.offset * block_size, upper_margin - block_size // 2 - font_size+15))


class Button:
    def __init__(self, x_offset, button_title, message_to_show):
        self.__title = button_title
        self.__title_width, self.__title_height = font.size(self.__title)
        self.__message = message_to_show
        self.__button_width = self.__title_width + block_size
        self.__button_height = self.__title_height + block_size
        self.__x_start = x_offset
        self.__y_start = upper_margin + 10 * block_size + self.__button_height
        self.rect_for_draw = self.__x_start, self.__y_start, self.__button_width, self.__button_height
        self.rect = pygame.Rect(self.rect_for_draw)
        self.__rect_for_button_title = self.__x_start + self.__button_width / 2 - \
            self.__title_width / 2, self.__y_start + \
            self.__button_height / 2 - self.__title_height / 2
        self.__color = BLACK

    def draw_button(self, color=None):
        if not color:
            color = self.__color
        pygame.draw.rect(screen, color, self.rect_for_draw)
        text_to_blit = font.render(self.__title, True, WHITE)
        screen.blit(text_to_blit, self.__rect_for_button_title)

    def change_color_on_hover(self):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw_button(GREEN_BLUE)

    def print_message_for_button(self):
        message_width, message_height = font.size(self.__message)
        rect_for_message = self.__x_start / 2 - message_width / \
            2, self.__y_start + self.__button_height / 2 - message_height / 2
        text = font.render(self.__message, True, BLACK)
        screen.blit(text, rect_for_message)


class AutoShips:
    def __init__(self, offset):
        self.offset = offset
        self.available_blocks = {(x, y) for x in range(
            1 + self.offset, 11 + self.offset) for y in range(1, 11)}
        self.ships_set = set()
        self.ships = self.__populate_grid()
        self.orientation = None
        self.direction = None

    def __create_start_block(self, available_blocks):
        self.orientation = random.randint(0, 1)
        # -1 is left or down, 1 is right or up
        self.direction = random.choice((-1, 1))
        x, y = random.choice(tuple(available_blocks))
        return x, y, self.orientation, self.direction

    def __create_ship(self, number_of_blocks, available_blocks):
        ship_coordinates = []
        x, y, self.orientation, self.direction = self.__create_start_block(
            available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not self.orientation:
                self.direction, x = self.__get_new_block_for_ship(
                    x, self.direction, self.orientation, ship_coordinates)
            else:
                self.direction, y = self.__get_new_block_for_ship(
                    y, self.direction, self.orientation, ship_coordinates)
        if self.__is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.__create_ship(number_of_blocks, available_blocks)

    def __get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
        self.direction = direction
        self.orientation = orientation
        if (coor <= 1 - self.offset * (self.orientation - 1) and self.direction == -1) or (
                coor >= 10 - self.offset * (self.orientation - 1) and self.direction == 1):
            self.direction *= -1
            return self.direction, ship_coordinates[0][self.orientation] + self.direction
        else:
            return self.direction, ship_coordinates[-1][self.orientation] + self.direction

    def __is_ship_valid(self, new_ship):
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def __add_new_ship_to_set(self, new_ship):
        self.ships_set.update(new_ship)

    def __update_available_blocks_for_creating_ships(self, new_ship):
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if self.offset < (elem[0] + k) < 11 + self.offset and 0 < (elem[1] + m) < 11:
                        self.available_blocks.discard(
                            (elem[0] + k, elem[1] + m))

    def __populate_grid(self):
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5 - number_of_blocks):
                new_ship = self.__create_ship(
                    number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.__add_new_ship_to_set(new_ship)
                self.__update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list

def computer_shoots(set_to_shoot_from):
    pygame.time.delay(500)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block

def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy,
                      opponents_ships_set):
    for elem in opponents_ships_list:
        diagonal_only = True
        if fired_block in elem:
            ind = opponents_ships_list.index(elem)
            if len(elem) == 1:
                diagonal_only = False
            update_dotted_and_hit_sets(
                fired_block, computer_turn, diagonal_only)
            elem.remove(fired_block)
            opponents_ships_set.discard(fired_block)
            if computer_turn:
                last_hits_list.append(fired_block)
                update_around_last_computer_hit(fired_block, True)
            if not elem:
                update_destroyed_ships(
                    ind, computer_turn, opponents_ships_list_original_copy)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    destroyed_computer_ships.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(fired_block)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False

def update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy):
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, False)

def update_around_last_computer_hit(fired_block, computer_hits):
    global around_last_computer_hit_set, computer_available_to_fire_set
    if computer_hits and fired_block in around_last_computer_hit_set:
        around_last_computer_hit_set = computer_hits_twice()
    elif computer_hits and fired_block not in around_last_computer_hit_set:
        computer_first_hit(fired_block)
    elif not computer_hits:
        around_last_computer_hit_set.discard(fired_block)

    around_last_computer_hit_set -= dotted_set_for_computer_not_to_shoot
    around_last_computer_hit_set -= hit_blocks_for_computer_not_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_computer_not_to_shoot


def computer_first_hit(fired_block):
    x_hit, y_hit = fired_block
    if x_hit > 16:
        around_last_computer_hit_set.add((x_hit - 1, y_hit))
    if x_hit < 25:
        around_last_computer_hit_set.add((x_hit + 1, y_hit))
    if y_hit > 1:
        around_last_computer_hit_set.add((x_hit, y_hit - 1))
    if y_hit < 10:
        around_last_computer_hit_set.add((x_hit, y_hit + 1))


def computer_hits_twice():
    last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(last_hits_list) - 1):
        x1 = last_hits_list[i][0]
        x2 = last_hits_list[i + 1][0]
        y1 = last_hits_list[i][1]
        y2 = last_hits_list[i + 1][1]
        if x1 == x2:
            if y1 > 1:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))
        elif y1 == y2:
            if x1 > 16:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 25:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    global dotted_set
    x, y = fired_block
    a = 15 * computer_turn
    b = 11 + 15 * computer_turn
    hit_blocks_for_computer_not_to_shoot.add(fired_block)
    hit_blocks.add(fired_block)
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (not diagonal_only or i != 0 and j != 0) and a < x + i < b and 0 < y + j < 11:
                add_missed_block_to_dotted_set((x + i, y + j))
    dotted_set -= hit_blocks

def add_missed_block_to_dotted_set(fired_block):
    dotted_set.add(fired_block)
    dotted_set_for_computer_not_to_shoot.add(fired_block)

def draw_ships(ships_coordinates_list, name):
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Horizontal and 1block ships
        ship_width = block_size * len(ship)
        ship_height = block_size
        if name=='hum':
            if len(ship) > 1 and ship[0][0] == ship[1][0]:
                ship_width, ship_height = ship_height, ship_width
            x = block_size * (x_start - 1) + left_margin
            y = block_size * (y_start - 1) + upper_margin
            if len(ship) == 1:
                my_image = pygame.image.load("TOMAT.PNG").convert_alpha()
                scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                screen.blit(scaled_image, (x, y))
            if len(ship) == 2:
                if ship[0][0] == ship[1][0]:
                    my_image = pygame.image.load("OGURECHEK.PNG").convert_alpha()
                    vert = pygame.transform.rotate(my_image, 90)
                    scaled_image = pygame.transform.scale(vert, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
                else:
                    my_image = pygame.image.load("OGURECHEK.PNG").convert_alpha()
                    scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
            if len(ship) == 3:
                if ship[0][0] == ship[1][0]:
                    my_image = pygame.image.load("selderey.PNG").convert_alpha()
                    vert = pygame.transform.rotate(my_image, 90)
                    scaled_image = pygame.transform.scale(vert, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
                else:
                    my_image = pygame.image.load("selderey.PNG").convert_alpha()
                    scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
            if len(ship) == 4:
                if ship[0][0] == ship[1][0]:
                    my_image = pygame.image.load("BAKLADGANCHEG.png").convert_alpha()
                    vert = pygame.transform.rotate(my_image, 90)
                    scaled_image = pygame.transform.scale(vert, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
                else:
                    my_image = pygame.image.load("BAKLADGANCHEG.png").convert_alpha()
                    scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
        else:
            if len(ship) > 1 and ship[0][0] == ship[1][0]:
                ship_width, ship_height = ship_height, ship_width
            x = block_size * (x_start - 1) + left_margin
            y = block_size * (y_start - 1) + upper_margin
            if len(ship) == 1:
                my_image = pygame.image.load("YABLOKO.png").convert_alpha()
                scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                screen.blit(scaled_image, (x, y))
            if len(ship) == 2:
                if ship[0][0] == ship[1][0]:
                    my_image = pygame.image.load("GRISHA.png").convert_alpha()
                    scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
                else:
                    my_image = pygame.image.load("GRISHA.png").convert_alpha()
                    vert = pygame.transform.rotate(my_image, 90)
                    scaled_image = pygame.transform.scale(vert, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
            if len(ship) == 3:
                if ship[0][0] == ship[1][0]:
                    my_image = pygame.image.load("BANANA.png").convert_alpha()
                    vert = pygame.transform.rotate(my_image, 90)
                    scaled_image = pygame.transform.scale(vert, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
                else:
                    my_image = pygame.image.load("BANANA.png").convert_alpha()
                    scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
            if len(ship) == 4:
                if ship[0][0] == ship[1][0]:
                    my_image = pygame.image.load("ANANAS.png").convert_alpha()
                    scaled_image = pygame.transform.scale(my_image, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))
                else:
                    my_image = pygame.image.load("ANANAS.png").convert_alpha()
                    vert = pygame.transform.rotate(my_image, 90)
                    scaled_image = pygame.transform.scale(vert, (ship_width, ship_height))
                    scaled_image.set_colorkey((255, 255, 255))
                    screen.blit(scaled_image, (x, y))

def draw_from_dotted_set(dotted_set_to_draw_from):
    for elem in dotted_set_to_draw_from:
        pygame.draw.circle(screen, BLACK, (block_size * (
            elem[0] - 0.5) + left_margin, block_size * (elem[1] - 0.5) + upper_margin), block_size // 6)


def draw_hit_blocks(hit_blocks_to_draw_from):
    for block in hit_blocks_to_draw_from:
        x1 = block_size * (block[0] - 1) + left_margin
        y1 = block_size * (block[1] - 1) + upper_margin
        pygame.draw.line(screen, BLACK, (x1, y1),
                         (x1 + block_size, y1 + block_size), block_size // 6)
        pygame.draw.line(screen, BLACK, (x1, y1 + block_size),
                         (x1 + block_size, y1), block_size // 6)


def show_message_at_rect_center(text, rect, which_font=font, color=RED):
    text_width, text_height = which_font.size(text)
    text_rect = pygame.Rect(rect)
    x_start = text_rect.centerx - text_width / 2
    y_start = text_rect.centery - text_height / 2
    background_rect = pygame.Rect(
        x_start - block_size / 2, y_start, text_width + block_size, text_height)
    text_to_blit = which_font.render(text, True, color)
    screen.fill(WHITE, background_rect)
    screen.blit(text_to_blit, (x_start, y_start))


def ship_is_valid(ship_set, blocks_for_manual_drawing):
    return ship_set.isdisjoint(blocks_for_manual_drawing)


def check_ships_numbers(ship, num_ships_list):
    return (5 - len(ship)) > num_ships_list[len(ship)-1]


def update_used_blocks(ship, used_blocks_set):
    for block in ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                used_blocks_set.add((block[0]+i, block[1]+j))
    return used_blocks_set


def restore_used_blocks(deleted_ship, used_blocks_set):
    for block in deleted_ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                used_blocks_set.discard((block[0]+i, block[1]+j))
    return used_blocks_set


computer = AutoShips(0)
computer_ships_working = copy.deepcopy(computer.ships)

auto_button_place = left_margin + 17 * block_size
manual_button_place = left_margin + 20 * block_size
how_to_create_ships_message = "Как вы хотите создать корабли? Нажмите кнопку"
auto_button = Button(auto_button_place, "АВТО", how_to_create_ships_message)
manual_button = Button(manual_button_place, "ВРУЧНУЮ",
                       how_to_create_ships_message)
undo_message = "Для отмены последнего корабля нажмите кнопку"
undo_button_place = left_margin + 12 * block_size
undo_button = Button(undo_button_place, "ОТМЕНА", undo_message)

class ImageButton:
    def __init__(self,x,y,width,height,text,image_path, hover_image_path=None,sound_path=None):
        self.x=x
        self.y=y
        self.width=width
        self.height=height
        self.text=text
        self.image=pygame.image.load(image_path)
        self.image=pygame.transform.scale(self.image,(width,height))
        self.hover_image=self.image
        if hover_image_path:
            self.hover_image=pygame.image.load(hover_image_path)
            self.hover_image=pygame.transform.scale(self.hover_image,(width,height))
        self.rect=self.image.get_rect(topleft=(x,y))
        self.sound=None
        if sound_path:
            self.sound=pygame.mixer.Sound(sound_path)
        self.is_hovered=False

    def draw(self,screen):
        current_image=self.hover_image if self.is_hovered else self.image
        screen.blit(current_image,self.rect.topleft)

        font=pygame.font.Font(None, 36)
        text_surface=font.render(self.text,True,(255,255,255))
        text_rect=text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface,text_rect)

    def check_hover(self,mouse_pos):
        self.is_hovered=self.rect.collidepoint(mouse_pos)

    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button ==1 and self.is_hovered:
            if self.sound:
                self.sound.play()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT,button=self))

pygame.init()
WIDTH, HEIGHT=1750,850
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Меню')

def new_game():

    def main():
        ships_creation_not_decided = True
        ships_not_created = True
        drawing = False
        game_over = False
        computer_turn = False
        start = (0, 0)
        ship_size = (0, 0)

        rect_for_grids = (0, 0, size[0], upper_margin + 12 * block_size)
        rect_for_messages_and_buttons = (0, upper_margin + 11 * block_size, size[0], 5 * block_size)
        message_rect_for_drawing_ships = (undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2], upper_margin + 11 * block_size, size[0] - (
        undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2]), 4 * block_size)
        message_rect_computer=(left_margin-2*block_size,upper_margin+11*block_size,14*block_size,4*block_size)
        message_rect_human = (left_margin + 15 * block_size, upper_margin + 11 * block_size, 10 * block_size, 4 * block_size)
        human_ships_to_draw = []
        human_ships_set = set()
        used_blocks_for_manual_drawing = set()
        num_ships_list = [0, 0, 0, 0]
        screen.fill(WHITE)
        computer_grid = Grid("КОМПЬЮТЕР", 0)
        human_grid = Grid("ЧЕЛОВЕК", 15)

        while ships_creation_not_decided:
            auto_button.draw_button()
            manual_button.draw_button()
            auto_button.change_color_on_hover()
            manual_button.change_color_on_hover()
            auto_button.print_message_for_button()
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    ships_creation_not_decided = False
                    ships_not_created = False

                elif event.type == pygame.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                    print("Clicked AUTO!", event.pos)
                    human = AutoShips(15)
                    human_ships_to_draw = human.ships
                    human_ships_set = human.ships_set
                    human_ships_working = copy.deepcopy(human.ships)
                    ships_creation_not_decided = False
                    ships_not_created = False
                elif event.type == pygame.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                    ships_creation_not_decided = False

            pygame.display.update()
            screen.fill(WHITE, rect_for_messages_and_buttons)

        while ships_not_created:
            screen.fill(WHITE, rect_for_grids)
            computer_grid = Grid("КОМПЬЮТЕР", 0)
            human_grid = Grid("ЧЕЛОВЕК", 15)

            undo_button.draw_button()
            undo_button.print_message_for_button()
            undo_button.change_color_on_hover()
            mouse = pygame.mouse.get_pos()
            if not human_ships_to_draw:
                undo_button.draw_button(LIGHT_GRAY)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ships_not_created = False
                    game_over = True
                elif undo_button.rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                    if human_ships_to_draw:
                        deleted_ship = human_ships_to_draw.pop()
                        num_ships_list[len(deleted_ship) - 1] -= 1
                        used_blocks_for_manual_drawing = restore_used_blocks(
                            deleted_ship, used_blocks_for_manual_drawing)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    drawing = True
                    x_start, y_start = event.pos
                    start = x_start, y_start
                    ship_size = (0, 0)
                elif drawing and event.type == pygame.MOUSEMOTION:
                    x_end, y_end = event.pos
                    end = x_end, y_end
                    ship_size = x_end - x_start, y_end - y_start
                elif drawing and event.type == pygame.MOUSEBUTTONUP:
                    x_end, y_end = event.pos
                    drawing = False
                    ship_size = (0, 0)
                    start_block = ((x_start - left_margin) // block_size + 1,
                                   (y_start - upper_margin) // block_size + 1)
                    end_block = ((x_end - left_margin) // block_size + 1,
                                 (y_end - upper_margin) // block_size + 1)
                    if start_block > end_block:
                        start_block, end_block = end_block, start_block
                    temp_ship = []
                    if 15 < start_block[0] < 26 and 0 < start_block[1] < 11 and 15 < end_block[0] < 26 and 0 < \
                            end_block[1] < 11:
                        screen.fill(WHITE, message_rect_for_drawing_ships)
                        if start_block[0] == end_block[0] and (end_block[1] - start_block[1]) < 4:
                            for block in range(start_block[1], end_block[1] + 1):
                                temp_ship.append((start_block[0], block))
                        elif start_block[1] == end_block[1] and (end_block[0] - start_block[0]) < 4:
                            for block in range(start_block[0], end_block[0] + 1):
                                temp_ship.append((block, start_block[1]))
                        else:
                            show_message_at_rect_center(
                                "КОРАБЛЬ СЛИШКОМ БОЛЬШОЙ!", message_rect_for_drawing_ships)
                    else:
                        show_message_at_rect_center(
                            "КОРАБЛЬ ЗА ПРЕДЕЛАМИ СЕТКИ!", message_rect_for_drawing_ships)
                    if temp_ship:
                        temp_ship_set = set(temp_ship)
                        if ship_is_valid(temp_ship_set, used_blocks_for_manual_drawing):
                            if check_ships_numbers(temp_ship, num_ships_list):
                                num_ships_list[len(temp_ship) - 1] += 1
                                human_ships_to_draw.append(temp_ship)
                                human_ships_set |= temp_ship_set
                                used_blocks_for_manual_drawing = update_used_blocks(
                                    temp_ship, used_blocks_for_manual_drawing)
                            else:
                                show_message_at_rect_center(
                                    f"УЖЕ ДОСТАТОЧНО {len(temp_ship)}-ПАЛУБНЫХ КОРАБЛЕЙ",
                                    message_rect_for_drawing_ships)
                        else:
                            show_message_at_rect_center(
                                "КОРАБЛИ ПРИКАСАЮТСЯ!", message_rect_for_drawing_ships)
                if len(human_ships_to_draw) == 10:
                    ships_not_created = False
                    human_ships_working = copy.deepcopy(human_ships_to_draw)
                    screen.fill(WHITE, rect_for_messages_and_buttons)
            pygame.draw.rect(screen, BLACK, (start, ship_size), 3)
            draw_ships(human_ships_to_draw, 'hum')
            pygame.display.update()

        while not game_over:
            draw_ships(human_ships_to_draw, 'hum')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if (left_margin < x < left_margin + 10 * block_size) and (
                            upper_margin < y < upper_margin + 10 * block_size):
                        fired_block = ((x - left_margin) // block_size + 1,
                                       (y - upper_margin) // block_size + 1)
                        computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, False,
                                                              computer.ships,
                                                              computer.ships_set)
                        draw_from_dotted_set(dotted_set)
                        draw_hit_blocks(hit_blocks)
                        screen.fill(WHITE,message_rect_computer)
            if computer_turn:
                set_to_shoot_from = computer_available_to_fire_set
                if around_last_computer_hit_set:
                    set_to_shoot_from = around_last_computer_hit_set
                fired_block = computer_shoots(set_to_shoot_from)
                computer_turn = check_hit_or_miss(
                    fired_block, human_ships_working, True, human_ships_to_draw, human_ships_set)

            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)
            draw_ships(destroyed_computer_ships, 'comp')

            if not computer.ships_set:
                show_message_at_rect_center('ВЫ ВЫЙГРАЛИ!',(0,0,size[0],size[1]),game_over_font)
            if not human_ships_set:
                show_message_at_rect_center('ВЫ ПРОИГРАЛИ!',(0,0,size[0],size[1]), game_over_font)
            pygame.display.update()
    main()
    pygame.quit()

def main_menu():
    start_button=ImageButton(493,532,180,180,'', 'start_button.jpg','start_button_pushed.jpg','')
    exit_button=ImageButton(1077, 532, 180, 180, '', 'exit_button.jpg', 'exir_button_pushed.jpg', '')
    running=True
    while running:
        screen.fill((255,255,0))
        main_background=pygame.image.load('background_image.jpg')
        screen.blit(main_background,(0,0))

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
                pygame.quit()
                sys.exit()
            if event.type==pygame.USEREVENT and event.button==exit_button:
                running=False
                pygame.quit()
                sys.exit()
            if event.type==pygame.USEREVENT and event.button==start_button:
                new_game()
            for btn in [start_button,exit_button]:
                btn.handle_event(event)
        for btn in [start_button,exit_button]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(screen)
        pygame.display.flip()

main_menu()