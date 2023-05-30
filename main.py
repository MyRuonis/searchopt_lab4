from collections import Counter, defaultdict

from tqdm import trange

from search.load import get_student_assignments
from splendor.arena import Arena
from splendor.game import SplendorGame
from math import isnan

TRIALS = 12

if __name__ == "__main__":
    players = get_student_assignments()

    # Query 1. League or Tournament
    competition_type = ''
    while not competition_type:
        print('Which kind of competition will you use?\n'
              '   [1] League type (2 player)\n'
              '   [2] Tournament (2 player)\n'
              '   [3] Tournament (3 player)\n'
              '   [4] Tournament (4 player)\n'
              '   [5] 1:1 match with human\n'
              '   [6] human vs human')
        competition_type = input('Choose: ').strip()

        if competition_type not in '123456':
            print(f'Input "{competition_type}" is invalid!')
            competition_type = ''

    # Query 2. Display
    display_type = '1' if competition_type in '56' else ''
    while not display_type:
        print('Do you want to display moves?\n'
              '   [1] Always\n'
              '   [2] Only for the first trial\n'
              '   [3] Never')
        display_type = input('Choose: ').strip()

        if display_type not in '123':
            print(f'Input "{display_type}" is invalid!')
            display_type = ''

    seconds = 5
    if display_type in '12':
        seconds = input('How many seconds will you need to read moves for each turn (default: 5 sec)?').strip()
        seconds = float(seconds)
        if isnan(seconds):
            seconds = 5
        else:
            seconds = max(int(seconds), 1)
        print(f"For each turn, the display will wait for {seconds} second(s).")

    # Generate match
    match_events = []
    n_players = 2
    if competition_type == '1':
        from itertools import combinations

        match_events = [(a, b) for a, b in combinations(players, r=2)]
    elif competition_type in '234':
        n_players = int(competition_type)
        match_events = []
        for i in range(0, len(players), n_players):
            group = players[i:i + n_players]
            if len(group) < n_players:
                group += players[0:n_players - len(group)]
            match_events.append(tuple(group))
    elif competition_type == '5':
        match_events = [(a, 'human') for a in players]
    else:
        match_events = [('human1', 'human2')]

    # Initialize game
    game = SplendorGame(n_players)

    winning_log = defaultdict(list)
    for match in match_events:
        arena = Arena(game, *match)

        counter = Counter()
        for trial in trange(TRIALS, desc=' vs '.join(match)):
            # Reset the game
            game.reset()
            arena.rotate_players()

            display = (display_type == '1') or (trial == 0 and display_type == '2') or ('human' in match)
            counter.update(arena.play(verbose=display, wait=seconds))

        print()
        print('-' * 80)
        for p, c in sorted(counter.items(), key=lambda t: t[1], reverse=True):
            print(f'Winning rate of {p:10s} = {c / TRIALS * 100:6.2f}%')
        print('-' * 80)

        if competition_type in '234':
            # Print the winners
            max_value = max(counter.values())
            winners = [p for p, c in counter.items() if c == max_value]
            winning_log[match] = tuple(winners)
            print(f'The winner of {" vs ".join(match)} is {" & ".join(winners)}!')
        else:
            # Accumulate the winning rate
            for p, c in counter.items():
                winning_log[p].append(c)

    print()
    print('=' * 80)
    print('FINAL RESULT')
    print('-' * 80)

    for key, items in sorted(winning_log.items(), key=lambda t: t[1], reverse=True):
        if competition_type in '234':
            print(f'Winner of {" vs ".join(key):40s} is {" & ".join(items)}.')
        else:
            c = sum(items) / (TRIALS * len(items))
            print(f'Winning rate of {key:10s} = {c * 100:6.2f}%')
