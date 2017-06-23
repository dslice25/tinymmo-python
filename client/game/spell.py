import pyglet

class Spell:

  def __init__(self, caster_source, target_source, caster, target):
    
    self.caster_grid = []
    self.target_grid = []
    
    if caster_source:
      caster_raw = pyglet.image.load(caster_source)
      self.caster_grid = pyglet.image.ImageGrid(caster_raw, 4, 4)
    
    if target_source:
      target_raw = pyglet.image.load(target_source)
      self.target_grid = pyglet.image.ImageGrid(target_raw, 4, 4)

    if self.caster_grid:
      self.caster_animation = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(self.caster_grid, 0.2, True))
    
    if self.target_grid:
      self.target_animation = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(self.target_grid, 0.2, True))

    self.caster_x = caster.spritex
    self.caster_y = caster.spritey

    self.target_x = target.spritex
    self.target_y = target.spritey

    self.timer = 5
    self.expired = False
    
    pyglet.clock.schedule_once(self.expireme, 3.0)

  def expireme(self,dt):
    
    print "I'm expired!"
    self.expired = True

  def draw(self):
    if self.caster_grid:
      self.caster_animation.set_position(self.caster_x - 16 - 32, self.caster_y - 32)
      self.caster_animation.draw()
    
    if self.target_grid:
      self.target_animation.set_position(self.target_x - 16 - 32, self.target_y - 32)
      self.target_animation.draw()

