import time
import holdem_functions
import holdem_argparser

'''
    Board: These are the community cards supplied to the calculation. This is in the form of a list of strings, with each string representing a card. If you do not want to specify community cards, you can set board to be None. Example: ["As", "Ks", "Jd"]
    Exact: This is a boolean which is True if you want an exact calculation, and False if you want a Monte Carlo simulation.
    Number of Simulations: This is the number of iterations run in the Monte Carlo simulation. Note that this parameter is ignored if Exact is set to True. This number must be positive, even if Exact is set to true.
    Input File: The name of the input file you want Holdem Calculator to read from. Mark as None, if you do not wish to read from a file. If Input File is set, library calls will not return anything.
    Hole Cards: These are the hole cards for each of the players. This is in the form of a list of strings, with each string representing a card. Example: ["As", "Ks", "Jd", "Td"]
    Verbose: This is a boolean which is True if you want Holdem Calculator to print the results.
'''
def calculate(board, exact, num, input_file, hole_cards, verbose):
    args = holdem_argparser.LibArgs(board, exact, num, input_file, hole_cards)
    hole_cards, n, e, board, filename = holdem_argparser.parse_lib_args(args)
    return run(hole_cards, n, e, board, filename, verbose)

def run(hole_cards, num, exact, board, file_name, verbose):
    if file_name:
        input_file = open(file_name, 'r')
        for line in input_file:
            if line is not None and len(line.strip()) == 0:
                continue
            hole_cards, board = holdem_argparser.parse_file_args(line)
            deck = holdem_functions.generate_deck(hole_cards, board)
            run_simulation(hole_cards, num, exact, board, deck, verbose)
            print "-----------------------------------"
        input_file.close()
    else:
        deck = holdem_functions.generate_deck(hole_cards, board)
        return run_simulation(hole_cards, num, exact, board, deck, verbose)

def run_simulation(hole_cards, num, exact, given_board, deck, verbose):
    num_players = len(hole_cards)
    # Create results data structures which track results of comparisons
    # 1) result_histograms: a list for each player that shows the number of
    #    times each type of poker hand (e.g. flush, straight) was gotten
    # 2) winner_list: number of times each player wins the given round
    # 3) result_list: list of the best possible poker hand for each pair of
    #    hole cards for a given board
    result_histograms, winner_list = [], [0] * (num_players + 1)
    for _ in xrange(num_players):
        result_histograms.append([0] * len(holdem_functions.hand_rankings))
    # Choose whether we're running a Monte Carlo or exhaustive simulation
    board_length = 0 if given_board is None else len(given_board)
    # When a board is given, exact calculation is much faster than Monte Carlo
    # simulation, so default to exact if a board is given
    if exact or given_board is not None:
        generate_boards = holdem_functions.generate_exhaustive_boards
    else:
        generate_boards = holdem_functions.generate_random_boards
    if (None, None) in hole_cards:
        hole_cards_list = list(hole_cards)
        unknown_index = hole_cards.index((None, None))
        for filler_hole_cards in holdem_functions.generate_hole_cards(deck):
            hole_cards_list[unknown_index] = filler_hole_cards
            deck_list = list(deck)
            deck_list.remove(filler_hole_cards[0])
            deck_list.remove(filler_hole_cards[1])
            holdem_functions.find_winner(generate_boards, tuple(deck_list),
                                         tuple(hole_cards_list), num,
                                         board_length, given_board, winner_list,
                                         result_histograms)
    else:
        holdem_functions.find_winner(generate_boards, deck, hole_cards, num,
                                     board_length, given_board, winner_list,
                                     result_histograms)
    if verbose:
        holdem_functions.print_results(hole_cards, winner_list,
                                       result_histograms)
    return holdem_functions.find_winning_percentage(winner_list)

