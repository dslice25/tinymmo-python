import pyglet

class SoundSet:
  
  def __init__(self):
  
    self.sounds = {}
    self.sounds['melee'] = pyglet.media.load('data/melee sounds/melee sound.wav')
    self.sounds['sword'] = pyglet.media.load('data/melee sounds/sword sound.wav')
    self.sounds['animal'] = pyglet.media.load('data/melee sounds/animal melee sound.wav')

    self.player = pyglet.media.Player()

  def play(self, sound):
    
    if self.player.source != self.sounds[sound]:    
      self.player.queue(self.sounds[sound]) 

    

