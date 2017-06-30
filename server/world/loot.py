from item import Item
import ConfigParser
import copy

def load_loot(world):

  config = ConfigParser.RawConfigParser()
  config.read('server_data/loot.ini')

  loot = []
  
  for loot in config.sections():
    gold_min = config.getint(loot,'gold_min')
    gold_max = config.getint(loot,'gold_max')

    items_common = config.get(loot,'items_common').split(',')
    items_common = filter(None, items_common)

    items_uncommon = config.get(loot,'items_uncommon').split(',')
    items_uncommon = filter(None, items_uncommon)

    items_rare = config.get(loot,'items_rare').split(',')
    items_rare = filter(None, items_rare)
    
    world.loot[loot] = Loot(loot, gold_min,gold_max,items_common,items_uncommon,items_rare)  
    


class Loot:

  def __init__(self, name, gold_min,gold_max,items_common,items_uncommon,items_rare):

    self.gold_min = gold_min
    self.gold_max = gold_max
    self.items_common = items_common
    self.items_uncommon = items_uncommon
    self.items_rare = items_rare

    print "Loaded LOOT",name
