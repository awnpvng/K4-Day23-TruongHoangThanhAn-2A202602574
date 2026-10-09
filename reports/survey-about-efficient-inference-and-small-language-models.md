# Survey on Efficient Inference and Small Language Models

## TL;DR
- **Small Language Model (SLM) Foundations**: High-performance SLMs require meticulous data curation, where recursive self-improvement frameworks like DataFoundry [1] and stringent deduplication [2] prevent catastrophic data repetition damage.
- **Dynamic Compute Routing**: Architectural innovations like Mixture-of-Depths (MoD) [3] and continuous Mixture of Tokens (MoT) [4] allocate compute dynamically across token positions, reducing forward-pass FLOPs and increasing throughput.
- **Quantization & Extreme Compression**: Post-training quantization (GPTQ [5], AWQ [6]), variable bit-rate formats (EXL2) [7], and 1.58-bit ternary weight paradigms (BitNet b1.58) [8] dramatically shrink model footprints while maintaining task accuracy.
- **Memory Virtualization & Serving**: Engine-level optimizations such as PagedAttention in vLLM [9] eliminate KV-cache memory fragmentation, achieving multi-fold serving throughput gains.
- **Speculative Decoding Acceleration**: Draft-then-verify speculative decoding frameworks combined with adaptive multi-method verification deliver substantial end-to-end latency speedups [10][11] on accelerator hardware.

## Background
The rapid proliferation of Large Language Models (LLMs) has transformed artificial intelligence, yet deploying massive models at scale introduces severe computational, memory, and energy bottlenecks. In response, the research community has pivoted toward two complementary paradigms: Small Language Models (SLMs) and efficient inference systems. SLMs—typically comprising under 7 billion parameters—achieve remarkable capability parity with much larger architectures when trained on exceptionally curated data and optimized with parameter-efficient designs. Simultaneously, efficient inference engineering addresses the memory-bandwidth-bound nature of autoregressive generation through post-training quantization, memory virtualization, and speculative decoding. This survey synthesizes recent advancements across these domains, examining foundational scaling, compression algorithms, system-level memory management, and speculative execution strategies.

## Data Curation and Scaling Foundations for Small Language Models
The scaling efficiency of Small Language Models is intrinsically tied to data composition and structural parameter allocation. Traditional post-hoc data filtering often creates a mismatch where quality issues originate during dataset construction but are only caught afterward. To address this, recursive self-improvement frameworks such as DataFoundry evolve data preparators prior to large-scale data production [1]. Furthermore, aggressive pretraining deduplication is essential; internal data repetition damages language models systematically, with evaluation loss peaking at intermediate repetition levels when compute on repeated data is held constant [2]. 

Beyond data purity, optimizing neural scaling laws for sub-7B models requires identifying parameter-efficient subnetworks. The ProbeScale framework combines neural scaling insights with probing techniques to optimize the performance-parameter trade-off in small language models [12]. By tailoring scaling strategies specifically to compact architectures, researchers can maximize capability without incurring the storage and compute penalties associated with over-parameterized models.

## Dynamic Compute and Architectural Innovations
To further accelerate inference and reduce FLOP counts per forward pass, modern SLMs incorporate dynamic compute allocation mechanisms that move beyond static transformer layers. Mixture-of-Depths (MoD) introduces dynamic compute allocation across token positions and network depth via top-k routing, enforcing a strict static computation graph with a user-defined capacity budget while enabling up to 50% faster step times [3]. 

Similarly, continuous Mixture of Tokens (MoT) architectures group tokens from different examples to process via shared experts without discontinuous top-k routing during pretraining, improving training stability while retaining parameter scalability and supporting transition tuning for discrete sparse MoE inference [4]. These architectural shifts ensure that compute is expended only where semantic complexity demands it, preserving accelerator utilization.

## Post-Training Quantization and Extreme Weight Compression
Because autoregressive decoding is fundamentally memory-bandwidth-bound, reducing the precision of model weights is paramount for high-throughput inference. GPTQ established a robust foundation for one-shot weight quantization using approximate second-order Hessian information, significantly reducing perplexity degradation at 3-bit and 4-bit precision [5]. Building on the insight that weights are not equally important, Activation-aware Weight Quantization (AWQ) demonstrates that protecting just 1% of salient weights based on activation magnitude via per-channel scaling greatly reduces quantization error without hardware-inefficient mixed-precision execution [6].

For fine-grained deployment, variable bit-rate formats such as ExLlamaV2 (EXL2) allow custom precision allocations across layers (e.g., 4.25-bit or 4.65-bit), pushing the Pareto frontier of model size versus perplexity [7]. At the extreme edge of compression, BitNet b1.58 introduces 1-bit quantization where weights are restricted to ternary values ($\{-1, 0, +1\}$, averaging 1.58 bits) and activations are quantized to 8-bit integers, achieving full-precision performance parity while delivering massive memory and energy reductions [8].

## KV Cache Virtualization and Serving Infrastructure
Even with compressed weights, generative inference is bottlenecked by the dynamic Key-Value (KV) cache, which consumes substantial GPU memory and suffers from severe fragmentation during variable-length sequence generation. PagedAttention solves this by drawing inspiration from operating system virtual memory and paging, partitioning the KV cache into fixed-size physical blocks that eliminate external fragmentation [9]. 

Integrated within the vLLM serving engine, PagedAttention achieves near-zero memory waste and supports efficient block-level memory sharing (such as copy-on-write for parallel sampling and beam search), boosting serving throughput by 2–4× over baseline frameworks [9]. These system-level abstractions allow high-density multi-tenant serving without sacrificing response latency.

## Speculative Decoding and Acceleration Paradigms
Speculative decoding accelerates autoregressive generation by decoupling draft generation from target model verification. A lightweight draft model or auxiliary structure generates multiple speculative future tokens, which the larger target model verifies in parallel in a single forward pass [10]. Recent production-grade evaluations on vLLM highlight that target model verification dominates runtime execution, and verification costs of rejected tokens can introduce overhead under high system load [11].

To mitigate these overheads, advanced systems employ adaptive multi-method strategies—such as combining $n$-gram matching and lightweight neural drafters (e.g., EAGLE variants)—to optimize acceptance rates. These combined approaches can achieve up to a 4.9× end-to-end throughput improvement over standard autoregressive decoding [11].

## Trends and Open Problems
Despite significant strides in efficient inference and small language models, several open challenges remain:
1. **Draft-Verification Co-Design**: Optimizing draft models to dynamically match varying hardware loads and sequence lengths without incurring synchronization bottlenecks.
2. **Extreme Quantization Generalization**: Scaling 1-bit and sub-2bit paradigms (like BitNet b1.58) across diverse architectures (e.g., multimodal and reasoning models) without accuracy collapse.
3. **Continuous Batching Integration**: Seamlessly coupling speculative decoding and dynamic compute routing (MoD/MoT) with continuous batching engines under strict latency SLAs.
4. **Automated Data-Compression Co-Design**: Bridging data curation pipelines (DataFoundry) with quantization-aware pretraining to produce inherently compression-friendly small language models.

## References
[1] DataFoundry: Evolving Data Preparators via Recursive Self-Improvement. arxiv. https://arxiv.org/abs/2608.29966 (2026-08-30)
[2] Internal Data Repetition Destroys Language Models. arxiv. https://arxiv.org/abs/2606.24998 (2026-06-23)
[3] Mixture-of-Depths: Dynamically allocating compute in transformer-based language models. web. https://arxiv.org/abs/2404.02258 (2024-04-02)
[4] Mixture of Tokens: Continuous MoE through Cross-Example Aggregation. web. https://proceedings.neurips.cc/paper_files/paper/2024/file/bc427eb348789b190e3ea050cceff8a3-Paper-Conference.pdf (n.d.)
[5] GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers. arxiv. https://arxiv.org/abs/2210.17323 (2022-10-31)
[6] AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration. web. https://arxiv.org/abs/2306.00978 (2023-06-01)
[7] ExLlamaV2 (EXL2) Quantization and Inference. web. https://oobabooga.github.io/blog/posts/gptq-awq-exl2-llamacpp/ (2023-09-01)
[8] BitNet b1.58 1-Bit Models and bitnet.cpp Inference. web. https://arxiv.org/abs/2504.12285 (2025-04-12)
[9] Efficient Memory Management for Large Language Model Serving with PagedAttention. arxiv. https://arxiv.org/abs/2309.06180 (2023-09-12)
[10] Unlocking Efficiency in Large Language Model Inference: A Comprehensive Survey of Speculative Decoding. web. https://aclanthology.org/2024.findings-acl.456.pdf (n.d.)
[11] Production-Grade Evaluation of Speculative Decoding in vLLM. web. https://arxiv.org/abs/2601.11580 (n.d.)
[12] ProbeScale: Probing Analysis to Optimize Neural Scaling Laws for Efficient Small Language Model Inference. hf-search. https://huggingface.co/papers/2606.01806 (2026-06-01)
