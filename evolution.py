import numpy as np


class Evolution():
    
    def __init__(self, initial_params=2048, num_parents=10, mutation_prob=0.05, learning_rate=0.01,sigma=1):
        self.parents = num_parents
        self.mutation_prob = mutation_prob
        self.learning_rate = learning_rate
        self.sigma = sigma
        self.initial_params = initial_params
        
    
    def fitness(self, rewards):
        
        fitness = np.argmax(rewards, self.parents)
        
        return fitness
    
    def evolve(self, population, rewards):
        best_genes = np.argsort(rewards)[-self.parents:].flatten()
        
        num_params = len(self.initial_params)
        new_genes = []
        
        for gene in best_genes:
            new_genes.append(gene.get_params())
        
        R = np.array(new_genes)
        m = R.mean()
        s = R.std()
        A = (R - m) / s
        
        N = np.random.randn(self.parents, num_params) ### MUTATION BASIS
        
        params = params + self.learning_rate / (self.parents * self.sigma) * np.dot(N.T, A)
        
        print(rewards, population)
        
        return params