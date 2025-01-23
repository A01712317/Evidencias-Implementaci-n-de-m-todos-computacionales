class NFA:
    def __init__(self):
        self.transitions = {}  # Diccionario de transiciones
        self.start_state = None
        self.accept_state = None

    def add_transition(self, from_state, to_state, symbol):
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append((to_state, symbol))

    def display(self):
        for state, transitions in self.transitions.items():
            print(f"{state} => {transitions}")
        print(f"Start state: {self.start_state}")
        print(f"Accepting state: {self.accept_state}")


def create_nfa_for_symbol(symbol):
    nfa = NFA()
    start_state = 0
    accept_state = 1
    nfa.start_state = start_state
    nfa.accept_state = accept_state
    nfa.add_transition(start_state, accept_state, symbol)
    return nfa


def union_nfas(nfa1, nfa2):
    nfa = NFA()
    start_state = 0
    accept_state = 1

    nfa.start_state = start_state
    nfa.accept_state = accept_state

    # Añadimos transiciones de inicio
    nfa.add_transition(start_state, nfa1.start_state, 'ε')
    nfa.add_transition(start_state, nfa2.start_state, 'ε')

    # Añadimos las transiciones de nfa1 y nfa2
    for state, transitions in nfa1.transitions.items():
        for to_state, symbol in transitions:
            nfa.add_transition(state, to_state, symbol)

    for state, transitions in nfa2.transitions.items():
        for to_state, symbol in transitions:
            nfa.add_transition(state, to_state, symbol)

    # Añadimos transiciones de aceptación
    nfa.add_transition(nfa1.accept_state, accept_state, 'ε')
    nfa.add_transition(nfa2.accept_state, accept_state, 'ε')

    return nfa


def concatenate_nfas(nfa1, nfa2):
    nfa = NFA()
    start_state = 0
    accept_state = 1

    nfa.start_state = start_state
    nfa.accept_state = accept_state

    # Añadimos las transiciones de nfa1
    for state, transitions in nfa1.transitions.items():
        for to_state, symbol in transitions:
            nfa.add_transition(state, to_state, symbol)

    # Añadimos las transiciones de nfa2
    for state, transitions in nfa2.transitions.items():
        for to_state, symbol in transitions:
            nfa.add_transition(state, to_state, symbol)

    # Conectamos el estado de aceptación de nfa1 con el estado de inicio de nfa2
    nfa.add_transition(nfa1.accept_state, nfa2.start_state, 'ε')

    # Estado de aceptación será el de nfa2
    nfa.accept_state = nfa2.accept_state

    return nfa


def kleene_star_nfa(nfa):
    new_nfa = NFA()
    start_state = 0
    accept_state = 1

    new_nfa.start_state = start_state
    new_nfa.accept_state = accept_state

    # Añadimos transiciones de inicio
    new_nfa.add_transition(start_state, nfa.start_state, 'ε')
    new_nfa.add_transition(start_state, accept_state, 'ε')

    # Añadimos las transiciones de nfa
    for state, transitions in nfa.transitions.items():
        for to_state, symbol in transitions:
            new_nfa.add_transition(state, to_state, symbol)

    # Añadimos transiciones de aceptación
    new_nfa.add_transition(nfa.accept_state, accept_state, 'ε')
    new_nfa.add_transition(nfa.accept_state, nfa.start_state, 'ε')

    return new_nfa

def regex_to_nfa(regex):
    stack = []
    i = 0
    while i < len(regex):
        char = regex[i]
        print(f"Procesando: {char}")  # Imprime el carácter que estamos procesando
        print(f"Pila actual: {stack}")  # Imprime el estado actual de la pila

        if char == '(':  # Abre paréntesis, es el inicio de una subexpresión
            # Procesamos la subexpresión dentro de los paréntesis
            subexpr = ''
            i += 1
            open_parens = 1  # Contador para paréntesis
            while open_parens > 0 and i < len(regex):
                if regex[i] == '(':
                    open_parens += 1
                elif regex[i] == ')':
                    open_parens -= 1
                subexpr += regex[i]
                i += 1

            # Recursivamente procesamos la subexpresión entre paréntesis
            print(f"Subexpresión procesada: {subexpr}")  # Imprime la subexpresión procesada
            nfa = regex_to_nfa(subexpr[:-1])  # Llamada recursiva para subexpresión (sin el ')')
            stack.append(nfa)
            continue

        elif char == ')':  # Cierre de paréntesis
            # No se hace nada aquí, ya procesamos la subexpresión
            pass

        elif char in 'ab':  # Si el carácter es 'a' o 'b', crea el NFA correspondiente
            stack.append(create_nfa_for_symbol(char))

        elif char == '|':  # Unión de dos NFA
            if len(stack) < 2:
                raise ValueError(f"Error: No hay suficientes NFA para realizar la unión, pila: {stack}")
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(union_nfas(nfa1, nfa2))

        elif char == '.':  # Concatenación
            if len(stack) < 2:
                raise ValueError(f"Error: No hay suficientes NFA para realizar la concatenación, pila: {stack}")
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(concatenate_nfas(nfa1, nfa2))

        elif char == '*':  # Estrella de Kleene
            if len(stack) < 1:
                raise ValueError(f"Error: No hay NFA para aplicar la estrella de Kleene, pila: {stack}")
            nfa = stack.pop()
            stack.append(kleene_star_nfa(nfa))

        i += 1

    if len(stack) != 1:
        raise ValueError(f"Error: La pila no contiene un solo NFA al final del procesamiento, pila final: {stack}")

    return stack.pop()


# Ejemplo de uso
regex = "(a|b)*abb"  # Ejemplo de expresión regular

# Paso 1: Convertir la expresión regular a NFA
try:
    nfa = regex_to_nfa(regex)  # Convierte a NFA
    nfa.display()
except ValueError as e:
    print(f"Error en la conversión de la expresión regular a NFA: {e}")
