import random
from array import array
import libtcodpy as libtcod
from itertools import repeat
import math
import time
import os

class River:
    def __init__(self, length, width=80):
        self.terrain = dict()
        self.terrain['grass'] = Terrain('x',libtcod.Color(0, 128, 0))
        self.terrain['sand'] = Terrain('*',libtcod.Color(255, 255, 128))
        self.terrain['river'] = Terrain('~',libtcod.Color(0,0,255))
        self.terrain['shallow_river'] = Terrain('+',libtcod.Color(0,128,255))
        self.terrain['rapid'] = Terrain('%',libtcod.Color(255,255,255))
        self.terrain['road'] = Terrain('.',libtcod.Color(128,128,128))
        self.terrain['tree'] = Terrain('T',libtcod.Color(128,128,128))
        self.terrain['bush'] = Terrain('B',libtcod.Color(128,128,128))
        
        self.speed = min(max(random.gauss(1000,250),250),1750)
        self.cross_sectional_area = array('f')
        
        self.length = length
        self.width = width
        self.grid = []
        self.depth = []
        
        
        
        ds_n = int(2**math.ceil(math.log(self.width)/math.log(2)))
        ds_n_col = int(ds_n+1)
        ds_n_row = int(math.ceil(self.length/float(ds_n))*ds_n+1)
        

        
        ds_grid = []
        ds_is_set = []
        ds_h = []
        for r in range(ds_n_row):
            temp_grid = []
            temp_is_set = []
            temp_h = []
            for c in range(ds_n_col):
                temp_grid.append(0.0)
                temp_is_set.append(False)
                temp_h.append(0.5+abs(0.5-float(c)/(ds_n_col-1)))
            ds_grid.append(temp_grid)
            ds_is_set.append(temp_is_set)
            ds_h.append(temp_h)
        
        ds_current_n = ds_n/2
        
        for r in range(0,ds_n_row,ds_current_n):
            for c in range(0,ds_n_col,ds_current_n):
                if c == ds_current_n:
                    ds_grid[r][c] = random.randint(-20,-5)
                else:
                    ds_grid[r][c] = random.randint(5,10)
                ds_is_set[r][c] = True
        
        while not all([all(x) for x in ds_is_set]):
            ds_is_set_temp = [list(a) for a in ds_is_set]
            ds_current_n = ds_current_n/2
            for r in range(0,ds_n_row,ds_current_n):
                for c in range(0,ds_n_col,ds_current_n):
                    if not ds_is_set[r][c]:
                        temp_sum = 0
                        temp_count = 0
                        for neighbor_r in [-ds_current_n,0,ds_current_n]:
                            for neighbor_c in [-ds_current_n,0,ds_current_n]:
                                if neighbor_r != neighbor_c and \
                                    neighbor_r + r >= 0 and neighbor_r + r < ds_n_row and \
                                    neighbor_c + c >= 0 and neighbor_c + c < ds_n_col and \
                                    ds_is_set[neighbor_r + r][neighbor_c + c]:
                                    
                                    temp_sum += ds_grid[neighbor_r + r][neighbor_c + c]
                                    temp_count += 1
                        
                        ds_grid[r][c] = temp_sum/temp_count+ ds_h[r][c]*(random.random()-0.5)*ds_current_n
                        ds_is_set_temp[r][c] = True
            
            for r in range(ds_n_row):
                for c in range(ds_n_col):
                   ds_is_set[r][c] = ds_is_set[r][c] or ds_is_set_temp[r][c]
        
        
        interp_idx = [(ds_n_col-1)/float(self.width-1)*x for x in range(self.width)]
        for r in range(self.length):
            temp_depth = []
            for c in range(self.width):
                prev = int(max(math.floor(interp_idx[c]),0))
                next = int(min(math.ceil(interp_idx[c]),ds_n_col-1))
                frac = interp_idx[c] % 1
                temp_depth.append(ds_grid[r][prev]*(1-frac) + ds_grid[r][next]*frac)
            self.depth.append(temp_depth)
        
        is_river = []
        for r in range(self.length):
            temp_is_river = []
            for c in range(self.width):
                temp_is_river.append(False)
            is_river.append(temp_is_river)
        
        is_river_needs_update = []
        for c in range(self.width):
            if self.depth[0][c] < 0:
                is_river_needs_update.append([0,c])
        
        while len(is_river_needs_update) > 0:
            x = is_river_needs_update.pop()
            r = x[0]
            c = x[1]
            if r-1 >= 0          and not is_river[r-1][c] and self.depth[r-1][c] < 0:
                is_river[r-1][c] = True
                is_river_needs_update.append([r-1,c])
            if r+1 < self.length and not is_river[r+1][c] and self.depth[r+1][c] < 0:
                is_river[r+1][c] = True
                is_river_needs_update.append([r+1,c])
            if c-1 >= 0          and not is_river[r][c-1] and self.depth[r][c-1] < 0:
                is_river[r][c-1] = True
                is_river_needs_update.append([r,c-1])
            if c+1 < self.width  and not is_river[r][c+1] and self.depth[r][c+1] < 0:
                is_river[r][c+1] = True
                is_river_needs_update.append([r,c+1])
        
        for r in range(self.length):
            self.cross_sectional_area.append(-sum([self.depth[r][c]*is_river[r][c]*5 for c in range(self.width)]))
        for r in range(self.length):
            temp_grid = []
            for c in range(self.width):
                temp_depth = self.depth[r][c]
                if not is_river[r][c]:
                    if temp_depth > 5:
                        terrain = self.terrain['grass']
                    else:
                        terrain = self.terrain['sand']
                else:
                    if temp_depth > -8 and float(self.speed)/self.cross_sectional_area[r] > 1:
                        terrain = self.terrain['rapid']
                    elif temp_depth > -2:
                        terrain = self.terrain['shallow_river']
                    else:
                        terrain = self.terrain['river']
                temp_grid.append(terrain)
            self.grid.append(temp_grid)


class Game:
    def __init__(self,screen_width,screen_height,river_length):
        self.upper_buffer = 5
        self.river = River(river_length,screen_width)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.message_width = screen_width
        self.message_height = 2
        self.stats_width = screen_width
        self.stats_height = 3
        self.map_height = screen_height-self.message_height-self.stats_height
        self.map_width = screen_width
        # self.player = Player(self, self.upper_buffer, int(self.map_width/2), '@', libtcod.Color(255,255,255), \
            # [Traverse(self.river.terrain['rapid'],0.05), \
            # Traverse(self.river.terrain['river'],0.05),  \
            # Traverse(self.river.terrain['sand'],0.15),   \
            # Traverse(self.river.terrain['road'],1), \
            # Traverse(self.river.terrain['shallow_river'],0.10)])
        self.player = Player(self, self.upper_buffer, int(self.map_width/2), '@', libtcod.Color(255,255,255), \
            [Traverse(self.river.terrain['rapid'],1), \
            Traverse(self.river.terrain['river'],1),  \
            Traverse(self.river.terrain['sand'],1),   \
            Traverse(self.river.terrain['road'],1), \
            Traverse(self.river.terrain['shallow_river'],1)])
        self.camera_row = self.player.row - self.upper_buffer
        self.time = 0
        self.map_con = libtcod.console_new(self.map_width, self.map_height)
        self.message_con = libtcod.console_new(self.message_width, self.message_height)
        self.stats_con  = libtcod.console_new(self.stats_width, self.stats_height)
        self.message_log = []
        self.last_move_time = -10
        self.max_move_frequency = 3

    
    def draw(self, thing_to_draw, row,col):
        if row >= self.camera_row and row < self.camera_row + self.map_height:
            libtcod.console_set_default_foreground(self.map_con, thing_to_draw.color)
            libtcod.console_put_char(self.map_con, col, row - self.camera_row, thing_to_draw.char, libtcod.BKGND_NONE)
    
    def current(self, time_change):
        space = self.river.grid[self.player.row][self.player.col]
        if space == self.river.terrain['river']:
            rate = 1
        elif space == self.river.terrain['rapid']:
            rate = 1
        else:
            rate = 0
        
        self.player.move(time_change*rate*self.river.speed/self.river.cross_sectional_area[self.player.row]/5,0)
        
    def render(self):
        for row in range(self.camera_row,self.camera_row+self.map_height):
            for col in range(self.map_width):
                self.draw(self.river.grid[row][col],row,col)
        
        self.draw(self.player,self.player.row,self.player.col)
        
        libtcod.console_clear(self.message_con)
        if len(self.message_log) > 0 and self.time - self.message_log[-1].timestamp < 5:
            libtcod.console_print_ex(self.message_con, 0,0, libtcod.BKGND_NONE, libtcod.LEFT,self.message_log[-1].text)
        
        
        #blit the contents of "con" to the root console
        libtcod.console_blit(self.message_con, 0, 0, 0, 0, 0, 0, 0)
        libtcod.console_blit(self.map_con, 0, 0, 0, 0, 0, 0,self.message_height)
        libtcod.console_blit(self.stats_con, 0, 0, 0, 0, 0, 0, self.message_height + self.map_height)
    
    def handle_keys(self,state_list):
        key = libtcod.console_check_for_keypress()
        if key.vk == libtcod.KEY_ESCAPE:
            return state_list['exit']

     
        if key.vk == libtcod.KEY_UP:
            self.player.move(-1,0)
        elif key.vk == libtcod.KEY_DOWN:
            self.player.move(1,0)
        elif key.vk == libtcod.KEY_LEFT:
            self.player.move(0,-1)
        elif key.vk == libtcod.KEY_RIGHT:
            self.player.move(0,1)
        return(state_list['game'])

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, game, row, col, char, color, traverse_list):
        self.game = game
        self.row = row
        self.col = col
        self.char = char
        self.color = color
        self.traverse_list = traverse_list
        self.row_frac = 0
        self.col_frac = 0
 
    def move(self, dr, dc):
        terrain = [x.terrain for x in self.traverse_list]
        if dr > 0:
            r_dir = 1
        elif dr < 0:
            r_dir = -1
        else:
            r_dir = 0
        
        if dc > 0:
            c_dir = 1
        elif dc < 0:
            c_dir = -1
        else:
            c_dir = 0
        
        if self.row+r_dir < self.game.river.length and self.row+r_dir >= 0 and self.col+c_dir < self.game.river.width and self.col+c_dir >= 0 and self.game.river.grid[self.row+r_dir][self.col+c_dir] in terrain:
            speed = self.traverse_list[terrain.index(self.game.river.grid[self.row][self.col])].speed
            self.row_frac += dr * speed
            self.col_frac += dc * speed
            if abs(self.row_frac) >= 1:
                self.row += r_dir
                self.row_frac = 0
            
            if abs(self.col_frac) >= 1:
                self.col += c_dir
                self.col_frac = 0

class Player(Object):
    def move(self,dr,dc):
        current_terrain = self.game.river.grid[self.row][self.col]
        Object.move(self,dr,dc)
        new_terrain = self.game.river.grid[self.row][self.col]
        if (current_terrain == self.game.river.terrain['river'] or \
            current_terrain == self.game.river.terrain['rapid']) and new_terrain == self.game.river.terrain['sand']:
            self.game.message_log.append(Message("You walk onto the beach.",self.game.time))
        elif current_terrain == self.game.river.terrain['sand'] and new_terrain == self.game.river.terrain['river']:
            self.game.message_log.append(Message("You get back into the river.",self.game.time))
        elif current_terrain == self.game.river.terrain['sand'] and new_terrain == self.game.river.terrain['rapid']:
            self.game.message_log.append(Message("You get back into the river at a rapid point.",self.game.time))
        
        self.game.camera_row = self.row - self.game.upper_buffer

class Terrain:
    def __init__(self, char, color):
        self.char = char
        self.color = color

class Traverse:
    def __init__(self, terrain, speed):
        self.terrain = terrain
        self.speed = speed

class Message:
    def __init__(self,text,timestamp):
        self.text = text
        self.timestamp = timestamp
        
class Intro:
    def __init__(self,screen_width,screen_height,game):
        logo_file = open(os.path.join(b'data',b'logo.txt'))
        self.logo = logo_file.readlines()
        logo_file.close()
        self.logo_height = len(self.logo)
        self.logo_width = max([len(x) for x in self.logo])
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.intro_con = libtcod.console_new(self.screen_width, self.screen_height)
        self.speed = game.river.speed
        if self.speed < 500:
            self.river_string = 'VERY SLOW'
        if self.speed < 750:
            self.river_string = 'SLOW'
        elif self.speed < 1250:
            self.river_string = 'DECENT'
        elif self.speed < 1500:
            self.river_string = 'FAST'
        else:
            self.river_string = 'VERY FAST'
        self.option_rows = ['Start at the beginning of the river.','Start at the midpoint of the river.','Cancel the tubing adventure (quit).']
        self.selected_row = 0
    
    def render(self):

        libtcod.console_set_default_foreground(self.intro_con, libtcod.Color(0,255,255))
        libtcod.console_set_default_background(self.intro_con, libtcod.Color(0,0,0))
        for i in range(self.logo_height):
            libtcod.console_print_ex(self.intro_con, max((self.screen_width-self.logo_width)/2,0),i, libtcod.BKGND_NONE, libtcod.LEFT,self.logo[i])
        
        libtcod.console_set_default_foreground(self.intro_con, libtcod.Color(255,255,255))        
        
        libtcod.console_print_ex(self.intro_con, 5,self.logo_height + 1, libtcod.BKGND_NONE, libtcod.LEFT,'Today the river speed is: ' + self.river_string + '.')
        
        for i in range(len(self.option_rows)):

            if i == self.selected_row:
                libtcod.console_set_default_background(self.intro_con, libtcod.Color(128,128,0))
            else:
                libtcod.console_set_default_background(self.intro_con, libtcod.Color(0,0,0))
            
            libtcod.console_print_ex(self.intro_con, 5,self.logo_height + 3 + i, libtcod.BKGND_SET, libtcod.LEFT,self.option_rows[i])
        
        libtcod.console_blit(self.intro_con, 0, 0, 0, 0, 0, 0, 0)
    
    def handle_keys(self,state_list):
        key = libtcod.console_wait_for_keypress(True)
        if key.vk == libtcod.KEY_ENTER:
            if self.selected_row == 0:
                return state_list['game']
            elif self.selected_row == 1:
                return state_list['game']
            elif self.selected_row == 2:
                return state_list['exit']
        elif libtcod.console_is_key_pressed(libtcod.KEY_UP):
            self.selected_row = max(self.selected_row - 1,0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            self.selected_row = min(self.selected_row + 1,len(self.option_rows)-1)
        return state


#############################################
# Initialization & Main Loop
#############################################

full_width = 80
full_height = 45


libtcod.console_set_custom_font(os.path.join(b'data',b'terminal8x12_gs_ro.png'), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
libtcod.console_init_root(full_width, full_height, 'TUBING SIMULATOR', False)
libtcod.console_disable_keyboard_repeat()
libtcod.sys_set_fps(30)
game = Game(full_width,full_height,600)
intro = Intro(full_width,full_height,game)

state_list = dict(game=game,intro=intro,exit='exit')


state = intro
current_time = time.time()

while not libtcod.console_is_window_closed() and state != state_list['exit']:
    if state == intro:
        intro.render()
        libtcod.console_flush()
        state = intro.handle_keys(state_list)

    elif state == game:
        new_time = time.time()
        game.time += new_time - current_time
        game.current((new_time - current_time)/10)
        current_time = new_time
        #render the screen
        game.render()
     
        libtcod.console_flush()
     
        #handle keys and exit game if needed
        state = game.handle_keys(state_list)
    
    