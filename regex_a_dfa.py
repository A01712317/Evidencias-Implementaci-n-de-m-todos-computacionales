import re
from collections import defaultdict

class NFA:
    def __init__(self, num_states, transitions, start_state, accept_states):
        self.num_states = num_states
        self.transitions = transitions  # Dictionary representation
        self.start_state = start_state
        self.accept_states = accept_states

    def __str__(self):
        result = []
        for state, trans in self.transitions.items():
            for symbol, next_states in trans.items():
                for next_state in next_states:
                    result.append(f"{state} => [({next_state}, '{symbol}')]")
        result.append(f"Accepting state: {', '.join(map(str, self.accept_states))}")
        return "\n".join(result)


class DFA:
    def __init__(self, transitions, start_state, accept_states):
        self.transitions = transitions  # Dictionary representation
        self.start_state = start_state
        self.accept_states = accept_states

    def __str__(self):
        result = []
        for state, trans in self.transitions.items():
            for symbol, next_state in trans.items():
                result.append(f"{state} => [('{next_state}', '{symbol}')]")
        result.append(f"Accepting states: {', '.join(self.accept_states)}")
        return "\n".join(result)


def regex_to_nfa(regex):
    postfix = to_postfix(regex)
    state_counter = 0

    def new_state():
        nonlocal state_counter
        state = state_counter
        state_counter += 1
        return state

    def add_transition(trans, state_from, symbol, state_to):
        trans[state_from][symbol].add(state_to)

    transitions = defaultdict(lambda: defaultdict(set))
    stack = []

    for char in postfix:
        if char.isalnum():  # Operand
            start = new_state()
            end = new_state()
            add_transition(transitions, start, char, end)
            stack.append((start, end))
        elif char == '*':  # Kleene Star
            nfa_start, nfa_end = stack.pop()
            start = new_state()
            end = new_state()
            # Epsilon transitions for Kleene Star
            add_transition(transitions, start, '#', nfa_start)
            add_transition(transitions, nfa_end, '#', nfa_start)  # Allows multiple repetitions
            add_transition(transitions, start, '#', end)  # Allows zero repetitions
            add_transition(transitions, nfa_end, '#', end)  # Epsilon transition to end
            stack.append((start, end))
        elif char == '+':  # Kleene Plus
            nfa_start, nfa_end = stack.pop()
            start = new_state()
            end = new_state()
            # Epsilon transitions for Kleene Plus (requires at least one repetition)
            add_transition(transitions, start, '#', nfa_start)
            add_transition(transitions, nfa_end, '#', nfa_start)  # Allows subsequent repetitions
            add_transition(transitions, nfa_end, '#', end)  # Allows transition to end after repetition
            stack.append((start, end))
        elif char == '|':  # Union
            nfa2_start, nfa2_end = stack.pop()
            nfa1_start, nfa1_end = stack.pop()
            start = new_state()
            end = new_state()
            # Epsilon transitions for Union
            add_transition(transitions, start, '#', nfa1_start)
            add_transition(transitions, start, '#', nfa2_start)
            add_transition(transitions, nfa1_end, '#', end)
            add_transition(transitions, nfa2_end, '#', end)
            stack.append((start, end))
        elif char == '.':  # Concatenation
            nfa2_start, nfa2_end = stack.pop()
            nfa1_start, nfa1_end = stack.pop()
            add_transition(transitions, nfa1_end, '#', nfa2_start)
            stack.append((nfa1_start, nfa2_end))

    start_state, accept_state = stack.pop()
    accept_states = {accept_state}

    return NFA(state_counter, transitions, start_state, accept_states)


def to_postfix(regex):
    precedence = {'*': 3, '.': 2, '|': 1, '(': 0, ')': 0}
    output = []
    operators = []

    for char in regex:
        if char.isalnum():
            output.append(char)
        elif char == '(':
            operators.append(char)
        elif char == ')':
            while operators and operators[-1] != '(':
                output.append(operators.pop())
            operators.pop()
        else:
            while operators and precedence[operators[-1]] >= precedence[char]:
                output.append(operators.pop())
            operators.append(char)

    while operators:
        output.append(operators.pop())

    return ''.join(output)


def nfa_to_dfa(nfa):
    def epsilon_closure(states):
        stack = list(states)
        closure = set(states)
        while stack:
            state = stack.pop()
            for next_state in nfa.transitions[state].get('#', []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    symbols = set(symbol for trans in nfa.transitions.values() for symbol in trans if symbol != '#')
    start_closure = frozenset(epsilon_closure({nfa.start_state}))
    dfa_states = {start_closure: 'A'}
    dfa_transitions = {}
    accept_states = set()
    unmarked_states = [start_closure]
    state_counter = 0

    while unmarked_states:
        current = unmarked_states.pop()
        dfa_transitions[dfa_states[current]] = {}
        for symbol in symbols:
            next_states = set()
            for state in current:
                next_states.update(nfa.transitions[state].get(symbol, []))
            closure = frozenset(epsilon_closure(next_states))
            if closure not in dfa_states:
                state_counter += 1
                dfa_states[closure] = chr(65 + state_counter)
                unmarked_states.append(closure)
            dfa_transitions[dfa_states[current]][symbol] = dfa_states[closure]
        if current & nfa.accept_states:
            accept_states.add(dfa_states[current])

    return DFA(dfa_transitions, 'A', accept_states)


# Example usage
regex = "(a|b)*"
nfa = regex_to_nfa(regex)
print("NFA:")
print(nfa)

dfa = nfa_to_dfa(nfa)
print("\nDFA:")
print(dfa)
