import pyglet

from twisted.internet import task

class Monster:

  def __init__(self, title, source, x, y):
    
    self.x = x
    self.y = y

    raw = pyglet.image.load(source)
    grid = pyglet.image.ImageGrid(raw, 4, 3)
    self.frame_w = grid[0].width
    self.frame_h = grid[0].height
    self.frame = 0
    self.action = 'wait'
    self.direction = 'south'
   
    self.title = title
    self.speed = 2
    # Movement
    self.destx = self.x
    self.desty = self.y
    self.spritex = self.x * 32
    self.spritey = self.y * 32

    self.label = pyglet.text.Label(self.title,
                                   font_name='Times New Roman',
                                   font_size=12,
                                   color=(255,0,0,255),
                                   x=self.spritex,
                                   y=self.spritey,
                                   anchor_x="center",)

    # Frames within grid (e,s,w,n)
    # wait 1:1, 4:4, 7:7, 10:10
    # walk 0:2, 3:5, 6:8, 9:11

    self.sprites = {}
    for a in [ 'wait', 'walk', 'attack' ]:
      self.sprites[a] = {}
      for d in [ 'east', 'south', 'west', 'north' ]:
        self.sprites[a][d] = []


    self.sprites['wait']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[1:2], 1, True))
    self.sprites['wait']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[4:5], 1, True))
    self.sprites['wait']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[7:8], 1, True))
    self.sprites['wait']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[10:11], 1, True))

    self.sprites['walk']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[0:2], 0.125, True))
    self.sprites['walk']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[3:5], 0.125, True))
    self.sprites['walk']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[6:8], 0.125, True))
    self.sprites['walk']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[9:11], 0.125, True))
    
    self.sprites['attack']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[0:2], 0.125, True))
    self.sprites['attack']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[3:5], 0.125, True))
    self.sprites['attack']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[6:8], 0.125, True))
    self.sprites['attack']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[9:11], 0.125, True))

    # Scheduel our update frequency
    self.update_task = task.LoopingCall(self.update)
    self.update_task.start(1/60.0)

  def unload(self):
    self.update_task.stop()

  def go(self, direction, start, speed):
    self.x = start[0]
    self.y = start[1]
    self.destx = start[0]
    self.desty = start[1]

    if speed == 'fast':
      self.speed = 4
    elif speed == 'slow':
      self.speed = 1

    if direction == 'north':
      self.desty += 1
      self.direction = 'north'
    elif direction == 'south':
      self.desty -= 1
      self.direction = 'south'
    elif direction == 'east':
      self.destx += 1
      self.direction = 'east'
    elif direction == 'west':
      self.destx -= 1
      self.direction = 'west'

  def attack(self):
    
    if self.action == 'wait':
      self.action = 'attack'
      pyglet.clock.schedule_once(self.wait,1.0)

  def wait(self,dt=0):

    self.action = 'wait'

  def die(self):
    
    self.action = 'wait'

  def stop(self):

    self.action = 'wait'    

  def update(self):
    
    # Don't move if we are doing something else
    if self.action in [ 'attack', 'die', 'cast' ]:
      return
    
    if self.direction == 'north':
      if self.spritey < self.desty * 32:
        self.spritey += self.speed
        self.action = 'walk'
      else:
        self.y = self.desty
        self.spritey = self.desty * 32
        self.action = 'wait'

    elif self.direction == 'south':
      if self.spritey > self.desty * 32:
        self.spritey -= self.speed
        self.action = 'walk'
      else:
        self.y = self.desty
        self.spritey = self.desty * 32
        self.action = 'wait'
    
    elif self.direction == 'east':
      if self.spritex < self.destx * 32:
        self.spritex += self.speed
        self.action = 'walk'
      else:
        self.x = self.destx
        self.spritex = self.destx * 32
        self.action = 'wait'
    
    elif self.direction == 'west':
      if self.spritex > self.destx * 32:
        self.spritex -= self.speed
        self.action = 'walk'
      else:
        self.x = self.destx
        self.spritex = self.destx * 32
        self.action = 'wait'
     

  def draw(self, target):
    draw_x = self.spritex 
    draw_y = self.spritey 
    self.sprites[self.action][self.direction].set_position(draw_x,draw_y)
    if target:
      self.label.bold = True
      self.label.font_size = 14
    else:
      self.label.bold = False
      self.label.font_size = 12

    self.sprites[self.action][self.direction].draw()
    self.label.x = self.spritex + (self.sprites[self.action][self.direction].width/2)
    self.label.y = self.spritey + self.sprites[self.action][self.direction].height
    self.label.draw()
