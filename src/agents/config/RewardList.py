class RewardList:
    KILL = 200                  # reward for killing an enemy
    DIE = 0                     # reward for dying

    DAMAGES = 3                 # reward for doing 1 damage
    HP_LOSS = -1                # reward for losing 1 hp

    ROUND_START = -5            # reward when the round starts
    BAD_MOVEMENT = -2           # reward for making a bad movement action
    BAD_SPELL_CASTING = -10     # reward for casting a spell without being in enemy's range
    BAD_SPELL_SELECTION = -2    # reward for trying to cast a spell without the necessary amount of PA