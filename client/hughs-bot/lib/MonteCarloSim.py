import argparse
import socket
import sys
import logging
from collections import OrderedDict
import math
import random
from card import Card
from deck import Deck
from evaluator import Evaluator

fulldeck = {"2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "Ts", "Js", "Qs", "Ks", "As", "2h", "3h", "4h", "5h", "6h", "7h", "8h", "9h", "Th", "Jh", "Qh", "Kh", "Ah", "2c", "3c", "4c", "5c", "6c", "7c", "8c", "9c", "Tc", "Jc", "Qc", "Kc", "Ac", "2d", "3d", "4d", "5d", "6d", "7d", "8d", "9d", "Td", "Jd", "Qd", "Kd", "Ad"}

"""
Author: Hugh Pearse
Calculate the win percentage given n random iterations, n players, with 2 hole cards and a board with 3,4 or 5 cards
"""
def calculate(iterations, numOpponents, hole, board):
    deck = eval(repr(fulldeck))
    for card in hole:
        deck.remove(card)
    for card in board:
        deck.remove(card)
    
    boardCopy = []
    for card in board:
        boardCopy.append(Card.new(card))
    
    holeCopy = []
    for card in hole:
        holeCopy.append(Card.new(card))
    
    wincount = 0
    
    #execute N monte carlo simulations
    for iter in range(0,iterations):
        deckCopy = eval(repr(deck))
        opponentsCards = []
        
        #randomly populate opponents holes
        for pl in range(0,numOpponents):
            #select 2 cards without replacement
            hc1 = random.choice(list(deckCopy))
            deckCopy.remove(hc1)
            hc2 = random.choice(list(deckCopy))
            deckCopy.remove(hc2)
            opphole = [Card.new(hc1), Card.new(hc2)]
            opponentsCards.append(opphole)
        
        #calculate my hand strength
        evaluator = Evaluator()
        myrank = evaluator.evaluate(boardCopy, holeCopy)
        myhs = 1.0 - evaluator.get_five_card_rank_percentage(myrank)
        
        win = True
        #calculate hand strength of each opponent and compare to my hand
        for opphole in opponentsCards:
            oprank = evaluator.evaluate(boardCopy, opphole)
            ophs = 1.0 - evaluator.get_five_card_rank_percentage(oprank)
            
            if ophs >= myhs:
                win = False
        
        if win == True:
            wincount += 1
    
    return float(wincount)/float(iterations)

if __name__ == '__main__':
    print calculate(100, 1, ['Ah', 'Ad'], ['Ts', '7s', '6s'])
