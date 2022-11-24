from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()

window.fps_counter.enabled=False
window.exit_button.enabled=False

random.seed(0)

Entity.default_shader = lit_with_shadows_shader

window.fullscreen = True

Sky()
ground = Entity(model='plane', scale=(200, 5, 200), texture="grass",collider='mesh')

player = FirstPersonController(origin_y=-.5, speed=15, origin_x = 6)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))

zid1 = Entity(model='cube',texture='zid',collider='cube',scale=(200,10,5),position=(0,5,100))
zid2 = duplicate(zid1, z=-100)
zid3 = duplicate(zid1, rotation_y=90,x=-100,z=0)
zid4 = duplicate(zid3, x=100)

gun = Entity(model='modeli\pistolj', parent=camera, position=(.4,-.35,.75),
             scale=(0.07),rotation_y=180, origin_z=2.5, texture='modeli\pistolj',
             on_cooldown=False,collider='mesh')
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad',
                          color=color.yellow, enabled=False)

puska = Entity(model="modeli/shotgun.obj", parent=camera, scale=.05, 
              on_cooldown=False,position=(0.6, -0.9,2.59),rotation=(266,32,136),color=color.black)
puska.muzzle_flash = Entity(parent=puska, z=1, world_scale=.5, model='quad', enabled=True)
puska.enabled = False

label = Text(
  text = f'Meci: {0}/{0}',
  color=color.black,
  position=(0.7, -0.4),
  scale=1
)

slikameci = Button(texture='modeli\\meci',position=(0.67,-0.4),scale=.04,color=color.white,enabled=False)
slikapatroni = Button(texture='modeli\\patroni',position=(0.67,-0.4),scale=.04,color=color.white,enabled=False)

player.cursor.color = color.white
player.cursor.texture='modeli\\scope'
player.cursor.scale=(0.1)
player.cursor.rotation_z = (90)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent

muzika = Audio("modeli\intro.wav")

naslov = Text(text='GVZD Shooter by Aleksandar Simic', scale=3, x=-0.60,
             y=0.40,visible=False ,color=color.green)

naslov2 = Text(text='PAUZA', scale=5, x=-0.20,
             y=0.30,visible=False ,color=color.green)

levellabel = Text(text='Levelup', scale=5, x=-0.20, y=0.30,visible=False ,color=color.green)
pobedalabel = Text(text='Game Over - POBEDA', scale=5, x=-0.60, y=0.30,visible=False ,color=color.green)

button = Button(position=(-.01, .11),texture='modeli\\nastavi',color=color.white,highlight_color=color.turquoise,
                scale=(0.3,0.1),text_color=color.black)
button.enabled = False
button2 = Button(position=(-.01, -.01),texture='modeli\\opcije',color=color.white,highlight_color=color.turquoise,
                scale=(0.3,0.1),text_color=color.black)
button2.enabled = False
button3 = Button(position=(-.01, -.13),texture='modeli\\izadji',color=color.white,highlight_color=color.turquoise,
                scale=(0.3,0.1),text_color=color.black)
button3.enabled = False

button4 = Button(position=(-.01, .11),texture='modeli\\igraj',color=color.white,highlight_color=color.turquoise,
                scale=(0.3,0.1),text_color=color.black)
button4.enabled = False

def starttimer():
  novit = 15
  while novit > 0:
    novit -= 1
  if novit <= 0:
    novit = 0

def startuj():
  naslov.visible = False
  button2.enabled = False
  button3.enabled = False
  button4.enabled = False
  mouse.locked = True
  mouse.visible = False
  label.visible = True
  muzika.stop()
  starttimer()
  if drzi == 0:
    puska.enabled = True
    slikapatroni.enabled = True
    gun.enabled = False
    slikameci.enabled = False
  elif drzi == 1:
    puska.enabled = False
    slikapatroni.enabled = False
    gun.enabled = True
    slikameci.enabled = True

  application.paused = not application.paused

naslov.visible = True
button2.enabled = True
button3.enabled = True
button3.on_click = application.quit
button4.enabled = True
button4.on_click = startuj
mouse.locked = False
mouse.visible = True
puska.enabled = False
slikapatroni.enabled = False
gun.enabled = False
slikameci.enabled = False
label.visible = False
application.paused = not application.paused
muzika.play()

t = 2
while t > 0:
  time.sleep(1)
  t -= 1
if t <= 0:
  t = 0
  novit = 15

level = 1
neprijatelji = 1

from ursina.prefabs.health_bar import HealthBar

class Enemy(Entity):
  def __init__(self, **kwargs):
    super().__init__(parent=shootables_parent, model='modeli\man.fbx',texture="modeli\orc",
                      position=(-5,0.0,6.7),scale=0.1,double_sided=True, origin_y=-.5,collider='mesh', **kwargs)

    self.health_bar = Entity(parent=self, y=18, model='cube', color=color.red,
                              world_scale=(1.5,.1,.1))
    self.max_hp = 100
    self.hp = self.max_hp

  def update(self):
    dist = distance_xz(player.position, self.position)

    self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


    self.look_at_2d(player.position, 'y')
    hit_info = raycast(self.world_position + Vec3(0,2,0), self.forward, 30, ignore=(self,))
    if hit_info.entity == player:
        if dist > 2:
            self.position += self.forward * time.dt * 29

  @property
  def hp(self):
    return self._hp

  @hp.setter
  def hp(self, value):
    global neprijatelji
    self._hp = value
    levellabel.visible = False
    if value <= 0:
        destroy(self)
        Audio("modeli\\beep.wav")
        neprijatelji -= 1
        
        if neprijatelji == 0:
          kreiraj()
        return

    self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
    self.health_bar.alpha = 1

# Enemy()
enemies = [Enemy(x=1)]

class Enemy2(Entity):
  def __init__(self, **kwargs):
    super().__init__(parent=shootables_parent, model='modeli\spider',color=color.black,
                      position=(-5,0.0,6.7),scale=0.05,double_sided=True,collider='box', **kwargs)

    self.health_bar = Entity(parent=self, y=18, model='cube', color=color.red,
                              world_scale=(1.5,.1,.1))
    self.max_hp = 200
    self.hp = self.max_hp

  def update(self):
    dist = distance_xz(player.position, self.position)
    self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
    self.look_at_2d(player.position, 'y')
    hit_info = raycast(self.world_position + Vec3(0,2,0), self.forward, 30, ignore=(self,))
    if hit_info.entity == player:
      self.position += self.forward * time.dt * 89

  @property
  def hp(self):
    return self._hp

  @hp.setter
  def hp(self, value):
    global neprijatelji
    self._hp = value
    levellabel.visible = False
    if value <= 0:
        destroy(self)
        Audio("modeli\\beep.wav")
        neprijatelji -= 1
        
        if neprijatelji == 0:
          kreiraj()
        return

    self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
    self.health_bar.alpha = 1

class Enemy3(Entity):
  def __init__(self, **kwargs):
    super().__init__(parent=shootables_parent, model='modeli\\robot',color=color.black,
                      position=(-5,0.0,6.7),scale=0.04,double_sided=True,collider='box', **kwargs)

    self.health_bar = Entity(parent=self, y=18, model='cube', color=color.red,
                              world_scale=(1.5,.1,.1))
    self.max_hp = 500
    self.hp = self.max_hp

  def update(self):
    dist = distance_xz(player.position, self.position)
    self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
    self.look_at_2d(player.position, 'y')
    hit_info = raycast(self.world_position + Vec3(0,2,0), self.forward, 30, ignore=(self,))
    if hit_info.entity == player:
      self.position += self.forward * time.dt * 59

  @property
  def hp(self):
    return self._hp

  @hp.setter
  def hp(self, value):
    global neprijatelji
    self._hp = value
    if value <= 0:
        destroy(self)
        muzika.play()
        levellabel.visible = False
        pobedalabel.visible = True
        return

    self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
    self.health_bar.alpha = 1

sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()

def kreiraj():
  global neprijatelji,level,levellabel
  level += 1
  neprijatelji = level
  levellabel.visible = True
  if level <= 5:
    enemies = [Enemy(x=x*level) for x in range(level)]
  elif level == 6:
    enemies2 = [Enemy2(x=x*level) for x in range(level)]
  elif level == 7:
    enemies2 = [Enemy2(x=x*level) for x in range(level)]
  elif level == 8:
    enemies3 = [Enemy3(x=x*1) for x in range(1)]


meci = 10
sarzer = 30
ispaljenimeci = 0
drzi = 1

def input(key):
  global meci, sarzer, ispaljenimeci, drzi

  if key =='1':
    if drzi == 0:
      drzi = 1
      meci = 10
      sarzer = 30
      gun.enabled = True
      slikameci.enabled = True
      puska.enabled = False
      slikapatroni.enabled = False

  if key =='2':
    if drzi == 1:
      drzi = 0
      meci = 7
      sarzer = 21
      gun.enabled = False
      slikameci.enabled = False
      puska.enabled = True
      slikapatroni.enabled = True

  if key == 'r':
    if drzi == 0:
      if meci <= 6:
        if sarzer > 0:
          if ispaljenimeci > sarzer:
            meci += sarzer
            sarzer = 0
            ispaljenimeci = 0
            Audio("modeli\\reload.wav")
          else:
            sarzer -= ispaljenimeci
            meci += ispaljenimeci
            ispaljenimeci = 0
            Audio("modeli\\reload.wav")

    elif drzi == 1:
      if meci <= 9:
        if sarzer > 0:
          if ispaljenimeci > sarzer:
            meci += sarzer
            sarzer = 0
            ispaljenimeci = 0
            Audio("modeli\\reload.wav")
          else:
            sarzer -= ispaljenimeci
            meci += ispaljenimeci
            ispaljenimeci = 0
            Audio("modeli\\reload.wav")
  
  if key=="left mouse down":
    if meci > 0:
      meci -= 1
      ispaljenimeci += 1
      if drzi == 1:
        shoot()
        Audio("modeli\gunshot.wav")
        player.cursor.tooltip = Tooltip('-asdasdasdasd25')
      elif drzi == 0:
        rafal()
        Audio("modeli\puska.wav")
    elif meci <= 0:
      player.cursor.shake(duration=0.8)
      Audio("modeli\prazno.wav")
  
  if held_keys["left shift"]:
    player.speed=45
  else:
    player.speed = 10

  if held_keys['left mouse']:
    if drzi == 0:
      puska.rotation_x = 260
    elif drzi == 1:
      gun.rotation_x = 10
  else:
    if drzi == 0:
      puska.rotation_x = 266
    elif drzi == 1:
      gun.rotation_x = -0.0

def update():

  if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
    player.cursor.color = color.green
  else:
    player.cursor.color = color.white

  label.text = f'Meci: {meci}/{sarzer}'

kliknuo = 0
def pause_input(key):
  global kliknuo
  if key == 'escape':
    application.paused = not application.paused
    label.visible = not label.visible
    if pobedalabel.visible == True:
      pobedalabel.visible = False

    if kliknuo == 0:
      kliknuo = 1
      naslov.visible = True
      naslov2.visible = True
      button.enabled = True
      button.on_click = klik
      button2.enabled = True
      button3.enabled = True
      button3.on_click = application.quit
      puska.enabled = False
      slikapatroni.enabled = False
      gun.enabled = False
      slikameci.enabled = False
      mouse.locked = False
      mouse.visible = True
    elif kliknuo == 1:
      kliknuo = 0
      naslov.visible = False
      naslov2.visible = False
      button.enabled = False
      button2.enabled = False
      button3.enabled = False
      mouse.locked = True
      mouse.visible = False
      if drzi == 0:
        puska.enabled = True
        slikapatroni.enabled = True
        gun.enabled = False
        slikameci.enabled = False
      elif drzi == 1:
        puska.enabled = False
        slikapatroni.enabled = False
        gun.enabled = True
        slikameci.enabled = True
        
pause_handler = Entity(ignore_paused=True, input=pause_input)

def klik():
  global kliknuo
  kliknuo = 0
  naslov.visible = False
  naslov2.visible = False
  button.enabled = False
  button2.enabled = False
  button3.enabled = False
  mouse.locked = True
  mouse.visible = False
  if drzi == 0:
    puska.enabled = True
    slikapatroni.enabled = True
    gun.enabled = False
    slikameci.enabled = False
  elif drzi == 1:
    puska.enabled = False
    slikapatroni.enabled = False
    gun.enabled = True
    slikameci.enabled = True

  application.paused = not application.paused
  label.visible = not label.visible

def shoot():
  if not gun.on_cooldown:
    gun.on_cooldown = True
    gun.muzzle_flash.enabled=True
    from ursina.prefabs.ursfx import ursfx
    ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)],
          pitch=random.uniform(-13,-12),
          pitch_change=-12, speed=3.0)

    invoke(gun.muzzle_flash.disable, delay=.05)
    invoke(setattr, gun, 'on_cooldown', False, delay=.15)
    if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
        mouse.hovered_entity.hp -= 25
        mouse.hovered_entity.blink(color.red)

def rafal():
  if not puska.on_cooldown:
    puska.on_cooldown = True
    puska.muzzle_flash.enabled=False
    from ursina.prefabs.ursfx import ursfx
    ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)],
          pitch=random.uniform(-13,-12),
          pitch_change=-12, speed=-1.0)

    invoke(puska.muzzle_flash.disable, delay=.01)
    invoke(setattr, puska, 'on_cooldown', False, delay=-.05)
    if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
        mouse.hovered_entity.hp -= 255
        mouse.hovered_entity.blink(color.red)

app.run()