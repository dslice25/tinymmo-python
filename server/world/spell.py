class Spell:

  def __init__(self, name, title, caster_source, target_source, range, level, target_hp, target_mp, target_hit, target_dam, target_arm, caster_hp, caster_mp, caster_hit, caster_dam, caster_arm, description, mana_cost):
    
    self.title = title
    self.name = name

    # TODO: Load spell animations
    self.caster_source = caster_source
    self.target_source = target_source
    self.mana_cost = mana_cost
    self.description = description
    self.range = range
    self.level = level
    self.target_hp = target_hp
    self.target_mp = target_mp
    self.target_hit = target_hit
    self.target_dam = target_dam
    self.target_arm = target_arm
    self.caster_hp = caster_hp
    self.caster_mp = caster_mp
    self.caster_hit = caster_hit
    self.caster_dam = caster_dam
    self.caster_arm = caster_arm

  def state(self):

    return { 'title': self.title, 'name': self.name }

