import threading
from collections import Counter
from importlib import import_module
from time import sleep, time
from traceback import format_exc

try:
    import thread
except ImportError:
    import _thread as thread


def exit_after(s):
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, thread.interrupt_main, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer


class Arena:
    """
    An Arena class where any 2 ~ 4 agents can be play in turn against each other.
    """

    def __init__(self, game, *players):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See main.py for pitting
        human players/other baselines with each other.
        """
        self.game = game
        self.player_names = players
        self.players = [self.create_player(p) for p in players]

    def create_player(self, name):
        # Initialize algorithm
        module = import_module(f'search.search_{name}' if not name.startswith('human') else 'search.human')
        return module.Assignment(self.game)

    def rotate_players(self):
        self.players = self.players[1:] + self.players[:1]
        self.player_names = self.player_names[1:] + self.player_names[:1]

    def play(self, verbose=False, wait=5):
        """
        Executes one episode of a game.

        Returns:
            List of winners (player names)
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """

        retired_players = set()

        # Assign ID to each player
        for p, player in enumerate(self.players):
            player.player_id = p

        cur_player = 0
        failures = Counter()
        board = self.game.initial_state()
        it = 0
        while not self.game.game_ended(board).any():
            if len(retired_players) == len(self.players) - 1:
                # All the other players are retired. The remaining player is the winner.
                break

            it += 1
            if verbose:
                self.game.print_board(board, self.player_names)
                print()
                print(f'Turn {it} Player {cur_player} ({self.player_names[cur_player]}): ', end='')

            if cur_player in retired_players:
                action = 60  # Do nothing without considering other actions
                is_valid = True
            else:
                assert self.players[cur_player].player_id == cur_player
                try:
                    action = exit_after(300)(self.players[cur_player].search)(board)
                except Exception as e:
                    action = 60
                    failures.update([cur_player])

                    if verbose:
                        if isinstance(e, KeyboardInterrupt):
                            print(f'Player {cur_player} failure ({failures[cur_player]}/3): Used more than 5 minutes to think.')
                        else:
                            print(f'Player {cur_player} failure ({failures[cur_player]}/3): {format_exc()}')

                    if failures[cur_player] >= 3:
                        if verbose:
                            print(f'Player {cur_player} retire: The number of failures by player {cur_player} exceeded 3')
                        retired_players.add(cur_player)
                        board = self.game.retire_player(board, self.players[cur_player])

                valids = self.game.valid_moves(board, cur_player)
                is_valid = valids[action] != 0

                if verbose:
                    print(f'P{cur_player} decided to {self.game.move_as_string(action)}')
                    sleep(wait)  # sleep 5 seconds to let humans read

            if not is_valid:
                # Pass the turn
                if verbose:
                    print(f'As the action is illegal, the game system rejected "{self.game.move_as_string(action)}." '
                          f'Instead, the player will do nothing.')
                action = 60  # Do nothing action

            # Notify a player's action to the board and all players
            board, next_player = self.game.next_state_of(board, cur_player, action)
            for player in self.players:
                player.collect_action_done(board, cur_player, action)
            cur_player = next_player

        if len(retired_players) < len(self.players) - 1:
            result = []
            for p, utility in enumerate(self.game.game_ended(board).tolist()):
                if utility > 0:
                    result.append(self.player_names[p])
        else:
            result = [p for i, p in enumerate(self.player_names) if i not in retired_players]

        if verbose:
            self.game.print_board(board, self.player_names)
            print("Game over: Turn ", str(it), "Winners ", result)
            sleep(wait)  # sleep 5 seconds to let humans read

        return result
