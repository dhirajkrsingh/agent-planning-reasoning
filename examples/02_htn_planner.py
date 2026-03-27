"""
Example 2: HTN (Hierarchical Task Network) Planner
=====================================================
Decomposes abstract tasks into primitive actions using methods.
Domain: A cooking assistant that plans meal preparation.

Run: python examples/02_htn_planner.py
"""


class HTNPlanner:
    """Hierarchical Task Network planner."""

    def __init__(self):
        self.methods = {}  # task_name -> list of (condition, subtasks) tuples
        self.operators = {}  # action_name -> (precond_fn, effect_fn)

    def add_method(self, task_name: str, condition, subtasks: list):
        """Register a decomposition method for a compound task."""
        if task_name not in self.methods:
            self.methods[task_name] = []
        self.methods[task_name].append((condition, subtasks))

    def add_operator(self, action_name: str, precondition, effect):
        """Register a primitive operator."""
        self.operators[action_name] = (precondition, effect)

    def plan(self, tasks: list, state: dict, depth: int = 0) -> list:
        """Recursively decompose and plan tasks."""
        if not tasks:
            return []

        task = tasks[0]
        remaining = tasks[1:]
        indent = "  " * (depth + 1)

        task_name = task[0] if isinstance(task, tuple) else task
        task_args = task[1:] if isinstance(task, tuple) else ()

        # Try as primitive operator
        if task_name in self.operators:
            precond, effect = self.operators[task_name]
            if precond(state, *task_args):
                new_state = dict(state)
                effect(new_state, *task_args)
                print(f"{indent}[EXECUTE] {task_name}({', '.join(str(a) for a in task_args)})")
                rest_plan = self.plan(remaining, new_state, depth)
                if rest_plan is not None:
                    return [(task_name, task_args)] + rest_plan
            return None

        # Try as compound task (decompose with methods)
        if task_name in self.methods:
            for condition, method_subtasks in self.methods[task_name]:
                if condition(state, *task_args):
                    subtasks = method_subtasks(state, *task_args) if callable(method_subtasks) else method_subtasks
                    print(f"{indent}[DECOMPOSE] {task_name} -> {len(subtasks)} subtasks")
                    result = self.plan(subtasks + remaining, state, depth + 1)
                    if result is not None:
                        return result

        print(f"{indent}[FAILED] Cannot plan for {task_name}")
        return None


def setup_cooking_domain():
    """Set up the cooking assistant HTN domain."""
    planner = HTNPlanner()

    # === Primitive Operators ===

    planner.add_operator("get_ingredient",
        precondition=lambda s, item: item in s.get("available", set()),
        effect=lambda s, item: s.setdefault("prepared", set()).add(item)
    )

    planner.add_operator("chop",
        precondition=lambda s, item: item in s.get("prepared", set()),
        effect=lambda s, item: (s.setdefault("chopped", set()).add(item))
    )

    planner.add_operator("heat_pan",
        precondition=lambda s: not s.get("pan_hot", False),
        effect=lambda s: s.update({"pan_hot": True})
    )

    planner.add_operator("add_oil",
        precondition=lambda s: s.get("pan_hot", False),
        effect=lambda s: s.update({"oil_added": True})
    )

    planner.add_operator("cook_item",
        precondition=lambda s, item: (item in s.get("chopped", set()) or item in s.get("prepared", set())) and s.get("oil_added", False),
        effect=lambda s, item: s.setdefault("cooked", set()).add(item)
    )

    planner.add_operator("season",
        precondition=lambda s, seasoning: True,
        effect=lambda s, seasoning: s.setdefault("seasonings", set()).add(seasoning)
    )

    planner.add_operator("plate_dish",
        precondition=lambda s: len(s.get("cooked", set())) > 0,
        effect=lambda s: s.update({"plated": True})
    )

    planner.add_operator("boil_water",
        precondition=lambda s: not s.get("water_boiling", False),
        effect=lambda s: s.update({"water_boiling": True})
    )

    planner.add_operator("cook_pasta",
        precondition=lambda s: s.get("water_boiling", False),
        effect=lambda s: s.setdefault("cooked", set()).add("pasta")
    )

    planner.add_operator("add_sauce",
        precondition=lambda s: "pasta" in s.get("cooked", set()),
        effect=lambda s: s.setdefault("cooked", set()).add("sauce")
    )

    # === Compound Methods ===

    # Make a stir fry
    planner.add_method("make_stir_fry",
        condition=lambda s: True,
        subtasks=lambda s: [
            ("prepare_vegetables",),
            ("prepare_pan",),
            ("stir_fry_cook",),
            ("finish_dish",),
        ]
    )

    # Prepare vegetables
    planner.add_method("prepare_vegetables",
        condition=lambda s: True,
        subtasks=lambda s: [
            ("get_ingredient", "onion"),
            ("get_ingredient", "pepper"),
            ("get_ingredient", "broccoli"),
            ("chop", "onion"),
            ("chop", "pepper"),
            ("chop", "broccoli"),
        ]
    )

    # Prepare pan
    planner.add_method("prepare_pan",
        condition=lambda s: not s.get("pan_hot", False),
        subtasks=[("heat_pan",), ("add_oil",)]
    )

    planner.add_method("prepare_pan",
        condition=lambda s: s.get("pan_hot", False) and not s.get("oil_added", False),
        subtasks=[("add_oil",)]
    )

    planner.add_method("prepare_pan",
        condition=lambda s: s.get("oil_added", False),
        subtasks=[]
    )

    # Stir fry cooking
    planner.add_method("stir_fry_cook",
        condition=lambda s: True,
        subtasks=lambda s: [
            ("cook_item", "onion"),
            ("cook_item", "pepper"),
            ("cook_item", "broccoli"),
            ("season", "soy_sauce"),
            ("season", "garlic"),
        ]
    )

    # Finish dish
    planner.add_method("finish_dish",
        condition=lambda s: True,
        subtasks=[("plate_dish",)]
    )

    # Make pasta
    planner.add_method("make_pasta",
        condition=lambda s: True,
        subtasks=lambda s: [
            ("boil_water",),
            ("cook_pasta",),
            ("add_sauce",),
            ("season", "basil"),
            ("plate_dish",),
        ]
    )

    # Make a full meal (compound)
    planner.add_method("make_meal",
        condition=lambda s: "pasta" in s.get("available", set()),
        subtasks=lambda s: [
            ("make_pasta",),
        ]
    )

    planner.add_method("make_meal",
        condition=lambda s: "onion" in s.get("available", set()),
        subtasks=lambda s: [
            ("make_stir_fry",),
        ]
    )

    return planner


if __name__ == "__main__":
    print("=== HTN Cooking Planner ===")

    planner = setup_cooking_domain()

    # Scenario 1: Stir fry
    print(f"\n{'='*50}")
    print("  Scenario 1: Make a Stir Fry")
    print(f"{'='*50}")

    state1 = {
        "available": {"onion", "pepper", "broccoli", "oil", "soy_sauce", "garlic"},
    }
    print(f"  Ingredients: {state1['available']}")
    plan1 = planner.plan([("make_stir_fry",)], state1)
    if plan1:
        print(f"\n  Plan ({len(plan1)} steps):")
        for i, (action, args) in enumerate(plan1, 1):
            print(f"    {i}. {action}({', '.join(str(a) for a in args)})")

    # Scenario 2: Pasta
    print(f"\n{'='*50}")
    print("  Scenario 2: Make Pasta")
    print(f"{'='*50}")

    state2 = {
        "available": {"pasta", "tomato_sauce", "basil"},
    }
    print(f"  Ingredients: {state2['available']}")
    plan2 = planner.plan([("make_pasta",)], state2)
    if plan2:
        print(f"\n  Plan ({len(plan2)} steps):")
        for i, (action, args) in enumerate(plan2, 1):
            print(f"    {i}. {action}({', '.join(str(a) for a in args)})")
