import pyglet
import time
from animationset import AnimationSet

from twisted.internet import task, reactor

class Player:

  def __init__(self, title, gender, body, hairstyle, haircolor, armor, head, weapon, x, y):
    
    self.x = x
    self.y = y
    self.action    = 'wait'
    self.direction = 'south'
    self.armor     = armor
    self.gender    = gender
    self.body      = body
    self.hairstyle = hairstyle
    self.haircolor = haircolor
    self.head      = head
    self.weapon    = weapon
    # Movement
    self.destx = self.x
    self.desty = self.y
    self.spritex = self.x * 32
    self.spritey = self.y * 32
    self.speed = 6
    
    self.path = []

    self.animation = AnimationSet(self.gender, self.body, self.hairstyle, self.haircolor, self.armor, self.head, self.weapon)
    
    self.title = title
    self.label = pyglet.text.Label(self.title,
                                   font_name='Times New Roman',
                                   font_size=12,
                                   color=(0,0,255,255),
                                   width=32,
                                   x=self.spritex,
                                   y=self.spritey)

    # Scheduel our update frequency
    self.update_task = task.LoopingCall(self.update)
    self.update_task.start(1/60.0)


    # Track all tasks
    self.tasks = []

  def unload(self):
    if self.update_task.running:
      self.update_task.stop()

  def set_weapon(self,weapon):

    self.weapon = weapon
    self.animation = AnimationSet(self.gender, self.body, self.hairstyle, self.haircolor, self.armor, self.head, self.weapon)

  def set_armor(self,armor):
    
    self.armor = armor
    self.animation = AnimationSet(self.gender, self.body, self.hairstyle, self.haircolor, self.armor, self.head, self.weapon)

  def set_head(self,head):
    
    self.head = head
    self.animation = AnimationSet(self.gender, self.body, self.hairstyle, self.haircolor, self.armor, self.head, self.weapon)

  def wait(self, dt=0):
    print "WAITING!"
    self.action = 'wait'

  def slash(self):
    
    if self.action == 'wait':
      self.action = 'slash'
      task.deferLater(reactor,1.5,self.wait)

  def thrust(self):
    
    if self.action == 'wait':
      self.action = 'thrust'
      task.deferLater(reactor,1.5,self.wait)
  
  def bow(self):
    
    if self.action == 'wait':
      self.action = 'bow'
      task.deferLater(reactor,1.5,self.wait)

  def cast(self):
    
    if self.action == 'wait':
      self.action = 'cast'
      task.deferLater(reactor,1.5,self.wait)

  def die(self):
    
    self.wait()
    self.action = 'die'

  def go(self, direction, start, end):
   
    self.direction = direction
    self.x = start[0]
    self.y = start[1]
    self.destx = end[0]
    self.desty = end[1]
    self.spritex = self.x * 32
    self.spritey = self.y * 32
  
  def pathfollow(self):

    if self.action == 'wait':
      if self.path:
        dest = self.path.pop(0)
        self.destx = dest[0]
        self.desty = dest[1]
        if dest[0] > self.x:
          self.direction = 'east'
        elif dest[0] < self.x:
          self.direction = 'west'
        if dest[1] > self.y:
          self.direction = 'north'
        elif dest[1] < self.y:
          self.direction = 'south'
   
  def update(self):
    # Don't move if we are doing something else
    if self.action in [ 'slash', 'die', 'cast', 'thrust', 'die', 'bow' ]:
      return
  
    self.pathfollow()
   
    self.action = 'wait'
       
    if self.direction == 'north':
      if self.spritey < self.desty * 32:
        self.spritey += self.speed
        self.action = 'walk'       
      else:
        self.spritey = self.desty * 32
        self.y = self.desty

    if self.direction == 'south':
      if self.spritey > self.desty * 32:
        self.spritey -= self.speed
        self.action = 'walk'       
      else:
        self.spritey = self.desty * 32
        self.y = self.desty

    if self.direction == 'east':
      if self.spritex < self.destx * 32:
        self.spritex += self.speed
        self.action = 'walk'       
      else:
        self.spritex = self.destx * 32
        self.x = self.destx
    
    if self.direction == 'west':
      if self.spritex > self.destx * 32:
        self.spritex -= self.speed
        self.action = 'walk'       
      else:
        self.spritex = self.destx * 32
        self.x = self.destx

  def draw(self, target):
    self.animation.draw(self.action, self.direction, self.spritex, self.spritey)
    self.label.x = self.spritex
    self.label.y = self.spritey + 64
    if target:
      self.label.bold = True
      self.label.font_size = 14
    else:
      self.label.bold = False
      self.label.font_size = 12
    self.label.draw()
