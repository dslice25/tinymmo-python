import time
import random
import ConfigParser
from twisted.internet import task, reactor

class Npc:

  config = ConfigParser.RawConfigParser()
  config.read('server_data/npcs.ini')
  index  = 0

  def getid(self):
    
    Npc.index += 1
    return Npc.index

  def __init__(self, name, x, y, zone, world, spawn):

    self.name  = "%s-%s" % (name, self.getid())
    self.x     = x
    self.y     = y
    self.zone  = zone
    self.world = world
    self.spawn = spawn

    self.title     = Npc.config.get(name, 'title')
    self.hp        = [ Npc.config.getint(name, 'hp'), Npc.config.getint(name, 'hp') ]
    self.mp        = [ Npc.config.getint(name, 'mp'), Npc.config.getint(name, 'mp') ]
    self.level     = Npc.config.getint(name, 'level')
    self.hit       = Npc.config.getint(name, 'hit')
    self.dam       = Npc.config.getint(name, 'dam')
    self.arm       = Npc.config.getint(name, 'arm')
    self.mode      = Npc.config.get(name, 'mode')
    self.gender    = Npc.config.get(name, 'gender')
    self.body      = Npc.config.get(name, 'body')
    self.hairstyle = Npc.config.get(name, 'hairstyle')
    self.haircolor = Npc.config.get(name, 'haircolor')
    self.armor     = Npc.config.get(name, 'armor')
    self.head      = Npc.config.get(name, 'head')
    self.weapon    = Npc.config.get(name, 'weapon')
    self.shop      = Npc.config.get(name, 'shop')
    self.quest     = Npc.config.get(name, 'quest')
    self.villan    = Npc.config.getboolean(name, 'villan')
    self.loot      = Npc.config.get(name, 'loot')
    self.attack_speed = Npc.config.getfloat(name, 'speed')
      
    self.attack_type = 'slash'
    self.target      = None 
    self.path        = []

    self.ready_to_attack = True
    
    if self.weapon in [ 'sword', 'wand' ]:
      self.attack_type = 'slash'
    elif self.weapon in [ 'spear' ]:
      self.attack_type = 'thrust'
    elif self.weapon in [ 'bow' ]:
      self.attack_type = 'bow'
    
    self.update_task = task.LoopingCall(self.update)
    self.update_task.start(1.0)

    self.world.npcs[self.name] = self
      
    self.world.events.append({ 'type': 'addnpc', 'gender': self.gender, 'body': self.body, 'hairstyle': self.hairstyle, 'haircolor': self.haircolor, 'armor': self.armor, 'head': self.head, 'weapon': self.weapon, 'title': self.title, 'name': self.name, 'x': self.x, 'y': self.y, 'zone': self.zone, 'villan': self.villan })

  def unload(self):
    self.update_task.stop()

  def state(self):
    
    return { 'title': self.title,
             'name': self.name, 
             'gender': self.gender, 
             'body': self.body, 
             'hairstyle': self.hairstyle,
             'haircolor': self.haircolor,
             'armor': self.armor,
             'head': self.head,
             'weapon': self.weapon,
             'x': self.x, 
             'y': self.y, 
             'zone': self.zone,
             'villan': self.villan, }
  
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
        self.world.events.append({ 'type': 'npcdie', 'name': self.name, 'title': self.title, 'zone': self.zone })
        reactor.callLater(2.0, self.world.cleanup_npc, self)

    if self.mode == 'wait':
      # heal 10% per second while waiting
      if self.hp[0] < self.hp[1]:
        self.hp[0] += self.hp[1]/10
      if self.mp[0] < self.mp[1]:
        self.mp[0] += self.mp[1]/10
      # but dont go over!
      if self.hp[0] > self.hp[1]:
        self.hp[0] = self.hp[1]
      if self.mp[0] > self.mp[1]:
        self.mp[0] = self.mp[1]

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
      
      self.world.events.append({'type': 'npcmove', 'speed': 'slow', 'name': self.name, 'zone': self.zone, 'direction': direction, 'start': (self.x,self.y), 'end': (self.x + x, self.y + y)})
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
      
    elif self.mode == 'dead':
      pass

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
      
      self.world.events.append({ 'type': 'npcmove', 'speed': 'fast', 'name': self.name, 'zone': self.zone, 'direction': self.direction, 'start': (self.x,self.y), 'end': dest })
      self.x = dest[0]
      self.y = dest[1]
      
      # set mode to waiting if path is now empty
      if not self.path:
        self.mode = 'wait'

  def attack(self):
    self.ready_to_attack = False
    
    tohit  = random.randint(1,20) + self.hit
    damage = random.randint(1, self.dam)
    arm    = 0
      
    if self.target.__class__.__name__ == 'Player':
      arm = self.world.get_player_arm(self.target.name)
    else:
      arm = self.target.arm

    if tohit >= arm:
      # It's a hit
      self.world.events.append({'type': 'npc'+self.attack_type, 'name': self.name, 'dam': damage, 'target': self.target.name, 'zone': self.zone, 'title': self.title, 'target_title': self.target.title })
      self.target.take_damage(self,damage)
    
    reactor.callLater(self.attack_speed, self.reset_attack)

  def reset_attack(self):
    self.ready_to_attack = True
