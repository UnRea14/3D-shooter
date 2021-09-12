import FPS_Camera
from ursina import *
from Textures_Audio import box_texture, ground_texture, sky_texture


class Gun(Entity):
    def __init__(self):
        super().__init__(
            parent=camera.ui,
            model=r'assets/Objects/m4.obj',
            color=color.red,
            scale=0.05,
            rotation=Vec2(-5, -15),
            position=Vec2(0.9, -0.9))

    def active(self):
        self.rotation = (0, -15)

    def passive(self):
        self.rotation = (-5, -15)


keys_dict = {'q': False, 'left mouse': False, 'm': False, 'w': False, 'r': False}

# borders
border1 = Entity(parent=scene, model='quad', scale=100, collider='box', position=(0, 50, 0), visible=False)
border2 = Entity(parent=scene, model='quad', scale=100, collider='box', position=(50, 50, -50), rotation=(0, 90, 0),
                 visible=False)
border3 = Entity(parent=scene, model='quad', scale=100, collider='box', position=(-50, 50, -50),
                 rotation=(0, 90, 0),
                 visible=False)
border4 = Entity(parent=scene, model='quad', scale=100, collider='box', position=(0, 50, -100), visible=False)

# boxes
box1 = Entity(parent=scene, texture=box_texture, model='assets/Objects/block.obj', collider='box',
              position=(5, 1.3, -26),
              scale=1.3)
box2 = Entity(parent=scene, texture=box_texture, model='assets/Objects/block.obj', collider='box',
              position=(-25, 1.3, -56),
              scale=1.3)
box3 = Entity(parent=scene, texture=box_texture, model='assets/Objects/block.obj', collider='box',
              position=(35, 1.3, -70),
              scale=1.3)
box4 = Entity(parent=scene, texture=box_texture, model='assets/Objects/block.obj', collider='box',
              position=(25, 1.3, -41),
              scale=1.3)
box5 = Entity(parent=scene, texture=box_texture, model='assets/Objects/block.obj', collider='box',
              position=(-30, 1.3, -80),
              scale=1.3)
box6 = Entity(parent=scene, texture=box_texture, model='assets/Objects/block.obj', collider='box',
              position=(1, 1.3, -85),
              scale=1.3)
box7 = Entity(parent=scene, texture=box_texture, model='assets/Objects/block.obj', collider='box',
              position=(-40, 1.3, -20),
              scale=1.3)

gun = Gun()
game_floor = Entity(parent=scene, texture=ground_texture, model='quad', scale=100, origin_y=0.5,
                    rotation=Vec3(90, 0, 0), collider='box', double_sided=True)
falling_floor = Entity(parent=scene, model='quad', visible=False, scale=100, origin_y=-15,
                       rotation=Vec3(90, 0, 0), collider='box')
sky = Entity(parent=scene, model='sphere', texture=sky_texture, scale=500, double_sided=True)
fps_camera = FPS_Camera.FPS_camera()
fps_camera.position = (random.randint(-30, 30), 5, random.randint(-70, -30))
