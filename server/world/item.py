import ConfigParser

class Item:

  index = 0
  config = ConfigParser.RawConfigParser()
  config.read('server_data/items.ini')

  def getid(self):
    
    Item.index += 1
    return Item.index

  def __init__(self, name, player, container, equipped, world):

    self.name      = "%s-%s" % (name, self.getid())
    self.player    = player
    self.container = container
    self.equipped  = equipped
    self.world     = world
    self.title     = Item.config.get(name, 'title')
    self.gear_type = Item.config.get(name, 'gear_type')
    self.slot      = Item.config.get(name, 'slot')
    self.hit       = Item.config.getint(name, 'hit')
    self.dam       = Item.config.getint(name, 'dam')
    self.arm       = Item.config.getint(name, 'arm')
    self.speed     = Item.config.getfloat(name, 'speed')
    self.icon      = Item.config.get(name,'icon')
    self.value     = Item.config.getint(name, 'value')

    self.world.items[self.name] = self

  def state(self):
    
    return { 'title': self.title, 'name': self.name, 'slot': self.slot, 'equipped': self.equipped, 'gear_type': self.gear_type, 'icon': self.icon, 'hit': self.hit, 'dam': self.dam, 'arm': self.arm, 'speed': self.speed, 'value': self.value }

