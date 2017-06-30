import time
import random
import ConfigParser
from item import Item
from twisted.internet import task, reactor


def load_players(world, x, y, zone):

  pconfig = ConfigParser.RawConfigParser()
  pconfig.read('server_data/players.ini')
  
  iconfig = ConfigParser.RawConfigParser()
  iconfig.read('server_data/items.ini')
  
  
  for name in pconfig.sections():
    level = pconfig.getint(name, 'level')
    exp = pconfig.getint(name, 'exp')
    title = pconfig.get(name,'title')
    gender = pconfig.get(name,'gender')
    body = pconfig.get(name,'body')
    hairstyle = pconfig.get(name,'hairstyle')
    haircolor = pconfig.get(name,'haircolor')
    spells = pconfig.get(name,'spells').split(',')
    hp = pconfig.getint(name,'hp')
    mp = pconfig.getint(name,'mp')
    hit = pconfig.getint(name,'hit')
    dam = pconfig.getint(name,'dam')
    arm = pconfig.getint(name,'arm')
    password = pconfig.get(name,'password')
    items = pconfig.get(name,'items')
    if items:
      items = items.split(',')
    spells = pconfig.get(name,'spells')
    if spells:
      spells = spells.split(',')
    
    world.players[name] = Player(name, title, level, exp, gender, body, hairstyle, haircolor, password, x, y, zone, spells, hp, mp, hit, dam, arm, world)  
    print items
    # Load player items
    for iname in items:
      Item(iname, player=name, container=None, equipped=False, world=world)

class Player:

  levels = [ 0, 100, 200, 400, 800, 1600, 3200, 6400, 12800 ]


  def __init__(self, name, title, level, exp, gender, body, hairstyle, haircolor, password, x, y, zone, spells, hp, mp, hit, dam, arm, world):

    self.title = title
    self.name = name
    self.level = level
    self.exp = exp
    self.x = x
    self.y = y
    self.zone = zone
    self.online = False
    self.password = password
    self.target = None
    self.fighting = False
    self.spells = spells # list of spells known by this player
    self.running = False
    self.hp = [ hp, hp ]
    self.mp = [ mp, mp ]
    self.hit = hit
    self.dam = dam
    self.arm = arm
    self.gold = 0
    self.mode = 'wait' # wait, running, fighting, casting, dead
    self.direction = 'south'
    self.world = world
    self.path = []
    self.gender = gender
    self.hairstyle = hairstyle
    self.haircolor = haircolor
    self.body = body

    # Schedule update task
    self.update_task = task.LoopingCall(self.update)
    self.update_task.start(1.0)
    
    # Schedule pathfollow task
    self.pathfollow_task = task.LoopingCall(self.pathfollow)
    self.pathfollow_task.start(0.25)
  
    self.ready_to_attack = True
   
   
    self.quests = {}
    
    print "Loaded PLAYER",self.state()

  def unload(self):
    self.update_task.stop()
    self.pathfollow_task.stop()

  def state(self):
    
    armor = 'clothes'
    weapon = 'unarmed'
    head = 'none'
    # Get armor type
    for item in self.world.items.values():
      if item.player == self.name and item.equipped == 1:
        if item.slot == 'armor':
          armor = item.gear_type
        elif item.slot == 'weapon':
          weapon = item.gear_type
        elif item.slot == 'head':
          head = item.gear_type

    return { 'title': self.title,
             'name': self.name, 
             'gender': self.gender, 
             'body': self.body, 
             'hairstyle': self.hairstyle, 
             'haircolor': self.haircolor, 
             'armor': armor, 
             'head': head, 
             'weapon': weapon, 
             'x': self.x, 
             'y': self.y, 
             'zone': self.zone, }

  def take_damage(self, attacker, damage):

    if not self.target:
      self.target = attacker

    self.hp[0] -= damage
    
    if self.hp[0] < 0:
      self.hp[0] = 0

    self.world.events.append(self.world.player_stats(self.name))

  def warp(self, zone, x, y):
    # Drop player
    self.world.events.append({ 'type': 'dropplayer', 'name': self.name, 'zone': self.zone })
    
    self.x = x
    self.y = y
    self.zone = zone
    self.path = []
  
    # Add player back 
    event = { 'type': 'addplayer' }
    event.update(self.state())
    self.world.events.append(event)
     
    # Tell client to refresh
    event = self.world.refresh(self.name)
    event['zone'] = "player_%s" % self.name
    self.world.events.append(event)

  def pathfollow(self):
    
    if self.path:
      self.mode = 'running'
      dest = self.path.pop(0)
      
      if dest[0] > self.x:
        self.direction = 'east'
      elif dest[0] < self.x:
        self.direction = 'west'
      
      if dest[1] > self.y:
        self.direction = 'north'
      elif dest[1] < self.y:
        self.direction = 'south'  
      
      #self.world.events.append({ 'type': 'playermove', 'name': self.name, 'zone': self.zone, 'direction': self.direction, 'start': (self.x,self.y), 'end': dest })
      self.x = dest[0]
      self.y = dest[1]
      
      # set mode to waiting if path is now empty
      if not self.path:
        self.mode = 'wait'

  def update(self):
    
    if not self.online:
      return

    # Set player level
    if self.exp >= (self.level**2 * 100):
      self.level += 1
      self.world.events.append({ 'type': 'message', 'name': self.name, 'zone': self.zone, 'message': "%s has reached level %s" % (self.title, self.level)})

      # reward some stats
      self.hp[1] += int(self.level * 1.5)
      self.mp[1] += int(self.level * 1.5)
      self.arm = int(self.level * 1.5)
      self.dam = int(self.level * 1.5)
      self.hit = int(self.level * 1.5)



    if self.hp[0] < 1:
      if self.mode != 'dead':
        self.mode = 'dead'
        self.world.events.append({ 'type': 'playerdie', 'name': self.name, 'title': self.title, 'zone': self.zone })
        reactor.callLater(3.0, self.world.respawn_player, self)

    # Are we on a warp tile?
    for warp in self.world.warps:
      if warp.start_x == self.x and warp.start_y == self.y and warp.start_zone == self.zone:
        self.warp(warp.end_zone,warp.end_x,warp.end_y)
   
   
    # Are we on the edge of the map? Then warp
    zone = self.world.zones[self.zone]
    if self.x == 0:
      # Warp west
      if zone.borders['west']:
        if self.world.zones[zone.borders['west']]:
          end_zone = self.world.zones[zone.borders['west']]
          if end_zone:
            end_x = end_zone.width - 2
            end_y = self.y
            self.path = []
            self.warp(end_zone.name, end_x, end_y)

    elif self.x == zone.width - 1:
      # Warp east
      if zone.borders['east']:
        if self.world.zones[zone.borders['east']]:
          end_zone = self.world.zones[zone.borders['east']]
          if end_zone:
            end_x = 1
            end_y = self.y
            self.path = []
            self.warp(end_zone.name, end_x, end_y)
    
    elif self.y == 0:
      # Warp south
      if zone.borders['south']:
        if self.world.zones[zone.borders['south']]:
          end_zone = self.world.zones[zone.borders['south']]
          if end_zone:
            end_x = self.x
            end_y = end_zone.height - 2
            self.path = []
            self.warp(end_zone.name, end_x, end_y)
    
    elif self.y == zone.height - 1:
      # Warp north
      if zone.borders['north']:
        if self.world.zones[zone.borders['north']]:
          end_zone = self.world.zones[zone.borders['north']]
          if end_zone:
            end_x = self.x
            end_y = 1
            self.path = []
            self.warp(end_zone.name, end_x, end_y)

    if self.mode == 'wait':
      # heal 5% per second while waiting
      if self.hp[0] < self.hp[1]:
        self.hp[0] += self.hp[1]/20 + 1
      if self.mp[0] < self.mp[1]:
        self.mp[0] += self.mp[1]/20 + 1

      # but dont go over!
      if self.hp[0] > self.hp[1]:
        self.hp[0] = self.hp[1]
      if self.mp[0] > self.mp[1]:
        self.mp[0] = self.mp[1]

    elif self.mode == 'fighting':
      
      if self.target is None:
        self.mode = 'wait'
        return
      
      if self.target.mode == 'dead':
        self.mode = 'wait'
        self.target = None
        return
      
      if self.ready_to_attack:
        self.attack()
        
    elif self.mode == 'casting':
      pass
    
    elif self.mode == 'dead':
      self.path = []
      self.target = None

  def attack(self):
    self.ready_to_attack = False

    tohit  = random.randint(1,20) + self.world.get_player_hit(self.name)
    damage = random.randint(1, self.world.get_player_dam(self.name))
    attack = self.world.get_player_attack_type(self.name)

    if tohit >= self.target.arm:
      # It's a hit
      self.world.events.append({'type': 'player'+attack, 'name': self.name, 'dam': damage, 'target': self.target.name, 'zone': self.zone, 'target_title': self.target.title })
      self.target.take_damage(self,damage)
    
    attack_speed = self.world.get_player_attack_speed(self.name)
    reactor.callLater(attack_speed, self.reset_attack)

  def reset_attack(self):
    self.ready_to_attack = True
