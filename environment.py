import numpy as np
class SnowboardEnvironment:
    
    actions = []
    def __init__(self) -> None:
        self.ACTION_LEFT  = -1
        self.ACTION_DOWN  = 0
        self.ACTION_RIGHT = 1
        self.SNOW   = 0
        self.DEAD   = 1
        self.TRAIT  = 2
        self.FLAG   = 3
        
        self.actions = [self.ACTION_LEFT, self.ACTION_DOWN, self.ACTION_RIGHT]
        self.num_actions = len(self.actions)
        
        self.state = np.zeros((10,10))
        
    def get_num_actions(self):
        
        return self.num_actions
    
    def get_state_dimension(self):
        
        return self.state.shape
    
    def get_state(self):
        
        return self.state
    
    def set_element_state(self, x,y,element):
        
        self.state[x,y] = element
        
    
    