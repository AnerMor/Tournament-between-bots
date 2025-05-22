#this bot will always defect
import time

import time
import bot_api


def main():

    defect_bot = bot_api.GameState("DEFECT_BOT")
    # Client setup

    # Game loop
    while not defect_bot.is_competition_over:
        for _ in range(bot_api.NUM_ROUNDS):
            # Receive round start signal
            if not defect_bot.get_round_start_signal():
                break
            decision = bot_api.DEFECT
            defect_bot.send_decision(decision)

            # Receive and print score
            defect_bot.update_score()

            print(f"my total score: {defect_bot.my_total_score}\n")

        defect_bot.reset_for_new_game()


if __name__ == "__main__":
    main()