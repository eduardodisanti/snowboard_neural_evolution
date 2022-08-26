#!/usr/bin/env python
"""A Neural evolution based on SkiFree"""

# Source code taken from Warren Sande at
# http://www.manning-source.com/books/sande/All_Files_By_Chapter/hw_ch10_code/skiing_game.py
# Released under the MIT license http://www.opensource.org/licenses/mit-license.php

import pygame, sys, os, random
from environment import SnowboardEnvironment

SKIER_LEFT  = 0
SKIER_RIGHT = 1

initial_energy = 300

skier_images = ["images/skier_down.png",
                "images/snowboarder_right1.png",
                "images/snowboarder_right2.png",
                "images/snowboarder_left2.png",
                "images/snowboarder_left1.png"]

try:
    if os.environ["USER"]:
        player = os.environ["USER"]
    else:
        player = os.environ["LOGNAME"]
except KeyError:
    player = os.environ["LOGNAME"]
    
start_speed = 10


class SkierClass(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/skier_down.png")
        self.rect = self.image.get_rect()
        self.rect.center = [random.randint(20, 620), 100]
        self.angle = 0
        self.score = 0
        self.energy = initial_energy
        self.speed = [0, start_speed]
        
    def turn(self, direction):
        self.angle = self.angle + direction
        if self.angle < -2: self.angle = -2
        if self.angle >  2: self.angle =  2
        center = self.rect.center
        self.image = pygame.image.load(skier_images[self.angle])
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = [self.angle, self.speed[1] - abs(self.angle) * 2]
        self.energy-=1
        return self.speed
    
    def move(self):
        self.rect.centerx = self.rect.centerx + self.speed[0]*2
        if self.rect.centerx < 20:  self.rect.centerx = 20
        if self.rect.centerx > 620: self.rect.centerx = 620
        
class ObstacleClass(pygame.sprite.Sprite):
    def __init__(self, image_file, location, type):
        pygame.sprite.Sprite.__init__(self)
        self.image_file = image_file
        self.image = pygame.image.load(image_file)
        self.location = location
        self.rect = self.image.get_rect()
        self.rect.center = location
        self.type = type
    
    def update(self):
        self.rect.centery -= scroll_speed
        if self.rect.centery < -32:
            self.kill()

def create_map(environment):
    global obstacles
    locations = []
    for _ in range(10):
        row = random.randint(0, 9)
        col = random.randint(0, 9)
        location = [col * 64 + 20, row * 64 + 20 + 640]
        if not (location in locations):
            locations.append(location)
            type = random.choices(["tree", "flag", "trait", "ice", "plown"], weights=[6,2,1,0.5,0.5])[0]
            if type == "tree": 
                tr = random.randint(1,3)
                img = "images/pine_"+str(tr)+".png"
                environment.set_element_state(row,col, environment.DEAD)
            elif type == "flag": 
                    img = "images/skier_flag.png"
                    environment.set_element_state(row,col, environment.FLAG)
            elif type == "trait":
                    tr = random.randint(2,5)
                    img = "images/reward_" + str(tr) + ".png"
                    environment.set_element_state(row,col, environment.TRAIT)
            elif type == "ice":
                    tr = random.randint(2,5)
                    img = "images/ice.png"
                    environment.set_element_state(row,col, environment.DEAD)
            elif type == "plown":
                    tr = random.randint(2,5)
                    img = "images/plown.png"
                    environment.set_element_state(row,col, environment.DEAD)
            print(type, img)
            obstacle = ObstacleClass(img, location, type)
            obstacles.add(obstacle)

def animate():
    screen.fill([255, 255, 255])
    obstacles.draw(screen)
    for skier in skiers:
        screen.blit(skier.image, skier.rect)
    screen.blit(score_text,  [ 10, 10])
    screen.blit(energy_text, [300, 10])
    pygame.display.flip()

def sample_action(sk):
    
    return random.randint(0,2)

def kill_skier(skier, hit=True):
    if hit:
        skier.image = pygame.image.load("images/skier_crash.jpg")
    animate()
    #pygame.time.delay(10)
    skiers.remove(skier)
    skier.kill()

def main(training = False):
    global screen
    global obstacles
    global skiers
    global score_text
    global energy_text
    global scroll_speed
    
    num_skiers = 44
    pygame.init()
    screen = pygame.display.set_mode([640, 640])
    clock = pygame.time.Clock()
    skiers = []
    
    environment = SnowboardEnvironment()
    
    for _ in range(num_skiers):
        skier = SkierClass()
        skiers.append(skier)
    
    start_speed = 20
    scroll_speed = start_speed
    obstacles = pygame.sprite.Group()
    map_position = 0
    points = 0
    create_map(environment)
    font = pygame.font.Font(None, 50)
    
    running = True
    while running:
        clock.tick(int(scroll_speed))
        for event in pygame.event.get():
            skier = skiers[0]
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    skier.speed = skier.turn(-1)
                elif event.key == pygame.K_RIGHT:
                    skier.speed = skier.turn(1)
        skier.move()
        
        map_position += scroll_speed
        
        if map_position >= 640:
            create_map(environment)
            map_position = 0

        best_score = 0
        best_energy = 0
        for skier in skiers:
            if skier.energy > best_energy:
                best_energy = skier.energy
            if skier.score > best_score:
                best_score = skier.score
            action = sample_action(skier)
            if action == SKIER_LEFT:
                skier.turn(-1)
            elif action == SKIER_RIGHT:
                skier.turn(1)
            skier.move()
            hit = pygame.sprite.spritecollide(skier, obstacles, False)
            if skier.energy <= 0:
                kill_skier(skier, hit=False)
            if hit:
                x = (hit[0].location[0] - 20)//64
                y = (hit[0].location[1] - 640 - 20)//64

                if hit[0].type == "tree" or hit[0].type == "ice" or hit[0].type == "plown":
                    kill_skier(skier, hit=True)
                    
                elif hit[0].type == "flag":
                    skier.score += points
                    if not training:
                        environment.set_element_state(x,y, environment.SNOW)
                    
                elif hit[0].type == "trait":
                    skier.energy += 10
                    if skier.energy > initial_energy:
                        skier.energy = initial_energy
                    if not training:
                        hit[0].kill()
                    environment.set_element_state(x,y, environment.SNOW)
            skier.score+=1
            
        alive_skiers= len(skiers)
        if alive_skiers==0:
            pygame.time.delay(1000)
            screen.fill([255, 255, 255])
            game_over = font.render("Game Over!", 1, (0, 0, 0))
            scores_rows = []
            scores_table = []
            for row in scores_rows:
                scores_table.append(row.split(":"))
            for i in range(len(scores_table)):
                high_player = "{}. {:.<100}".format(i + 1, scores_table[i][0])
                high_score = "{}  ".format(scores_table[i][1])
                high_player_surf = font.render(high_player, 1, (0, 0, 0))
                high_score_surf = font.render(high_score, 1, (0, 0, 0), (255, 255, 255))
                screen.blit(high_player_surf, [20, 250 + 50 * i])
                screen.blit(high_score_surf, [640 - high_score_surf.get_width(), 250 + 50 * i])
            table_header = font.render("High Scores:", 1, (0, 0, 0))
            screen.blit(table_header, [20, 170])    
            screen.blit(score_text, [20, 70])
            screen.blit(game_over, [20, 20])
            pygame.display.flip()
            while True:
                clock.tick(20)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: sys.exit()
            
        obstacles.update()
        score_text  = font.render("Best score: " + str(best_score), 1, (0, 0, 0))
        energy_text = font.render("Energy: " + str(best_energy), 1, (0, 0, 0))
        scroll_speed+=1e-2
        points = int(scroll_speed / start_speed)
        animate()

if __name__ == "__main__":
    training = True
    main(training)
    pygame.quit()