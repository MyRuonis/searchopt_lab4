from numpy import random

from splendor.game import SplendorGame
from splendor.logic import move_to_str


class Assignment:
    def __init__(self, game: SplendorGame):
        self.game = game
        self.random = random.Generator(random.PCG64(27))
        self.player_id = -1

    def __call__(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    def show_all_moves(self, valid):
        for i, v in enumerate(valid):
            if i in [12, 12 + 15, 12 + 15 + 3 + 30] or i % 5 == 0:
                print()
            if v:
                print(f'[{i}] {move_to_str(i, short=True):15s}', end='\t')
        print()

    def show_main_moves(self, valid):
        # Number of max gems that player can take
        if any(valid[45:55]):
            can_take = 3
        elif any(valid[35:45]):
            can_take = 2
        elif any(valid[30:35]):
            can_take = 1
        else:
            can_take = 0
        need_to_give_gems = (self.game.board.players_gems[self.player_id].sum() >= 9)

        print()
        if any(valid[12:27]):
            print(f'12-26 = rsv', end='\t')
        for i, v in enumerate(valid):
            if i % 5 == 0:
                print()
            if v:
                if 0 <= i < 12 or 27 <= i < 30 or (30 <= i < 35 and can_take <= 1) or (
                        35 <= i < 45 and can_take <= 2) or 45 <= i < 60 or (60 <= i < 80 and need_to_give_gems):
                    print(f'{i} = {move_to_str(i, short=True):15s}', end='\t')
        print('([+] to show all moves)')

    def search(self, board) -> int:
        valid = self.game.valid_moves(board, self.player_id)

        self.show_main_moves(valid)
        while True:
            input_move = input()
            if input_move == '+':
                self.show_all_moves(valid)
            else:
                try:
                    a = int(input_move)
                    if not valid[a]:
                        raise Exception('')
                    break
                except:
                    print('Invalid move:', input_move)
        return a

    def collect_action_done(self, board, player, action):
        pass
