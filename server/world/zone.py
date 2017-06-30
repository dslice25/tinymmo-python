import pytmx
import time
from astar import *
from monsterspawn import MonsterSpawn
from npcspawn import NpcSpawn
from warp import Warp
import ConfigParser
import os

def load_zones(world):

  config = ConfigParser.RawConfigParser()
  config.read('server_data/zones.ini')
  
  for name in config.sections():
    title = config.get(name,'title')
    source = config.get(name,'source')
    north = config.get(name,'north')
    south = config.get(name,'south')
    east =  config.get(name,'east')
    west = config.get(name,'west')
    borders = { 'north': north, 'south': south, 'east': east, 'west': west }
    world.zones[name] = Zone(name, source, title, borders, world)

class Zone:
  '''
  Zone with astar pathfinding.
  '''

  def __init__(self, name, source, title, borders, world):

    self.name   = name
    self.source = os.path.basename(source)
    self.title  = title
    self.world  = world
    self.borders = borders
    
    # Logic to load zone file
    self.data = pytmx.TiledMap('server_data/zones/' + source)
    
    self.client_data = ''
    with open('server_data/zones/' + source, 'r') as zonefile:
      self.client_data = zonefile.read()
    
    self.width = self.data.width
    self.height = self.data.height

    self.blocked = self.data.layers.index(self.data.get_layer_by_name('blocked'))
 
    self.graph = GridWithWeights(self.width, self.height)
   
    self.graph.walls = [ (x,self.height - y - 1) for x,y,gid in self.data.layers[self.blocked].tiles() ] 

    for o in self.data.objects:
      if o.type == 'monster_spawn':
        x = int(o.x/32)
        y = self.height - int(o.y/32) - 1
        w = int(o.width/32)
        h = int(o.height/32)
        max_spawn = int(o.properties['max_spawn'])
        spawn_delay = float(o.properties['spawn_delay'])
        monster_name = o.name

        # Create monster spawn
        MonsterSpawn(monster_name, x, y, w, h, self.name, max_spawn, spawn_delay, self.world)
      
      if o.type == 'npc_spawn':
        x = int(o.x/32)
        y = self.height - int(o.y/32) - 1
        w = int(o.width/32)
        h = int(o.height/32)
        max_spawn = int(o.properties['max_spawn'])
        spawn_delay = float(o.properties['spawn_delay'])
        npc_name = o.name

        # Create npc spawn
        NpcSpawn(npc_name, x, y, w, h, self.name, max_spawn, spawn_delay, self.world)

      if o.type == 'warp':
        x = int(o.x/32)
        y = self.height - int(o.y/32) - 1
        #w = int(o.width/32)
        #h = int(o.height/32)
        end_zone = o.properties['end_zone']
        end_x = int(o.properties['end_x'])
        end_y = int(o.properties['end_y'])
        
        self.world.warps.append(Warp(self.name, x, y, end_zone, end_x, end_y))

    print "Loaded ZONE",self.name
     
  def heuristic(self, a,b):
    (x1,y1) = a
    (x2,y2) = b

    return abs(x1 - x2) + abs(y1 - y2)

  def get_path(self, start, goal):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    if start == goal:
      return []

    if goal[0] > self.width:
      return []
    
    if goal[0] < 0:
      return []
      
    if goal[1] > self.height:
      return []
    
    if goal[1] < 0:
      return [] 

    if goal in self.graph.walls:
      return []
  
    while not frontier.empty():
      current = frontier.get()
  
      if current == goal:
        break
  
      for next in self.graph.neighbors(current):
        new_cost = cost_so_far[current] + self.graph.cost(current, next)
        if next not in cost_so_far or new_cost < cost_so_far[next]:
          cost_so_far[next] = new_cost
          priority = new_cost + self.heuristic(goal, next)
          frontier.put(next, priority)
          came_from[next] = current
  
    path = [ current ]
    while current != start:
      current = came_from[current]
      path.append(current)
    
    path.reverse()
    path.pop(0)
    return path
 
  def open_at(self, x, y):
    '''
    Determine if x,y are open for movement.
    '''
    if x > self.width - 1:
      return False
    elif x < 0:
      return False
    elif y > self.height - 1:
      return False
    elif y < 0:
      return False
    elif self.data.get_tile_gid(x, self.height - y - 1, self.blocked) > 0:
      return False
    else:
      return True

