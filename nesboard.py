#!/usr/bin/env python
"""A Neural evolution based on SkiFree"""

# Source code taken from Warren Sande at
# http://www.manning-source.com/books/sande/All_Files_By_Chapter/hw_ch10_code/skiing_game.py
# Released under the MIT license http://www.opensource.org/licenses/mit-license.php

import pygame, sys, os, random
import numpy as np
import deap
from ANN import ANN2
from environment import SnowboardEnvironment
from evolution import Evolution

SKIER_LEFT  = 1
SKIER_NOTHING = 0
SKIER_RIGHT = 2

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
        self.is_alive = True
        
    def turn(self, direction):
        self.angle = self.angle + direction
        if self.angle < -2: self.angle = -2
        if self.angle >  2: self.angle =  2
        center = self.rect.center
        self.image = pygame.image.load(skier_images[self.angle])
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = [self.angle, self.speed[1] - abs(self.angle) * 2]
        self.energy-=2
        return self.speed
    
    def set_ANN(self, NN):
        self.ANN = NN
    
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
            type = random.choices(["tree", "flag", "trait", "ice", "plown"], weights=[5,3,1,0.5,0.5])[0]
            if type == "tree": 
                tr = random.randint(1,3)
                img = "images/pine_"+str(tr)+".png"
            elif type == "flag": 
                    img = "images/skier_flag.png"
            elif type == "trait":
                    tr = random.randint(2,5)
                    img = "images/reward_" + str(tr) + ".png"
            elif type == "ice":
                    tr = random.randint(2,5)
                    img = "images/ice.png"
            elif type == "plown":
                    tr = random.randint(2,5)
                    img = "images/plown.png"
            print(type, img)
            obstacle = ObstacleClass(img, location, type)
            obstacles.add(obstacle)
            
    for o in obstacles:
        
        V = environment.SNOW
        y = (o.location[0] - 20) // 64
        x = (o.location[1]  - 640 - 20)// 64
        #if y < 640:
        print(o.location, o.type)
        if o.type == "tree" or o.type=="plow" or o.type=="ice":
            V = environment.DEAD
        elif o.type == "trait":
                V = environment.TRAIT
        elif o.type == "flag":
                V = environment.FLAG
                
        environment.set_element_state(x, y, V)
        
    print("End create_map")

def animate():
    screen.fill([255, 255, 255])
    obstacles.draw(screen)
    for skier in skiers:
        if skier.is_alive:
            screen.blit(skier.image, skier.rect)
    screen.blit(score_text,  [ 10, 10])
    screen.blit(energy_text, [300, 10])
    pygame.display.flip()

def kill_skier(skier, hit=True):
    if hit:
        skier.image = pygame.image.load("images/skier_crash.jpg")
    animate()
    #pygame.time.delay(10)
    #results.append(skier)
    skier.kill() # MISSING SOME OVERLOADING
    skier.is_alive = False

def sample_action(sk, env, map_position, random=False):
    
    if not random:
        model = sk.ANN
        angle = sk.angle
        box = np.array(sk.rect)
        
        state = env.create_state( box, angle)
        
        action = np.argmax(model.forward(state))
    else:
        action = random.randint(0,2)
        
    return action

def refresh_environment(obstacles, environment):
    
    print("--------------------------")    
    environment.reset()
    for o in obstacles:
        
        V = environment.SNOW
        y = (o.location[0] - 20) // 64
        x = (o.location[1]  - 640 - 20)// 64
        #if y < 640:
        print(o.location, o.type)
        if o.type == "tree" or o.type=="plow" or o.type=="ice":
            V = environment.DEAD
        elif o.type == "trait":
                V = environment.TRAIT
        elif o.type == "flag":
                V = environment.FLAG
                
        environment.set_element_state(x, y, V)

    return environment

def main(generation, num_skiers=44, training=False):
    global screen
    global obstacles
    global skiers
    global score_text
    global energy_text
    global scroll_speed
    global results
    
    pygame.init()
    screen = pygame.display.set_mode([640, 640])
    clock = pygame.time.Clock()
    skiers  = []
    results = []
    
    for i in range(num_skiers):
        skier = SkierClass()
        skier.set_ANN(generation[i])
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

        #environment = refresh_environment(obstacles, environment)
        best_score = 0
        best_energy = 0
        
        alive_skiers=0
        for i in range(0, len(skiers)):
            skier = skiers[i]
            if skier.is_alive:
                alive_skiers+=1
                if skier.energy > best_energy:
                    best_energy = skier.energy
                if skier.score > best_score:
                    best_score = skier.score
                action = sample_action(skier, environment, map_position)
                if action == SKIER_LEFT:
                    skier.turn(-1)
                elif action == SKIER_RIGHT:
                    skier.turn(1)
                skier.move()
                hit = pygame.sprite.spritecollide(skier, obstacles, False)
                if skier.energy <= 0:
                    kill_skier(skier, hit=False)
                if hit:
                    if hit[0].type == "tree" or hit[0].type == "ice" or hit[0].type == "plown":
                        kill_skier(skier, hit=True)
                        
                    elif hit[0].type == "flag":
                        skier.score += points
                        if not training:
                            hit[0].kill()
                        
                    elif hit[0].type == "trait":
                        skier.energy += 10
                        if skier.energy > initial_energy:
                            skier.energy = initial_energy
                        if not training:
                            hit[0].kill()
                skier.score+=1
                skier.energy -=1
        
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
            if not training:
                while True:
                    clock.tick(20)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: sys.exit()
            else:
                running = False
            
        obstacles.update()
        score_text  = font.render("Best score: " + str(best_score), 1, (0, 0, 0))
        energy_text = font.render("Energy: " + str(best_energy), 1, (0, 0, 0))
        scroll_speed+=1e-2
        points = int(scroll_speed / start_speed)
        animate()
        
    rewards = []
    for skier in skiers:
        rewards.append(skier.score)
    return rewards 

if __name__ == "__main__":
    training = True
    
    evolution = Evolution(num_parents=10, mutation_prob=0.05)

    environment = SnowboardEnvironment()
    D = environment.get_state_dimension() + 5
    M1 = 32
    M2 = 96
    K = environment.get_num_actions()
    action_max = environment.get_num_actions()
    
    generation = []
    num_subjects = 100
    for i in range(num_subjects):
        nn = ANN2(D, M1, M2, K, action_max)
        nn.init()
        generation.append(nn)
    
    done = False
    i = 0
    while not done:
        rewards = main(generation, num_skiers=num_subjects, training=True)
        
        generation = evolution.evolve(generation, rewards)
        if i > 10:
            break
        i+=1
        
    pygame.quit()