import argparse
import socket
import sys
import logging
import lib.BillChenCalc as bcc
import lib.MonteCarloSim as mcs

#Dictionary to split up parsing different packages


"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player:
    '''
        Initialize new player
    '''
    def __init__(self):
        logging.basicConfig(filename='log.txt',level=logging.DEBUG)
        self.holeCards = ['', '']                   #an array of strings indicating which holeCards you have
        self.boardCards = ['', '', '', '', '']      #an array of strings indicating which boardCards are out
        self.lastActions = [''] * 10                #an array of strings of the last actions that ocurred
        self.legalActions = ['', '', '', '', '']    #an array of strings indicating possible actions that can be made
        self.options = {
            "NEWGAME"           :   self.newGame,
            "KEYVALUE"          :   self.keyValue,
            "REQUESTKEYVALUES"  :   self.requestKeyValues,
            "NEWHAND"           :   self.newHand,
            "GETACTION"         :   self.getAction,
            "HANDOVER"          :   self.handOver
        }

    '''
        Used for running the game bot, should not be edited
    '''
    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                print "Cumulative change in bankroll (P/L): " + str(self.myBank)
                break
            #Determine packet type
            word = data.split()[0]
            logging.info(word)
            self.options[word](data)
            print data
        # Clean up the socket.
        s.close()

    '''
        Function to parse the new game packet 

        Ex. 
        NEWGAME yourName oppName stackSize bb numHands timeBank
        NEWGAME player1 player2 200 2 1000 20.000000
    '''
    def newGame(self, data):
        params = data.split()
        self.yourName = params[1]               #strings that identify your name
        self.oppName = params[2]                #strings that identify opponent name
        self.stackSize = int(params[3])         #integer number of chips in your chipstack 
        self.startingStackSize = int(params[3]) #integer number of chips in your chipstack at the start of the tournament
        self.bb = int(params[4])                #the big blind being used for the match (guaranteed to be a multiple of 2)
        self.numHands = int(params[5])          #an integer indicating the maximum number of hands to be played this match in the case where the tournament is still ongoing
        self.timeBank = float(params[6])        #a floating point number indicating the number of seconds your bot has left to return an action
        self.totalTimeBank = float(params[6])

    '''
        Function to parse the key value packet
    '''
    def keyValue(self, data):
        print "keyValue"

    '''
        Function to process requestKeyValues packet
    '''
    def requestKeyValues(self, data):
        # At the end, the engine will allow your bot save key/value pairs.
        # Send FINISH to indicate you're done.
        s.send("FINISH\n")

    '''
        Function to process newHand packet

        Ex.
        NEWHAND handId button holeCard1 holeCard2 holeCard3 holeCard4 myBank otherBank timeBank
        NEWHAND 10 true Ah Ac Kh Kc 100 -100 20.000000
        
    '''
    def newHand(self, data):
        self.reset()
        params = data.split()
        self.handId = int(params[1])            #an integer number indicating which hand has been dealt. This counter starts from 1 and increments with each hand.
        self.button = bool(params[2])           #a boolean indicating if you are the button
        self.holeCards[0] = params[3]           #Each card is represented by 2 alphanumeric characters. The first character indicates the rank 
        self.holeCards[1] = params[4]           #of the card, drawn from {2,3,4,5,6,7,8,9,T,J,Q,K,A} (T, Q, K, and A stand for ten, queen, king, 
                                                #and ace respectively). The second character indicates the suit of the card, drawn from {d,c,s,h}
        self.myBank = int(params[5])            #an integer indicating your cumulative change in bankroll
        self.otherBank = int(params[6])         #an integer indicating the opponent player's cumulative change in bankroll
        self.handType = 0                       #no hand has been indentified yet
        self.timeBank = float(params[7])
        self.lastBetValue = 0.0
        self.inGame = True
        print "\nHand: " + str(self.holeCards)

    '''
        Evaluate starting hand pre-flop
    '''
    def startingHandEval(self):
        cardANumeral = list(self.holeCards[0])[0]
        cardASuit = list(self.holeCards[0])[1]
        cardBNumeral = list(self.holeCards[1])[0]
        cardBSuit = list(self.holeCards[1])[1]
        chenScore = bcc.calculate([str(cardANumeral+cardASuit), str(cardBNumeral+cardBSuit)])
        
        return chenScore

    '''
        Evaluate hand after the flop
    '''
    def postFlopEval(self):
        prob = mcs.calculate(100, 1, self.holeCards, [self.boardCards[0], self.boardCards[1], self.boardCards[2]])
        return prob
    
    '''
        Evaluate hand after the turn
    '''
    def postTurnEval(self):
        prob = mcs.calculate(100, 1, self.holeCards, [self.boardCards[0], self.boardCards[1], self.boardCards[2], self.boardCards[3]])
        return prob

    '''
        Evaluate hand after the river
    '''
    def postRiverEval(self):
        prob = mcs.calculate(100, 1, self.holeCards, [self.boardCards[0], self.boardCards[1], self.boardCards[2], self.boardCards[3], self.boardCards[4]])
        return prob

    '''
        Function to process getAction packet
        Ex.
        GETACTION potSize numBoardCards [boardCards] numLastActions [lastActions] numLegalActions [legalActions] timeBank
        GETACTION 30 5 As Ks Qh Qd Qc 3 CHECK:two CHECK:one DEAL:RIVER 2 CHECK BET:2:30 19.997999999999998
    '''
    def getAction(self, data):
        params = data.split()
        self.potSize = int(params[1])           #an integer indicating the number of chips currently in the pot
        self.numBoardCards = int(params[2])     #an integer indicating the number of cards currently shown on the board. (Depending on the current street, there will be 0, 3, 4, or 5 cards.)
        ind = 3
        for i in range(self.numBoardCards):
            self.boardCards[i] = params[ind]
            ind += 1
        self.numLastActions = int(params[ind])  #an integer indicating how many PerformedActions are in the lastActions list of actions
        ind += 1
        for i in range(self.numLastActions):
            self.lastActions[i] = params[ind]
            ind += 1
        self.numLegalActions = int(params[ind]) #an integer indicating the number of LegalActions in the legalActions list of actions
        ind += 1
        for i in range(self.numLegalActions):
            self.legalActions[i] = params[ind]
            ind += 1
        self.timeBank = float(params[ind])
        
        #Parse last actions
        dealName = ""
        for action in self.lastActions:
            actionArray = action.split(':')
            if actionArray[0] == "DEAL":
                dealName = actionArray[1]
                print "Round: " + dealName
                print "Board cards: "  + str(self.boardCards)
            if actionArray[0] == "POST" or actionArray[0] == "BET" or actionArray[0] == "RAISE":
                #last POST BET or RAISE action is recorded
                self.lastBetValue = actionArray[1]
        
        #Calculate card strength for each round type
        handStrength = -1.0
        if self.numBoardCards == 0 and self.inGame == True:#PRE-FLOP
            handStrength = (float((100.0/20.0))*float(self.startingHandEval()))/100.0
        elif self.numBoardCards == 3 and self.inGame == True:#FLOP
            handStrength = self.postFlopEval()
        elif self.numBoardCards == 4 and self.inGame == True:#TURN
            handStrength = self.postTurnEval()
        elif self.numBoardCards == 5 and self.inGame == True:#RIVER
            handStrength = self.postRiverEval()
        
        #parse possible actions
        checkCall = "" # CHECK CALL
        canFold = False
        canBet = False
        canCall = False
        placeBetVal = 0
        raiseBetCommand = ""
        for action in self.legalActions:
            actionArray = action.split(':')
            if actionArray[0] == "CALL" or actionArray[0] == "CHECK":
                canCall = True
                checkCall = actionArray[0]
            if actionArray[0] == "FOLD":
                canFold = True
            if actionArray[0] == "RAISE" or actionArray[0] == "BET":
                canBet = True
                raiseBetCommand = actionArray[0]
                placeBetVal = actionArray[1]
        
        #calculate rate of return
        #where Rate of Return = Hand Strength / Pot Odds.
        #Mick West, "Inner Product", Game Developer Magazine, November 2005.
        potOdds = 0.0
        rateOfReturn = 1.0
        if (checkCall == "CALL" or checkCall == "CHECK"):
            potOdds = float(self.lastBetValue)/float(self.potSize)
            rateOfReturn = float(handStrength)/float(potOdds)
        
        print "potOdds:" + str(potOdds)
        print "handStrength:" + str(handStrength)
        print "rateOfReturn:" + str(rateOfReturn)
        
        #FOLD, (CALL or CHECK), RAISE decision
        if (rateOfReturn < 0.5 and canFold == True) or self.inGame == False:
            self.inGame = False
            print "FOLDING"
            s.send("FOLD\n")
        elif ((rateOfReturn >= 0.5) and (rateOfReturn <= 1.3) and (self.inGame == True) and (canCall == True)):
            print checkCall + "ING"
            s.send(checkCall + "\n")
        elif ((rateOfReturn > 1.3) and (self.inGame == True) and (canBet == True)):
            print raiseBetCommand + "ING" + " by: " + str(placeBetVal)
            s.send(raiseBetCommand + ":" + str(placeBetVal) + "\n")
        else:
            print checkCall + "ING"
            s.send(checkCall + "\n")

    '''
        Function to process handOver packet

        Ex. HANDOVER myBankRoll opponentBankRoll numBoardCards [boardCards] numLastActions [lastActions] timeBank
        HANDOVER 20 -20 5 As Ks Qh Qd Qc 1 WIN:20:one 19.997999999999998
    '''
    def handOver(self, data):
        params = data.split()
        self.myBankRoll = int(params[1])            #your net cumulative change in bankroll after the hand
        self.opponentBankRoll = int(params[2])      #opponent net cumulative change in bankroll after the hand
        self.numBoardCards = int(params[3])
        ind = 4
        for i in range(self.numBoardCards):
            self.boardCards[i] = params[ind]
            ind += 1
        self.numLastActions = int(params[ind])  #an integer indicating how many PerformedActions are in the lastActions list of actions
        ind += 1
        for i in range(self.numLastActions):
            self.lastActions[i] = params[ind]
            ind += 1
        self.timeBank = float(params[ind])

    '''
        Resets before each new hand
    '''
    def reset(self):
        self.boardCards = ['', '', '', '', '']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s)
