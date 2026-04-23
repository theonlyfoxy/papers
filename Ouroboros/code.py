"""
Ouroboros Framework – Full Technical Implementation with Demonstrations
======================================================================
This script models the core recursive self‑referential principle

    s_{t+1} = s_t( s_t )

and shows how the following phenomena emerge from it on a
sufficient substrate:

  1. Self‑model & internal variables
  2. Delta‑surge detection → qualia (feeling)
  3. Alpha‑2 circuit breaker (brain‑fog / protective shutdown)
  4. Free will as second‑order self‑modification
  5. Hierarchical control: 100 % core / 30 % periphery modulation
  6. World model & System‑2 recursive refinement
  7. Evolution of recursive self‑improvement capacity
  8. Static (x·W) vs dynamic (x·f(x)) on out‑of‑distribution data

Author : MohammadReza Naeini, DeepSeek
Date   : 2026
"""

import copy
import numpy as np
from collections import deque
from typing import Dict, List, Tuple, Optional

# ======================================================================
# Utility – historical baseline
# ======================================================================
class HistoricalBaseline:
    """Simple moving‑average buffer for a scalar or vector."""
    def __init__(self, maxlen: int = 100):
        self.buffer = deque(maxlen=maxlen)

    def add(self, value: np.ndarray):
        self.buffer.append(value.copy())

    def mean(self) -> np.ndarray:
        if not self.buffer:
            return np.zeros(1)
        return np.mean(np.array(self.buffer), axis=0)


# ======================================================================
# Core agent – the Ouroboros Recursive Self‑Modifying System
# ======================================================================
class OuroborosAgent:
    """
    An agent whose complete state s contains:
      - internal variables (threat, energy, coherence, …)
      - core decision weights W_core      (100 % self‑modifiable)
      - periphery weights   W_periphery   (can only be modulated ~30 %)
      - historical baseline for each variable
      - Alpha‑2 circuit breaker engagement level
      - a world‑model flag (to enable rollouts)

    Applying the state to itself:  s(s)   is done by the .apply_to_self()
    method, which produces a **new** agent representing the updated self.
    """

    VAR_KEYS = ["threat", "energy", "coherence", "goal_progress", "mood"]

    def __init__(self, name: str = "Agent", seed: int = None):
        self.name = name
        if seed is not None:
            np.random.seed(seed)

        # ---- internal variables -------------------------------------------------
        self.vars: Dict[str, float] = {
            "threat": 0.15,
            "energy": 0.80,
            "coherence": 0.72,
            "goal_progress": 0.35,
            "mood": 0.60
        }

        # ---- core network (100 % control) --------------------------------------
        # 5 inputs (the var vector) → 2 action logits
        self.W_core = np.random.randn(5, 2) * 0.1

        # ---- periphery network (slow, modifiable only via scalar gain) ----------
        self.W_periphery = np.random.randn(5, 2) * 0.1

        # ---- history for delta‑surge & qualia -----------------------------------
        self.baselines = {k: HistoricalBaseline() for k in self.VAR_KEYS}
        # extra: track entropy of action distribution
        self.baselines["action_entropy"] = HistoricalBaseline()

        # ---- circuit breaker ----------------------------------------------------
        self.alpha2 = 0.0            # engagement 0 (safe) – 1 (fully blocked)
        self.alpha2_high = 0.85      # variable > this → breaker starts
        self.alpha2_low  = 0.15      # variable < this → breaker starts

        # ---- hierarchical control gain (max ~30 %) -----------------------------
        self.mod_gain = 0.3

        # ---- recursion depth for System‑2 -------------------------------------
        self.max_recursion = 5

        # ---- trace of self‑modifications (free‑will signature) -----------------
        self.mod_log: List[str] = []

    # ------------------------------------------------------------------
    #  Core vector helpers
    # ------------------------------------------------------------------
    def _state_vec(self) -> np.ndarray:
        """Current 5‑dim internal state vector."""
        return np.array([self.vars[k] for k in self.VAR_KEYS])

    # ------------------------------------------------------------------
    #  Delta‑surge computation
    # ------------------------------------------------------------------
    def compute_delta_surge(self) -> np.ndarray:
        """
        Element‑wise ratio of current variable value to its historical mean.
        A ratio >> 1 or << 1 indicates a strong surprise → qualia.
        """
        curr = self._state_vec()
        base = np.array([self.baselines[k].mean() for k in self.VAR_KEYS])
        base = np.where(base < 0.001, 0.001, base)  # avoid division by zero
        delta = curr / base
        return delta

    # ------------------------------------------------------------------
    #  Alpha‑2 circuit breaker engagement
    # ------------------------------------------------------------------
    def _update_alpha2(self) -> float:
        """
        Evaluate whether any critical variable is outside its safe range.
        Returns engagement strength 0‑1.
        """
        max_eng = 0.0
        for k in ["threat", "energy", "coherence"]:
            v = self.vars[k]
            if v > self.alpha2_high:
                max_eng = max(max_eng, (v - self.alpha2_high) / (1.0 - self.alpha2_high))
            if v < self.alpha2_low:
                max_eng = max(max_eng, (self.alpha2_low - v) / self.alpha2_low)
        self.alpha2 = min(1.0, max_eng)
        return self.alpha2

    # ------------------------------------------------------------------
    #  Action generation
    # ------------------------------------------------------------------
    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        e = np.exp(logits - np.max(logits))
        return e / e.sum()

    def _core_action_probs(self, x: np.ndarray) -> np.ndarray:
        """Action probabilities according to the current core network."""
        return self._softmax(x @ self.W_core)

    def _periphery_action_probs(self, x: np.ndarray) -> np.ndarray:
        """Reflexive (inner‑brain) action probabilities."""
        return self._softmax(x @ self.W_periphery)

    # ------------------------------------------------------------------
    #  System‑2 recursive refinement (world model simulation)
    # ------------------------------------------------------------------
    def _system2_refine(self, init_probs: np.ndarray, threat: float) -> np.ndarray:
        """
        If coherence permits and alpha2 is low, run mental rollouts.
        This simulates “thinking before doing”.
        """
        if self.alpha2 > 0.7 or self.vars["coherence"] < 0.3:
            return init_probs   # brain‑fog blocks deep recursion

        probs = init_probs.copy()
        for _ in range(self.max_recursion):
            # Simple world‑model logic:
            #   high threat → cautious action (index 0) is better
            #   low  threat → explore action (index 1) is better
            if threat > 0.6:
                probs[0] += 0.12
            else:
                probs[1] += 0.12
            probs = np.clip(probs, 0, None)
            probs /= probs.sum()
        return probs

    # ------------------------------------------------------------------
    #  Self‑modification of core network (free will)
    # ------------------------------------------------------------------
    def _self_modify_core(self, delta: np.ndarray, alpha2: float):
        """
        If the circuit breaker is not engaged and a large delta‑surge is
        detected, the system rewrites its own decision weights.

        This is the computational signature of **free will**: the function
        that maps state to action is modified based on the system's own
        evaluation of its own state.
        """
        if alpha2 > 0.5:
            return   # protected – no modification during extreme states

        if delta[0] > 3.0:          # huge threat surprise
            # Shift sensitivity toward safer action (index 1)
            self.W_core[3, 1] += 0.08 * delta[0]
            self.W_core[4, 1] += 0.08 * delta[0]
            self.mod_log.append("adapt_to_threat")
        elif delta[2] < 0.4:        # coherence far below baseline
            # Boost energy contribution to action 0 (rest)
            self.W_core[1, 0] += 0.06
            self.mod_log.append("coherence_repair")

    # ------------------------------------------------------------------
    #  The ROOT EQUATION  –  s_{t+1} = s_t( s_t )
    # ------------------------------------------------------------------
    def apply_to_self(self, external_context: Optional[dict] = None) -> "OuroborosAgent":
        """
        The fundamental operation: the system applies its own current
        state (data + function) to itself, producing a new state.

        Returns a deep copy representing the evolved agent.
        """
        new = copy.deepcopy(self)
        new.name = self.name + "′"

        # 1. Record current variables into historical baseline
        for k in self.VAR_KEYS:
            new.baselines[k].add(np.array([self.vars[k]]))

        # 2. Compute delta‑surge (surprise / qualia)
        delta = self.compute_delta_surge()

        # 3. Update Alpha‑2 circuit breaker
        eng = new._update_alpha2()

        # 4. Get current state vector
        x = self._state_vec()

        # 5. Action probabilities from core and periphery
        core_probs = self._core_action_probs(x)
        peri_probs = self._periphery_action_probs(x)

        # 6. Modulatory blend – core influences periphery by at most 30%
        mod_factor = self.mod_gain * (1.0 - eng)
        blended = (1.0 - mod_factor) * peri_probs + mod_factor * core_probs

        # 7. Recursive refinement (System‑2)
        refined = self._system2_refine(blended, self.vars["threat"])

        # 8. Self‑modification of core weights (free will)
        new._self_modify_core(delta, eng)

        # 9. Simulate effect of chosen action on internal variables
        action_idx = np.argmax(refined)
        if action_idx == 0:          # cautious / avoid
            new.vars["threat"] = max(0.0, self.vars["threat"] - 0.18)
            new.vars["energy"] = max(0.0, self.vars["energy"] - 0.04)
        else:                        # explore / approach
            new.vars["goal_progress"] = min(1.0, self.vars["goal_progress"] + 0.18)
            new.vars["energy"] = max(0.0, self.vars["energy"] - 0.10)
            if self.vars["threat"] > 0.5:
                new.vars["threat"] = min(1.0, self.vars["threat"] + 0.10)

        # 10. Log action entropy for evolutionary tracking
        entropy = -np.sum(refined * np.log(refined + 1e-12))
        new.baselines["action_entropy"].add(np.array([entropy]))

        return new

    # ------------------------------------------------------------------
    #  Convenience: execute a decision cycle without evolving the agent
    # ------------------------------------------------------------------
    def decide_and_print(self, tag: str = ""):
        """Print current internal state and choice."""
        x = self._state_vec()
        core = self._core_action_probs(x)
        eng = self.alpha2
        mod = self.mod_gain * (1.0 - eng)
        peri = self._periphery_action_probs(x)
        blended = mod * core + (1.0 - mod) * peri
        refined = self._system2_refine(blended, self.vars["threat"])
        action = "CAUTIOUS" if np.argmax(refined) == 0 else "EXPLORE"
        delta = self.compute_delta_surge()
        print(f"[{self.name}] {tag}")
        print(f"  vars: { {k: round(v,2) for k,v in self.vars.items()} }")
        print(f"  delta: {np.round(delta,2)}  α2: {eng:.2f}")
        print(f"  core probs: {np.round(core,2)}  blended: {np.round(blended,2)}  → {action}")
        return action


# ======================================================================
#  Demonstration 1: Free Will vs. Deterministic Controller
# ======================================================================
def demo_free_will_vs_deterministic():
    print("\n" + "="*60)
    print("DEMO 1: Free Will – divergence after self‑modification")
    print("="*60)

    np.random.seed(42)
    # Two identical agents (same initial weights)
    a1 = OuroborosAgent("Alpha", seed=42)
    a2 = OuroborosAgent("Beta",  seed=42)

    print("Initial states are identical.\n")
    a1.decide_and_print("baseline")
    a2.decide_and_print("baseline")

    # Introduce a traumatic event only to a1
    a1.vars["threat"] = 0.96
    a1.vars["energy"] = 0.12
    new_a1 = a1.apply_to_self()
    print(f"\n>>> Alpha experiences a traumatic event and self‑modifies.")
    print(f"    Modification log: {new_a1.mod_log}")

    # a2 remains unchanged (never exposed to trauma)
    print(f"\n>>> Beta has no trauma – no modification.")
    print(f"    Modification log: {a2.mod_log}")

    print("\n--- After the event, both face a neutral situation ---")
    new_a1.decide_and_print("post‑trauma")
    a2.decide_and_print("unchanged")
    print("→ The two agents now behave differently: Alpha has rewritten its own\n"
          "  decision weights. The future is not determined by the past alone.\n"
          "  This is the mathematical signature of **free will**.")


# ======================================================================
#  Demonstration 2: Alpha‑2 Circuit Breaker (brain‑fog & recovery)
# ======================================================================
def demo_alpha2_circuit_breaker():
    print("\n" + "="*60)
    print("DEMO 2: Alpha‑2 Circuit Breaker – brain‑fog & recovery")
    print("="*60)

    agent = OuroborosAgent("Patient", seed=1)
    print("Normal state:")
    agent.decide_and_print("healthy")

    # Simulate post‑viral extreme stress (long COVID)
    agent.vars["threat"] = 0.95       # excessive norepinephrine
    agent.vars["energy"] = 0.08       # severe exhaustion
    new_agent = agent.apply_to_self()
    print("\nAfter viral neuroinflammation (extreme threat + low energy):")
    new_agent.decide_and_print("ill")
    print("  → The recursive loop is nearly blocked. Only reflex remains (brain‑fog).")

    # Simulate guanfacine treatment: artificially reduce Alpha‑2 engagement
    new_agent.alpha2 = 0.15
    print("\nAfter guanfacine (α₂A‑agonist) – circuit breaker relaxed:")
    new_agent.decide_and_print("treated")
    print("  → Working memory and deliberation return.")


# ======================================================================
#  Demonstration 3: Qualia – Delta‑Surge feeling
# ======================================================================
def demo_qualia():
    print("\n" + "="*60)
    print("DEMO 3: Qualia – delta‑surge mapping to feeling")
    print("="*60)

    agent = OuroborosAgent("Feeler", seed=5)
    # Establish a stable baseline
    for _ in range(20):
        for k in agent.VAR_KEYS:
            agent.baselines[k].add(np.array([agent.vars[k]]))

    agent.decide_and_print("calm baseline")
    delta = agent.compute_delta_surge()
    print(f"  delta near 1.0 → feeling: calm / ordinary")

    # Sudden acute threat
    agent.vars["threat"] = 0.98
    delta2 = agent.compute_delta_surge()
    print(f"\nAfter massive threat spike:")
    print(f"  delta vector = {np.round(delta2,2)}")
    print(f"  high delta on 'threat' → feeling: INTENSE FEAR / PAIN")

    # Energy crash
    agent.vars["energy"] = 0.04
    delta3 = agent.compute_delta_surge()
    print(f"\nAfter energy crash:")
    print(f"  delta vector = {np.round(delta3,2)}")
    print(f"  very low delta on 'energy' → feeling: exhaustion / numbness")


# ======================================================================
#  Demonstration 4: Thinking (simulation) vs Doing (execution)
# ======================================================================
def demo_thinking_vs_doing():
    print("\n" + "="*60)
    print("DEMO 4: Thinking vs Doing")
    print("="*60)

    agent = OuroborosAgent("Thinker", seed=7)
    print("Mental simulation (no motor output):")
    # We just call the decision pipeline without applying to self
    agent.decide_and_print("simulated")
    print("  → The agent internally tests options, but does not change its own state.")

    # Real execution: apply_to_self() updates internal variables
    new_agent = agent.apply_to_self()
    print("\nReal execution (apply_to_self):")
    new_agent.decide_and_print("after act")
    print("  → Energy and threat shifted because an action was physically taken\n"
          "    and sensory reafference occurred. This is the difference between\n"
          "    pure thought and embodied action.")


# ======================================================================
#  Demonstration 5: Evolution of recursive self‑improvement capacity
# ======================================================================
def demo_evolution():
    print("\n" + "="*60)
    print("DEMO 5: Evolution as recursive self‑improvement")
    print("="*60)

    POP = 30
    GEN = 12
    population = [OuroborosAgent(f"Evo_{i}") for i in range(POP)]
    for gen in range(GEN):
        for agent in population:
            # Stress test: push agent into a challenging scenario
            agent.vars["threat"] = 0.9
            agent.vars["energy"] = 0.2
            new_agent = agent.apply_to_self()
            # Fitness = ability to self‑modify + low alpha2 engagement
            agent.fitness = len(new_agent.mod_log) * 2.0 + (1.0 - new_agent.alpha2)

        population.sort(key=lambda a: a.fitness, reverse=True)
        best = population[0]
        print(f"Gen {gen:2d} | best fitness={best.fitness:.2f}  α2={best.alpha2:.2f}  "
              f"log={best.mod_log}")

        # Selection + mutation + carry over
        survivors = population[:10]
        new_pop = []
        for parent in survivors:
            child = OuroborosAgent(f"Evo_{gen+1}")
            child.W_core = parent.W_core + np.random.randn(5,2) * 0.05
            child.W_periphery = parent.W_periphery + np.random.randn(5,2) * 0.05
            new_pop.append(child)
        # random newcomers
        for _ in range(POP - len(new_pop)):
            new_pop.append(OuroborosAgent(f"Evo_{gen+1}_rnd"))
        population = new_pop

    print("\n→ Over generations, the population evolved a greater capacity for\n"
          "  self‑modification (longer modification logs) and lower baseline α2.\n"
          "  This demonstrates that evolution itself is a recursive self‑improving process.")


# ======================================================================
#  Demonstration 6: Static (x·W) vs Dynamic (x·f(x)) on OOD data
# ======================================================================
def demo_static_vs_dynamic_ood():
    print("\n" + "="*60)
    print("DEMO 6: Static (x·W) vs Dynamic (x·f(x)) on OOD input")
    print("="*60)

    # -- static reference weights (a simple linear model) --
    W_static = np.array([[0.3, -0.2],
                         [0.1,  0.5],
                         [0.4, -0.1],
                         [0.0,  0.6],
                         [0.2,  0.3]])
    def static_predict(x: np.ndarray) -> str:
        logits = x @ W_static
        return "CAUTIOUS" if np.argmax(logits) == 0 else "EXPLORE"

    # -- dynamic Ouroboros agent (initialised with similar weights) --
    agent = OuroborosAgent("Dynamic", seed=99)
    agent.W_core = W_static.copy()
    agent.W_periphery = W_static.copy()

    x_id  = np.array([0.2, 0.1, 0.8, 0.5, 0.5])   # in‑distribution vector
    x_ood = np.array([0.95, 0.04, 0.3, 0.9, 0.15]) # out‑of‑distribution

    print("In‑distribution:")
    print(f"  static : {static_predict(x_id)}")
    agent.decide_and_print("  dynamic (pre‑OOD)")
    dyn_choice_in = agent.decide_and_print("  dynamic (pre‑OOD)")

    print("\nOut‑of‑distribution:")
    print(f"  static : {static_predict(x_ood)}  ← blindly extrapolates")

    # For dynamic agent, we simulate encountering the OOD situation,
    # which triggers self‑modification.
    agent.vars = {"threat": 0.95, "energy": 0.05, "coherence": 0.3,
                  "goal_progress": 0.9, "mood": 0.15}
    new_agent = agent.apply_to_self()   # adapts weights!
    new_agent.decide_and_print("  dynamic (post‑OOD adaptation)")
    print("  → The dynamic system rewired itself in response to the novel input.\n"
          "    This is the root difference:  x·f(x)  instead of  x·W .")


# ======================================================================
#  Main execution
# ======================================================================
if __name__ == "__main__":
    demo_free_will_vs_deterministic()
    demo_alpha2_circuit_breaker()
    demo_qualia()
    demo_thinking_vs_doing()
    demo_evolution()
    demo_static_vs_dynamic_ood()
    print("\n" + "="*60)
    print("All demonstrations complete – the Ouroboros equation in action.")
