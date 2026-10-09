# A Comprehensive Survey of LLM Agents and Tool Use: Architectures, Multi-Agent Collaboration, and Security Evaluation

## TL;DR
- **Foundational API Integration**: Modern LLM agents have evolved from basic prompt-based API calls to robust function-calling architectures like Gorilla, APIGen, and ToolACE that support parallel execution, doc-retrieval adaptation, and synthetic self-evolution data [1][2][3].
- **Advanced Multi-Hop Reasoning & Policies**: Advanced evaluation frameworks such as VAKRA test agents across thousands of APIs and multi-source constraints, highlighting the challenge of adhering to natural-language tool-use policies [4].
- **Multi-Agent Orchestration & Workflows**: Multi-agent collaboration frameworks (e.g., MultiAgentBench) and structured topologies (such as graph-based communication) significantly enhance reasoning success across coding and research environments, while large-scale APIs are mastered via search-tree algorithms like DFSDT in ToolLLM [5][6].
- **Interactive & Executable Testbeds**: Executable benchmarking suites connecting WebArena Verified and SWE-Gym reveal that live-stressed environments yield fundamentally different system insights than static text baselines [7].
- **Critical Security Vulnerabilities**: Tool-using agents face severe threat surfaces including indirect prompt injection and tool-mediated control-flow hijacking, with mixed attacks achieving average success rates exceeding 84% in benchmarks like Agent Security Bench (ASB) and AgentDojo [8][9][10].

## Background
The paradigm of Large Language Models (LLMs) has expanded rapidly from static text generation to interactive agentic workflows capable of leveraging external tools, APIs, and digital environments. Tool-augmented language models bridge the gap between static parametric knowledge and dynamic external execution, enabling models to query databases, invoke third-party APIs, execute code, and interact with operating systems and web browsers. 

Historically, early approaches relied on prompt engineering and hand-crafted templates. However, as API ecosystems expanded to tens of thousands of services, specialized fine-tuning, automated dataset generation, and rigorous evaluation pipelines became essential [3][6]. Understanding how agents plan, execute, collaborate, and defend against security exploits is central to the development of robust autonomous systems.

## Foundations and Architectures of Tool-Augmented LLMs
The foundational layer of LLM tool use rests on precise API-calling frameworks and function-calling representations. Early milestones such as Gorilla demonstrated that fine-tuning language models with document retrieval adaptation effectively mitigates API hallucinations and handles diverse interface specifications [1]. To scale data availability without human bottlenecking, automated pipelines like APIGen generate verified, diverse function-calling datasets that power robust performance on benchmarks like the Berkeley Function-Calling Benchmark [3]. Similarly, the ToolACE framework employs a self-evolution synthesis process to produce diverse tool-learning data, boosting the function-calling capabilities of parameter-limited models [2].

Beyond single-turn function calling, modern agents must handle complex, multi-hop reasoning workflows across diverse API libraries. The VAKRA benchmark evaluates agents across more than 8,000 executable APIs spanning 62 domains, testing multi-hop reasoning over structured interfaces and natural-language tool-use policy constraints [4]. To further streamline tool integration, automated frameworks like AutoTools simplify tool encapsulation (transforming documentation into callable functions with runtime validation) and tool programming within unified code execution environments such as Python [11].

## Multi-Agent Collaboration and Orchestration
As tasks grow more intricate, single-agent architectures often hit cognitive and planning bottlenecks. This has driven a transition toward multi-agent systems (MASs) that coordinate multiple specialized LLM roles. Comprehensive surveys classify multi-agent collaboration mechanisms across distinct dimensions, including communication structures (star, chain, tree, graph), collaboration types (cooperation, competition, coopetition), and centralized orchestration frameworks [12]. 

Empirical evaluations via frameworks like MultiAgentBench and the MARBLE methodology demonstrate that graph-based communication topologies and cognitive planning significantly improve milestone-based KPIs and task success across domains like collaborative coding and research [5]. To handle massive, real-world API spaces, ToolLLM introduced a large-scale instruction-tuning dataset spanning over 16,000 RESTful APIs and leveraged a depth-first search-based decision tree (DFSDT) algorithm to optimize planning and solution-path annotations [6].

## Interactive Environments and Executable Testbeds
Static benchmarks often fail to capture the stochastic, stateful nature of real-world digital interactions. Consequently, the research community has pivoted toward interactive, executable testbeds. An executable benchmarking suite connecting WebArena Verified, SWE-Gym, and MiniWoB++ through shared workload adapters and task manifests proves that evaluating web and code agents under live-stressed executable conditions alters systems-facing conclusions compared to clean static baselines [7]. These interactive environments ensure that agents can maintain persistent state, react to unexpected tool outputs, and recover from runtime execution errors.

## Security, Robustness, and Evaluation
Despite their powerful capabilities, tool-using LLM agents introduce profound security risks across their operational lifecycle. A systematic review of 247 papers highlights that delegated authority, persistent state, and bidirectional information flow create critical threat surfaces, where prompt injection and tool-mediated control-flow hijacking dominate [8]. Untrusted tool outputs can easily carry indirect prompt injections that subvert the agent's original system instructions.

Dynamic environments such as AgentDojo measure agent robustness across realistic applications like e-banking and email clients using formal utility checks over environment states [9]. Furthermore, Agent Security Bench (ASB) evaluates direct prompt injections, indirect prompt injections, memory poisoning, and plan-of-thought (PoT) backdoors across multiple LLM backbones, revealing average attack success rates up to 84.30% for mixed attacks [10]. While defense mechanisms such as data delimiters, prompt sandwiching, and isolation filters offer partial protection, they frequently introduce trade-offs with benign utility and false positives [8][9].

## Trends and Open Problems
1. **Long-Horizon Stateful Planning**: Enhancing agent reliability over extended execution horizons where errors compound and tool states mutate continuously.
2. **Robustness Against Adversarial Tool Outputs**: Developing compositional and verifiable defenses against indirect prompt injection without degrading baseline task utility.
3. **Standardized Executable Evaluation**: Expanding interactive, live-stressed testbeds that bridge web, mobile, and desktop environments to better reflect real-world deployment challenges.
4. **Agent Alignment and Policy Adherence**: Ensuring that multi-agent systems and tool-augmented models faithfully adhere to complex natural-language governance and security policies.

## References
[1] Gorilla: Large Language Model Connected with Massive APIs. hf-search. https://huggingface.co/papers/2305.15334 (2023-05-24)
[2] ToolACE: Winning the Points of LLM Function Calling. hf-search. https://huggingface.co/papers/2409.00920 (2024-09-02)
[3] APIGen: Automated Pipeline for Generating Verifiable and Diverse Function-Calling Datasets. hf-search. https://huggingface.co/papers/2406.18518 (2024-06-26)
[4] VAKRA: Evaluating Multi-Hop Reasoning Across APIs and Retrieval Under Tool-Use Policies. arxiv. https://arxiv.org/abs/2608.12282 (2026-08-12)
[5] MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents. hf-search. https://huggingface.co/papers/2406.08979 (2024-06-13)
[6] ToolLLM: Facilitating Large Language Models to Master 16,464 Real-world APIs. web. https://arxiv.org/abs/2307.16789 (2023-07-27)
[7] An Executable Benchmarking Suite for Tool-Using Agents. web. https://arxiv.org/abs/2605.11030 (2026-05-11)
[8] Toward Secure LLM Agents: Threat Surfaces, Attacks, Defenses, and Evaluation. web. https://arxiv.org/abs/2606.10749 (n.d.)
[9] AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents. web. https://arxiv.org/abs/2406.13352 (n.d.)
[10] Agent Security Bench (ASB): A Comprehensive Framework for Benchmarking Security of LLM-based Agents. web. https://proceedings.iclr.cc/paper_files/paper/2025/file/5750f91d8fb9d5c02bd8ad2c3b44456b-Paper-Conference.pdf (2025)
[11] AutoTools: Automated Tool-Use Framework. web. https://dl.acm.org/doi/epdf/10.1145/3696410.3714825 (n.d.)
[12] Multi-Agent Collaboration Mechanisms: A Survey of LLMs. web. https://arxiv.org/abs/2501.06322 (2025-01-10)
