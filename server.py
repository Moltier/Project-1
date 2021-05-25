import socket, threading, time
from game import Game, Player, characters
from engine import get_cell_coord
from network import PORT, send_object, get_object, message_to_all
from display import spectator
from spec_functions import cp

SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind((socket.gethostname(), PORT))  # socket.gethostname()


class Server:
    def __init__(self):
        self.spectator_mode = False  # for testing
        self.max_game_count = 5
        self.max_player_count = 2
        self.connections = []
        self.games_dict = {}
        self.player_counts = {}  # game_id: player_count
        self.base_scroll = [0, 0]
        self.framerate = 60
        self.sec_per_message = 0.1
        self.chars = {}

    def update_player_count(self):
        self.player_counts = {}
        for i in self.games_dict:
            self.player_counts[i] = self.games_dict[i].player_count


def threaded_client(conn, addr):
    print(f'New Connection from {addr}.')
    print(f'Connection data: {conn}.')
    print()

    # Initializing
    server_data.chars = characters.copy()

    send_object(('Games IDs + Player Counts', server_data.player_counts), conn)

    while True:
        # try:
        key_code, new_object = get_object(conn)

        if key_code == 'Name':
            player_data = Player()
            player_data.name = new_object

        # Multiplayer menu
        elif key_code == 'New Game' and len(server_data.games_dict) < server_data.max_game_count:
            player_data.id = 0
            game_data = Game('map1')
            game_data.players.append(player_data)
            game_data.players[player_data.id].name = player_data.name

            if new_object == 'Test Game':
                game_data.test_mode = True

            for i in range(server_data.max_game_count):
                if i not in server_data.games_dict:
                    server_data.games_dict[i] = game_data
                    game_data.id = i
                    break

            game_data.connections.append(conn)
            server_data.connections.remove(conn)
            server_data.games_dict[game_data.id] = game_data
            server_data.update_player_count()
            if game_data.test_mode:
                send_object(('Test Game Success', ''), conn)
            else:
                send_object(('New Game Success', ''), conn)

            for conn in server_data.connections:
                send_object(('Games IDs + Player Counts', server_data.player_counts), conn)

        elif key_code == 'Exit':
            try:
                game_data.connections.remove(conn)
                if not any(game_data.connections):
                    del server_data.games_dict[game_data.id]
            except Exception:
                pass
            conn.close()
            return

        elif key_code == 'Back to Main':
            try:
                game_data.connections.remove(conn)
                if not any(game_data.connections):
                    del server_data.games_dict[game_data.id]
            except Exception:
                pass

        elif key_code == 'Join Game':
            game_id = new_object
            game_data = server_data.games_dict[game_id]

            for n in range(4):
                try:
                    game_data.players[n]
                except IndexError:
                    game_data.connections.insert(n, conn)
                    server_data.connections.remove(conn)
                    player_data.id = n
                    game_data.players.insert(n, player_data)
                    game_data.player_count += 1
                    server_data.update_player_count()
                    break

            game_data.players[player_data.id].name = player_data.name

            for game_conn in game_data.connections:
                if game_conn:
                    if conn == game_conn:
                        send_object(('Join', (player_data.id, game_data.players, game_data.isReady)), game_conn)
                    else:
                        send_object(('New Join', game_data.players), game_conn)

            for server_conn in server_data.connections:
                send_object((('Games IDs + Player Counts'), server_data.player_counts), server_conn)

        # Lobby
        elif not game_data.isRunning:
            if key_code == 'Game data':
                send_object(('Game data', game_data), conn)
            elif key_code == 'Set map':
                game_data.map = new_object
            elif key_code == 'Set char':
                char_id = new_object
                if not server_data.chars[char_id].isTaken:
                    game_data.players[player_data.id].char_id = char_id

                    for i in server_data.chars.keys():
                        server_data.chars[i].isTaken = False
                        for player in game_data.players:
                            server_data.chars[player.char_id].isTaken = True

                    message_to_all(('Players data', game_data.players), game_data.connections)

            elif key_code == 'Ready':
                game_data.isReady[player_data.id] = True
                message_to_all(('IsReady', (player_data.id, True)), game_data.connections)
                if game_data.test_mode or game_data.isReady.count(True) >= server_data.max_player_count:
                    game_data.load_map()

                    removable_char_ids = []
                    for i, char in server_data.chars.items():
                        if not char.isTaken:
                            removable_char_ids.append(i)

                    for n in removable_char_ids:
                        server_data.chars.pop(n)

                    if server_data.spectator_mode:
                        spectator_thread = threading.Thread(target=spectator, args=(game_data, server_data))
                        spectator_thread.start()

                    game_data.isReady = [False, False, False, False]
                    game_data.isRunning = True
                    game_data.start_time = game_data.update_time = round(time.time(), 2)
                    message_to_all(('Run', (game_data.map, game_data.start_time)), game_data.connections)
                    continue
            elif key_code == 'Not Ready':
                game_data.isReady[player_data.id] = False
                message_to_all(('IsReady', (player_data.id, False)), game_data.connections)

            elif key_code == 'Exit Lobby':
                game_data.connections.remove(conn)
                server_data.connections.append(conn)
                server_data.chars[game_data.players[player_data.id].char_id].isTaken = False
                game_data.remove_player(player_data.id)
                server_data.player_counts[game_data.id] -= 1
                message_to_all(('Remove Player', player_data.id), game_data.connections)
                if not any(game_data.connections):
                    del server_data.games_dict[game_data.id]
                    server_data.update_player_count()
                for server_conn in server_data.connections:
                    send_object(('Games IDs + Player Counts', server_data.player_counts), server_conn)
            continue
        elif game_data.isRunning:
            if key_code == 'Button Click':
                cp(9876, key_code)

            elif key_code == 'New Action':
                server_data.chars[game_data.players[player_data.id].char_id].new_orders_data = new_object

            elif key_code == 'Chat':
                message_to_all(('Chat', [player_data.id, new_object]), game_data.connections)

            elif key_code == 'Next Wave':
                game_data.isReady[player_data.id] = True

        # except ConnectionResetError as e:
        #     cp(8237, f'Connection lost to {address}.  {e}.')
        #     game_data.players[player_data.id - 1] = None  # ez még lehet nem elég, hisz újra kéne küldeni az adatot, hogy ne mutassák
        #     game_data.connections.remove(conn)
        #     conn.close()
        #     return


def data_thread():
    while True:
        try:
            for game_data in server_data.games_dict.values():  # ez így nem jó, mert menet közben bővülhet
                if game_data.isRunning:
                    game_data.game_time = round(time.time(), 2)
                    game_data.dt = game_data.game_time - game_data.last_time
                    game_data.last_time = game_data.game_time

                    # Character moves:
                    time_to_act = game_data.dt
                    for player in game_data.players:
                        if player.char_id >= 0:
                            char = server_data.chars[player.char_id]
                            # Refresh orders if 'New Action' from client.
                            if char.new_orders_data:  # ez lehet lista kéne legyen, amihez appendelem az új orders_data-t
                                server_data.chars[game_data.players[player.id].char_id].orders_num = char.new_orders_data[0]
                                server_data.chars[game_data.players[player.id].char_id].orders = char.new_orders_data[1]
                                server_data.chars[game_data.players[player.id].char_id].new_orders_data = None
                                server_data.chars[game_data.players[player.id].char_id].is_new_order = True  # itt pedig pop-olnám a felhasználtat
                                # ezáltal elkerülném az esetleges összeakadást.

                            for order in char.orders:
                                if char.is_new_order:
                                    action = order[1]
                                    if action:
                                        target_coord = order[0]
                                        try:
                                            target_coord[0] += server_data.base_scroll[0]
                                            target_coord[1] += server_data.base_scroll[1]
                                        except TypeError:
                                            pass

                                        if action == 'MT':
                                            prev_coord = server_data.chars[game_data.players[player.id].char_id].crafting_cell_coord
                                            server_data.chars[game_data.players[player.id].char_id].crafting_cell_coord \
                                                = get_cell_coord(target_coord, game_data.cell_size)
                                            if prev_coord and prev_coord != server_data.chars[game_data.players[player.id].char_id].crafting_cell_coord:
                                                game_data.cells_dict[prev_coord].completion = 100
                                                try:
                                                    game_data.crafting_cell_coords.remove(prev_coord)
                                                except ValueError:
                                                    pass

                                            server_data.chars[game_data.players[player.id].char_id].iscrafting = False
                                    server_data.chars[game_data.players[player.id].char_id].is_new_order = False

                                server_data.chars[game_data.players[player.id].char_id].move(
                                    server_data.chars, game_data, order[0], server_data.framerate)

                                if game_data.dt > 0:
                                    server_data.chars[game_data.players[player.id].char_id].crafting(
                                        game_data, isServer=True)

                                if (not server_data.chars[game_data.players[player.id].char_id].orders[0][1]
                                        or server_data.chars[game_data.players[player.id].char_id].orders[0][0]
                                        == server_data.chars[game_data.players[player.id].char_id].rect.center) \
                                        and len(server_data.chars[game_data.players[player.id].char_id].orders) > 1:
                                    server_data.chars[game_data.players[player.id].char_id].orders.pop(0)
                                    server_data.chars[game_data.players[player.id].char_id].is_new_order = True

                                if game_data.dt == 0:
                                    break

                            game_data.dt = time_to_act

                    # Adat küldés poziciókról, célpontokról és cellákról
                    if game_data.game_time - game_data.update_time >= server_data.sec_per_message:  # X időközönként
                        delta_time = round(game_data.game_time - game_data.update_time, 2)
                        cells_data = {}
                        for cell_coord in game_data.crafting_cell_coords + game_data.completed_crafts:
                            cells_data[cell_coord] = [
                                game_data.cells_dict[cell_coord].next_craft,
                                int(game_data.cells_dict[cell_coord].completion)
                            ]
                        global_data = [cells_data]  # will be more
                        for player in game_data.players:  # a játékban levő klienseknek aktuális adatot küld
                            if game_data.connections[player.id]:
                                char_coords_list = [
                                    server_data.chars[player.char_id].rect.center for player in game_data.players if player.char_id >= 0]

                                send_object(
                                    ('Data',
                                     (delta_time,
                                      server_data.chars[player.char_id].orders_num,
                                      global_data,
                                      char_coords_list,
                                      server_data.chars[player.char_id].char_data())),
                                    game_data.connections[player.id])

                        game_data.completed_crafts = []
                        game_data.update_time = game_data.game_time

                    if not game_data.battle_mode:
                        if game_data.isReady.count(True) == len(game_data.connections):
                            game_data.battle_mode = True
                            game_data.wave_num += 1
                            game_data.generate_enemies()
                            message_to_all(('Next Wave', ''), game_data.connections)
        except RuntimeError:
            continue


SERVER.listen(5)  # maximum number of connect requests
server_data = Server()
print()
print('[SERVER] started. Waiting for connections...')
print()

server_thread = threading.Thread(target=data_thread)
server_thread.start()

while True:  # handling new connections
    connection, address = SERVER.accept()
    server_data.connections.append(connection)
    SERVER.setblocking(1)  # prevents timeout
    thread1 = threading.Thread(target=threaded_client, args=(connection, address))
    thread1.start()

