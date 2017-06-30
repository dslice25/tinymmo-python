import ConfigParser

def load_quests(world):

  config = ConfigParser.RawConfigParser()
  config.read('server_data/quests.ini')
  
  
  for name in config.sections():
    title = config.get(name,'title')
    dialog = config.get(name,'dialog')
    level = config.getint(name,'level')
    item_reward = config.get(name,'item_reward')
    exp_reward = config.getint(name,'exp_reward')
    gold_reward = config.getint(name,'gold_reward')
    requires = config.get(name,'requires')
    kill_target = config.get(name,'kill_target')
    kill_count  = config.getint(name,'kill_count')

    
    world.quests[name] = Quest(name, title, dialog, world, level, item_reward, exp_reward, gold_reward, requires, kill_target, kill_count)  
  

class Quest:
  '''
  Generates PlayerQuest objects. Held by Npc.
  '''
  def __init__(self, name, title, dialog, world, level, item_reward, exp_reward, gold_reward, requires, kill_target, kill_count):

    self.name        = name
    self.title       = title
    self.dialog      = dialog
    self.world       = world
    self.level       = level
    self.item_reward = item_reward
    self.exp_reward  = exp_reward
    self.gold_reward = gold_reward
    self.requires    = requires
    self.kill_target = kill_target
    self.kill_count  = kill_count

    print "Loaded QUEST %s" % self.name

  def assign(self, player_name):

    if self.avaliable_to(player_name):

      self.world.players[player_name].quests[self.name] = PlayerQuest(self.name,self.world)
    
      return { 'type': 'message', 'message': "You accept the quest." }
    
    else:
      return { 'type': 'message', 'message': "That quest is not avaliable." }

  def avaliable_to(self, player_name):
    
    # dont already have quest
    if self.world.players[player_name].quests.has_key(self.name):
      print "already have"
      return False 

    # player is appropriate level
    if self.world.players[player_name].level < self.level:
      print "wrong level"
      return False
    
    # player has completed prereqs
    if self.requires:
      if not self.world.players[player_name].quests.has_key(self.requires):
        print "don't have prereq"
        return False

      if not self.world.players[player_name].quests[self.requires].is_complete():
        print "dont have prereq complete"
        return False

    return True


class PlayerQuest:
  '''
  Track player quest progression.
  '''

  def __init__(self, name, world):

    self.name  = name
    self.world = world
    
    self.kill_count = 0
    self.item_count = 0
 
  def check_goal(self, target_name):
    target_name = target_name.split('-')
    
    if target_name[0] == self.world.quests[self.name].kill_target:
      self.kill_count += 1
     
  def is_complete(self):
    # Test if all goals are met
   
    if self.kill_count >= self.world.quests[self.name].kill_count:
      return True

    return False
    
  def get_log_entry(self):
  
    title = self.world.quests[self.name].title
    dialog = self.world.quests[self.name].dialog
    target = self.world.quests[self.name].kill_target
    count = [self.kill_count, self.world.quests[self.name].kill_count]

    return { 'title': title, 'dialog': dialog, 'target': target, 'count': count } 
