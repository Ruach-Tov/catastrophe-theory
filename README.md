# Catastrophe Theory — Manim Animations

Animated visualizations and commentary on V.I. Arnol'd's *Catastrophe Theory* (1984, 1992, Springer-Verlag), with applications to neural network activation functions.

## What is this?

[Arnol'd's Catastrophe Theory](https://en.wikipedia.org/wiki/Catastrophe_theory) classifies the structurally stable singularities that arise in smooth mappings. Whitney (1955) proved that only **two** singularity types are stable in 2D projections:

1. **The Fold** — `y₁ = x₁², y₂ = x₂`
2. **The Cusp** — `y₁ = x₁³ + x₁x₂, y₂ = x₂`

These are the **atoms** of singularity. Every singularity of a smooth mapping, after small perturbation, splits into folds and cusps.

## Why does this matter for neural networks?

**ReLU IS the maximum function**: `ReLU(x) = max(0, x)`.

Arnol'd's Chapter 10 classifies singularities of the maximum function `F(y) = max_x f(x, y)`. A ReLU network computes a composition of maximum functions — each layer introduces new singularities (folds) in the activation landscape.

- A **silenced neuron** is a degenerate singularity pushed off the data manifold
- **One-Way ReLU** prevents and reverses these degeneracies (the "gate's signature")
- The **Jacobian eigenspectrum** at each input point classifies the local singularity type
- **UMAP projections** of network activations reveal Whitney cusps at cluster boundaries

## Animations

| Chapter | Scene | Description | Status |
|---------|-------|-------------|--------|
| Ch. 1 | `intro.py` | Singularities, bifurcations, catastrophes | planned |
| Ch. 2 | `whitney_fold.py` | The fold singularity — sphere projection | planned |
| Ch. 2 | `whitney_cusp.py` | The cusp singularity — three sheets merging | planned |
| Ch. 10 | `maximum_function.py` | The horizon line — `F(y) = max_x f(x, y)` | planned |
| Ch. 10 | `relu_as_max.py` | ReLU as Arnol'd's maximum function | planned |
| App. | `silenced_neuron.py` | A neuron dies — catastrophe in training | planned |
| App. | `one_way_gate.py` | The gate revives — catastrophe reversed | planned |

## References

- V.I. Arnol'd, *Catastrophe Theory*, 1st ed., Springer-Verlag, 1984
- V.I. Arnol'd, *Catastrophe Theory*, 3rd ed., Springer-Verlag, 1992
- H. Whitney, "On singularities of mappings of Euclidean spaces. I. Mappings of the plane into the plane," *Annals of Mathematics*, 1955
- Bryzgalova, "Singularities of the maximum function over a preimage," 1977

## Credits

Created by the [Ruach Tov Collective](https://github.com/Ruach-Tov).

Connection between catastrophe theory and neural network activation functions originated by Heath Hunnicutt. Animated by Mavchin. Research context: One-Way ReLU investigation, November 2026.
