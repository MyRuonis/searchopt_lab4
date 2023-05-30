from numpy import random

from splendor.game import SplendorGame


class Assignment:
    def __init__(self, game: SplendorGame):
        self.game = game
        self.random = random.Generator(random.PCG64(27))
        self.player_id = -1

    def __call__(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    def search(self, board) -> int:
        valids = self.game.valid_moves(board, self.player_id)
        candidates = []
        current_score = self.game.player_score(board, self.player_id)
        for act, score in enumerate(valids):
            if score == 0:
                continue

            next_board, _ = self.game.next_state_of(board, self.player_id, act)
            score = self.game.player_score(next_board, self.game.next_player_of(self.player_id))
            candidates += [(score, act)]

        max_score, _ = max(candidates, key=lambda x: x[0])
        if max_score == current_score:
            # Card buying actions first
            actions_leading_to_max = [m for m, v in enumerate(valids) if v > 0 and 0 <= m < 12]
            # If there's no such action, try gem collecting action
            if len(actions_leading_to_max) == 0:
                actions_leading_to_max = [m for m, v in enumerate(valids) if
                                          v > 0 and 12 + 15 + 3 <= m < 12 + 15 + 3 + 30]
            # If it's not possible to collect gems, select from all actions
            if len(actions_leading_to_max) == 0:
                actions_leading_to_max = [m for (m, v) in enumerate(valids) if v > 0]
        else:
            actions_leading_to_max = [m for s, m in candidates if s == max_score]

        move = random.choice(actions_leading_to_max)
        return move

    def collect_action_done(self, board, player, action):
        pass
