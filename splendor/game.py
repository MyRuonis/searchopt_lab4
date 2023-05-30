from typing import List

from .logic import move_to_str, print_board
from .logic_numba import Board, action_size


class SplendorGame:
    """
    This class specifies the Splendor Game class.
    """

    def __init__(self, num_players=2):
        assert 2 <= num_players <= 4, 'Number of players should be either 2, 3, or 4.'
        self.num_players = num_players
        self.board = Board(num_players)

    def reset(self):
        self.board.init_game()

    def initial_state(self):
        """
        Returns: a representation of the board
        """
        self.board.init_game()
        return self.board.get_state()

    def next_player_of(self, player: int) -> int:
        """
        Returns: next player
        """
        return (player + 1) % self.num_players

    def next_state_of(self, board, player: int, action: int, deterministic=False):
        """
        Input:
            board: current board
            player: current player (0, 1, 2, 3)
            action: action taken by current player
            deterministic: False to apply "chance factor" (for real moves), True
                           for deterministic results (for MCTS exploration)

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        self.board.copy_state(board, True)
        next_player = self.board.make_move(action, player, deterministic)
        return self.board.get_state(), next_player

    def get_player_gems(self, board, player: int) -> List[int]:
        """
        Input:
            board: current board
            player: player for query (0, 1, 2, 3)
        Returns:
            List of integers denoting gems which the given player has.
            The order will be [White(Diamond), Blue(Sapphire), Green(Emerald), Red(Ruby), Black(Onyx), Jocker(Gold)]
        """
        self.board.copy_state(board, True)
        return self.board.players_gems[player][:6].tolist()

    def get_player_points(self, board, player: int) -> int:
        """
        Input:
            board: current board
            player: player for query (0, 1, 2, 3)
        Returns:
            Current score of the given player
        """
        self.board.copy_state(board, True)
        return self.board.get_score(player)

    def get_player_noble_counts(self, board, player: int) -> int:
        """
        Input:
            board: current board
            player: player for query (0, 1, 2, 3)
        Returns:
            Number of nobles who visited the given player
        """
        self.board.copy_state(board, True)
        nobles_count = 0
        for noble in range(self.board.num_nobles):
            noble_condition = self.board.players_nobles[self.board.num_nobles * player + noble]
            nobles_count += int(noble_condition.any())

        return nobles_count

    def get_player_cards(self, board, player: int) -> List[int]:
        """
        Input:
            board: current board
            player: player for query (0, 1, 2, 3)
        Returns:
            List of integers denoting cards & card points which the given player has.
            The order will be [White(Diamond), Blue(Sapphire), Green(Emerald), Red(Ruby), Black(Onyx), Dummy, Card Points]
        """
        self.board.copy_state(board, True)
        return self.board.players_cards[player].tolist()

    def get_gems_in_bank(self, board) -> List[int]:
        """
        Input:
            board: current board
        Returns:
            List of integers denoting gems in the bank.
            The order will be [White(Diamond), Blue(Sapphire), Green(Emerald), Red(Ruby), Black(Onyx), Jocker(Gold)]
        """
        self.board.copy_state(board, True)
        return self.board.bank[0][:6].tolist()

    def get_cards_with_tier(self, board, tier: int) -> List[dict]:
        """
        Input:
            board: current board
            tier: the index of tier for query (0, 1, 2)
        Returns:
            List of dictionaries (about cards on the given tier).
            Each dictionary has information about a card opened on the given tier.
            - 'cost' denotes cost of buying the specific card in terms of gems.
                The order will be [White(Diamond), Blue(Sapphire), Green(Emerald), Red(Ruby), Black(Onyx)]
            - 'earning' denotes the earned gems and points by buying this card.
                The order will be [White(Diamond), Blue(Sapphire), Green(Emerald), Red(Ruby), Black(Onyx), Dummy, Card Points]
        """
        self.board.copy_state(board, True)
        card_info = []
        for card in range(4):
            card_info.append({
                'cost': self.board.cards_tiers[8 * tier + 2 * card][:5].tolist(),
                'earning': self.board.cards_tiers[8 * tier + 2 * card + 1].tolist(),
            })

        return card_info

    def get_nobles_remaining(self, board) -> List[list]:
        """
        Input:
            board: current board
        Returns:
            List of lists (about nobles who don't visited any players yet).
            Each list has information about the time when nobles visit a player.
            The order will be [White(Diamond), Blue(Sapphire), Green(Emerald), Red(Ruby), Black(Onyx)]
        """
        self.board.copy_state(board, True)
        nobles_info = []
        for noble in range(self.board.num_nobles):
            noble_condition = self.board.nobles[noble][:5]
            if noble_condition.any():
                nobles_info.append(noble_condition.tolist())

        return nobles_info

    def get_reserved_cards(self, board, player) -> List[dict]:
        """
        Get the list of reserved card
        Input:
            board: current board
            player: current player object (i.e. Assignment instance)
        """
        self.board.copy_state(board, True)
        player = player.player_id
        card_info = []
        for card in range(3):
            card_info.append({
                'cost': self.board.players_reserved[6 * player + 2 * card][:5].tolist(),
                'earning': self.board.players_reserved[6 * player + 2 * card + 1].tolist(),
            })

        return card_info

    def retire_player(self, board, player):
        """
        Make a player retire. You can't use this inside your algorithm
        Input:
            board: current board
            player: current player object (i.e. Assignment instance)
        """
        self.board.copy_state(board, True)
        self.board.retire_player(player.player_id)
        return self.board.get_state()

    def valid_moves(self, board, player: int):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        self.board.copy_state(board, False)
        return self.board.valid_moves(player)

    def game_ended(self, board):
        """
        Input:
            board: current board

        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """
        self.board.copy_state(board, False)
        return self.board.check_end_game()

    def player_score(self, board, player: int) -> float:
        """
        Input:
            board: current board
            player: player you want to have score (may not be current player)

        Returns:
            score of such player
        """
        self.board.copy_state(board, False)
        return self.board.get_score(player)

    def number_of_turns_so_far(self, board) -> int:
        """
        Input:
            board: current board

        Returns:
            number of played rounds so far
        """
        self.board.copy_state(board, False)
        return self.board.get_round()

    def total_number_of_actions(self) -> int:
        """
        Returns: number of all possible actions
        """
        return action_size()

    def string_representation(self, board) -> str:
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        return board.tobytes()

    def move_as_string(self, move: int) -> str:
        """
        Input:
            move: int coding for an action

        Returns:
            string: a human representation of such move, as a printable string
        """
        return move_to_str(move)

    def print_board(self, numpy_board, players):
        """
        Input:
            numpy_board: a numpy representation of a board, may be different than self.board

        Print: a human representation of such board on stdout, used during pit involving a human
        """
        board = Board(self.num_players)
        board.copy_state(numpy_board, False)
        print_board(board, players)
