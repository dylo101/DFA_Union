import json
import itertools

# Function to read DFA from a JSON file
def readDFA(file_path):
    with open(file_path, 'r') as f:
        DFAData = json.load(f)
    
    states = set()
    transitions = {}
    acceptStates = set()
    startState = DFAData.get("start-state")

    # Extract states and transitions
    for entry in DFAData["states"]:
        stateName = entry["state"]
        states.add(stateName)
        transitions[stateName] = {symbol: entry[symbol] for symbol in entry if symbol not in ["state"]}

    # Extract accepting states
    for acc in DFAData["accept-states"]:
        acceptStates.add(acc["state"])

    return {
        "states": states,
        "transitions": transitions,
        "start": startState,
        "accepts": acceptStates
    }

# Function to generate union DFA States
def generateUnionStates(dfa1, dfa2):
    productStates = set(itertools.product(dfa1["states"], dfa2["states"]))
    return productStates

# Function to generate union DFA Transitions
def generateUnionTransitions(dfa1, dfa2, productStates):
    productTransitions = {}

    symbols = set()
    for transition in dfa1["transitions"].values():
        symbols.update(transition.keys())

    # Build transitions for the union DFA
    for (s1, s2) in productStates:
        productTransitions[(s1, s2)] = {}
        for symbol in symbols:
            next1 = dfa1["transitions"][s1][symbol]
            next2 = dfa2["transitions"][s2][symbol]
            productTransitions[(s1, s2)][symbol] = (next1, next2)

    return {
        "states": productStates,
        "transitions": productTransitions
    }

#Test Function For Program
#if __name__ == "__main__":
    dfa1 = readDFA("TestFile11.json")
    dfa2 = readDFA("TestFile12.json")

    # Step 1: build Cartesian product of states
    union_states = generateUnionStates(dfa1, dfa2)

    print("Union States:")
    for s in union_states:
        print(s)

    # Step 2: build transition function from union states
    union_transitions = generateUnionTransitions(dfa1, dfa2, union_states)

    print("\nUnion Transitions:")
    for s, transition in union_transitions.items():
        print(f"\n{s} -> {transition}")