# Comprehensive Survey on Large Language Model Agents and Tool Use

## TL;DR
- **Foundational Integration:** Early architectures like ReAct and MRKL established core paradigms for interleaving verbal reasoning traces with external execution loops or modular neuro-symbolic routers [1][2].
- **Self-Supervised Tool Acquisition:** Frameworks such as Toolformer demonstrate that language models can autonomously learn API invocation through self-supervised filtering and fine-tuning [3].
- **Massive-Scale API Navigation:** Advanced frameworks like ToolLLM and Gorilla empower models to navigate over 16,000 real-world APIs using neural retrieval, specialized fine-tuning, and document adaptation [4][5].
- **Advanced Execution and Schema Adaptation:** To mitigate multi-step error accumulation and schema misalignment, recent methods employ executable block subroutines and tool-to-model schema alignments [6][7].
- **Rigorous Evaluation and Security Challenges:** Benchmarks such as AgentBench, ToolQA, AgentDojo, and ReliabilityBench reveal persistent gaps in agent reasoning, vulnerability to indirect prompt injections, and production stress failures [8][9][10][11][12].

## Background
Large language models (LLMs) have achieved remarkable capabilities in zero-shot general language understanding and generation. However, they remain bounded by inherent limitations such as static parametric memory, inability to access up-to-date real-world facts, and difficulty performing exact symbolic computations. To overcome these bottlenecks, recent research has focused on equipping LLMs with external tools—ranging from web search engines and calculators to thousands of specialized APIs and software execution environments. 

Equipping LLMs with tool use transforms them from passive text predictors into active autonomous agents capable of perceiving environments, formulating plans, executing multi-step workflows, and interacting with software tools. This survey synthesizes foundational architectures, advanced tool-learning methodologies, multi-agent collaborations, evaluation benchmarks, and security considerations shaping the modern landscape of agentic AI.

## Foundations and Architectures of LLM Agents
The foundational architecture of agentic tool use relies on bridging the gap between language generation and external symbolic execution. A primary milestone in this domain is the ReAct framework, which introduces a unified autoregressive generation loop interleaving verbal reasoning traces (Thought) with task-specific actions (Action) [1]. By interleaving reasoning and acting, ReAct allows language models to dynamically update their plans based on environment feedback, outperforming standard prompting across knowledge-intensive reasoning and interactive decision-making tasks such as HotpotQA, Fever, AlfWorld, and WebShop.

Complementing interactive reasoning loops, modular neuro-symbolic architectures such as MRKL Systems couple LLMs as central routers with specialized external expert modules and discrete tools [2]. MRKL addresses the fundamental limitations of monolithic language models by routing queries to dedicated knowledge sources and symbolic calculators. Similarly, self-supervised approaches like Toolformer demonstrate that language models can teach themselves to use tools (such as calendars, Q&A systems, and calculators) by generating API call candidates and filtering them based on perplexity reduction and output quality improvement [3]. This enables models to acquire tool-use capabilities without requiring massive human-annotated trajectories.

## Advanced Tool Learning and Massive-Scale API Navigation
As the ecosystem of available software tools expands, scaling agent capabilities to thousands of APIs becomes critical. ToolLLM addresses this challenge by introducing a general framework designed to empower open-source language models to master over 16,000 real-world APIs [4]. Supported by ToolBench—a massive benchmark of instruction-following API interaction tasks—ToolLLM utilizes an efficient breadth-first search decision tree algorithm (DFS/BFS) for trajectory collection and integrates a neural API retriever to dynamically select relevant APIs from vast candidate pools.

In parallel, Gorilla focuses on connecting large language models with massive API repositories through specialized fine-tuning and document retrieval integration [5]. Gorilla is trained to generate precise API calls and handle complex constraints across rapidly changing API documentation, mitigating parameter hallucinations. Moving beyond individual API selection, recent work also examines meta-capabilities: the MetaTool benchmark systematically evaluates whether LLMs can determine *whether* a tool is needed and *which* specific tool to choose, uncovering prevalent over-reliance and under-reliance patterns in state-of-the-art models [13].

## Execution Paradigms and Small Language Model Optimization
Traditional agentic workflows often rely on step-by-step tool calling, which suffers from cumulative error propagation across intermediate execution rounds. To address this, frameworks like HyperTool fold deterministic multi-step tool subroutines into single model-visible calls using executable code blocks, significantly improving multi-step accuracy and efficiency [6]. 

Furthermore, deploying small language models (SLMs) in agentic systems introduces unique challenges due to schema misalignment, where models hallucinate tool names absent from schemas because of pretraining biases. Rather than retraining models, schema-adaptation methods modify tool schemas to align with the models' pretraining representations, substantially boosting small model reliability [7].

## Evaluation Benchmarks and Autonomous Agent Capabilities
Evaluating LLM agents requires rigorous interactive environments rather than static dataset checks. AgentBench provides a comprehensive evaluation framework spanning multi-turn decision-making, API calls, operating systems, databases, and games, demonstrating a wide performance gap between proprietary models like GPT-4 and open-source alternatives in error recovery and complex planning [8]. 

Similarly, ToolQA evaluates an LLM's ability to use external tools to answer complex questions requiring externalized factual retrieval beyond parametric memory, testing precise query formulation and output synthesis without hallucination [9].

## Security, Robustness, and Production Stress Challenges
As LLM agents are deployed in real-world workflows interacting with untrusted data and external tools, security and robustness emerge as paramount concerns. AgentDojo is an extensible evaluation framework built to assess adversarial robustness, revealing that current tool-using agents are highly susceptible to indirect prompt injections embedded within retrieved web pages, user emails, or tool outputs that hijack control flow [10].

At the production level, ReliabilityBench evaluates agent consistency, robustness, and fault tolerance under production-like stress conditions, showing substantial performance degradation under API latency and transient tool failures [11]. To mitigate these operational and security risks, frameworks like AgenTRIM introduce offline reconstruction and online enforcement of least-privilege tool access, restricting tool privileges based on task context to prevent unauthorized data access and unintended side effects [12].

## Trends and Open Problems
- **Dynamic Schema Adaptation and Self-Healing:** Developing agents that can autonomously adapt to undocumented API changes and self-correct syntax or semantic parameter errors during execution.
- **Robustness Against Indirect Prompt Injection:** Designing principled defense mechanisms and isolation layers that shield agent control flows from malicious instructions embedded in retrieved web content or tool payloads.
- **Cost-Efficiency and Latency Optimization:** Reducing the token overhead and inference latency associated with multi-step search algorithms and iterative reasoning loops in production environments.
- **Standardized Multi-Agent Protocols:** Establishing secure, interoperable communication and task-delegation standards for collaborative multi-agent systems operating across heterogeneous tool ecosystems.

## References
[1] ReAct: Synergizing Reasoning and Acting in Language Models. hf-search. https://huggingface.co/papers/2210.03629 (2022-10-06)
[2] MRKL Systems: A modular, neuro-symbolic architecture that combines large language models, external knowledge sources and discrete reasoning. hf-search. https://huggingface.co/papers/2205.00445 (2022-05-01)
[3] Toolformer: Language Models Can Teach Themselves to Use Tools. hf-search. https://huggingface.co/papers/2302.04761 (2023-02-09)
[4] ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs (ToolBench). hf-search. https://huggingface.co/papers/2307.16789 (2023-07-31)
[5] Gorilla: Large Language Model Connected with Massive APIs. hf-search. https://huggingface.co/papers/2305.15334 (2023-05-24)
[6] HyperTool: Beyond Step-Wise Tool Calls for Tool-Augmented Agents. hf-search. https://huggingface.co/papers/2606.13663 (2026-06-11)
[7] Don't Adapt Small Language Models for Tools; Adapt Tool Schemas to the Models. hf-search. https://huggingface.co/papers/2510.07248 (2026-04-19)
[8] AgentBench: Evaluating LLMs as Agents. hf-search. https://huggingface.co/papers/2308.03688 (2023-08-07)
[9] ToolQA: A Dataset for LLM Question Answering with External Tools. hf-search. https://huggingface.co/papers/2306.13304 (2023-06-23)
[10] AgentDojo: A Dynamic Environment to Evaluate Attacks and Defenses for LLM Agents. hf-search. https://huggingface.co/papers/2406.13352 (2024-06-19)
[11] ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions. hf-search. https://huggingface.co/papers/2601.06112 (2026-01-03)
[12] AgenTRIM: Tool Risk Mitigation for Agentic AI. web. https://huggingface.co/papers/2601.12449 (2026-01-18)
[13] MetaTool Benchmark for Large Language Models: Deciding Whether to Use Tools and Which to Use. hf-search. https://huggingface.co/papers/2310.03128 (2023-10-04)
