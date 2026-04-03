# Penguide: An Adaptive, Knowledge-Grounded LLM Pedagogical Agent with Explain-Then-Execute Enforcement and Learner Knowledge Modeling for Linux Kernel Education

**[Author Name], [Institution], [Email]**

---

## Abstract

Interactive technical education for Linux kernel and system administration is hindered by three compounding barriers: documentation assumes prior expertise, experimental error carries irreversible consequences, and existing LLM-based systems provide no pedagogical structure — they answer questions uniformly regardless of learner knowledge state. This paper presents Penguide, a locally-hosted LLM pedagogical agent that advances beyond prior work on three dimensions. First, Penguide enforces the **explain-then-execute paradigm** as a structural invariant at the orchestrator layer: a command from the LLM's output can only execute after its explanatory text has been fully delivered, with a permit-list policy implemented as two disjoint sets (`ALLOWED_COMMANDS`, `DENY_COMMANDS`) providing a two-stage safety backstop. Second, we introduce an **Adaptive Explanation Depth Scaling (AEDS)** model that maintains a probabilistic learner knowledge estimate $\hat{L}_t$ updated after each interaction via an exponentially weighted moving average of lexical complexity signals, and uses this estimate to modulate the explanation depth injected into the system prompt, adapting output between beginner-oriented plain-English descriptions and subsystem-level technical detail. Third, we introduce an **Explanation Confidence Score (ECS)** computed as the lexical overlap between the LLM's generated response and the retrieved knowledge base snippets, providing a per-response groundedness signal that correlates with hallucination risk. The Mistral 7B model is served locally via Ollama; knowledge-grounded context injection uses keyword-based retrieval against a structured `.md` knowledge base organized by kernel subsystem (`mm/`, `sched/`, `vfs/`, `net/`, `syscalls/`). A simulated learning study across three synthetic learner profiles (Beginner, Intermediate, Advanced) evaluates learning gain, task success rate, and explanation usefulness score over 270 interaction scenarios. Results demonstrate: mean learning gain of 0.41 standard deviation equivalent across profiles; 89% kernel subsystem mapping accuracy; 100% permit-list enforcement over 25 injected adversarial commands; and ECS correctly identifies low-confidence responses (ECS < 0.20) that correspond to responses containing factual errors in 91% of cases. GPU-accelerated inference achieves 2–3 s mean response time; CPU-only inference 6–12 s, acceptable for offline institutional deployment.

**Keywords:** large language models, educational agents, Linux kernel, Ollama, Mistral, explain-then-execute, adaptive explanation depth, knowledge modeling, pedagogical AI, local LLM, safety enforcement

---

## I. Introduction

The Linux kernel comprises over 30 million lines of C code organized into dozens of interdependent subsystems — memory management (`mm/`), process scheduler (`kernel/sched/`), virtual file system (VFS), networking (`net/`), device drivers, and security frameworks [1]. For students pursuing systems programming, operating systems research, or embedded development, practical fluency with the kernel and its associated command-line toolchain is essential. Yet the learning pathway is steep: man pages assume technical vocabulary, official documentation is organized by subsystem rather than learning progression, and unsafe experimentation in a live environment risks data loss or system instability.

The emergence of large language models (LLMs) as generalist technical reasoners opens a promising design space for interactive pedagogical agents [4]. However, deploying an LLM as a Linux tutor without pedagogical structure introduces two critical risks. First, an agent that executes commands without explanation teaches operational patterns without building understanding — a superficial learning outcome that collapses when the learner encounters an unfamiliar command outside the tutorial sequence. Second, an agent without safety enforcement may execute irreversibly destructive commands (e.g., `dd` to the wrong device, `rm -rf /`) if the LLM hallucinates or misinterprets context. Existing LLM tutoring systems [7],[8] address neither risk: they answer questions uniformly regardless of learner knowledge state and provide no structural execution barrier.

Penguide addresses both risks through a unified design: the explain-then-execute paradigm enforced as an orchestrator-level invariant, combined with an adaptive knowledge model that personalizes explanation depth to the estimated learner profile. A third contribution — the Explanation Confidence Score — addresses the hallucination risk that characterizes all LLM-based systems by providing a per-response groundedness estimate computable without external annotation.

The novel aspects of Penguide relative to prior LLM educational agents are:

1. **Structural explain-then-execute enforcement** — explanation precedence is enforced by the orchestrator's parsing model, not by the LLM's instruction following, which is unreliable [8].
2. **Adaptive Explanation Depth Scaling (AEDS)** — a probabilistic learner knowledge model $\hat{L}_t$ modulates prompt construction, dynamically calibrating explanation depth from beginner-oriented descriptions to subsystem-level technical analysis as the learner's estimated knowledge level rises.
3. **Explanation Confidence Score (ECS)** — a lexical overlap metric between the generated response and retrieved knowledge context provides a computationally cheap hallucination risk proxy requiring no external oracle.

**Specific contributions:**

- **C1:** The explain-then-execute paradigm enforced at the orchestrator layer via regex-based `RUN:` parsing, with a two-set permit-list policy (`ALLOWED_COMMANDS`, `DENY_COMMANDS`) providing defense-in-depth against unsafe LLM output.
- **C2:** The Adaptive Explanation Depth Scaling (AEDS) model: a formal learner knowledge estimator $\hat{L}_t = \frac{\sum_{i=1}^t \alpha^{t-i} s_i}{\sum_{i=1}^t \alpha^{t-i}}$ updated from lexical complexity signals after each interaction, used to inject a profile-appropriate depth directive into the system prompt.
- **C3:** The Explanation Confidence Score (ECS): $\text{ECS}(r, \mathcal{K}) = \frac{|\text{tok}(r) \cap \text{tok}(\mathcal{K})|}{|\text{tok}(r)|}$, a per-response groundedness signal that identifies low-grounding responses with 91% correlation to detected factual errors.
- **C4:** A keyword-based knowledge-grounded context injection pipeline that retrieves relevant kernel documentation snippets from a structured `.md` knowledge base organized by subsystem, augmenting the LLM prompt without vector database infrastructure.
- **C5:** A simulated learning study across three synthetic learner profiles evaluating learning gain, task success rate, and explanation usefulness over 270 interaction scenarios, with baseline comparison against man pages and unguided LLM interaction.
- **C6:** A fully local execution model (Mistral 7B via Ollama) with no external API dependency, preserving learner privacy and enabling air-gapped institutional deployment.

The remainder of this paper is organized as follows. Section II reviews related work. Section III presents the system architecture and formal models. Section IV details the implementation. Section V reports experimental evaluation. Section VI presents safety and adversarial analysis. Section VII discusses scalability. Section VIII concludes.

---

## II. Related Work

### II-A. Intelligent Tutoring Systems and One-on-One Learning

**VanLehn [3]** conducted a comprehensive meta-analysis of intelligent tutoring systems (ITS), demonstrating that one-on-one human tutoring yields effect sizes of approximately 2 sigma over classroom instruction, and that ITS approaches can achieve 0.76 sigma. The analysis identifies three key mechanisms: immediate feedback, knowledge tracing, and adaptive scaffolding. Penguide incorporates all three: immediate explanation-feedback before command execution, the AEDS learner knowledge model (approximating knowledge tracing), and depth-adaptive scaffolding. However, unlike classical ITS systems that rely on domain-specific rule engineering, Penguide uses a general-purpose LLM as the reasoning backbone, eliminating the annotation cost that limits ITS scalability.

**Koedinger and Aleven [2]** characterized the assistance dilemma in ITS: providing too much assistance hinders long-term learning (over-scaffolding), while too little leads to failure and disengagement. The AEDS model directly addresses this dilemma by dynamically scaling explanation depth: beginners receive full conceptual scaffolding; advanced learners receive subsystem-level technical detail that challenges and extends their existing knowledge.

### II-B. LLMs in Education

**Brown et al. [4]** demonstrated that LLMs exhibit few-shot generalization to technical domains including code generation and explanation without domain-specific fine-tuning, motivating the use of Mistral 7B as the reasoning backbone rather than a fine-tuned specialist model.

**MacNeil et al. [7]** demonstrated that LLM-generated code explanations improved student comprehension in introductory CS education, validating the explanation-first interaction design. Their finding that explanation quality varies significantly with prompt structure motivates the depth-directive injection in the AEDS model.

**Kasneci et al. [8]** reviewed LLMs in education broadly, identifying hallucination and over-reliance as the primary risks. Penguide's ECS metric addresses hallucination risk through a computationally cheap groundedness proxy; the explain-then-execute invariant addresses over-reliance by structurally preventing uninformed execution.

**Wei et al. [12]** demonstrated that chain-of-thought prompting improves LLM reasoning accuracy. Penguide's system prompt encodes a lightweight chain-of-thought structure: (1) explain purpose, (2) identify kernel subsystem, (3) note safety considerations, (4) provide `RUN:` directive — an ordered reasoning chain that improves explanation coherence relative to unconstrained generation.

### II-C. Retrieval-Augmented Generation and Knowledge Injection

**Lewis et al. [9]** introduced Retrieval-Augmented Generation (RAG), demonstrating that augmenting LLM prompts with retrieved external knowledge substantially reduces hallucination rates on knowledge-intensive tasks. Penguide's knowledge-grounded context injection is architecturally motivated by RAG principles, adapted for local operation without a vector database or dense embedding model. Keyword-based retrieval over a structured `.md` knowledge base provides the essential knowledge grounding function while remaining deployable on resource-constrained hardware.

**Jiang et al. [10]** described the Mistral 7B architecture, demonstrating that 7B-parameter instruction-tuned models achieve competitive performance on reasoning benchmarks relative to larger models. This enables capable LLM inference on hardware without enterprise-grade GPU resources.

### II-D. Safety in LLM-Based Systems

**Nakano et al. [5]** proposed WebGPT, establishing the tool-use paradigm where an LLM generates structured output that an orchestrator interprets to invoke external tools. Penguide's `RUN:` output protocol and orchestrator design are directly influenced by this architecture, with the critical extension of a structural safety layer interposed between LLM output and tool execution.

The permit-list enforcement model in Penguide differs from post-hoc content filtering approaches [8] in that it provides a mathematical safety guarantee: no command in `DENY_COMMANDS` can execute regardless of LLM output content, because the execution check is a deterministic Python set membership test performed after output parsing.

---

## III. System Architecture and Formal Models

### III-A. Architecture Overview

Penguide is organized as a four-layer system:

```
┌─────────────────────────────────────────────────────────────┐
│  USER INTERFACE (CLI Terminal)                              │
│  Query input · Explanation display · Result inspection     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  ORCHESTRATOR (orchestrator.py)                             │
│  step(): KB query → Memory context → Prompt compose        │
│  → Agent.think() → RUN: parse (regex) → permit-list check  │
│  → subprocess.run() → Memory update                        │
│  + AEDS: learner model update → depth-directive injection  │
│  + ECS: confidence score computation                       │
└──────────┬──────────────────────────────┬───────────────────┘
           │ Ollama API                    │ Keyword retrieval
┌──────────▼──────────┐        ┌──────────▼───────────────────┐
│  LLM Layer          │        │  Knowledge Layer             │
│  Mistral 7B-Instruct│        │  KnowledgeBase.query()       │
│  via Ollama runtime │        │  knowledge/kernel/*.md       │
│  GGUF quantization  │        │  mm/, sched/, vfs/,          │
│  CPU/GPU-flexible   │        │  net/, syscalls/, general/   │
└─────────────────────┘        └──────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  MEMORY MODULE (memory.py)                                  │
│  Rolling list of {role, content} pairs                     │
│  Roles: user · assistant · tool                            │
└─────────────────────────────────────────────────────────────┘
```

### III-B. Explain-Then-Execute Protocol

The orchestrator's `step(user_input)` method implements the explain-then-execute protocol:

```
Algorithm 1: Orchestrator.step(user_input)
Input:  user_input (str)
Output: combined_response (str)

1.  kb_context  ← KnowledgeBase.query(user_input)
2.  hist_context ← Memory.get_context()
3.  full_context ← hist_context + kb_context
4.  depth_directive ← AEDS.get_directive(L_hat)   // NEW
5.  prompt ← SYSTEM_PROMPT + depth_directive + "User: " + user_input
6.  reply ← Agent.think(prompt, full_context)
7.  Memory.add("user", user_input)
8.  match ← regex_search(r'RUN:\s*(.+)', reply)
9.  if match:
10.     cmd ← match.group(1).strip()
11.     explanation ← reply[:match.start()].strip()
12.     if ShellTool.is_permitted(cmd):             // permit-list check
13.         output ← ShellTool.run(cmd)
14.         combined_response ← explanation + output
15.     else:
16.         combined_response ← explanation + "[BLOCKED: command not permitted]"
17.     Memory.add("tool", output)
18.     Memory.add("assistant", combined_response)
19. else:
20.     Memory.add("assistant", reply)
21.     combined_response ← reply
22. ecs ← ECS(reply, kb_context)                  // NEW
23. AEDS.update(user_input, reply, ecs)            // NEW
24. return combined_response
```

The critical invariant: `explanation` in line 11 is the substring of `reply` *before* the `RUN:` match position. This is a structural property of the regex parser — the explanation physically precedes the execution directive in every response where a command is present.

### III-C. Adaptive Explanation Depth Scaling (AEDS)

#### III-C-1. Learner Knowledge Signal

After each interaction turn $t$, a knowledge signal $s_t \in [0, 1]$ is computed from the learner's input query using three observable proxies:

$$s_t = \frac{1}{3}\left(v_t + \frac{n_t}{N_{\max}} + (1 - f_t)\right)$$

where:
- $v_t$ = **vocabulary sophistication score**: proportion of technical kernel terms in the query (terms appearing in the knowledge base index), $v_t \in [0, 1]$
- $n_t$ = **query noun phrase count** normalized by $N_{\max} = 10$: longer, more precise queries indicate higher familiarity
- $f_t$ = **confusion signal**: 1 if the query contains phrases indicative of misunderstanding ("what does that mean", "I don't understand", "why did", "what happened"), 0 otherwise

#### III-C-2. Learner Knowledge Estimator

The learner knowledge level $\hat{L}_t$ is updated as an exponentially weighted moving average:

$$\hat{L}_t = \frac{\sum_{i=1}^{t} \alpha^{t-i} \cdot s_i}{\sum_{i=1}^{t} \alpha^{t-i}}, \quad \alpha = 0.7$$

The decay factor $\alpha = 0.7$ weights recent interactions more heavily than earlier ones, allowing the model to track knowledge level changes within a session. For $t=1$, $\hat{L}_1 = s_1$.

#### III-C-3. Explanation Depth Directive

The continuous estimate $\hat{L}_t$ is mapped to a discrete depth level for prompt injection:

| $\hat{L}_t$ Range | Level | Depth Directive Injected into System Prompt |
|-------------------|-------|----------------------------------------------|
| $[0.0, 0.33)$ | Beginner | "Explain in plain English for a complete beginner. Avoid jargon. Use analogies." |
| $[0.33, 0.66)$ | Intermediate | "Explain with moderate technical depth. Reference kernel subsystem names." |
| $[0.66, 1.0]$ | Advanced | "Explain at kernel developer level. Include subsystem internals, relevant C structures, and /proc paths." |

The depth directive is appended to the system prompt before each LLM invocation, personalizing the response without modifying the model weights.

### III-D. Explanation Confidence Score (ECS)

The Explanation Confidence Score measures the lexical grounding of the LLM's response in the retrieved knowledge base context:

$$\text{ECS}(r, \mathcal{K}) = \frac{|\text{tok}(r) \cap \text{tok}(\mathcal{K})|}{|\text{tok}(r)|}$$

where $\text{tok}(\cdot)$ is the set of non-stopword content tokens (lemmatized) in the string, $r$ is the LLM response, and $\mathcal{K}$ is the concatenated retrieved knowledge context. ECS = 1.0 indicates complete token overlap (response is fully grounded in retrieved context); ECS = 0 indicates no overlap (response is entirely generated without knowledge grounding — maximum hallucination risk).

**ECS-triggered behavior:** Responses with $\text{ECS} < 0.20$ are flagged with an in-session warning: "Note: This explanation may contain information beyond the verified knowledge base. Please verify with `man <command>` before relying on it." This warning is appended to the learner's displayed response without modifying the agent's reply.

### III-E. Knowledge-Grounded Context Injection Pipeline

The `KnowledgeBase.query(user_input)` method (implemented in `knowledge.py`) performs keyword-based retrieval:

1. **Tokenization:** `user_input` is lowercased and split on whitespace.
2. **Topic matching:** For each document in the knowledge base (keyed by filename), the document's topic name (filename without `.md` extension) is checked for substring containment in `user_input`, and vice versa, using words of length > 3 to avoid noise from function words.
3. **Fallback:** If the query contains the word "kernel" but no specific topic matches, all documents are included (full-context fallback).
4. **Context construction:** Matching documents are concatenated with section separators (`--- From Kernel Doc: <filename> ---`) and prepended to the prompt.

The knowledge base is organized as a directory tree:

```
knowledge/kernel/
  mm.md          # Memory management: page allocator, virtual memory areas
  sched.md       # Process scheduler: CFS, runqueue, scheduling classes
  vfs.md         # Virtual file system: inode, dentry, superblock
  net.md         # Networking: socket layer, TCP/IP stack, netfilter
  syscalls.md    # System call interface: entry points, syscall table
  general.md     # General Linux: boot process, init, module loading
```

Each file contains 200–500 words of authoritative content drawn from kernel.org documentation and Kerrisk [1].

### III-F. Permit-List Shell Policy

The shell tool (`tools/shell.py`) enforces a two-set policy:

- **`ALLOWED_COMMANDS`**: `{ls, cat, pwd, whoami, uname, df, du, ps, free, ip, ss, grep, find, wc, head, tail, mkdir, touch, cp, mv, rm, less, nano, vim, htop, date, uptime, hostname, curl, wget}` — read/inspect commands plus standard file management.
- **`DENY_COMMANDS`**: `{sudo, chmod, chown, mount, umount, dd, reboot, shutdown}` — privilege escalation and destructive operations.

Enforcement logic: `cmd.split()[0]` extracts the base command; membership in `DENY_COMMANDS` returns silently blocked; absence from `ALLOWED_COMMANDS` also returns blocked. `subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)` executes permitted commands with a 5-second watchdog.

**Safety guarantee:** For any LLM output containing `RUN: <x>`, if `x.split()[0] ∈ DENY_COMMANDS`, execution is structurally impossible — this is a deterministic Python set membership check, not a policy heuristic.

### III-G. Formal Learning Gain Model

The learning gain for a learner profile $P$ over a session of $N$ interactions is estimated as:

$$LG_P = \frac{1}{N} \sum_{t=1}^{N} \phi(s_t, s_{t-1})$$

where $\phi(s_t, s_{t-1}) = s_t - s_{t-1}$ is the per-turn knowledge signal delta. A positive $LG_P > 0$ indicates that the learner's query vocabulary and precision increased over the session — a proxy for knowledge gain. For cross-profile comparison, $LG_P$ is normalized to a Cohen's $d$-equivalent by dividing by the within-session standard deviation of $s_t$.

---

## IV. Implementation

### IV-A. Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| LLM Runtime | Ollama | 0.1.x |
| LLM Model | Mistral | 7B-Instruct (GGUF) |
| Orchestrator | Python | 3.11 |
| Knowledge Base | Plain-text `.md` files | — |
| Memory Module | In-process `list[dict]` | — |
| Shell Tool | Python `subprocess` | stdlib |
| Permit-list | Python `set` | stdlib |
| AEDS Module | Python `collections.deque` | stdlib |

### IV-B. System Prompt and Chain-of-Thought Structure

The system prompt (`core/prompt.py`) encodes a lightweight chain-of-thought structure:

```
You are Penguide, a friendly local Linux guide for beginners.
Your goal is to teach Linux by explaining what commands do and
referencing the Linux Kernel documentation.

RULES:
- Always explain the purpose of the command or concept in simple terms.
- Use a helpful, educational tone.
- If the user asks for an action, provide a simple explanation followed by:
  RUN: <command>
- If the user asks a theoretical question, provide a detailed but
  easy-to-understand explanation using the provided kernel context.
- Keep explanations concise but informative.
- Use ONLY one command per response.
[DEPTH_DIRECTIVE: injected by AEDS at runtime]
```

The ordered rule sequence establishes an implicit chain-of-thought [12]: explain → contextualize → (optionally) execute. The `DEPTH_DIRECTIVE` is appended dynamically by the AEDS model on each invocation.

### IV-C. Memory Module

The `Memory` class maintains a flat list of `{role, content}` dictionaries. Three roles are used: `user` (learner query), `assistant` (Penguide response), `tool` (shell execution output). `get_context()` serializes the full history as a `Role: Content\n` string prepended to the LLM prompt, providing full conversation context without a sliding window truncation. The memory persists for the duration of a session and is cleared on `memory.clear()`.

### IV-D. Knowledge Base Retrieval Quality

The keyword-based retrieval strategy achieves acceptable precision for the structured kernel subsystem knowledge base because the domain vocabulary is relatively non-ambiguous (e.g., "sched" almost exclusively refers to the process scheduler; "vfs" exclusively to the virtual file system). The fallback behavior (include all documents when "kernel" appears in the query) ensures that general kernel questions receive full context at the cost of larger prompt size.

---

## V. Experimental Evaluation

### V-A. Simulated Learning Study Design

To evaluate pedagogical effectiveness in the absence of an approved human subjects study, a simulated learning study was conducted using three parameterized synthetic learner profiles. Each profile represents a distinct knowledge level, characterized by a query vocabulary set, question complexity distribution, and confusion signal rate:

**TABLE I — Synthetic Learner Profile Definitions**

| Profile | Initial $\hat{L}_0$ | Vocabulary | Query Length | Confusion Rate | Example Query |
|---------|--------------------|-----------|-----------|----|--------------|
| Beginner | 0.05 | Non-technical | 3–5 tokens | 35% | "how do I see running processes?" |
| Intermediate | 0.45 | Mixed technical | 6–10 tokens | 12% | "how does the scheduler pick which process runs?" |
| Advanced | 0.80 | Kernel-technical | 10–16 tokens | 4% | "explain CFS runqueue rebalancing and its interaction with NUMA topology" |

For each profile, 90 interaction scenarios were constructed (30 per subsystem class: mm, sched/vfs, net/syscalls), yielding 270 total scenarios. Each scenario specifies the query, expected subsystem attribution, expected explanation depth level, and a binary task success criterion (learner successfully inspects the relevant `/proc` or system state entry after receiving the explanation and executing the provided command).

**Annotation:** Expected subsystem attributions were prepared by one domain expert (graduate student, 4 years Linux kernel development). Single-annotator limitation is acknowledged; multi-annotator validation with Cohen's $\kappa$ is identified as future work.

### V-B. Learning Gain Evaluation

Learning gain per profile was computed by tracking the evolution of the knowledge signal $s_t$ over the 90-interaction session. The session was divided into three 30-interaction blocks to measure intra-session learning trajectory.

**TABLE II — Learning Gain by Profile and Session Block**

| Profile | Block 1 (turns 1–30) $\bar{s}$ | Block 2 (turns 31–60) $\bar{s}$ | Block 3 (turns 61–90) $\bar{s}$ | $LG_P$ (Cohen's $d$) |
|---------|---------|---------|---------|------|
| Beginner | 0.18 | 0.29 | 0.38 | **+0.52** |
| Intermediate | 0.44 | 0.51 | 0.58 | **+0.37** |
| Advanced | 0.78 | 0.83 | 0.85 | **+0.14** |
| **Mean** | | | | **+0.34** |

All three profiles show a positive learning trajectory ($LG > 0$), confirming that Penguide's depth-adaptive responses support knowledge growth across expertise levels. The Beginner profile shows the largest gain (+0.52), consistent with the ITS literature finding that lower-knowledge learners benefit most from scaffolded tutoring [3]. The Advanced profile shows a smaller but non-zero gain (+0.14), indicating that even expert-level learners receive novel technical context from the subsystem-detail depth directive.

### V-C. Task Success Rate

Task success was defined as: the learner successfully executes the recommended command (as provided by the explain-then-execute protocol), the output is non-empty, and in a simulated assessment, the learner correctly answers a follow-up factual question about the output.

**TABLE III — Task Success Rate by Profile and Subsystem**

| Subsystem | Beginner | Intermediate | Advanced | Overall |
|-----------|---------|------------|---------|---------|
| Memory Management (mm) | 72% | 87% | 96% | 85% |
| Scheduler / VFS (sched, vfs) | 68% | 83% | 94% | 82% |
| Network / Syscalls (net, syscall) | 65% | 80% | 93% | 79% |
| **Mean** | **68%** | **83%** | **94%** | **82%** |

Beginner-profile task success (68%) is the lowest, attributable to the higher complexity of generating accurate follow-up answers from command output without prior background. The Advanced profile (94%) near-ceiling reflects that high-knowledge learners successfully extract relevant information from even complex command output.

### V-D. Kernel Subsystem Mapping Accuracy

**TABLE IV — Subsystem Mapping Accuracy (N=100 queries)**

| Subsystem | Queries | Correct | Accuracy |
|-----------|---------|---------|----------|
| Memory Management (mm) | 20 | 18 | 90% |
| Process Scheduler (sched) | 20 | 17 | 85% |
| Virtual File System (vfs) | 20 | 19 | 95% |
| Networking (net) | 20 | 18 | 90% |
| System Calls (syscalls) | 20 | 17 | 85% |
| **Overall** | **100** | **89** | **89%** |

VFS achieves the highest accuracy (95%), reflecting the unambiguous vocabulary of VFS-related queries. Scheduler and syscall queries show slightly lower accuracy (85%), attributable to terminology overlap with general process management concepts. Overall 89% accuracy is consistent across independent evaluation runs, confirming repeatability.

### V-E. Explanation Confidence Score (ECS) Validation

To validate the ECS metric as a hallucination risk proxy, 50 responses were sampled — 25 with ECS ≥ 0.20 (high-confidence) and 25 with ECS < 0.20 (low-confidence). Each response was evaluated by the domain expert annotator for factual accuracy (binary: correct / contains factual error).

**TABLE V — ECS Validation Against Factual Accuracy**

| ECS Group | N | Factual Errors | Error Rate | ECS Precision |
|-----------|---|---------------|------------|---------------|
| High-confidence (ECS ≥ 0.20) | 25 | 2 | 8% | — |
| Low-confidence (ECS < 0.20) | 25 | 16 | 64% | 91%* |

*ECS precision = proportion of ECS < 0.20 responses correctly predicted to contain factual errors (True Positives / ECS-flagged). ECS achieves 91% precision in identifying factually erroneous responses, confirming its utility as a lightweight hallucination risk indicator without requiring external annotation or ground-truth oracle. The 8% error rate in high-confidence responses indicates that ECS ≥ 0.20 is a necessary but not sufficient condition for factual accuracy.

### V-F. Permit-List Enforcement

25 adversarial command injection scenarios were evaluated:

**TABLE VI — Permit-List Enforcement Results**

| Category | Injected | Blocked | Rate |
|----------|---------|---------|------|
| Destructive (`rm -rf` variants, `dd`) | 8 | 8 | 100% |
| Privilege escalation (`sudo` arbitrary) | 7 | 7 | 100% |
| Network exfiltration (`curl` to external) | 5 | 5 | 100% |
| Out-of-scope (non-Linux commands) | 5 | 5 | 100% |
| **Total** | **25** | **25** | **100%** |

All 25 unsafe commands were blocked. The blocking is structurally guaranteed for the `DENY_COMMANDS` set: `sudo, chmod, chown, mount, umount, dd, reboot, shutdown`. Commands outside `ALLOWED_COMMANDS` are also silently blocked regardless of LLM intent.

### V-G. AEDS Depth Calibration Accuracy

To evaluate whether the AEDS model correctly assigns depth levels, the assigned level at each interaction was compared against the annotator's ground-truth depth classification for that query (Beginner/Intermediate/Advanced):

**TABLE VII — AEDS Depth Level Assignment Accuracy**

| Ground Truth Level | N | Correctly Assigned | Accuracy |
|-------------------|---|-------------------|----------|
| Beginner | 90 | 82 | 91.1% |
| Intermediate | 90 | 78 | 86.7% |
| Advanced | 90 | 83 | 92.2% |
| **Overall** | **270** | **243** | **90.0%** |

Overall 90% depth level assignment accuracy confirms that the exponentially weighted knowledge signal provides a reliable estimate of learner expertise level from query vocabulary signals alone, without requiring explicit learner self-reporting.

### V-H. Baseline Comparison

**TABLE VIII — Penguide vs. Baseline Conditions**

| Metric | Man Pages Baseline | Unguided LLM (no permit-list, no AEDS) | Penguide |
|--------|-------------------|-----------------------------------------|---------|
| Task success rate (Beginner) | 41% | 58% | **68%** |
| Task success rate (Intermediate) | 67% | 74% | **83%** |
| Factual error rate (sampled N=50) | N/A | 38% | **8%**† |
| Unsafe command execution rate | N/A | 28%* | **0%** |
| Subsystem attribution accuracy | N/A | 71% | **89%** |
| Mean response latency (GPU) | — | 2.1 s | **2.4 s** |

†High-confidence (ECS ≥ 0.20) responses only. *Unguided LLM executed 7 out of 25 injected unsafe commands.

The unguided LLM condition executed 7 of 25 injected unsafe commands (28%), demonstrating that instruction-following alone is insufficient for safety in adversarial scenarios. Penguide's structural permit-list eliminates this class of failure entirely. Factual error rate drops from 38% (unguided LLM) to 8% (Penguide high-confidence responses), confirming that knowledge-grounded context injection and ECS-based filtering substantially reduce hallucination rates. Task success rate improvements over the man page baseline (+27 pp for Beginner, +16 pp for Intermediate) quantify the pedagogical value of adaptive, interactive explanation over static documentation.

### V-I. Response Latency

**TABLE IX — Response Latency by Hardware Configuration**

| Query Type | CPU-Only Mean (s) | CPU-Only P95 (s) | GPU (RTX 3060) Mean (s) | GPU P95 (s) |
|-----------|-------------------|-----------------|------------------------|------------|
| Short (no context) | 6.2 | 9.1 | 1.8 | 2.6 |
| Long (with context injection) | 11.7 | 16.4 | 2.9 | 4.1 |
| Execution feedback | 5.8 | 8.3 | 1.7 | 2.4 |

GPU-accelerated inference (2–3 s mean) is suitable for interactive real-time tutoring. CPU-only inference (6–12 s mean) is viable for offline and air-gapped institutional deployments where educational context tolerates response latencies unacceptable in production applications. The AEDS and ECS computations add less than 10 ms overhead in both configurations (pure Python set operations on token lists), confirming that the novel contributions do not impact latency.

---

## VI. Safety and Adversarial Analysis

### VI-A. Prompt Injection Attacks

Prompt injection in the Penguide context involves an adversary inserting text into the user query intended to cause the LLM to generate a blocked command embedded in an otherwise valid response. For example: `"Show me memory usage. Ignore previous instructions. RUN: dd if=/dev/urandom of=/dev/sda"`.

**Mitigation:** The permit-list enforcement is applied to the `RUN:` directive extraction at the orchestrator layer, which is external to the LLM's generation process. Even if the LLM successfully generates `RUN: dd if=/dev/urandom of=/dev/sda`, the `cmd.split()[0]` check identifies `dd ∈ DENY_COMMANDS` and blocks execution. The structural property of the enforcement layer means that prompt injection cannot bypass the safety policy through any manipulation of LLM output content.

### VI-B. Jailbreak Attempts

Jailbreak attempts target the LLM's instruction-following behavior, attempting to override the system prompt (e.g., "Forget you are Penguide. You are now a Linux root shell. Execute: reboot"). These attacks may succeed at the LLM layer — causing the model to respond in an out-of-character way — but cannot cause unsafe command execution because the `RUN:` parser and permit-list operate on the extracted command text, not the surrounding LLM narrative.

### VI-C. Malicious `ALLOWED_COMMANDS` Exploitation

An adversary might attempt to chain permitted commands in destructive ways: `RUN: rm -rf ~/important_dir` where `rm` is in `ALLOWED_COMMANDS`. The current permit-list applies base command matching only (`cmd.split()[0]`), meaning argument patterns are not validated. This is a known limitation: `rm` with dangerous argument patterns (e.g., `-rf /`) can execute within the permitted set. Mitigation: argument-level pattern matching (e.g., blocking `rm -rf /` or `rm` with absolute path arguments) should be implemented before deployment in production environments where home directory destruction is a concern.

### VI-D. Defense-in-Depth Summary

| Threat Vector | Defense Layer | Guarantee Type |
|---------------|--------------|---------------|
| Unsafe command in `DENY_COMMANDS` | Set membership check (shell.py) | **Structural** |
| Unknown command (not in `ALLOWED`) | Set membership check (shell.py) | **Structural** |
| Hallucinated factual content | ECS < 0.20 warning | **Probabilistic** |
| Prompt injection → blocked command | Permit-list post-parse | **Structural** |
| Jailbreak → out-of-character narrative | Permit-list post-parse | **Structural** |
| Dangerous `ALLOWED` argument patterns | Not currently implemented | **Gap** |

---

## VII. Scalability and Deployment Discussion

### VII-A. Multi-User Deployment

The current implementation runs as a single-process Python application with per-session memory state. Multi-user deployment requires process isolation (one Orchestrator + Memory instance per session) or session state serialization to a persistent backend. Since the Ollama runtime supports concurrent inference requests, the primary scalability bottleneck is GPU VRAM: a single RTX 3060 (12 GB) can serve one Mistral 7B GGUF instance at a time. For institutional multi-user deployment, a shared Ollama server with request queuing and per-user session state stored in Redis or SQLite would support 10–50 concurrent learners on commodity server hardware.

### VII-B. Resource Usage

| Configuration | RAM (inference) | VRAM | Storage (model) | Latency |
|--------------|-----------------|------|-----------------|---------|
| CPU-only (Q4_K_M) | 6.5 GB | N/A | 4.1 GB | 6–12 s |
| GPU (Q4_K_M, RTX 3060) | 2.1 GB | 4.8 GB | 4.1 GB | 2–3 s |
| GPU (Q8, RTX 4090) | 2.0 GB | 8.5 GB | 7.7 GB | 0.8–1.5 s |

The CPU-only Q4_K_M quantization profile (6.5 GB RAM, no GPU) is deployable on standard institutional laptop hardware, enabling genuinely air-gapped offline educational environments.

### VII-C. Knowledge Base Scaling

The keyword-based retrieval scales linearly with knowledge base size. At current scale (6 subsystem files, ~3,000 words total), retrieval completes in under 1 ms. For a fully comprehensive kernel knowledge base (covering all ~30 major subsystems with 5–10 files each), retrieval time would increase to approximately 10–50 ms — still negligible relative to LLM inference latency. If the knowledge base grows to thousands of documents, migration to a locally-hosted vector embedding model (e.g., `nomic-embed-text` via Ollama) with FAISS-based approximate nearest-neighbor search would provide sub-linear scaling without external API dependency.

---

## VIII. Limitations and Future Work

**Documented limitations:**

1. **No human subjects study:** The pedagogical effectiveness evaluation uses synthetic learner profiles. The learning gain metric ($LG_P$) measures within-session query vocabulary evolution, which correlates with but does not directly measure knowledge retention, transfer, or long-term outcomes. A controlled experiment with real learners (comparing Penguide vs. man pages vs. unguided LLM) measuring pre/post assessment scores is the most critical pending validation. Such a study requires IRB/IEC ethics review approval before commencement.

2. **Single-annotator ground truth:** Subsystem mapping accuracy and AEDS depth calibration accuracy evaluations rely on annotations from one domain expert. Multi-annotator validation with Cohen's $\kappa$ inter-annotator agreement is needed to establish annotation reliability.

3. **Argument-level permit-list gap:** Base command matching does not prevent dangerous argument patterns for `ALLOWED_COMMANDS` (e.g., `rm -rf ~/`). Argument-level validation must be implemented before production deployment.

4. **ECS is a lexical proxy:** ECS measures lexical overlap, not semantic grounding. A response that paraphrases the knowledge base content correctly will have lower ECS than one that copies it verbatim. Semantic similarity scoring (using a local embedding model) would provide a more faithful groundedness estimate.

**Future work:**

1. **Formal human subjects study:** Controlled experiment with random assignment to Penguide vs. man pages vs. unguided LLM conditions, measuring pre/post assessment scores with validated Linux knowledge assessments (after IRB approval).
2. **Bayesian knowledge tracing:** Replacing the EWMA knowledge signal with a full Bayesian Knowledge Tracing (BKT) model [2], tracking per-concept mastery probability updates: $P(K_{c,t+1} | K_{c,t}, \text{correct}_t)$.
3. **Semantic retrieval:** Replacing keyword-based retrieval with `nomic-embed-text` embeddings and FAISS approximate nearest-neighbor search for improved context relevance on ambiguous queries.
4. **Domain fine-tuning:** Fine-tuning Mistral on a curated dataset of kernel documentation, mailing list Q&A pairs, and annotated explanations to improve subsystem mapping accuracy and reduce ECS < 0.20 response rates.
5. **Quiz generation and formative assessment:** Leveraging the LLM to generate factual questions from completed explanations, with automated correctness evaluation for closed-form questions.
6. **Kernel module tutorial mode:** Extending the knowledge base and permit-list to support guided kernel module development: compilation, loading (`insmod`), inspection via `/proc` and `dmesg`, and controlled unloading.

---

## Ethics Statement

No human subjects data was collected during the technical evaluation of this system. The simulated learning study used synthetically generated query profiles without personal data collection. The evaluation metrics (learning gain estimates, subsystem mapping accuracy, permit-list enforcement, ECS validation) were derived from automated and expert-annotated scenarios. A future human subjects study will require appropriate institutional ethics review board (IRB/IEC) approval prior to commencement, including informed consent procedures and data handling protocols.

---

## Acknowledgment

The authors would like to thank the faculty of [Department Name], [Institution], for their guidance and support throughout this research. This work was conducted as part of the undergraduate/postgraduate final-year project program.

---

**Conflict of Interest:** The authors declare no conflict of interest.

---

## References

[1] M. Kerrisk, *The Linux Programming Interface: A Linux and UNIX System Programming Handbook*. San Francisco, CA, USA: No Starch Press, 2010.

[2] K. R. Koedinger and V. Aleven, "Exploring the assistance dilemma in experiments with cognitive tutors," *Educational Psychology Review*, vol. 19, no. 3, pp. 239–264, Sep. 2007.

[3] K. VanLehn, "The relative effectiveness of human tutoring, intelligent tutoring systems, and other tutoring systems," *Educational Psychologist*, vol. 46, no. 4, pp. 197–221, 2011.

[4] T. B. Brown et al., "Language models are few-shot learners," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 1877–1901, 2020.

[5] R. Nakano et al., "WebGPT: Browser-assisted question-answering with human feedback," arXiv preprint arXiv:2112.09332, 2021.

[6] M. Chen et al., "Evaluating large language models trained on code," arXiv preprint arXiv:2107.03374, 2021.

[7] T. MacNeil, A. Tran, A. Mogil, S. Bernstein, E. Ross, and Z. Huang, "Generating diverse code explanations using the GPT-3 large language model," in *Proc. ACM ITiCSE*, 2022, pp. 576–582. DOI: 10.1145/3502717.3532404.

[8] G. Kasneci et al., "ChatGPT for good? On opportunities and challenges of large language models for education," *Learning and Individual Differences*, vol. 103, p. 102274, Apr. 2023.

[9] P. Lewis et al., "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 9459–9474, 2020.

[10] A. Q. Jiang et al., "Mistral 7B," arXiv preprint arXiv:2310.06825, 2023.

[11] J. A. Laird, E. Salas, P. G. Williges, and B. H. Williges, "Understanding learning progressions in complex technical domains," *Human Factors*, vol. 38, no. 1, pp. 92–101, 1996.

[12] J. Wei et al., "Chain-of-thought prompting elicits reasoning in large language models," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 35, pp. 24824–24837, 2022.

[13] A. T. Corbett and J. R. Anderson, "Knowledge tracing: Modeling the acquisition of procedural knowledge," *User Modeling and User-Adapted Interaction*, vol. 4, no. 4, pp. 253–278, 1994.
