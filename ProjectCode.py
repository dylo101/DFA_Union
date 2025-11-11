import json
import itertools
import sys

# Function to read DFA from a JSON file
def readDFA(file_path):
    try:
        with open(file_path, 'r') as f:
            DFAData = json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"Error: '{file_path}' is not a valid JSON file.")
    except FileNotFoundError:
        raise ValueError(f"Error: File '{file_path}' not found.")

    # Error Checking
    keyCheck = ["states", "start-state", "accept-states"]
    for key in keyCheck:
        if key not in DFAData:
            raise ValueError(f"Error: Missing key '{key}' in DFA JSON.")
        if not DFAData[key]:
            raise ValueError(f"Error: '{key}' cannot be empty in DFA JSON.")

    states = set()
    transitions = {}
    acceptStates = set()
    startState = DFAData.get("start-state")

    # Validates Start State
    if not isinstance(startState, str) or not startState.strip():
        raise ValueError("Error: 'start-state' must be a valid and non-empty string.")

    # Extract states and transitions
    for entry in DFAData["states"]:
        if "state" not in entry:
            raise ValueError("Error: Each state entry must have a 'state' key.")
        stateName = entry["state"]
        states.add(stateName)

        transitions[stateName] = {symbol: entry[symbol] for symbol in entry if symbol not in ["state"]}
        if not transitions[stateName]:
            raise ValueError(f"Error: State '{stateName}' must have at least one transition.")
        
    # Extract accepting states
    for acc in DFAData["accept-states"]:
        if "state" not in acc:
            raise ValueError("Error: Each accept state entry must have a 'state' key.")
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
            try: 
                next1 = dfa1["transitions"][s1][symbol]
                next2 = dfa2["transitions"][s2][symbol]
            except KeyError:
                raise ValueError(f"Error: Transition for symbol '{symbol}' is missing in one of the DFAs.")
            productTransitions[(s1, s2)][symbol] = (next1, next2)

    return {
        "states": productStates,
        "transitions": productTransitions
    }

#Test Function For Program
#if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ProjectCode.py <input1.json> <input2.json>")
        sys.exit(1)

    dfa1, dfa2 = sys.argv[1], sys.argv[2]

    try:
        dfa1 = readDFA(dfa1)
        dfa2 = readDFA(dfa2)
    except ValueError as e:
        print(e)
        sys.exit(1)

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