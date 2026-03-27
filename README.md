# Agent Planning & Reasoning

How agents think before they act — classical planning (STRIPS/PDDL), hierarchical task networks, goal decomposition, and chain-of-thought reasoning for autonomous agents.

## Overview

Planning turns goals into action sequences. Reasoning allows agents to handle uncertainty, incomplete information, and adapt plans when the world changes.

```
    ┌─────────────────────────────────────────────────┐
    │                 Planning Pipeline                 │
    │                                                   │
    │  Goal ──> Decompose ──> Search ──> Plan ──> Act  │
    │                          │                        │
    │                    ┌─────┴──────┐                │
    │                    │  Operators  │                │
    │                    │ (actions +  │                │
    │                    │ preconditions│               │
    │                    │ + effects)  │                │
    │                    └────────────┘                 │
    │                                                   │
    │  Reasoning Layer:                                │
    │    Beliefs ──> Inference ──> Updated Beliefs     │
    │    Evidence ──> Rules ──> Conclusions            │
    └─────────────────────────────────────────────────┘
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **STRIPS Planning** | Classical planning with preconditions and effects |
| **HTN (Hierarchical Task Network)** | Decompose abstract tasks into primitive actions |
| **Forward/Backward Chaining** | Search from initial state forward or goal backward |
| **Goal Decomposition** | Break complex goals into manageable sub-goals |
| **Plan Repair** | Fix broken plans instead of replanning from scratch |
| **Chain-of-Thought** | Step-by-step reasoning for complex decisions |

## Examples

| File | Description |
|------|-------------|
| `01_strips_planner.py` | Classical STRIPS-style planner for a blocks world |
| `02_htn_planner.py` | Hierarchical task network for a cooking recipe domain |
| `03_chain_of_thought.py` | Chain-of-thought reasoning agent that shows its work |

## Best Practices

1. **Define clear state representations** — planning quality depends on good abstractions
2. **Keep operator libraries modular** — each action should have well-defined pre/post conditions
3. **Use hierarchical decomposition** for complex domains — flat planning doesn't scale
4. **Implement plan monitoring** — detect when a plan fails and trigger replanning
5. **Combine planning with learning** — learn which plans work and reuse them
6. **Add reasoning traces** — make agent thinking transparent for debugging

## References

- [Significant-Gravitas/AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) — Autonomous planning agent
- [yoheinakajima/babyagi](https://github.com/yoheinakajima/babyagi) — Task-driven autonomous agent
- [microsoft/autogen](https://github.com/microsoft/autogen) — Multi-agent conversation with planning
- [AIMA Python](https://github.com/aimacode/aima-python) — AI textbook planning algorithms
- [pyperplan](https://github.com/aibasel/pyperplan) — Lightweight PDDL planner

## License

MIT
