import random
import time
import copy
import ConfigParser
from monster import Monster
from twisted.internet import task
import ConfigParser

class MonsterSpawn:


  def __init__(self, name, x, y, w, h, zone, spawn_max, spawn_delay, world):
    
    self.name        = name
    self.x           = x
    self.y           = y
    self.w           = w
    self.h           = h
    self.zone        = zone
    self.spawn_max   = spawn_max
    self.spawn_delay = spawn_delay
    self.world       = world
    self.spawn_count = 0

    # Schedule update task
    self.spawn_task = task.LoopingCall(self.spawn)
    self.spawn_task.start(self.spawn_delay, now=False)
 
  def spawn(self):

    if self.spawn_count < self.spawn_max:
      x = random.randint(self.x, self.x + self.w)
      y = random.randint(self.y, self.y + self.h)
      
      # Create monster
      Monster(self.name, x, y, self.zone, self.world, self)
      
      self.spawn_count += 1
  
