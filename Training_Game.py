from Textures_Audio import *
from Game_Parameters import *


def reload():
    """
    reloads the gun
    """
    global bullets
    reload_sound.play()
    bullets = 30
    bullets_txt.text = str(bullets)


def shoot():
    """
    shoots the gun and sends the server a message that the current player shot
    """
    global bullets
    gunfire_sound.play()
    bullets -= 1
    bullets_txt.text = str(bullets)
    fps_camera.update(1)


def update():
    global bullets
    if held_keys['w'] and held_keys['left shift']:
        gun.active()
    else:
        gun.passive()
        if bullets > 0:
            if held_keys['left mouse']:
                if not keys_dict['left mouse']:
                    keys_dict['left mouse'] = True
                    shoot()
            else:
                keys_dict['left mouse'] = False

        if held_keys['r']:
            if not keys_dict['r'] and bullets < 30:
                keys_dict['r'] = True
                reload()
        else:
            keys_dict['r'] = False

    if held_keys['r']:
        if not keys_dict['r'] and bullets < 30:
            keys_dict['r'] = True
            reload()
    else:
        keys_dict['r'] = False

    if held_keys['q']:
        quit()


# ints
bullets = 30

# texts
quit_txt = Text(parent=camera.ui, text='q - quit training', position=(-0.85, 0.45, 0), scale=2, color=color.dark_gray)
shoot_txt = Text(parent=camera.ui, text='left mouse button - shoot gun', position=(-0.85, 0.4, 0), scale=2, color=color.dark_gray)
reload_txt = Text(parent=camera.ui, text='r - reload gun', position=(-0.85, 0.35, 0), scale=2, color=color.dark_gray)
w_txt = Text(parent=camera.ui, text='w - forward', position=(-0.85, 0.3, 0), scale=2, color=color.dark_gray)
a_txt = Text(parent=camera.ui, text='a - left', position=(-0.85, 0.25, 0), scale=2, color=color.dark_gray)
s_txt = Text(parent=camera.ui, text='s - backward', position=(-0.85, 0.2, 0), scale=2, color=color.dark_gray)
d_txt = Text(parent=camera.ui, text='d - right', position=(-0.85, 0.15, 0), scale=2, color=color.dark_gray)
space_txt = Text(parent=camera.ui, text='space - jump', position=(-0.85, 0.1, 0), scale=2, color=color.dark_gray)
shift_txt = Text(parent=camera.ui, text='left shift + w - run', position=(-0.85, 0.05, 0), scale=2, color=color.dark_gray)
ctr_txt = Text(parent=camera.ui, text='left ctr - crouch', position=(-0.85, 0, 0), scale=2, color=color.dark_gray)
bullets_txt = Text(parent=camera.ui, text=str(bullets), color=color.blue, position=(0.78, -0.4, 0), scale=3)

app.run()
