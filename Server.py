import socket
import select
import datetime


class Player:
    def __init__(self, sock, player_name):
        self.player_name = player_name
        self.sock = sock
        self.kills = 0
        self.health = 100

    def get_name(self):
        """
        returns the player's name
        :return: str
        """
        return self.player_name

    def get_kills(self):
        """
        returns the player's kills
        :return: int
        """
        return self.kills

    def set_kills(self, kills):
        """
        sets the player's kills to the given kills
        """
        self.kills = kills

    def inc_kills(self):
        """
        increments kills
        """
        self.kills += 1

    def get_sock(self):
        """
        returns the player's socket
        :return: socket
        """
        return self.sock

    def get_health(self):
        """
        returns the player's name
        :return: str
        """
        return self.health

    def set_health(self, health):
        """
        sets the player's health to the given health
        """
        self.health = health


def send_kills(p1, p2):
    """
    creates the kills message and appends it to message_to_append list
    :param p2: the player that we want to send to his kills
    :param p1: the other player that we don't want to send the message to
    """
    global messages_to_send
    message = p2.get_name() + "/" + str(p2.get_kills())
    length = str(len(message))
    messages_to_send.append((p1.sock, length.zfill(2) + message))  # name/kills


def send_health(p1, p2):
    """
    creates the kills message and appends it to message_to_append list
    :param p2: the player that we want to send to his health
    :param p1: the other player that we don't want to send the message to
    """
    global messages_to_send
    message = p1.get_name() + "*" + str(p1.get_health())
    length = str(len(message))
    messages_to_send.append((p2.sock, length.zfill(2) + message))  # name*health


def send_killed(p1, p2):
    """
    creates the kills message and appends it to message_to_append list
    :param p2: the player that killed
    :param p1: the player that got killed
    """
    global messages_to_send
    message = p2.get_name() + " killed " + p1.get_name()
    length = str(len(message))
    messages_to_send.append((p1.sock, length.zfill(2) + message))  # name killed name


def send_won(p1):
    """
    creates the kills message and appends it to message_to_append list
    :param p1: the player who won
    """
    global messages_to_send, game_ended, t
    t = datetime.datetime.now().second
    game_ended = True
    message = p1.get_name() + " won!"
    print(message)
    length = str(len(message))
    messages_to_send.append((None, length.zfill(2) + message))  # name won!


def send_max_killer(p1):
    """
    creates the kills message and appends it to message_to_append list
    :param p1: the max killer
    """
    message = p1.get_name() + " - " + str(p1.get_kills())
    print(message)
    length = str(len(message))
    messages_to_send.append((None, length.zfill(2) + message))  # name - 0


def handle_shot(p1, p2, who_shot):
    """
    handles the shot message
    :param p1: player 1
    :param p2: player 2
    :param who_shot: player name - which player shot the other player
    """
    b = False
    if who_shot == p1.get_name():
        p1.set_health(p1.get_health() - 30)
        send_health(p1, p2)
        if p1.get_health() <= 0:
            send_killed(p1, p2)
            p2.inc_kills()
            send_kills(p1, p2)
            b = True
    else:
        p2.set_health(p2.get_health() - 30)
        send_health(p2, p1)
        if p2.get_health() <= 0:
            send_killed(p2, p1)
            p1.inc_kills()
            send_kills(p2, p1)
            b = True

    if p1.get_kills() >= 30 or p2.get_kills() >= 30:
        if p1.get_kills() >= 30:
            send_won(p1)
        else:
            send_won(p2)
        p1.set_health(100)
        p1.set_kills(0)
        p2.set_health(100)
        p2.set_kills(0)
    elif b:
        if p1.get_kills() > p2.get_kills():
            send_max_killer(p1)
        elif p1.get_kills() < p2.get_kills():
            send_max_killer(p2)


def handle_respawned(who):
    """
    handles the respawned message
    :param who: the player's name that respawned
    """
    if who == p1.get_name():
        p1.set_health(100)
    else:
        p2.set_health(100)


def handle_joined(name, players_socket):
    """
    handles the joined message
    :param players_socket: current player socket
    :param name: the name of the player that joined
    """
    global p1, p2
    if p1.get_name() == "":
        p1 = Player(sock=players_socket, player_name=name)
    else:
        p2 = Player(sock=players_socket, player_name=name)


def handle_left(name, client_sockets, players_socket):
    """
    handles the left message
    :param name: the name of the player that left
    :param client_sockets: the list of players sockets
    :param players_socket: the current player socket
    """
    global p1, p2
    if (p1.get_name() != "" and p2.get_name() == "") or (p1.get_name() == "" and p2.get_name() != ""):
        p1 = Player(None, "")
        p2 = Player(None, "")
    else:
        if p1.get_name() == name:
            p1 = Player(None, "")
            p2.set_kills(0)
            send_kills(p2, p1)
            p2.set_health(100)
            send_health(p2, p1)
            send_won(p2)
        else:
            p2 = Player(None, "")
            p1.set_kills(0)
            send_kills(p1, p2)
            p1.set_health(100)
            send_health(p1, p2)
            send_won(p1)
    client_sockets.remove(players_socket)
    players_socket.close()


def handle_client_crash(player_socket, client_sockets):
    """

    """
    global p1, p2
    if player_socket == p1.get_sock():
        message = p1.get_name() + " left!"
        length = str(len(message))
        messages_to_send.append((None, length.zfill(2) + message))
        p1 = Player(None, "")
        p2.set_kills(0)
        send_kills(p2, p1)
        p2.set_health(100)
        send_health(p2, p1)
        send_won(p2)
    else:
        message = p1.get_name() + " left!"
        length = str(len(message))
        messages_to_send.append((None, length.zfill(2) + message))
        p2 = Player(None, "")
        p1.set_kills(0)
        send_kills(p1, p2)
        p1.set_health(100)
        send_health(p1, p2)
        send_won(p1)
    print(message)
    client_sockets.remove(player_socket)
    player_socket.close()


def main():
    global messages_to_send, t, t_count, game_ended, p1, p2
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8820))
    server_socket.listen()
    print("Looking for players...")
    client_sockets = []
    data = ""
    while True:
        r_list, w_list, x_list = select.select([server_socket] + client_sockets, [], [], 0.01)
        if game_ended:
            t1 = datetime.datetime.now().second
            if t1 - t >= 1:
                message = "Game restarts in " + str(t_count)
                print(message)
                length = str(len(message))
                messages_to_send.append((None, length.zfill(2) + message))
                if t_count == 0:
                    game_ended = False
                    t_count = 5
                else:
                    t_count -= 1
                    t = t1

            for player_socket in r_list:
                if player_socket is not server_socket:
                    try:
                        length = player_socket.recv(2).decode()
                        try:
                            data = player_socket.recv(int(length)).decode()

                            if "|" not in data:
                                print(data)

                            length = str(len(data))
                            messages_to_send.append((player_socket, length.zfill(2) + data))

                        except ValueError:
                            client_sockets.remove(player_socket)
                            player_socket.close()

                    except ConnectionResetError:
                        handle_client_crash(player_socket, client_sockets)
        else:
            for player_socket in r_list:
                if player_socket is server_socket:
                    connection, client_address = player_socket.accept()
                    if p1.get_name() == "" or p2.get_name() == "":
                        client_sockets.append(connection)
                        if p1.get_name() == "":
                            length = str(len(p2.get_name()))
                            connection.send((length.zfill(2) + p2.get_name()).encode())
                        else:
                            length = str(len(p1.get_name()))
                            connection.send((length.zfill(2) + p1.get_name()).encode())
                    else:
                        connection.send("15Server is full!".encode())
                else:
                    try:
                        length = player_socket.recv(2).decode()
                        try:
                            data = player_socket.recv(int(length)).decode()
                        except ValueError:
                            client_sockets.remove(player_socket)
                            player_socket.close()

                        if "|" not in data:
                            print(data)

                        if " shot " in data:
                            who_shot = data.split(" shot ")[1]
                            handle_shot(p1, p2, who_shot)

                        elif " respawned" in data:
                            length = str(len(data))
                            messages_to_send.append((None, length.zfill(2) + data))
                            who = data.split(" respawned")[0]
                            handle_respawned(who)

                        else:
                            length = str(len(data))
                            messages_to_send.append((player_socket, length.zfill(2) + data))
                            if " joined!" in data:
                                name = data.split(" joined!")[0]
                                handle_joined(name, player_socket)

                            elif " left!" in data:
                                name = data.split(" left!")[0]
                                handle_left(name, client_sockets, player_socket)

                    except ConnectionResetError:
                        handle_client_crash(player_socket, client_sockets)

        for message in messages_to_send:
            current_socket, data = message
            for sock in client_sockets:
                if sock != current_socket:
                    sock.send(data.encode())
        messages_to_send = []


messages_to_send = []
game_ended = False
t = None
t_count = 5
p1 = Player(None, "")
p2 = Player(None, "")

if __name__ == "__main__":
    main()
