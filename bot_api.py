import socket
import struct
import arcade
import time


HOST = '127.0.0.1'
PORT = 12345
MAX_MESSAGE_LENGTH = 1024

COOPERATE = 'cooperate'
DEFECT = 'defect'


ROUND_START_BYTE = 5
JOIN_GAME = 0
DECISION_TYPE = 2
WIN_TYPE = 4

COMPETITION_OVER_TYPE = 6

SCORE_TYPE = 3
NUM_ROUNDS = 10
NUM_PLAYERS_TYPE = 7
RECEIVE_TOTAL_SCORES_TYPE = 8

WINDOW_LENGTH = 700
WINDOW_WIDTH = 1200

EMPTY_CIRCLE_COLOR = arcade.color.WHITE
COOPERATE_CIRCLE_COLOR = arcade.color.BRIGHT_GREEN
DEFECT_CIRCLE_COLOR = arcade.color.CANDY_APPLE_RED

COLOR_DICT = {
    None: EMPTY_CIRCLE_COLOR,
    COOPERATE: COOPERATE_CIRCLE_COLOR,
    DEFECT: DEFECT_CIRCLE_COLOR
}


class GameState:

    def __init__(self, name='', graphics=True):
        self.client_socket = None
        self.game_number = 1
        self.round = 0
        self.my_total_score = 0
        self.opponent_total_score = 0
        self.opponent_last_decision = ''
        self.opponent_decisions_list = []
        self.my_last_decision = ''
        self.my_decisions_list = []
        self.my_name = name
        self.graphics = graphics
        self.is_game_over = False
        self.num_rounds = NUM_ROUNDS

        self.connect_to_server()

        self.is_competition_over = False

        if self.graphics:
            if self.round > 0:
                arcade.start_render()
                arcade.close_window()
                arcade.finish_render()
                arcade.open_window(WINDOW_WIDTH, WINDOW_LENGTH, self.my_name)
                self.create_graphics()

    def reset_for_new_game(self):
        self.round = 0
        self.my_total_score = 0
        self.opponent_total_score = 0
        self.opponent_last_decision = ''
        self.opponent_decisions_list = []
        self.my_last_decision = ''
        self.my_decisions_list = []
        self.is_game_over = False
        self.game_number += 1

        arcade.start_render()
        arcade.set_background_color(arcade.color.BLACK)
        arcade.draw_text(f"Loading next game...", 70, 500, arcade.color.WHITE, 40, font_name="Kenney Rocket Square")
        arcade.draw_text(f"Loading next game...", 70, 500, arcade.color.WHITE, 40, font_name="Kenney Rocket Square")
        arcade.finish_render()

    def connect_to_server(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        self.client_socket = client_socket
        print(f"Connected to server: {HOST}:{PORT}")
        self.send_message(JOIN_GAME, self.my_name.encode())
        self.loading_screen()
        return client_socket

    def get_round_start_signal(self):
        round_start_signal = self.client_socket.recv(1)
        if round_start_signal == ROUND_START_BYTE.to_bytes(1, byteorder='big'):
            print("Round start")
            return True

        if round_start_signal == COMPETITION_OVER_TYPE.to_bytes(1, byteorder='big'):
            print("competition ended")
            self.is_competition_over = True

            sorted_names = []
            sorted_scores = []

            num_players = int(self.client_socket.recv(1).decode())
            print(f"num players {num_players}")

            for i in range(num_players):
                received_name = self.client_socket.recv(40).decode()
                # print(f"received name {received_name.split(' ')[0]}")
                sorted_names.append(received_name.split(' ')[0])
            for i in range(num_players):
                received_score = self.client_socket.recv(10).decode()
                # print(f"received score {received_score.split(' ')[0]}")
                sorted_scores.append(received_score.split(' ')[0])

            print(f"\nFinal scores")
            arcade.start_render()
            arcade.set_background_color(arcade.color.BLACK)
            arcade.draw_text(f"SCOREBOARD", 300, 630, arcade.color.BRIGHT_TURQUOISE, 50, font_name="Kenney Rocket Square")
            for i in range(num_players):
                print(f"place {i+1}: {sorted_names[i]} with {sorted_scores[i]} points")
                arcade.draw_text(f"place {i+1}: {sorted_names[i]} with {sorted_scores[i]} points", 70, 570-80*i,
                                 arcade.color.WHITE,  20, font_name="Kenney Rocket Square")

                if sorted_names[i] == self.my_name:
                    arcade.draw_rectangle_outline(WINDOW_WIDTH/2, 580-80*i, WINDOW_WIDTH - 100, 40, arcade.color.DAFFODIL, 5)

            arcade.finish_render()
            arcade.run()

            self.client_socket.close()
            return False

    def send_decision(self, decision):
        self.my_last_decision = decision
        self.my_decisions_list.append(decision)
        self.send_message(DECISION_TYPE, decision.encode())

    def update_score(self):
        type = self.client_socket.recv(1)
        if type[0] == WIN_TYPE:
            print("you Won the game!")
            self.is_game_over = True
            return

        score = receive_integer(self.client_socket)
        self.round += 1
        print(f"Round {self.round} - Score: {score}")
        self.my_total_score += int(score)
        self.opponent_total_score += self.calculate_op_score(score)
        self.opponent_last_decision = self.calculate_op_decision(score)
        self.opponent_decisions_list.append(self.opponent_last_decision)
        print(f"Opponent's last decision: {self.opponent_last_decision}")

        if self.graphics:
            self.create_graphics()

        if self.round >= self.num_rounds:
            self.is_game_over = True


    def calculate_op_decision(self, s):
        if s == 5 or s == 3:
            return COOPERATE

        elif s == 1 or s == 0:
            return DEFECT

    def calculate_op_score(self, s):
        if s == 1:
            return 1
        elif s == 5:
            return 0
        elif s == 3:
            return 3

        elif s == 0:
            return 5

    def send_message(self, type, data):
        type = type.to_bytes(1, byteorder='big')
        self.client_socket.send(type + data)
        # print(f"message {type} data {data}")

    def get_average_points(self):
        return self.my_total_score / self.round

    def create_graphics(self):
        try:
            arcade.set_background_color(arcade.color.BLACK)
            arcade.start_render()

            arcade.draw_rectangle_filled(WINDOW_WIDTH - 600, WINDOW_LENGTH - 380, WINDOW_WIDTH - 320, WINDOW_LENGTH - 420, arcade.color.DAFFODIL)
            arcade.draw_rectangle_filled(WINDOW_WIDTH - 600, WINDOW_LENGTH-380, WINDOW_WIDTH-350, WINDOW_LENGTH-450, arcade.color.BOLE)
            # arcade.draw_line(170, 320, 1030, 320, arcade.color.DAFFODIL, 10)

            for i in range(len(self.my_decisions_list)):
                self.draw_circle(i, 0, self.opponent_decisions_list[i])
                self.draw_circle(i, 1, self.my_decisions_list[i])

            for i in range(len(self.my_decisions_list), NUM_ROUNDS):
                self.draw_circle(i, 0)
                self.draw_circle(i, 1)

            arcade.draw_text(str(self.my_total_score), 1050, 370, arcade.color.WHITE, 40, font_name="Kenney Rocket Square")
            arcade.draw_text(str(self.opponent_total_score), 1050, 250, arcade.color.WHITE, 40, font_name="Kenney Rocket Square")

            if self.round == 10:
                self.round -= 1

            arcade.draw_text(f"ROUND {str(self.round + 1)}", 300, 500, arcade.color.BRIGHT_TURQUOISE, 60, font_name="Kenney Rocket Square")
            arcade.draw_text("MY BOT", 25, 370, arcade.color.WHITE, 20, font_name="Kenney Rocket Square")
            arcade.draw_text("OPPONENT", 5, 250, arcade.color.WHITE, 15, font_name="Kenney Rocket Square")
            arcade.draw_text(f"GAME {self.game_number}", 150, 600, arcade.color.WHITE, 15, font_name="Kenney Rocket Square")

            arcade.finish_render()
            time.sleep(1)
        except KeyboardInterrupt:
            print("keyboard interrupt")

    def loading_screen(self):
        arcade.open_window(WINDOW_WIDTH, WINDOW_LENGTH, self.my_name)
        arcade.set_background_color(arcade.color.BLACK)
        arcade.start_render()
        arcade.draw_text(f"WELCOME {self.my_name} ", 70, 500, arcade.color.WHITE, 40, font_name="Kenney Rocket Square")
        arcade.draw_text(f"GAME WILL START SOON ", 100, 300, arcade.color.WHITE, 25, font_name="Kenney Rocket Square")
        arcade.finish_render()

    def draw_circle(self, round, whos_line, decision=None):
        color = COLOR_DICT[decision]
        center_x = 330 + 80*(round-1)
        center_y = 270 + 100*whos_line
        arcade.draw_circle_filled(center_x, center_y, 30, color)


def send_int(type, client_socket, num):
    type = type.to_bytes(1, byteorder='big')
    num_bytes = struct.pack('i', num)
    client_socket.send(type + num_bytes)
    # print(f"message {type + num_bytes}")


def receive_integer(server_socket):
    num_bytes = server_socket.recv(4)
    # print(f"num bytes {num_bytes}")
    num = struct.unpack('i', num_bytes)[0]
    return num
