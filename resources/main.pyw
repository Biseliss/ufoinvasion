try:
    import pygame
except:
    import subprocess
    subprocess.check_call(["python.exe", "-m", "pip", "install", "pygame"])
    import pygame
import sys
import random
import time
import json
from threading import Thread
pygame.init()
pygame.font.init()
try:
    pygame.mixer.init()
    audio = True
except:
    audio = False
clock = pygame.time.Clock()
fps = 60

def load_settings():
    global settings
    try:
        with open('./resources/settings.json', encoding="utf-8") as settings:
            settings = json.load(settings)
    except:
        f = open("./resources/settings.json", "w")
        f.write("{}")
        f.close()
        with open('./resources/settings.json', encoding="utf-8") as settings:
            settings = json.load(settings)

def save_settings():
    with open("./resources/settings.json", "w", encoding="utf-8") as write_file:
        json.dump(settings, write_file, ensure_ascii=False, indent=4)

def settings_integrity_check():
    global settings
    mass = list(settings.keys())
    if ("music_volume" not in mass or type(settings["music_volume"]) != float):
        settings["music_volume"] = 1
    if ("sounds_volume" not in mass or type(settings["sounds_volume"]) != float):
        settings["sounds_volume"] = 1

def exit():
    global running
    running = False
    pygame.quit()
    sys.exit()

class slider:
    def __init__(self, pos, value):
        self.pos = pos
        self.value = value
        self.slider_size = (16, 20)
        self.line_height = 4
        self.catched = False
    def ris(self):
        pygame.draw.rect(screen, (200, 200, 200), (self.pos[0], self.pos[1] + self.slider_size[1] // 2 - self.line_height // 2, 200 * self.value, self.line_height))
        pygame.draw.rect(screen, (150, 150, 150), (self.pos[0] + 200 * self.value, self.pos[1] + self.slider_size[1] // 2 - self.line_height // 2, 200 - 200 * self.value, self.line_height))
        pygame.draw.rect(screen, (255, 255, 255), (self.pos[0] + 200 * self.value - self.line_height, self.pos[1], self.slider_size[0], self.slider_size[1]))
    def cycle(self, mouse_pos):
        if (self.catched):
            if (mouse_pos[0] <= self.pos[0]):
                self.value = 0
                return 0
            elif (mouse_pos[0] >= self.pos[0] + 200):
                self.value = 1
                return 1
            else:
                self.value = (mouse_pos[0] - self.pos[0]) / 200
                return (mouse_pos[0] - self.pos[0]) / 200
        else:
            return False
    def catch(self, mouse_pos):
        if (self.pos[0] - self.slider_size[0] // 2 <= mouse_pos[0] < self.pos[0] + 200 + self.slider_size[0] // 2 and self.pos[1] <= mouse_pos[1] < self.pos[1] + self.slider_size[1]):
            self.catched = True

class button:
    def __init__(self, size, pos, color, color_h, color_p, text, text_color, font):
        self.size = size
        self.pos = pos
        self.colors = color, color_h, color_p
        self.text = text
        self.text_color = text_color
        self.font = font
    def press_check(self, mouse_pos):
        return self.pos[0] <= mouse_pos[0] < self.pos[0] + self.size[0] and self.pos[1] <= mouse_pos[1] < self.pos[1] + self.size[1]
    def ris(self, mode):
        pygame.draw.rect(screen, self.colors[mode], (self.pos[0], self.pos[1], self.size[0], self.size[1]))
        s_text(self.text, True, (self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2), self.text_color, 5, resources[self.font])

class ufo:
    def __init__(self, level):
        self.alive = True
        self.size = (96, 96)
        if (random.randint(0, 1)):
            self.pos = [1280, random.randint(0, 720 - self.size[0])]
            self.vx = random.uniform(-round(level), -1)
        else:
            self.pos = [-self.size[0], random.randint(0, 720 - self.size[0])]
            self.vx = random.uniform(1, round(level))
        #self.pos = [random.randint(0, 1280 - self.size[0]), random.randint(0, 720 - self.size[0])]
        self.prev_img = 1
        self.l_des = 0
        self.vy = 0
        #print(level)
    def ris(self):
        if (self.alive):
            screen.blit(resources[f"obj{self.prev_img}"], self.pos)
        else:
            screen.blit(resources[f"des{self.l_des}"], self.pos)
    def cycle(self):
        if (self.alive):
            self.pos[0] += self.vx
            self.pos[1] += self.vy
            return not (-self.size[0] <= self.pos[0] < 1280 + self.size[0] and -self.size[1] <= self.pos[1] < 720 + self.size[1])
        return False
    def click(self, mouse_pos):
        if (not self.alive): return False
        return check_box(self.pos, self.size, mouse_pos)

def change_volume():
    global settings
    if (not audio): return
    mv = sliders["music_volume"].value
    sv = sliders["sounds_volume"].value
    resources["ambient"].set_volume(mv)
    resources["deathsound"].set_volume(sv)
    resources["button"].set_volume(sv)
    settings["music_volume"] = mv
    settings["sounds_volume"] = sv

def s_text(text, ttx, place, color, mode, font, alpha=0):
    #1 - нормальный режим; 2 - режим с отстопом от правого края; 3 - режим с отступом от левого края; 4 - по центру (x); 5 - по центру (х, у)
    if (mode==1):
        screen.blit(font.render(text, ttx, color),(place[0],place[1]))
    elif (mode==4):
        texti=font.render(text, ttx, color)
        if (alpha!=0):
            texti.set_alpha(alpha)
        screen.blit(texti,((screen_size-texti.get_rect()[2])//2+place[0],place[1]))
    elif (mode==5):
        texti=font.render(text, ttx, color)
        if (alpha!=0):
            texti.set_alpha(alpha)
        screen.blit(texti, ((place[0])-(texti.get_rect()[2]//2), (place[1])-(texti.get_rect()[3]//2)))

def check_box(pos, size, mouse_pos):
    return (pos[0] <= mouse_pos[0] < pos[0] + size[0] and pos[1] <= mouse_pos[1] < pos[1] + size[1])

def load_resources():
    global resources
    resources = {}
    for i in r:
        resources[i] = pygame.image.load(f"./resources/images/{i}.png").convert_alpha()
    if (audio):
        for i in s:
            resources[i] = pygame.mixer.Sound(f"./resources/sounds/{i}.wav")
    resources["font"] = pygame.font.Font('./resources/font.ttf', 24)
    resources["big_font"] = pygame.font.Font('./resources/font.ttf', 48)

def pause():
    global paused
    mouse_button_pressed = (False, False, False)
    mbd = False
    while (running):
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(resources["bg"], (0, 0))
        s_text(f"Hits: {hits}", True, (10, 10), (255, 255, 255), 1, resources["font"])
        s_text(f"Misses: {misses}", True, (10, 38), (255, 255, 255), 1, resources["font"])
        s_text(f"Missed: {missed}", True, (10, 66), (255, 255, 255), 1, resources["font"])
        s_text(f"Level: {int(level)}", True, (10, 94), (255, 255, 255), 1, resources["font"])
        s_text("Paused", True, (1280//2, 340), (255, 255, 255), 5, resources["big_font"])
        s_text("Press ESCAPE to continue", True, (1280//2, 400), (255, 255, 255), 5, resources["big_font"])
        
        s_text("Music volume:", True, (10, 664), (255, 255, 255), 1, resources["font"])
        s_text("Sounds volume:", True, (10, 692), (255, 255, 255), 1, resources["font"])
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                exit()
            elif (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    paused = False
                    return
            elif (event.type == pygame.MOUSEBUTTONDOWN):
                mbd = True
                mouse_button_pressed = pygame.mouse.get_pressed()
                if (mouse_button_pressed[0]):
                    sliders["music_volume"].catch(mouse_pos)
                    sliders["sounds_volume"].catch(mouse_pos)
            elif (event.type == pygame.MOUSEBUTTONUP):
                sliders["music_volume"].catched = False
                sliders["sounds_volume"].catched = False
                mbd = False
                if (mouse_button_pressed[0]):
                    if (buttons["resume_button"].press_check(mouse_pos)):
                        if (audio): resources["button"].play()
                        paused = False
                        return False
                    elif (buttons["menu_button"].press_check(mouse_pos)):
                        if (audio): resources["button"].play()
                        paused = False
                        return True
        if (buttons["resume_button"].press_check(mouse_pos)):
            if (mbd):
                buttons["resume_button"].ris(2)
            else:
                buttons["resume_button"].ris(1)
        else:
            buttons["resume_button"].ris(0)
        if (buttons["menu_button"].press_check(mouse_pos)):
            if (mbd):
                buttons["menu_button"].ris(2)
            else:
                buttons["menu_button"].ris(1)
        else:
            buttons["menu_button"].ris(0)
        if (mbd):
            sliders["music_volume"].cycle(mouse_pos)
            sliders["sounds_volume"].cycle(mouse_pos)
            change_volume()
        sliders["music_volume"].ris()
        sliders["sounds_volume"].ris()
        pygame.display.flip()
        clock.tick(fps)

def game():
    global running, objects, hits, missed, misses, level, paused
    mouse_button_pressed = (False, False, False)
    running = True
    paused = False
    hit = False
    #mbd = False
    objects = []
    hits = 0
    missed = 0
    misses = 0
    level = 0.1
    Thread(target=ufo_animation).start()
    Thread(target=ufo_spawner).start()
    while (running):
        screen.blit(resources["bg"], (0, 0))
        s_text(f"Hits: {hits}", True, (10, 10), (255, 255, 255), 1, resources["font"])
        s_text(f"Misses: {misses}", True, (10, 38), (255, 255, 255), 1, resources["font"])
        s_text(f"Missed: {missed}", True, (10, 66), (255, 255, 255), 1, resources["font"])
        s_text(f"Level: {int(level)}", True, (10, 94), (255, 255, 255), 1, resources["font"])
        mouse_pos = pygame.mouse.get_pos()
        for i in objects:
            if (i.cycle()):
                objects.remove(i)
                missed += 1
                #print(hits, missed)
            else:
                i.ris()
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                exit()
            elif (event.type == pygame.MOUSEBUTTONDOWN):
                mbd = True
                mouse_button_pressed = pygame.mouse.get_pressed()
                if (mouse_button_pressed[0]):
                    for i in objects:
                        if (i.click(mouse_pos)):
                            hit = True
                            hits += 1
                            level = hits / 10
                            i.alive = False
                            if (audio): resources["deathsound"].play()
                    if (hit):
                        hit = False
                    else:
                        misses += 1
            elif (event.type == pygame.MOUSEBUTTONUP):
                mbd = False
            elif (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    paused = True
                    if (pause()): return
                    save_settings()
        pygame.display.flip()
        clock.tick(fps)

def menu():
    mbd = False
    if (audio): resources["ambient"].play(loops=-1, maxtime=0, fade_ms=0)
    while (True):
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(resources["bg"], (0, 0))
        screen.blit(resources["title"], (0, 0))
        s_text("Music volume:", True, (10, 664), (255, 255, 255), 1, resources["font"])
        s_text("Sounds volume:", True, (10, 692), (255, 255, 255), 1, resources["font"])
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                exit()
            elif (event.type == pygame.MOUSEBUTTONDOWN):
                mbd = True
                mouse_button_pressed = pygame.mouse.get_pressed()
                if (mouse_button_pressed[0]):
                    sliders["music_volume"].catch(mouse_pos)
                    sliders["sounds_volume"].catch(mouse_pos)
            elif (event.type == pygame.MOUSEBUTTONUP):
                mbd = False
                sliders["music_volume"].catched = False
                sliders["sounds_volume"].catched = False
                if (mouse_button_pressed[0]):
                    if (buttons["play_button"].press_check(mouse_pos)):
                        if (audio): resources["button"].play()
                        save_settings()
                        game()
            sliders["music_volume"].cycle(mouse_pos)
            sliders["sounds_volume"].cycle(mouse_pos)
            change_volume()
        sliders["music_volume"].ris()
        sliders["sounds_volume"].ris()
        if (buttons["play_button"].press_check(mouse_pos)):
            if (mbd):
                buttons["play_button"].ris(2)
            else:
                buttons["play_button"].ris(1)
        else:
            buttons["play_button"].ris(0)
        pygame.display.flip()
        clock.tick(fps)
    
def ufo_spawner():
    global objects
    while (running):
        if (paused):
            time.sleep(0.5)
            continue
        objects.append(ufo(level))
        time.sleep(1.5 / (level * 0.05 + 1))

def ufo_animation():
    global objects
    while (running):
        if (paused):
            time.sleep(0.5)
            continue
        for i in objects:
            if (i.alive):
                i.prev_img += 1
                if (i.prev_img >= 4):
                    i.prev_img = 1
            else:
                i.l_des += 1
                if (i.l_des >= 4):
                    objects.remove(i)
        time.sleep(0.1)

def init_game():
    global screen, buttons, sliders, r, s
    load_settings()
    settings_integrity_check()
    r = ["bg", "obj1", "obj2", "obj3", "des0", "des1", "des2", "des3", "title"]
    s = ["ambient", "deathsound", "button"]
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption('UFO Invasion')
    pygame.display.set_icon(pygame.image.load("./resources/images/obj0.png").convert_alpha())
    load_resources()
    buttons = {"resume_button": button((512, 64), ((1280 - 512) // 2, 476), (255, 0, 0), (255, 64, 64), (191, 0, 0), "Resume", (255, 255, 255), "big_font"),
               "menu_button": button((512, 64), ((1280 - 512) // 2, 545), (0, 0, 255), (64, 64, 255), (0, 0, 191), "Exit to main menu", (255, 255, 255), "big_font"),
               "play_button": button((512, 64), ((1280 - 512) // 2, 545), (0, 0, 255), (64, 64, 255), (0, 0, 191), "Play", (255, 255, 255), "big_font")}
    sliders = {"music_volume": slider((200, 664), settings["music_volume"]), "sounds_volume": slider((200, 692), settings["sounds_volume"])}
    change_volume()

