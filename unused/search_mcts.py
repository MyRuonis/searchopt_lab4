from numpy import random

from splendor.game import SplendorGame


class Node:
    def __init__(self, player: int, children: list):
        self.player = player
        self.valid_actions = children
        self.number_of_visits = [0 for _ in children]
        self.number_of_wins = [0 for _ in children]
        self.nodes_expanded = {}
        self.parent = None
        self.action = None

    def get_child_node(self, next_player, act):
        if act not in self.nodes_expanded:
            self.expand_node(act, Node(next_player, []))
        return self.nodes_expanded[act]

    def expand_node(self, action, node):
        assert action in self.valid_actions, f'{action} not in {self.valid_actions}'
        self.nodes_expanded[action] = node
        node.parent = self
        node.action = action

    def update(self, action, is_win):
        if action is not None:
            idx = self.valid_actions.index(action)
            self.number_of_visits[idx] += 1
            self.number_of_wins[idx] += int(is_win)

        if self.parent is not None:
            self.parent.update(self.action, is_win)

    def update_children(self, valid_moves):
        children = [a for a, v in enumerate(valid_moves) if v == 1]

        self.valid_actions = children
        self.number_of_visits = [0 for _ in children]
        self.number_of_wins = [0 for _ in children]

    def is_unexpanded_yet(self):
        return not self.nodes_expanded


class Assignment:
    def __init__(self, game: SplendorGame):
        self.game = game
        self.random = random.Generator(random.PCG64(27))
        self.node = None
        self.player_id = -1

    def __call__(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    def selection(self, board):
        # Exploration 50% Exploitation 50% (Note that this is not UCB-1)
        node = self.node
        ply = 0
        player = self.player_id
        while not node.is_unexpanded_yet() and ply < 10:
            if self.random.random() > 0.5:
                act, _ = max(zip(node.valid_actions, node.number_of_visits), key=lambda t: t[1])
                if act == 0:
                    break
            elif len(node.valid_actions):
                act = self.random.choice(node.valid_actions)
            else:
                break

            board, player = self.game.next_state_of(board, player, act)
            node = node.get_child_node(player, act)
            ply += 1

            if not node.valid_actions:
                node.update_children(self.game.valid_moves(board, player))

        return board, player, node

    def rollout(self, board, player) -> int:
        valids = [a for a, v in enumerate(self.game.valid_moves(board, player)) if v == 1]
        return self.random.choice(valids)

    def expand(self, board, player, node):
        while not self.game.game_ended(board).any():
            act = self.rollout(board, player)
            board, player = self.game.next_state_of(board, player, act)

        is_win = self.game.game_ended(board)[self.player_id] > 0
        node.update(None, is_win)

    def search(self, board) -> int:
        if self.node is None:
            self.node = Node(self.player_id, [])
        if not self.node.valid_actions:
            self.node.update_children(self.game.valid_moves(board, self.player_id))

        for _ in range(1000):
            selection_board, selection_player, node = self.selection(board)
            self.expand(selection_board, selection_player, node)

        # Choose the most frequently visited path for this node
        act, _ = max(zip(self.node.valid_actions, self.node.number_of_visits), key=lambda t: t[1])
        return act

    def collect_action_done(self, board, player, action):
        assert self.node.player == player, f'{self.node.player} vs {player}'

        next_player = self.game.next_player_of(player)
        self.node = self.node.get_child_node(next_player, action)

        if not self.node.valid_actions:
            self.node.update_children(self.game.valid_moves(board, next_player))
