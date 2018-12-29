#!/home/erik/anaconda3/bin/python
#-*- coding: utf-8 -*-

from deuces import Card, Evaluator, Deck

deck = Deck()
evaluator = Evaluator()
board = deck.draw(3)
hand1 = deck.draw(2)
hand2 = deck.draw(2)

score1 = evaluator.evaluate(board, hand1)
score2 = evaluator.evaluate(board, hand2)

# print('Player 1', Card.print_pretty_cards(hand1), score1)
# print("Player 2", Card.print_pretty_cards(hand2), score2)
Card.print_pretty_cards(deck.draw(3))
