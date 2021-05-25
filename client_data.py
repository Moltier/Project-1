import time, csv, pyautogui
from spec_functions import cp


class Client:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.fullscreen = True
        self.max_name_len = 15

        self.player_name = ''
        self.width = 800
        self.height = 500
        self.framerate = 60
        self.cam_smoothing = True
        self.prediction = True
        self.artificial_lag = 0  # sec

        self.base_scroll = [0, 0]
        self.scroll = [0, 0]
        self.game_ids = []
        self.player_counts = []
        self.key_timer = 0
        self.chars = {}
        self.chars_pred = {}

        self.sp_game = True
        self.message = ''

        # menus
        self.main_menu = True
        self.exit_main_menu = False
        self.sp_menu = False
        self.mp_menu = False
        self.settings_menu = False
        self.lobby_menu = False
        self.map_selection = False
        self.character_selection = False
        self.game = False  # gameIsRunning
        self.exit_game = False

        # in game menus
        self.current_menu = None

        self.crafting_code = None
        self.craftable_tile = None
        self.craftable_code = None
        self.transparent_obj = None
        self.cursor_cell = None
        self.can_follow = False  # Cursor követés

        self.left_mouse_down = False
        self.left_mouse_released = False
        self.left_shift_down = False
        self.chat_window_open = False
        self.chat_window_timer = time.time()
        self.chat_messages = []
        self.cursor_update_time = time.time()
        self.cursor_refresh_time = 0.05
        self.action = None  # character action

        # battle mode
        self.targeting_distance = 50

    def update(self, data):  # szervertől kapott adattal frissíti a sajátot
        for i, v in data.items():
            self.game_ids.append(i)
            self.player_counts.append(v)

    def save_settings(self, settings_list):
        for setting in settings_list:
            if setting.name == 'Fullscreen':
                self.fullscreen = setting.data
            elif setting.name == 'Resolution':
                res_list = setting.data.split('x')
                self.width = int(res_list[0])
                self.height = int(res_list[1])
            elif setting.name == 'Framerate':
                self.framerate = int(setting.data)
            elif setting.name == 'Camera Scrolling':
                self.cam_smoothing = setting.data
            elif setting.name == 'Client Prediction':
                self.prediction = setting.data
            elif setting.name == 'Player Name':
                self.name = setting.data

        with open('Data\\settings', 'w', encoding='utf-8') as csv_file:
            fieldnames = ['setting', 'value']
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()
            csv_writer.writerow({'setting': 'Fullscreen', 'value': f'{self.fullscreen}'})
            csv_writer.writerow({'setting': 'Resolution', 'value': f'{self.width}x{self.height}'})
            csv_writer.writerow({'setting': 'Framerate', 'value': f'{self.framerate}'})
            csv_writer.writerow({'setting': 'Camera Scrolling', 'value': f'{self.cam_smoothing}'})
            csv_writer.writerow({'setting': 'Client Prediction', 'value': f'{self.prediction}'})
            csv_writer.writerow({'setting': 'Player Name', 'value': self.player_name})


client_data = Client()

with open('Data\\settings', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(filter(lambda row: row[0] != '#', csv_file))
    for line in csv_reader:
        value = line['value'].strip()
        if line['setting'] == 'Fullscreen':
            if value == 'True':
                client_data.fullscreen = True
                client_data.width = pyautogui.size().width
                client_data.height = pyautogui.size().height
            else:
                client_data.fullscreen = False
        elif line['setting'] == 'Resolution' and not client_data.fullscreen:
            resolution = value.split('x')
            client_data.width = int(resolution[0])
            client_data.height = int(resolution[1])
        elif line['setting'] == 'Framerate':
            client_data.framerate = int(value)
        elif line['setting'] == 'Camera Scrolling':
            if value == 'True':
                client_data.cam_smoothing = True
            else:
                client_data.cam_smoothing = False
        elif line['setting'] == 'Client Prediction':
            if value == 'True':
                client_data.prediction = True
            else:
                client_data.prediction = False
        elif line['setting'] == 'Player Name':
            if value != '':
                client_data.player_name = value  # ezt nem kezeli le jól
        else:
            cp(666, 'Error. Invalid setting in client_data.py.')
