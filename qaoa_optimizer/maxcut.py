"""Small, exact state-vector QAOA simulator for weighted Max-Cut.

Bit i in an integer bitstring denotes vertex i. This is a classical simulation
of the standard |+> initial state, cost unitary exp(-i gamma C), and X mixer.
No quantum hardware is used. Complexity is O(layers * vertices * 2**vertices).
"""
from __future__ import annotations

import cmath
import math
from typing import Sequence

MAX_VERTICES = 9


def validate_graph(vertices: int, edges: Sequence[Sequence[float]]) -> list[tuple[int, int, float]]:
    if isinstance(vertices, bool) or not isinstance(vertices, int) or not 2 <= vertices <= MAX_VERTICES:
        raise ValueError(f"vertices must be an integer between 2 and {MAX_VERTICES}")
    if not isinstance(edges, (list, tuple)) or not edges:
        raise ValueError("edges must be a non-empty array of [u, v, weight] triples")
    normalized = []
    seen = set()
    for edge in edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 3:
            raise ValueError("each edge must contain exactly [u, v, weight]")
        u, v, weight = edge
        if any(isinstance(x, bool) or not isinstance(x, int) for x in (u, v)):
            raise ValueError("vertex indices must be integers")
        if not (0 <= u < vertices and 0 <= v < vertices) or u == v:
            raise ValueError("edge endpoints must be different vertices in range")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
            raise ValueError("edge weights must be finite and positive")
        key = (min(u, v), max(u, v))
        if key in seen:
            raise ValueError("duplicate undirected edge")
        seen.add(key)
        normalized.append((key[0], key[1], float(weight)))
    return normalized


def cut_values(vertices: int, edges: Sequence[Sequence[float]]) -> list[float]:
    normalized = validate_graph(vertices, edges)
    return [sum(w for u, v, w in normalized if ((mask >> u) ^ (mask >> v)) & 1)
            for mask in range(1 << vertices)]


def probabilities(costs: Sequence[float], gammas: Sequence[float], betas: Sequence[float]) -> list[float]:
    nstates = len(costs)
    if nstates < 4 or nstates & (nstates - 1):
        raise ValueError("costs must have a power-of-two length >= 4")
    if len(gammas) != len(betas) or not gammas or len(gammas) > 3:
        raise ValueError("provide 1 to 3 QAOA layers")
    if not all(math.isfinite(x) for x in (*gammas, *betas)):
        raise ValueError("angles must be finite")
    amplitudes = [complex(1 / math.sqrt(nstates)) for _ in range(nstates)]
    for gamma, beta in zip(gammas, betas):
        amplitudes = [a * cmath.exp(-1j * gamma * cost) for a, cost in zip(amplitudes, costs)]
        c, s = math.cos(beta), -1j * math.sin(beta)
        for bit in range(nstates.bit_length() - 1):
            step = 1 << bit
            for base in range(0, nstates, step * 2):
                for j in range(base, base + step):
                    a, b = amplitudes[j], amplitudes[j + step]
                    amplitudes[j] = c * a + s * b
                    amplitudes[j + step] = s * a + c * b
    return [abs(a) ** 2 for a in amplitudes]


def optimize_maxcut(vertices: int, edges: Sequence[Sequence[float]], layers: int = 1,
                    grid: int = 10) -> dict:
    costs = cut_values(vertices, edges)
    if isinstance(layers, bool) or not isinstance(layers, int) or not 1 <= layers <= 3:
        raise ValueError("layers must be between 1 and 3")
    if isinstance(grid, bool) or not isinstance(grid, int) or not 4 <= grid <= 24:
        raise ValueError("grid must be between 4 and 24")

    def evaluate(gammas, betas):
        probs = probabilities(costs, gammas, betas)
        return sum(p * c for p, c in zip(probs, costs))

    # Find the best p=1 grid point; zero-valued later layers embed a p=1 solution.
    best = (-math.inf, [0.0], [0.0])
    for gi in range(grid):
        for bi in range(grid):
            g = 2 * math.pi * gi / grid
            b = math.pi * bi / (2 * grid)
            score = evaluate([g], [b])
            if score > best[0]:
                best = (score, [g], [b])
    gammas = best[1] + [0.0] * (layers - 1)
    betas = best[2] + [0.0] * (layers - 1)
    score = best[0]
    delta_g, delta_b = 2 * math.pi / grid, math.pi / (2 * grid)
    # Bounded deterministic coordinate-search refinement, including later layers.
    for _ in range(10):
        for parameter, delta, period in ((gammas, delta_g, 2 * math.pi),
                                         (betas, delta_b, math.pi)):
            for layer in range(layers):
                original = parameter[layer]
                for step in (-delta, delta):
                    parameter[layer] = (original + step) % period
                    candidate = evaluate(gammas, betas)
                    if candidate > score + 1e-12:
                        score, original = candidate, parameter[layer]
                parameter[layer] = original
        delta_g /= 2
        delta_b /= 2

    probs = probabilities(costs, gammas, betas)
    likely = max(range(len(probs)), key=lambda i: probs[i])
    optimum = max(costs)
    optimal_masks = [i for i, value in enumerate(costs) if math.isclose(value, optimum, abs_tol=1e-9)]
    return {
        "vertices": vertices,
        "edges": [list(edge) for edge in validate_graph(vertices, edges)],
        "layers": layers,
        "gammas": gammas,
        "betas": betas,
        "expected_cut": score,
        "exact_optimum": optimum,
        "approximation_ratio": score / optimum if optimum else 1.0,
        "most_likely_bitstring": format(likely, f"0{vertices}b")[::-1],
        "most_likely_cut": costs[likely],
        "most_likely_probability": probs[likely],
        "optimal_bitstrings": [format(i, f"0{vertices}b")[::-1] for i in optimal_masks],
        "distribution": [
            {"bitstring": format(i, f"0{vertices}b")[::-1], "probability": probability, "cut": costs[i]}
            for i, probability in enumerate(probs)
        ],
        "simulator": "classical state-vector QAOA",
    }
