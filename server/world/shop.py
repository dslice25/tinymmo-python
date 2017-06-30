from item import Item
import ConfigParser
import copy

class ShopItem:
  '''
  Spawns items in merchant inventory
  '''
  mi_index = 0

  def __init__(self, name, title, gear_type, slot, hit, dam, arm, value, icon):
    
    self.name      = name
    self.title     = title
    self.gear_type = gear_type
    self.slot      = slot
    self.hit       = hit
    self.dam       = dam
    self.arm       = arm
    self.value     = value 
    self.icon      = icon

  def create(self, buyer_name, world):
    
    Item(self.name, player=buyer_name, container=None, equipped=False, world=world)
  
def load_shops(world):

  config = ConfigParser.RawConfigParser()
  config.read('server_data/shops.ini')

  shops = []
  
  for shop in config.sections():
    title    = config.get(shop,'title')
    for_sale = config.get(shop,'for_sale').split(',')
    
    world.shops[shop] = Shop(shop, title, for_sale, world)  
    


class Shop:

  def __init__(self, name, title, for_sale, world):

    self.title = title
    self.name = name
    self.world = world
    self.inventory = {}

    self.message = "Welcome to my shop! What would you like to buy?"

    config = ConfigParser.RawConfigParser()
    config.read('server_data/items.ini')

    for sale_item in for_sale:
      title = config.get(sale_item,'title')
      gear_type = config.get(sale_item,'gear_type')
      slot = config.get(sale_item,'slot')
      hit = config.getint(sale_item,'hit')
      dam = config.getint(sale_item,'dam')
      arm = config.getint(sale_item,'arm')
      value = config.getint(sale_item,'value')
      icon = config.get(sale_item,'icon')

      self.inventory[sale_item] = ShopItem(sale_item, title, gear_type, slot, hit, dam, arm, value, icon)

    print "Loaded SHOP",self.name

  def get_inventory(self):

    inv = {}
    for name,item in self.inventory.items():
      inv[name] = { 'title': item.title, 'slot': item.slot, 'hit': item.hit, 'dam': item.dam, 'arm': item.arm, 'value': item.value, 'icon': item.icon }

    return inv

  def sell(self, item_name, seller_name):
    
    # remove sold object from game world
    del self.world.items[item_name]

    # TODO: pay player for item

  def buy(self, item_name, buyer_name):
    
    # Add purchased item to game world
    self.inventory[item_name].create(buyer_name, self.world)

    # TODO: deduct gold from player for purchase
