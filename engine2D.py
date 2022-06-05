from os import environ
from urllib.parse import scheme_chars
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame

from enum import IntEnum

import win32api
import win32con
import win32gui

pygame_window = 0
pygame_windowWidth = 0
pygame_windowHeight = 0

default_render_target = 0
screen_surface = 0

pygame_clock = 0
screen_width = 0
screen_height = 0
pygame_window_caption = "engine2D application"

input_array = [False] * 16

# Array of active objects
object_array = []
# Array containing object ids that have to be destroyed
destruction_queue = []
# Total number of objects being created. Used for assigning IDs.
object_counter = 0

# Screen viewports
default_viewport = None
current_viewport = None

class Button(IntEnum):
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3
    SPACE = 4
    PG_UP = 5
    PG_DOWN = 6
    ESC = 7
    RETURN = 8
    SHIFT = 9
    CTRL = 10
    MOUSE1 = 11
    MOUSE2 = 12

class RenderTarget:

    def __init__(self, w, h):
        self.render_surface = pygame.surface.Surface([w, h])
        self.w = w
        self.h = h

    def DrawTarget(self, x, y):
        screen_surface.blit(self.render_surface, [x, y, self.w, self.h])

class Viewport:
    def __init__(self, x, y, w, h):
        self.x = x 
        self.y = y 
        self.w = w
        self.h = h
    
    def ToScreen(self, x, y):
        return (x - self.x, y - self.y)

    def FromScreen(self, x, y):
        return (x + self.x, y + self.y)
    
    def IsInView(self, x, y):
        vp_x, vp_y = self.ToScreen(x, y)
        if(vp_x < 0 or vp_y < 0): return False
        if(vp_x >= self.w and vp_y >= self.h): return False
        return True

class TileSet:
    def __init__(self, filename, tilesize_w, tilesize_h, columns):
        self.image = Image(filename)
        self.tilesize_w = tilesize_w
        self.tilesize_h = tilesize_h
        self.columns = columns

        # Find total tiles here 
        self.total_tiles = int((self.image.h / self.tilesize_h) * self.columns)

        self.tiles = [0] * (self.total_tiles + 1)

        for i in range(1, self.total_tiles+1):
            self.tiles[i] = self._GetTileSurface(i)
        
    def _GetTileSurface(self, index):
        tilestartx = (int((index - 1) % self.columns)) * self.tilesize_w
        tilestarty = (int((index - 1) / self.columns)) * self.tilesize_h
        new_surface = self.image.image_data.subsurface((tilestartx, tilestarty, self.tilesize_w, self.tilesize_h))
        return Image("", self.tilesize_w, self.tilesize_h, new_surface)

    def DrawTile(self, index, x, y, w=0, h=0, angle=0, horiz_flip=False, vert_flip=False):
        if(index < len(self.tiles)):
            DrawImage(self.tiles[index], x, y, w, h, angle, horiz_flip, vert_flip)

class Font:
    def __init__(self):
        self.ch_w = 0
        self.ch_h = 0
        pass
    
    def PutChar(self, c, x, y):
        pass

    def PutString(self, s, x, y):
        pass

class TrueTypeFont(Font):
    def __init__(self, filename, font_size, font_width, antialias=True):
        self.ch_h = font_size
        self.ch_w = font_width
        self.antialias = antialias
        self.ttf_font = pygame.font.Font(filename, font_size)
    
    def PutString(self, s, x, y):
        screen_surface.blit(self.ttf_font.render(s, self.antialias, (255, 255, 255)), (x,y))
    
    def PutChar(self, c, x, y):
        self.PutString(c, x, y)

class BitmapFont(Font):
    def __init__(self, filename, ch_w, ch_h, colorkey_r=0, colorkey_g=0, colorkey_b=0, ch_offset=0, font_scale=1): 
        self.image = Image(filename)
        self.image = MakeTransparentImage(self.image, colorkey_r, colorkey_g, colorkey_b)
        self.image = ResizeImage(self.image, font_scale * self.image.w, font_scale * self.image.h)
        self.ch_w = ch_w * font_scale
        self.ch_h = ch_h * font_scale
        self.ch_offset = ch_offset
        self.columns = int((self.image.w / self.ch_w))

        self.total_chars = int((self.image.h / self.ch_h) * self.columns)
        self.characters = [0] * (self.total_chars)

        for i in range(0, self.total_chars):
            new_surface = self.image.image_data.subsurface((int(i % self.columns) * self.ch_w, int(i / self.columns) * self.ch_h, self.ch_w, self.ch_h))
            self.characters[i] = Image("", self.ch_w, self.ch_h, new_surface)
    
    def PutChar(self, c, x, y):
        if(ord(c) - self.ch_offset < len(self.characters) and (ord(c) - self.ch_offset) >= 0):
            DrawImage(self.characters[ord(c) - self.ch_offset], x, y)
        else:
            DrawBlock(x, y, self.ch_w, self.ch_h, 255, 0, 0, True)
    
    def PutString(self, s, x, y):
        for i in range(0, len(s)):
            self.PutChar(s[i], x+i*(self.ch_w), y)

class Object:
    def __init__(self):
        # Physics variables -- unused mostly
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0

        # Object attributes
        self.id = 0
        self.hidden = False
        self.disabled = False
    
    def __del__(self):
        pass

    def Disable(self):
        self.disabled = True
    
    def Enable(self):
        self.disabled = False
    
    def Hide(self):
        self.hidden = True
    
    def DisableAllExceptMe(self):
        for i in range(len(object_array)):
            object_array[i].Disable()
        
        self.Enable()

    def Show(self):
        self.hidden = False
    
    def Delete(self):
        DeleteObject(self.id)

    def Create(self):
        pass

    def Update(self, elapsed):
        pass

    def Draw(self, elapsed):
        pass
    
    def OnTextInput(self, elapsed, c):
        pass

    def OnKeyPress(self, elapsed, key):
        pass

    def OnKeyPressed(self, elapsed, key):
        pass

    def OnKeyRelease(self, elapsed, key):
        pass
    
    def OnMouseMove(self, elapsed, x, y):
        pass

    def OnDestroy(self):
        pass

class Image:
    image_data = 0
    w = 0 
    h = 0

    def __init__(self, file, w=0, h=0, image_data=0):
        if(not image_data):
            self.image_data = pygame.image.load(file).convert_alpha()
            self.w = self.image_data.get_width()
            self.h = self.image_data.get_height()
        else:
            self.w = w
            self.h = h
            self.image_data = image_data
        
        if(w != 0 and h != 0):
            self.image_data = pygame.transform.scale(self.image_data, (w,h)).convert_alpha()
    
    def GetPixel(self, x, y):
        return self.image_data.get_at((x,y))
    

class Sprite:
    sprite_frames = []
    total_frames = 0
    w = 0
    h = 0

    def __init__(self, img, horiz=1, vert=1, w=0,h=0):
        # Calculate width and height of sprites
        self.sprite_frames = []
        self.h = int(img.h / horiz)
        self.w = int(img.w / vert)
        for y in range(0, img.h, self.h):
            for x in range(0, img.w, self.w):
                frame = Image("", self.w, self.h, img.image_data.subsurface(x, y, self.w, self.h))
                if(w != 0 and h != 0):
                    frame = ResizeImage(frame, w, h)
                self.sprite_frames.append(frame)
        
        if(w != 0 and h != 0):
            self.w = w
            self.h = h
    
        self.total_frames = len(self.sprite_frames)

    def GetFrame(self, idx):
        return self.sprite_frames[idx]

# Animation player object
# Create an animation player using a sprite
# Then add animations to it
# Finally play it, render it, etc
# DrawAnimation() must be called in another objects draw variable
class AnimationPlayer(Object):
    
    def __init__(self, sprite):
        super().__init__()

        self.is_playing = False
        self.is_looping = False
        self.playing_animation_key = ""
        self.current_frame = 0

        self.timer = 0
        self.sprite = sprite

        self.animations = {}
    
    def Update(self, elapsed):
        if(self.is_playing):
            self.timer += (elapsed / 1000)
            if(self.timer >= self.animations[self.playing_animation_key][1]):
                self.timer = 0
                self.current_frame += 1
                if(self.current_frame >= len(self.animations[self.playing_animation_key][0])):
                    if(self.is_looping):
                        self.current_frame = 0
                    else:
                        self.StopAnimation()
    
    def DrawAnimation(self, x, y, pivotx=0, pivoty=0, angle=0, horiz_flip=False, vert_flip=False):
        DrawSprite(self.sprite, self.animations[self.playing_animation_key][0][self.current_frame], x, y, pivotx, pivoty, angle, horiz_flip, vert_flip)

    def StopAnimation(self):
        self.is_playing = False
        self.is_looping = False
        self.playing_animation_key = ""
        self.current_frame = 0 
        self.timer = 0

    def PlayAnimation(self, animation_key, is_looping):
        self.is_playing = True
        self.is_looping = is_looping
        self.playing_animation_key = animation_key
        self.current_frame = 0
        self.timer = 0

    def AddAnimation(self, animation_key, frames, interval):
        self.animations[animation_key] = [frames, interval]

# Timer object
# Initialized with a timer_callback that is called after every 
# interval (in millseconds)
# Timer callback should take 
class Timer(Object):

    def __init__(self, interval_ms, timer_callback):
        super().__init__()
        self.interval = interval_ms
        self.timer_callback = timer_callback
        self.timer = 0
        self.disabled = True
    
    def Start(self):
        self.disabled = False
    
    def Update(self, elapsed):
        self.timer += elapsed
        if(self.timer >= self.interval):
            self.timer = 0
            self.disabled = True
            self.timer_callback(self.id)


def events_onkeypress(elapsed, key):
    for object in object_array:
        if(not object.disabled):
            object.OnKeyPress(elapsed, key)

def events_onkeypressed(elapsed, key):
    for object in object_array:
        if(not object.disabled):
            object.OnKeyPressed(elapsed, key)

def events_onkeyrelease(elapsed, key):
    for object in object_array:
        if(not object.disabled):
            object.OnKeyRelease(elapsed, key)

def events_ontextinput(elapsed, c):
    for object in object_array:
        if(not object.disabled):
            object.OnTextInput(elapsed, c)
        
def events_onmousemove(elapsed, x, y):
    for object in object_array:
        if(not object.disabled):
            object.OnMouseMove(elapsed, current_viewport.FromScreen(x, y)[0], current_viewport.FromScreen(x, y)[1])

def ProcessEvents(elapsed):
    # Get inputs
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            return False
            
        if event.type == pygame.KEYDOWN:
            if(event.unicode.isprintable() and event.unicode != ''):
                events_ontextinput(elapsed, str(event.unicode[0]))

            if(event.key == pygame.K_BACKSPACE): events_ontextinput(elapsed, '\b')
            
            if event.key == pygame.K_UP:        events_onkeypress(elapsed, Button.UP); input_array[Button.UP] = True
            if event.key == pygame.K_DOWN:      events_onkeypress(elapsed, Button.DOWN); input_array[Button.DOWN] = True
            if event.key == pygame.K_LEFT:      events_onkeypress(elapsed, Button.LEFT); input_array[Button.LEFT] = True
            if event.key == pygame.K_RIGHT:     events_onkeypress(elapsed, Button.RIGHT); input_array[Button.RIGHT] = True
            if event.key == pygame.K_PAGEUP:    events_onkeypress(elapsed, Button.PG_UP); input_array[Button.PG_UP] = True
            if event.key == pygame.K_PAGEDOWN:  events_onkeypress(elapsed, Button.PG_DOWN); input_array[Button.PG_DOWN] = True
            if event.key == pygame.K_ESCAPE:    events_onkeypress(elapsed, Button.ESC); input_array[Button.ESC] = True
            if event.key == pygame.K_SPACE:     events_onkeypress(elapsed, Button.SPACE); input_array[Button.SPACE] = True
            if event.key == pygame.K_RETURN:    events_onkeypress(elapsed, Button.RETURN); input_array[Button.RETURN] = True; events_ontextinput(elapsed, '\n')
            if event.key == pygame.K_LSHIFT:    events_onkeypress(elapsed, Button.SHIFT); input_array[Button.SHIFT] = True
            if event.key == pygame.K_LCTRL:     events_onkeypress(elapsed, Button.CTRL); input_array[Button.CTRL] = True
            
        elif event.type == pygame.KEYUP: 
            if event.key == pygame.K_UP:        events_onkeyrelease(elapsed, Button.UP); input_array[Button.UP] = False
            if event.key == pygame.K_DOWN:      events_onkeyrelease(elapsed, Button.DOWN); input_array[Button.DOWN] = False
            if event.key == pygame.K_LEFT:      events_onkeyrelease(elapsed, Button.LEFT); input_array[Button.LEFT] = False
            if event.key == pygame.K_RIGHT:     events_onkeyrelease(elapsed, Button.RIGHT); input_array[Button.RIGHT] = False
            if event.key == pygame.K_PAGEUP:    events_onkeyrelease(elapsed, Button.PG_UP); input_array[Button.PG_UP] = False
            if event.key == pygame.K_PAGEDOWN:  events_onkeyrelease(elapsed, Button.PG_DOWN); input_array[Button.PG_DOWN] = False
            if event.key == pygame.K_ESCAPE:    events_onkeyrelease(elapsed, Button.ESC); input_array[Button.ESC] = False
            if event.key == pygame.K_SPACE:     events_onkeyrelease(elapsed, Button.SPACE); input_array[Button.SPACE] = False
            if event.key == pygame.K_RETURN:    events_onkeyrelease(elapsed, Button.RETURN); input_array[Button.RETURN] = False
            if event.key == pygame.K_LSHIFT:    events_onkeyrelease(elapsed, Button.SHIFT); input_array[Button.SHIFT] = False
            if event.key == pygame.K_LCTRL:     events_onkeyrelease(elapsed, Button.CTRL); input_array[Button.CTRL] = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:   events_onkeypress(elapsed, Button.MOUSE1); input_array[Button.MOUSE1] = True
            if event.button == pygame.BUTTON_RIGHT:  events_onkeypress(elapsed, Button.MOUSE2); input_array[Button.MOUSE2] = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_LEFT:   events_onkeyrelease(elapsed, Button.MOUSE1); input_array[Button.MOUSE1] = False
            if event.button == pygame.BUTTON_RIGHT:  events_onkeyrelease(elapsed, Button.MOUSE2); input_array[Button.MOUSE2] = False
    
    
    for idx, i in enumerate(input_array):
        if i == True:
            events_onkeypressed(elapsed, idx)
        
    return True


def Loop(fps):
    global screen_surface, screen_width, screen_height, pygame_clock, pygame_window
    global destruction_queue, object_array
    
    pygame_clock = pygame.time.Clock()
    old_ticks = pygame.time.get_ticks()
    elapsed = 0
    mouse_x, mouse_y = pygame.mouse.get_pos()
    running = True
    pygame.display.set_caption(pygame_window_caption)

    while running:
        
        new_ticks = pygame.time.get_ticks()
        elapsed = pygame.time.get_ticks() - old_ticks
        old_ticks = new_ticks
        
        # Destroy objects queued for destruction
        if(destruction_queue != []):
            new_object_array = []
            for object in object_array:
                destroyed = False
                for destroyed_id in destruction_queue:
                    if(object.id == destroyed_id):
                        destroyed = True

                if(not destroyed):
                    new_object_array.append(object)
            
            object_array = new_object_array
            # Reset destruction queue
            destruction_queue = []

        # Update Objects
        for object in object_array:
            if(not object.disabled):
                object.Update(elapsed)
        
        # Clear Screen
        Clear(0,0,0)
    
        for object in object_array:
            if(not object.hidden):
                object.Draw(elapsed)

        running = ProcessEvents(elapsed)

        # Process mouse coordinates
        new_mouse_x, new_mouse_y = pygame.mouse.get_pos()
        if new_mouse_x != mouse_x or new_mouse_y != mouse_y:
            mouse_x = new_mouse_x
            mouse_y = new_mouse_y
            events_onmousemove(elapsed, new_mouse_x, new_mouse_y)

        if(pygame_window):
            pygame_window.blit(pygame.transform.scale(screen_surface, (pygame_windowWidth, pygame_windowHeight)), [0,0,pygame_windowWidth, pygame_windowHeight])

        # Update to screen
        pygame.display.flip()
        pygame_clock.tick(fps)

def IsPressed(key):
    return input_array[key]

def SetCaption(caption):
    global pygame_window_caption
    pygame_window_caption = caption

def GetScreenSurface():
    return screen_surface

def GetHeight():
    return screen_surface.get_size()[1]

def GetWidth():
    return screen_surface.get_size()[0]

def Clear(r, g, b):
    global screen_surface
    screen_surface.fill((r, g, b))

def SetRenderTarget(target):
    global screen_surface
    if(target == None):
        screen_surface = default_render_target
    else:
        screen_surface = target.render_surface

def DrawPixel(x, y, r, g, b):
    x, y = current_viewport.ToScreen(x, y)
    screen_surface.set_at((int(x), int(y)), pygame.Color((int(r), int(g), int(b))))

def DrawLine(x1, y1, x2, y2, r, g, b, width=1):
    x1, y1 = current_viewport.ToScreen(x1, y1)
    x2, y2 = current_viewport.ToScreen(x2, y2)

    pygame.draw.line(screen_surface, pygame.Color(int(r),int(g),int(b)), (x1, y1), (x2, y2), width)

def DrawCircle(x, y, radius, r, g, b, filled = False, linewidth = 1):
    x, y = current_viewport.ToScreen(x, y)
    if(filled):
        pygame.draw.circle(screen_surface, pygame.Color(int(r), int(g), int(b)), (x,y), radius, 0)
    else:
        pygame.draw.circle(screen_surface, pygame.Color(int(r), int(g), int(b)), (x,y), radius, linewidth)

def DrawTriangle(x1, y1, x2, y2, x3, y3, r, g, b, filled = False, linewidth = 1):
    x1, y1 = current_viewport.ToScreen(x1, y1)
    x2, y2 = current_viewport.ToScreen(x2, y2)
    x3, y3 = current_viewport.ToScreen(x3, y3)

    if(filled):
        pygame.draw.polygon(screen_surface, pygame.Color(int(r), int(g), int(b)), [(x1,y1), (x2, y2), (x3, y3)], 0)
    else:
        pygame.draw.polygon(screen_surface, pygame.Color(int(r), int(g), int(b)), [(x1,y1), (x2, y2), (x3, y3)], linewidth)

def DrawBlock(x, y, w, h, r, g, b, filled = False, linewidth = 1, opacity=255):
    x, y = current_viewport.ToScreen(x, y)
    
    if(opacity != 255):
        rect = pygame.surface.Surface((w, h))
        rect.set_alpha(opacity)
        if(filled):
            rect.fill((int(r), int(g), int(b)))
        else:
            pygame.draw.rect(rect, (int(r), int(g), int(b)), [0,0,w,h], linewidth)
        
        screen_surface.blit(rect, [x, y])
        return
    
    if(filled):
        pygame.draw.rect(screen_surface, pygame.Color(int(r), int(g), int(b)), pygame.Rect(x, y, w, h), 0)
    else:
        pygame.draw.rect(screen_surface, pygame.Color(int(r), int(g), int(b)), pygame.Rect(x, y, w, h), linewidth)

def DrawImage(img, x, y, pivotx=0, pivoty=0, angle=0, horiz_flip = False, vert_flip = False, opacity=255):
    # Transform to viewport
    x, y = current_viewport.ToScreen(x, y)
    if(horiz_flip):
        img = FlipImage(img, True, False)
    if(vert_flip):
        img = FlipImage(img, False, True)

    if(opacity != 255):
        img = OpacityImage(img, opacity)
        
    if(angle == 0):
            screen_surface.blit(img.image_data, (round(x - pivotx), round(y - pivoty)))
    else:
        w = img.w
        h = img.h

        # This is the rectangle of the original image.
        box = [pygame.math.Vector2(p) for p in [(0,0), (w,0), (w,-h), (0, -h)]]

        # This is the rotated rectangle itself
        box_rotate = [p.rotate(angle) for p in box]
        
        # The minimum (top left) and maximum co-ordinates (bottom right) of the box
        min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

        # The pivot vector
        pivot = pygame.math.Vector2(pivotx, -pivoty)

        # Rotating the pivot vector
        pivot_rotated = pivot.rotate(angle)

        # Difference b/w the rotated and the current pivot
        pivot_ds = pivot_rotated - pivot

        # Rotating the image causes change in the center of the image so the new origin 
        # has to be changed.
        origin = [
            (x - pivotx + min_box[0] - pivot_ds[0]), 
            (y - pivoty - max_box[1] + pivot_ds[1])
        ]
        rotated_image = pygame.transform.rotate(img.image_data, angle)

def DrawSprite(spr, index, x, y, pivotx=0, pivoty=0, angle=0, horiz_flip=False, vert_flip=False):
        if(index < spr.total_frames):
            DrawImage(spr.sprite_frames[int(index)], x, y, pivotx, pivoty, angle, horiz_flip, vert_flip)

def LoadImage(file):
    return Image(file)

def DuplicateImage(img):
    new_image_data = img.image_data.copy().convert_alpha()
    return Image("", img.w, img.h, new_image_data)

def SetWindowTransprentColor(r, g, b, opacity=200):
    hwnd = pygame.display.get_wm_info()["window"]
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
    # Set window transparency color
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*(r,g,b)), opacity, win32con.LWA_COLORKEY)
  
def CropImage(img, x, y, w, h):
    new_img = DuplicateImage(img)
    cropped_image = pygame.Surface((w,h))
    cropped_image.blit(new_img.image_data, (0,0), (x,y,w,h))
    new_img.image_data = cropped_image
    new_img.w = w 
    new_img.h = h
    return new_img

def MakeTransparentImage(img, r,g,b):
    new_img = DuplicateImage(img)
    new_img.image_data.set_colorkey(pygame.Color(int(r), int(g), int(b)))
    new_img.image_data.convert_alpha()
    return new_img

def OpacityImage(img, opacity):
    new_img = DuplicateImage(img)
    alpha_surface = pygame.Surface(img.image_data.get_size(), pygame.SRCALPHA)
    alpha_surface.fill((255, 255, 255, opacity))
    new_img.image_data.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return new_img

def ResizeImage(img, w, h):
    new_img = DuplicateImage(img)
    new_img.w = w
    new_img.h = h
    new_img.image_data = pygame.transform.scale(img.image_data, (w,h))
    return new_img

def FlipImage(img, horizontal=False, vertical=False):
    new_img = DuplicateImage(img)
    new_img.image_data = pygame.transform.flip(new_img.image_data, horizontal, vertical)
    return new_img

def LoadSound(filename):
    return pygame.mixer.Sound(filename)

def PlaySound(snd):
    snd.play()

def LoadMusic(file):
    pygame.mixer.music.load(file)

def PlayMusic():
    pygame.mixer.music.play()

def StopMusic():
    pygame.mixer.music.stop()

def Ticks():
    return pygame.time.get_ticks()

def Quit():
    pygame.quit()

def AddObject(obj):
    global object_counter
    object_counter += 1
    
    obj.id = object_counter
    object_array.append(obj)
    
    obj.Create()

    return obj.id

def DeleteObject(id):
    destruction_queue.append(id)

def EnableAllObjects():
    for i in range(len(object_array)):
        object_array[i].Enable()
        

def Init(w, h, window_w=0, window_h=0, borderless=False, custom_title_bar=False):
    global screen_surface, pygame_window, screen_width, screen_height, pygame_windowHeight, pygame_windowWidth, current_viewport, default_viewport, default_render_target

    pygame.init()
    if(window_w != 0 and window_h != 0):
        screen_surface = pygame.Surface([w, h])
        pygame_window = pygame.display.set_mode([window_w, window_h], pygame.DOUBLEBUF | (pygame.NOFRAME if borderless else 0), 32)
    else:
        window_w = w
        window_h = h
        screen_surface = pygame.display.set_mode([window_w, window_h], pygame.DOUBLEBUF | (pygame.NOFRAME if borderless else 0), 32)
    
    default_render_target = screen_surface
    screen_width = w
    screen_height = h
    pygame_windowWidth = window_w
    pygame_windowHeight = window_h

    default_viewport = Viewport(0, 0, screen_width, screen_height)
    current_viewport = default_viewport

    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
