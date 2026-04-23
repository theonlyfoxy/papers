"""
Ouroboros Framework – Universe, Physics & Quantum Physics Edition
==================================================================
Demonstrates the root equation  s_{t+1} = s_t(s_t)  applied to a
toy quantum‑cosmological universe.  Shows emergence of:

  • superposition & measurement (collapse biased by observer free will)
  • entanglement & non‑local correlation
  • quantum foam (Planck‑scale noise)
  • black holes as information compressors, Hawking radiation
  • cosmic fine‑tuning & dark‑energy balancing
  • arrow of time from historical baseline

Author : MohammadReza Naeini, DeepSeek
Date   : 2026
"""

import numpy as np
from collections import deque
from typing import List, Tuple, Optional

# ============================================================================
# 1. Quantum tools – a single qubit or entangled pair
# ============================================================================
class Qubit:
    """ A two‑level quantum system represented by complex amplitudes. """
    def __init__(self, alpha: complex = 1+0j, beta: complex = 0j):
        norm = np.sqrt(abs(alpha)**2 + abs(beta)**2)
        self.alpha = alpha / norm
        self.beta  = beta  / norm

    def state_vector(self) -> np.ndarray:
        return np.array([self.alpha, self.beta])

    def probabilities(self) -> np.ndarray:
        return np.array([abs(self.alpha)**2, abs(self.beta)**2])

    def measure(self, bias: float = 0.0) -> int:
        """
        Collapse the qubit.  `bias` is a free‑will influence
        (-1 … +1) that shifts the outcome toward 0 (bias<0) or 1 (bias>0).
        """
        probs = self.probabilities()
        # apply a soft bias: move probability mass slightly
        shift = bias * 0.3  # max 30 % shift
        probs[0] = max(0.0, probs[0] + shift)
        probs[1] = max(0.0, probs[1] - shift)
        probs /= probs.sum()
        outcome = np.random.choice([0, 1], p=probs)
        # collapse
        if outcome == 0:
            self.alpha, self.beta = 1+0j, 0j
        else:
            self.alpha, self.beta = 0j, 1+0j
        return outcome


class EntangledPair:
    """ Bell state |00⟩ + |11⟩. """
    def __init__(self):
        self.alpha = 1/np.sqrt(2)
        self.beta  = 1/np.sqrt(2)
        self.qubits = (Qubit(1+0j,0j), Qubit(1+0j,0j))  # temporary
        self.collapsed = False

    def measure(self, which: int, bias: float = 0.0) -> int:
        """ Measure one qubit; the whole pair collapses. """
        if not self.collapsed:
            probs = np.array([abs(self.alpha)**2, abs(self.beta)**2])
            shift = bias * 0.3
            probs[0] = max(0.0, probs[0] + shift)
            probs[1] = max(0.0, probs[1] - shift)
            probs /= probs.sum()
            outcome = np.random.choice([0, 1], p=probs)
            if outcome == 0:
                # both |0⟩
                self.qubits[0].alpha, self.qubits[0].beta = 1, 0
                self.qubits[1].alpha, self.qubits[1].beta = 1, 0
            else:
                # both |1⟩
                self.qubits[0].alpha, self.qubits[0].beta = 0, 1
                self.qubits[1].alpha, self.qubits[1].beta = 0, 1
            self.collapsed = True
        return self.qubits[which].measure()  # already collapsed, no bias further


# ============================================================================
# 2. Universe state – contains quantum fields, geometry, history, etc.
# ============================================================================
class Universe:
    """
    The universal state vector s_t.  It contains:
      - fine‑structure constant alpha
      - dark‑energy parameter w
      - quantum foam amplitude (Planck noise)
      - black‑hole registry (list of black holes)
      - historical baseline for self‑evaluation
    """
    def __init__(self):
        # ----- fundamental 'constants' (evolvable) -----
        self.alpha_fine    = 1/137.036      # fine‑structure constant
        self.w_dark_energy = -1.0           # equation‑of‑state parameter (close to -1)

        # ----- spacetime fields -----
        self.expansion_rate = 0.07          # H0 in arbitrary units (scaled)

        # ----- quantum foam intensity -----
        self.foam_amplitude = 1e-5          # Planck‑scale noise level

        # ----- black holes list (each is a dict: mass, entropy, evaporating) -----
        self.black_holes: List[dict] = []

        # ----- historical baseline for key variables -----
        self.baseline = {k: deque(maxlen=100) for k in
                         ["alpha_fine", "w_dark_energy", "expansion_rate", "entropy"]}
        self.entropy = 1.0                 # a proxy for total cosmic entropy

        # ----- world model (simple linear predictor) -----
        self.world_model_weights = np.random.randn(3) * 0.01  # for predicting entropy

        # ----- circuit‑breaker engagement (alpha2) -----
        self.alpha2_engaged = 0.0

    def _update_baseline(self):
        """ Record current state into historical windows. """
        self.baseline["alpha_fine"].append(self.alpha_fine)
        self.baseline["w_dark_energy"].append(self.w_dark_energy)
        self.baseline["expansion_rate"].append(self.expansion_rate)
        self.baseline["entropy"].append(self.entropy)

    def _delta_surge(self, var: str) -> float:
        """ Ratio of current value to mean of recent history. """
        hist = self.baseline[var]
        if len(hist) < 5:
            return 1.0
        mean_val = np.mean(hist)
        if mean_val < 1e-12:
            return 1.0
        return getattr(self, var) / mean_val

    def _alpha2_update(self):
        """ Circuit breaker: if any critical ratio is extreme, block wild changes. """
        surges = [self._delta_surge(v) for v in ["alpha_fine", "expansion_rate"]]
        max_deviation = max(abs(s-1.0) for s in surges)
        self.alpha2_engaged = min(1.0, max_deviation / 0.5)

    def _apply_quantum_foam(self):
        """ Tiny random fluctuations in spacetime fields (virtual particles). """
        self.alpha_fine    += np.random.normal(0, self.foam_amplitude)
        self.w_dark_energy += np.random.normal(0, self.foam_amplitude * 0.1)
        # Keep within sensible bounds
        self.alpha_fine    = max(0.001, self.alpha_fine)
        self.w_dark_energy = max(-1.5, min(-0.5, self.w_dark_energy))

    def _update_black_holes(self):
        """ Hawking radiation: evaporate a tiny fraction of each black hole. """
        for bh in self.black_holes:
            if bh["evaporating"]:
                # mass loss ~ 1/mass^2
                dm = 0.001 / (bh["mass"]**2 + 0.1)
                bh["mass"] -= dm
                bh["entropy"] = bh["mass"] ** 2  # simplified Bekenstein‑Hawking
                if bh["mass"] <= 0.01:
                    self.black_holes.remove(bh)

    def apply_to_self(self, create_black_hole: bool = False) -> "Universe":
        """
        The root equation: s_{t+1} = s_t(s_t).
        We simulate the universe evaluating itself and modifying its own laws.
        Returns a new Universe instance (deep copy) as the next state.
        """
        new = Universe.__new__(Universe)
        new.__dict__ = {k: v for k, v in self.__dict__.items()}
        # deep copy mutable structures
        new.baseline = {k: deque(v, maxlen=100) for k, v in self.baseline.items()}
        new.black_holes = [bh.copy() for bh in self.black_holes]
        new.world_model_weights = self.world_model_weights.copy()

        # --- 1. Record history ---
        new._update_baseline()

        # --- 2. Quantum foam noise ---
        new._apply_quantum_foam()

        # --- 3. Compute delta‑surges and circuit breaker ---
        new._alpha2_update()

        # --- 4. Self‑modification of constants (gradient descent) ---
        # If expansion is too fast (dilution), reduce w slightly.
        if not new.alpha2_engaged:
            delta_exp = new._delta_surge("expansion_rate")
            if delta_exp > 1.1:   # expanding too fast relative to history
                new.w_dark_energy += 0.001   # make it more negative (slower)
            elif delta_exp < 0.9: # too slow
                new.w_dark_energy -= 0.001
            # Keep w bounded
            new.w_dark_energy = max(-1.5, min(-0.5, new.w_dark_energy))

            # Fine‑tune alpha: if entropy grows too fast, tweak alpha slightly.
            delta_entropy = new._delta_surge("entropy")
            if delta_entropy > 1.05:
                new.alpha_fine -= 0.0001   # slow down complexity loss
            elif delta_entropy < 0.95:
                new.alpha_fine += 0.0001

        # --- 5. Expansion update ---
        # The expansion rate responds to w (a simplistic Friedmann‑like equation)
        new.expansion_rate += -0.01 * (new.w_dark_energy + 1.0)
        new.expansion_rate = max(0.01, new.expansion_rate)

        # --- 6. Entropy evolution ---
        # Entropy increases with expansion but black holes store information.
        new.entropy += 0.02 * new.expansion_rate
        # Black holes reduce entropy growth (information preservation)
        total_bh_mass = sum(bh["mass"] for bh in new.black_holes)
        new.entropy -= 0.05 * total_bh_mass
        new.entropy = max(0.01, new.entropy)

        # --- 7. Black hole physics ---
        new._update_black_holes()

        # --- 8. World model update (simple gradient descent) ---
        # The universe tries to predict its own entropy.
        features = np.array([new.expansion_rate, new.w_dark_energy, new.alpha_fine])
        predicted_entropy = np.dot(features, new.world_model_weights)
        error = new.entropy - predicted_entropy
        new.world_model_weights += 0.01 * error * features

        # --- 9. Optionally create a black hole (demo) ---
        if create_black_hole:
            new.black_holes.append({"mass": 10.0, "entropy": 100.0, "evaporating": True})

        return new


# ============================================================================
# 3. Observer – a recursive agent that can measure quantum systems
# ============================================================================
class Observer:
    """
    Represents a conscious (recursive) observer with internal variables
    and a self‑modifying core.  Its free will influences quantum collapse.
    """
    def __init__(self, name: str):
        self.name = name
        # Internal variables (0‑1)
        self.vars = {
            "threat": 0.2,
            "coherence": 0.8,
            "goal_progress": 0.5,
            "energy": 0.9
        }
        # Core decision weights (self‑modifiable)
        self.core_weights = np.random.randn(4, 2) * 0.1
        # Historical baseline for delta‑surge
        self.baseline = {k: deque(maxlen=50) for k in self.vars}
        self.alpha2 = 0.0

    def _state_vec(self) -> np.ndarray:
        return np.array([self.vars[k] for k in self.vars])

    def _compute_delta(self) -> np.ndarray:
        curr = self._state_vec()
        means = np.array([np.mean(self.baseline[k]) if self.baseline[k] else 0.5 for k in self.vars])
        means = np.where(means < 0.001, 0.001, means)
        return curr / means

    def update(self):
        """ Apply self‑modification loop s_{t+1} = s_t(s_t) at the observer scale. """
        # record current state
        for k, v in self.vars.items():
            self.baseline[k].append(v)

        delta = self._compute_delta()
        # circuit breaker
        max_delta = max(abs(d-1.0) for d in delta)
        self.alpha2 = min(1.0, max_delta / 0.5)

        # self‑modify core weights if delta high and breaker not engaged
        if self.alpha2 < 0.5:
            if delta[0] > 2.0:  # threat spike
                self.core_weights[0, 0] += 0.1   # increase bias toward safe action
            if delta[1] < 0.5:  # coherence drop
                self.core_weights[1, 1] += 0.1   # boost exploration

    def measure_bias(self) -> float:
        """ Return a bias in [-1, 1] based on internal state for quantum collapse. """
        # A simple heuristic: high threat favours outcome 0 (safer), high goal_progress favours 1.
        threat = self.vars["threat"]
        goal = self.vars["goal_progress"]
        return (goal - threat) * 0.8  # roughly in [-1, 1]


# ============================================================================
# 4. Demonstrations
# ============================================================================

def demo_superposition_and_measurement():
    print("=" * 70)
    print("DEMO 1: Superposition & Observer‑Biased Collapse")
    print("=" * 70)
    q = Qubit(1/np.sqrt(2), 1/np.sqrt(2))
    obs = Observer("Alice")
    print(f"Initial qubit state: |0⟩ coeff={q.alpha:.3f}, |1⟩ coeff={q.beta:.3f}")
    print(f"Probabilities: {np.round(q.probabilities(), 3)}")
    # Observer's internal state influences collapse
    print(f"Observer threat={obs.vars['threat']}, goal={obs.vars['goal_progress']}")
    bias = obs.measure_bias()
    print(f"Observer bias (from free will): {bias:.2f}")
    outcome = q.measure(bias=bias)
    print(f"Collapsed to |{outcome}⟩")
    print("  ↳ The outcome was not purely random; it was tilted by the observer's volition.\n")


def demo_entanglement():
    print("=" * 70)
    print("DEMO 2: Entanglement – Non‑local Correlation")
    print("=" * 70)
    pair = EntangledPair()
    obs1 = Observer("Bob")
    obs2 = Observer("Carol")
    # Measure first qubit with observer Bob's bias
    bias1 = obs1.measure_bias()
    out1 = pair.measure(0, bias=bias1)
    out2 = pair.measure(1)  # now collapsed, second bias is irrelevant
    print(f"Bob measures qubit A → |{out1}⟩")
    print(f"Carol measures qubit B → |{out2}⟩ (same outcome, instant correlation)")
    print("  ↳ The correlation is a property of the unified state vector, not a signal.\n")


def demo_quantum_foam():
    print("=" * 70)
    print("DEMO 3: Quantum Foam – Planck‑Scale Noise")
    print("=" * 70)
    universe = Universe()
    print(f"Before foam: α={universe.alpha_fine:.6f}, w={universe.w_dark_energy:.6f}")
    for _ in range(10):
        universe._apply_quantum_foam()
    print(f"After 10 foam events: α={universe.alpha_fine:.6f}, w={universe.w_dark_energy:.6f}")
    print("  ↳ Tiny, irreducible fluctuations—the loop's creative probes.\n")


def demo_black_hole_lifecycle():
    print("=" * 70)
    print("DEMO 4: Black Hole – Compression & Hawking Evaporation")
    print("=" * 70)
    u = Universe()
    print("Initial black holes:", u.black_holes)
    # create a black hole
    u = u.apply_to_self(create_black_hole=True)
    print("After creation:", u.black_holes)
    # evaporate for many steps
    for i in range(50):
        u = u.apply_to_self()
    print("After evaporation steps:", u.black_holes)
    print("  ↳ Black holes store information; Hawking radiation slowly releases it.\n")


def demo_cosmic_evolution():
    print("=" * 70)
    print("DEMO 5: Cosmic Fine‑Tuning & Dark Energy Balancing")
    print("=" * 70)
    u = Universe()
    print(f"Initial constants: α={u.alpha_fine:.4f}, w={u.w_dark_energy:.4f}, H={u.expansion_rate:.4f}")
    # Run many iterations to see evolution
    for epoch in range(200):
        u = u.apply_to_self()
        if epoch % 40 == 0:
            print(f"  epoch {epoch}: α={u.alpha_fine:.4f}, w={u.w_dark_energy:.4f}, H={u.expansion_rate:.4f}, entropy={u.entropy:.3f}")
    print("  ↳ The universe tunes its own constants to balance structure vs. dilution.\n")


def demo_observer_free_will_and_wavefunction():
    print("=" * 70)
    print("DEMO 6: Free Will Shapes Quantum Reality")
    print("=" * 70)
    # Show that an observer with different internal states collapses differently.
    q = Qubit(1/np.sqrt(2), 1/np.sqrt(2))
    obs_neutral = Observer("Neutral")
    obs_fearful = Observer("Fearful")
    obs_fearful.vars["threat"] = 0.95
    obs_fearful.update()

    # set a fixed random seed to compare fairly
    np.random.seed(42)
    outcome_neutral = q.measure(bias=obs_neutral.measure_bias())
    np.random.seed(42)  # same initial quantum state, same random stream
    q2 = Qubit(1/np.sqrt(2), 1/np.sqrt(2))  # fresh identical qubit
    outcome_fearful = q2.measure(bias=obs_fearful.measure_bias())
    print(f"Neutral observer: outcome = |{outcome_neutral}⟩")
    print(f"Fearful observer: outcome = |{outcome_fearful}⟩")
    print("  ↳ Different internal states bias the universe's choice during collapse.\n")


if __name__ == "__main__":
    demo_superposition_and_measurement()
    demo_entanglement()
    demo_quantum_foam()
    demo_black_hole_lifecycle()
    demo_cosmic_evolution()
    demo_observer_free_will_and_wavefunction()
    print("All demonstrations complete – the Ouroboros loop in physical action.")
