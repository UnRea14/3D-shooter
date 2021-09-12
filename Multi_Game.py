from Textures_Audio import *
from Game_Parameters import *
import socket
import select
import random
import glob


class Enemy(Button):
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), player_name=""):
        super().__init__(
            parent=scene,
            model='cube',
            color=color.red,
            position=position,
            rotation=rotation)
        self.name = player_name
        self.alive = True

    def is_hovered(self):
        """
        checks if current player is hovered by another player
        :return: true if current player is hovered by another, false else
        """
        if self.hovered:
            return True
        return False


def get_name():
    """
    gets name from user
    :return: str
    """
    global name
    name = input(
        "Enter a name (name cannot contain space, '-', '|', '/', '*' name length <= 8 and name only in English): ")
    while 0 > len(name) or len(name) > 8 or "|" in name or "-" in name or "/" in name or "*" in name or " " in name or not check_ascii_name(name):
        print("Invalid name!")
        name = input(
            "Enter a different name (name cannot contain space, '-', '|', '/', '*' name length <= 8 and name only in "
            "English): ")
    return name


def check_ascii_name(name1):
    """
    checks if the name is in a different language, returns true if the name is in english or in a language that contains English letters
    :param name1: name that we want to check
    :return: boolean
    """
    print()
    if len(ascii(name1)) != len(name1) + 2:
        return False
    return True


def send_and_create_position_rotation_message():
    """
    creating and sending the rotation position name message
    """
    global me_position, me_rotation, length
    me_position = str(fps_camera.position)
    me_rotation = str(fps_camera.rotation)
    message = (me_position.split("Vec3")[1]).replace("(", "").replace(")", "") + "|" + (
        me_rotation.split("Vec3")[1]).replace("(", "").replace(")", "")
    length = str(len(message))
    player_socket.send((length.zfill(2) + message).encode())


def shoot():
    """
    shoots the gun and sends the server a message that the current player shot
    """
    global bullets, game_ended
    gunfire_sound.play()
    bullets -= 1
    bullets_txt.text = str(bullets)
    fps_camera.update(1)
    length1 = str(len("shoot"))
    player_socket.send((length1.zfill(2) + "shoot").encode())
    if enemy.alive:
        if enemy.hovered:
            hit_sound.play()
            message = name + " shot " + enemy.name
            length1 = str(len(message))
            player_socket.send((length1.zfill(2) + message).encode())


def reload():
    """
    reloads the gun
    """
    global bullets
    reload_sound.play()
    bullets = 30
    bullets_txt.text = str(bullets)


def respawn():
    """
    respawns the player and sends to the server a message that the player has respawned
    """
    global alive, bullets, feed_changed, feed, length
    dead_txt.disable()
    alive = True
    bullets = 30
    bullets_txt.text = str(bullets)
    health_txt.text = "100"
    fps_camera.enable()
    fps_camera.position = (random.randint(-30, 30), 5, random.randint(-70, -30))
    feed_changed = True
    feed = name + " respawned"
    length = str(len(feed))
    player_socket.send((length.zfill(2) + feed).encode())


def restart():
    """
    restart all the variables that need to be restarted
    """
    global alive, health_changed, bullets, game_ended, feed, feed_changed
    game_ended = False
    alive = True
    health_changed = True
    feed = "Game restarted"
    feed_changed = True
    bullets = 30
    bullets_txt.text = str(bullets)
    health_txt.text = "100"
    kills_txt.text = ""
    most_kills_txt.text = ""
    win_lost_txt.text = ""
    fps_camera.enable()
    fps_camera.position = (random.randint(-30, 30), 2, random.randint(-70, -30))
    enemy.alive = True


def handle_position_rotation():
    """
    handles position, rotation message
    """
    position_1 = data.split("|")[0]
    rotation_1 = data.split("|")[1]
    enemy.position = (
        float(position_1.split(",")[0]), float(position_1.split(",")[1]) + 2, float(position_1.split(",")[2]))
    enemy.rotation = (float(rotation_1.split(",")[0]), float(rotation_1.split(",")[1]), float(rotation_1.split(",")[2]))


def handle_killed():
    """
    handles killed message
    """
    global feed, feed_changed
    feed_changed = True
    feed = data
    enemy.alive = False


def handle_respawned():
    """
    handles respawned message
    """
    global feed_changed, feed
    feed_changed = True
    feed = data
    enemy.alive = True


def handle_won():
    """
    handle won message
    """
    global game_ended
    game_ended = True
    dead_txt.disable()
    if data.split(" won!")[0] == name:
        win_lost_txt.position = (-0.15, 0.3, 0)
        win_lost_txt.text = "WIN"
        win_lost_txt.color = color.blue
        win_sound.play()
    else:
        win_lost_txt.position = (-0.2, 0.3, 0)
        win_lost_txt.text = "LOSS"
        win_lost_txt.color = color.red
        lost_sound.play()


def handle_joined():
    """
    handles joined message
    """
    global feed_changed, feed
    enemy.enable()
    feed_changed = True
    feed = data
    enemy.name = data.split(" joined!")[0]
    send_and_create_position_rotation_message()


def handle_left():
    """
    handles left message
    """
    global feed_changed, feed
    feed_changed = True
    feed = data
    enemy.disable()


def handle_most_kills_player():
    """
    handles most kills player message
    """
    most_killer = data.split(" - ")[0]
    if most_killer == name:
        most_kills_txt.text = "You" + " - " + data.split(" - ")[1]
    else:
        most_kills_txt.text = data


def handle_health():
    """
    handles health message
    """
    global alive, feed, feed_changed
    hurt_sound.play()
    health1 = data.split("*")[1]
    if int(health1) <= 0:
        dead_txt.enable()
        health_txt.text = "0"
        alive = False
        fps_camera.y = -1.5
        fps_camera.disable()
        feed = enemy.name + " killed You"
        feed_changed = True
    else:
        health_txt.text = health1


def handle_game_restart():
    """
    handles the game restart messages
    """
    global feed, feed_changed
    if data[17] == "0":
        feed = "Game restarted"
        restart()
    else:
        feed = data
    feed_changed = True


def get_server_data():
    """
    retrieves server information from a text file, if the text file doest exists creates a new text file and inputs ip and ports
    """
    path = "assets\\Server_Information.txt"
    file_list = glob.glob("assets\\Server_Information.txt")
    if len(file_list) == 0:
        file = open(path, 'w')
        print("Server's information txt file doesn't exists!")
        ip = input("Enter server's ip: ")
        port = input("Enter server's port: ")
        file.write(ip + "," + port)
        file_data = ip + "," + port
    else:
        file = open(path, 'r')
        file_data = file.read()
    file.close()
    return file_data


def receive_from_server():
    """
    receives data from server and acts accordingly
    """
    global alive, data

    if me_position != str(fps_camera.position) or me_rotation != str(fps_camera.rotation):
        send_and_create_position_rotation_message()

    r_list, w_list, e_list = select.select([player_socket], [player_socket], [])
    for sock in r_list:
        length1 = player_socket.recv(2).decode()
        try:
            data = sock.recv(int(length1)).decode()
        except ValueError:
            print("error - ValueError")
            quit()

        if "|" not in data:
            print(data)

        if "|" in data:  # 0,0,0|0,0,0
            handle_position_rotation()

        elif "Game restart" in data:  # (Game restarts in 5) or (Game restarted)
            handle_game_restart()

        elif "shoot" in data:  # shoot
            enemy_fire_sound.play()

        elif " killed " in data:  # me killed name
            handle_killed()

        elif "*" in data:  # me*health
            handle_health()

        elif "/" in data:  # me/kills
            kills_txt.text = data.split("/")[1]

        elif " respawned" in data:  # name respawned
            handle_respawned()

        elif " won!" in data:  # name won!
            handle_won()

        elif " joined!" in data:  # name joined!
            handle_joined()

        elif " left!" in data:   # name left!
            handle_left()

        elif " - " in data:  # name - kills
            handle_most_kills_player()


def update():
    """
    called every frame, handles inputs and calls a function that received data from user
    """
    global feed_changed, feed, alive

    receive_from_server()

    if feed_changed:
        feed_changed = False
        feed_txt.text = feed

    if not game_ended:
        if held_keys['m'] and not alive:
            if not keys_dict['m']:
                keys_dict['m'] = True
                respawn()
        else:
            keys_dict['m'] = False

        if held_keys['q']:
            feed = name + " left!"
            length1 = str(len(feed))
            player_socket.send((length1.zfill(2) + feed).encode())
            quit()

    if alive:
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


def main():
    """
    joining the server, receiving a player name if someone has joined the server and sending the first message
    """
    global feed, length, player_socket, data, name
    ip = server_data.split(",")[0]
    port = server_data.split(",")[1]
    print("Connecting to the server...")
    try:
        player_socket.connect((ip, int(port)))
    except ConnectionRefusedError:
        print("Server is offline!")
        quit()
    length = player_socket.recv(2).decode()
    try:
        data = player_socket.recv(int(length)).decode()
    except ValueError:
        print("error - ValueError")
        quit()
    if data == "Server is full!":
        print(data)
        quit()
    enemy.name = data
    while name == enemy.name:
        print("Player with the same name already joined the server!")
        name = get_name()
    feed = name + " joined!"
    length = str(len(feed))
    player_socket.send((length.zfill(2) + feed).encode())
    print("Joined!")

    app.run()


player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_data = get_server_data()

# ints
position1 = 0
rotation1 = 0
bullets = 30
length = 0

# booleans
feed_changed = False
health_changed = False
alive = True
game_ended = False

# strings
feed = ""
data = ""
me_position = ""
me_rotation = ""
name = get_name()

# entities
enemy = Enemy(position=(0, -1, 0))

# texts
dead_txt = Text(parent=camera.ui, text="Dead", color=color.red, scale=5, position=(-0.15, 0.2, 0))
dead_txt.disable()
bullets_txt = Text(parent=camera.ui, text=str(bullets), color=color.blue, position=(0.78, -0.4, 0), scale=3)
feed_txt = Text(parent=camera.ui, text="", color=color.dark_gray, position=(-0.88, 0.47, 0))
health_txt = Text(parent=camera.ui, text="100", color=color.blue, position=(-0.85, -0.4, 0), scale=3)
most_kills_txt = Text(parent=camera.ui, text="", position=(0, 0.5, 0))
kills_txt = Text(parent=camera.ui, text="", color=color.blue, position=(0.78, 0.45, 0), scale=2)
win_lost_txt = Text(parent=camera.ui, text="", color=color.red, scale=5)

if __name__ == "__main__":
    main()
