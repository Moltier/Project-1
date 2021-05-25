# import socket, threading
import sys
# from network import PORT, send_object, get_object
from game import *
from static_objects import *
from display import *
from player import player_data
# import profile


pygame.init()
pygame.font.init()
if client_data.fullscreen:
    SCREEN = pygame.display.set_mode((0, 0),
                                     pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
else:
    SCREEN = pygame.display.set_mode((client_data.width, client_data.height),
                                     pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Gnomes!")
clock = pygame.time.Clock()


def main_menu():
    game_data.players = []
    while client_data.main_menu:
        clock.tick(client_data.framerate)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    pass  # pop up kérdés

            if event.type == pygame.MOUSEBUTTONDOWN:
                if sp_button.rect.collidepoint(pos):
                    client_data.sp_game = True
                    client_data.sp_menu = True
                    client_data.main_menu = False
                elif mp_button.rect.collidepoint(pos):
                    client_data.mp_menu = True
                    client_data.main_menu = False
                elif main_menu_options_button.rect.collidepoint(pos):
                    client_data.settings_menu = True
                    client_data.main_menu = False
                    run = False
                elif main_menu_exit_button.rect.collidepoint(pos):
                    pygame.quit()
                    sys.exit()

        draw_main_menu(SCREEN)


def draw_main_menu(SCREEN):
    SCREEN.blit(background_pic, (0, 0))
    menu_btns_group.draw(SCREEN)
    pygame.display.update()


def exit_main_menu():
    while client_data.exit_main_menu:
        clock.tick(client_data.framerate)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    client_data.main_menu = True
                    client_data.exit_main_menu = False

            # elif event.type == pygame.MOUSEBUTTONDOWN:
            #     pos = pygame.mouse.get_pos()
            #
            #     if resolution_btn.click(pos):
            #         resolution_btn.open = True

        draw_options(SCREEN)


def draw_exit(SCREEN):
    SCREEN.fill((150, 150, 150))
    # resolution_btn.draw(SCREEN)
    pygame.display.update()


def options():
    while client_data.settings_menu:
        clock.tick(client_data.framerate)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for setting in [fullscreen_btn, resolution_btn, framerate_btn, camera_scrolling_btn, prediction_btn,
                            player_name_btn]:
                if setting.open:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKSPACE:
                            setting.data = setting.data[:-1]
                        elif event.key in (pygame.K_KP_ENTER, pygame.K_RETURN):
                            setting.open = False
                            options_save_button.color = (0, 255, 0)
                        else:
                            if len(setting.data) < client_data.max_name_len:
                                setting.data += event.unicode

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    client_data.main_menu = True
                    client_data.settings_menu = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if fullscreen_btn.click(pos):
                    client_data.fullscreen = not client_data.fullscreen
                    fullscreen_btn.data = str(client_data.fullscreen)
                elif resolution_btn.click(pos):
                    resolution_btn.open = True
                elif framerate_btn.click(pos):
                    framerate_btn.open = True
                elif camera_scrolling_btn.click(pos):
                    client_data.camera_scrolling = not client_data.camera_scrolling
                    camera_scrolling_btn.data = str(client_data.camera_scrolling)
                elif prediction_btn.click(pos):
                    client_data.prediction = not client_data.prediction
                    prediction_btn.data = str(client_data.prediction)
                elif player_name_btn.click(pos):
                    player_name_btn.open = True

                elif options_save_button.rect.collidepoint(pos):
                    client_data.save_settings([fullscreen_btn, resolution_btn, framerate_btn, camera_scrolling_btn,
                                               prediction_btn, player_name_btn])
                    player_data.name = client_data.player_name
                    options_save_button.color = (50, 50, 50)
                elif options_back_button.rect.collidepoint(pos):
                    client_data.main_menu = True
                    client_data.settings_menu = False

        draw_options(SCREEN)


def draw_options(SCREEN):
    SCREEN.fill((150, 150, 150))

    fullscreen_btn.draw(SCREEN)
    resolution_btn.draw(SCREEN)
    framerate_btn.draw(SCREEN)
    camera_scrolling_btn.draw(SCREEN)
    prediction_btn.draw(SCREEN)
    player_name_btn.draw(SCREEN)

    options_btns_group.draw(SCREEN)
    pygame.display.update()


def sp_menu():
    global game_data
    player_data.id = 0
    game_data.players.append(player_data)
    while client_data.sp_menu:
        clock.tick(client_data.framerate)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    client_data.main_menu = True
                    player_data.id = None
                    game_data = Game()
                    client_data.lobby_menu = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if lobby_start_button.rect.collidepoint(pos):
                    game_data.game_time = game_data.start_time  # game_time így még gondot okozhat
                    game_objects.load_map()
                    game_objects.create_blocker_lines()
                    game_objects.create_matrix(2000, 2000)
                    game_objects.update_modifiers(game_data)
                    game_objects.create_characters()
                    game_objects.my_char_group.add(game_objects.chars_dict[game_data.players[player_data.id].char_id])
                    game_objects.characters_group.empty()
                    for id in game_data.chosen_char_ids:
                        game_objects.characters_group.add(game_objects.chars_dict[id])
                    game_objects.my_char_group.sprite.set_health_bar_size(client_data)
                    game_objects.my_char_group.sprite.talent_tree.update(game_data)

                    client_data.sp_menu = False
                    client_data.game = True
                    game_data.start_time = time.time()

                elif lobby_back_button.rect.collidepoint(pos):
                    client_data.sp_menu = False
                    client_data.main_menu = True

                elif map_picture.rect.collidepoint(pos):
                    client_data.sp_menu = False
                    client_data.map_selection = True

                elif lobby_icon_buttons[player_data.id].click(pos):
                    client_data.sp_menu = False
                    client_data.character_selection = True

        draw_sp_menu(SCREEN)


def draw_sp_menu(SCREEN):
    SCREEN.fill((150, 150, 150))

    sp_menu_btns_group.draw(SCREEN)
    lobby_icon_buttons[player_data.id].draw(SCREEN)
    pygame.display.update()


""" Multiplayer is off, for faster development. """
# def data_thread():
#     while True:
#         if not client_data.sp_game and not client_data.connected:
#             try:
#                 client_data.socket.connect((socket.gethostname(), PORT))
#                 client_data.connected = True
#                 print()
#                 print('Connected to Server.')
#                 pass
#             except ConnectionRefusedError as e:
#                 print(f'Server not found. - {e}.')
#                 time.sleep(0.5)
#                 continue
#
#         while not client_data.sp_game and client_data.connected:
#             try:
#                 key_code, new_object = get_object(client_data.socket)
#                 if not client_data.game:
#                     if key_code == 'New Game Success':
#                         player_data.id = 0
#                         game_data.players.append(player_data)
#                         name_objs[0].text = player_data.name
#                         client_data.mp_menu = False
#                         client_data.lobby_menu = True
#                     elif key_code == 'Test Game Success':
#                         player_data.id = 0
#                         game_data.players.append(player_data)
#                         game_data.players[player_data.id] = player_data
#                         game_data.players[player_data.id].char_id = 0
#                         send_object(('Set char', game_data.players[0].char_id), client_data.socket)
#                         send_object(('Ready', ''), client_data.socket)
#                         client_data.mp_menu = False
#                     elif key_code == 'Join':
#                         player_data.id, game_data.players, game_data.isReady = new_object
#                         game_data.chosen_char_ids = []  # ezt majd fixálni
#
#                         for player in game_data.players:
#                             name_objs[player.id].text = player.name
#
#                         for i, player in enumerate(game_data.players):
#                             if player.char_id >= 0:
#                                 lobby_icon_buttons[i].image = gnome_icons[player.char_id]
#                             if game_data.isReady[i]:
#                                 ready_circles[i].color = (0, 255, 0)
#                         client_data.mp_menu = False
#                         client_data.lobby_menu = True
#
#                     elif key_code == 'Games IDs + Player Counts':
#                         client_data.update(new_object)
#                     elif key_code == 'New Join':
#                         game_data.players = new_object
#                         for player in game_data.players:
#                             name_objs[player.id].text = player.name
#                     elif key_code == 'Full':
#                         continue
#
#                     if key_code == 'Run':
#                         game_data.map, game_data.start_time = new_object
#                         game_data.game_time = game_data.start_time  # game_time így még gondot okozhat
#                         game_objects.load_map()
#                         game_objects.create_blocker_lines()
#                         game_objects.create_matrix(2000, 2000)
#                         game_objects.update_modifiers(game_data)
#                         game_objects.create_characters()
#                         game_objects.my_char_group.add(game_objects.chars_dict[game_data.players[player_data.id].char_id])
#                         game_objects.characters_group.empty()
#                         for id in game_data.chosen_char_ids:
#                             game_objects.characters_group.add(game_objects.chars_dict[id])
#
#                         game_objects.my_char_group.sprite.timeline = [[
#                             game_data.start_time,
#                             game_objects.my_char_group.sprite.orders_num,
#                             game_objects.my_char_group.sprite.orders
#                         ]]
#                         game_objects.my_char_group.sprite.set_health_bar_size(client_data)
#
#                         client_data.lobby_menu = False
#                         client_data.game = True
#
#                         orders_num = game_objects.my_char_group.sprite.orders_num
#
#                         game_data_pred = deepcopy(game_data)
#
#                         if client_data.artificial_lag > 0:
#                             message = (orders_num, game_objects.my_char_group.sprite.orders)
#                             new_action_thread = threading.Thread(
#                                 target=new_action, args=(
#                                     client_data.artificial_lag, client_data.socket,
#                                     message)
#                             )
#                             new_action_thread.start()
#                         else:
#                             send_object(
#                                 ('New Action',
#                                  (orders_num, game_objects.my_char_group.sprite.orders)),
#                                 client_data.socket)
#
#                     elif key_code == 'Remove Player':
#                         player_id = new_object
#                         game_data.chosen_char_ids.remove(game_data.players[player_id].char_id)
#                         game_data.remove_player(player_id)
#                         ready_circles[new_object].color = (255, 0, 0)
#                         lobby_icon_buttons[new_object].image = question_mark
#                         name_objs[new_object].text = ''
#
#                     elif key_code == 'Players data':
#                         game_data.players = new_object
#                         game_data.chosen_char_ids = []  # itt lehet csupán a választott id-ket kell megkapni
#
#                         for i, player in enumerate(game_data.players):
#                             lobby_icon_buttons[i].image = gnome_icons[player.char_id]
#
#                     elif key_code == 'IsReady':
#                         if new_object[1]:
#                             ready_circles[new_object[0]].color = (0, 255, 0)
#                             if new_object[0] == player_data.id:
#                                 game_data.isReady[player_data.id] = True
#                         else:
#                             ready_circles[new_object[0]].color = (255, 0, 0)
#                             if new_object[0] == player_data.id:
#                                 game_data.isReady[player_data.id] = False
#
#                 elif client_data.game:
#                     if key_code == 'Data':
#                         delta_time, server_orders_num, global_data, char_coords, char_data = new_object
#                         # Többi játékos új koordinátája
#                         for player_id, coord in enumerate(char_coords):
#                             char_id = game_data.players[player_id].char_id
#                             for char in game_objects.characters_group:
#                                 if player_id != player_data.id and char_id == char.id:
#                                     char.rect.center = coord
#
#                         # ha nincs az alábbiakban eltérés az aktuálishoz képest,
#                         # akkor nem is kéne futtatni a frissítést a saját karakterre
#                         if client_data.prediction:
#                             pass
#                             for i, char in game_objects.chars_dict.items():
#                                 game_objects.chars_dict_pred[i] = CharacterPrediction(*char.save_pred_data())
#
#                             saved_char_data = game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].save_data()
#
#                             game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline \
#                                 = game_objects.chars_dict[game_data_pred.players[player_data.id].char_id].timeline.copy()
#                             game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].orders \
#                                 = game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline[-1][2]
#
#                             cells_data = global_data[0]
#                             game_data_pred.update_cells(cells_data)
#                             game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].rect.center = char_coords[player_data.id]
#                             game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].update_char_data(char_data)
#
#                             # Remove outdated timeline data
#                             for i, data in enumerate(game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline):
#                                 order_num = data[1]
#                                 if order_num == server_orders_num:
#                                     current_data_time = data[0]
#                                     new_data_time = round(current_data_time + delta_time, 2)
#                                     game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline[i][0] = new_data_time
#                                     game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline \
#                                         = game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline[i:]
#                                     break
#                             else:
#                                 cp(9999, 'This should never happen!')
#                                 print()
#
#                             # Timeline végrehajtása (saját karakter)
#                             for i, timeline_data in enumerate(game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline):
#                                 if i + 1 < len(game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline):
#                                     game_data_pred.dt = game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline[i + 1][0] \
#                                                         - timeline_data[0]
#                                 else:
#                                     game_data_pred.dt = game_data_pred.game_time - timeline_data[0]
#
#                                 game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].orders \
#                                     = game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].timeline[0][2]
#
#                                 for order in game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].orders:
#                                     game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].move(
#                                         order, game_objects.chars_dict_pred, game_data_pred, client_data.framerate)
#
#                                     if game_data_pred.dt > 0:
#                                         game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].crafting(game_data_pred)
#
#                                     if not game_objects.chars_dict_pred[game_data_pred.players[player.id].char_id].orders[0][0] \
#                                             and len(game_objects.chars_dict_pred[game_data_pred.players[player.id].char_id].orders) > 1:
#                                         game_objects.chars_dict_pred[game_data_pred.players[player.id].char_id].orders.pop(0)
#
#                                     if game_data_pred.dt == 0:
#                                         break
#
#                             fixed_char_data = game_objects.chars_dict_pred[game_data_pred.players[player_data.id].char_id].save_data()
#                             diff = []
#                             for i, data in enumerate(saved_char_data):
#                                 diff.append(fixed_char_data[i] - data)
#                             game_objects.chars_dict[game_data_pred.players[player_data.id].char_id].data_diff_list = diff
#
#                         elif not client_data.prediction:
#                             cells_data = global_data[0]
#                             game_data.update_cells(cells_data)
#                             game_objects.my_char_group.sprite.rect.center = char_coords[
#                                 player_data.id]
#                             game_objects.my_char_group.sprite.update_char_data(char_data)
#
#                     elif key_code == 'Chat':
#                         chat_area.chat_data.append([game_data.players[new_object[0]], new_object[1]])
#                         client_data.chat_window_timer = time.time()
#
#                     elif key_code == 'Next Wave':
#                         game_data.wave_num += 1
#                         game_data.battle_mode = True
#
#             except ConnectionResetError as e:
#                 print(f'Connection lost to SERVER. - {e}')
#                 client_data.connected = False
#                 client_data.socket.close()
#                 client_data.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 break
#         time.sleep(1)


# def mp_menu():
#     client_data.sp_game = False
#
#     client_data.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#     thread = threading.Thread(target=data_thread)
#     thread.daemon = True
#     thread.start()
#
#     while client_data.mp_menu:
#         if client_data.connected:
#             send_object(('Name', player_data.name), client_data.socket)
#         else:
#             time.sleep(0.5)
#             continue
#
#         while client_data.mp_menu and client_data.connected:
#             clock.tick(client_data.framerate)
#             pos = pygame.mouse.get_pos()
#
#             if player_data.id != -1:
#                 if game_data.test_mode:
#                     client_data.mp_menu = False
#                     client_data.game = True
#
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     send_object(('Exit', ''), client_data.socket)
#                     pygame.quit()
#                     sys.exit()
#                 elif event.type == pygame.KEYUP:
#                     if event.key == pygame.K_ESCAPE:
#                         send_object(('Back to Main', ''), client_data.socket)
#                         client_data.mp_menu = False
#                         client_data.main_menu = True
#
#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     if new_game_button.rect.collidepoint(pos):
#                         new_game_button.click()
#                         send_object(('New Game', ''), client_data.socket)
#                     elif test_game_button.rect.collidepoint(pos):
#                         test_game_button.click()
#                         test_joined = False
#                         for i in client_data.game_ids:
#                             if client_data.player_counts[i] < 4:
#                                 send_object(('Join Game', i), client_data.socket)  # el kell dönteni melyik
#                                 test_joined = True
#                                 break
#                         if not test_joined:
#                             send_object(('New Game', 'Test Game'), client_data.socket)
#
#                     elif mp_back_button.rect.collidepoint(pos):
#                         mp_back_button.click()
#                         send_object(('Back to Main', ''), client_data.socket)  # más üzit kéne küldenie
#                         client_data.mp_menu = False
#                         client_data.main_menu = True
#                     else:
#                         for i, button in enumerate(game_lobby_buttons):
#                             if button.click(pos) \
#                                     and i in client_data.game_ids \
#                                     and client_data.player_counts[i] < 4:
#                                 send_object(('Join Game', i), client_data.socket)
#
#             draw_mp(SCREEN)


# def draw_mp(SCREEN):
#     SCREEN.fill((150, 150, 150))
#
#     for i, button in enumerate(game_lobby_buttons):
#         if i in client_data.game_ids and client_data.player_counts[i] < 4:
#             button.draw(SCREEN)
#
#     mp_menu_btns_group.draw(SCREEN)
#     pygame.display.update()


# def lobby():
#     global game_data
#     while client_data.lobby_menu:
#         clock.tick(client_data.framerate)
#         pos = pygame.mouse.get_pos()
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 send_object(('Exit Lobby', ''), client_data.socket)
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.KEYUP:
#                 if event.key == pygame.K_ESCAPE:
#                     send_object(('Exit Lobby', ''), client_data.socket)
#                     client_data.mp_menu = True
#                     player_data.id = None
#                     game_data = Game()
#                     client_data.lobby_menu = False
#
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if lobby_back_button.rect.collidepoint(pos):
#                     send_object(('Back to Main', ''), client_data.socket)  # más üzit kéne küldenie
#                     client_data.mp_menu = False
#                     client_data.main_menu = True
#
#                 if map_picture.rect.collidepoint(pos) and not game_data.isReady[player_data.id] and player_data.id == 0:
#                     client_data.lobby_menu = False
#                     client_data.map_selection = True
#
#                 elif lobby_icon_buttons[player_data.id].click(pos) and not game_data.isReady[player_data.id]:
#                     client_data.lobby_menu = False
#                     client_data.character_selection = True
#
#                 elif ready_button.rect.collidepoint(pos) and game_data.players[player_data.id].char_id != -1:
#                     if game_data.isReady[player_data.id]:
#                         send_object(('Not Ready', ''), client_data.socket)
#                     else:
#                         send_object(('Ready', ''), client_data.socket)
#         draw_lobby(SCREEN)


# def draw_lobby(SCREEN):
#     SCREEN.fill((150, 150, 150))
#
#     lobby_btns_group.draw(SCREEN)
#
#     for name in name_objs:
#         name.draw_text(SCREEN)
#     for btn in lobby_icon_buttons:
#         btn.draw(SCREEN)
#     for circle in ready_circles:
#         circle.draw(SCREEN)
#     pygame.display.update()


def map_selection():
    while client_data.map_selection:
        clock.tick(client_data.framerate)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    client_data.map_selection = False
                    if client_data.sp_game:
                        client_data.sp_menu = True
                    else:
                        client_data.lobby_menu = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(map_sel_buttons):
                    if btn.click(pos):
                        map_name.text = f'map{i+1}'
                        game_data.map = f'map{i+1}'
                        client_data.map_selection = False
                        if client_data.sp_game:
                            client_data.sp_menu = True
                        else:
                            send_object(('Set map', f'map{i+1}'), client_data.socket)
                            client_data.lobby_menu = True

        draw_map_menu(SCREEN)


def draw_map_menu(SCREEN):
    SCREEN.fill((200, 200, 200))

    for btn in map_sel_buttons:
        btn.draw(SCREEN)

    for map_name in map_names:
        map_name.draw(SCREEN)
    pygame.display.update()


def character_selection():
    while client_data.character_selection:
        clock.tick(client_data.framerate)
        pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    client_data.character_selection = False
                    if client_data.sp_game:
                        client_data.sp_menu = True
                    else:
                        client_data.lobby_menu = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if client_data.sp_game:
                    for i, button in enumerate(char_sel_buttons):
                        if button.click(pos):
                            game_data.players[player_data.id].char_id = i
                            game_data.chosen_char_ids = [i]
                            lobby_icon_buttons[player_data.id].image = gnome_icons[i]

                            client_data.character_selection = False
                            client_data.sp_menu = True
                else:
                    for i, button in enumerate(char_sel_buttons):
                        if button.click(pos) and i not in game_data.chosen_char_ids:
                            send_object(('Set char', i), client_data.socket)
                            client_data.character_selection = False
                            client_data.lobby_menu = True

        draw_character_menu(SCREEN)


def draw_character_menu(SCREEN):
    SCREEN.fill((200, 200, 200))

    for i, button in enumerate(char_sel_buttons):
        if i not in game_data.chosen_char_ids:
            button.draw(SCREEN)
        else:
            pass  # szürkítenie kéne a képet

    pygame.display.update()


# def new_action(lag_time, socket, message):  # just to create lag
#     msg = deepcopy(message)
#     time.sleep(lag_time)
#     send_object(('New Action', msg), socket)


def game_loop():
    char_id = game_data.players[player_data.id].char_id
    client_data.current_menu = base_menu_btns_group
    game_objects.generate_waypoints()

    while True:
        game_data.cursor.rect.topleft = list(pygame.mouse.get_pos())  # ezt lehet csak akkor kéne futtatni ha történik vlm az egérrel
        game_data.cursor.rect.x += client_data.base_scroll[0]
        game_data.cursor.rect.y += client_data.base_scroll[1]

        game_update()
        draw_game(SCREEN)

        # Handle Keys/Buttons
        if game_data.talent_tree_on:
            talent_tree_buttons(game_data)
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            try:
                handle_game_keys(event, client_data, game_data)
            except AttributeError:
                handle_game_mouse_buttons(event, client_data, game_data)

            if game_objects.my_char_group.sprite.new_order != game_objects.my_char_group.sprite.orders[-1]:
                order_type, target = game_objects.my_char_group.sprite.new_order
                game_objects.my_char_group.sprite.orders = [game_objects.my_char_group.sprite.new_order]
                game_objects.my_char_group.sprite.orders_num += 1

                if order_type == 'Move':
                    game_objects.my_char_group.sprite.path = find_path(
                        game_objects.my_char_group.sprite.rect.center, target, game_objects)
                    if len(game_objects.my_char_group.sprite.path) == 0:
                        game_objects.my_char_group.sprite.remove_order()
                elif order_type == 'Basic Attack':
                    start_time = time.time()
                    target_coord = target.rect.center

                # if not client_data.sp_game:
                #     orders_num = game_objects.my_char_group.sprite.orders_num
                #     orders = game_objects.my_char_group.sprite.orders
                #     game_objects.my_char_group.sprite.timeline.append([
                #         game_data.game_time, orders_num, orders
                #     ])
                #
                #     if client_data.artificial_lag > 0:
                #         message = (orders_num, orders)
                #         new_action_thread = threading.Thread(target=new_action, args=(
                #             client_data.artificial_lag, client_data.socket, message))
                #         new_action_thread.start()
                #     else:
                #         send_object(('New Action', (orders_num, orders)), client_data.socket)


def talent_tree_buttons(game_data):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_ESCAPE, pygame.K_c]:
                game_data.talent_tree_on = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left
                if game_objects.my_char_group.sprite.talent_tree.set_status(pygame.mouse.get_pos(), game_data):
                    game_objects.my_char_group.sprite.update_stats(game_data)


def handle_game_mouse_buttons(event, client_data, game_data):
    target_coord = game_data.cursor.rect.topleft
    in_play_area = False

    if 0 < target_coord[0] < game_objects.matrix.width and 0 < target_coord[1] < game_objects.matrix.height:
        in_play_area = True
    target_coord = int(target_coord[0]), int(target_coord[1])
    if event.type == pygame.MOUSEMOTION:
        if in_play_area:
            if event.buttons[2]:  # right
                if game_data.game_time - client_data.cursor_refresh_time > client_data.cursor_update_time \
                        and client_data.can_follow:
                    game_objects.my_char_group.sprite.new_order = ['Move', target_coord]
                    client_data.cursor_update_time = game_data.game_time

    elif event.type == pygame.MOUSEBUTTONDOWN:
        curs_coord = (target_coord[0] - client_data.base_scroll[0], target_coord[1] - client_data.base_scroll[1])
        if event.button == 1:  # Left
            if not game_data.battle_mode:
                if next_wave_btn.rect.collidepoint(curs_coord):
                    for obj in game_objects.trap_group:
                        obj.update(game_objects, game_data.dt)

                    game_objects.update_modifiers(game_data)
                    game_objects.next_wave(game_data)

                    # itt kéne először a game_data alapján a szorzókat kiszámolni (pl fatigue) építmények alapján.
                    # Majd a karakter képességek alapján kiszámolni a karakter szorzókat. (ez majd ha lesz szintlépés)
                    # Ezután a karakter actual statok számítása/beállítása
                    for chars in game_objects.characters_group:
                        chars.update_stats(game_data)

                    spawn_time_mlt = 0.01 * (100 - (game_data.wave_num - 1))
                    game_objects.generate_enemy_teams(easy_enemy_teams_dict[game_data.wave_num], spawn_time_mlt)
                    client_data.can_follow = False

                elif in_play_area:
                    if client_data.crafting_code:
                        game_objects.my_char_group.sprite.new_order = [client_data.crafting_code, target_coord]
                        client_data.can_follow = False

                    else:
                        game_objects.my_char_group.sprite.new_order = ['Move', target_coord]
                        client_data.cursor_update_time = game_data.game_time
                        client_data.can_follow = True

            # elif game_data.battle_mode:
            #     if game_menu_btn.rect.collidepoint(curs_coord):
            #         pass  # először játéktéren kívüli dolgokat ellenörzi
            #
            #     elif in_play_area:
            #         game_objects.my_char_group.sprite.new_order = ['Move', target_coord]
            #         client_data.cursor_update_time = game_data.game_time
            #         client_data.can_follow = True

        elif event.button == 3:
            if game_menu_btn.rect.collidepoint(curs_coord):
                pass  # először játéktéren kívüli dolgokat ellenörzi

            elif in_play_area:
                game_objects.my_char_group.sprite.new_order = ['Move', target_coord]
                client_data.cursor_update_time = game_data.game_time
                client_data.can_follow = True


def handle_game_keys(event, client_data, game_data):
    target_coord = game_data.cursor.rect.topleft
    if client_data.chat_window_open:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                type_area.text = type_area.text[:-1]
            elif event.key in (pygame.K_KP_ENTER, pygame.K_RETURN):
                client_data.chat_window_timer = time.time()
                client_data.chat_window_open = False
            else:
                type_area.text += event.unicode

    elif event.key == pygame.K_ESCAPE:
        if event.type == pygame.KEYDOWN:
            if game_data.talent_tree_on:
                game_data.talent_tree_on = False
            elif client_data.current_menu == base_menu_btns_group:
                # a GAME MENU-t kéne felhoznia, ahol lenne SETTINGS és EXIT button
                pygame.quit()
                sys.exit()
            else:
                client_data.current_menu = base_menu_btns_group
                game_objects.transparent_group.empty()
                client_data.crafting_code = None

    elif event.key in (pygame.K_KP_ENTER, pygame.K_RETURN):  # ez csak multiplayerbe kéne
        if event.type == pygame.KEYDOWN:
            client_data.chat_window_open = True

    elif event.key == pygame.K_LALT:
        if event.type == pygame.KEYUP:
            if game_data.alternative_mode > 1:
                game_data.alternative_mode = 0
            else:
                game_data.alternative_mode += 1

    elif event.key == pygame.K_1:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            # Ez így gáz...
            if client_data.current_menu == tile_btns_group:
                client_data.crafting_code = game_objects.new_obj('T-02')
            elif client_data.current_menu == garden_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-01')
            elif client_data.current_menu == floor_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-08')
            elif client_data.current_menu == wall_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-15')
            elif client_data.current_menu == garden_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-22')
            elif client_data.current_menu == floor_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-29')
            elif client_data.current_menu == wall_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-36')
            elif client_data.current_menu == char_spec_btns_group:
                client_data.crafting_code = game_objects.new_obj(game_objects.my_char_group.sprite.craft_skill1)

            if client_data.crafting_code:
                client_data.current_menu = directions_btns_group

    elif event.key == pygame.K_2:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == tile_btns_group:
                client_data.crafting_code = game_objects.new_obj('T-03')
            elif client_data.current_menu == garden_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-02')
            elif client_data.current_menu == floor_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-09')
            elif client_data.current_menu == wall_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-16')
            elif client_data.current_menu == garden_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-23')
            elif client_data.current_menu == floor_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-30')
            elif client_data.current_menu == wall_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-37')
            elif client_data.current_menu == char_spec_btns_group:
                client_data.crafting_code = game_objects.new_obj(game_objects.my_char_group.sprite.craft_skill2)

            if client_data.crafting_code:
                client_data.current_menu = directions_btns_group

    elif event.key == pygame.K_3:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == tile_btns_group:
                client_data.crafting_code = game_objects.new_obj('T-04')
            elif client_data.current_menu == garden_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-03')
            elif client_data.current_menu == floor_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-10')
            elif client_data.current_menu == wall_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-17')
            elif client_data.current_menu == garden_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-24')
            elif client_data.current_menu == floor_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-31')
            elif client_data.current_menu == wall_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-38')
            elif client_data.current_menu == char_spec_btns_group:
                client_data.crafting_code = game_objects.new_obj(game_objects.my_char_group.sprite.craft_skill3)

            if client_data.crafting_code:
                client_data.current_menu = directions_btns_group

    elif event.key == pygame.K_4:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == garden_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-04')
            elif client_data.current_menu == floor_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-11')
            elif client_data.current_menu == wall_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-18')
            elif client_data.current_menu == garden_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-25')
            elif client_data.current_menu == floor_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-32')
            elif client_data.current_menu == wall_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-39')
            elif client_data.current_menu == char_spec_btns_group:
                client_data.crafting_code = game_objects.new_obj(game_objects.my_char_group.sprite.craft_skill4)

            if client_data.crafting_code:
                client_data.current_menu = directions_btns_group

    elif event.key == pygame.K_5:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == garden_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-05')
            elif client_data.current_menu == floor_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-12')
            elif client_data.current_menu == wall_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-19')
            elif client_data.current_menu == garden_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-26')
            elif client_data.current_menu == floor_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-33')
            elif client_data.current_menu == wall_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-40')

            if client_data.crafting_code:
                client_data.current_menu = directions_btns_group

    elif event.key == pygame.K_6:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == garden_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-06')
            elif client_data.current_menu == floor_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-13')
            elif client_data.current_menu == wall_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-20')
            elif client_data.current_menu == garden_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-27')
            elif client_data.current_menu == floor_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-34')
            elif client_data.current_menu == wall_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-41')

            if client_data.crafting_code:
                client_data.current_menu = directions_btns_group

    elif event.key == pygame.K_7:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == garden_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-07')
            elif client_data.current_menu == floor_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-14')
            elif client_data.current_menu == wall_obj_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-21')
            elif client_data.current_menu == garden_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-28')
            elif client_data.current_menu == floor_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-35')
            elif client_data.current_menu == wall_trap_btns_group:
                client_data.crafting_code = game_objects.new_obj('O-42')

            if client_data.crafting_code:
                client_data.current_menu = directions_btns_group

    elif event.key == pygame.K_q:
        if event.type == pygame.KEYDOWN and game_data.battle_mode:
            game_objects.my_char_group.sprite.get_order(
                'S-01', target_coord, game_objects.my_char_group.sprite.battle_skill1, game_data, game_objects)
        elif event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = garden_trap_btns_group
            elif client_data.current_menu == directions_btns_group:
                game_objects.transparent_group.sprite.rotate(-90)

    elif event.key == pygame.K_w:
        if event.type == pygame.KEYDOWN and game_data.battle_mode:
            game_objects.my_char_group.sprite.get_order(
                'S-02', target_coord, game_objects.my_char_group.sprite.battle_skill2, game_data, game_objects)
        elif event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = floor_trap_btns_group
            else:
                # in need of an update
                client_data.crafting_code = game_objects.my_char_group.sprite.skill2
                game_objects.transparent_group.add(create_object(game_objects.my_char_group.sprite.skill2, transp=True))

    elif event.key == pygame.K_e:
        if event.type == pygame.KEYDOWN and game_data.battle_mode:
            game_objects.my_char_group.sprite.get_order(
                'S-03', target_coord, game_objects.my_char_group.sprite.battle_skill3, game_data, game_objects)
        elif event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = wall_trap_btns_group
            elif client_data.current_menu == directions_btns_group:
                game_objects.transparent_group.sprite.rotate(90)

    elif event.key == pygame.K_r:
        if event.type == pygame.KEYDOWN and game_data.battle_mode:
            game_objects.my_char_group.sprite.get_order(
                'S-04', target_coord, game_objects.my_char_group.sprite.battle_skill4, game_data, game_objects)
        elif event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = char_spec_btns_group

    elif event.key == pygame.K_a:
        if event.type == pygame.KEYDOWN and game_data.battle_mode:
            game_objects.my_char_group.sprite.get_order(
                'S-00', target_coord, game_objects.my_char_group.sprite.battle_skill0, game_data, game_objects)
        elif event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = garden_obj_btns_group

    elif event.key == pygame.K_s:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = floor_obj_btns_group

    elif event.key == pygame.K_d:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = wall_obj_btns_group

    elif event.key == pygame.K_f:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            if client_data.current_menu == base_menu_btns_group:
                client_data.current_menu = tile_btns_group

    elif event.key == pygame.K_x:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            game_objects.my_char_group.sprite.destroy(target_coord, game_objects)

    elif event.key == pygame.K_c:
        if event.type == pygame.KEYUP and not game_data.battle_mode:
            game_data.talent_tree_on = not game_data.talent_tree_on


def game_update():
    # Time
    game_data.current_time = time.time()
    game_data.dt = game_data.time_to_act = game_data.current_time - game_data.last_time
    game_data.last_time = game_data.current_time
    game_data.game_time = round(game_data.current_time, 2)
    timer_area.text = time.strftime("%M:%S", time.gmtime(round(game_data.last_time - game_data.start_time, 2)))

    # Game state check
    if not game_objects.enemies_group and game_data.battle_mode:
        round_finished = True
        for team_data in game_objects.enemy_wave.values():
            team = team_data[0]
            if len(team) > 0:
                round_finished = False
                break

        if round_finished:
            game_data.battle_mode = False
            game_data.handle_loot(game_objects.characters_group)
            game_objects.my_char_group.sprite.talent_tree.update(game_data)

            for trap in game_objects.trap_group:
                trap.update_effects(game_objects.characters_group)

    # Scroll
    if client_data.cam_smoothing:
        client_data.base_scroll[0] = round(
            client_data.base_scroll[0] + (game_objects.my_char_group.sprite.rect.centerx
                                          - client_data.base_scroll[0] - client_data.width / 2) / 20, 3)
        client_data.base_scroll[1] = round(
            client_data.base_scroll[1] + (game_objects.my_char_group.sprite.rect.centery
                                          - client_data.base_scroll[1] - client_data.height / 2) / 20, 3)
        client_data.scroll = client_data.base_scroll.copy()
        client_data.scroll = int(client_data.scroll[0]), int(client_data.scroll[1])
    else:
        client_data.scroll = int(game_objects.my_char_group.sprite.rect.centerx - client_data.width / 2), \
                             int(game_objects.my_char_group.sprite.rect.centery - client_data.height / 2)

    # Image update:
    for obj in game_objects.object_group:
        obj.image_update(game_data.current_time)
    for char in game_objects.characters_group:
        char.update_image()

    # Character orders execution / updates:
    if client_data.sp_game:
        if game_data.battle_mode:
            game_objects.my_char_group.sprite.update_skills(game_data.time_to_act)
            # ezt sztem az ellenfelekre is alkalmazni kéne majd
        game_objects.my_char_group.update(game_objects, game_data)
        game_data.time_to_act = game_data.dt
    elif client_data.prediction:
        pass

    # Update Enemies, projectiles or transparent object
    if game_data.alternative_mode == 2:
        game_objects.infobox.update(game_data.cursor.rect.topleft, client_data.base_scroll, game_objects.matrix.dict)

    if game_data.battle_mode:
        energy_multiplier = game_data.dt * game_data.energy_percent / 100
        game_objects.trap_group.update(game_objects, game_data.dt)
        game_objects.projectiles_group.update(game_objects, game_data.dt)
        game_objects.update_spawn_timers(game_data.dt)
        game_objects.spawn_enemies(game_data)
        for enemy in game_objects.enemies_group:
            enemy.update(game_data, game_objects)
    else:
        for key, resource_obj in resource_num_dict.items():
            resource_obj.update(game_objects.my_char_group.sprite.resources[key])

        if game_objects.transparent_group:
            for key, cost_obj in new_craft_cost_dict.items():
                cost_obj.update(f"-{game_objects.transparent_group.sprite.cost[key]}")
            if game_objects.transparent_group.sprite.type == 'Trap':
                game_objects.transparent_group.sprite.update_trap_dir()
            cursor_cell_coord = get_matrix_coord(game_data.cursor.rect.topleft, game_objects.cell_size)
            game_objects.transparent_group.sprite.rect.topleft = cursor_cell_coord

    # Chat update
    # if not client_data.chat_window_open and type_area.text and not client_data.sp_game:
    #     send_object(('Chat', type_area.text), client_data.socket)
    #     type_area.text = ''


def draw_game(SCREEN):
    pygame.display.update()
    clock.tick(client_data.framerate)

    # Background
    SCREEN.fill((50, 50, 50))

    if game_data.talent_tree_on:
        game_objects.my_char_group.sprite.talent_tree.draw(SCREEN, game_data)
        return

    for tile in game_objects.tile_group:
        tile.draw(SCREEN, client_data.base_scroll)
    for obj in game_objects.object_group:
        obj.draw(SCREEN, client_data.base_scroll)
        if game_data.alternative_mode >= 1:
            obj.draw_upgrades(SCREEN, client_data.base_scroll)
    for trap in game_objects.trap_group:
        trap.draw(SCREEN, client_data.base_scroll)
        if game_data.alternative_mode >= 1:
            trap.draw_upgrades(SCREEN, client_data.base_scroll)

    # for tile in game_objects.tile_group:  # just to show cell coords
    #     tile.draw_cell_indexes(SCREEN, client_data.base_scroll)

    game_objects.draw_path(SCREEN, client_data.base_scroll, game_objects.my_char_group.sprite)

    for item in items_group:
        item.draw(SCREEN, client_data.base_scroll)

    # Players
    for char in game_objects.characters_group:
        char.draw(SCREEN, client_data.scroll)

    if game_data.battle_mode:
        # Enemies
        for enemy in game_objects.enemies_group:
            enemy.draw(SCREEN, client_data.base_scroll)
        for proj in game_objects.projectiles_group:
            proj.draw(SCREEN, client_data.base_scroll)

        # Effects
        for effect in game_objects.effect_group:
            effect.draw_effects(SCREEN, client_data.base_scroll)

        battle_skill_btns_group.draw(SCREEN)

    else:
        craft_mode_btns_group.draw(SCREEN)
        # Resource Area
        for res_num_obj in resource_num_dict.values():
            res_num_obj.draw(SCREEN)

        if game_objects.transparent_group:
            for cost_obj in new_craft_cost_dict.values():
                if int(cost_obj.text) < 0:
                    cost_obj.draw(SCREEN)

        client_data.current_menu.draw(SCREEN)

    for obj in game_objects.transparent_group:
        obj.draw(SCREEN, client_data.base_scroll)

    # InfoBox
    if game_data.alternative_mode == 2:
        game_objects.infobox.draw(SCREEN)

    game_menu_btn_group.draw(SCREEN)
    game_objects.my_char_group.sprite.draw_hp_bar(SCREEN)
    timer_area.draw(SCREEN)

    # if client_data.chat_window_open \
    #         or game_data.last_time - client_data.chat_window_timer < 5:  # vagy épp érkezett üzenet
    #     chat_area.draw(SCREEN)
    #     type_area.draw(SCREEN)
    # az üzeneteket sokáig kéne látni, de szürke háttér nélkül, csak a szöveget.


def main():
    # pygame.mouse.set_visible(False)
    # pygame.mouse.set_cursor()
    player_data.name = client_data.player_name
    while True:
        if client_data.main_menu:
            main_menu()
        elif client_data.exit_main_menu:
            exit_main_menu()
        elif client_data.sp_menu:
            sp_menu()
        # elif client_data.mp_menu:
        #     mp_menu()
        elif client_data.settings_menu:
            options()
        elif client_data.game:
            game_loop()
        # elif client_data.lobby_menu:
        #     lobby()
        elif client_data.map_selection:
            map_selection()
        elif client_data.character_selection:
            character_selection()
        else:
            pass  # ide egy töltőképernyő


game_data = Game()
game_objects = GameObject()

main()
# profile.run('main()')
