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
        self.reset()
        
    def reset(self):
        self.state = np.zeros((10,10))
        
    def get_num_actions(self):
        
        return self.num_actions
    
    def get_action_space(self):
        
        return self.actions
    
    def create_state(self, skier_position, angle):
        
        state = np.zeros(self.get_state_dimension() + 4 + self.get_num_actions())
        l = self.get_state_dimension()
        state = np.zeros(l + 4 + 1)
        state[0:l] = self.get_state().flatten()
        state[l:l+4] = skier_position
        state[l+4:] = angle
        
        return state
        
    
    def get_state_dimension(self):
        
        return self.state.flatten().shape[0]
    
    def get_state(self):
        
        return self.state
    
    def set_element_state(self, x,y,element):
        
        self.state[x,y] = element
        
    
    