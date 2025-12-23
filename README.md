# Pacman Search & Adversarial Agents

This repository contains a collection of intelligent agents for the Pacman environment,
focusing on pathfinding and adversarial decision-making under strict real-time constraints.

The project explores how classical AI search and game-playing algorithms behave in
practice, and how targeted engineering optimisations can significantly improve
robustness, speed, and overall performance.

## Project Overview
The objective was to design an autonomous Pacman agent capable of maximising game
scores while maintaining survivability in a dynamic, multi-agent environment.

The agent transitions between:
- **Goal-oriented behaviour** (efficient food collection)
- **Adversarial behaviour** (anticipating and evading ghosts)

This is achieved through a custom decision-making pipeline that adapts its strategy
based on environmental risk and remaining resources.

## Core Capabilities
- **Adversarial Decision-Making:** Anticipates ghost behaviour using lookahead search.
- **Real-Time Optimisation:** Dynamically adapts search depth to respect per-move time limits.
- **Efficient Pathfinding:** Navigates complex mazes while avoiding traps and dead ends.

## Algorithms & Techniques

### Adversarial Search (Pacman vs Ghosts)
- **Minimax with Alpha–Beta Pruning** to evaluate future game states efficiently.
- **Custom Evaluation Function** incorporating:
  - Distance to food and capsules (via BFS)
  - Ghost proximity penalties
  - Incentives for engaging scared ghosts
  - Survival and movement encouragement terms

### Engineering Optimisations
To make adversarial search viable in real time, several optimisations were introduced:
- **Adaptive Search Depth:** Deeper search when threats are nearby, shallower search when safe.
- **Action Pre-Sorting:** Orders moves by a preliminary heuristic to improve pruning efficiency.
- **Branching Control:** Limits exploration to the top 3 candidate actions per state.
- **Oscillation Detection:** Identifies and breaks movement loops to avoid wasted computation.

### Pathfinding & Resource Collection
- **A\* Search:** Optimal pathfinding using the Manhattan distance heuristic.
- **Greedy Best-First Search (GBFS):** Rapid selection of high-value food targets.
- **Breadth-First Search (BFS):** Used selectively to compute true maze distances and validate reachability.

## Performance Highlights
- **High Survivability:** The final adversarial agent consistently outperformed baseline
  greedy strategies in survival time across multiple layouts.
- **Score Optimisation:** Achieved strong average scores on `originalClassic` and
  `capsuleClassic` by balancing aggressive collection with defensive positioning.
- **Runtime Stability:** Maintained decision latency within per-move time limits through
  pruning, adaptive depth, and action filtering.

## Key Learnings
- Heuristic quality and action ordering often matter more than deeper search.
- Adaptive strategies outperform fixed-depth policies in dynamic environments.
- Preventing pathological behaviours (loops, dead ends) is critical for real-time agents.
- Practical AI systems require careful trade-offs between optimality and predictability.

## Technical Stack
- **Language:** Python
- **Concepts:** State-Space Search, Heuristics, Game Theory, Multi-Agent Systems
