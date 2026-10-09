# Reinforcement Learning for Large Language Model Reasoning: A Comprehensive Survey

## TL;DR
- **Paradigm Evolution**: Reinforcement learning (RL) post-training bridges standard alignment techniques (PPO, DPO) and specialized reward mechanisms to drive advanced multi-step LLM reasoning [1][2].
- **Reward Modeling**: Transitioning from coarse Outcome Reward Models (ORMs) to fine-grained Process Reward Models (PRMs) enables stepwise verification and robust credit assignment during complex problem solving [3][4].
- **Test-Time Search & Planning**: Integrating structured search frameworks—such as Monte Carlo Tree Search (MCTS), on-policy tree search (TreeRL), and agentic turn-based optimization ($AT^2PO$)—dramatically enhances test-time scaling and reasoning depth [5][6][7].
- **Off-Policy Optimization & Stability**: Methods like Reshaped Sequence Policy Optimization (ReSPO) resolve gradient starvation and distribution mismatch when reusing rollouts in RL with verifiable rewards (RLVR) [8].
- **Empirical Frontiers & Limitations**: While frameworks like WizardMath push performance on mathematical benchmarks, evaluations like GSM-Symbolic and MATH-Beyond expose underlying fragility, distribution boundaries, and reward hacking challenges [9][10][11].

## Background
The rapid advancement of Large Language Models (LLMs) has transformed natural language understanding and generation, yet autonomous multi-step reasoning remains a critical frontier. While autoregressive generation via standard Chain-of-Thought (CoT) prompting elicits stepwise inference, static pre-training and standard supervised fine-tuning (SFT) often leave models prone to error propagation, logical inconsistencies, and unguided exploration. To overcome these bottlenecks, reinforcement learning (RL) post-training has emerged as the cornerstone for endowing LLMs with rigorous reasoning capabilities. 

Historically rooted in Reinforcement Learning from Human Feedback (RLHF) and optimization algorithms such as Proximal Policy Optimization (PPO) and Direct Preference Optimization (DPO), RL for reasoning shifts the objective from superficial stylistic alignment to verifiable problem-solving [1][2]. By incentivizing correct logical trajectories, penalizing non-sequiturs, and harnessing verifiable rewards (RLVR), RL enables models to explore alternative hypothesis spaces, self-correct, and scale computational inference dynamically at test time.

## Foundations and Core Optimization Algorithms
At the core of RL-driven reasoning are policy optimization algorithms that update model weights based on scalar reward feedback. A central debate in post-training compares online policy gradient methods (like PPO) with offline preference optimization (like DPO). Comprehensive analyses reveal that while DPO offers computational simplicity by bypassing explicit reward model training and value function estimation, PPO maintains superior online exploration dynamics crucial for discovering novel reasoning paths in expansive mathematical and symbolic spaces [2].

To guide these optimization algorithms, reward design is paramount. Traditional approaches rely on Outcome Reward Models (ORMs), which evaluate only the final answer of a generated trajectory [4]. Although simple to implement when ground-truth answers are verifiable, ORMs suffer from sparse feedback and high variance on long-horizon reasoning tasks. To mitigate this, Process Reward Models (PRMs) provide step-by-step verification, offering fine-grained supervision that tracks logical progression and isolates exact failure points in multi-step proofs or calculations [3]. Furthermore, decoupled value policy optimization (DVPO) and global value guidance frameworks optimize credit assignment by separating policy updates from value estimation, stabilizing training across extended generation horizons [12].

## Test-Time Search and Planning Frameworks
While single-pass generation benefits from policy optimization, complex reasoning tasks in mathematics, coding, and multi-hop QA often require systematic exploration and backtracking. Recent advances couple LLMs with structured test-time search and planning paradigms. On-policy tree search frameworks, such as TreeRL, integrate tree-structured search directly into the reinforcement learning loop, ensuring that policy updates align with exploration trajectories rather than static offline data distributions [5]. 

Similarly, combining Monte Carlo Tree Search (MCTS) with iterative preference learning enables models to systematically evaluate branching reasoning paths, constructing high-quality preference datasets derived from search rollouts [6]. To handle interactive and multi-turn problem solving, agentic turn-based policy optimization frameworks ($AT^2PO$) unify trajectory-level rewards with turn-level planning objectives, maximizing exploration diversity [7]. Moreover, integrated architectures like ReSearch train models via RL to autonomously determine when and how to invoke external search tools during internal reasoning steps, bridging parametric knowledge with dynamic external verification [13].

## Addressing Distribution Mismatch and Gradient Starvation
As RL with verifiable rewards (RLVR) scales, models frequently reuse generated rollouts across multiple policy updates to maximize sample efficiency. However, this off-policy reuse introduces severe distribution mismatch and optimization pathologies. In clipped policy gradient objectives, strict clipping thresholds often suppress under-generated positive reasoning responses—a phenomenon known as sign-dependent gradient starvation [8]. 

To resolve these stability issues, Reshaped Sequence Policy Optimization (ReSPO) replaces traditional clipping mechanisms with a smooth, two-branch sequence optimization objective [8]. By ensuring that positive exploration trajectories are not penalized or starved of gradient updates due to reference policy drift, ReSPO facilitates stable policy convergence during extensive multi-step rollouts, unlocking deeper test-time scaling for complex symbolic tasks.

## Applications, Benchmarks, and Empirical Evaluation
Reinforcement learning post-training has demonstrated remarkable empirical success across demanding reasoning domains, most notably in mathematical problem solving (e.g., GSM8K and MATH) and automated coding. Pioneering frameworks like WizardMath leverage Reinforced Evol-Instruct Feedback (RLEIF) to systematically amplify reasoning complexity, significantly outperforming base models and standard SFT baselines on established benchmarks [9]. Furthermore, empirical scaling studies reveal that while larger models exhibit higher sample efficiency during RL post-training, they eventually encounter saturation limits, necessitating careful data reuse and efficient exploration strategies [14].

Despite these impressive performance gains, recent diagnostic evaluations highlight substantial vulnerabilities in current RL-driven reasoning models. Benchmarks such as GSM-Symbolic demonstrate that when numerical values are perturbed or irrelevant clauses are introduced, models experience marked performance degradation, exposing an over-reliance on surface-level pattern matching rather than robust logical abstraction [10]. Compounding this, rigorous new evaluations like MATH-Beyond establish that pushing models beyond pre-trained base capabilities remains exceptionally difficult, as current reward functions frequently induce reward hacking and brittle shortcut learning instead of genuine discovery [11].

## Trends and Open Problems
The field of reinforcement learning for LLM reasoning is rapidly evolving toward several key frontiers. First, the synergy between test-time compute scaling and process supervision is redefining inference economics, trading off increased search depth for smaller, highly verified base models. Second, mitigating reward hacking and distribution collapse in open-ended reasoning environments remains an active theoretical challenge. Finally, developing generalized verification frameworks that can autonomously generate process supervision signals without human annotation or brittle rule-based parsers will be crucial for scaling reasoning models into unbounded scientific and agentic domains.

## References
[1] Enhancing Large Language Model Reasoning with Reward Models: An Analytical Survey. hf-search. https://huggingface.co/papers/2510.01925 (2025-10-02)
[2] Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study. hf-search. https://huggingface.co/papers/2404.10719 (2024-04-16)
[3] Rewarding Progress: Scaling Automated Process Verifiers for LLM Reasoning. hf-search. https://huggingface.co/papers/2410.08146 (2024-10-10)
[4] Logical Reasoning with Outcome Reward Models for Test-Time Scaling. hf-search. https://huggingface.co/papers/2508.19903 (2025-08-27)
[5] TreeRL: LLM Reinforcement Learning with On-Policy Tree Search. hf-search. https://huggingface.co/papers/2506.11902 (2025-06-13)
[6] Monte Carlo Tree Search Boosts Reasoning via Iterative Preference Learning. hf-search. https://huggingface.co/papers/2405.00451 (2024-05-01)
[7] AT^2PO: Agentic Turn-based Policy Optimization via Tree Search. hf-search. https://huggingface.co/papers/2601.04767 (2026-01-08)
[8] ReSPO: Reshaped Sequence Policy Optimization for Gradient Starvation in Off-Policy Learning. hf-daily. https://huggingface.co/papers/2609.35433 (2026-09-28)
[9] WizardMath: Empowering Mathematical Reasoning for Large Language Models via Reinforced Evol-Instruct. web. https://huggingface.co/papers/2308.09583 (2023-08-18)
[10] GSM-Symbolic: Understanding the Limitations of Mathematical Reasoning in Large Language Models. web. https://huggingface.co/papers/2410.05229 (2024-10-07)
[11] MATH-Beyond: A Benchmark for RL to Expand Beyond the Base Model. web. https://huggingface.co/papers/2510.11653 (2025-10-13)
[12] Lean and Mean: Decoupled Value Policy Optimization with Global Value Guidance. hf-search. https://huggingface.co/papers/2502.16944 (2025-02-24)
[13] ReSearch: Learning to Reason with Search for LLMs via Reinforcement Learning. hf-search. https://huggingface.co/papers/2503.19470 (2025-03-25)
[14] Scaling Behaviors of LLM Reinforcement Learning Post-Training: An Empirical Study in Mathematical Reasoning. web. https://huggingface.co/papers/2509.25300 (2025-09-29)
