"""
Example 1: STRIPS-Style Planner
==================================
A classical STRIPS planner for the Blocks World domain.
Operators have preconditions and effects. Uses forward state-space search.

Run: python examples/01_strips_planner.py
"""

from collections import deque
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Predicate:
    """A logical predicate like on(A, B) or clear(A)."""
    name: str
    args: tuple

    def __repr__(self):
        return f"{self.name}({', '.join(self.args)})"


@dataclass
class Operator:
    """A STRIPS operator with preconditions and effects."""
    name: str
    params: tuple
    preconditions: frozenset  # Set of Predicates that must be true
    add_effects: frozenset  # Predicates that become true
    delete_effects: frozenset  # Predicates that become false

    def __repr__(self):
        return f"{self.name}({', '.join(self.params)})"

    def applicable(self, state: frozenset) -> bool:
        return self.preconditions.issubset(state)

    def apply(self, state: frozenset) -> frozenset:
        return (state - self.delete_effects) | self.add_effects


def create_blocks_world_operators(blocks: list) -> list:
    """Generate all ground operators for the Blocks World."""
    operators = []
    positions = blocks + ["table"]

    for block in blocks:
        # Move block from one block to another
        for source in blocks:
            if source == block:
                continue
            for dest in blocks:
                if dest == block or dest == source:
                    continue
                op = Operator(
                    name=f"move({block},{source},{dest})",
                    params=(block, source, dest),
                    preconditions=frozenset([
                        Predicate("on", (block, source)),
                        Predicate("clear", (block,)),
                        Predicate("clear", (dest,)),
                    ]),
                    add_effects=frozenset([
                        Predicate("on", (block, dest)),
                        Predicate("clear", (source,)),
                    ]),
                    delete_effects=frozenset([
                        Predicate("on", (block, source)),
                        Predicate("clear", (dest,)),
                    ]),
                )
                operators.append(op)

        # Move block from a block to table
        for source in blocks:
            if source == block:
                continue
            op = Operator(
                name=f"move_to_table({block},{source})",
                params=(block, source),
                preconditions=frozenset([
                    Predicate("on", (block, source)),
                    Predicate("clear", (block,)),
                ]),
                add_effects=frozenset([
                    Predicate("on", (block, "table")),
                    Predicate("clear", (source,)),
                ]),
                delete_effects=frozenset([
                    Predicate("on", (block, source)),
                ]),
            )
            operators.append(op)

        # Move block from table to another block
        for dest in blocks:
            if dest == block:
                continue
            op = Operator(
                name=f"move_from_table({block},{dest})",
                params=(block, dest),
                preconditions=frozenset([
                    Predicate("on", (block, "table")),
                    Predicate("clear", (block,)),
                    Predicate("clear", (dest,)),
                ]),
                add_effects=frozenset([
                    Predicate("on", (block, dest)),
                ]),
                delete_effects=frozenset([
                    Predicate("on", (block, "table")),
                    Predicate("clear", (dest,)),
                ]),
            )
            operators.append(op)

    return operators


def bfs_plan(initial_state: frozenset, goal: frozenset, operators: list, max_depth: int = 20) -> list:
    """Breadth-first search through state space."""
    if goal.issubset(initial_state):
        return []

    queue = deque([(initial_state, [])])
    visited = {initial_state}
    nodes_explored = 0

    while queue:
        state, plan = queue.popleft()
        nodes_explored += 1

        if len(plan) >= max_depth:
            continue

        for op in operators:
            if op.applicable(state):
                new_state = op.apply(state)
                if new_state not in visited:
                    new_plan = plan + [op]
                    if goal.issubset(new_state):
                        print(f"  Found plan! (explored {nodes_explored} states)")
                        return new_plan
                    visited.add(new_state)
                    queue.append((new_state, new_plan))

    print(f"  No plan found (explored {nodes_explored} states)")
    return None


def print_state(state: frozenset, label: str = ""):
    """Pretty-print a blocks world state."""
    if label:
        print(f"\n  {label}:")
    on_table = []
    stacks = {}
    for pred in sorted(state, key=str):
        if pred.name == "on" and pred.args[1] == "table":
            on_table.append(pred.args[0])

    # Build stacks
    for base in on_table:
        stack = [base]
        current = base
        while True:
            top = None
            for pred in state:
                if pred.name == "on" and pred.args[1] == current:
                    top = pred.args[0]
                    break
            if top:
                stack.append(top)
                current = top
            else:
                break
        stacks[base] = stack

    # Render
    max_height = max(len(s) for s in stacks.values()) if stacks else 0
    for level in range(max_height - 1, -1, -1):
        row = "    "
        for base in sorted(stacks.keys()):
            if level < len(stacks[base]):
                row += f"[{stacks[base][level]}] "
            else:
                row += "    "
        print(row)
    print("    " + "--- " * len(stacks))
    print("    " + "TABLE")


if __name__ == "__main__":
    print("=== STRIPS Blocks World Planner ===")

    blocks = ["A", "B", "C", "D"]
    operators = create_blocks_world_operators(blocks)
    print(f"  Generated {len(operators)} ground operators for {len(blocks)} blocks")

    # Initial: A on table, B on A, C on table, D on C
    initial = frozenset([
        Predicate("on", ("A", "table")),
        Predicate("on", ("B", "A")),
        Predicate("on", ("C", "table")),
        Predicate("on", ("D", "C")),
        Predicate("clear", ("B",)),
        Predicate("clear", ("D",)),
    ])

    # Goal: A on B, B on C, C on D, D on table
    goal = frozenset([
        Predicate("on", ("A", "B")),
        Predicate("on", ("B", "C")),
        Predicate("on", ("C", "D")),
        Predicate("on", ("D", "table")),
    ])

    print_state(initial, "Initial State")
    print(f"\n  Goal: A on B, B on C, C on D, D on table")

    print(f"\n  Planning...")
    plan = bfs_plan(initial, goal, operators, max_depth=10)

    if plan:
        print(f"\n  Plan ({len(plan)} steps):")
        state = initial
        for i, op in enumerate(plan, 1):
            state = op.apply(state)
            print(f"    {i}. {op}")
        print_state(state, "Final State")
    else:
        print("  No plan found!")
