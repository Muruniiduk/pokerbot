
# coding: utf-8

# In[29]:


from Equity import equity, get_hand_range, filter_known, compare
from deuces import Card, Evaluator, Deck
from itertools import combinations, permutations
import numpy as np
import pandas as pd
import copy
import operator


# In[30]:


deck = Deck()
board = deck.draw(5)


# In[31]:


# Jupyter examples on this specific board
board = []
for card_str in ['Ks', '7h', 'As', '6c', '9h']:
    board += [Card.new(card_str)]
Card.print_pretty_cards(board)


# # Very simple situation
# 
# Let us assume a river, where the effective SPR (stack-to-pot ratio) is 1. The possible betting size for hero is 0.5. Villain can only shove (bet 1). Hero is out of position (OOP).
# 
# Can the NN be as simple as:
# - input: hand's percentile rank vs own range and rank vs opponent's perceivied range
# - output: 1 node for each decision (x/f, x/c, b/f, b/c)
# 
# Opponent can only shove.
# - (x, c, b)
# 
# Dumb bot to train against - defending (call+bet freq) frequency is such that bluffing any two against it wouldn't be profitable.
# 
# If bot calls and wins, it win's 1+bet, if not, then loses bet. If we bet 100% of the time with it's own range then it needs to call top bet/(1+bet) of the hands. It will bet the best third of calling hands.

# In[32]:


crange = filter_known(board, get_hand_range("AQ+, 99+, ATs+, Ah2h, Ah3h, Ah4h, Ah5h, Ah6h, Ah7h, Ah8h, Ah9h"))


# In[33]:


# dumb bot strategy
def getAction(board, betSize, myRange, myHand):
    hand2eq = dict()
    for hand in myRange: hand2eq[str(hand)] = equity(list([hand]), myRange, board) #remember the equity vs range
    sorted_hands = [hand for hand,x in sorted(hand2eq.items(), key=operator.itemgetter(1))] #sort cards by equity
    freq = betSize/(1+betSize) #defending frequency s.t. bluffing 100% w/ same range wouldn't be profitable
    hands = len(sorted_hands)
    calling_hands = sorted_hands[int((1-2*freq/3.0)*hands):int((1-freq/3.0)*hands)] #bottom 2/3 of defending freq
    betting_hands = sorted_hands[int((1-freq/3.0)*hands):] #top 1/3 of defending freq
    if str(myHand) in betting_hands:
        return "bet"
    if str(myHand) in calling_hands:
        return "call"
    return "fold"


# In[34]:


Card.print_pretty_cards(crange[20])
getAction(board, 0.5, crange, crange[58])


# In[35]:


def getPercentileRank(board, handRange, pHand):
    hand2eq = dict()
    for hand in handRange: hand2eq[str(hand)] = equity(list([hand]), handRange, board)
    sorted_hands = [hand for hand,x in sorted(hand2eq.items(), key=operator.itemgetter(1))]
    return sorted_hands.index(str(pHand))/len(sorted_hands)


# In[36]:


a = getPercentileRank(board, crange, crange[20])
hand = crange[0]
a


# ## Reward function
# assumes lines to be legal

# In[37]:


heroLines = ['x/f', 'x/c', 'b/f', 'b/c'] # /action means when villain bets
villainLines = ['xx', 'xb', 'bf','bc', 'bb'] #first char is hero's action
def rewards(heroLine, heroHand, villainLine, villainHand, board):
    hAction1, hAction2 = heroLine.split('/')
    vAction = villainLine[1]
    hIsWinner = True if compare(heroHand, villainHand, board) == -1 else False
    if vAction == 'f': return (1.0,0)
    if vAction == 'x': return (1 * hIsWinner, 1 * (1-hIsWinner) )
    if vAction == 'c': return (2,-0.5) if hIsWinner else (-0.5,2)  #since bet is 0.5 then pot is 2
    #below is eff. else: villain bets
    if hAction1 == 'x' and hAction2 == 'f': return (0,1)
    if hAction1 == 'b' and hAction2 == 'f': return (-0.5,1.5)
    if hAction1 == 'x' and hAction2 == 'c': return (3,-1) if hIsWinner else (-1,3)
    if hAction1 == 'b' and hAction2 == 'c': return (3,-1) if hIsWinner else (-1,3)
    return "error in rewards method"


# In[38]:


def getPossible(lines, hAction): return list(filter(lambda line: line[0]==hAction, lines))
list(map(lambda line: line[1], getPossible(villainLines, 'x')))
#vLines = list(filter(lambda line: line[0]==hAction1, villainLines)) #filter out where line is legal
#vActions = list(map(lambda line: line[1], vLines)) #get V actions


# In[39]:


Card.print_pretty_cards(crange[0])
Card.print_pretty_cards(crange[5])
Card.print_pretty_cards(board)


# In[40]:


#If AcKc is hero for tree hero x, villain b, hero c
rewards('x/c', crange[0], 'xb', crange[5], board)


# In[41]:


#If sAcQh is hero for tree hero x, villain b, hero c
rewards('x/c', crange[5], 'xb', crange[0], board)


# # Creating dataset
# 
# Same range for villain for all boards, same for hero

# In[55]:


bets = 3.5+8+21.833 #hero calls from SB 3.5, BB folds, Villain is In Position (IP)
pot = 2 * bets
stack = 100 - bets
print(pot, stack) #SPR = 1


# In[69]:


hrange = get_hand_range("AJ+, 66, 77, 88, 99, TT, JJ, A2s+, 98s, T9s, JTs, KQs")
vrange = get_hand_range("A9+, 22+, KQ, JQ, TJ, A2s+, 98s, T9s, JTs, KQs")
print(len(hrange), len(vrange))


# In[89]:


deck = Deck()
board = deck.draw(5)


# In[91]:


a = pd.DataFrame()
a['h_hand'] = [Card.print_pretty_cards(hrange[0])]
a['v_hand'] = [Card.print_pretty_cards(vrange[0])]
a['h_perc'] = [getPercentileRank(board, hrange, hrange[0])]
a['v_perc'] = [getPercentileRank(board, vrange, hrange[0])]
a


# In[94]:


import sys
sys.path
get_ipython().system('jupyter kernelspec list')


# # Goal
# 
# If our bot learns to play game theory optimal, we can expect to see couple of things:
# - it knows that you should bluff with worst hands with no equity
# - it knows to protect it's checking range (checks couple of good hands)

# **First idea.** Functional keras. 2 NN-s. 1 output is first action and 2nd is final action. 2nd NN gets same inputs as 1st but also output of the 1st. E.g. > 0.5 for the first is bet, for the second is call. How to implement reward or loss? Can reward-3 be considered as loss?
