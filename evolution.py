import numpy as np


class Evolution():
    
    def __init__(self, num_parents=10, mutation_prob=0.05):
        self.parents = num_parents
        self.mutation_prob = mutation_prob
        
    
    def fitness(self, rewards):
        
        fitness = np.argmax(rewards, self.parents)
        
        return fitness
    
    def evolve(self, population, rewards):
        
        print(rewards, population)