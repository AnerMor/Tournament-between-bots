# starts with cooperating and then mimicking the opponents decisions
import time
import bot_api


def main():
    TitForTat_bot = bot_api.GameState("TIT-FOR-TAT_BOT")
    # Client setup
    # client_socket = bot_api.connect_to_server()

    # Game loop
    while not TitForTat_bot.is_competition_over:
        for _ in range(bot_api.NUM_ROUNDS):
            # Receive round start signal
            if not TitForTat_bot.get_round_start_signal():
                break

            if TitForTat_bot.opponent_last_decision == bot_api.DEFECT:
                decision = bot_api.DEFECT
            else:
                decision = bot_api.COOPERATE

            TitForTat_bot.send_decision(decision)

            # Receive and print score
            TitForTat_bot.update_score()

            print(f"my total score: {TitForTat_bot.my_total_score}\n")

        TitForTat_bot.reset_for_new_game()

    # # Close connection
    # TitForTat_bot.client_socket.close()


if __name__ == "__main__":
    main()
