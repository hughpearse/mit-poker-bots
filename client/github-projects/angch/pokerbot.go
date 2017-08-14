// quick hack, too lazy to fix this properly.
// Yes, I know scoring logic coded here is wrong for the following format:
//   "make the best hand using exactly two of the dealt cards and three community cards."

package main

import (
	"bufio"
	"fmt"
	"log"
	"net"
	"strconv"
	"strings"
)

// NEWHAND handId button holeCard1 holeCard2 holeCard3 holeCard4 myBank otherBank timeBank
// NEWHAND 1 false Js Qd 8h 4d 0 0 10.000000
type hand struct {
	handId    int
	button    bool
	cards     []string
	myBank    int
	otherBank int
	timeBank  float64
}

type action struct {
	action string
	min    int
	max    int
	who    string
}

// GETACTION potSize numBoardCards [boardCards] numLastActions [lastActions] numLegalActions [legalActions] timebank
// GETACTION 3 0 2 POST:1:go POST:2:test1 3 CALL FOLD RAISE:4:6 10.0
type getAction struct {
	potSize      int
	boardCards   []string
	lastActions  []string
	legalActions []action
	timeBank     float64
}

// yes, too lazy to implement flushes and straights.
func score(h hand) int {
	// pair checks

	face := make(map[byte]int, 0)
	suit := make(map[byte]int, 0)

	for _, v := range h.cards {
		f := v[0]
		s := v[1]
		face[f] = face[f] + 1
		suit[s] = suit[s] + 1
	}

	pairs := 0
	trips := 0
	fours := 0
	for _, v := range face {
		if v == 2 {
			pairs++
		}
		if v == 3 {
			trips++
		}
		if v == 4 {
			fours++
		}
	}

	if fours == 1 {
		fmt.Println("Four of a kind!")
		return 100
	}
	if pairs == 1 && trips == 1 {
		fmt.Println("Full house")
		return 50
	}
	if trips == 1 {
		fmt.Println("3 of a kind")
		return 30
	}
	if pairs == 2 {
		fmt.Println("2 pairs!")
		return 10
	}
	if pairs == 1 {
		fmt.Println("one pair")
		return 5
	}

	return 0
}

func parseHand(input string) hand {
	inputs := strings.Split(strings.TrimSpace(string(input)), " ")
	h := hand{}

	if len(inputs) == 10 {
		if inputs[0] != "NEWHAND" {
			log.Fatal("Not a new hand")
		}
		handId, err := strconv.Atoi(inputs[1])
		if err != nil {
			log.Println("Non int handId", inputs[1])
		}
		h.handId = handId

		if inputs[2] == "false" {
			h.button = false
		} else {
			h.button = true
		}

		h.cards = make([]string, 4)
		for i := 3; i <= 6; i++ {
			c := inputs[i]
			h.cards[i-3] = c
		}

		bank, err := strconv.Atoi(inputs[7])
		h.myBank = bank
		bank, err = strconv.Atoi(inputs[8])
		h.otherBank = bank

		h.timeBank, err = strconv.ParseFloat(inputs[9], 64)
		if err != nil {
			log.Fatal("parse timebank", err)
		}

	} else {
		log.Fatal("wrong sized inputs", inputs)
	}

	return h
}

func parseGetAction(input string) getAction {
	inputs := strings.Split(strings.TrimSpace(string(input)), " ")
	ga := getAction{}

	if len(inputs) < 1 {
		log.Fatal("Not enough getactions")
	}
	if inputs[0] != "GETACTION" {
		log.Fatal("Not a GetAction")
	}
	ga.potSize, _ = strconv.Atoi(inputs[1])

	//GETACTION 3 0 2 POST:1:go POST:2:test1 3 CALL FOLD RAISE:4:6 10.0
	size, _ := strconv.Atoi(inputs[2])
	ga.boardCards = make([]string, size)
	k := 3
	for i := 0; i < size; i++ {
		ga.boardCards[i] = inputs[k]
		k++
	}

	size, _ = strconv.Atoi(inputs[k])
	k++
	ga.lastActions = make([]string, size)
	for i := 0; i < size; i++ {
		ga.lastActions[i] = inputs[k]
		k++
	}

	size, _ = strconv.Atoi(inputs[k])
	k++
	ga.legalActions = make([]action, size)
	for i := 0; i < size; i++ {
		a := action{}

		split := strings.Split(inputs[k], ":")
		a.action = split[0]

		if a.action == "RAISE" {
			min, _ := strconv.Atoi(split[1])
			max, _ := strconv.Atoi(split[2])
			a.min = min
			a.max = max
		}

		ga.legalActions[i] = a
		k++
	}

	return ga
}

// GETACTION 3 0 2 POST:1:go POST:2:test1 3 CALL FOLD RAISE:4:6 10.0
// https://xkcd.com/221/
func pickRandomAction(h hand, ga getAction) action {
	return ga.legalActions[0]
}

func pickScoredAction(h hand, ga getAction) action {
	s := score(h)
	if s == 0 {
		a := action{
			action: "FOLD",
		}
		return a
	}
	if s > 0 {
		a := action{
			action: "CALL",
		}

		for _, v := range ga.legalActions {
			if v.action == "RAISE" {
				a.action = "RAISE:" + strconv.Itoa(v.min)
			}
		}
		return a
	}
	return ga.legalActions[0]
}

func runBot() {
	url := "localhost:3001"
	conn, err := net.Dial("tcp", url)
	if err != nil {
		log.Fatal("Can't connect to bot engine at ", url)
	}
	engine := bufio.NewReader(conn)
	newgame, err := engine.ReadString('\n')
	if err != nil {
		log.Println("Stream closed")
		return
	}
	fmt.Println(newgame)

	for {
		// expect new hand
		newhand, err := engine.ReadString('\n')
		if err != nil {
			//log.Fatal(err)
			log.Println("Stream closed2")
			return
		}
		fmt.Println(newhand)
		fmt.Println("<< ", newhand)

		commands := strings.Split(strings.TrimSpace(newhand), " ")
		if commands[0] == "REQUESTKEYVALUES" {
			//fmt.Println("cont")
			fmt.Println("> ", "FINISH")
			fmt.Fprintf(conn, "FINISH\n")
			continue
		}
		// NEWHAND 1 false Js Qd 8h 4d 0 0 10.000000
		hand := parseHand(newhand)
		fmt.Println(hand)
		//fmt.Fprintf(conn, "FOLD\r\n")

		for {
			// expect new action or handover
			newaction, err := engine.ReadString('\n')
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println("< ", newaction)
			commands := strings.Split(strings.TrimSpace(newaction), " ")
			if commands[0] == "HANDOVER" {
				//fmt.Println("cont")
				break
			}
			getAction := parseGetAction(newaction)
			//pickAction := pickRandomAction(hand, getAction)
			pickAction := pickScoredAction(hand, getAction)
			fmt.Fprintf(conn, pickAction.action+"\n")
			fmt.Println("> ", pickAction)
		}
	}
}

func main() {
	//	for {
	if true {
		runBot()
		runBot()
	}
	////		time.Sleep(time.Second * 20)
	//	}
	//	runBot()
	//hand := parseHand("NEWHAND 1 false Js Qd 8h 4d 0 0 10.000000")
	//fmt.Println(Score(hand))
	//getAction := parseGetAction("GETACTION 3 0 2 POST:1:go POST:2:test1 3 CALL FOLD RAISE:4:6 10.0")
	//fmt.Println(getAction)
}
