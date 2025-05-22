# this bot always cooperate

import bot_api
# Client setup


def main():

    cooperate_bot = bot_api.GameState('COOPERATE_BOT')
    # Client setup

    # Game loop
    while not cooperate_bot.is_competition_over:
        for _ in range(bot_api.NUM_ROUNDS):
            # Receive round start signal
            if not cooperate_bot.get_round_start_signal():
                break
            decision = bot_api.COOPERATE
            cooperate_bot.send_decision(decision)

            # Receive and print score
            cooperate_bot.update_score()

            print(f"my total score: {cooperate_bot.my_total_score}\n")

            # time.sleep(1)

        cooperate_bot.reset_for_new_game()


if __name__ == "__main__":
    main()
