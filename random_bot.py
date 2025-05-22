# randomly selecting between cooperating and defecting in each round
import time
import bot_api
import random
import socket


def main():
    random_bot = bot_api.GameState("RANDOM_BOT")
    # Client setup
    # client_socket = bot_api.connect_to_server()

    # Game loop
    while not random_bot.is_competition_over:
        for _ in range(bot_api.NUM_ROUNDS):
            # Receive round start signal
            if not random_bot.get_round_start_signal():
                break

            a = random.randint(0, 1)
            if a == 0:
                decision = bot_api.DEFECT
            else:
                decision = bot_api.COOPERATE

            random_bot.send_decision(decision)

            # Receive and print score
            random_bot.update_score()

            print(f"my total score: {random_bot.my_total_score}\n")

        random_bot.reset_for_new_game()


if __name__ == "__main__":
    main()
