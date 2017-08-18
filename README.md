# mit-poker-bots
The MIT poker bots server is responsible for dealing the cards and evaluating the winner. This project contains 2 poker bots and a command line interface to play against the bot. 

## Hughs bot
The bot's strategy is to use the Bill Chen formula to calculate the strength of the hole cards, then upon the board cards being dealt, it uses an iterative Monte Carlo simulation to simulate 3000 matches per round. The hands in each iteration are evaluated using the Deuces hand evaluation library to compare the hand strength of the virtual players in the simulation. The win frequency is calculated as a value between 0.0 and 1.0. The pot odds are then divided by the win frequency to infer the rate of return. If the rate of return is low, fold, medium then call or check, high then bet or raise.

## Hughs bot with discards
This bot extends the previous bot by discarding weak cards evaluated using monte carlo simulations. It was seperated in to a seperate folder as it is not pure Texas Holdem'. However allowing players to discard weak cards is the equivalent of cancelling an order in an orderbook on a trading platform, so it is a good feature to include.

## Manual command line interface
This bot can be run as an alternative player allowing a human user to interact with a bot on the MIT server.

## Setting up the environment
The only dependency is Python 2.7 with numpy

Install Numpy
```
pip install numpy
```

Configure the server
```
edit server/config.txt
```

Run the server
```
Open the command line and execute server/runserver.bat
```

Run a bot as player 1
```
Open the command line and execute client/hughs-bot-discards/pokerbot.bat -h localhost 3000
```

Run a bot as player 2
```
Open the command line and execute client/hughs-bot-discards/pokerbot.bat -h localhost 3001
```