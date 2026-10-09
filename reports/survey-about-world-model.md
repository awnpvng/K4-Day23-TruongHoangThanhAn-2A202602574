# Comprehensive Survey on World Models: Foundations, Architectures, Applications, and Open Challenges

## TL;DR
- World models serve as internal simulation engines that predict environmental transitions under agent actions, enabling model-based reinforcement learning, planning, and policy evaluation [1].
- Algorithms like DreamerV3 stabilize general model-based RL across over 150 diverse domains through categorical representations and symlog predictions, successfully solving sparse-reward tasks like Minecraft from scratch [2].
- Architectural paradigms have evolved from recurrent latent state-space models and diffusion-based generators (such as DIAMOND in Atari) to decoder-free Joint-Embedding Predictive Architectures (JEPAs) like LeWAM [3][4][5].
- Embodied AI and autonomous systems leverage 3D/4D occupancy forecasting and video diffusion world models to bridge perception with action-conditioned decision-making [6][7][8].
- Despite scaling successes, generative world models frequently suffer from physical hallucinations, state drift, and long-horizon accumulation errors, highlighting the gap between visual realism and true physical understanding [7][8].

## Background
World models refer to computational frameworks designed to capture, encode, and predict the dynamics of external environments. Originating from classical control theory, cognitive science, and Model-Based Reinforcement Learning (MBRL) frameworks like Dyna, modern world models have undergone a paradigm shift. Rather than relying solely on reactive policies, an agent equipped with a world model can internally simulate future trajectories, evaluate alternative action sequences, and optimize behavior without incurring the sample complexity of physical interactions [1]. 

As articulated in recent comprehensive surveys, world models function both as representational compressors of high-dimensional sensory streams and as predictive simulators of environmental evolution [5][7]. The field has expanded rapidly from compact latent imagination models in simulated gridworlds to foundation-scale video generation engines, 3D/4D occupancy forecasting frameworks, and World-Action Models (WAMs) tailored for robotics and autonomous driving [1][6][8].

## Foundations and Model-Based Reinforcement Learning
The foundational evolution of world models is deeply rooted in model-based reinforcement learning (MBRL), where learning an environment model enables proactive planning. A milestone in this trajectory is DreamerV3, introduced on January 12, 2023, which established a general RL algorithm capable of learning environment dynamics and improving behavior by imagining future scenarios in a compact latent space [2]. DreamerV3 introduced robust techniques such as categorical representations, symlog predictions, and balance loss to stabilize training across more than 150 diverse domains using a single fixed set of hyperparameters [2]. Notably, it became the first algorithm to solve open-world sparse-reward tasks—such as collecting diamonds in Minecraft from scratch—without human data or hand-crafted curricula [2].

Building upon these foundations, contemporary robot learning frameworks define world models as predictive representations of how physical environments evolve under specific actions [1]. These models support policy learning, simulation, evaluation, and data generation by acting as learned simulators that produce imagined observations, rewards, and terminations for policy updates or decision-time action ranking [1].

## Architectural Innovations and Representation Learning
World model architectures trade off representation fidelity and computational efficiency across several distinct paradigms: recurrent state-space models (RSSMs), transformers, diffusion generators, and decoder-free joint-embedding predictive architectures (JEPAs) [3][5][6]. 

Representation formats span continuous latent spaces, discrete token codebooks via VQ-VAE, object-centric slots, and 3D/4D occupancy grids [5][6]. For instance, the DIAMOND agent demonstrated that incorporating diffusion world modeling directly into Atari 100k benchmarks significantly enhances agent policy learning by capturing fine visual details compared to traditional compressed low-fidelity latent models [3]. In parallel, decoder-free architectures like LeWAM utilize bidirectional transformers for forward, backward, inverse dynamics, and policy prediction within a Joint-Embedding Predictive Architecture (JEPA) latent space, improving linear probing of robot states while eliminating redundant pixel-level reconstruction [4]. Furthermore, native 3D and 4D world modeling approaches (such as VideoGen, OccGen, and LiDARGen) utilize latent diffusion models and diffusion transformers (DiTs) to forecast volumetric occupancy in autonomous driving and robotics [6].

## Applications Across Domains: Robotics, Autonomous Driving, and Embodied AI
World models have become foundational across diverse domains, including autonomous driving, robotics, game AI, and embodied AI [7][8]. Comprehensive taxonomies classify embodied world models along three primary axes: functionality (decision-coupled vs. general-purpose), temporal modeling, and spatial representation [8]. 

In autonomous driving, video-based and ego-conditioned occupancy world models (such as GAIA-1, GenAD, and OccWorld) predict complex traffic dynamics, road condition evolution, and multi-agent interactions [6][7]. In robotics and interactive game simulation (such as Atari and MineDOJO), action-conditioned video generation models (e.g., AdaWorld, Vid2World, Pandora, and Yume) autoregressively imagine future scenes conditioned on control actions and text prompts [7][8]. These models serve as internal simulators that bridge perception, future prediction, and action-conditioned planning, facilitating robust sim-to-real transfer and long-horizon task execution [7][8].

## Trends, Challenges, and Open Problems
Despite rapid advancements, world models face critical structural and physical limitations. A central debate concerns whether world models should prioritize understanding static present representations or forecasting future states for decision-making [7]. 

Current video-centric generative models—inspired by foundation video models like Sora—often generate visually impressive sequences but suffer from severe physical hallucinations, object permanence failures, and an inability to simulate fundamental physical laws such as forces, fluid dynamics, and lighting interactions [7]. Moreover, long-horizon planning remains fragile because small prediction errors accumulate over extended trajectories, leading to severe state drift and inconsistent object dynamics [8]. Additional open challenges include data scarcity for action-conditioned video and occupancy pairs, scaling laws for volumetric and temporal representations, and the necessity to evaluate world models based on functional planning utility rather than mere visual pixel realism [6][7][8].

## References
[1] World Model for Robot Learning: A Comprehensive Survey. hf-search. https://arxiv.org/abs/2605.00080 (2026-04-30)
[2] Mastering Diverse Domains through World Models. web. https://arxiv.org/abs/2301.04104 (2023-01-12)
[3] Diffusion for World Modeling: Visual Details Matter in Atari. hf-search. https://huggingface.co/papers/2405.12399 (2024-05-20)
[4] LeWAM: A JEPA World Action Model with Diffusion-Steering-Based MPC. arxiv. https://arxiv.org/abs/2610.12407 (2026-10-08)
[5] World Models: A Comprehensive Survey of Architectures, Methodologies, Reasoning Paradigms, and Applications. web. https://arxiv.org/abs/2606.00133 (2026-06-02)
[6] 3D and 4D World Modeling: A Survey. arxiv. https://arxiv.org/abs/2509.07996 (2025-09-07)
[7] Understanding World or Predicting Future? A Comprehensive Survey of World Models. web. https://dl.acm.org/doi/10.1145/3746449 (2025-09-09)
[8] A Comprehensive Survey on World Models for Embodied AI. web. https://arxiv.org/abs/2510.16732 (2026-06-25)
