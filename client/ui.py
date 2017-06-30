import pyglet
from pyglet_gui.mixins import HighlightMixin
from pyglet_gui.manager import Manager
from pyglet_gui.buttons import Button, OneTimeButton, Checkbox, GroupButton
from pyglet_gui.scrollable import Scrollable
from pyglet_gui.document import Document
from pyglet_gui.constants import ANCHOR_CENTER, HALIGN_LEFT, HALIGN_RIGHT, ANCHOR_RIGHT, ANCHOR_TOP_LEFT, ANCHOR_BOTTOM_LEFT,ANCHOR_BOTTOM_RIGHT,ANCHOR_TOP,ANCHOR_TOP_RIGHT
from pyglet_gui.gui import Label,Graphic,Frame,PopupConfirm
from pyglet_gui.text_input import TextInput
from pyglet_gui.theme import Theme
from pyglet_gui.containers import VerticalContainer, HorizontalContainer, Spacer, GridContainer

import copy
import os
import json

UI_THEME = Theme(json.load(open('client_data/theme/mmo_theme.json','r')), resources_path='client_data/theme/')


class ConnectManager(Manager):
  
  def __init__(self, client):


    self.client = client

    self.connect_button = OneTimeButton(label="Connect", on_release=self.connect)
    self.server_field = TextInput("localhost")
    self.port_field = TextInput("10000")
    self.connect_container = VerticalContainer([self.connect_button, self.server_field, self.port_field])
    Manager.__init__(self, Frame(self.connect_container,path='connectFrame') , window=self.client.window,theme=UI_THEME)

  def connect(self, state):
    self.client.try_connect(self.server_field.get_text(),int(self.port_field.get_text()))

class LoginManager(Manager):
  
  def __init__(self, client):
    

    self.client = client
    self.login_button = OneTimeButton(label="Login", on_release=self.login)
    self.username_field = TextInput("")
    self.password_field = TextInput("")
    self.login_container = VerticalContainer([self.login_button, self.username_field, self.password_field])
    Manager.__init__(self, Frame(self.login_container), window=self.client.window,theme=UI_THEME)

  def login(self, state):
    self.client.try_login(self.username_field.get_text(),self.password_field.get_text())

class ChatWindowManager(Manager):
  
  def __init__(self, client):
    


    self.client = client
    self.message_container = VerticalContainer(content=[], align=HALIGN_LEFT)
    self.messages = Scrollable(height=100, width=300, is_fixed_size=True, content=self.message_container)
    self.text_input = TextInput("", length=20, max_length=256)
    self.send_button = OneTimeButton("Send", on_release=self.submit_message)
    self.enter_field = HorizontalContainer([self.text_input,self.send_button])
    self.chat_window = VerticalContainer([self.messages,self.enter_field])
    Manager.__init__(self, Frame(self.chat_window, path='chatFrame'), window=self.client.window, theme=UI_THEME, is_movable=True, anchor=ANCHOR_BOTTOM_LEFT)

  def add_message(self, message):

    step = 40
    for i in range(0, len(message), step):
      self.message_container.add(Label("> " + message[i:step], font_name='Lucida Grande'))
      step += 40

    self.text_input.set_text("")

  def submit_message(self, state):

    message = self.text_input.get_text()
    self.text_input.set_text("")

    if message[0] == "/":
      self.message_container.add(Label("> " + message, font_name='Lucida Grande', color=[200,200,255,255] ))
      self.client.command(message[1:].split(' '))
    else:
      self.client.chat(message)

class InventoryManager(Manager):

  def __init__(self, client, inventory):

    self.client = client

    invitems = []

    for name, value in inventory.items():
      title    = value['title']
      equipped = value['equipped']
      icon     = value['icon']
      hit      = value['hit']
      dam      = value['dam']
      arm      = value['arm']
      invitems.append(Frame(InventoryItem(name, title, equipped, icon, self.client, hit, dam, arm), is_expandable=True))
   
    self.close_button   = OneTimeButton(label='Close', on_release=self.close) 
    self.inventory_list = Scrollable(height=256, width=512, is_fixed_size=True, content=VerticalContainer(invitems, align=HALIGN_LEFT))
    self.inventory_container = VerticalContainer([self.inventory_list,self.close_button])
    Manager.__init__(self, Frame(self.inventory_container, is_expandable=True), window=self.client.window, theme=UI_THEME, is_movable=True, anchor=ANCHOR_BOTTOM_RIGHT)

  def close(self, toggle):
    self.delete()

class InventoryItem(HorizontalContainer):

  def __init__(self, name, title, equipped, icon, client, hit, dam, arm, desc=""):
   
    self.client = client
    self.name   = name
    self.title  = title
    icon        = Graphic(path=['icons', icon])
    title       = Label(self.title)
    stats       = HorizontalContainer([Label(str(dam), color=[255,100,100,255]),
                                       Label(str(hit), color=[100,100,255,255]),
                                       Label(str(arm), color=[100,255,100,255]),])
    button_text = 'Equip '
    if equipped:
      button_text = 'Remove'

    equip_button = Button(label=button_text, is_pressed=equipped, on_press=self.equip)
    use_button   = OneTimeButton(label='Use', on_release=self.use)
    drop_button  = OneTimeButton(label='Drop', on_release=self.confirm_drop)

    HorizontalContainer.__init__(self, [icon,title,stats,equip_button,use_button,drop_button], align=HALIGN_LEFT)

  def equip(self, toggle):
    
    if toggle:
      self.client.equip(self.name)
    else:
      self.client.unequip(self.name)

  def use(self, toggle):
    self.client.use(self.name)
    self.delete()

  def drop(self, toggle):
    self.client.drop(self.name)
    self.close(toggle)
    self.delete()

  def confirm_drop(self, toggle):
    self.client.popupManager = PopupConfirm(text="Drop your %s?" % self.title, window=self.client.window, theme=UI_THEME, on_ok=self.drop)
    self.client.popupManager.pop_to_top()
  
  def close(self, toggle):
    self.client.popupManager.delete()

    
class CharacterManager(Manager):

  def __init__(self, client, stats):

    self.client = client
    
    # Stats Container
    title = Label("%s" % (stats['title']), font_size=12)
    level = Label("%s" % (stats['level']), font_size=12)
    title_container = HorizontalContainer([title,level], align=HALIGN_LEFT)

    # HorizontalContainer
    hp_icon = Graphic(path=['icons','heart'])
    hp  = Label("%s/%s"  % (stats['hp'][0],stats['hp'][1]),font_size=10)
    hp_container = HorizontalContainer([hp_icon,hp], align=HALIGN_LEFT)

    # HorizontalContainer
    mp_icon = Graphic(path=['icons','potionBlue'])
    mp  = Label("%s/%s"  % (stats['mp'][0],stats['mp'][1]),font_size=10)
    mp_container = HorizontalContainer([mp_icon,mp], align=HALIGN_LEFT)
    
    # HorizontalContainer
    gold_icon = Graphic(path=['icons','coin'])
    gold = Label("%s" % stats['gold'],color=[255,255,255,255],font_size=12)
    gold_container = HorizontalContainer([gold_icon,gold], align=HALIGN_LEFT)
    
    # HorizontalContainer 
    dam_icon = Graphic(path=['icons','dagger'])
    dam = Label("%s" % stats['dam'],color=[255,100,100,255],font_size=10)
    dam_container = HorizontalContainer([dam_icon,dam], align=HALIGN_LEFT)

    hit_icon = Graphic(path=['icons','x'])
    hit = Label("%s" % stats['hit'],color=[100,100,255,255],font_size=12)
    hit_container = HorizontalContainer([hit_icon,hit], align=HALIGN_LEFT)
    
    arm_icon = Graphic(path=['icons','shieldSmall'])
    arm = Label("%s" % stats['arm'],color=[100,255,100,255],font_size=12)
    arm_container = HorizontalContainer([arm_icon,arm], align=HALIGN_LEFT)

    inv_button = OneTimeButton(label='Inventory', on_release=self.inventory)
    quest_button = OneTimeButton(label='Quest Log', on_release=self.questlog)
    logout_button = OneTimeButton(label='Logout', on_release=self.logout)
    
    #self.character_window = VerticalContainer([title, hp_icon, hp, mp_icon, mp, gold_icon, gold, dam, hit, arm, inv_button, quest_button, logout_button])
    self.character_window = VerticalContainer([title_container, hp_container, mp_container, gold_container, dam_container, hit_container, arm_container, inv_button, quest_button, logout_button], align=HALIGN_LEFT)

    Manager.__init__(self, Frame(self.character_window), window=self.client.window, theme=UI_THEME, is_movable=False, anchor=ANCHOR_TOP_RIGHT)

  def inventory(self, toggle):
    self.client.get_inventory()

  def questlog(self, toggle):
    self.client.get_questlog()

  def logout(self, toggle):
    print "logging out..."


class ShopManager(Manager):

  def __init__(self, client, inventory=[], player_inventory=[]):

    self.client = client

    invitems = []

    for name, value in inventory.items():
      title = value['title']
      icon  = value['icon']
      dam   = value['dam']
      hit   = value['hit']
      arm   = value['arm']
      gold  = value['value']
      invitems.append(Frame(ShopItem(name, title, icon, self.client, dam, hit, arm, gold), is_expandable=True))
    
    self.shop_inventory_list = Scrollable(height=256, width=512, is_fixed_size=True, content=VerticalContainer(invitems, align=HALIGN_LEFT))

    player_invitems = []    
    for name, value in player_inventory.items():
      title = value['title']
      icon  = value['icon']
      dam   = value['dam']
      hit   = value['hit']
      arm   = value['arm']
      player_invitems.append(Frame(PlayerShopItem(name, title, icon, self.client, dam, hit, arm), is_expandable=True))
    
    self.player_inventory_list = Scrollable(height=256, width=512, is_fixed_size=True, content=VerticalContainer(player_invitems, align=HALIGN_LEFT))


    self.exit_button = OneTimeButton(label='Close', on_release=self.close)
    self.inventory_container = HorizontalContainer([self.shop_inventory_list, self.player_inventory_list, self.exit_button])

    Manager.__init__(self, Frame(self.inventory_container,is_expandable=True), window=self.client.window, theme=UI_THEME, is_movable=True)

  def close(self, toggle):
    self.delete()

class ShopItem(HorizontalContainer):

  def __init__(self, name, title, icon, client, dam, hit, arm, gold, desc=""):
   
    self.client = client
    self.name   = name
    self.title  = title
    icon        = Graphic(path=['icons', icon])
    title       = Label(self.title)
    gold        = Label("%sg" % gold, color=[230,244,68,255])
    stats       = HorizontalContainer([Label(str(dam), color=[255,100,100,255]),
                                     Label(str(hit), color=[100,100,255,255]),
                                     Label(str(arm), color=[100,255,100,255]),])

    buy_button = OneTimeButton(label='Buy', on_release=self.confirm) 
    HorizontalContainer.__init__(self, [icon,title,gold,stats,buy_button], align=HALIGN_LEFT)

  def confirm(self, toggle):
    self.client.popupManager = PopupConfirm(text="Buy a %s?" % self.title, window=self.client.window, theme=UI_THEME, on_ok=self.buy)
    self.client.popupManager.pop_to_top()
    
  def close(self, toggle):
    self.client.popupManager.delete()

  def buy(self, toggle):
    self.client.buy(self.name)
    self.close(toggle)

class PlayerShopItem(HorizontalContainer):

  def __init__(self, name, title, icon, client, dam, hit, arm, gold=0, desc=""):
   
    self.client = client
    self.name   = name
    self.title  = title
    icon        = Graphic(path=['icons', icon])
    title       = Label(self.title)
    gold        = Label("%sg" % gold, color=[230,244,68,255])
    stats       = HorizontalContainer([Label(str(dam), color=[255,100,100,255]),
                                     Label(str(hit), color=[100,100,255,255]),
                                     Label(str(arm), color=[100,255,100,255]),])

    sell_button = OneTimeButton(label='Sell', on_release=self.confirm) 
    HorizontalContainer.__init__(self, [icon,title,gold,stats,sell_button], align=HALIGN_LEFT)

  def confirm(self, toggle):
    self.client.popupManager = PopupConfirm(text="Sell your %s?" % self.title, window=self.client.window, theme=UI_THEME, on_ok=self.sell)
    self.client.popupManager.pop_to_top()
    
  def close(self, toggle):
    self.client.popupManager.delete()

  def sell(self, toggle):
    self.client.sell(self.name)
    self.close(toggle)
    self.delete()

class ContainerManager(Manager):

  def __init__(self, client, inventory=[]):

    self.client = client

    invitems = []

    for name, value in inventory.items():
      title = value['title']
      icon  = value['icon']
      dam   = value['dam']
      hit   = value['hit']
      arm   = value['arm']
      gold  = value['value']
      invitems.append(Frame(ContainerItem(name, title, icon, self.client, dam, hit, arm, gold), is_expandable=True))
    
    self.container_inventory_list = Scrollable(height=256, width=512, is_fixed_size=True, content=VerticalContainer(invitems, align=HALIGN_LEFT))

    self.exit_button = OneTimeButton(label='Close', on_release=self.close)
    self.inventory_container = HorizontalContainer([self.container_inventory_list, self.exit_button])

    Manager.__init__(self, Frame(self.inventory_container,is_expandable=True), window=self.client.window, theme=UI_THEME, is_movable=True)

  def close(self, toggle):
    self.delete()

class ContainerItem(HorizontalContainer):

  def __init__(self, name, title, icon, client, dam, hit, arm, gold, desc=""):
   
    self.client = client
    self.name   = name
    self.title  = title
    icon        = Graphic(path=['icons', icon])
    title       = Label(self.title)
    gold        = Label("%sg" % gold, color=[230,244,68,255])
    stats       = HorizontalContainer([Label(str(dam), color=[255,100,100,255]),
                                     Label(str(hit), color=[100,100,255,255]),
                                     Label(str(arm), color=[100,255,100,255]),])

    take_button = OneTimeButton(label='Take', on_release=self.take) 
    
    HorizontalContainer.__init__(self, [icon,title,gold,stats,take_button], align=HALIGN_LEFT)

  def take(self, toggle):
    self.client.take(self.name)
    self.delete()

class QuestDialogManager(Manager):

  def __init__(self, client, name, title, dialog):

    self.client = client
    self.name   = name
    title       = Label(title, font_size=12)
    dialog      = pyglet.text.decode_text(dialog)
    document    = Document(dialog, width=300, height=100)


    accept_button = OneTimeButton(label="Ok, I'll do it!", on_release=self.accept)
    reject_button = OneTimeButton(label="No, Thanks.", on_release=self.reject)

    text_container   = VerticalContainer([title,document])
    button_container = HorizontalContainer([accept_button,reject_button])
    quest_container  = VerticalContainer([text_container,button_container])
    
    Manager.__init__(self, Frame(quest_container, is_expandable=True), window=self.client.window, theme=UI_THEME, is_movable=True)

  def accept(self, toggle):
    self.client.accept_quest(self.name)
    self.delete()

  def reject(self, toggle):
    self.delete()

class QuestLogManager(Manager):

  def __init__(self, client, quests):

    self.client = client
    
    quest_list = []
    for quest in quests:
      quest_title = Label(quest['title'])
      quest_container = HorizontalContainer([quest_title])
      quest_list.append(quest_container)


    close_button = OneTimeButton(label="Close", on_release=self.close)

    quest_container = VerticalContainer(quest_list)
    button_container = HorizontalContainer([close_button])

    questlog_container = VerticalContainer([quest_container,button_container])

    Manager.__init__(self, Frame(questlog_container, is_expandable=True), window=self.client.window, theme=UI_THEME, is_movable=True)

  def close(self, toggle):
    self.delete()

