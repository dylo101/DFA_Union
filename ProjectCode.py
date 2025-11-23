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

# Generate union DFA accepting states
def generateUnionAcceptStates(dfa1, dfa2, productStates):
    unionAcceptStates = set()
    for (s1, s2) in productStates:
        # Accept if either DFA accepts state
        if s1 in dfa1["accepts"] or s2 in dfa2["accepts"]:
            unionAcceptStates.add((s1, s2))
    return unionAcceptStates

# Generate union DFA start state
def generateUnionStartState(dfa1, dfa2):
    return (dfa1["start"], dfa2["start"])

def validateUnionDFA(dfa1, dfa2, productStates, productTransitions, productStartState, productAcceptStates):

    # Collect errors here
    errors = []

    # Check start state validity
    if productStartState not in productStates:
        errors.append(f"Start state {productStartState} is not in product states.")

    # Check transitions exist for every product state
    for state in productStates:
        if state not in productTransitions:
            errors.append(f"No transitions found for product state {state}.")
            continue
        symbols = next(iter(dfa1["transitions"].values())).keys()
        for symbol in symbols:
            if symbol not in productTransitions[state]:
                errors.append(f"State {state} missing transition on '{symbol}'.")
            else:
                nxt = productTransitions[state][symbol]
                if nxt not in productStates:
                    errors.append(f"Transition {state} --{symbol}--> {nxt} goes to invalid state.")

    # Check accept states are inside product states
    for acc in productAcceptStates:
        if acc not in productStates:
            errors.append(f"Accepting state {acc} is not a valid product state.")

    # Reachability check from start state
    reachable = set()
    stack = [productStartState]

    while stack:
        cur = stack.pop()
        if cur in reachable:
            continue
        reachable.add(cur)
        for nxt in productTransitions.get(cur, {}).values():
            if nxt not in reachable:
                stack.append(nxt)
    unreachable = productStates - reachable
    if unreachable:
        errors.append(f"Unreachable states: {unreachable}")

    # Final report
    if errors:
        return {"result": "Validation Fail", "errors": errors}
    else:
        return {"result": "Validation Success"}

def outputUnionDFA(states, transitions, startState, acceptStates, filename="UnionDFA.json"):

    print("\n=== UNION DFA OUTPUT ===")

    # Print States
    print("\nStates:")
    for s in sorted(states):
        print(" ", s)

    # Print Start State
    print("\nStart State:")
    print(" ", startState)

    # Print Accept State(s)
    print("\nAccepting State(s):")
    for s in sorted(acceptStates):
        print(" ", s)

    # Print Transitions
    print("\nTransitions:")
    for state, trans in sorted(transitions.items()):
        print(f"{state}:")
        for symbol, target in trans.items():
            print(f"   on '{symbol}' -> {target}")

    def tup_to_name(t):
        return f"{t[0]},{t[1]}"

    # Builds list for "states"
    jsonStatesList = []
    for state in sorted(states):
        entry = {"state": tup_to_name(state)}
        for symbol, dest in transitions[state].items():
            entry[symbol] = tup_to_name(dest)
        jsonStatesList.append(entry)

    # Builds list for "accept-states"
    jsonAcceptList = [{"state": tup_to_name(acc)} for acc in sorted(acceptStates)]

    # Builds final JSON object
    outputJSON = {
        "states": jsonStatesList,
        "start-state": tup_to_name(startState),
        "accept-states": jsonAcceptList
    }

    # Save to JSON file
    with open(filename, "w") as outFile:
        json.dump(outputJSON, outFile, indent=4)

    print(f"\nUnion DFA saved to file: {filename}")
    print("======\n")


# Test Function For Program
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ProjectCode.py <input1.json> <input2.json>")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]

    try:
        dfa1 = readDFA(file1)
        dfa2 = readDFA(file2)
    except ValueError as e:
        print(e)
        sys.exit(1)

    # Generate union DFA components
    union_states = generateUnionStates(dfa1, dfa2)
    transitionData = generateUnionTransitions(dfa1, dfa2, union_states)
    union_transitions = transitionData["transitions"]
    union_accepts = generateUnionAcceptStates(dfa1, dfa2, union_states)
    union_start = generateUnionStartState(dfa1, dfa2)

    # Validate DFA
    validation = validateUnionDFA(
        dfa1,
        dfa2,
        union_states,
        union_transitions,
        union_start,
        union_accepts
    )

    if validation["result"] == "Validation Success":
        print("Validation Success")
        outputUnionDFA(
            union_states,
            union_transitions,
            union_start,
            union_accepts,
            "UnionDFA.json"
        )
        print("The Union DFA has been successfully generated and created as a file! Thank you!")
    else:
        print("Validation Fail")
        for err in validation.get("errors", []):
            print(" -", err)
        print("There seems to be an issue with the generated Union DFA. Make sure everything is correct and try again!")