from twisted.internet import reactor, protocol, endpoints, task
from twisted.protocols import basic
import json

PLAYER_ACTION_TIME = 1.0 # seconds it takes to perform an action
MONSTER_ACTION_TIME = 2.0 # seconds it takes to perform an action
TICK_RATE = 60 # seconds between keepalive ticks

class GameProtocol(basic.LineReceiver):
    def __init__(self, factory):
      self.factory = factory
      self.player_name = None
      self.authenticated = False
      self.last_event = len(self.factory.world.events)

    def connectionMade(self):
      print "Connection made"
      self.factory.clients.add(self)

    def connectionLost(self, reason):
      print "Connection lost"
      if self.player_name: 
        self.factory.world.player_leave(self.player_name)
      
      self.factory.clients.remove(self)

    def prepare(self, data):
      '''
      Take raw data and prep for sending by converting it to json.
      '''
      final = ""

      try:
        final = json.dumps(data)
      except:
        final = ""

      return final + "\r\n"

    def unpack(self, data):
      '''
      Take recieved data unpack it for usage.
      '''
      final = None

      try:
        final = json.loads(data)
      except:
        final = None

      return final

    def lineReceived(self, line):
      if self.authenticated:
        self.playing(line)

      else:
        self.login(line)

    def login(self, line):
      data = self.unpack(line)
      userok = False
      passok = False
      if data:
        if data['name'] in self.factory.world.players.keys():
          if not self.factory.world.players[data['name']].online:
            userok = True
        if userok:
          if data['password'] == self.factory.world.players[data['name']].password:
            passok = True
      
      if not passok:
        self.transport.write(self.prepare({"type": "loginfailed", "message": "bad username or password"}))
        return False
      if not userok:
        self.transport.write(self.prepare({"type": "loginfailed", "message": "bad username or password"}))
        return False
    
      self.authenticated = True 
      self.player_name = data['name']
      self.factory.world.player_join(self.player_name)
      self.transport.write(self.prepare({"type": "loginsucceeded", "message": "request initial data"}))

      # Start sending events
      e = task.LoopingCall(self.sendevents)
      e.start(0.1)
      return True

    def playing(self, line): 
      data = self.unpack(line)

      # Process data
      if data:
        send_now = self.factory.world.process_data(self.player_name, data)

        # Send any additional data to client
        if send_now:
          self.transport.write(self.prepare(send_now))

    # Send all game events since last event 
    def sendevents(self):
      if self.authenticated and self.player_name:
        events = self.factory.world.get_events(self.player_name, self.last_event)
        if not events['events']:
          return
        events_data = self.prepare(events)
        if events_data:
          self.transport.write(events_data)
          self.last_event = len(self.factory.world.events)
      


class GameFactory(protocol.Factory):
  
  def __init__(self, world):
    self.world = world
    self.clients = set()


  def buildProtocol(self, addr):
    return GameProtocol(self)


