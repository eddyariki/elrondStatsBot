import time
import json



class Order:
    #A class that manages large orders in memory
    def __init__(self, id, maxLife):
        self.id = str(id)
        self.birth = time.time()
        self.maxLife = maxLife
    
    def checkLife(self):
        life = time.time() - self.birth
        return life < self.maxLife*60
    def __str__(self):
        return self.id
    def __repr__(self):
        return self.id
    
