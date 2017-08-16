import argparse
import socket
import sys
import logging
from collections import OrderedDict
import math

"""
Author: Hugh Pearse
"""

def calculate(hole):
    rank = OrderedDict(( ('2',1.0), ('3',1.5), ('4',2), ('5',2.5), ('6',3), ('7',3.5), ('8',4.0), ('9',4.5), ('T',5.0), ('J',6.0), ('Q',7.0), ('K',8.0), ('A',10.0) ))
    cardANumeral = list(hole[0])[0]
    cardASuit = list(hole[0])[1]
    cardBNumeral = list(hole[1])[0]
    cardBSuit = list(hole[1])[1]
    
    score = 0.0
    #pair
    if cardANumeral == cardBNumeral:
        score = rank[cardANumeral] * 2.0
        if score < 5.0:
            score = 5.0
        if cardANumeral == '5':
            score = score + 1.0
    #distinct
    else:
        if rank[cardANumeral] > rank[cardBNumeral]:
            score = rank[cardANumeral]
        else:
            score = rank[cardBNumeral]
    
    #suits
    if cardASuit == cardBSuit:
        score = score + 2.0
    
    gap = math.fabs(rank.keys().index(cardANumeral) - rank.keys().index(cardBNumeral)) - 1 
    
    #gap penalty
    if gap == 1:
        score = score - 1.0
    elif gap == 2:
        score = score - 2.0
    elif gap == 3:
        score = score - 4.0
    elif gap > 3:
        score = score - 5.0
    
    #connector bonus
    if (gap == 0 or gap == 1) and (rank.keys().index(cardANumeral) < 10 and rank.keys().index(cardBNumeral) < 10):
        score = score + 1.0
    
    #round off score
    return score

if __name__ == '__main__':
    print calculate(['Ah', 'Ad'])# 20 points 
    print calculate(['9s', '8s'])# 7.5 points
    print calculate(['Ks', '9s'])# 6 points
    print ""
    print calculate(['As', 'Ks'])# 12 points
    print calculate(['Th', 'Td'])# 10 points 
    print calculate(['5s', '7s'])# 5.5 points
    print calculate(['2h', '7d'])# -1.5 points 
    print ""
    print calculate(['Ah', 'Ad'])#20
    print calculate(['Kh', 'Kd'])#16
    print calculate(['Qh', 'Qd'])#14
    print calculate(['Jh', 'Jd'])#12
    print calculate(['As', 'Ks'])#12
    print calculate(['As', 'Qs'])#11
    print calculate(['Th', 'Td'])#10
    print calculate(['Ah', 'Kd'])#10
    print calculate(['As', 'Js'])#10
    print calculate(['5h', '5d'])#6
    print calculate(['6h', '6d'])#6
    print calculate(['Jh', '9d'])#6
    print calculate(['Ks', '2s'])#5
