# SS 2020 Programmierpraktium Projekt
# ALexander Guggenberger

# 0.0 LOAD PACKAGES ###############################################################

import math
import os
import random
import ctypes
import datetime
import sys

import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])   

install("pygame")
install("Pillow")

# should this not work, copy to console and enter (invalide syntax error if run from editor):
# pip install pygame
# pip install Pillow

import pygame
from pygame import mixer

# 0.1 IMAGE PROCESSING ##################################################################
# if images have not been processed so far, run code for image processing

os.chdir(os.path.dirname(sys.argv[0]))

if not(os.path.isfile("images/crashing_0_0.png")):
    import image_processing

# 0.2 SET UP ######################################################################

# avoids automatical stretching of the screen (resolution issues)
# note: this line only works for Windows
ctypes.windll.user32.SetProcessDPIAware()

# set working directory

pygame.init()
mixer.init()

win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = pygame.display.get_surface().get_size()

clock = pygame.time.Clock()

pygame.display.set_caption("Die Trireme der Extreme")


# 1.0 IMAGES, SURFACES AND SOUND

# load images for map and command_bar
bg_wasser = pygame.image.load("images/Hintergrund/bg_wasser.jpeg").convert()
bg_links = pygame.image.load("images/Hintergrund/bg_links.jpeg").convert()
bg_rechts = pygame.image.load("images/Hintergrund/bg_rechts.jpeg").convert()
bg_unten = pygame.image.load("images/Hintergrund/bg_unten.jpeg").convert()
bg_links_oben = pygame.image.load("images/Hintergrund/bg_links_oben.jpeg").convert()
bg_rechts_oben = pygame.image.load("images/Hintergrund/bg_rechts_oben.jpeg").convert()

bg = [[bg_links_oben, bg_wasser, bg_rechts_oben], 
      [bg_links, bg_wasser, bg_rechts],
      [bg_wasser, bg_unten, bg_wasser]]

minimap = pygame.image.load("images/minimap.jpeg").convert()

# load and resize intro background image to screen format before loading
intro_bg = pygame.image.load("images/intro_bg.jpeg").convert()
intro_bg = pygame.transform.scale(intro_bg, (W, H))

# create surfaces for buttons, decoration and command bar

#buttons (intro screen buttons and quit button)
button = pygame.Surface((int(W/2), int(H/10)))
button.set_alpha(128)
button.fill((255,255,255))

button_bright = pygame.Surface((int(W/2), int(H/10)))
button_bright.set_alpha(200)
button_bright.fill((255,255,255))

#command bar
command_bar = pygame.Surface((int(400), int(H - minimap.get_height() - H/200 - H * 6/50 - (400 - minimap.get_width()))))
command_bar.set_alpha(128)
command_bar.fill((255,255,255))

# in-game quit button
small_button = pygame.Surface((int(command_bar.get_width()), int(H/20)))
small_button.set_alpha(128)
small_button.fill((255,255,255))

small_button_bright = pygame.Surface((int(command_bar.get_width()), int(H/20)))
small_button_bright.set_alpha(200)
small_button_bright.fill((255,255,255))

#tiny deco bars for main screen
tiny_bar = pygame.Surface((W, int(H/200)))
tiny_bar.set_alpha(128)
tiny_bar.fill((255,255,255))

#deco bars
deco_bar = pygame.Surface((W, int(H/20)))
deco_bar.set_alpha(128)
deco_bar.fill((255,255,255))

#big bar for title screen caption
caption_bar = pygame.Surface((int(W * 3/4), int(H/4)))
caption_bar.set_alpha(128)
caption_bar.fill((255,255,255))

#background surface for help/mission explanation
mission_explanation_bg = pygame.Surface((int(W/2), int(H/2)))
mission_explanation_bg.set_alpha(128)
mission_explanation_bg.fill((255,255,255))

# create list of music
playlist = list()
playlist.append("sounds/Spielmusik_gemächlich Export 1.mp3")
playlist.append("sounds/Spielmusik_Spannung Export 1.mp3")
playlist.append("sounds/Spielmusik_ruhig Export 1.mp3")

# pieces will be repeated infinitely (see main loop)
song_counter = 1
pygame.mixer.music.load(playlist[0])  
pygame.mixer.music.play()

# load sounds
ocean_waves = pygame.mixer.Sound("sounds/meeresrauschen.wav")
rowing_sound = pygame.mixer.Sound("sounds/rudern.wav")
crashing_sound = pygame.mixer.Sound("sounds/crash.wav")

ocean_waves.set_volume(0.5)
rowing_sound.set_volume(0.1)
crashing_sound.set_volume(1)

pygame.mixer.music.set_volume(1)

# set high enough number of channels s.t. new ships will always find a new channel for their sound
pygame.mixer.set_num_channels(50)

# font sizes
tinyFont = pygame.font.SysFont('freesansbold.ttf', 15)
smallFont = pygame.font.SysFont('freesansbold.ttf', 30)
mediumFont = pygame.font.Font('freesansbold.ttf', 50)
largeFont = pygame.font.Font('freesansbold.ttf', 100)

# 2.0 OBJECT ######################################################################

class vessel(object):
    row = [[pygame.image.load(os.path.join("images", "rowing_" + str(j) + "_" + str(i) + ".png")) for i in range(1, 41)] for j in range(0,4)]
    crash = [[pygame.image.load(os.path.join("images", "crashing_" + str(j) + "_" + str(i) + ".png")) for i in range(1, 40)] for j in range(0,4)]

    def __init__(self, x, y, angle, type, number):
        self.x = x
        self.y = y
        self.angle = angle
        self.type = type
        self.number = number
        
        self.rowing = False
        self.direction = 1
        self.crashing = False
        self.rowCount = 0
        self.crashCount = 0
        self.velocity = ai_velocity * types_velocity[type] # only used for computer ships
        self.channel = number + 1 # channel for sounds
        self.destroyed = False
        self.troops = round(types_troops[type] * (1 + 0.6 * (random.random() - 0.5))) # ai ships carry the number of troops of their type plus some variation

        self.width = self.row[self.type][0].get_width()
        self.height = self.row[self.type][0].get_height()

    def draw(self, win):
        if self.rowing == True:
            rot_img = pygame.transform.rotate(self.row[self.type][(self.rowCount//3)%len(self.row[self.type])], self.angle)
            if end == False:
                self.rowCount += 1 * self.direction
            
            if 0 < self.x < W and 0 < self.y < H and  not(pygame.mixer.Channel(self.channel).get_busy()):
                pygame.mixer.Channel(self.channel).play(rowing_sound)

        if self.crashing == True:
            if self.crashCount == 0:
                rowing_sound.stop()
                
            if (not(pygame.mixer.Channel(self.channel).get_busy()) and self.crashCount <= len(self.crash[self.type])):                
                crashing_sound.play()
                   
            if self.crashCount < 60:
                rot_img = pygame.transform.rotate(self.crash[self.type][(self.crashCount//3)], self.angle)
                if end == False:
                    self.crashCount += 1
                    
            if 60 <= self.crashCount < 630:
                rot_img = pygame.transform.rotate(self.crash[self.type][(self.crashCount//30 + 18)], self.angle)
                if end == False:
                    self.crashCount += 1
                    
            if self.crashCount >= 630:
                self.destroyed = True

        else:
            rot_img = pygame.transform.rotate(self.row[self.type][(self.rowCount//3)%len(self.row[self.type])], self.angle)
#            pygame.mixer.Channel(self.channel).stop()

        win.blit(rot_img, (self.x - int(rot_img.get_width()/2),self.y - int(rot_img.get_height()/2),))

# 3.0 INITIAL VARIABLES ###########################################################

fps = 60

time = 0

intro = False #variables that determine whether screens are shown
end = False
show_mission = True

hit_points = 200 #start population
last_time_new_ships = 0 #generate a variable containing the last time that ships were spawned

interval = 80 #determin interval in which enemy ships are spawned

ai_ships = [] #generate of list of ai ships:    
ai_velocity = 1.2 #set ai ship base velocity (will increase over time and varies by type)
print(ai_velocity)
types_velocity = (0, 1.5, 1.2, 1) #write down characteristics of types (velocity factor and troops carried)
types_troops = (0, 200,  120, 30)

velocity1 = 0 #start values for main ship
velocity = 0
angle_dif = 0
xSpeed = ySpeed = 0       
ship = vessel((int(W - command_bar.get_width())/2), int(H/2), 200, 0, 0) #place main ship

bgX = - 1400 + W/2 #initial position of background
bgY = - 1800 + H/2

points0 = [(0,0), #points around main ship used for collision with islands and other ships (relative to the center of the main ship)
          (0, ship.height * 3/4),
          (0, -ship.height * 3/4),
          (0, ship.height/3),
          (0, -ship.height/3),
          (ship.width/2, ship.height/2),
          (ship.width/2, -ship.height/2),
          (-ship.width/2, ship.height/2),
          (-ship.width/2, -ship.height/2)]

# render text that does not change:

mission = largeFont.render("Mission", 1, (0, 0, 0))

mission_text = []
mission_text.append(smallFont.render("Der Zweite Punische Krieg tobt und die sizilianische Polis Syrakus, deren Bürger", 1, (0,0,0)))
mission_text.append(smallFont.render("Ihr seid, steht auf der Seite Kathargos. Schon seit längerem hat das expansionslüsterne", 1, (0,0,0)))
mission_text.append(smallFont.render("Rom seinen begehrlichen Blick darauf geworfen. Nur die von Euch befehligte Trireme", 1, (0,0,0)))
mission_text.append(smallFont.render("steht noch zwischen Eurer Stadt und ihrem Untergang - doch verzagt nicht, Poseidon", 1, (0,0,0)))
mission_text.append(smallFont.render("ist Euch wohlgesonnen, und Euer Schiff ist denen des Feindes klar überlegen - es", 1, (0,0,0)))
mission_text.append(smallFont.render("ist gewissermaßen die Trireme der Extreme...", 1, (0,0,0)))
mission_text.append(smallFont.render("Falls ein Schiff des Imperiums die Ausläufer der Stadt erreicht, wird Eure Bevölkerung", 1, (0,0,0)))
mission_text.append(smallFont.render("um genau die Mannschaftsgröße des gelandeten Schiffes, die euch auf der Strategiekarte", 1, (0,0,0)))
mission_text.append(smallFont.render("angezeigt wird, dezimiert.", 1, (0,0,0)))
mission_text.append(smallFont.render("Rammt und versenkt alle römischen Schiffe, bevor es soweit kommt, und verhindert, dass", 1, (0,0,0)))
mission_text.append(smallFont.render("die Kreise des Archimedes gestört werden!", 1, (0,0,0)))

start_caption = largeFont.render("Die Trireme der Extreme", 1, (0, 0, 0))
start_text = mediumFont.render("Spiel starten", 1, (0,0,0))
quit_text = mediumFont.render("Schließen", 1, (0,0,0))

end_caption = largeFont.render("Alea iacta est!", 1, (0, 0, 0))

end_text = []

end_text.append(smallFont.render("Über das Meer hallt bedrohlich der Gleichschritt der Legionen in den menschenleeren", 1, (0,0,0)))
end_text.append(smallFont.render("Straßen zu Euch hinüber, und Euer Blick schweift fassungslos über die rauchenden", 1, (0,0,0)))
end_text.append(smallFont.render("Trümmer der einst prächtigen Polis. Ares hat sich von Euch abgewandt:", 1, (0,0,0)))
end_text.append(smallFont.render("Schlussendlich haben die feindlichen Schiffe Euren äußersten Anstrengungen zum Trotz", 1, (0,0,0)))
end_text.append(smallFont.render("die Küste der Stadt erreicht und Syrakus fällt an das römische Imperium. Ihr wagt Euch", 1, (0,0,0)))
end_text.append(smallFont.render("nicht auszumalen, was dies für den weiteren Verlauf des Krieges bedeuten mag.", 1, (0,0,0)))
end_text.append(smallFont.render("Nicht zuletzt wurden die Kreise des Archimedes nachhaltig gestört -", 1, (0,0,0)))
end_text.append(smallFont.render("doch ist dies angesichts seines Ablebens ein eher unwesentliches Problem.", 1, (0,0,0)))

ok_text = mediumFont.render("OK", 1, (0,0,0))

to_start_screen = smallFont.render("Spiel beenden", 1, (0,0,0))
hilfe = smallFont.render("Mission", 1, (0,0,0))

geschwindigkeit = smallFont.render("Geschwindigkeit (Knoten):", 1, (0,0,0))
zeit = smallFont.render("Zeit:", 1, (0,0,0))
zeit_bis_zur_naechsten_welle = smallFont.render("Zeit bis zur nächsten Welle:", 1, (0,0,0))
population = smallFont.render("Population:", 1, (0,0,0))

#4.0 FUNCTIONS ####################################################################

# write a function that does all the drawing in the main loop
def redrawWindow():

#draw background water:
    for x in range(0,3):
        for y in range(0,3):
            win.blit(bg[y][x], (bgX + x*bg_wasser.get_width(), bgY + y*bg_wasser.get_height()))

#draw ai ships
    for ai_ship in ai_ships:
        ai_ship.draw(win)

#draw main ship
    ship.draw(win)

#draw points around the ship:
    
#    for point in points3:
#       pygame.draw.circle(win, (255,0,0), point, 3)

#    pygame.draw.circle(win, (255,0,0), p_jetty[0], 3)

# draw command_bar and minimap   

    win.blit(command_bar, (W - command_bar.get_width(), int(4 * tiny_bar.get_height() + 2 * small_button.get_height())))
    win.blit(command_bar, (W - command_bar.get_width(), int(5 * tiny_bar.get_height() + 2 * small_button.get_height() + command_bar.get_height())))
    
    mini_xy = ((W - command_bar.get_width() + (command_bar.get_width() - minimap.get_width())/2, H - minimap.get_height() - (command_bar.get_width() - minimap.get_width())/2))
    win.blit(minimap, mini_xy)

#make quit and help button
#create variables for mouse interaction
    mouse = pygame.mouse.get_pos()
    left_click = pygame.mouse.get_pressed()[0]

#first, draw tiny deco bar above the buttons to make it look nicer

    win.blit(tiny_bar, (int(W - command_bar.get_width()), 0))

# quit button    
    small_button1xy = (int(W - command_bar.get_width()), int(2*tiny_bar.get_height()))
    
    if (small_button1xy[0] < mouse[0] < small_button1xy[0] + small_button.get_width() and
        small_button1xy[1] < mouse[1] < small_button1xy[1] + small_button.get_height()):

        win.blit(small_button_bright, (small_button1xy[0], small_button1xy[1]))
        
        if left_click == True:
            pygame.mixer.music.stop()
            start_screen()

    else:
        win.blit(small_button, (small_button1xy[0], small_button1xy[1]))

# help/mission explanation
    global show_mission
    if show_mission == True:
        
        win.blit(mission_explanation_bg, (int((W- command_bar.get_width())/2 - mission_explanation_bg.get_width()/2), int(H/5)))

        win.blit(mission,
                 (int((W- command_bar.get_width())/2 - mission.get_width()/2), 
                  int(H/5 + 50)))

        for i in range(0, len(mission_text)):
            win.blit(mission_text[i], 
                     (int((W- command_bar.get_width())/2 - mission_text[i].get_width()/2), 
                      int(H/5 + 50 + mission.get_height() + 40 + i * (mission_text[i].get_height() + 7))))
        
        ok_buttonxy = (int((W - command_bar.get_width())/2 - mission_explanation_bg.get_width()/2), int(H/5 + mission_explanation_bg.get_height() + H/40))

        if (ok_buttonxy[0] < mouse[0] < ok_buttonxy[0] + button.get_width() and ok_buttonxy[1] < mouse[1] < ok_buttonxy[1] + button.get_height()):
                        
            win.blit(button_bright, (ok_buttonxy[0], ok_buttonxy[1]))

            if left_click == 1:
                show_mission = False

        else:
            win.blit(button, (ok_buttonxy[0], ok_buttonxy[1]))

        win.blit(ok_text, (int(ok_buttonxy[0] + (button.get_width() - ok_text.get_width())/2), 
                           int(ok_buttonxy[1] + (button.get_height() - ok_text.get_height())/2)))

# help button
    small_button2xy = (int(W - command_bar.get_width()), int(3*tiny_bar.get_height() + small_button.get_height()))
    
    if (small_button2xy[0] < mouse[0] < small_button2xy[0] + small_button.get_width() and
        small_button2xy[1] < mouse[1] < small_button2xy[1] + small_button.get_height()):

        win.blit(small_button_bright, (small_button2xy[0], small_button2xy[1]))
        
        if left_click == True:
            show_mission = True

    else:
        win.blit(small_button, (small_button2xy[0], small_button2xy[1]))
    
    win.blit(to_start_screen, (small_button1xy[0] + small_button.get_width()/2 - to_start_screen.get_width()/2,
                               small_button1xy[1] + small_button.get_height()/2 - to_start_screen.get_height()/2))
    win.blit(hilfe, (small_button2xy[0] + small_button.get_width()/2 - hilfe.get_width()/2,
                               small_button2xy[1] + small_button.get_height()/2 - hilfe.get_height()/2))

# draw ships on minimap
# main ship:
    pygame.draw.circle(win, (255,0,0), (int(mini_xy[0] + points1[0][0] * minimap.get_width()/(bg_wasser.get_width()* len(bg[0]))),
                                         int(mini_xy[1] + points1[0][1] * minimap.get_width()/(bg_wasser.get_height()* len(bg)))), 4)

#computer ships:
    for ai_ship in ai_ships:
        pygame.draw.circle(win, (0,0,0), (int(mini_xy[0] + (ai_ship.x - bgX) * minimap.get_width()/(bg_wasser.get_width()* len(bg[0]))),
                                         int(mini_xy[1] + (ai_ship.y - bgY) * minimap.get_width()/(bg_wasser.get_height()* len(bg)))), 4)
#write number of troops on the ship right above the point representing the ship
        win.blit(tinyFont.render(str(ai_ship.troops), 1, (0,0,0)), (int(mini_xy[0] + (ai_ship.x - bgX) * minimap.get_width()/(bg_wasser.get_width()* len(bg[0])) + 5),
                                                                  int(mini_xy[1] + (ai_ship.y - bgY) * minimap.get_width()/(bg_wasser.get_height()* len(bg)) - 10)))

#text
    text1 = mediumFont.render(str(round(abs(velocity) * 1.5, 1)), 1, (0,0,0))
    text2 = mediumFont.render(str(datetime.timedelta(seconds = round(time))), 1, (0,0,0))
    text3 = mediumFont.render(str(datetime.timedelta(seconds = round(interval - (time - last_time_new_ships)))), 1, colour(interval, (interval - (time - last_time_new_ships))))
    text4 = mediumFont.render(str(hit_points), 1, (0,0,0))

    horizontal_shift = H/5 #auxiliar variables for vertical distances between information displays
    small_shift = H/40
    big_shift = H/15

    win.blit(geschwindigkeit, 
             (W - command_bar.get_width() + 40, horizontal_shift))
    win.blit(text1, 
             (W - command_bar.get_width()/2 - text1.get_width()/2, horizontal_shift + 1*small_shift))
    win.blit(zeit, 
             (W - command_bar.get_width() + 40, horizontal_shift + 1*small_shift + 1*big_shift))
    win.blit(text2, 
             (W - command_bar.get_width()/2 - text2.get_width()/2, horizontal_shift + 2*small_shift + 1*big_shift))
    win.blit(zeit_bis_zur_naechsten_welle, 
             (W - command_bar.get_width() + 40, horizontal_shift + 2*small_shift + 2*big_shift))
    win.blit(text3, 
             (W - command_bar.get_width()/2 - text3.get_width()/2, horizontal_shift +3*small_shift + 2*big_shift))
    win.blit(population, 
             (W - command_bar.get_width() + 40, horizontal_shift  + 3*small_shift + 3*big_shift))
    win.blit(text4, 
             (W - command_bar.get_width()/2 - text4.get_width()/2, horizontal_shift + 4*small_shift + 3*big_shift))
    
#unmute to blit frame rate
    fps_text = smallFont.render("FPS: " + str(round(clock.get_fps(), 2)), 1, (255,255,255))
    win.blit(fps_text, (5, 5))
    
    pygame.display.update()

#define a function that returns a colour from green to red depending on a value (for displaying time until next wave)
def colour(max_val, val):
    r = max(0, min(1, 2 * (max_val - val)/max_val) * 200)
    g = max(0, min(1, 2 * val/max_val) * 200)
    b = 0
    return (r, g, b)

#define distance function
def dist(a,b):
    dist  = math.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    return dist

#make a function for the start screen
def start_screen():

    intro = True
    while intro:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        #create variables for mouse interaction
        mouse = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        
#show intro background
        win.blit(intro_bg, (0,0))
 
#draw decorative bars
        win.blit(deco_bar, (0, int(H * 1/20)))
        win.blit(deco_bar, (0, int(H * 19/20 - deco_bar.get_height())))
    
        win.blit(caption_bar, (int(W/2 - caption_bar.get_width()/2), int(H * 4/20)))
    
#show buttons, make them brighter if mouse is above them and link them to the corresponding actions               
        button1xy = (int(W/2 - button.get_width()/2), int(H * 10/20))
        button2xy = (int(W/2 - button.get_width()/2), int(H * 13/20))

#play button
        if (button1xy[0] < mouse[0] < button1xy[0] + button.get_width() and button1xy[1] < mouse[1] < button1xy[1] + button.get_height()):
                        
            win.blit(button_bright, (button1xy[0], button1xy[1]))

            if left_click == 1:
                pygame.mixer.music.stop()
                global song_counter
                song_counter = 1
                intro = False

        else:
            win.blit(button, (button1xy[0], button1xy[1]))

#quit button:           
        if (button2xy[0] < mouse[0] < button2xy[0] + button.get_width() and button2xy[1] < mouse[1] < button2xy[1] + button.get_height()):
                        
            win.blit(button_bright, (button2xy[0], button2xy[1]))

            if left_click == 1:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

        else:
            win.blit(button, (button2xy[0], button2xy[1]))

#make text (caption and click options)
        win.blit(start_caption, (int(W/2 - start_caption.get_width()/2), int(H * 4/20 + caption_bar.get_height()/2 - start_caption.get_height()/2)))
        win.blit(start_text, (int(button1xy[0] + (button.get_width() - start_text.get_width())/2), int(button1xy[1] + (button.get_height() - start_text.get_height())/2)))
        win.blit(quit_text, (int(button2xy[0] + (button.get_width() - quit_text.get_width())/2), int(button2xy[1] + (button.get_height() - quit_text.get_height())/2)))

        pygame.display.update()
        clock.tick(fps)

#make a function for the end screen
def end_screen():

    global end
    
    end = True
    while end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        #create variables for mouse interaction
        mouse = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]

#show end background (last picture from game)
#draw background water:
        for x in range(0, 3):
            for y in range(0,3):
                win.blit(bg[y][x], (bgX + x*bg_wasser.get_width(), bgY + y*bg_wasser.get_height()))

#draw ai ships
        for ai_ship in ai_ships:
            ai_ship.draw(win)

#draw main ship
        ship.draw(win)

#draw decorative bars
        win.blit(deco_bar, (0, int(H * 1/20)))
        win.blit(deco_bar, (0, int(H * 19/20 - deco_bar.get_height())))

#draw transparent white background (use mission explanation background for this)
        win.blit(mission_explanation_bg, (int(W/2 - mission_explanation_bg.get_width()/2), int(H * 4/20)))
    
#show buttons, make them brighter if mouse is above them and link them to the corresponding actions
        button1xy = (int(W/2 - button.get_width()/2), int(H * 4/20 + mission_explanation_bg.get_height() + H/20))

#quit button
        if (button1xy[0] < mouse[0] < button1xy[0] + button.get_width() and button1xy[1] < mouse[1] < button1xy[1] + button.get_height()):
                        
            win.blit(button_bright, (button1xy[0], button1xy[1]))

            if left_click == 1:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

        else:
            win.blit(button, (button1xy[0], button1xy[1]))

#make text (caption and click options)
        win.blit(end_caption, (int(W/2 - end_caption.get_width()/2), int(H * 4/20 + 50)))
        win.blit(quit_text, (int(button1xy[0] + (button.get_width() - quit_text.get_width())/2), int(button1xy[1] + (button.get_height() - quit_text.get_height())/2)))
        
        score = mediumFont.render("Ihr habt " + str(datetime.timedelta(seconds = round(time))) + " durchgehalten", 1, (0,0,0))
        win.blit(score, (int(W/2 - score.get_width()/2), int(H * 4/20 + 50 + end_caption.get_height() + 20)))

        for i in range(0, len(end_text)):
            win.blit(end_text[i],
                     (int(W/2 - end_text[i].get_width()/2), 
                      int(H/5 + 50 + end_caption.get_height() + 40 + score.get_height() + 20 + 15 + i * (end_text[i].get_height() + 7))))

# play ocean waves sound        
        if not(pygame.mixer.Channel(0).get_busy()):
            pygame.mixer.Channel(0).play(ocean_waves)

        pygame.display.update()
        clock.tick(fps)

def generate_ships(new_ships):
    
    for i in range (0, new_ships):
#draw random position of ship on parts of the edges of the map
        w = random.random() * 16000

        if w <= 3000:
            x, y = (15000, w + 2000)
        if 3000 < w <= 8000:
            x, y = (15000, w + 7000)
        if 8000 < w <= 10500:    
            x,y = (15000 - (w - 8000), 15000)
        if 10500 < w <= 16000:
            x,y = (7500 - (w - 10500), 15000)

#calculate corresponding angle, s.t. ship heads towards target island    
        angle = math.degrees(math.atan((x - 2000)/(y - 2000)))

#randomly draw type of the ship
        type = round(random.random() * 2 + 1)

#add newly generated object to ai_ships list (coordinates need to be adjusted for shift if starting background screen)     
        ai_ships.append(vessel(x + bgX, y + bgY, angle, type, (len(ai_ships) + 1)))

start_screen()

# 5.0 MAIN LOOP ###############################################################

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit() 

#5.1 check whether music has ended and start new song if it has so (ocean noise respectively)
    if not(pygame.mixer.music.get_busy()):    
        pygame.mixer.music.load(playlist[song_counter%3])
        song_counter += 1
        pygame.mixer.music.play()   
        
#play the noise of the see:
    if not(pygame.mixer.Channel(0).get_busy()):
        pygame.mixer.Channel(0).play(ocean_waves)

# 5.2 keyboard inputs and steering of the main ship
    
    keys = pygame.key.get_pressed()   

#navigation of ship
    if keys[pygame.K_LEFT]:
        angle_dif = 0.15 * velocity

    if keys[pygame.K_RIGHT]:
        angle_dif = - 0.15 * velocity

    if keys[pygame.K_UP]:
        ship.rowing = True
        ship.direction = 1
        velocity1 += 0.02

    if keys[pygame.K_DOWN]:
        ship.rowing = True
        ship.direction = - 1
        velocity1 -= 0.02

#adjustments regarding velocity        
    velocity1 = min(10, velocity1)
    velocity1 = max(- 5, velocity1)
    angle_dif = angle_dif * 0.93
    
    if not(keys[pygame.K_UP]) and velocity1 > 0:
            velocity1 -= 0.04
    if not(keys[pygame.K_DOWN]) and velocity1 < 0:
            velocity1 += 0.04

    if velocity < 1 and velocity > -1 and not(keys[pygame.K_UP] or keys[pygame.K_DOWN]):
        ship.rowing = False

#5.2 has ship gone aground?
#test background colour of points around the ship in order to detect whether ship is colliding with an island
#find location of each of the points on the background image   
        
#points1 contains the coordinates of the point on the whole background
    points1 = [(int((math.cos(math.radians(-ship.angle)) * (point[0]) - math.sin(math.radians(-ship.angle)) * (point[1]) + ship.x - bgX)), 
               int((math.sin(math.radians(-ship.angle)) * (point[0]) + math.cos(math.radians(-ship.angle)) * (point[1]) + ship.y - bgY)))
                for point in points0]

#points2 contains the coordinate of the points on the background tile they are currently on, and the indices of this tile (in the matrix of background images)
    points2 = [(point[0]%bg_wasser.get_width(),
                point[1]%bg_wasser.get_height(),
                int(point[0]//bg_wasser.get_width()),
                int((point[1])//bg_wasser.get_height()))
                for point in points1]

#points3 contains the coordinates of the points on the screen
    points3 = [(int(math.cos(math.radians(-ship.angle)) * (point[0]) - math.sin(math.radians(-ship.angle)) * (point[1]) + ship.x),
                 int(math.sin(math.radians(-ship.angle)) * (point[0]) + math.cos(math.radians(-ship.angle)) * (point[1]) + ship.y)) for point in points0]

#reduce speed if points are not in water:
    if min([bg[point[3]][point[2]].get_at((point[0],point[1]))[2] for point in points2]) < 140:
        velocity1 = velocity1 * 0.7
        
#set speed to zero if inner points are not in water
    if min([bg[point[3]][point[2]].get_at((point[0],point[1]))[2] for point in (points2[3],points2[4])]) < 140:
        velocity1 = 0

#5.3 ai ships
#spawn ai ships if last spawn has been at least three minutes ago
    if (last_time_new_ships == 0 or (time - last_time_new_ships) >= interval - 0.1):
        #first, increase velocity of newly generated ai ships over time so it gets more difficult every time new ships are generated
            ai_velocity += 0.1
        #spawn new ships
            generate_ships(5)
        #update last_time_new_ships (add a little so it does not stay zero for 
        #the first two frames and generates ships twice. Correpsondingly substract 0.1 above):
            last_time_new_ships = time + 0.1

    for ai_ship in ai_ships:
    
        ai_ship.x += xSpeed - math.sin(math.radians(ai_ship.angle)) * ai_ship.velocity
        ai_ship.y += ySpeed - math.cos(math.radians(ai_ship.angle)) * ai_ship.velocity
        ai_ship.rowing = True

#stop ships if they go aground (similar mechanism as for main ship, but only left upper corner background tile is relevant)
#reduce speed if point in the bow of the ship is on sand:
        if (ai_ship.x - math.sin(math.radians(ai_ship.angle)) * ai_ship.width/3 - bgX < 5000 and
            ai_ship.y - math.cos(math.radians(ai_ship.angle)) * ai_ship.height/3 - bgY < 5000):
                if bg_links_oben.get_at(
                    (int(ai_ship.x - math.sin(math.radians(ai_ship.angle)) * ai_ship.width/3 - bgX),
                     int(ai_ship.y - math.cos(math.radians(ai_ship.angle)) * ai_ship.height/3 - bgY)))[2] < 140:

                        ai_ship.velocity = ai_ship.velocity * 0.7
                        ai_ship.rowing = False
                        
#set to zero if ship stands almost still (so it does not do little jumps on the sand)
                        if ai_ship.velocity < 0.1:
                            ai_ship.velocity = 0
    
#reduce "hit points", i.e. population of island by as much as the ship was carrying troops, if it is still big enough...
                            if ai_ship.troops < hit_points:
                                hit_points -= ai_ship.troops
                                ai_ship.troops = 0
#if there are more troups on the ship than population remaining on the island, game is over :(
                            else:
                                end_screen()
#ramming between ai ships and main ship:
#test distance between three points: middle, bow and stern
        if (dist((ai_ship.x, ai_ship.y), points3[4]) < ai_ship.width/2 or
            dist((ai_ship.x - math.sin(math.radians(ai_ship.angle)) * ai_ship.width/3, ai_ship.y - math.cos(math.radians(ai_ship.angle)) * ai_ship.height/3), points3[4]) < ai_ship.width/2 or
            dist((ai_ship.x + math.sin(math.radians(ai_ship.angle)) * ai_ship.width/3, ai_ship.y + math.cos(math.radians(ai_ship.angle)) * ai_ship.height/3), points3[4]) < ai_ship.width/2):
            
            ai_ship.crashing = True
            ai_ship.rowing = False
            ai_ship.velocity = 0
            if velocity1 > 0:
                velocity1 = velocity1 - 1  

        if ai_ship.destroyed == True:
            ai_ships.remove(ai_ship)
            del ai_ship

#5.4 final main ship velocity after everything happened
    velocity = 20/(1 + math.exp(- 0.2 * (velocity1))) - 10
    ship.angle = ship.angle + angle_dif

#translate the main ship vekocity to the shift of the coordinates of the background
    xSpeed = math.sin(math.radians(ship.angle)) * velocity
    ySpeed = math.cos(math.radians(ship.angle)) * velocity

#5.5 avoid main ship from going beyond the border of the map
    if bgX >= 0:
        xSpeed = min(xSpeed, 0)
    if - bgX >= bg_wasser.get_width() * len(bg[0]) - W - 5:
        xSpeed = max(xSpeed, 0)

    if bgY >= 0:
        ySpeed = min(xSpeed, 0)
    if - bgY >= bg_wasser.get_height() * len(bg) - H:
        ySpeed = max(xSpeed, 0)

#shift coordinates of background:
    bgX += xSpeed
    bgY += ySpeed

#count time in seconds:
    time += 1/clock.get_fps()

    clock.tick(fps)
    redrawWindow()

























