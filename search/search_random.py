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
        valids = [a for a, v in enumerate(self.game.valid_moves(board, self.player_id)) if v == 1]
        return self.random.choice(valids)

    def collect_action_done(self, board, player, action):
        pass
