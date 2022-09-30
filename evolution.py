import numpy as np


class Evolution():
    
    def __init__(self, initial_params, num_parents=10, mutation_prob=0.05, learning_rate=0.01,sigma=1):
        self.parents = num_parents
        self.mutation_prob = mutation_prob
        self.learning_rate = learning_rate
        self.sigma = sigma
        self.initial_params = initial_params
    
    def fitness(self, rewards):
        
        fitness = np.argmax(rewards, self.parents)
        
        return fitness
    
    def evolve(self, population, rewards, action_debrief):
        best_genes = np.argsort(rewards)[-self.parents:].flatten()
        
        num_params = self.initial_params.shape[0]
        new_genes = np.zeros((self.parents, self.initial_params.shape[1]), dtype=np.float32)
        
        i = 0
        for gene in best_genes:
            J = population[gene].get_params()
            new_genes[i] = J
            #print(i, rewards[gene], action_debrief[gene])
            i+=1
            
        R = new_genes.copy()
        m = R.mean()
        s = R.std()
        A = (R - m) / s
        N = np.random.randn(self.parents, num_params) ### MUTATION BASIS
        params = self.initial_params + self.learning_rate / (self.parents * self.sigma) * np.dot(N.T, A)
        
        self.initial_params = params
        
        return population