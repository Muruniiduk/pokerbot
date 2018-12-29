# coding: utf-8
# @author Jaan Erik Pihel

from deuces import Card, Evaluator, Deck
from itertools import combinations, permutations
import numpy as np
import pandas as pd
import copy

# get_ipython().system('python --version')
# import sys
# sys.version
# get_ipython().system('python --version')

# ## Calculating turn equity for 2 given hands
# deck = Deck()
evaluator = Evaluator()
# board = deck.draw(4)
# hand1 = deck.draw(2)
# hand2 = deck.draw(2)
# Card.print_pretty_cards(hand1)
# Card.print_pretty_cards(hand2)
# Card.print_pretty_cards(board)

def draw(deck, card):
    deck.cards.remove(Card.new(card))
    return Card.new(card)

def draw_hand(deck, card1, card2): return [draw(deck, card1), draw(deck, card2)]

def compare(hand1, hand2, board):
    e1 = evaluator.evaluate(board, hand1)
    e2 = evaluator.evaluate(board, hand2)
#     print('For')
#     Card.print_pretty_cards(hand1)
#     Card.print_pretty_cards(hand2)
#     Card.print_pretty_cards(board)
#     print("results ", e1, e2)
    if e1 < e2: return -1
    if e1 > e2: return 1
    return 0

# def equity(hand1,hand2,board):
#     windrawlose = [0,0,0]
#     for card in deck.cards:
#         result = compare(hand1,hand2,board+[card])
#         windrawlose[result+1] += 1
#     if (windrawlose[2] == 0): return 1
#     return np.round(windrawlose[0]/(windrawlose[0]+windrawlose[2]),decimals=3)

# Card.print_pretty_cards(hand1)
# Card.print_pretty_cards(hand2)
# Card.print_pretty_cards(board)
# equity(hand1,hand2,board)

# ## Calculating river equity for 1 known hand vs any2
# deck = Deck()
# board = deck.draw(5)
# hand1 = draw_hand(deck, "As", "Ac")
# Card.print_pretty_cards(board)
# def equity(hand1, board):
#     windrawlose = [0,0,0]
#     for hand2 in combinations(deck.cards, 2):
#         hand2 = list(hand2)
#         result = compare(hand1, hand2, board)
#         windrawlose[result+1] += 1
#     if (windrawlose[2] == 0): return 1
#     return np.round(windrawlose[0]/(windrawlose[0]+windrawlose[2]),decimals=3)

# ## Hand ranges

# Method for creating a list (or set) of hands that satisfy a given string. For QQ+ it returns \[QQ,KK,AA\] with all suits. This can be slow, because it will be given from user only once, I think?
#
# Example: "22+, AQ+,ATs+,KJs+"
#
# Formula:
#
# - If are same, then + means that pocket pair or higher.
# - If different, then first card remains same, second will rise.
# - If s is at the end, then must be same suit.
def uniq(lst):
    last = object()
    for item in lst:
        if item == last:
            continue
        yield item
        last = item

def sort_and_deduplicate(l):
    return list(uniq(sorted(l, reverse=True)))

def get_hand_range(range_string):
    """Expect correct syntax"""
    order = ["2","3","4","5","6","7","8","9","T","J","Q","K","A"]
    suits = ['s','h','d','c']
    res_range = list() #RESULT
    condition_list = range_string.replace(' ','').split(',')
    for condition in condition_list:
        fst = condition[0]
        snd = condition[1]

        if fst==snd and '+' in condition: #"""Pockets"""
            for i in range(order.index(fst),len(order)):
                for suit_pair in combinations(suits,2): #matters not, which card is which suit
                    res_range += [[Card.new(order[i]+suit_pair[0]),Card.new(order[i]+suit_pair[1])]]
        elif 's' in condition and '+' in condition and len(condition)==4: #"""Suits and +"""
            for i in range(order.index(snd),order.index(fst)):
                for suit in suits:
                    res_range += [[Card.new(fst+suit),Card.new(order[i]+suit)]]
        elif '+' in condition and len(condition)==3: #"""Only +"""
            for i in range(order.index(snd),order.index(fst)):
                for suit_pair in permutations(suits,2): #doesn't consider suitedness luckily
                    res_range += [[Card.new(fst+suit_pair[0]),Card.new(order[i]+suit_pair[1])]]
        elif 's' in condition and len(condition)==3: #"""Only s"""
            for suit in suits:
                res_range += [[Card.new(fst+suit),Card.new(snd+suit)]]
        elif len(condition)==4: #"""With given suits"""
            res_range += [[Card.new(condition[:2]),Card.new(condition[2:])]]
        else: #"""Given combo with any nonsuits"""
            for suit_pair in permutations(suits,2):
                res_range += [[Card.new(fst+suit_pair[0]),Card.new(order[i]+suit_pair[1])]]
    return sort_and_deduplicate(res_range)

# r = get_hand_range("32+")
# for hand in r:
#     Card.print_pretty_cards(hand)

def filter_known(allknown, hand_range):
    res = list()
    for hand in hand_range:
        if not (hand[0] in allknown or hand[1] in allknown): res += [hand]
    return res

# r = get_hand_range("AA+")
# print(len(r))
# r = filter_known([Card.new("As")],r)
# print('After removing one\n', len(r))

# ## Equity for one known hand vs range
# deck = Deck()
# board = deck.draw(5)
# hand1 = draw_hand(deck, "Js", "Jc")
# def equity(hand1, board, range_string):
#     windrawlose = [0,0,0]
#     for hand2 in filter_known(board+hand1, get_hand_range(range_string)):
#         result = compare(hand1, hand2, board)
#         windrawlose[result+1] += 1
#     if (windrawlose[2] == 0): return 1
#     return np.round(windrawlose[0]/(windrawlose[0]+windrawlose[2]),decimals=3)
#
# Card.print_pretty_cards(hand1)
# Card.print_pretty_cards(board)
# equity(hand1,board, "88+")

# ## Equity for range vs range
# deck = Deck()
# board = deck.draw(5)
# def equity(range1, range2, board):
#     windrawlose = [0,0,0]
#     for hand1 in get_hand_range(range1):
#         for hand2 in filter_known(board+hand1, get_hand_range(range2)):
#             result = compare(hand1, hand2, board)
#             windrawlose[result+1] += 1
#     if (windrawlose[2] == 0): return 1
#     return np.round(windrawlose[0]/(windrawlose[0]+windrawlose[2]),decimals=3)

def equity(range1, range2, board):
    windrawlose = [0,0,0]
    for hand1 in range1:
        for hand2 in filter_known(board+hand1, range2):
            result = compare(hand1, hand2, board)
            windrawlose[result+1] += 1
    if (windrawlose[2] == 0): return 1
    return np.round(windrawlose[0]/(windrawlose[0]+windrawlose[2]),decimals=3)
