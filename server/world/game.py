import time
import os,ConfigParser
import random
import math

from twisted.internet import reactor

from player import Player,load_players
from zone import Zone,load_zones
from spell import Spell
from container import Container
from item import Item
from warp import Warp
from shop import Shop,load_shops
from quest import Quest,load_quests
from loot import Loot,load_loot

class Game:

  def __init__(self):

    
    # Events queue
    self.events = []

    # Tick counter
    self.tick = time.time()

    # For logging events
    self.last_event = 0
    
    # Warps table
    self.warps = []

    # Items table
    self.items = {}

    # Player spawn location
    self.player_spawn_x = 7
    self.player_spawn_y = 7
    self.player_spawn_zone = 'start'

    # Players table
    self.players = {}
    load_players(self, self.player_spawn_x, self.player_spawn_y, self.player_spawn_zone)

    # Monsters table
    self.monsters = {}
    
    # Npcs table
    self.npcs = {}
    
    # Containers table
    self.containers = {}
    self.container_index = 0

    # Zones table
    self.zones = {}
    load_zones(self)

    # Shops table
    self.shops = {}
    load_shops(self)

    # Loot table
    self.loot = {}
    load_loot(self)

    # Quests table
    self.quests = {}
    load_quests(self)

    # Spells table
    self.spells = {}

    

  def process_data(self, player_name, data, protocol=None):
    
    send_now = None

    if data['action'] == 'activate':
      send_now = self.player_activate(player_name)
    
    elif data['action'] == 'equip':
      self.player_equip(player_name, data['name'])

    elif data['action'] == 'unequip':
      self.player_unequip(player_name, data['name'])
   
    elif data['action'] == 'buy':
      send_now = self.player_buy(player_name, data['item'])

    elif data['action'] == 'sell':
      self.player_sell(player_name, data['item'])
  
    elif data['action'] == 'drop':
      self.player_drop(player_name, data['item'])

    elif data['action'] == 'use':
      self.player_use(player_name, data['item'])
    
    elif data['action'] == 'take':
      send_now = self.player_take(player_name, data['item'])
    
    elif data['action'] == 'acceptquest':
      send_now = self.player_accept_quest(player_name, data['name'])
       
    elif data['action'] == 'settarget':
      send_now = self.set_player_target(player_name, data['x'], data['y'])
    
    elif data['action'] == 'goto': 
      self.player_goto(player_name, data['x'], data['y'])

    elif data['action'] == 'cast':
      self.player_cast(player_name, data['spell'])

    elif data['action'] == 'chat':
      self.chat(player_name, data['message'])
    
    elif data['action'] == 'disengage':
      self.player_disengage(player_name)

    elif data['action'] == 'inventory':
      send_now = self.player_inventory(player_name)
   
    elif data['action'] == 'questlog':
      send_now = self.player_questlog(player_name)
       
    elif data['action'] == 'playerstats':
      send_now = self.player_stats(player_name)

    elif data['action'] == 'refresh':
      send_now = self.refresh(player_name)
    
    return send_now

  def player_stats(self, player_name):

    player = self.players[player_name]
    
    stats = { "title": player.title, "hit": self.get_player_hit(player_name), "dam": self.get_player_dam(player_name), "arm": self.get_player_arm(player_name), "hp": player.hp, "mp": player.mp, "gold": player.gold, "exp": player.exp, "level": player.level }
  
    return { "type": "playerstats", "stats": stats, "zone": "player_%s" % player_name }

  def player_goto(self, player_name, x, y):
    player = self.players[player_name]
    zone = self.zones[player.zone]
    start = player.x,player.y
    end = x,y 
    player.path = zone.get_path(start,end)
    
    self.events.append({"type": "playerpath", "name": player_name, "path": player.path, "zone": player.zone})

  def refresh(self, player_name):

    zone_name = self.players[player_name].zone
    zone_source = self.zones[zone_name].source

    zone_data = self.zones[zone_name].client_data

    send_now = { 'type': 'refresh', 'player_name': player_name, 'zone_data': zone_data, 'zone': zone_name, 'zone_source': zone_source, 'players': {}, 'monsters': {}, 'npcs': {}, 'containers': {} }
    
    # Add players to send_now dataset
    for k,v in self.players.items():
      if v.zone == zone_name and v.online:
        send_now['players'][k] = v.state()
  
    # Add monsters to send_now dataset
    for k,v in self.monsters.items():
      if v.zone == zone_name:
        send_now['monsters'][k] = v.state()
    
    # Add npcs to send_now dataset
    for k,v in self.npcs.items():
      if v.zone == zone_name:
        send_now['npcs'][k] = v.state()
  
    # Add containers to send_now dataset
    for k,v in self.containers.items():
      if v.zone == zone_name:
        send_now['containers'][k] = v.state()
    
    return send_now


  def get_events(self, player_name, upto):

    # Collect all events from the relevant zone    
    event_list = [ e for e in self.events[upto:] if e['zone'] in [ 'all', self.players[player_name].zone, "player_%s" % player_name ] ]

    return { "type": "events", "events": event_list }

  def player_join(self, player_name):
    
    # New player data
    self.players[player_name].online = True
      
    # Add addplayer event
    event = { 'type': 'addplayer' }
    event.update(self.players[player_name].state())
    self.events.append(event)

    return player_name

  def cleanup_monster(self, monster):
    # drop monster
    self.events.append({'type': 'dropmonster', 'name': monster.name, 'title': monster.title, 'zone': monster.zone })
    
    # award exp to killer
    monster.target.exp += ( monster.level / monster.target.level ) * ( 10 * monster.level )

    # check if this death satisfies quests
    for quest in monster.target.quests.values():
      quest.check_goal(monster.name)

    # create container object holding monster treasure
    container_name = "container-%s" % self.container_index 
    self.container_index += 1
    title = "Remains of %s" % monster.title
    x = monster.x
    y = monster.y
    zone = monster.zone
    source = 'data/LPC Base Assets/tiles/chests.png' #TODO: gravestone? corpse?

    # award random amount of gold 
    monster.target.gold += random.randint(self.loot[monster.loot].gold_min, self.loot[monster.loot].gold_max)
    
    create_container = False
    # 50% chance of common 
    for i in self.loot[monster.loot].items_common:
      if random.random() < 0.5:
        create_container = True
        item = Item(i, None, container_name, False, self)
   
    # 10% chance of uncommon
    for i in self.loot[monster.loot].items_uncommon:
      if random.random() < 0.1:
        create_container = True
        item = Item(i, None, container_name, False, self)
    
    # 5% chance of rare
    for i in self.loot[monster.loot].items_rare:
      if random.random() < 0.05:
        create_container = True
        item = Item(i, None, container_name, False, self)

    if create_container:
      self.containers[container_name] = Container(title, container_name, x, y, zone, monster.target.name, source, 32, 32, 0, 0)
      self.events.append({'type': 'addcontainer', 'name': container_name, 'title': title, 'x': x, 'y': y, 'zone': zone, 'source': source, 'source_w': 32, 'source_h': 32, 'source_x': 0, 'source_y': 0})
    
      # clean up container after 60 sec
      reactor.callLater(60.0, self.cleanup_container, container_name)
    
    # Really delete monster
    monster.spawn.spawn_count -= 1
    del self.monsters[monster.name]


  def cleanup_npc(self, npc):
    # drop npc
    self.events.append({'type': 'dropnpc', 'name': npc.name, 'title': npc.title, 'zone': npc.zone })


    # award exp to killer
    npc.target.exp += ( npc.level / npc.target.level ) * ( 10 * npc.level )

    # create container object holding npc treasure
    container_name = "container-%s" % self.container_index 
    self.container_index += 1
    title = "Remains of %s" % npc.title
    x = npc.x
    y = npc.y
    zone = npc.zone
    source = 'data/LPC Base Assets/tiles/chests.png' #TODO: gravestone? corpse?

    # award random amount of gold 
    npc.target.gold += random.randint(self.loot[npc.loot].gold_min, self.loot[npc.loot].gold_max)
    
    create_container = False
    # 50% chance of common 
    for i in self.loot[npc.loot].items_common:
      if random.random() < 0.5:
        create_container = True
        item = Item(i, None, container_name, False, self)
   
    # 10% chance of uncommon
    for i in self.loot[npc.loot].items_uncommon:
      if random.random() < 0.1:
        create_container = True
        item = Item(i, None, container_name, False, self)
    
    # 5% chance of rare
    for i in self.loot[npc.loot].items_rare:
      if random.random() < 0.05:
        create_container = True
        item = Item(i, None, container_name, False, self)

    if create_container:
      self.containers[container_name] = Container(title, container_name, x, y, zone, npc.target.name, source, 32, 32, 0, 0)
      self.events.append({'type': 'addcontainer', 'name': container_name, 'title': title, 'x': x, 'y': y, 'zone': zone, 'source': source, 'source_w': 32, 'source_h': 32, 'source_x': 0, 'source_y': 0})
    
    # clean up container after 60 sec
    reactor.callLater(60.0, self.cleanup_container, container_name)

    npc.spawn.spawn_count -= 1
    del self.npcs[npc.name]

  def cleanup_container(self, container_name):

    title = self.containers[container_name].title
    zone  = self.containers[container_name].zone

    self.events.append({'type': 'dropcontainer', 'name': container_name, 'title': title, 'zone': zone})
    
    del self.containers[container_name]
     
  def respawn_player(self, player):
    
    self.events.append({ 'type': 'dropplayer', 'name': player.name, 'zone': player.zone })
    
    # Add addplayer event
    event = { 'type': 'addplayer' }
    player.hp[0] = player.hp[1]
    player.mode = 'wait'
    player.x = self.player_spawn_x
    player.y = self.player_spawn_y
    player.destx = self.player_spawn_x
    player.desty = self.player_spawn_y
    player.zone  = self.player_spawn_zone
    event.update(player.state())
    self.events.append(event)
    
    player_refresh = self.refresh(player.name)
    player_refresh['zone'] = "player_%s" % player.name
    self.events.append(player_refresh)

  def monster_die(self, name):

    self.events.append({ 'type': 'monsterdie', 'name': name, 'zone': self.monster[name].zone })
    
  def remove_monster(self, name):
    
    self.events.append({ 'type': 'dropmonster', 'name': name, 'zone': self.monster[name].zone })
    
    self.monsters[name].spawn.spawn_count -= 1
    del self.monsters[name]

  def npc_die(self,name):
    
    self.events.append({ 'type': 'npcdie', 'name': name, 'zone': self.npcs[name].zone })

  def remove_npc(self, name):
    
    self.events.append({ 'type': 'dropnpc', 'name': name, 'zone': self.npcs[name].zone })
    
    self.npcs[name].spawn.spawn_count -= 1
    del self.npcs[name]

  def set_player_target(self, player_name, x, y):
    
    zone = self.players[player_name].zone
    piz = [ p for p in self.players.values() if p.zone == zone and p.name != player_name and p.online ]
    miz = [ m for m in self.monsters.values() if m.zone == zone ]
    niz = [ n for n in self.npcs.values() if n.zone == zone ]
    ciz = [ c for c in self.containers.values() if c.zone == zone ]
    tgt = None
    objtype = None

    # get thing closest to x,y
    all_things = list(piz + miz + niz + ciz)
    all_things_sorted = sorted(all_things, key=lambda z: math.sqrt( ((x-z.x)**2)+((y-z.y)**2) ))
    
    # if nothing found, unset target
    if len(all_things_sorted) < 1:
      self.players[player_name].target = None
      return { 'type': 'unsettarget', }
    else:
      tgt = all_things_sorted[0]
    
    # if too far from mouse, unset target
    if math.sqrt( ((x-tgt.x)**2)+((y-tgt.y)**2) ) > 3:
      self.players[player_name].target = None
      return { 'type': 'unsettarget', }

    if tgt:
      self.players[player_name].target = tgt
      return { 'type': 'settarget', 'name': tgt.name, 'objtype': tgt.__class__.__name__ }
    else:
      self.players[player_name].target = None
      return { 'type': 'unsettarget', }

  def player_leave(self, player_name):
      
    # Add dropplayer event
    self.events.append({ 'type': 'dropplayer', 'name': player_name, 'zone': self.players[player_name].zone })
    self.players[player_name].online = False
    self.players[player_name].target = None
    self.players[player_name].mode = 'wait'
    
  def walk(self, player_name, direction):
    '''
    Player requests to go north.
    '''
    
    send_event = False
    zone = self.players[player_name].zone
    startx = self.players[player_name].x
    starty = self.players[player_name].y
    endx = self.players[player_name].x
    endy = self.players[player_name].y

    if direction == 'north':
      endy += 1
    elif direction == 'south':
      endy -= 1
    elif direction == 'east':
      endx += 1
    elif direction == 'west':
      endx -= 1

    # If player is free, then perform action
    if self.players[player_name].free():
      if self.zones[zone].open_at(endx,endy):
        self.players[player_name].reset()
        send_event = True

    if send_event:
      self.players[player_name].x = endx
      self.players[player_name].y = endy
      self.players[player_name].mode = 'running'
      self.players[player_name].direction = direction
      self.events.append({ 'type': 'playermove', 'name': player_name, 'zone': zone, 'direction': direction, 'start': (startx,starty), 'end': (endx,endy) })

  def stopwalk(self, player_name):
    self.players[player_name].mode = 'wait'

    
  def warp(self, player, target_warp):
    
    # Drop player
    self.events.append({ 'type': 'dropplayer', 'name': player.name, 'zone': player.zone })
    
    player.x = target_warp.end_x
    player.y = target_warp.end_y
    player.zone = target_warp.end_zone
    player.path = []
    
    # Add addplayer event
    event = { 'type': 'addplayer' }
    event.update(player.state())
    self.events.append(event)

    player_refresh = self.refresh(player.name)
    player_refresh['zone'] = "player_%s" % player.name
    self.events.append(player_refresh)


  def chat(self, player_name, message):
    
    zone = self.players[player_name].zone
    self.events.append({ 'type': 'playerchat', 'name': player_name, 'zone':  zone, 'message': message })

  def player_attack(self, player_name):
    
    player = self.players[player_name]
     
    if player.target:
      if self.in_attack_range(player,target):
        player.mode = 'fighting'
      else:
        return { 'type': 'message', 'message': "You are not in range to attack %s" % target.title }

  def player_activate(self, player_name):

    target = self.players[player_name].target
    player = self.players[player_name]
    send_now = {}

    # if no target, no action
    if target == None:
      send_now = { 'type': 'message', 'message': "What to whom?" }

    # if target is monster, then fight it
    elif target.__class__.__name__ == 'Monster':
      if self.in_attack_range(player, target):
        player.mode = 'fighting'
        send_now = { 'type': 'message', 'message': "You attack the %s" % target.title }
      else:
        send_now = { 'type': 'message', 'message': "You are not in range to attack %s" % target.title }

    # if npc has shop or quest info, they are friendly. no attacking
    elif target.__class__.__name__ == 'Npc':
      if target.shop:
        if self.shops.has_key(target.shop):
          shop = self.shops[target.shop]
          send_now = { 'type': 'shop', 'name': target.shop, 'title': shop.title, 'inventory': shop.get_inventory(), 'player_inventory': self.player_inventory(player_name) }
      
      elif target.quest:
        if self.quests.has_key(target.quest):
          quest = self.quests[target.quest]
          if quest.avaliable_to(player_name):
            send_now = { 'type': 'questdialog', 'name': quest.name, 'title': quest.title, 'dialog': quest.dialog }
      
      elif target.villan:
        if self.in_attack_range(player, target):
          player.mode = 'fighting'
          send_now = { 'type': 'message', 'message': "You attack the %s" % target.title }
        else:
          send_now = { 'type': 'message', 'message': "You are not in range to attack %s" % target.title }
   
    elif target.__class__.__name__ == 'Container':
      inv = {}
      for name,item in self.items.items():
        if item.container == target.name:
          inv[name] = { 'title': item.title, 'slot': item.slot, 'hit': item.hit, 'dam': item.dam, 'arm': item.arm, 'value': item.value, 'icon': item.icon }
      
      if len(inv.keys()) > 0:
        send_now = { 'type': 'container', 'title': target.title,  'inventory': inv }
      else:
        send_now = { 'type': 'message', 'message': "There's nothing to take from the %s" % target.title }
    
    elif target.__class__.__name__ == 'Player':
      inv = {}
      for name,item in self.items.items():
        if item.player == target.name and item.equipped == False:
          inv[name] = { 'title': item.title, 'slot': item.slot, 'hit': item.hit, 'dam': item.dam, 'arm': item.arm, 'value': item.value, 'icon': item.icon }

      send_now = { 'type': 'give', 'title': "Give to %s" % target.title,  'inventory': inv }
    

    return send_now


  def player_accept_quest(self, player_name, quest_name):
 
    send_now = {}
     
    if not self.quests.has_key(quest_name):
      return send_now

    return self.quests[quest_name].assign(player_name)


  def player_questlog(self, player_name):

    quests = []
    for quest in self.players[player_name].quests.values():
      quests.append(quest.get_log_entry())

    return { 'type': 'questlog', 'quests': quests } 

  def player_buy(self, player_name, item_name):

    shop = self.players[player_name].target.shop
    
    if not self.shops.has_key(shop):
      return

    if len([ i for i in self.items.values() if i.player == player_name ]) >= 12:
      return { 'type': 'message', 'message': "You can't carry any more!" }
  
    self.shops[shop].buy(item_name, player_name)

    return { 'type': 'message', 'message': "You bought a %s" % item_name }

  def player_take(self, player_name, item_name):

    if not self.items.has_key(item_name):
      return

    if not self.items[item_name].container:
      return

    container_name = self.items[item_name].container
    
    if not self.containers.has_key(container_name):
      return

    if not self.containers[container_name].owner == player_name:
      return

    if self.items[item_name].player:
      return
    
    # reassign to player
    self.items[item_name].container = None
    self.items[item_name].player = player_name

    return { 'type': 'message', 'message': "You took the %s" % self.items[item_name].title }

  def player_sell(self, player_name, item_name):

    shop = self.players[player_name].target.shop
    
    if not self.shops.has_key(shop):
      return
  
    self.shops[shop].sell(item_name, player_name)
    
    return { 'type': 'message', 'message': "You sold a %s" % item_name }
  
  def player_use(self, player_name, item_name):
    # Skip if this item doesn't exist
    if not self.items.has_key(item_name):
      return
    
    # Skip if this item isn't owned by player
    if self.items[item_name].player != player_name:
      return
    
    # Skip if this item is already equipped
    if self.items[item_name].equipped:
      return
  
    item_title = self.items[item_name].title
    #del self.items[item_name]
    
    return { 'type': 'message', 'message': "You use the %s." % item_title } 
    

  def player_drop(self, player_name, item_name):
    
    # Skip if this item doesn't exist
    if not self.items.has_key(item_name):
      return
    
    # Skip if this item isn't owned by player
    if self.items[item_name].player != player_name:
      return
    
    # Skip if this item is already equipped
    if self.items[item_name].equipped:
      return
  
    item_title = self.items[item_name].title
    del self.items[item_name]
    
    return { 'type': 'message', 'message': "You drop the %s." % item_title } 
    
    
  def player_equip(self, player_name, item_name):
   
    # Skip if this item doesn't exist
    if not self.items.has_key(item_name):
      return
    
    # Skip if this item cannot be equipped
    if self.items[item_name].slot == None:
      return
    
    # Skip if this item is already equipped
    if self.items[item_name].equipped:
      return
   
    # Skip if this items isn't owned by player
    if self.items[item_name].player != player_name:
      return

    # Is there something already in that slot
    slot = self.items[item_name].slot
    if [ i for i in self.items.values() if i.player == player_name and i.slot == slot and i.equipped ]:
      return

    self.items[item_name].equipped = True
    gear_type = self.items[item_name].gear_type
    zone = self.players[player_name].zone
    
    if slot == 'armor':
      self.events.append({ 'type': 'setplayerarmor', 'name': player_name, 'zone':  zone, 'armor': gear_type,})
    elif slot == 'weapon':
      self.events.append({ 'type': 'setplayerweapon', 'name': player_name, 'zone':  zone, 'weapon': gear_type,})
    elif slot == 'head':
      self.events.append({ 'type': 'setplayerhead', 'name': player_name, 'zone':  zone, 'head': gear_type,})

    self.events.append(self.player_stats(player_name))
    
  def player_unequip(self, player_name, item_name):

    # Skip if this item doesn't exist
    if not self.items.has_key(item_name):
      return
    
    # Skip if this item cannot be equipped
    if self.items[item_name].slot == 'none':
      return
    
    # Skip if this item is unequipped
    if not self.items[item_name].equipped:
      return

    # Skip if this items isn't owned by player
    if self.items[item_name].player != player_name:
      return

    self.items[item_name].equipped = False
    
    slot = self.items[item_name].slot
    zone = self.players[player_name].zone

    if slot == 'armor':
      self.events.append({ 'type': 'setplayerarmor', 'name': player_name, 'zone':  zone, 'armor': 'clothes',})
    elif slot == 'weapon':
      self.events.append({ 'type': 'setplayerweapon', 'name': player_name, 'zone':  zone, 'weapon': 'unarmed',})
    elif slot == 'head':
      self.events.append({ 'type': 'setplayerhead', 'name': player_name, 'zone':  zone, 'head': 'none',})
    
    self.events.append(self.player_stats(player_name))

  def player_inventory(self, player_name):
    
    # Return hash of player's items
    inv = {}
    for k,v in self.items.items():
      if v.player == player_name:
        inv[k] = v.state()
    
    return { 'type': 'inventory', 'inventory': inv }

  def player_disengage(self, player_name):
    
    # Player disengages and stops fighting
    self.players[player_name].fighting = False

  def player_cast(self, player_name, spell, target):
    
    # Can't cast if fighting 
    if not self.players[player_name].free():
      return
    
    if spell in self.players[player_name].spells:
      zone = self.players[player_name].zone
      caster_anim = self.spells[spell].caster_source
      target_anim = self.spells[spell].target_source
      self.events.append({ 'type': 'playercast', 'name': player_name, 'zone':  zone, 'caster_anim': caster_anim, 'target': target, 'target_anim': target_anim })
      
  def get_player_dam(self, player_name):
    '''
    Get total damage of player
    '''
    base_damage = self.players[player_name].dam
    gear_damage = 0
    
    for item_name,item in self.items.items():
      if item.equipped and item.player == player_name:
        gear_damage += item.dam
    
    return base_damage + gear_damage

  
  def get_player_hit(self, player_name):
    '''
    Get hit bonus for player
    '''
    base_hit = self.players[player_name].hit
    gear_hit = 0
    
    for item_name,item in self.items.items():
      if item.equipped and item.player == player_name:
        gear_hit =+ item.hit
    
    return base_hit + gear_hit


  def get_player_arm(self, player_name):
    '''
    Get armor class of player
    '''
    base_arm = self.players[player_name].arm
    gear_arm = 0
    
    for item_name,item in self.items.items():
      if item.equipped and item.player == player_name:
        gear_arm = item.arm
    
    return base_arm + gear_arm


  def get_player_attack_type(self, player_name):
    
    attack_type = 'slash'
    
    for item_name,item in self.items.items():
      if item.equipped and item.slot == 'weapon' and item.player == player_name:
        if item.gear_type in [ 'sword', 'wand' ]:
          attack_type = 'slash'
        elif item.gear_type == 'bow':
          attack_type = 'bow'
        elif item.gear_type == 'spear':
          attack_type = 'thrust'
    return attack_type
  
  def get_player_attack_speed(self, player_name):
    
    attack_speed = 3.0
    
    for item_name,item in self.items.items():
      if item.equipped and item.slot == 'weapon' and item.player == player_name:
        attack_speed = item.speed

    return attack_speed

  def get_distance_between(self, obj1, obj2):
    
    return abs(obj1.x - obj2.x) + abs(obj1.y - obj2.y)

  def in_attack_range(self, attacker, target):
    
    distance = self.get_distance_between(attacker,target)

    if attacker.__class__.__name__ == 'Player':
      attack_type = self.get_player_attack_type(attacker.name)
      if attack_type == 'slash':
        if distance < 2:
          return True
      elif attack_type == 'bow':
        if distance < 10:
          return True   
      elif attack_type == 'thrust':
        if distance < 5:
          return True

    elif attacker.__class__.__name__ == 'Npc':
      attack_type = attacker.attack_type
      if attack_type == 'slash':
        if distance < 2:
          return True
      elif attack_type == 'bow':
        if distance < 10:
          return True   
      elif attack_type == 'thrust':
        if distance < 5:
          return True
      
    elif attacker.__class__.__name__ == 'Monster':
      # TODO: Give individual monsters an attack range
      if distance < 2:
        return True

    return False


  def loop(self):
    
    # update game world
    # Keepalive tick
    #if time.time() - 60 > self.tick:
    #  self.events.append({ 'type': 'tick', 'time': time.time(), 'zone': 'all' })
    #  self.tick = time.time()
    
    # Follow event queue
    for e in self.events[self.last_event:]:
      if e['type'] in ['playermove','npcmove','monstermove']:
        continue
      #print "EVENT %s: %s" % (e['type'], e)

    self.last_event = len(self.events)

