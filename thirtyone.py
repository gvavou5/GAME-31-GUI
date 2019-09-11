############################################################################
################################## GUI- Simple31 ##################################
############################################################################

############################################################################
################################## How Simple31 game works? ######################
############################################################################
'''
This implementation allows 2-8 players to play. Every player gets cards.
The one with the highest score (<=31) is the winner. If the score is more than 31 then the player is lost.
'''

import random
import PlayingCards as pc

class Player():
    def __init__(self, name, deck):
        self.name = name
        self.deck = deck
        self.score = 0
    def plays(self):
        card = self.deck.draw()
        print('Player {} got: {}'.format(self.name, card.detailed_info()))
        card_value = self._calculate_value(card)
        self.score += card_value
        self._check_if_exceeded()
        if self.score != -1:
            reply = input('The score is: {}. Play again? (n/y)'.format(self.score))
            if not reply or reply.lower() not in "οo":
                self.plays()
            else :
                print(self)
        else:
            print(self)
    def _check_if_exceeded(self):
        if self.score > 31:
            print('>31 ... {} :-('.format(self.name))
            self.score = -1
    def _calculate_value(self, card):
        if card.value.isdigit(): return int(card.value)
        elif card.value == 'A': return 1
        else: return 10
    def __str__(self):
        return 'Player '+self.name+' has:'+str(self.score)+' points'

class ComputerPlayer(Player):
    def plays(self):
        card = self.deck.draw()
        print('PC ({}) got: {}'.format(self.name, card.detailed_info()))
        card_value = self._calculate_value(card)
        self.score += card_value
        self._check_if_exceeded()
        if self._computer_strategy(): self.plays()
        else:
            print('PC:', self)
    def _computer_strategy(self):
        return False if self.score >= 25 or self.score == -1 else True

class Game():
    def __init__(self):
        print("We play the 31 game")
        self.n_players = self.number_of_players()
        self.players = []
        self.d = pc.Deck()
        self.d.shuffle()
        char = ord('A')
        for i in range(char, char+self.n_players):
            if chr(i) == 'A': self.players.append(ComputerPlayer(chr(i), self.d))
            else: self.players.append(Player(chr(i), self.d))
        self.show_players()
        self.play_game()
    def number_of_players(self):
        num = 0
        while num<2 or num>8 :
            reply = input('(2-8) Players')
            if reply.isdigit() and 2 <= int(reply) <= 8 :
                return int(reply)
    def play_game(self):
        for p in self.players:
            print(50*'*','\nPlayer ', p.name, ' now is playing')
            p.plays()
        self.show_winner()
    def show_winner(self):
        max_score = max(x.score for x in self.players)
        if max_score == -1: print("No winner")
        else:
            winners = [x for x in self.players if x.score == max_score]
            print(50*'*',"\nWinner: ")
            for player in winners:
                print( player)
    def show_players(self):
        print('Players: [', end ='')
        for player in sorted(self.players, key=lambda x: x.name):
            print(player.name, end = ',')
        print(']')

if __name__ == '__main__': Game()
