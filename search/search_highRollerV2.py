from numpy import random

from splendor.game import SplendorGame


class Assignment:
    def __init__(self, game: SplendorGame):
        self.game = game
        self.random = random.Generator(random.PCG64(27))
        self.player_id = -1

        ## to be changed for 3,4 players
        self.bank_max = [4, 4, 4, 4, 4, 4]
        self.myBonus = [0, 0, 0, 0, 0]

    def __call__(self, *args, **kwargs):
        return self.search(*args, **kwargs)

    def search(self, board) -> int:
        """
        This function do adversarial searching using the given game board.
        You can access the states in the board using functions in self.game, such as:
            -
        """
        
        """
            Strategy algorithm
            High Roller:
                - Go for cards that have the least required moves to get

            To add:
                - If someone will quicker reach the best card, go for the 2nd
                - Optimal gem collecting
                - Golden token recognition
                - Reserving good cards
                - Pick all possible gems :)
                - Update ## to be changed for 3,4 players
        """

        # Get all possible cards
        cards = []
        for i in range(3):
            cards = cards + self.game.get_cards_with_tier(board, i)

        # Assign ratios
        for card in cards:
            card['ratio'] = self.ratio(board, card)

        # Debugging
        #f = open("logs.txt", "a")
        #for card in cards:
            #f.write("{0}\n".format(card['ratio']))
        #f.write("\n")
        #f.close()

        # Find the highest ratio card
        myCardID = 0
        for i in range(1, len(cards)):
            if cards[i]['ratio'] < cards[myCardID]['ratio']:
                myCardID = i
        
        neededGems = [i for i in cards[myCardID]['cost']]
        myGems = self.game.get_player_gems(board, self.player_id)
        for i in range(len(neededGems)):
            neededGems[i] -= (myGems[i] + self.myBonus[i])

        buy = neededGems[0] <= 0 and neededGems[1] <= 0 and neededGems[2] <= 0 and neededGems[3] <= 0 and neededGems[4] <= 0
        if buy:
            for i in range(5):
                self.myBonus[i] += cards[myCardID]['earning'][i]
            return myCardID
        else:
            #valids = [a for a, v in enumerate(self.game.valid_moves(board, self.player_id)) if v == 1]
            ## Best move is to get 3 different ones
            #valids = filter(lambda number: number >= 30, valids)

            gemsToPick = self.game.get_gems_in_bank(board)
            picking = 0
            for i in range(len(neededGems)):
                if neededGems[i] > 0 and gemsToPick[i] > 0:
                    picking += 1

            if picking >= 3:
                # Will get the 3 most gem requiring types and sort them by order White .. smt .. smt
                ids = [0, 1, 2, 3, 4]
                buy = sorted(zip(neededGems, ids), reverse=True)[:3]
                buy = sorted(buy, key=lambda tup: tup[1])

                if buy[0][1] == 0: # Starts with 1 white
                    if buy[1][1] == 1: # If 2nd is blue
                        return 45 + buy[2][1] - 2
                    elif buy[1][1] == 2: # If 2nd is green
                        return 45 + buy[2][1] - 3
                    else: # If 2nd is red
                        return 50
                elif buy[0][1] == 1: # Starts with 1 blue
                    if buy[1][1] == 2:
                        return 51 + buy[2][1] - 3
                    else:
                        return 53
                else: # Red Green Grey
                    return 54
            elif picking == 2:
                first = -1
                for i in range(len(neededGems)):
                    if neededGems[i] > 0 and gemsToPick[i] > 0:
                        first = i
                        break
                
                move = 35
                if first == 1:
                    move = 39
                elif first == 2:
                    move = 42
                elif first == 3:
                    move = 44

                for i in range(i + 1, len(neededGems)):
                    if neededGems[i] > 0 and gemsToPick[i] > 0:
                        move += i - first - 1
                        return move
            elif picking == 1: ## If only 1 type available buy 1 or 2 of it depending on how much is needed
                bank = self.game.get_gems_in_bank(board)
                for i in range(len(neededGems)):
                    if neededGems[i] > 0 and gemsToPick[i] > 0:
                        if neededGems[i] > 1 and bank[i] >= 4:
                            return i + 55
                        else:
                            return i + 30
            else: # if cant pick any gems that are needed, just wait
                return 60

        return 60

    def collect_action_done(self, board, player, action):
        a = 5
        #raise NotImplementedError()

    def ratio(self, board, card):
        bank = self.game.get_gems_in_bank(board)
        myGems = self.game.get_player_gems(board, self.player_id)

        turns = 1 # for buying the card
        prestige = card['earning'][6]

        # Deep copy to not mess up the initial values
        values = [i for i in card['cost']]

        total = 0
        for i in range(len(values)):
            total += values[i]
            if values[i] > bank[i] + myGems[i] + self.myBonus[i]:
                return float('inf')
        if total > 10:
            return float('inf')

        for i in range(len(values)):
            values[i] -= (myGems[i] + self.myBonus[i])

        values.sort(reverse=True) # 4 3 2 1 0
        done = False
        while not done:
            # if all prices are 0 done
            if values[0] <= 0:
                done = True
                break
            
            # if only 1 price left then count how many turns it takes by taking 1 gem at a time
            if values[1] <= 0:
                turns += values[0]
                done = True
                break
            
            # if more than 1 price left, take 3 per turn from most gem required spots
            turns += 1
            for j in range(3):
                values[j] -= 1

            # resort the order
            values.sort(reverse=True)

        return turns
            
            
