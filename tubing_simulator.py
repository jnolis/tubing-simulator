import random
from array import array
import libtcodpy as libtcod
from itertools import repeat
import math
import time

class River:
    def __init__(self, length, width=80):
        self.terrain = dict()
        self.terrain['grass'] = Terrain('x',libtcod.Color(0, 128, 0))
        self.terrain['sand'] = Terrain('*',libtcod.Color(255, 255, 128))
        self.terrain['river'] = Terrain('~',libtcod.Color(0,0,255))
        self.terrain['rapid'] = Terrain('%',libtcod.Color(255,255,255))
        
        self.length = length
        self.width = width
        self.grid = []
        
        min_river_left = width*1/8
        max_river_left = width*3/8
        min_river_right = width*5/8
        max_river_right = width*7/8
        min_river_depth = 2
        max_river_depth = 10
        
        self.max_river_cross_sectional_area = max_river_depth * (max_river_right-min_river_left)
        
        self.river_left = array('I')
        self.river_right = array('I')
        self.river_depth = array('I')
        self.river_cross_sectional_area = array('I')
        self.sand_left = array('I')
        self.sand_right = array('I')
        
        self.river_left.append(random.randint(min_river_left,max_river_left))
        self.river_right.append(random.randint(min_river_right,max_river_right))
        self.river_depth.append(random.randint(min_river_depth,max_river_depth))
        self.sand_left.append(random.randint(0,self.river_left[0]))
        self.sand_right.append(random.randint(self.river_right[0],width-1))
        self.river_cross_sectional_area.append((self.river_right[0]-self.river_left[0])*self.river_depth[0])
                
        for row in range(1,length):
            river_left_shift = random.randint(-1,1)
            river_right_shift = random.randint(-1,1)
            river_depth_shift = random.randint(-1,1)
            
            sand_left_shift = random.randint(-1,1)
            sand_right_shift = random.randint(-1,1)
            
            new_river_left = min(max(self.river_left[-1]+river_left_shift,min_river_left),max_river_left)
            new_river_right = min(max(self.river_right[-1]+river_right_shift,min_river_right),max_river_right)
            new_river_depth = min(max(self.river_depth[-1]+river_depth_shift,min_river_depth),max_river_depth)
            new_sand_left = min(max(0,self.sand_left[-1]+sand_left_shift),new_river_left)
            new_sand_right = min(max(new_river_right,self.sand_right[-1]+sand_right_shift),width-1)
            
            self.river_left.append(new_river_left)
            self.river_right.append(new_river_right)
            self.river_depth.append(new_river_depth)
            self.sand_left.append(new_sand_left)
            self.sand_right.append(new_sand_right)
            
            self.river_cross_sectional_area.append((new_river_right-new_river_left)*new_river_depth)
        
        # self.rapids = array('I')
        # num_rapids = random.randint(1,self.length/50)
        # for i in range(0,num_rapids):
            # rapid_length = random.randint(1,10)
            # rapid_start = random.randint(0,self.length)
            # self.rapids.extend(range(rapid_start,rapid_start+rapid_length))

        for row in range(0,length):
            new_row = []
            for col in range(0,width):  
                if col < self.sand_left[row]:
                    new_row.append(self.terrain['grass'])
                elif col < self.river_left[row]:
                    new_row.append(self.terrain['sand'])
                elif col < self.river_right[row]:
                    if self.river_cross_sectional_area[row] < 150 and self.river_depth[row] < 4:
                        new_row.append(self.terrain['rapid'])
                    else:
                        new_row.append(self.terrain['river'])
                elif col < self.sand_right[row]:
                    new_row.append(self.terrain['sand'])
                else:
                    new_row.append(self.terrain['grass'])
            self.grid.append(new_row)
        
        print self.river_cross_sectional_area

class Game:
    def __init__(self,screen_width,screen_height,river_length):
        self.upper_buffer = 5
        self.river = River(river_length,screen_width)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_height = screen_height-5
        self.map_width = screen_width
        self.player = Object(self.river, self.upper_buffer, int(self.map_width/2), '@', libtcod.Color(255,255,255), [Traverse(self.river.terrain['rapid'],1), Traverse(self.river.terrain['river'],1),Traverse(self.river.terrain['sand'],0.1)])
        self.camera_row = self.player.row - self.upper_buffer

    def move(self, dr, dc):
        self.player.move(dr,dc)
        self.camera_row = min(max(self.player.row - self.upper_buffer,0),game.river.length-self.map_height)
    
    def draw(self, thing_to_draw, row,col):
        if row >= self.camera_row and row < self.camera_row + self.map_height:
            libtcod.console_set_default_foreground(con, thing_to_draw.color)
            libtcod.console_put_char(con, col, row - self.camera_row, thing_to_draw.char, libtcod.BKGND_NONE)
    
    def current(self, time_change):
        space = self.river.grid[self.player.row][self.player.col]
        if space == self.river.terrain['river']:
            rate = 1
        elif space == self.river.terrain['rapid']:
            rate = 3
        else:
            rate = 0
        
        self.move(time_change*rate*self.river.max_river_cross_sectional_area/self.river.river_cross_sectional_area[self.player.row],0)
    
    def render(self):
        for row in range(self.camera_row,self.camera_row+self.map_height):
            for col in range(self.map_width):
                self.draw(self.river.grid[row][col],row,col)
        
        self.draw(self.player,self.player.row,self.player.col)
        
        #blit the contents of "con" to the root console
        libtcod.console_blit(con, 0, 0, self.screen_width, self.screen_height, 0, 0, 0)
    
    def handle_keys(self):
        key = libtcod.console_check_for_keypress()
     
        if key.vk == libtcod.KEY_ESCAPE:
            return True  #exit game
     
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            self.move(-1,0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            self.move(1,0)
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            self.move(0,-1)
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            self.move(0,1)

class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, river, row, col, char, color, traverse_list):
        self.river = river
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
        
        if self.row+r_dir < self.river.length and self.row+r_dir >= 0 and self.col+c_dir < self.river.width and self.col+c_dir >= 0 and self.river.grid[self.row+r_dir][self.col+c_dir] in terrain:
            speed = self.traverse_list[terrain.index(self.river.grid[self.row][self.col])].speed
            self.row_frac += dr * speed
            self.col_frac += dc * speed
            self.row += int(self.row_frac)
            self.col += int(self.col_frac)
            self.row_frac = self.row_frac - int(self.row_frac)
            self.col_frac = self.col_frac - int(self.col_frac)

class Terrain:
    def __init__(self, char, color):
        self.char = char
        self.color = color

class Traverse:
    def __init__(self, terrain, speed):
        self.terrain = terrain
        self.speed = speed

#############################################
# Initialization & Main Loop
#############################################
game = Game(80,45,100)
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(game.screen_width, game.screen_height, 'TUBING SIMULATOR 2015', False)
libtcod.sys_set_fps(20)
con = libtcod.console_new(game.screen_width, game.screen_height)


current_time = time.time()
while not libtcod.console_is_window_closed():
    new_time = time.time()
    game.current(new_time - current_time)
    current_time = new_time
    #render the screen
    game.render()
 
    libtcod.console_flush()
 
 
    #handle keys and exit game if needed
    exit = game.handle_keys()
    if exit:
        break