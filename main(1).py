import time
import tracemalloc

MAX_RECURSION_DEPTH = 10000

def dpll(cnf, assignment=set(), depth=0):
    if depth > MAX_RECURSION_DEPTH:
        return None

    cnf = simplify(cnf, assignment)

    # If any clause is empty -> conflict
    if any(len(clause) == 0 for clause in cnf):
        return False

    # If no clauses left -> SAT
    if not cnf:
        return True

    # Unit propagation
    unit_literals = {next(iter(clause)) for clause in cnf if len(clause) == 1}
    if unit_literals:
        return dpll(cnf, assignment | unit_literals, depth + 1)

    # Pure literal elimination
    pure_literals = find_pure_literals(cnf)
    if pure_literals:
        return dpll(cnf, assignment | pure_literals, depth + 1)

    # Choose a literal to branch on
    chosen = next(iter(next(iter(cnf))))  # choose any literal
    return (
        dpll(cnf, assignment | {chosen}, depth + 1) or
        dpll(cnf, assignment | {negate(chosen)}, depth + 1)
    )

def simplify(cnf, assignment):
    simplified = set()
    for clause in cnf:
        if clause & assignment:
            continue  # clause is satisfied
        new_clause = {lit for lit in clause if negate(lit) not in assignment}
        simplified.add(frozenset(new_clause))
    return simplified

def find_pure_literals(cnf):
    literals = set()
    negations = set()
    for clause in cnf:
        for lit in clause:
            if lit.startswith('¬'):
                negations.add(lit[1:])
            else:
                literals.add(lit)
    pure = (literals - negations) | ({'¬' + l for l in (negations - literals)})
    return pure

def negate(literal):
    return literal[1:] if literal.startswith('¬') else '¬' + literal

def print_cnf(cnf):
    return ' ∧ '.join(['(' + ' ∨ '.join(sorted(clause)) + ')' for clause in cnf])

# --- Test Examples ---
cnf_examples = [
    {'name': 'Trivial SAT', 'cnf': [{ 'A' }]},
    {'name': 'Trivial UNSAT', 'cnf': [{ 'A' }, { '¬A' }]},
    {'name': 'Simple SAT', 'cnf': [{ 'A', 'B' }, { '¬A' }]},
    {'name': 'Simple UNSAT', 'cnf': [{ 'A' }, { 'B' }, { '¬A', '¬B' }]},
    {'name': 'Chain SAT', 'cnf': [{ 'A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }]},
    {'name': 'Chain UNSAT', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }, { '¬C', '¬A' }]},
    {'name': '3-SAT SAT', 'cnf': [{ 'A', 'B', 'C' }, { '¬A', 'D', 'E' }, { '¬B', '¬E', 'F' }]},
    {'name': '3-SAT UNSAT', 'cnf': [{ 'A' }, { 'B' }, { 'C' }, { '¬A', '¬B' }, { '¬B', '¬C' }, { '¬C', '¬A' }]},
    {'name': 'Redundant SAT', 'cnf': [{ 'A' }, { 'A', 'B' }, { 'A', 'B', 'C' }]},
    {'name': 'Deep Contradiction', 'cnf': [{ 'A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }, { '¬D', 'E' }, { '¬E', '¬A' }]},
    {'name': 'Pure Literal SAT', 'cnf': [{ 'A' }, { 'B', 'C' }, { 'C', 'D' }]},
    {'name': 'Unit Propagation SAT', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }]},
    {'name': 'Deep UNSAT', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }, { '¬D', 'E' }, { '¬E', '¬A' }]},
    {'name': 'Complex 3-SAT SAT', 'cnf': [{ 'A', 'B', 'C' }, { '¬A', 'D', 'E' }, { '¬B', '¬E', 'F' }, { '¬C', 'F', 'G' }, { '¬D', '¬F', 'G' }]},
    {'name': 'Hard contradiction', 'cnf': [{ 'A' }, { '¬A', 'B' }, { '¬B', 'C' }, { '¬C', 'D' }, { '¬D', 'E' }, { '¬E', 'F' }, { '¬F', '¬A' }]},
]

for i, example in enumerate(cnf_examples, start=1):
    name = example['name']
    cnf = {frozenset(clause) for clause in example['cnf']}

    print(f"Example {i}: {name}")
    print("CNF:", print_cnf(cnf))

    tracemalloc.start()
    start = time.perf_counter()
    result = dpll(cnf)
    end = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if result is None:
        print("Result:️ Too complexp")
    elif result is True:
        print("Result: SATISFIABLE")
    else:
        print("Result: UNSATISFIABLE")

    print(f" Time: {(end - start) * 1e6:.2f} μs")
    print(f" Peak memory: {peak / 1024:.2f} KB")
