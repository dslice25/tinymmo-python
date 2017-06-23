import pyglet
from animationset import AnimationSet

from twisted.internet import task

class Npc:

  def __init__(self, title, gender, body, hairstyle, haircolor, armor, head, weapon, x, y, villan):
    
    self.x = x
    self.y = y

    self.action    = 'wait'
    self.direction = 'south'
   
    self.title = title
    self.villan = villan

    # Movement
    self.destx = self.x
    self.desty = self.y
    self.spritex = self.x * 32
    self.spritey = self.y * 32

    self.speed = 1

    self.animation = AnimationSet(gender, body, hairstyle, haircolor, armor, head, weapon)
 
    label_color = (255,255,0,255)
    if self.villan:
      label_color = (255,0,0,255)
       
    self.label = pyglet.text.Label(self.title,
                                   font_name='Times New Roman',
                                   font_size=12,
                                   color=label_color,
                                   x=self.spritex,
                                   y=self.spritey,
                                   anchor_x="center",)

    # Scheduel our update frequency
    self.update_task = task.LoopingCall(self.update)
    self.update_task.start(1/60.0)

  def unload(self):
    self.update_task.stop()

  def wait(self, dt=0):
    self.action = 'wait'

  def go(self, direction, start, speed):

    self.wait()
  
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

  def slash(self):
    
    if self.action == 'wait':
      self.action = 'slash'

  def thrust(self):
    
    if self.action == 'wait':
      self.action = 'thrust'
      pyglet.clock.schedule_once(self.wait,1.5)
  
  def bow(self):
    
    if self.action == 'wait':
      self.action = 'bow'
      pyglet.clock.schedule_once(self.wait,1.5)

  def cast(self):
    
    if self.action == 'wait':
      self.action = 'cast'
      pyglet.clock.schedule_once(self.wait,1.5)

  def die(self):

    self.action = 'die'

  def update(self):
    # Don't move if we are doing something else
    if self.action in [ 'slash', 'die', 'cast', 'thrust', 'die', 'bow' ]:
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
    self.animation.draw(self.action, self.direction, self.spritex, self.spritey, )
    if target:
      self.label.bold = True
      self.label.font_size =  14
    else:
      self.label.bold = False
      self.label.font_size =  12
    
    self.label.x = self.spritex + 16
    self.label.y = self.spritey + 64
    self.label.draw()
