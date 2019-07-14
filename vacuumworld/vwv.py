


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 20:12:24 2019

@author: ben, Nausheen

from IPython import get_ipython
get_ipython().magic('reset -sf')
"""

import tkinter as tk
import traceback
import os

from collections import OrderedDict as odict
from PIL import Image, ImageTk


#from Slider import Slider
#from vw import Environment
from .slider import Slider
from .vw import Grid
from .vwenvironment import init as init_environment


#might need to change this for the real package...
PATH = os.path.dirname(__file__) + "/../"

WIDTH = 640
HEIGHT = 480
ROOT_FONT = "Verdana 10 bold" #font.Font(family='Helvetica', size=36, weight='bold')
BUTTON_PATH = PATH + "res/button.png"
LOCATION_AGENT_IMAGES_PATH = PATH + "res/locations/agent"
LOCATION_DIRT_IMAGES_PATH = PATH + "res/locations/dirt"
DEFAULT_LOCATION_SIZE = 60
DEFAULT_GRID_SIZE = 480
BACKGROUND_COLOUR_SIDE = 'grey'
BACKGROUND_COLOUR_GRID = 'white'

INITIAL_ENVIRONMENT_DIM = 8
        
def get_location_img_files(path):
    return [file for file in os.listdir(path) if file.endswith(".png")]

class VWButton:
    
    def __init__(self, root, img, fun, text = None):
        self.img = img
        self.fun = fun
        self._button = tk.Button(root,
                                 text = text,
                                 bd=0,
                                 font = ROOT_FONT,
                                 fg='white',
                                 highlightthickness = 0,
                                 bg='white', 
                                 activebackground='white', 
                                 activeforeground='white',
                                 highlightcolor='white',
                                 compound = 'center',
                                 command = fun)
        self._button.config(image=img)
        
    def pack(self, side):
        self._button.pack(side=side)
        
class VWMainMenu(tk.Frame):
    
    def __init__(self, root, _start, _exit):
        super(VWMainMenu,self).__init__(root)
        self.configure(background='white')
        self.canvas = tk.Canvas(self, width=480, 
                                height=480, 
                                bd=0, 
                                highlightthickness=0)
        self.canvas.create_rectangle(0,0,481,481,fill="blue") # placeholder for image
        self.canvas.pack()
        
        self.buttons = {}

        button_image = ImageTk.PhotoImage(Image.open(BUTTON_PATH))
        self.button_frame = tk.Frame(self)
        
        self.buttons['start'] = VWButton(self.button_frame, button_image, _start, 'start')
        self.buttons['exit'] = VWButton(self.button_frame, button_image, _exit, 'exit')
        self.buttons['start'].pack('left')
        self.buttons['exit'].pack('left')
        self.button_frame.pack()

        self.pack()

def _start():
    main_menu.pack_forget()
    main_interface.pack()
    
class CanvasDragManager:
    
    def __init__(self, name, grid, canvas, item, on_start, on_drop):
        self.x = 0
        self.y = 0
        self.canvas = canvas
        
        self._on_start = on_start
        self._on_drop = on_drop
        self.canvas.tag_bind(item, "<ButtonPress-1>", self.on_start)
        self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(item, "<ButtonRelease-1>", self.on_drop)
        #self.canvas.configure(cursor="hand1")  
        self.drag_image = None
        self.drag = None
        self.dragging = False
        self.grid = grid
        self.name = name
        
    def _in_bounds(self, x,y):
        return x < DEFAULT_GRID_SIZE and x > 0 and y < DEFAULT_GRID_SIZE and y > 0
        
    def on_start(self, event):
        if not self.dragging:
            self._on_start(event)
            self.dragging = True
            self.x = event.x
            self.y = event.y
        
    def on_drag(self, event):
        
        inc = DEFAULT_GRID_SIZE / self.grid.dim
        x = int(event.x / inc) * inc + (inc / 2) + 1
        y = int(event.y / inc) * inc + (inc / 2) + 1
        
        if x != self.x or y != self.y:
            if x <= DEFAULT_GRID_SIZE:
                self.canvas.itemconfigure(self.drag, state='normal')
            else:
                self.canvas.itemconfigure(self.drag, state='hidden')
            dx = x - self.x
            dy = y - self.y
            self.canvas.move(self.drag, dx, dy)
            self.x = x
            self.y = y

            
    def on_drop(self, event):
        print('drop')
        if self._in_bounds(event.x, event.y):
            self._on_drop(event, self)
        self.dragging = False
        
    
class VWInterface(tk.Frame):
    
    SIDE_PANEL_WIDTH = 4 * DEFAULT_LOCATION_SIZE
    
    def __init__(self, parent, grid):
        super(VWInterface, self).__init__(parent)
        self.configure(background=BACKGROUND_COLOUR_SIDE)
        self.canvas = tk.Canvas(self, width=DEFAULT_GRID_SIZE+DEFAULT_LOCATION_SIZE*4, 
                                height=DEFAULT_GRID_SIZE, 
                                bd=0, 
                                highlightthickness=0)
        #self.canvas.create_rectangle(0,0,481,481,fill="blue") # placeholder for grid
        #self.drag = self.canvas.create_rectangle(230,230,10,10, fill='yellow')

        self._init_buttons()

        self.canvas.configure(background=BACKGROUND_COLOUR_GRID)
        
        self.grid = grid
        
        self.placed_images = {}
        self.canvas_dirts = {}
        self.canvas_agents = {}
        
        self._init_dragables()
        self._init_options()
        
        self.grid_lines = []
        self._draw_grid(DEFAULT_GRID_SIZE, grid.dim)
        self.canvas.pack()
    
    def pack_buttons(self, b1, b2):
        for button in self.buttons.values():
            button._button.pack_forget()
        self.buttons[b1].pack('left')
        self.buttons[b2].pack('right')
    
    def _init_buttons(self):
        self.buttons = {}
        button_image = tk.PhotoImage(file=BUTTON_PATH)
        self.button_frame = tk.Frame(self)
        self.button_frame.configure(bg='white')
        self.buttons['back'] = VWButton(self.button_frame, button_image, _back, 'back')
        self.buttons['play'] = VWButton(self.button_frame, button_image, _play, 'play')
        
        self.buttons['resume']  = VWButton(self.button_frame, button_image, _resume, 'resume')
        self.buttons['pause'] = VWButton(self.button_frame, button_image, _pause, 'pause')
        self.buttons['stop'] = VWButton(self.button_frame, button_image, _stop, 'stop')

        self.buttons_tag = self.canvas.create_window((DEFAULT_GRID_SIZE + 2 + VWInterface.SIDE_PANEL_WIDTH/2,
                                                      DEFAULT_LOCATION_SIZE/2), 
                                                      width=VWInterface.SIDE_PANEL_WIDTH, 
                                                      height=DEFAULT_LOCATION_SIZE, 
                                                      window=self.button_frame)
                
        self.pack_buttons('back', 'play')
    
    def _init_options(self):
        background = 'red'
        x = DEFAULT_GRID_SIZE + 2
        y = 6 * DEFAULT_LOCATION_SIZE
        w = VWInterface.SIDE_PANEL_WIDTH#DEFAULT_GRID_SIZE - 4 * DEFAULT_LOCATION_SIZE
        h = DEFAULT_GRID_SIZE - 6 * DEFAULT_LOCATION_SIZE
        self.options_frame = tk.Frame(self)
        self.options = self.canvas.create_window((x + w/2,y + h/2), width=w, height=h, window=self.options_frame)
        self.options_frame.configure(bg=background)
       
        self._size_slider_option(self.options_frame, background)
        self._save_option(self.options_frame, background)
        self._load_option(self.options_frame, background)
    
    def _save_option(self, parent, bg):
        f = tk.Frame(parent, bg=bg)
        t = tk.Label(f, text=" save ", bg=bg, font = ROOT_FONT)
        t.pack(side='left')
        f.pack()
    
    def _load_option(self, parent, bg):
        f = tk.Frame(parent, bg=bg)
        t = tk.Label(f, text=" load ", bg=bg, font = ROOT_FONT)
        t.pack(side='left')
        f.pack()
    
    def _size_slider_option(self, parent, bg):
        f = tk.Frame(parent, bg=bg)
        t = tk.Label(f, text=" size ", bg=bg, font = ROOT_FONT)
        t.pack(side='left')
        increments = Grid.GRID_MAX_SIZE - Grid.GRID_MIN_SIZE
        self.grid_scale_slider = Slider(f, self.on_resize, None, increments * 16, 16, 
                                        increments=increments,
                                        start=(DEFAULT_GRID_SIZE/DEFAULT_LOCATION_SIZE) - Grid.GRID_MIN_SIZE)
        self.grid_scale_slider.pack(side='left')
        f.pack()
    
    def _reset_canvas(self):
        for line in self.grid_lines:
            self.canvas.delete(line)
        self.grid_lines.clear()
        for a in self.canvas_agents.values():
            self.canvas.delete(a)
        self.canvas_agents.clear()
        for d in self.canvas_dirts.values():
            self.canvas.delete(d)
        self.canvas_dirts.clear()
        self.placed_images.clear()
        
    def _draw_grid(self, size, env_dim):
        x = 0
        y = 0
        inc = size / env_dim
        for i in range(env_dim + 1):
           self.grid_lines.append(self.canvas.create_line(x,0,x,DEFAULT_GRID_SIZE))
           self.grid_lines.append(self.canvas.create_line(0,y,DEFAULT_GRID_SIZE,y))
           y += inc
           x += inc
           
    def _init_dragables(self):
        #load all images
        files = get_location_img_files(LOCATION_AGENT_IMAGES_PATH)
        names = [file.split('.')[0] for file in files]
        self.dragables = {}
        x = DEFAULT_GRID_SIZE + 2
        #for agents
        for name in names:
            file = os.path.join(LOCATION_AGENT_IMAGES_PATH, name) +  '.png'
            img = self._scale(Image.open(file), DEFAULT_LOCATION_SIZE)
            images = self._construct_images(img, name + '_')
            y = DEFAULT_LOCATION_SIZE
            for img_name, img in images.items():
                tk_img = ImageTk.PhotoImage(img)
                item = self.canvas.create_image(x + img.width/2,y + img.height/2, image=tk_img)
                drag_manager = CanvasDragManager(img_name, self.grid, self.canvas, item, self.drag_on_start, self.drag_on_drop)
                self.dragables[item] = (drag_manager, img, tk_img)
                y += DEFAULT_LOCATION_SIZE
            x += DEFAULT_LOCATION_SIZE
            
        #and for dirt...
        files = get_location_img_files(LOCATION_DIRT_IMAGES_PATH)
        names = [file.split('.')[0] for file in files]
        x = DEFAULT_GRID_SIZE + 2
        for name in names:
            file = os.path.join(LOCATION_DIRT_IMAGES_PATH, name) +  '.png'
            img = self._scale(Image.open(file), DEFAULT_LOCATION_SIZE)
            tk_img = ImageTk.PhotoImage(img)
            item = self.canvas.create_image(x + img.width/2,y + img.height/2, image=tk_img)
            drag_manager = CanvasDragManager(name, self.grid, self.canvas, item, self.drag_on_start, self.drag_on_drop)
            self.dragables[item] = (drag_manager, img, tk_img)
            x += DEFAULT_LOCATION_SIZE
    
    def _construct_images(self, img, name):
        return odict({name + 'north':img, name + 'west':img.copy().rotate(90), name + 'south':img.copy().rotate(180), name + 'east':img.copy().rotate(270)})
    
    def _scale(self, img, lsize):
        scale = lsize / max(img.width, img.height)
        return img.resize((int(img.width  * scale), int(img.height * scale)), Image.BICUBIC)
    
    def on_resize(self, value):
        value =  value + Grid.GRID_MIN_SIZE
        if value != self.grid.dim:
            print('resize', value)
            self.grid.reset(value)
            self._reset_canvas()
            self._draw_grid(DEFAULT_GRID_SIZE, grid.dim)
    
    def drag_on_start(self, event):
        drag_manager, image, _ = self.dragables[event.widget.find_closest(event.x, event.y)[0]]
        size = min(DEFAULT_LOCATION_SIZE, DEFAULT_GRID_SIZE  / self.grid.dim)
        print('size', size)
        drag_manager.drag_image = ImageTk.PhotoImage(self._scale(image, size))
        drag_manager.drag = self.canvas.create_image(event.x, event.y, image=drag_manager.drag_image)
        self.canvas.itemconfigure(drag_manager.drag, state='hidden')
        self.canvas.tag_lower(drag_manager.drag)
        print(drag_manager.drag)
        #keep the currently selected draggable on the top
        for d in self.canvas_dirts.values():
            self.canvas.tag_lower(d)
        for a in self.canvas_agents.values():
            self.canvas.tag_lower(a)

    def drag_on_drop(self, event, drag_manager):

        inc = int(DEFAULT_GRID_SIZE / self.grid.dim)
        x = int(event.x / inc) 
        y = int(event.y / inc)
        print(drag_manager.name, x,y)
        self.placed_images[(x,y)] = drag_manager.drag_image        
        #update the environment state
        colour, obj = drag_manager.name.split('_')
        if obj == 'dirt':
            dirt1 =  grid.dirt(colour)
            grid.replace_dirt((x,y), dirt1)
            if (x,y) in self.canvas_dirts:
                self.canvas.delete(self.canvas_dirts[(x,y)])
            self.canvas_dirts[(x,y)] = drag_manager.drag
            print(dirt1)
        else: #its and agent
            agent1 =  grid.agent(colour, obj)
            grid.replace_agent((x,y), agent1)
            if (x,y) in self.canvas_agents:
                self.canvas.delete(self.canvas_agents[(x,y)])
            self.canvas_agents[(x,y)] = drag_manager.drag
            print(agent1)
       
    def show_hide_side(self, state):
        for item in self.dragables.keys():
            self.canvas.itemconfigure(item, state=state)
        self.canvas.itemconfig(self.options, state=state)

import time
from threading import Thread, Event

def _play():
    print('play')
    play_event.set()
    main_interface.pack_buttons('stop', 'pause')
    main_interface.show_hide_side('hidden')
  
def _stop():
    print('stop')
    global reset
    reset = True
    play_event.clear()
    main_interface.pack_buttons('back', 'play')
    main_interface.show_hide_side('normal')

def _resume():
    print('resume')
    play_event.set()
    main_interface.pack_buttons('stop', 'pause')
    
def _pause():
    print('pause')
    play_event.clear()
    main_interface.pack_buttons('stop', 'resume')
        
def _back():
    print('back')
    play_event.clear()
    main_interface.pack_forget()
    main_menu.pack()

def _error(*_):
    traceback.print_exc()
    _finish()
    
def _finish():
    root.destroy()
    global finish
    finish = True


def run(_minds):  
    #required to avoid problems with running after errors (root must be destoryed!)
    
    
  #  import saveload
    
    try:
        global root
        tk.Tk.report_callback_exception = _error
        
        root = tk.Tk()
        root.title("Vacuum World")
        root.protocol("WM_DELETE_WINDOW", _finish)
        root.configure(background='white')
        
        global main_menu
        global main_interface
        global grid
        global minds
        minds = _minds
        
        grid = Grid(INITIAL_ENVIRONMENT_DIM)

        #saveload.load('/test.vw', grid)
        
        main_menu = VWMainMenu(root, _start, _finish)
        main_interface = VWInterface(root, grid)
        #print(dir(main_menu.canvas))
        
        global env_thread
        global play_event, finish, reset
        reset = True
        finish = False
        play_event = Event()
        
        env_thread = Thread(target=simulate, daemon=True)
        env_thread.start()
        
        root.mainloop()   
    except:
        _error()
        

def simulate():  
    try:
        def wait():
            play_event.wait()
            return play_event.is_set()
        global reset
        
        while wait() and not finish:
            if reset:
                global env
                env = init_environment(grid, minds)
                grid.cycle = 0
                reset = False
                
            print("evolve", grid.cycle)
            env.evolveEnvironment()
            grid.cycle += 1
            time.sleep(1)
    except:
        _error()
