import pyglet
from pytmx.util_pyglet import load_pyglet
from player import Player
from monster import Monster
from npc import Npc
from container import Container

from twisted.internet import task

import pprint

class Game:

  def __init__(self):
    
    self.player_name = None
    self.zone = None
    self.players = {}
    self.monsters = {}
    self.player_target = None
    self.spells = []
    self.npcs = {}
    self.containers = {}
    self.player_inventory = []
    
    # Zone file cache 
    self.zones = {}

  def load(self, player_name, zone_source, players, monsters, npcs, containers, zone_data):
    
    # unload monsters
    for m in self.monsters.values():
      m.unload()
    
    for p in self.players.values():
      p.unload()

    for n in self.npcs.values():
      n.unload()
    
    for s in self.spells:
      s.unload()
     
    # Load zone and save to cache
    if not self.zones.has_key(zone_source):
      
      # write zone_data to zone_source
      with open('client_data/zones/' + zone_source,'w') as tmxfile:
        tmxfile.write(zone_data)
       
      self.zones[zone_source] = load_pyglet('client_data/zones/' + zone_source)
      self.zone = self.zones[zone_source]
    
      for layer in self.zone.layers:
        print layer
        if layer.name == 'character' or layer.name == 'blocked' or layer.name == 'block' or layer.name == 'spawns':
          pass
        else:
          layer.batch = pyglet.graphics.Batch()
          layer.sprites = []
          for x, y, image in layer.tiles():
            y = self.zone.height - y - 1
            sprite = pyglet.sprite.Sprite(image, x * self.zone.tilewidth, y * self.zone.tileheight, batch=layer.batch)
            layer.sprites.append(sprite)
    else:
      # Set zone from cache
      self.zone = self.zones[zone_source]
    
    self.player_name = player_name
    self.players = {}
    self.monsters = {}
    self.npcs = {}
    self.containers = {}
    self.offset = []
    
    for name,player in players.items():
      self.players[name] = Player(player['title'], player['gender'], player['body'], player['hairstyle'], player['haircolor'], player['armor'], player['head'], player['weapon'], player['x'], player['y'])

    for name,npc in npcs.items():
      self.npcs[name] = Npc(npc['title'], npc['gender'], npc['body'], npc['hairstyle'], npc['haircolor'], npc['armor'], npc['head'], npc['weapon'], npc['x'], npc['y'],npc['villan'])

    for name,monster in monsters.items():
      self.monsters[name] = Monster(monster['title'], monster['source'], monster['x'], monster['y'])
    
    for name,container in containers.items():
      self.containers[name] = Container(container['title'], container['x'], container['y'], container['source'], container['source_w'], container['source_h'], container['source_x'], container['source_y'])

    # Set our label to green :)
    self.players[player_name].label.color = (0,255,0,255)
    
  def draw(self):
    if self.player_name == None:
      return

    if not self.zone:
      return
    
    for layer in self.zone.layers:
      if layer.name == 'character':

        for e in sorted( self.npcs.values() + self.monsters.values() + self.players.values() + self.containers.values(), key=lambda a: a.y, reverse=True):

          if e == self.player_target:
            e.draw(True)

          else:
            e.draw(False)

        for spell in self.spells:
          if not spell.expired:
            spell.draw()

      elif layer.name == 'blocked' or layer.name == 'block' or layer.name == 'spawns':
        # Don't draw the blocked layer
        pass
      else:
        #layer.batch.draw()
        pass

