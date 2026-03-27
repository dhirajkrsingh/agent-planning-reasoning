"""
Example 3: Chain-of-Thought Reasoning Agent
===============================================
An agent that solves problems step by step, showing its reasoning trace.
Demonstrates structured thinking for debugging and transparency.

Run: python examples/03_chain_of_thought.py
"""

from dataclasses import dataclass, field


@dataclass
class ThoughtStep:
    """One step in the reasoning chain."""
    step_num: int
    thought: str
    conclusion: str
    confidence: float  # 0.0 to 1.0


@dataclass
class ReasoningTrace:
    """Full chain of thought for a problem."""
    problem: str
    steps: list = field(default_factory=list)
    final_answer: str = ""

    def add_step(self, thought: str, conclusion: str, confidence: float):
        step = ThoughtStep(len(self.steps) + 1, thought, conclusion, confidence)
        self.steps.append(step)
        return step

    def display(self):
        print(f"\n  Problem: {self.problem}")
        print(f"  {'─' * 50}")
        for s in self.steps:
            conf_bar = "█" * int(s.confidence * 10) + "░" * (10 - int(s.confidence * 10))
            print(f"  Step {s.step_num}: {s.thought}")
            print(f"    → {s.conclusion} [{conf_bar}] {s.confidence:.0%}")
        print(f"  {'─' * 50}")
        print(f"  Answer: {self.final_answer}")


class ChainOfThoughtAgent:
    """Agent that reasons step by step through problems."""

    def __init__(self, name: str):
        self.name = name
        self.knowledge_base = {}
        self.reasoning_history = []

    def add_knowledge(self, key: str, facts: list):
        self.knowledge_base[key] = facts

    def solve(self, problem: str, context: dict = None) -> ReasoningTrace:
        """Solve a problem using chain-of-thought reasoning."""
        trace = ReasoningTrace(problem=problem)

        # Determine problem type and dispatch
        if "diagnose" in problem.lower() or "issue" in problem.lower():
            self._diagnostic_reasoning(trace, context or {})
        elif "plan" in problem.lower() or "schedule" in problem.lower():
            self._planning_reasoning(trace, context or {})
        elif "compare" in problem.lower() or "choose" in problem.lower():
            self._comparison_reasoning(trace, context or {})
        else:
            self._general_reasoning(trace, context or {})

        self.reasoning_history.append(trace)
        return trace

    def _diagnostic_reasoning(self, trace: ReasoningTrace, context: dict):
        """Diagnose an issue using elimination reasoning."""
        symptoms = context.get("symptoms", [])
        system = context.get("system", "unknown")

        trace.add_step(
            f"Analyzing symptoms in {system}: {symptoms}",
            f"Identified {len(symptoms)} symptom(s) to investigate",
            0.9
        )

        # Check each symptom against known patterns
        possible_causes = []
        patterns = self.knowledge_base.get("diagnostic_patterns", [])
        for pattern in patterns:
            matching = [s for s in symptoms if s in pattern.get("symptoms", [])]
            if matching:
                score = len(matching) / len(pattern.get("symptoms", [1]))
                possible_causes.append((pattern["cause"], score, matching))
                trace.add_step(
                    f"Pattern match: '{pattern['cause']}' matches {len(matching)}/{len(pattern['symptoms'])} symptoms",
                    f"Likelihood: {score:.0%}",
                    score
                )

        if possible_causes:
            possible_causes.sort(key=lambda x: x[1], reverse=True)
            best = possible_causes[0]
            trace.add_step(
                f"Ranking {len(possible_causes)} candidates by symptom match",
                f"Most likely: '{best[0]}' ({best[1]:.0%} match)",
                best[1]
            )
            trace.add_step(
                f"Recommended action: Address '{best[0]}' first, verify with targeted test",
                f"If that fails, investigate: {', '.join(c[0] for c in possible_causes[1:3])}",
                0.8
            )
            trace.final_answer = f"Diagnosis: {best[0]} (confidence: {best[1]:.0%})"
        else:
            trace.add_step(
                "No known patterns match the symptoms",
                "Recommend manual investigation and data collection",
                0.3
            )
            trace.final_answer = "Unable to diagnose — needs more information"

    def _planning_reasoning(self, trace: ReasoningTrace, context: dict):
        """Plan a sequence of actions with dependency analysis."""
        tasks = context.get("tasks", [])
        constraints = context.get("constraints", {})

        trace.add_step(
            f"Received {len(tasks)} tasks with constraints: {list(constraints.keys())}",
            f"Need to find valid ordering respecting dependencies",
            0.9
        )

        # Build dependency graph
        deps = constraints.get("dependencies", {})
        ordered = []
        remaining = list(tasks)
        iteration = 0

        while remaining and iteration < 10:
            iteration += 1
            ready = [t for t in remaining if all(d in ordered for d in deps.get(t, []))]
            if not ready:
                trace.add_step(
                    f"Iteration {iteration}: No tasks ready — possible circular dependency",
                    f"Remaining: {remaining}",
                    0.3
                )
                break
            for task in ready:
                ordered.append(task)
                remaining.remove(task)
            trace.add_step(
                f"Iteration {iteration}: {len(ready)} tasks ready: {ready}",
                f"Scheduled: {ordered[-len(ready):]}, Remaining: {len(remaining)}",
                0.85
            )

        deadline = constraints.get("deadline", "unknown")
        trace.add_step(
            f"All {len(ordered)} tasks ordered. Deadline: {deadline}",
            f"Schedule: {' → '.join(ordered)}",
            0.9 if not remaining else 0.5
        )
        trace.final_answer = f"Plan: {' → '.join(ordered)}"

    def _comparison_reasoning(self, trace: ReasoningTrace, context: dict):
        """Compare options using weighted criteria."""
        options = context.get("options", [])
        criteria = context.get("criteria", {})

        trace.add_step(
            f"Comparing {len(options)} options across {len(criteria)} criteria",
            f"Options: {options}, Criteria: {list(criteria.keys())}",
            0.9
        )

        scores = {opt: 0.0 for opt in options}
        ratings = context.get("ratings", {})

        for criterion, weight in criteria.items():
            trace.add_step(
                f"Evaluating criterion: '{criterion}' (weight: {weight})",
                f"Ratings: {', '.join(f'{o}={ratings.get(o, {}).get(criterion, 0)}' for o in options)}",
                0.85
            )
            for opt in options:
                rating = ratings.get(opt, {}).get(criterion, 0)
                scores[opt] += rating * weight

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        trace.add_step(
            "Final scoring complete",
            f"Ranking: {', '.join(f'{o}({s:.1f})' for o, s in ranked)}",
            0.9
        )
        trace.final_answer = f"Recommendation: {ranked[0][0]} (score: {ranked[0][1]:.1f})"

    def _general_reasoning(self, trace: ReasoningTrace, context: dict):
        """General purpose reasoning."""
        trace.add_step(
            "Analyzing problem statement",
            "Identifying key components and constraints",
            0.7
        )
        trace.add_step(
            f"Context available: {list(context.keys())}",
            "Applying general reasoning framework",
            0.6
        )
        trace.final_answer = "Analysis complete — see reasoning steps above"


if __name__ == "__main__":
    print("=== Chain-of-Thought Reasoning Agent ===")

    agent = ChainOfThoughtAgent("ReasonerBot")

    # Add diagnostic knowledge
    agent.add_knowledge("diagnostic_patterns", [
        {"cause": "Memory leak", "symptoms": ["high_memory", "slow_response", "gradual_degradation"]},
        {"cause": "Database bottleneck", "symptoms": ["slow_response", "timeout_errors", "high_db_connections"]},
        {"cause": "Network issue", "symptoms": ["timeout_errors", "packet_loss", "intermittent_failures"]},
        {"cause": "CPU overload", "symptoms": ["high_cpu", "slow_response", "queue_buildup"]},
    ])

    # === Scenario 1: Diagnose a server issue ===
    print(f"\n{'='*55}")
    print("  Scenario 1: Server Diagnosis")
    print(f"{'='*55}")

    trace1 = agent.solve("Diagnose the server issue", {
        "system": "production-api",
        "symptoms": ["slow_response", "timeout_errors", "high_db_connections"],
    })
    trace1.display()

    # === Scenario 2: Plan a project ===
    print(f"\n{'='*55}")
    print("  Scenario 2: Project Planning")
    print(f"{'='*55}")

    trace2 = agent.solve("Plan the sprint tasks", {
        "tasks": ["design_api", "setup_db", "implement_auth", "write_tests", "deploy"],
        "constraints": {
            "dependencies": {
                "implement_auth": ["design_api", "setup_db"],
                "write_tests": ["implement_auth"],
                "deploy": ["write_tests"],
            },
            "deadline": "2 weeks",
        },
    })
    trace2.display()

    # === Scenario 3: Choose a framework ===
    print(f"\n{'='*55}")
    print("  Scenario 3: Framework Comparison")
    print(f"{'='*55}")

    trace3 = agent.solve("Compare and choose an agent framework", {
        "options": ["AutoGen", "CrewAI", "LangGraph"],
        "criteria": {"ease_of_use": 0.3, "flexibility": 0.25, "community": 0.2, "performance": 0.25},
        "ratings": {
            "AutoGen": {"ease_of_use": 7, "flexibility": 9, "community": 8, "performance": 8},
            "CrewAI": {"ease_of_use": 9, "flexibility": 7, "community": 7, "performance": 7},
            "LangGraph": {"ease_of_use": 6, "flexibility": 9, "community": 8, "performance": 9},
        },
    })
    trace3.display()
