import time
import random
import ConfigParser
from twisted.internet import task, reactor

class Monster:
  
  config = ConfigParser.RawConfigParser()
  config.read('server_data/monsters.ini')
  index = 0

  def getid(self):
    
    Monster.index += 1
    return Monster.index

  def __init__(self, name, x, y, zone, world, spawn):
    
    self.name   = "%s-%s" % (name, self.getid())
    self.world  = world
    self.x      = x
    self.y      = y
    self.zone   = zone
    self.spawn  = spawn

    self.title  = Monster.config.get(name,'title')
    self.level  = Monster.config.getint(name, 'level')
    self.source = Monster.config.get(name,'source')
    self.hp     = [ Monster.config.getint(name, 'hp'), Monster.config.getint(name,'hp') ]
    self.hit    = Monster.config.getint(name, 'hit')
    self.arm    = Monster.config.getint(name, 'dam')
    self.dam    = Monster.config.getint(name, 'arm')
    self.mode   = Monster.config.get(name, 'mode')
    self.loot   = Monster.config.get(name, 'loot')
    
    self.attack_speed  = Monster.config.getfloat(name, 'speed')

    self.target = None

    self.ready_to_attack = True

    self.update_task = task.LoopingCall(self.update)
    self.update_task.start(1.0)

    self.world.monsters[self.name] = self
    
    self.world.events.append({ 'type':   'addmonster', 
                               'source': self.source, 
                               'title':  self.title,
                               'name':   self.name, 
                               'x':      self.x, 
                               'y':      self.y, 
                               'zone':   self.zone })

  def unload(self):
    self.update_task.stop()

  def state(self):

    return { 'title': self.title, 'source': self.source, 'name': self.name, 'x': self.x, 'y': self.y, 'zone': self.zone, }

  def take_damage(self, attacker, damage):

    if not self.target:
      self.target = attacker
    
    if self.mode in [ 'wander', 'wait' ]:
      self.mode = 'fighting'
    
    self.hp[0] -= damage

  def update(self):
    
    # Are we dead:
    if self.hp[0] < 1:
      if self.mode != 'dead':
        self.mode = 'dead'
        self.world.events.append({ 'type': 'monsterdie', 'name': self.name, 'title': self.title, 'zone': self.zone })
        reactor.callLater(2.0, self.world.cleanup_monster, self)

    if self.mode == 'wait':
      # heal 10% per second while waiting
      if self.hp[0] < self.hp[1]:
        self.hp[0] += self.hp[1]/10
      # but dont go over!
      if self.hp[0] > self.hp[1]:
        self.hp[0] = self.hp[1]

      if self.hp[0] == self.hp[1]:
        self.mode = 'wander'

    elif self.mode == 'wander':
      if random.random() > 0.10:
        return

      direction = 'south'
      x = random.randint(-1,1)
      y = 0
      if x > 0:
        direction = 'east'
      elif x < 0:
        direction = 'west'
      elif x == 0:
        y = random.randint(-1,1)
        if y > 0:
          direction = 'north'
        if y < 0:
          direction = 'south'
      
      if x == 0 and y == 0:
        return

      if not self.world.zones[self.zone].open_at(self.x + x, self.y + y):
        return
      
      self.world.events.append({'type': 'monstermove', 'speed': 'slow', 'name': self.name, 'zone': self.zone, 'direction': direction, 'start': (self.x,self.y), 'end': (self.x + x, self.y + y)})
      self.x += x
      self.y += y
    
    elif self.mode == 'fighting':
      if not self.target:
        self.mode = 'wait'
        return
      
      if self.target.mode == 'dead':
        self.mode = 'wait'
        self.target = None
        return
      
      # Are we in range of target
      if not self.world.in_attack_range(self,self.target):
        self.mode = 'chase'
        return
      else:
        self.path = []
     
      if self.ready_to_attack:
        self.attack() 
    
    elif self.mode == 'chase':
      # Move toward target
      
      if not self.target:
        self.mode = 'wait'
        return

      if self.target.mode == 'dead':
        self.mode = 'wait'
        self.target = None
        return

      if self.world.in_attack_range(self,self.target):
        self.mode = 'fighting'
        return
     
      # get path to target
      self.path = self.world.zones[self.zone].get_path((self.x,self.y),(self.target.x,self.target.y))

      # stop right in front of target, not on top of him
      del self.path[-1]

      self.mode = 'pathfollow'

    elif self.mode == 'dead':
      pass

    elif self.mode == 'wait':
      if self.path:
        self.mode = 'pathfollow'
        return

      if self.target:
        self.mode = 'fighting'
        return

    elif self.mode == 'pathfollow':
      if not self.path:
        self.mode = 'wait'
        return

      dest = self.path.pop(0)
      
      if dest[0] > self.x:
        self.direction = 'east'
      elif dest[0] < self.x:
        self.direction = 'west'
      
      if dest[1] > self.y:
        self.direction = 'north'
      elif dest[1] < self.y:
        self.direction = 'south'  
      
      self.world.events.append({ 'type': 'monstermove', 'speed': 'fast', 'name': self.name, 'zone': self.zone, 'direction': self.direction, 'start': (self.x,self.y), 'end': dest })
      self.x = dest[0]
      self.y = dest[1]
      
      # set mode to waiting if path is now empty
      if not self.path:
        self.mode = 'wait'

  def attack(self):
    self.ready_to_attack = False
    
    tohit  = random.randint(1,20) + self.hit
    damage = random.randint(1, self.dam)

    player_arm = self.world.get_player_arm(self.target.name)

    if tohit > player_arm:
      # It's a hit
      self.world.events.append({'type': 'monsterattack', 'name': self.name, 'dam': damage, 'target': self.target.name, 'zone': self.zone, 'title': self.title, 'target_title': self.target.title })
      self.target.take_damage(self,damage)
    
    reactor.callLater(self.attack_speed, self.reset_attack)

  def reset_attack(self):
    self.ready_to_attack = True
