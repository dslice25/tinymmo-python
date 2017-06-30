import pyglet
from PIL import Image
import sys

class AnimationSet:

  cache = {}

  def __init__(self, gender, body, hairstyle, haircolor, armor, head, weapon):
   
   
    # Generate image if it doesn't exist already
    self.gender = gender
    self.body = body
    self.haircolor = haircolor
    self.hairstyle = hairstyle
    self.armor = armor
    self.head = head
    self.weapon = weapon
    
    raw = None
    source = "%s_%s_%s_%s_%s_%s_%s" % ( self.gender, self.body, self.hairstyle, self.haircolor, self.armor, self.head, self.weapon )
    if source in self.cache.keys():
      raw = self.cache[source]
    else:
      raw = self.build()
      self.cache[source] = raw

    grid = pyglet.image.ImageGrid(raw, 21, 13)

    self.sprites = {}
    for a in [ 'die', 'bow', 'slash', 'wait', 'walk', 'thrust', 'cast' ]:
      self.sprites[a] = {}
      for d in [ 'east', 'south', 'west', 'north' ]:
        self.sprites[a][d] = []
    
    self.sprites['die']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[0:6], 0.15, False))
    self.sprites['die']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[0:6], 0.15, False))
    self.sprites['die']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[0:6], 0.15, False))
    self.sprites['die']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[0:6], 0.15, False))

    self.sprites['bow']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[13:26], 0.077, True))
    self.sprites['bow']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[26:39], 0.077, True))
    self.sprites['bow']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[39:52], 0.077, True))
    self.sprites['bow']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[52:65], 0.077, True))

    self.sprites['slash']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[65:71], 0.125, True))
    self.sprites['slash']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[78:84], 0.125, True))
    self.sprites['slash']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[91:97], 0.125, True))
    self.sprites['slash']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[104:110], 0.125, True))
    
    self.sprites['wait']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[117:118], 1, True))
    self.sprites['wait']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[130:131], 1, True))
    self.sprites['wait']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[143:144], 1, True))
    self.sprites['wait']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[156:157], 1, True))

    self.sprites['walk']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[118:126], 0.1, True))
    self.sprites['walk']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[131:139], 0.1, True))
    self.sprites['walk']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[144:152], 0.1, True))
    self.sprites['walk']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[157:165], 0.1, True))

    self.sprites['thrust']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[169:177], 0.166, True))
    self.sprites['thrust']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[182:190], 0.166, True))
    self.sprites['thrust']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[195:203], 0.166, True))
    self.sprites['thrust']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[208:216], 0.166, True))
    
    self.sprites['cast']['east'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[223:228], 0.177, True))
    self.sprites['cast']['south'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[236:241], 0.177, True))
    self.sprites['cast']['west'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[248:253], 0.177, True))
    self.sprites['cast']['north'] = pyglet.sprite.Sprite(pyglet.image.Animation.from_image_sequence(grid[261:266], 0.177, True))
 
  
  def draw(self, action, direction, x, y):
    self.sprites[action][direction].set_position(x - 16, y )
    self.sprites[action][direction].draw()


  def build(self):

    hair_path = None 
    torso_path = None
    hands_path = None
    legs_path = None
    feet_path = None
    shoulders_path = None
    head_path = None
    weapon_path = None
    back_path = None
    ammo_path = None
    
    base = 'client_data/Universal-LPC-spritesheet/'

    body_path = base + "body/%s/%s.png" % ( self.gender, self.body )
    
    if self.hairstyle != 'none': 
      hair_path = base + "hair/%s/%s/%s.png" % (self.gender, self.hairstyle, self.haircolor)
      
    if self.armor.startswith('clothes'):
      # format is "clothes[_pantscolor_shirtcolor]"
      clothes = self.armor.split("_")
      shirt_color   = 'maroon'
      pants_color   = 'white'
      if len(clothes) > 2:
        pants_color = clothes[1]
        shirt_color = clothes[2]
      legs_path = base + "legs/pants/%s/%s_pants_%s.png" % ( self.gender, pants_color, self.gender )
      feet_path = base + "feet/shoes/%s/black_shoes_%s.png" % ( self.gender, self.gender )
      if self.gender == 'male':
        torso_path = base + "torso/shirts/longsleeve/male/%s_longsleeve.png" % shirt_color
      elif self.gender == 'female':
        torso_path = base + "torso/shirts/sleeveless/female/%s_sleeveless.png" % shirt_color
    elif self.armor == 'leather':
      hands_path = base + "hands/bracers/%s/leather_bracers_%s.png" % (self.gender, self.gender)
      torso_path = base + "torso/leather/chest_%s.png" % self.gender
      shoulders_path = base + "torso/leather/shoulders_%s.png" % self.gender
      feet_path = base + "feet/shoes/%s/black_shoes_%s.png" % ( self.gender, self.gender )
      legs_path = base + "legs/pants/%s/white_pants_%s.png" % ( self.gender, self.gender )
    elif self.armor == 'chain':
      hands_path = base + "hands/bracers/%s/leather_bracers_%s.png" % (self.gender, self.gender)
      torso_path = base + "torso/chain/mail_%s.png" % self.gender
      shoulders_path = base + "torso/leather/shoulders_%s.png" % self.gender
      feet_path = base + "feet/shoes/%s/black_shoes_%s.png" % ( self.gender, self.gender )
      legs_path = base + "legs/pants/%s/white_pants_%s.png" % ( self.gender, self.gender )
    elif self.armor == 'plate':
      hands_path = base + "hands/gloves/%s/metal_gloves_%s.png" % (self.gender, self.gender)
      torso_path = base + "torso/plate/chest_%s.png" % self.gender
      shoulders_path = base + "torso/plate/arms_%s.png" % self.gender
      feet_path = base + "feet/armor/%s/metal_boots_%s.png" % (self.gender, self.gender)
      legs_path = base + "legs/armor/%s/metal_pants_%s.png" % (self.gender, self.gender)

    if self.head == 'hat':
      head_path = base + "head/caps/%s/leather_cap_%s.png" % (self.gender, self.gender)
    elif self.head == 'clothhood':
      head_path = base + "head/hoods/%s/cloth_hood_%s.png" % (self.gender, self.gender)
    elif self.head == 'chainhood':
      head_path = base + "head/hoods/%s/chain_hood_%s.png" % (self.gender, self.gender)
    elif self.head == 'chainhat':
      head_path = base + "head/helms/%s/chainhat_%s.png" % (self.gender, self.gender)
    elif self.head == 'helm':
      head_path = base + "head/helms/%s/metal_helm_%s.png" % (self.gender, self.gender)

    if self.weapon == 'bow':
      if self.body == 'skeleton':
        weapon_path = base + "weapons/right hand/either/bow_skeleton.png"
      else:
        weapon_path = base + "weapons/right hand/either/bow.png"
      back_path = base + "behind_body/equipment/quiver.png"
      ammo_path = base + "weapons/left hand/either/arrow.png"
    elif self.weapon == 'sword':
      weapon_path = base + "weapons/right hand/%s/dagger_%s.png" % (self.gender, self.gender)
    elif self.weapon == 'spear':
      weapon_path = base + "weapons/right hand/%s/spear_%s.png" % (self.gender, self.gender)
    elif self.weapon == 'wand':
      weapon_path = base + "weapons/right hand/%s/woodwand_%s.png" % (self.gender, self.gender)
    
    # Generate image
    body_img = Image.open(body_path).convert('RGBA')
    torso_img = Image.open(torso_path).convert('RGBA')
    if hands_path:
      hands_img = Image.open(hands_path).convert('RGBA')
    else:
      hands_img = None
    if shoulders_path:
      shoulders_img = Image.open(shoulders_path).convert('RGBA')
    else:
      shoulders_img = None
    legs_img = Image.open(legs_path).convert('RGBA')
    feet_img = Image.open(feet_path).convert('RGBA')
    if hair_path:
      hair_img = Image.open(hair_path).convert('RGBA')
    if head_path:
      head_img = Image.open(head_path).convert('RGBA')
    else:
      head_img = None
    if weapon_path:
      weapon_img = Image.open(weapon_path).convert('RGBA')
    else:
      weapon_img = None
    if back_path:
      back_img = Image.open(back_path).convert('RGBA')
    else:
      back_img = None
    if ammo_path:
      ammo_img = Image.open(ammo_path).convert('RGBA')
    else:
      ammo_img = None

    final = Image.new('RGBA', (832,1344), (255,255,255,0))
    
    # BACK
    if back_path:
      final.paste(back_img, (0,0), back_img)
    # BODY
    final.paste(body_img, (0,0), body_img)
    # FEET
    final.paste(feet_img, (0,0), feet_img)
    # LEGS
    final.paste(legs_img, (0,0), legs_img)
    # TORSO
    final.paste(torso_img, (0,0), torso_img)
    # HANDS
    if hands_path:
      final.paste(hands_img, (0,0), hands_img)
    # SHOULDERS
    if shoulders_path:
      final.paste(shoulders_img, (0,0), shoulders_img)
    # HAIR
    if hair_path:
      final.paste(hair_img, (0,0), hair_img)
    # HEAD
    if head_path:
      final.paste(head_img, (0,0), head_img)
    # WEAPON
    if weapon_path:
      final.paste(weapon_img, (0,0), weapon_img)
    # AMMO
    if ammo_path:
      final.paste(ammo_img, (0,0), ammo_img)

    final = final.transpose(Image.FLIP_TOP_BOTTOM)
    raw_final = final.tobytes()

    return pyglet.image.ImageData(832,1344,'RGBA',raw_final)
