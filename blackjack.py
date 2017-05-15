"""
Welcome to the exciting world of text-based BlackJack!
Step right up and test your luck!!
To play, run this file in your console using 'python blackjack.py'
"""
import random

class Deck(object):
    #point values dict (note ace can be 1 or 11, see card_values function)
    card_values = { 'A': 11, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9,'10':10, 'J':10, 'Q':10, 'K':10 }

    def __init__(self):
        self.unused_cards = []

    def shuffle(self):
        """
        Resets the deck
        """
        self.unused_cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4
        random.shuffle(self.unused_cards)

    def draw_card(self):
        """
        Draws a card from the top of the deck
        Places that card in the used card list
        Shuffles the deck if there are no more unused cards
        """

        if (len(self.unused_cards) == 0):
            print('Dealer had to shuffle the deck')
            self.shuffle()
        num_unused = len(self.unused_cards)
        card = self.unused_cards.pop(0)
        return card

    def print_unused_cards(self):
        print(self.unused_cards)


class Hand(object):
    def __init__(self):
        self.cards = []
        self.value = 0
        self.has_ace = False

    def __len__(self):
        return len(self.cards)

    def print_hand(self, starting_card = 0):
        """
        Prints the hand, skipping first card if hidden
        """
        #TODO list comp to print cards in this hand
        hand = []
        for card in range(starting_card, len(self.cards)):
            hand.append(self.cards[card])
        print(hand)
        if starting_card == 1:
            print('plus one face-down card')

    def add_card(self, card):
        """
        Adds card to hand, recalculates value and returns numerical value
        """
        self.cards.append(card)
        if card == 'A':
            has_ace = True
        self.value = self.calc_value()
        return self.value

    def is_blackjack(self):
        """
        Returns true if hand contains a blackjack (ace plus 10)
        """
        if len(self.cards) > 2 or self.value > 21:
            return False

        #keep track cards value
        total = 0
        for card in self.cards:
            if self.get_card_value(card) >= 10:
                total += self.get_card_value(card)

        if total == 21:
            return True
        else:
            return False

    def calc_value(self):
        """
        Returns the hand's numerical value
        If there is an ace in the hand, it is treated as 11 unless the hand
        busts, then it is treated as a 1
        """
        total = 0
        has_ace = 0
        for card in self.cards:
            total += self.get_card_value(card)
            if card == 'A':
                has_ace = 1
        #check to see if you would bust due to Ace in that case recalc with ace value = 1
        if has_ace and total > 21:
            total = total - 10

        return total

    def get_card_value(self, card):
        """
        Returns card's numerical value (11 for ace) based on card_val dict in Deck
        """
        return Deck.card_values[card]

    def discard_hand(self):
        """
        Discards and entire hand
        """
        while len(self.cards):
            self.discard(self.cards[0])

    def discard(self, card):
        """
        Discards the card into the used pile
        Also removes from hand
        """
        self.cards.remove(card)

class Game(object):
    """
    Tracks game variables including player input, wallet and winning/losing scenarios
    """
    def __init__(self):
        self.deck = Deck()
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.current_bet = 0
        self.start_new_game(self.deck)

    def start_new_game(self, deck):
        """
        Starts a new game by entering the play loop
        """
        print ('Welcome to PyBlackjack!')
        game_on = True
        self.deck.shuffle()

        #play/replay loop
        while True:
            #main game loop
            self.init_wallet()

            while self.wallet > 0 and game_on:
                #ask player how much they would like to bet
                self.current_bet = self.get_player_input('bet')
                self.TEST_deal_first_hand(self.deck)

                #check for blackjack on the first hand
                if self.dealer_hand.is_blackjack() or self.player_hand.is_blackjack():
                    winner = self.calculate_winner(self.player_hand, self.dealer_hand)
                    print('%s is the winner!' %(winner))

                move = ' '

                #ask player what they would like to do (hit or stand)
                while move != 's':
                    if self.is_bust(self.player_hand) or self.is_bust(self.dealer_hand):
                        break

                    if self.player_hand.is_blackjack() or self.dealer_hand.is_blackjack():
                        print('Blackjack!')
                        break

                    move = str.lower(self.get_player_input('move'))

                    if move == 'h':
                        print('You hit')
                        self.hit(self.player_hand)
                    else:
                        print('You stand')
                        break

                self.end_of_turn()

            if not self.replay():
                game_on = False
                print('Thanks for playing!')
                break

    def end_of_turn(self):
        self.dealer_move(self.dealer_hand)
        print('Your hand:')
        self.player_hand.print_hand()
        print('Dealers hand:')
        self.dealer_hand.print_hand()
        winner = self.calculate_winner(self.player_hand, self.dealer_hand)
        if winner == 'Bust':
            print('Bust!')
        else:
            print('%s is the winner!' %(winner))
        self.adjust_wallet(self.current_bet, winner)
        self.discard_hands()
        self.print_wallet()

    def init_wallet(self):
        self.wallet = 100

    def replay(self):
        replay = ''
        while replay not in ('y', 'Y', 'n', 'N'):
            replay = input('Would you like to play again? (enter y or n) ')

            if replay == 'y' or replay == 'Y':
                return True
            else:
                return False

    def dealer_move(self, hand):
        print('Dealer decides his move')
        while hand.value <= 16:
            print('Dealer hits')
            self.hit(hand)
        else:
            print('Dealer stands')

    def is_bust(self, hand):
        '''
        Returns true if hand is over 21
        '''
        if hand.value > 21:
            return True
        else:
            return False

    def adjust_wallet(self, current_bet, winner):
        """
        Adjusts the wallet based on whether player won or lost and their current bet
        """
        if winner == 'Player':
            self.increase_wallet(current_bet*2)
        else:
            self.decrease_wallet(current_bet)

    def print_wallet(self):
        """
        Prints out current amount in wallet
        """
        print('Current wallet amount is $%s' %(self.wallet))

    def calculate_winner(self, player_hand, dealer_hand):
        '''
        Returns False if no winner
        Returns player or dealer if one is a winner
        '''
        player_hand_value = player_hand.value
        dealer_hand_value = dealer_hand.value
        print('Player hand value: %s' %(player_hand_value))
        print('Dealer hand value: %s' %(dealer_hand_value))

        #did both player and dealer go bust?
        if self.is_bust(player_hand) and self.is_bust(dealer_hand):
            return 'Bust'

        #did dealer go bust?
        if self.is_bust(dealer_hand):
            return 'Player'

        #did player go bust?
        if self.is_bust(player_hand):
            return 'Dealer'

        #is player or dealer hand a blackjack?
        if dealer_hand.is_blackjack():
            return 'Dealer'

        if player_hand.is_blackjack():
            return 'Player'

        if dealer_hand_value >= player_hand_value:
            return 'Dealer'
        else:
            return 'Player'

    def discard_hands(self):
        """
        Discards all hands (player and dealer)
        """
        self.player_hand.discard_hand()
        self.dealer_hand.discard_hand()

    def deal_first_hand(self, deck):
        """
        Deals the first hand
        """
        print('Dealer deals the first hand')
        self.player_hand.add_card(deck.draw_card())
        self.dealer_hand.add_card(deck.draw_card())
        self.player_hand.add_card(deck.draw_card())
        self.dealer_hand.add_card(deck.draw_card())
        print('Your hand:')
        self.player_hand.print_hand(0)
        print('Dealers Hand:')
        self.dealer_hand.print_hand(1)

    def hit(self, hand):
        """
        A card is pulled into the hand. Steps:
        - check for blackjack (win)
        - check for over 21 (bust)
        """
        hand.add_card(self.deck.draw_card())
        hand.print_hand()

    def get_player_input(self, type):
        if type == 'bet':
            player_bet = ' '
            while True:
                player_bet = input('Enter the amount you would like to bet between 1 and %s: ' %(self.wallet))
                if self.is_valid_bet(player_bet):
                    return int(player_bet)
                    break
        elif type == 'move':
            player_move = ' '
            while True:
                player_move = input('Would you like to Hit (h) or Stand (s)? ')
                if self.is_valid_move(player_move):
                    return player_move
                    break

    def is_valid_move(self, move):
        if move in 'h s H S'.split():
            return True
        else:
            return False

    def is_valid_bet(self, bet):
        try:
            bet = int(bet)
            if bet <= self.wallet and bet > 0:
                return True
            else:
                return False
        except:
            print('Please enter a number between 1 and %s' %(self.wallet))
            return False

    def increase_wallet(self, amount):
        self.wallet += amount

    def decrease_wallet(self, amount):
        self.wallet -= amount

    def TEST_deal_first_hand(self, deck):
        """
        Various tests to test the winning calc function
        Uncomment the desired test and change deal_first_hand() in game loop
        to TEST_deal_first_hand(). Stand when given the option during gameplay
        """
        print('Dealer deals test hand (player has blackjack)')

        #test for player blackjack
        '''
        self.player_hand.add_card('A')
        self.dealer_hand.add_card(deck.draw_card())
        self.player_hand.add_card('K')
        self.dealer_hand.add_card(deck.draw_card())
        '''
        #test for dealer blackjack
        '''
        self.player_hand.add_card(deck.draw_card())
        self.dealer_hand.add_card('A')
        self.player_hand.add_card(deck.draw_card())
        self.dealer_hand.add_card('K')
        '''

        #test for both have blackjack
        '''
        self.player_hand.add_card('10')
        self.dealer_hand.add_card('A')
        self.player_hand.add_card('A')
        self.dealer_hand.add_card('K')
        '''

        #test for both bust
        '''
        self.player_hand.add_card('10')
        self.player_hand.add_card('10')
        self.player_hand.add_card('4')
        self.dealer_hand.add_card('4')
        self.dealer_hand.add_card('K')
        self.dealer_hand.add_card('K')
        '''

        #test for player bust
        '''
        self.player_hand.add_card('10')
        self.player_hand.add_card('10')
        self.player_hand.add_card('4')
        self.dealer_hand.add_card('4')
        self.dealer_hand.add_card('K')
        '''
        #test for dealer bust
        '''
        self.player_hand.add_card('10')
        self.player_hand.add_card('2')
        self.player_hand.add_card('4')
        self.dealer_hand.add_card('4')
        self.dealer_hand.add_card('K')
        self.dealer_hand.add_card('K')
        '''
        #test for tie
        '''
        self.player_hand.add_card('10')
        self.player_hand.add_card('8')
        self.dealer_hand.add_card('10')
        self.dealer_hand.add_card('8')
        '''

        #test for player wins
        '''
        self.player_hand.add_card('10')
        self.player_hand.add_card('K')
        self.dealer_hand.add_card('10')
        self.dealer_hand.add_card('8')
        '''

        #test for dealer wins
        '''
        self.player_hand.add_card('2')
        self.player_hand.add_card('2')
        self.dealer_hand.add_card('10')
        self.dealer_hand.add_card('8')
        '''

        print('TEST Your hand:')
        self.player_hand.print_hand()
        print('TEST Dealers hand:')
        self.dealer_hand.print_hand()

#begins the game by initializing the Game object
game = Game()
