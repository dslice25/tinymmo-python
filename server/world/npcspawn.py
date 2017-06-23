import random
import time
import copy
from npc import Npc
from twisted.internet import task
import ConfigParser

class NpcSpawn:


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
      
      # Create npc
      Npc(self.name, x, y, self.zone, self.world, self)
      
      self.spawn_count += 1
  
#class NpcSpawn:
#
#  npc_index = 0
#
#  def __init__(self, name, x, y, zone, spawn_max, spawn_delay, world):
#
#    # Load monster from data/monsters.ini
#    config = ConfigParser.RawConfigParser()
#    config.read('data/npcs.ini')
#
#    self.name = name
#    self.title = config.get(name, 'title')
#    self.x = x
#    self.y = y
#    self.zone = zone
#    self.spawn_delay = spawn_delay
#    self.spawn_max = spawn_max
#    self.spawn_count = 0
#    self.world = world
#    hp = config.getint(name, 'hp')
#    self.hp = [ hp, hp ]
#    mp = config.getint(name, 'mp')
#    self.mp = [ mp, mp ]
#    self.hit = config.getint(name, 'hit')
#    self.arm = config.getint(name, 'arm')
#    self.dam = config.getint(name, 'dam')
#    
#    self.gender = config.get(name, 'gender')
#    self.body = config.get(name, 'body')
#    self.hairstyle = config.get(name, 'hairstyle')
#    self.haircolor = config.get(name, 'haircolor')
#    self.armor = config.get(name, 'armor')
#    self.head = config.get(name, 'head')
#    self.weapon = config.get(name, 'weapon')
#
#    self.shop = config.get(name, 'shop')
#    self.quest = config.get(name, 'quest')
#    self.villan = config.getboolean(name, 'villan')
#    self.mode = config.get(name, 'mode')
#    
#    # spawn, title, x, y, zone, hp, mp, hit, arm, dam
#    self.build_hash = { 'gender': self.gender,
#                        'body': self.body, 
#                        'hairstyle': self.hairstyle,
#                        'haircolor': self.haircolor,
#                        'armor': self.armor,
#                        'head': self.head,
#                        'weapon': self.weapon,
#                        'title': self.title,
#                        'x': self.x,
#                        'y': self.y,
#                        'zone': self.zone,
#                        'hp': self.hp,
#                        'mp': self.dam,
#                        'hit': self.hit,
#                        'dam': self.dam,
#                        'arm': self.arm,
#                        'shop': self.shop,
#                        'quest': self.quest,
#                        'villan': self.villan,
#                        'mode': self.mode, }
#
#    # Schedule update task
#    self.spawn_task = task.LoopingCall(self.spawn)
#    self.spawn_task.start(self.spawn_delay, now=False)
#    
#  def spawn(self):
#
#    if self.spawn_count < self.spawn_max:
#      name = "%s-%s" % (self.name, self.npc_index)
#      self.npc_index += 1
#
#      self.world.npcs[name] = Npc(name=name, spawn=self, world=self.world, **copy.deepcopy(self.build_hash))
#      self.spawn_count += 1
#
#      self.world.events.append({ 'type': 'addnpc', 'gender': self.gender, 'body': self.body, 'hairstyle': self.hairstyle, 'haircolor': self.haircolor, 'armor': self.armor, 'head': self.head, 'weapon': self.weapon, 'title': self.title, 'name': name, 'x': self.x, 'y': self.y, 'zone': self.zone, 'villan': self.villan })
