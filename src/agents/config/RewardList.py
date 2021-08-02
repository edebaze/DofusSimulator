import inspect


class RewardList:
    KILL = 500                  # reward for killing an enemy
    DIE = 0                     # reward for dying
    REACH_MAX_TURN = -200          # reward for ending game with max turn

    DAMAGES = 3                 # reward for doing 1 damage
    HP_LOSS = 0                 # reward for losing 1 hp

    ROUND_START = 0             # reward when the round starts
    BAD_MOVEMENT = -50            # reward for making a bad movement action
    BAD_SPELL_CASTING = -100       # reward for casting a spell without being in enemy's range
    BAD_SPELL_SELECTION = -50     # reward for trying to cast a spell without the necessary amount of PA

    @staticmethod
    def get_rewards_dict():
        rewards = dict()
        for (reward_name, reward_value) in inspect.getmembers(RewardList):
            if RewardList.is_reward_name(reward_name):
                rewards[reward_name] = reward_value

        return rewards

    @staticmethod
    def get_rewards():
        rewards = [reward_value for (reward_name, reward_value) in inspect.getmembers(RewardList) if RewardList.is_reward_name(reward_name)]
        rewards.sort()
        return rewards

    @staticmethod
    def is_reward_name(item_name: str) -> bool:
        if not item_name.isupper():
            return False

        if item_name.startswith('_'):
            return False

        return True