from Textures_Audio import *
from ursina import *
import os


class StartButton(Button):
    def __init__(self, position=(0, 0, 0), b=True):
        super().__init__(
            parent=scene,
            position=position,
            color=color.gray,
            highlight_color=color.light_gray,
            scale=(4, 1),
            is_training=b)

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                if self.is_training:
                    os.system("python cd")
                    os.system("python Training_Game.py")
                else:
                    os.system("python Multi_Game.py")


def update():
    if held_keys['q']:
        quit()


multi_txt = Text(text="Multiplayer", color=color.white, position=(-0.2, 0.15, 0), scale=3)
training_txt = Text(text="Training", color=color.white, position=(-0.14, -0.09, 0), scale=3)
main_menu_background = Entity(parent=scene, model='quad', texture=background_texture, scale=Vec3(15, 10, 0))
multi_button = StartButton(position=(0, 1, 0), b=False)
training_button = StartButton(position=(0, -1, 0), b=True)
background_music.play()

app.run()
