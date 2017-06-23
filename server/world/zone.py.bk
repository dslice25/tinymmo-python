import pytmx

class Zone:

  def __init__(self, name, source, title):

    self.name = name
    self.source = source
    self.title  = title
    
    # Logic to load zone file
    self.data = pytmx.TiledMap(source)
    
    self.width = self.data.width
    self.height = self.data.height

    self.blocked = self.data.layers.index(self.data.get_layer_by_name('blocked'))
  
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
