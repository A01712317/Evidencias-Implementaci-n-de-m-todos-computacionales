from collections import defaultdict

def insertar_concatenacion_explicita(expresion_regular):
    """
    Inserta explícitamente el símbolo '.' para indicar concatenación en casos donde
    la concatenación es implícita (por ejemplo, en 'ab' o 'a(bc)').
    """
    salida = []  # Lista que contiene la expresión con concatenaciones explícitas
    caracteres_especiales = {'|', '*', '+', '(', ')'}  # Conjunto de operadores especiales

    i = 0
    while i < len(expresion_regular):
        simbolo_actual = expresion_regular[i]
        salida.append(simbolo_actual)

        # Si hay un símbolo siguiente, se verifica si es necesario insertar una concatenación explícita
        if i + 1 < len(expresion_regular):
            simbolo_siguiente = expresion_regular[i + 1]

            # Determina si es necesario insertar un '.' según las reglas de concatenación implícita
            es_operador_cerradura = simbolo_actual in ['*', '+']
            es_simbolo_normal_actual = simbolo_actual not in caracteres_especiales or simbolo_actual == ')'
            es_simbolo_normal_siguiente = simbolo_siguiente not in caracteres_especiales or simbolo_siguiente == '('

            # Regla para insertar '.' entre símbolos adyacentes que deben ser concatenados
            if (es_simbolo_normal_actual and es_simbolo_normal_siguiente) or (es_operador_cerradura and es_simbolo_normal_siguiente) or (simbolo_actual == ')' and simbolo_siguiente == '('):
                salida.append('.')

        i += 1

    return "".join(salida)

def convertir_a_postfijo(expresion_regular):
    """
    Convierte una expresión regular con operadores (|, ., *, +, ()) a notación postfija
    utilizando el algoritmo de Shunting Yard de Dijkstra.
    """
    # Precedencia de los operadores. Mayor número = mayor precedencia.
    precedencia = {'*': 3, '+': 3, '.': 2, '|': 1}

    salida = []  # Lista para almacenar la expresión en notación postfija
    pila_operadores = []  # Pila para los operadores

    i = 0
    while i < len(expresion_regular):
        simbolo = expresion_regular[i]

        if simbolo.isalnum():  # Si es un símbolo alfanumérico, va directamente a la salida
            salida.append(simbolo)
        elif simbolo == '(':  # Si es un paréntesis de apertura, lo apilamos
            pila_operadores.append(simbolo)
        elif simbolo == ')':  # Si es un paréntesis de cierre, desapilamos hasta encontrar '('
            while pila_operadores and pila_operadores[-1] != '(':
                salida.append(pila_operadores.pop())
            pila_operadores.pop()  # Desapilamos el '('
        elif simbolo in ['|', '.', '*', '+']:  # Si es un operador, manejamos la precedencia
            if simbolo in ['*', '+']:  # Operadores unarios: asociatividad derecha
                while pila_operadores and pila_operadores[-1] != '(' and precedencia.get(pila_operadores[-1], 0) > precedencia[simbolo]:
                    salida.append(pila_operadores.pop())
                pila_operadores.append(simbolo)
            else:  # Operadores binarios: asociatividad izquierda
                while pila_operadores and pila_operadores[-1] != '(' and precedencia.get(pila_operadores[-1], 0) >= precedencia[simbolo]:
                    salida.append(pila_operadores.pop())
                pila_operadores.append(simbolo)

        i += 1

    # Vaciamos la pila con los operadores restantes
    while pila_operadores:
        salida.append(pila_operadores.pop())

    return "".join(salida)

def generar_estado(contador):
    """
    Genera un nuevo ID para un estado, incrementando un contador.
    """
    estado = contador[0]
    contador[0] += 1
    return estado

def construir_nfa(postfix):
    """
    Construye un NFA (Automáta Finito No Determinista) a partir de una expresión regular en notación postfija
    utilizando la construcción de Thompson.
    
    En este algoritmo, para cada operador en la expresión regular postfija, se generan fragmentos de NFA que
    se combinan mediante concatenación, unión o cerradura de Kleene para formar el NFA completo.
    """
    pila_nfa = []  # Pila que contendrá los NFA parciales durante la construcción
    contador_estados = [0]  # Contador global para generar IDs únicos para los estados

    # Iterar sobre cada símbolo en la expresión regular en notación postfija
    for simbolo in postfix:
        if simbolo.isalnum():  # Si el símbolo es alfanumérico (un caracter simple)
            # Crear un NFA elemental para el símbolo alfanumérico
            inicio = generar_estado(contador_estados)  # Generar un nuevo estado de inicio
            fin = generar_estado(contador_estados)  # Generar un nuevo estado final

            # El NFA elemental tiene una transición que va del estado de inicio al estado final con el símbolo
            transiciones = [(inicio, simbolo, fin)]
            
            # Apilar el NFA creado
            pila_nfa.append((inicio, fin, transiciones))

        elif simbolo == '.':  # Si el símbolo es el operador de concatenación
            # Pop los dos NFA parciales de la pila
            nfa2 = pila_nfa.pop()  # NFA que se concatena
            nfa1 = pila_nfa.pop()  # NFA que se mantiene al inicio

            # Extraer los estados de los dos NFA
            inicio1, fin1, transiciones1 = nfa1
            inicio2, fin2, transiciones2 = nfa2

            # Crear un nuevo conjunto de transiciones, concatenando ambos NFA
            # Se añade una transición epsilon entre el estado final de nfa1 y el estado inicial de nfa2
            nuevas_transiciones = transiciones1 + transiciones2 + [(fin1, '#', inicio2)]

            # Apilar el nuevo NFA concatenado
            pila_nfa.append((inicio1, fin2, nuevas_transiciones))

        elif simbolo == '|':  # Si el símbolo es el operador de unión (alternativa)
            # Pop los dos NFA parciales de la pila
            nfa2 = pila_nfa.pop()  # NFA para la parte derecha de la unión
            nfa1 = pila_nfa.pop()  # NFA para la parte izquierda de la unión

            # Extraer los estados de los dos NFA
            inicio1, fin1, transiciones1 = nfa1
            inicio2, fin2, transiciones2 = nfa2

            # Crear un nuevo inicio y un nuevo final para la unión
            nuevo_inicio = generar_estado(contador_estados)  # Nuevo estado de inicio para el NFA combinado
            nuevo_fin = generar_estado(contador_estados)  # Nuevo estado de final para el NFA combinado

            # Crear transiciones para la unión:
            # - Se agregan transiciones epsilon desde el nuevo inicio a los inicios de ambos NFA
            # - Se agregan transiciones epsilon desde los finales de ambos NFA al nuevo estado final
            nuevas_transiciones = transiciones1 + transiciones2 + [
                (nuevo_inicio, '#', inicio1), (nuevo_inicio, '#', inicio2),
                (fin1, '#', nuevo_fin), (fin2, '#', nuevo_fin)
            ]
            
            # Apilar el nuevo NFA que representa la unión de los dos NFA
            pila_nfa.append((nuevo_inicio, nuevo_fin, nuevas_transiciones))

        elif simbolo == '*':  # Si el símbolo es el operador de cerradura de Kleene (repetición)
            # Pop el NFA parcial de la pila
            nfa = pila_nfa.pop()

            # Extraer los estados del NFA
            inicio, fin, transiciones = nfa

            # Crear un nuevo inicio y un nuevo final para la cerradura de Kleene
            nuevo_inicio = generar_estado(contador_estados)  # Nuevo estado de inicio
            nuevo_fin = generar_estado(contador_estados)  # Nuevo estado final

            # Crear transiciones para la cerradura de Kleene:
            # - Transiciones epsilon del nuevo inicio al estado de inicio original
            # - Transiciones epsilon del nuevo inicio al nuevo estado final (para permitir la cadena vacía)
            # - Transiciones epsilon del estado final original al estado de inicio original (para repetir)
            # - Transiciones epsilon del estado final original al nuevo estado final (para terminar la repetición)
            nuevas_transiciones = transiciones + [
                (nuevo_inicio, '#', inicio), (nuevo_inicio, '#', nuevo_fin),
                (fin, '#', inicio), (fin, '#', nuevo_fin)
            ]
            
            # Apilar el NFA que representa la cerradura de Kleene
            pila_nfa.append((nuevo_inicio, nuevo_fin, nuevas_transiciones))

        elif simbolo == '+':  # Si el símbolo es el operador 'plus' (al menos una vez)
            # Similar a la cerradura de Kleene, pero sin permitir la cadena vacía
            nfa = pila_nfa.pop()
            inicio, fin, transiciones = nfa
            nuevo_inicio = generar_estado(contador_estados)
            nuevo_fin = generar_estado(contador_estados)

            # Crear transiciones para el 'plus':
            # - Transiciones epsilon del nuevo inicio al estado de inicio original
            # - Transiciones epsilon del estado final original al estado de inicio original (para repetir)
            # - Transiciones epsilon del estado final original al nuevo estado final (para terminar)
            nuevas_transiciones = transiciones + [
                (nuevo_inicio, '#', inicio), (fin, '#', inicio), (fin, '#', nuevo_fin)
            ]
            
            # Apilar el NFA que representa la operación 'plus'
            pila_nfa.append((nuevo_inicio, nuevo_fin, nuevas_transiciones))

    # Al finalizar, solo debe quedar un NFA completo en la pila
    return pila_nfa.pop()  # Retornamos el NFA final que está en la cima de la pila


def clausura_epsilon(estados, transiciones):
    """
    Calcula la clausura epsilon de un conjunto de estados. La clausura epsilon
    es el conjunto de estados alcanzables mediante transiciones epsilon ('#').
    """
    pila = list(estados)
    resultado = set(estados)

    while pila:
        estado = pila.pop()
        for origen, simbolo, destino in transiciones:
            if origen == estado and simbolo == '#' and destino not in resultado:
                resultado.add(destino)
                pila.append(destino)

    return resultado

def mover_estados(estados, simbolo, transiciones):
    """
    Mueve un conjunto de estados mediante un símbolo determinado, retornando
    los estados alcanzables desde esos estados mediante el símbolo.
    """
    resultado = set()
    for estado in estados:
        for origen, s, destino in transiciones:
            if origen == estado and s == simbolo:
                resultado.add(destino)
    return resultado

def convertir_nfa_a_dfa(inicio_nfa, fin_nfa, transiciones, alfabeto):
    """
    Convierte un NFA en un DFA mediante la construcción de subconjuntos (Subset Construction).
    """
    clausura_inicial = clausura_epsilon([inicio_nfa], transiciones)
    dfa_estados = [clausura_inicial]
    cola = [clausura_inicial]
    nombre_estados = {tuple(sorted(clausura_inicial)): 'A'}
    contador_nombres = 1
    dfa_transiciones = []
    estados_aceptacion = set()

    while cola:
        estado_actual = cola.pop(0)
        nombre_estado_actual = nombre_estados[tuple(sorted(estado_actual))]

        # Si el estado final del NFA está en el conjunto de estados actuales, lo marcamos como aceptante
        if fin_nfa in estado_actual:
            estados_aceptacion.add(nombre_estado_actual)

        for simbolo in alfabeto:
            if simbolo == '#':
                continue  # No se procesan transiciones epsilon

            # Movemos y calculamos la clausura epsilon
            estados_siguientes = mover_estados(estado_actual, simbolo, transiciones)
            clausura_siguientes = clausura_epsilon(estados_siguientes, transiciones)

            if clausura_siguientes:
                clausura_tuple = tuple(sorted(clausura_siguientes))

                if clausura_tuple not in nombre_estados:
                    nombre_estados[clausura_tuple] = chr(ord('A') + contador_nombres)
                    contador_nombres += 1
                    dfa_estados.append(clausura_siguientes)
                    cola.append(clausura_siguientes)

                nombre_siguiente_estado = nombre_estados[clausura_tuple]
                dfa_transiciones.append((nombre_estado_actual, simbolo, nombre_siguiente_estado))

    return dfa_transiciones, estados_aceptacion, nombre_estados

def ejecutar():
    """
    Función principal que ejecuta todo el proceso de conversión de una expresión regular
    a un DFA.
    """
    alfabeto = input("Alfabeto: ").strip()
    regex_inicial = input("Expresión Regular: ").strip()

    # Paso 1: Insertar concatenación explícita
    regex_concatenada = insertar_concatenacion_explicita(regex_inicial)

    # Paso 2: Convertir a notación postfija (Shunting Yard)
    postfix = convertir_a_postfijo(regex_concatenada)

    # Paso 3: Construcción de Thompson -> NFA
    inicio_nfa, fin_nfa, transiciones_nfa = construir_nfa(postfix)

    # Mostrar el NFA
    print("\n--- NFA ---")
    trans_dict = defaultdict(list)
    for origen, simbolo, destino in transiciones_nfa:
        trans_dict[origen].append((destino, simbolo))

    for estado in sorted(trans_dict.keys()):
        print(f"{estado} => {trans_dict[estado]}")
    print(f"Estado de aceptación: {fin_nfa}")

    # Paso 4: Convertir NFA a DFA (construcción de subconjuntos)
    alfabeto_sin_epsilon = [c for c in alfabeto if c != '#']
    dfa_transiciones, dfa_aceptacion, nombre_estados = convertir_nfa_a_dfa(inicio_nfa, fin_nfa, transiciones_nfa, alfabeto_sin_epsilon)

    # Mostrar el DFA
    print("\n--- DFA ---")
    dfa_dict = defaultdict(list)
    for estado_origen, simbolo, estado_destino in dfa_transiciones:
        dfa_dict[estado_origen].append((estado_destino, simbolo))

    for estado in sorted(dfa_dict.keys()):
        print(f"{estado} => {dfa_dict[estado]}")
    print("Estados de aceptación:", sorted(dfa_aceptacion))

# Ejecuta la función principal
ejecutar()
