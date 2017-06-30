import pyglet
from pytmx.util_pyglet import load_pyglet

# workaround for pyinstaller
import sys
if 'twisted.internet.reactor' in sys.modules:
  del sys.modules['twisted.internet.reactor']

from pigtwist import pygletreactor
pygletreactor.install() # <- this must come before...
from twisted.internet import reactor, task # <- ...importing this reactor!
from twisted.protocols.ftp import FTPClient

from ui import LoginManager,ConnectManager,ChatWindowManager,InventoryManager,ShopManager,CharacterManager,ContainerManager,QuestDialogManager,QuestLogManager
from net import GameClientFactory,GameClientProtocol
from game.game import Game
from game.npc import Npc
from game.monster import Monster
from game.player import Player
from game.spell import Spell
from game.container import Container
from sfx import SoundSet
 
class Client:

  def __init__(self):

    self.game = Game()
    self.window = pyglet.window.Window(640,480)
    self.loginManager = LoginManager(self)
    self.connectManager = ConnectManager(self)
    self.chatManager = ChatWindowManager(self)
    self.inventoryManager = None
    self.shopManager = None
    self.popupManager = None
    self.characterManager = None
    self.containerManager = None
    self.questDialogManager = None
    self.questLogManager = None
    self.factory = GameClientFactory(self)
    self.protocol = None
    #self.sounds = SoundSet()
   
    self.update_task = task.LoopingCall(self.player_stats)

  def player_stats(self):

    self.protocol.send({'action': 'playerstats'})
    
  def process(self, data):

    if data['type'] == 'events':
      for event in data['events']:
        self.process(event)
    elif data['type'] == 'loginsucceeded':
      self.log(data)
      self.play() # OK, we can switch to playing mode
    elif data['type'] == 'refresh':
      self.log(data)
      self.game.load(data['player_name'],data['zone_source'],data['players'],data['monsters'],data['npcs'],data['containers'],data['zone_data'])
    elif data['type'] == 'addplayer':
      self.log(data)
      self.game.players[data['name']] = Player(data['title'],data['gender'],data['body'],data['hairstyle'],data['haircolor'],data['armor'],data['head'],data['weapon'],data['x'],data['y'])
      message = "%s is here." % (data['name'])
      self.chatManager.add_message(message)
    elif data['type'] == 'dropplayer':
      self.log(data)
      self.game.players[data['name']].unload()
      del self.game.players[data['name']]
      message = "%s left." % (data['name'])
      self.chatManager.add_message(message)
    elif data['type'] == 'addmonster':
      self.log(data)
      self.game.monsters[data['name']] = Monster(data['title'],data['source'],data['x'],data['y'])
    elif data['type'] == 'addcontainer':
      self.log(data)
      self.game.containers[data['name']] = Container(data['title'], data['x'], data['y'], data['source'], data['source_w'], data['source_h'], data['source_x'], data['source_y'])
    elif data['type'] == 'dropcontainer':
      self.log(data)
      if self.game.containers.has_key(data['name']):
        del self.game.containers[data['name']]
    elif data['type'] == 'playerpath':
      self.log(data)
      if self.game.players.has_key(data['name']):
        self.game.players[data['name']].path = data['path']
    elif data['type'] == 'playermove':
      self.log(data)
      if self.game.players.has_key(data['name']):
        self.game.players[data['name']].go(data['direction'],data['start'],data['end'])
    elif data['type'] == 'addnpc':
      self.log(data)
      self.game.npcs[data['name']] = Npc(data['title'],data['gender'],data['body'],data['hairstyle'],data['haircolor'],data['armor'],data['head'],data['weapon'],data['x'],data['y'],data['villan'])
    elif data['type'] == 'npcmove':
      self.log(data)
      if self.game.npcs.has_key(data['name']):
        self.game.npcs[data['name']].go(data['direction'],data['start'],data['speed'])
    elif data['type'] == 'monstermove':
      self.log(data)
      if self.game.monsters.has_key(data['name']):
        self.game.monsters[data['name']].go(data['direction'],data['start'],data['speed'])
    elif data['type'] == 'playerstop':
      self.log(data)
      if self.game.players.has_key(data['name']):
        self.game.players[data['name']].wait()
    elif data['type'] == 'playerslash':
      self.log(data)
      if self.game.players.has_key(data['name']):
        self.game.players[data['name']].slash()
        #self.sounds.play('sword')
        title = self.game.players[data['name']].title
        dam = data['dam']
        target_title = data['target_title']
        self.chatManager.add_message("%s slashes %s for %s damage!" % (title,target_title,dam))
    elif data['type'] == 'playerthrust':
      self.log(data)
      if self.game.players.has_key(data['name']):
        self.game.players[data['name']].thrust()
        title = self.game.players[data['name']].title
        #self.sounds.play('melee')
        dam = data['dam']
        target_title = data['target_title']
        self.chatManager.add_message("%s stabs %s for %s damage!" % (title,target_title,dam))
    elif data['type'] == 'playerbow':
      self.log(data)
      if self.game.players.has_key(data['name']):
        self.game.players[data['name']].bow()
        title = self.game.players[data['name']].title
        dam = data['dam']
        target_title = data['target_title']
        self.chatManager.add_message("%s shoots %s for %s damage!" % (title,target_title,dam))
    elif data['type'] == 'playercast':
      self.log(data)
      if self.game.players.has_key(data['name']):
        title = self.game.players[data['name']].title
        self.chatManager.add_message("%s casts!" % (title))
    elif data['type'] == 'npcslash':
      self.log(data)
      if self.game.npcs.has_key(data['name']):
        self.game.npcs[data['name']].slash()
        #self.sounds.play('sword')
        title = self.game.npcs[data['name']].title
        dam = data['dam']
        target_title = data['target_title']
        self.chatManager.add_message("%s slashes %s for %s damage!" % (title,target_title,dam))
    elif data['type'] == 'npcthrust':
      self.log(data)
      if self.game.npcs.has_key(data['name']):
        self.game.npcs[data['name']].thrust()
        title = self.game.npcs[data['name']].title
        #self.sounds.play('melee')
        dam = data['dam']
        target_title = data['target_title']
        self.chatManager.add_message("%s stabs %s for %s damage!" % (title,target_title,dam))
    elif data['type'] == 'npcbow':
      self.log(data)
      if self.game.npcs.has_key(data['name']):
        self.game.npcs[data['name']].bow()
        title = self.game.npcs[data['name']].title
        dam = data['dam']
        target_title = data['target_title']
        self.chatManager.add_message("%s shoots %s for %s damage!" % (title,target_title,dam))
    elif data['type'] == 'npccast':
      self.log(data)
      if self.game.npcs.has_key(data['name']):
        title = self.game.npcs[data['name']].title
        self.chatManager.add_message("%s casts!" % (title))
    elif data['type'] == 'inventory':
      self.log(data)
      self.inventoryManager = None
      self.inventoryManager = InventoryManager(self, data['inventory'])
      if self.characterManager:
        self.get_stats()
    elif data['type'] == 'shop':
      self.log(data)
      self.shopManager = ShopManager(self, data['inventory'], data['player_inventory']['inventory'])
    elif data['type'] == 'container':
      self.log(data)
      self.containerManager = ContainerManager(self, data['inventory'])
    elif data['type'] == 'questdialog':
      self.log(data)
      self.questDialogManager = None
      self.questDialogManager = QuestDialogManager(self, data['name'], data['title'], data['dialog'])
    elif data['type'] == 'questlog':
      self.log(data)
      self.questLogManager = None
      self.questLogManager = QuestLogManager(self, data['quests'])
    elif data['type'] == 'playerstats':
      self.log(data)
      self.characterManager = None
      self.characterManager = CharacterManager(self, data['stats'])
    elif data['type'] == 'setplayerhead':
      self.log(data)
      self.game.players[data['name']].set_head(data['head'])
    elif data['type'] == 'setplayerarmor':
      self.log(data)
      self.game.players[data['name']].set_armor(data['armor'])
    elif data['type'] == 'setplayerweapon':
      self.log(data)
      self.game.players[data['name']].set_weapon(data['weapon'])
    elif data['type'] == 'playerdie':
      self.log(data)
      if self.game.players.has_key(data['name']):
        self.game.players[data['name']].die()
    elif data['type'] == 'monsterattack':
      self.log(data)
      if self.game.monsters.has_key(data['name']):
        title = data['title']
        dam = data['dam']
        target = data['target']
        self.game.monsters[data['name']].attack()
        self.chatManager.add_message("%s hits %s for %s damage!" % (title,target,dam))
    elif data['type'] == 'monsterstop':
      self.log(data)
      if self.game.monsters.has_key(data['name']):
        self.monsters[data['name']].stop()
    elif data['type'] == 'monsterdie':
      self.log(data)
      if self.game.monsters.has_key(data['name']):
        self.game.monsters[data['name']].die()
        self.chatManager.add_message("%s dies!" % data['title'])
    elif data['type'] == 'dropmonster':
      self.log(data)
      if self.game.monsters.has_key(data['name']):
        self.game.monsters[data['name']].unload()
        del self.game.monsters[data['name']]
    elif data['type'] == 'npcdie':
      self.log(data)
      if self.game.npcs.has_key(data['name']):
        self.game.npcs[data['name']].die()
        self.chatManager.add_message("%s dies!" % data['title'])
    elif data['type'] == 'dropnpc':
      self.log(data)
      if self.game.npcs.has_key(data['name']):
        self.game.npcs[data['name']].unload()
        del self.game.npcs[data['name']]
    elif data['type'] == 'settarget':
      self.log(data)
      if data['objtype'] == 'Monster':
        self.game.player_target = self.game.monsters[data['name']]
      elif data['objtype'] == 'Npc':
        self.game.player_target = self.game.npcs[data['name']]
      elif data['objtype'] == 'Player':
        self.game.player_target = self.game.players[data['name']]
      elif data['objtype'] == 'Container':
        self.game.player_target = self.game.containers[data['name']]
    elif data['type'] == 'unsettarget':
      self.log(data)
      self.game.player_target = None
    elif data['type'] == 'playerchat':
      self.log(data)
      message = "<%s> %s" % (data['name'],data['message'])
      self.chatManager.add_message(message)
    elif data['type'] == 'message':
      self.log(data)
      self.chatManager.add_message(data['message'])
    elif data['type'] == 'tick':
      self.log(data)
    elif data['type'] == 'loginfailed':
      self.log(data)

  def log(self, data):
    print "%s: %s" % (data['type'].upper(), data)

  def set_protocol(self, protocol):
    
    self.protocol = protocol

  def try_connect(self, server, port):

    reactor.connectTCP(server, port, self.factory)

  def connected(self):

    self.login()

  def equip(self, item_name):

    self.protocol.send({'action': 'equip', 'name': item_name})
    self.protocol.send({'action': 'inventory'})

  def unequip(self, item_name):
    
    self.protocol.send({'action': 'unequip', 'name': item_name})
    self.protocol.send({'action': 'inventory'})

  def buy(self, item_name):
    
    self.protocol.send({'action': 'buy', 'item': item_name})
  
  def take(self, item_name):

    self.protocol.send({'action': 'take', 'item': item_name})

  def sell(self, item_name):

    self.protocol.send({'action': 'sell', 'item': item_name})

  def drop(self, item_name):

    self.protocol.send({'action': 'drop', 'item': item_name})

  def use(self, item_name):

    self.protocol.send({'action': 'use', 'item': item_name})

  def accept_quest(self, quest_name):

    self.protocol.send({'action': 'acceptquest', 'name': quest_name})

  def login(self):
    
    self.connectManager.delete()
    
    @self.window.event
    def on_draw():
      self.window.clear()
      self.loginManager.draw()

  def try_login(self, username, password):

    # Send login request
    self.protocol.send({"action": "login","name": username, "password": password})
    
  def chat(self, message):
    self.protocol.send({"action": "chat", "message": message})
       
  def command(self, command):
  
    if command[0] == 'logout':
      self.logout()

    elif command[0] == 'refresh':
      self.refresh()

    elif command[0] == 'inv':
      self.get_inventory()
    
    elif command[0] == 'stats':
      self.get_stats()

    elif command[0] == 'help':
      self.help()

  def get_stats(self):
    self.protocol.send({"action": "playerstats"})

  def get_inventory(self):
    self.protocol.send({"action": "inventory"})
   
  def get_questlog(self):
    self.protocol.send({"action": "questlog"})
    
  def refresh(self):
    self.protocol.send({"action": "refresh"})

  def logout(self):
    pass

  def get_target(self, x, y):
    self.protocol.send({"action": "settarget", "x": x, "y": y})

  def goto(self, x, y):
    self.protocol.send({"action": "goto", "x": x, "y": y})

  def interact(self, x, y):
    self.protocol.send({"action": "interact", "x": x, "y": y})

  def activate(self):
    self.protocol.send({"action": "activate", })
  
  def activate_or_move(self):
    self.protocol.send({"action": "activateormove", })

  def play(self):

    self.loginManager.delete()
    
    # Send refresh request
    self.refresh()

    # Get player stats
    self.player_stats()
    #self.update_task.start(3.0,now=True)

    fps_display = pyglet.clock.ClockDisplay()

    @self.window.event
    def on_draw():
      self.window.clear()
      self.game.draw()
      self.chatManager.draw()
      
      if self.shopManager:
        self.shopManager.draw()  
 
      if self.inventoryManager:
        self.inventoryManager.draw()
    
      if self.popupManager:
        self.popupManager.draw()
      
      if self.characterManager:
        self.characterManager.draw()
      
      if self.containerManager:
        self.containerManager.draw()
        
      if self.questDialogManager:
        self.questDialogManager.draw()
        
      if self.questLogManager:
        self.questLogManager.draw()
      
      fps_display.draw() 

    @self.window.event
    def on_mouse_press(x, y, button, modifiers):
        
      x = x/32
      y = y/32
      print x,y
      if button == pyglet.window.mouse.LEFT:
        self.goto(x,y)

      if button == pyglet.window.mouse.RIGHT:
        self.get_target(x,y)
        self.activate()

    @self.window.event
    def on_key_press(symbol, modifiers):
      if symbol == pyglet.window.key.LCTRL:
        if self.game.player_target:
          self.protocol.send({"action": "activate", })
        else:
          self.chatManager.add_message("You must have a target to do that!")


  def start(self):
    
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
  
    @self.window.event
    def on_draw():
      self.window.clear()
      self.connectManager.draw()

    @self.window.event
    def on_close():
      reactor.callFromThread(reactor.stop)

      # Return true to ensure that no other handlers
      # on the stack receive the on_close event
      return True
    
    reactor.run(call_interval=1/240.0)
