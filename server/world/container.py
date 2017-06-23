class Container:

  def __init__(self, title, name, x, y, zone, owner,  source, source_w, source_h, source_y, source_x):
    
    self.title = title
    self.name = name
    self.x = x
    self.y = y
    self.zone = zone
    self.source = source
    self.owner = owner
    self.source_w = source_w
    self.source_h = source_h
    self.source_x = source_x
    self.source_y = source_y

  def state(self):

    return { 'title': self.title, 
             'name': self.name, 
             'x': self.x, 
             'y': self.y, 
             'zone': self.zone, 
             'source': self.source, 
             'source_w': self.source_w, 
             'source_h': self.source_h,
             'source_x': self.source_x,
             'source_y': self.source_y, }

