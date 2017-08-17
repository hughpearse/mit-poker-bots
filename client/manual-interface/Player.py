import argparse
import socket
import sys
import logging
import os


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
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

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
            #print data
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
        print "\nNew Hand: " + str(self.holeCards)

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
        
        #parse last actions
        print "Last Actions: "
        action_command_list = []
        for action in self.lastActions:
            actionArray = action.split(':')
            action_command_list.append(actionArray[0])
            if len(actionArray[0]) > 0:
                print " " + str(actionArray)
        if "DEAL" in action_command_list:
            print "Hole cards:"
            print "    " + str(self.holeCards)
            print "Board cards:"
            print "    " + str(self.boardCards)
        
        #parse possible actions
        print "Possible Actions: "
        action_command_list = []
        for action in self.legalActions:
            actionArray = action.split(':')
            action_command_list.append(actionArray[0])
            if len(actionArray[0]) > 0:
                print " " + str(actionArray)
        
        user_input = "X"
        if not (user_input in action_command_list):
            user_input = raw_input('Enter action: ')
        
        if user_input == "CALL":
            s.send("CALL\n")
        elif user_input == "CHECK":
            s.send("CHECK\n")
        elif user_input == "FOLD":
            s.send("FOLD\n")
        elif user_input == "BET":
            quantity = raw_input('Enter amount: ')
            s.send("BET:" + str(quantity) + "\n")
        elif user_input == "RAISE":
            quantity = raw_input('Enter amount: ')
            s.send("RAISE:" + str(quantity) + "\n")
        elif user_input == "DISCARD":
            card = raw_input('Enter card: ')
            s.send("BET:" + str(card) + "\n")
        else:
            s.send("CHECK\n")
        print " "

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
