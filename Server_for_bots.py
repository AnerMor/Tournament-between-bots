import socket
import bot_api
import threading


# Server setup
HOST = '127.0.0.1'
PORT = 12345
NUM_PLAYERS = 2
NUM_ROUNDS = 10


class Player:
    def __init__(self):
        self.socket = None
        self.name = None
        self.total_competition_score = 0
        self.game_score = 0
        self.is_in_game = False
        self.amount_of_wins = 0

    def __repr__(self):
        return f"player \"{self.name.decode()}\""


def play_round(players):
    # Send round start signal
    for player in players:
        player.socket.send(bot_api.ROUND_START_BYTE.to_bytes(1, byteorder='big'))

    # Receive choices from clients
    choices = {}
    for player in players:
        choice = check_legal_decision(check_legal_message(player.socket, bot_api.DECISION_TYPE, 10))
        # name = name.decode()
        if choice is None:
            player.socket.close()
            return None, player.socket
        else:
            choices[player] = choice

    # Print decisions
    for player, choice in choices.items():
        print(f"{player.name.decode()} decision: {choice}")

    # Calculate scores
    scores = calculate_scores(choices)

    # Send scores to clients
    for player, score in scores.items():
        bot_api.send_int(bot_api.SCORE_TYPE, player.socket, score)
        player.total_competition_score += score
    return scores, None


def check_legal_message(client_socket, expected_type, expected_length):
    type = client_socket.recv(1)
    if type[0] != expected_type:
        print(f"unexpected type {type}")
        return None
    message = client_socket.recv(expected_length)
    try:
        message = message.decode()
    except Exception:
        print(f"Failed to decode message {message}")
        return None
    return message


def check_legal_decision(decision):
    if decision is None:
        return
    if decision == bot_api.COOPERATE or decision == bot_api.DEFECT:
        return decision
    print(f"unexpected  {decision}")
    return


def calculate_scores(choices):
    # print(f"choices {choices.items()})")
    scores = {}
    players = choices.keys()
    decisions = list(choices.values())

    if decisions[0] == decisions[1]:
        if decisions[0] == bot_api.COOPERATE:
            score = 3
        else:
            score = 1
        for player in players:
            scores[player] = score

    else:
        for client, choice in choices.items():
            if choice == bot_api.COOPERATE:
                scores[client] = 0
            else:
                scores[client] = 5

    # print(scores)
    return scores

#  Accept client connections


def wait_for_players(NUM_PLAYERS, server_socket):
    clients = []
    for i in range(NUM_PLAYERS):
        # print(f"server socket {server_socket}")
        client_socket, _ = server_socket.accept()
        print(f"socket {client_socket}")
        request = client_socket.recv(bot_api.MAX_MESSAGE_LENGTH)
        print(f"request {request}")

        if request[0] == bot_api.JOIN_GAME:
            player = Player()
            player.name = request[1:]
            player.socket = client_socket
            clients.append(player)
            print(f"Client connected: {client_socket.getpeername()}")

    return clients


def create_new_game(players):

    # Game loop

    total_scores = {player: 0 for player in players}
    print(f"total scores:  {total_scores}")
    for i in range(NUM_ROUNDS):
        print(f"\nRound {i + 1}")
        round_scores, loser_player = play_round(players)
        if loser_player is not None:
            total_scores[loser_player] = -1
            print("Game aborted")
            break
        for player, score in round_scores.items():
            total_scores[player] += score

    # Determine winner
    winner_player = max(total_scores, key=total_scores.get)
    winner_player.amount_of_wins += 1

    return winner_player


def handle_game(client_sockets):
    winner_player = create_new_game(client_sockets)
    print(f"\n And the winner is {winner_player}!")
    for client in client_sockets:
        client.is_in_game = False
    # end_connections(client_sockets)


def end_connections(players):
    # Close connections
    for player in players:
        player.socket.close()


def create_competition(players):
    games_list = []

    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            games_list.append([players[i], players[j]])

    games_played = []
    game_threads = []

    print(f"games list {games_list}")
    while len(games_played) < len(games_list):
        for game in games_list:
            if game in games_played:
                continue
            if (not game[0].is_in_game) and (not game[1].is_in_game):
                print(f"\nstarting game {game}")
                game[0].is_in_game = True
                game[1].is_in_game = True
                game_thread = threading.Thread(target=handle_game, args=(game,))
                game_threads.append(game_thread)
                game_thread.start()
                games_played.append(game)

    for thread in game_threads:
        thread.join()

    sorted_players_by_score = sorted(players, key=lambda player: player.total_competition_score, reverse=True)
    i = 1
    for player in sorted_players_by_score:
        print(f"\nplace {i}: {player.name.decode()} with {player.total_competition_score} points and {player.amount_of_wins} wins")
        i += 1

    for player in players:
        player.socket.send(bot_api.COMPETITION_OVER_TYPE.to_bytes(1, byteorder='big'))

        player.socket.send(str(NUM_PLAYERS).encode())
        for client in sorted_players_by_score:
            addition_spaces = 40-len(client.name.decode())
            player.socket.send(client.name + addition_spaces*' '.encode())

        for client in sorted_players_by_score:
            addition_spaces = 10-len(str(client.total_competition_score))
            player.socket.send(str(client.total_competition_score).encode() + addition_spaces*' '.encode())


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(NUM_PLAYERS)
    print(f"Server is listening on {HOST}:{PORT}")


    while True:
        players = wait_for_players(NUM_PLAYERS, server_socket)

        create_competition(players)


        # game_thread = threading.Thread(target=handle_game, args=(players,))
        # games_list.append(game_thread)
        # game_thread.start()


if __name__ == "__main__":
    main()
