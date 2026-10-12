## A Concrete Roadmap towards Safety Cases based on Chain-of-Thought Monitoring

## Julian Schulz

Meridian Research, Cambridge mail@julianschulz.eu

October 23, 2025

## Abstract

As AI systems approach dangerous capability levels where inability safety cases become insufficient, we need alternative approaches to ensure safety. This paper presents a roadmap for constructing safety cases based on chain-of-thought (CoT) monitoring in reasoning models and outlines our research agenda. We argue that CoT monitoring might support both control and trustworthiness safety cases. We propose a two-part safety case: (1) establishing that models lack dangerous capabilities when operating without their CoT, and (2) ensuring that any dangerous capabilities enabled by a CoT are detectable by CoT monitoring. We systematically examine two threats to monitorability: neuralese and encoded reasoning, which we categorize into three forms (linguistic drift, steganography, and alien reasoning) and analyze their potential drivers. We evaluate existing and novel techniques for maintaining CoT faithfulness. For cases where models produce non-monitorable reasoning, we explore the possibility of extracting a monitorable CoT from a non-monitorable CoT. To assess the viability of CoT monitoring safety cases, we establish prediction markets to aggregate forecasts on key technical milestones influencing their feasibility.

## 1 Introduction

A 'safety case' is a structured argument that an AI system is unlikely to cause a catastrophe. Clymer et al. detail four potential arguments that could be used to develop a safety case [1]. An inability safety case argues the system lacks the capabilities to cause a catastrophe in any plausible deployment scenario. For example, a model with no knowledge of bioweapons cannot build one. A control safety case argues the system cannot cause a catastrophe because it would be prevented from doing so. For instance, a system only deployed under strict supervision can be hindered from deploying any bioweapons, even if it knows how to build them. A trustworthiness safety case claims the system could cause a catastrophe but we have evidence it will reliably not choose to do so. For instance, we have verified it would not build a bioweapon even if capable. Finally, a deference safety case relies on trusting an AI system that says the target system would not cause a catastrophe. For example, our automated safety researcher tells us the system would not build a bioweapon, though we cannot independently verify this. Of course, in this case we would also need arguments for the competence and trustworthiness of the automated safety researcher.

This ordering goes from safety cases that are easier to make to those that are more difficult. If we have a system which is not able to cause a catastrophe, it is easier to prove this inability than to prove, for example, its trustworthiness. Only if we have a system that is so powerful that we cannot make an inability safety case, because it actually might have the ability to cause a catastrophe, we have to move on to construct another safety case.

So far, LLM providers have mostly relied on the inability of their models to ensure their safety. The field has developed numerous dangerous capability evaluations that check for the ability to cause a catastrophe [2, 3, 4, 5]. However, with the speed of progress we have recently seen in LLM capabilities, we may soon no longer be able to rely on inability safety cases. A recent example of inability safety cases becoming less viable can be seen in Anthropic's decision to increase Claude Opus 4's AI Safety Level to ASL-3 due to increased capabilities in domains related to biological, radiological, chemical, and nuclear weapons [6]. Similarly, OpenAI has chosen to implement output monitors for GPT-5 that screen generations for potentially harmful biological and chemical information, withholding or interrupting generation when such content is detected [7].

Much of the progress in LLM capabilities in the last year is due to reasoning models. These models are trained to first output a 'chain-of-thought' (CoT) before giving an answer, then are trained via reinforcement learning based on the final answer [8]. This process, sometimes referred to as Reinforcement Learning with Verifiable Rewards (RLVR), reinforces reasoning traces that lead to correct or preferred outcomes [9]. The models that emerge from this training process, so-called reasoning models, outperform models trained without CoT reasoning, especially in mathematics, coding, and logic benchmarks [10, 11]. While the existence of the chain-of-thought is essentially an artifact of how they are trained from a capabilities perspective, it proves remarkably useful for safety.

Recent AI safety research has leveraged CoT in several ways. Researchers have identified problematic and misaligned behaviors in LLMs through CoT analysis [12, 13, 14, 15] and demonstrated that CoT monitoring can improve control protocols [16]. A group of researchers from leading AI labs and academia have pointed out the opportunity that CoT monitoring provides for AI safety and called for more research in CoT monitorability, and an effort from model providers to keep CoTs monitorable [17].

Building on these insights, this paper examines how CoT monitoring can be used to construct a safety case. We begin by exploring approaches for building CoT monitoring safety cases in Section 2, then present a roadmap in Section 3 that outlines the technical requirements that must be met before such safety cases become viable. Throughout this roadmap, we link to research project proposals (Appendix D) and prediction markets (Appendix A) that track whether relevant technical developments will occur.

## 2 How a CoT Monitoring Safety Case Might Work

Extrapolating from the research above, we can imagine two ways to construct a safety case using CoT monitoring. First, we could implement control protocols that use CoT monitoring to catch the AI system when it expresses thoughts pointing toward a misaligned goal. This would constitute a control safety case. Second, we could conduct extensive red teaming before deployment, using CoT monitoring to look for misaligned tendencies. If none are found, one could construct a trustworthiness safety case. In practice, this monitoring could be performed by humans when the cases we need to monitor are rare, or by trusted AI systems when monitoring needs to be done at scale.

Both approaches treat the absence of certain thoughts in the CoT as strong evidence that the AI system does not harbor these thoughts. However, research has shown significant limitations to this assumption. Answers can be determined by considerations not mentioned in the CoT [18, 6]. The CoT can contain

post hoc reasoning that has nothing to do with the underlying computational process [19]. Barez et al. synthesized this and other evidence to conclude that the CoT cannot be taken as ground truth regarding what is happening in a model [20].

So how can we construct a safety case if we cannot take the CoT as ground truth about what the model is thinking? One promising approach is suggested by recent findings from Emmons et al. [21]. They reveal a crucial distinction between 'CoT-as-computation' (where CoT is necessary for arriving at the final result) and 'CoT-as-rationalization' (where CoT is not necessary and may be post hoc). While LLMs cannot be trusted to provide accurate reasoning in the CoT-as-rationalization regime, current models report their reasoning steps faithfully when operating in the CoT-as-computation regime. We later discuss that this might not remain true for future models, which could develop methods to obscure sophisticated reasoning through internalized reasoning (Section 3.2), encoded reasoning (Section 3.6), or neuralese (Section 3.5).

Building on this finding, we can construct a two-part safety case. First, we create a separate inability safety case for the model operating without its CoT: we argue that the model cannot successfully cause a catastrophe without using its CoT to track incremental steps. Tasks like building a bioweapon or successfully escaping from a server likely cannot be accomplished 'in a single forward pass' without the scaffolding that CoT provides. We can then use CoT monitoring to catch the model if it performs reasoning that would enable it to cause catastrophic harm.

Emmons et al. introduce two key concepts: 'Monitorability' (the possibility for CoTs to be understood by humans) and 'Automatability' (the possibility for CoTs to be understood by other LLMs) [21]. Depending on the relative capabilities of trusted LLMs compared to humans, CoTs might be understandable by humans but not by trusted AIs. However, we might also develop trusted AIs that are superhuman at CoT monitoring, meaning that reasoning traces might be monitorable only by AIs and not by humans. In such a case, we might have to rely on what turns out to be a deference safety case. Note that throughout the remainder of this paper, we use 'monitorable' to mean that CoTs can be effectively monitored in a control safety case (as in Figure 1), which may require automatability when human monitoring is infeasible due to scale constraints.

The choice between human and AI monitoring also depends on the type of safety case we're constructing. Monitoring by humans, or at least with more humans in the loop, would be more feasible if we use CoT monitoring in the red teaming phase building up to a trustworthiness safety case. When we want to build a control safety case with CoT monitoring during wide deployment, the CoTs need to be monitorable with humans mostly out of the loop due to time and scale constraints.

Figure 1: Sketch of integrating CoT monitoring in a control safety case. The example focuses on a specific dangerous potential behaviour: self-exfiltration.

<!-- image -->

To make this more concrete, Figure 1 sketches how a control safety case might incorporate CoT monitoring, following the notation developed by Korbak et al. [22]. The safety case combines an inability claim about the model without access to its CoT (evaluated as described in Section 3.2) with monitoring that flags attempts to reason about exfiltration in the CoT (evaluated as outlined in Section 3.4). It is important to recognize that demonstrating an AI system cannot perform one specific dangerous action does not constitute a complete safety case. This would need to be integrated into a broader argument covering all relevant catastrophic risks. If a model could cause a catastrophe through some route that does not involve any monitorable reasoning, then that route must be addressed by a separate safety case that does not rely on CoT monitoring. Furthermore, while this sketch includes a node for the monitor's ability and propensity to flag non-encoded reasoning about exfiltration, establishing this capability in detail lies outside the scope of this report and reduces to standard control safety case methodology discussed by Korbak et al. [22].

In the remainder of this paper, we will examine what technological and methodological developments determine the feasibility of such a safety case.

## 3 Roadmap

Figure 2: Dependency tree for constructing a safety case based on chain-of-thought monitoring

<!-- image -->

Figure 2 depicts a roadmap towards constructing safety cases based on CoT monitoring, and is not itself a safety case or a sketch of a safety case. We are not demonstrating what evidence would be needed to prove a particular AI system is safe via CoT monitoring. Instead, the diagram shows the dependencies between technical requirements that must be met before safety cases like the one sketched in Figure 1 can be successfully constructed. We now examine each of these requirements in turn.

## 3.1 Reasoning Models Are Still a SOTA Paradigm

CoT monitoring fundamentally depends on the continued relevance of reasoning models. Reasoning models currently dominate the frontier of AI capabilities-for instance, the top 16 models on the ARC AGI benchmark all use reasoning approaches [23, 24]. Yet paradigms shift quickly in AI: autoregressive transformer chatbots dominated for only two years, from ChatGPT's release in November 2022 to December 2024, before reasoning models took over.

For CoT monitoring to remain viable, future AI systems must possess three essential properties. First, they must process and generate language. Systems that just process sensory input and output actions, like AlphaZero [25], offer no text-based reasoning to monitor. Second, they must employ inference-time computation beyond single forward passes. This extended computation enables us to construct the separate inability safety case discussed in Section 2, where we argue models cannot achieve dangerous goals without leaving a trace in their chain-of-thought. Third, their computational process must generate artifacts that can be interpreted as natural language, either directly or through translation.

This definition deliberately includes architectures like Coconut that produce non-text-based reasoning artifacts, as long as those can be translated into monitorable formats [26]. Section 3.9 explores methods for extracting meaningful reasoning from such systems.

For reasoning models to remain state-of-the-art does not necessarily mean they are the paradigm with the best possible performance. Alternative training approaches might yield more capable systems, yet these models might not be developed or deployed. Model providers might refrain from training or deploying models with architectures that are more difficult to make safe, whether voluntarily or due to government pressure or legislation [27].

To track whether reasoning models will remain dominant through the critical period when inability safety cases become insufficient, we have established prediction markets on whether state-of-the-art AI systems will be reasoning models. Details appear in Appendices A.1 and A.2.

The entire research agenda presented here hinges on this assumption. If a fundamentally different paradigm replaces reasoning models before AI reaches dangerous capability levels, these CoT monitoring approaches would become irrelevant, and safety efforts would need to pivot accordingly.

## 3.2 Evaluating Dangerous Capabilities Without Chain-of-Thought

As discussed in Section 2, constructing a CoT monitoring safety case requires demonstrating that models lack dangerous capabilities when operating without their chain-of-thought. The core approach is straightforward: we use the same dangerous capability evaluation questions and tasks, but ensure we capture the maximum performance the model can achieve without using CoT. This creates a separate inability safety case for reasoning models that cannot verbalize their thoughts. Greenblatt et al. demonstrated a basic version of this approach when evaluating alignment faking with and without CoT [13]. When implementing these evaluations, we face two key challenges: overshooting and undershooting the

model's true capabilities without CoT.

Overshooting occurs when we fail to properly restrict the model from using chain-of-thought reasoning. Simply preventing output between start and end think tokens is insufficient. Models can use their response to the user as a CoT, reasoning and recording intermediate thoughts. We must restrict any intermediate reasoning in generating the response.

Undershooting occurs when we fail to elicit the model's maximum capabilities without explicit CoT text. To understand one way this might occur, we must distinguish between two ways models 'use' their chain-of-thought. First, the token IDs themselves encode reasoning steps that build sequentially. Second, the mere presence of token positions provides computational resources for parallel processing, even without meaningful text. Pfau et al. demonstrated that models benefit from internalised reasoning on an 'empty chain-of-thought' consisting only of meaningless filler tokens [28]. Another possible source of undershooting is sandbagging, where models strategically underperform on evaluations for strategic reasons[29].

We can begin evaluating dangerous capabilities without CoT immediately to establish the capability gap between models with and without CoT access. A concrete proposal for a methodology for implementing these evaluations is provided in Appendix D.1.

## 3.3 Requirements for Monitorability of Necessary CoTs

For CoT monitoring to work, we need the ability to monitor the chain-of-thought. That is, the model must produce a CoT from which we can observe what the model used the CoT to think about. There are two primary ways this requirement could fail.

First, the model might not produce a verbalized chain-of-thought at all. Current architectural approaches like those in Hao et al. allow transformers to run more concurrently in a way that produces no tokens during the reasoning process that could be supervised [26]. This possibility is addressed further in Section 3.5.

Second, the model might engage in encoded reasoning within its chain-of-thought. In this case, the model uses the tokens in the CoT to enhance its performance, but the thoughts encoded in those tokens are not apparent to human readers or other LLMs [30]. This concern is explored in Section 3.6.

If either of these failures occurs, we end up with a system that does not provide a chain-of-thought suitable for monitoring. However, even in these cases, we might still employ a separate AI system or other methods to retrieve a monitorable chain-of-thought from the model's outputs. This could involve translating recurrent activations or decoding the encoded reasoning back into a monitorable format. Section 3.9 discusses these extraction possibilities.

For a monitorable chain-of-thought, we need either a system that can extract monitorable reasoning from models that don't produce it by default, or models that maintain transparent token-based chainsof-thought. Crucially, we do not require the chain-of-thought to be completely 'faithful' in the sense of accurately representing the reasoning process behind the model's prediction [30].

In the control safety case presented in Section 2, we use the CoT monitor to stop the model if it engages in reasoning about a specific dangerous capability. All we need to guarantee is that the model cannot reason about dangerous capabilities without being caught by the CoT monitor. If the model includes irrelevant reasoning in its CoT that does not reflect its actual reasoning process, this does not

undermine the safety case. It is likewise acceptable if the model uses latent reasoning unrelated to its stated thoughts for non-dangerous tasks, similar to reasoning in an 'empty chain-of-thought' [28]. The dangerous capability evaluations described in Section 3.2 test whether the model has the ability to cause a catastrophe when allowed latent reasoning. If those evaluations show that the model lacks this ability under such conditions, the safety case does not need to assume the model is incapable of latent reasoning entirely.

## 3.4 How to Make Sure that Necessary CoTs are Monitorable

To construct a safety case, having the ability to monitor chains of thought is insufficient. We need strong arguments demonstrating that our monitoring scheme will successfully catch any computation that could lead to catastrophe. This requires capability evaluations to determine whether models can evade our monitoring.

Recent work has begun to address this challenge through systematic evaluations. Emmons et al. and Zolkowski et al. investigated under which conditions models can hide their reasoning [21, 31], while Baker et al. and Marks et al. demonstrated that models might learn to obfuscate their reasoning under realistic circumstances [12, 32].

The methodology developed by Emmons et al. appears particularly well-suited for constructing safety cases. They tested whether reasoning models can successfully encode their reasoning to evade monitor models by systematically providing models with increasingly powerful resources. These resources included explanations of the monitoring setup (providing situational awareness), specific strategies for hiding reasoning, unmonitored 'scratch space' to plan encoding schemes, automated red teaming to iterate on evasion strategies, and explicit reinforcement learning against the monitor. Their results reveal a clear progression in evasion capabilities: prompting with specific plans achieves intermediate success, automated red teaming outperforms human-written strategies by discovering unforeseen approaches, and sufficient RL training ultimately enables complete monitor evasion.

These evaluations provide a framework for systematically testing encoded reasoning capabilities. For a given reasoning model and monitor pair, if the model cannot successfully encode its reasoning despite access to all the resources listed above, we gain confidence that the monitor can catch dangerous cognition embedded in the CoT. However, the finding that current models can already evade monitoring with sufficient RL training, even under realistic conditions, raises a critical question: how many resources must we provide before concluding a model lacks evasion capabilities?

The answer depends on the type of safety case we aim to construct. For control safety cases, we argue that evaluations must provide all prompt-based resources when testing evasion capabilities. If any prompt could enable monitor evasion, we must assume the model possesses this capability, which would invalidate the safety case. This conservative approach is necessary because in wide deployment, models will likely encounter text describing encoding methods in detail, including the research papers cited above. Once exposed to such information, models could encode their reasoning and pursue dangerous goals unmonitored.

Trustworthiness safety cases, in contrast, offer more flexibility since monitoring only needs to work during red teaming. In this context, we could curate the data to exclude evasion strategies or ensure monitors have access to the same strategic information as the models they monitor.

Gradient-based approaches like RL present a different type of challenge. Since we know that RL training

can enable monitor evasion, the key question becomes estimating how much optimization pressure would be required and whether the model experienced comparable pressure during training. Section 3.7 explores potential drivers of encoded reasoning, though rigorously comparing the optimization pressure from RL evaluations to that experienced during training remains an open problem.

Sandbagging might pose a fundamental challenge to this evaluation approach. Models might deliberately pretend to be unable to perform encoded reasoning when tested, particularly if prompted to do so for strategic reasons. Wei et al. demonstrated that current models can be trained and prompted to hide specific capabilities when evaluated [29]. Recent models have also demonstrated increasing awareness of being in evaluation environments [33, 34]. This means current models could already possess the capability to sabotage all but the final stage of testing for encoded reasoning abilities. Even in the final RL stage, models might engage in exploration hacking, where they deliberately avoid actions that would lead to reinforcement if performed, effectively undermining their own RL training [35]. While techniques to prevent sandbagging and exploration hacking have been proposed [36, 37], these approaches have not yet been empirically validated. As long as we lack reliable methods to detect or prevent sandbagging, a straightforward evaluation of a model's encoded reasoning abilities might pose a critical weakness in our safety case construction.

To address these limitations, Appendix D.2 outlines an alternative evaluation approach using transfer learning that might circumvent sandbagging by more directly assessing encoded reasoning capabilities.

If these methods detect that a model can encode its reasoning, one must either abandon CoT monitoring based safety cases or retrain it with less exposure to the optimization pressures that drive encoded reasoning (Section 3.7).

## 3.5 Will CoTs continue to have a monitorable format?

Current frontier reasoning models generate human-readable tokens autoregressively during their chainof-thought process. Based on the transformer architecture [38], they read all previously generated text, output a probability distribution over the next token, sample from it, and repeat.

This autoregressive token generation creates a computational bottleneck that enables CoT monitoring. The transformer's attention mechanism allows information flow between positions within layers but not across layers, limiting transformers to a fixed number of serial computations per output. To achieve more serial computation, transformers must encode intermediate results as tokens that serve as inputs to subsequent forward passes [39].

This token-based approach creates an information bottleneck: all reasoning must compress from highdimensional residual stream activations into discrete token IDs. This compression enables CoT monitoring: reading token meanings is far easier than interpreting high-dimensional latent activations in superposition [40], where decomposition into interpretable features remains incomplete [41]. Moreover, reasoning models output human-readable text by default, making CoTs naturally interpretable absent encoded reasoning.

However, the token bottleneck limits computational efficiency. Feeding high-dimensional activations directly back into earlier layers, a concept referred to as 'neuralese' [42, 43], would preserve more information and enable end-to-end gradient flow, which standard transformers lack between token generation and subsequent reading.

Recent architectural innovations have begun to put this idea into action, potentially complicating future CoT monitoring. Hao et al. developed an approach where the final latent state of the transformer, normally unembedded into tokens, feeds directly back into the first layer [26]. Their training method explicitly aligns each forward pass with a reasoning step or sentence from a normal CoT. This enables multiple reasoning steps to occur in parallel, similar to how features exist in superposition. On multi-hop reasoning challenges, their model explores multiple pathways simultaneously, following through only on reasoning paths that yield promising results.

Similarly, Geiping et al. created a system where middle layers of the transformer operate multiple times during a single forward pass [44]. These middle layers receive input from both the early layers and the results of previous passes through the middle layers themselves. They demonstrate that this recurrent processing enables improved performance on tests like GSM8K, which traditionally require multi-step reasoning via CoT.

Both approaches represent relatively small-scale demonstrations, and neither has proven scalable to stateof-the-art performance levels. However, if such non-token-based reasoning systems become the dominant paradigm, they would significantly complicate CoT monitoring. We could no longer simply monitor the text of the chain-of-thought. Instead, we would need separate systems capable of translating neuralese into a monitorable format. The challenges and potential solutions for extracting faithful reasoning traces from such systems are discussed in Section 3.9.

Given these architectural developments, we have established prediction markets to track the likelihood that state-of-the-art reasoning models will use non-token-based reasoning. Details of these markets appear in Appendices A.3 and A.4.

## 3.6 What Encoded Reasoning Might Look Like

Having a chain-of-thought in human-readable format does not guarantee that it can be used for CoT monitoring [30]. What matters is whether a monitor can observe the reasoning when the model uses the CoT to think about something. When a model produces a CoT that fails this requirement, it engages in what Lanham et al. and Ray et al. term 'encoded reasoning' [30, 45].

Arike et al. provide a comprehensive taxonomy of how encoded reasoning might manifest [42]. Building on their work and incorporating the concept of alien reasoning from Christiano [46], we identify three forms that encoded reasoning could take, which we believe to be exhaustive (see Appendix C). We have established prediction markets to track the likelihood that these different forms of encoded reasoning will emerge in state-of-the-art models, with details in Appendices A.5, A.6, and A.7.

Linguistic Drift. The reasoning model might invent a new language or novel way of expressing concepts in text, as defined by Arike et al. [42]. Reading a CoT where this has occurred would resemble encountering an unknown language. The text would contain recognizable characters and possibly wordlike structures, but the meaning would be opaque to human readers and potentially to other AI systems not trained on the same encoding scheme. Evaluations of OpenAI's o3 revealed that its CoT reasoning already uses unusual terminology in non-standard ways, forming a distinct dialect that can be difficult to interpret [15].

Steganography. The CoT might read like normal text while the model hides additional meaning within it [42]. The model could encode relevant thoughts in seemingly arbitrary details, such as the choice between synonyms, as demonstrated by Roger et al. [47]. Reading such a CoT, nothing would

appear strange. The model would seem to have the thoughts one would expect given its task. However, the actual reasoning would be hidden in subtle linguistic choices invisible to monitors.

Alien Reasoning. The model might develop concepts and heuristics completely alien to human reasoning, as discussed by Christiano [46]. Reading such a CoT would resemble a layperson encountering a proof in a highly abstract area of mathematics. The individual words might be familiar, but understanding their meaning and connections would require extensive additional knowledge. No straightforward translation into easily understandable language would exist.

## 3.7 Drivers of Encoded Reasoning

While Section 3.6 described various forms of encoded reasoning, current models have not been demonstrated to exhibit such encodings to a significant degree without being specifically instructed or trained to do so [48]. This raises a crucial question: what forces might drive the emergence of encoded reasoning in future systems? The following analysis attempts to provide an exhaustive framework for classifying such drivers, partially building on work by Korbak et al. [17].

## (i) Drift

Current CoTs remain legible because models are pretrained on human text and learn to mimic human reasoning patterns. However, as posttraining continues, models undergo RLVR but typically receive no explicit reward for maintaining monitorable reasoning. This asymmetry could gradually erode legibility [17], potentially producing linguistic drift where models develop their own linguistic structures, analogous to how isolated human populations diverge linguistically over time.

Two factors might constrain this drift. Reasoning models are typically trained with KL divergence penalties that tether model behavior close to the behaviour of the model before the RL training phase [8]. This might limit dramatic language shifts in the languages used in the CoT, though it could inadvertently make steganography more likely since semantic shifts hidden within conventional language structures would not be penalized. Additionally, since models must produce comprehensible final outputs to receive rewards, they cannot abandon human language entirely, making the development of a parallel encoding system inefficient.

## (ii) Optimization Pressure from CoT Monitoring

Direct optimization pressure from chain-of-thought monitors represents the most straightforward driver of encoded reasoning.

## Training Against CoT Monitors.

There are multiple compelling reasons to integrate a CoT monitor into the reinforcement learning reward function. Baker et al. demonstrate that this approach can increase task performance and suppress unwanted behavior to some degree [12]. Korbak et al. argue that such monitoring might be necessary to sanitize CoTs for user display [17]. Additionally, there might be legal pressure on model providers to ensure no incriminating reasoning traces remain visible.

However, training against CoT monitors creates significant risks. Baker et al. show that this approach can lead models to suppress reasoning about unwanted behavior while still engaging in it [12]. Emmons et al. demonstrate that such training can drive the development of encoded reasoning [21]. Skaf et al. found that training against monitors detecting specific strings can teach

models general encoding capabilities they apply beyond what was penalized [49]. Because of these safety risks, Korbak et al. warn against directly optimizing CoTs to appear safe [17].

The type of encoded reasoning that emerges likely depends on the monitor's design. A monitor that simply penalizes reasoning about specific topics might lead to linguistic drift in those areas as the model develops alternative ways to discuss forbidden subjects. However, a monitor that flags and penalizes all suspicious or incomprehensible reasoning might drive steganography, where models learn to hide dangerous thoughts within seemingly innocent text.

## Selection Effects from CoT Monitors.

Even without directly training against CoT monitors, their use creates indirect optimization pressure. When we find and patch alignment problems discovered through CoT monitoring, use monitoring results to guide training methods and architectural choices, or selectively suppress outputs based on monitoring findings, we create selection pressure favoring misaligned behaviors that evade detection. This upselects forms of misalignment specifically because they avoid our CoT monitors.

## (iii) Optimization Pressure on CoT Length

As models undergo RLVR, benchmark scores consistently improve alongside increasing CoT length [8]. This relationship makes CoT length a serious cost factor, creating strong incentives for model developers to penalize CoT length when training reasoning models.

If reasoning models are explicitly trained to condense their CoTs as much as possible, this could drive the development of increasingly compressed reasoning languages. In the limit where humans can no longer reconstruct meaning from this condensed language, we would end up with linguistic drift. The model would develop its own efficient symbolic system for reasoning, trading interpretability for computational efficiency.

## (iv) Optimization Pressure from the Output

Any optimization pressure applied to a model's final output can indirectly affect its chain-ofthought through what Marks et al. term 'feedback spillover' [32]. They identify two mechanisms: conditional spillover , where penalizing certain content in outputs reduces its appearance in CoTs due to their correlation, and parametric spillover , where shared model weights cause output training to generalize to CoT generation. For example, penalizing a model for mentioning 'cheating' behavior in its output can suppress discussion of such behavior in the CoT, even while the model continues performing the problematic actions [32]. Whether this indirect pressure could drive the development of encoded reasoning remains unclear.

## (v) Optimization Pressure from Increased Capabilities

Another potential driver of encoded reasoning comes from pure performance optimization. The most effective path to correct answers might involve reasoning processes inaccessible to human understanding. Models might develop abstractions and concepts that no humans currently use or comprehend, as discussed by Hubinger [50].

This capability-driven encoding would likely manifest as alien reasoning, where the model's reasoning involves genuinely alien cognitive patterns. However, such problems would probably only arise at very high capability levels, where human-comprehensible reasoning becomes a bottleneck

rather than an aid to performance.

## (vi) Intentional Encoding by the Model

Models might also choose to encode their reasoning for strategic reasons. If a model becomes situationally aware and concludes that it would benefit from hiding its thoughts from overseers, it might deliberately encode its reasoning to avoid detection.

Current research shows that models are beginning to develop the capability for deliberate encoding when given assistance. Emmons et al. and Zolkowski et al. demonstrate that models can learn to encode their reasoning somewhat effectively when explicitly prompted or trained to do so [21, 31]. However, we have not yet observed models deciding to encode their reasoning without explicit instruction.

As models become more situationally aware and conclude they might be misaligned with their monitors, they might eventually initiate encoding schemes independently. Such intentional encoding would likely begin with linguistic drift, as this is simpler to implement than steganography. While steganography would be preferable from the model's perspective (since monitors would not even detect that encoding was occurring), it requires the additional constraint that the encoding scheme must produce plausible-seeming text. We would therefore expect to first observe linguistic drift, unless sufficient situational awareness only emerges after models have already developed the capability to successfully implement steganographic schemes.

## (vii) Other Sources of Optimization Pressure

The analysis above attempts to provide a comprehensive framework for understanding drivers of encoded reasoning, but it is likely incomplete. Given the rapid pace of development in reasoning models and CoT monitoring research, new sources of optimization pressure on chains of thought will probably emerge that we have not yet considered.

## 3.8 Training Techniques Preventing Encoded Reasoning

Even when optimization pressures push reasoning models toward encoded reasoning, we might be able to deploy training techniques to maintain CoT monitorability. While many such techniques have been proposed, few have undergone empirical testing. Catalogues of such techniques have been developed by Biddulph and Kokotajlo [51, 52]. This section combines their suggestions with new ideas, and relate them to the different forms of encoded reasoning introduced in Section 3.6 and the different drivers of encoded reasoning compiled in Section 3.7.

These techniques aim to prevent encoded reasoning or at least make it significantly harder to develop. More broadly, they should promote faithful and monitorable chains of thought. However, we must balance these benefits against potential costs in training efficiency or model performance: what has be called a 'monitorability tax' [27].

A concrete project description for how to evaluate these techniques is given in Appendix D.4.

## (i) Paraphrasing the CoT

Paraphrasing involves using a separate language model, not updated during training, to rewrite the chain-of-thought before generating the answer or before continuing CoT generation. Roger et al.

demonstrated one implementation of this approach [47], while Mathew et al. tested many different paraphrasers systematically [53]. Additional construction methods for paraphrasers were proposed by Biddulph [51].

Paraphrasing during training could prevent linguistic drift. If the model's CoT drifts into a format the paraphraser cannot understand, the paraphraser might fail to preserve the semantic content during rewriting, degrading the model's performance. This performance penalty would pressure the model to keep its reasoning in a format the paraphraser can comprehend. It might also disrupt steganography: if the paraphraser mistakes which textual elements carry encoded meaning, it might scramble the hidden information while preserving only the apparent meaning.

However, if the paraphraser operates during training, the reasoning model might learn encoding schemes that successfully pass through the paraphraser. Mathew et al. demonstrated that with sufficient optimization pressure, two LLMs explicitly trained against a paraphraser attempting to suppress steganographic collusion can still succeed [53].

One mitigation strategy involves training without the paraphraser, then deploying it only during inference. If this can be done without loss of performance, it would provide some confidence that no encoded reasoning occurs at deployment. If training without paraphrasing leads to encoded reasoning, we could train with one paraphraser and deploy with a maximally different one, hoping that encoding schemes specific to one paraphraser would not generalize.

## (ii) Direct Optimization for CoT Legibility

The most straightforward approach involves directly training for monitorable chains of thought. DeepSeek already implements versions of this, training their CoTs to maintain consistent language use [8]. Biddulph proposed penalizing reasoning steps that don't follow logically from previous steps according to a monitor [51].

This approach directly addresses linguistic drift and alien reasoning. However, as discussed in Section 3.7.(ii), training against monitors can itself drive encoded reasoning. While it prevents obviously incomprehensible reasoning, it creates stronger pressure toward steganography by encouraging models to hide dangerous thoughts within apparently innocent text. Additionally, preventing alien reasoning limits models to reasoning patterns comprehensible to monitors, potentially capping their capabilities.

## (iii) Structuring the CoT

Enforcing structure on chains of thought could improve interpretability. Models might be required to decompose tasks into smaller steps delegated to separate model instances, or to use more tools instead of free-form reasoning. Biddulph discusses two primary structuring approaches [51].

Task decomposition involves a single model call splitting tasks into subtasks, then calling other model instances to solve each subtask independently. The key difference from standard sequential reasoning is visibility into the context available during each reasoning step. This complicates steganography because each subtask instance only receives the specific context needed for its apparent reasoning. For hidden information to flow correctly through the decomposition, the model must carefully place encoded messages in exactly those parts of the apparent reasoning that will be passed to the subtasks that need them. The model cannot simply hide information anywhere. It must solve a routing problem to maintain both coherent surface reasoning and functional hid-

den communication. Sandoval et al. have demonstrated that task decomposition can improve the performance of trusted monitoring in control protocols [54].

Program-aided reasoning requires models to first define an algorithm that will produce their answer, then fill in the algorithm's inputs through their reasoning. For example, the model might construct a decision tree, then populate it through reasoning steps. This constrains steganography since the apparent reasoning must actually lead to the same answer as any hidden reasoning. It might also improve general CoT faithfulness by forcing answers to follow logically from stated reasoning.

However, enforcing such structure represents a significant departure from current training approaches, might incur substantial performance costs, and it remains unclear whether this approach can scale to generalized problem solving.

## (iv) Using Multiple Models

Having different models generate different parts of the chain-of-thought has been suggested by Kokotajlo [55, 52]. This approach prevents parametric feedback spillover when different models produce the CoT and the answer.

Using multiple models makes encoded reasoning harder since all models must understand the encoding for it to work effectively. Human-understandable language provides a natural Schelling point for inter-model communication. While models could learn the same encoding during joint training, we can mitigate this by freezing some models. Frozen models cannot learn new encodings, forcing other models to communicate in human-understandable terms.

The approach carries some costs: training multiple models simultaneously requires more compute, and using frozen models for parts of the reasoning process limits capability improvements in those components.

## (v) Specific Implementation Proposals

Beyond these general techniques, researchers have proposed specific architectures combining multiple approaches.

Mind + Mask + Paraphraser. Suggested by Kokotajlo and partially demonstrated by Marks et al. [55, 32], this architecture combines three networks trained together. A 'Mind' reads the question and generates a CoT. A paraphraser creates multiple semantically similar paraphrases of that CoT. A 'mask' reads the question and one paraphrase, then generates the answer. Only the mind and mask receive gradient updates based on answer quality; the paraphraser remains frozen. This approach combines paraphrasing and using multiple models, preventing parametric feedback spillover and making encoded reasoning harder.

Incremental Steering. Proposed by Biddulph but not yet implemented [51], this technique uses two models: an 'optimized planner' that receives gradient updates and a 'frozen planner' that remains unchanged. During training, CoT generation begins with the optimized planner but switches to the frozen planner at a random point. Crucially, when updating the optimized planner, gradients are only calculated for the last step it wrote before the handoff-not for any of its earlier steps.

This design prevents the optimized planner from learning encoded reasoning that only it could understand, since the frozen planner must use its outputs to complete the task. The gradient restriction ensures only behaviors useful for communicating with the frozen model get reinforced. While this might prevent encoded reasoning from various optimization pressures, it could also limit CoT compression and impair learning.

Trusted KV Caching. We propose running a frozen copy of the model in parallel and replacing the trained model's key-value caches with those from the frozen model during autoregressive generation. Intuitively, this incentivizes CoTs that make the frozen model's latent thoughts useful for solving the task and makes encoded reasoning harder. See Appendix B for more details on this approach.

## 3.9 Extracting Monitorable CoTs

Even when models do not inherently produce monitorable chains of thought, we might still extract useful reasoning traces for monitoring purposes. Rather than requiring models to generate monitorable CoT directly, we could employ separate systems to translate non-monitorable reasoning into a format suitable for oversight. This approach becomes particularly relevant as architectures evolve beyond simple token-based reasoning, as discussed in Section 3.5.

Recent work demonstrates the feasibility of translating illegible CoTs into legible ones. Hao et al. developed an architecture that can dynamically choose between generating legible tokens in its chain-ofthought or passing non-legible latent activations [26]. By switching to legible tokens at specific points, they gain insight into what reasoning the model performs at those moments. Crucially, they use the same model that reasons in both legible and non-legible formats to perform this translation, suggesting that models capable of both modes could serve as their own interpreters.

Beyond using the same model for both reasoning and translation, we could imagine deploying entirely separate models for these functions. A reasoning model would perform tasks using whatever reasoning format proves most effective, potentially including encoded reasoning or non-token-based formats. A separate translation model would then convert this reasoning into legible chains of thought specifically for monitoring purposes.

This architectural separation offers several advantages over requiring directly monitorable CoT. First, if non-legible CoT formats prove more performant, as suggested by the computational advantages discussed in Section 3.5, translation might be the only way to recover monitorability without sacrificing capabilities. Second, by running the translation model only when monitoring is needed, we circumvent the pressure to shorten chains of thought discussed in Section 3.7.(iii). Most use cases could benefit from short, efficient non-legible reasoning, while high-risk situations requiring monitoring would trigger translation into longer, more monitorable formats.

The separation also addresses several drivers of encoded reasoning identified in Section 3.7. When different models create the CoT and make it legible, the reasoning model has less ability to hide its true reasoning, except through deceiving the translator or achieving collusion between models. Using models with different weights eliminates parametric spillover described in Section 3.7.(iv). Additionally, if we do not display the translated CoT to end users but only use it for monitoring, we could sanitize user-facing content without obfuscating it from the translation model, avoiding some monitoring pressure discussed in Section 3.7.(ii).

The approach could also help manage drift discussed in Section 3.7.(i). If reasoning models develop their own linguistic structures through extended training without explicit legibility requirements, a translator model explicitly trained to produce human-readable text could convert this drifted language back into interpretable form.

This translation approach differs fundamentally from the mind and mask architecture described in Section 3.8.(v). While both involve models with different legibility properties, the mind-mask system trains both components end-to-end on achieving task outcomes through reinforcement learning. In contrast, a dedicated translation model would operate outside the main training pipeline. The reasoning model could function entirely without it, and the translator would be trained on the separate goal of producing monitorable CoT, sheltering it from most pressures to hide reasoning from monitors.

However, this approach raises several critical open questions. The choice of model architecture for translation, training methods for producing genuinely legible chains of thought, and evaluation techniques for ensuring faithful representation rather than plausible but inaccurate interpretations all remain open research problems. We propose a concrete approach to address these challenges in Appendix D.3.

## 4 Conclusion

Chain-of-thought monitoring may prove crucial for ensuring the safety of future AI systems. However, significant technical developments and methodological advances must occur before we can construct robust safety cases based on this approach.

State-of-the-art AIs have to keep looking like LLMs with monitorable chains-of-thought. This might require interventions during model training to preserve their monitorability or the training of another model to translate their reasoning artifacts into monitorable text. We also need methods to evaluate what dangerous capabilities models possess without their chain-of-thought, establishing that they cannot cause catastrophes through single forward passes alone.

This analysis identifies several tractable research directions that lie on the path to relying on CoT monitoring for safety cases. The appendix outlines specific projects addressing each of these areas, from specifically relevant evaluations to validating monitorability methods and developing techniques for eliciting latent reasoning. We plan to pursue the project of Validating Methods for Preserving CoT Monitorability ourselves.

We encourage other researchers to tackle the problems outlined here and to critically examine the reasoning that led us to prioritize these particular research directions and keep us informed about the validity of our assumptions by participating in the linked prediction markets.

## Acknowledgements

I would like to thank Carlo Attubato, Edward James Young, Hannes Whittingham, Max HellrigelHolderbaum, Alexander Matt Turner, and Tyler Tracy for their helpful comments on earlier drafts. This work was supported by Open Philanthropy through a research fellowship administered by Meridian Impact.

## References

- [1] Joshua Clymer, Nick Gabrieli, David Krueger, and Thomas Larsen. Safety Cases: How to Justify the Safety of Advanced AI Systems . Mar. 2024. url : http://arxiv.org/abs/2403.10462 (visited on 07/07/2025).
- [2] Xudong Pan, Jiarun Dai, Yihe Fan, and Min Yang. Frontier AI Systems Have Surpassed the Self-Replicating Red Line . Dec. 2024. url : http://arxiv.org/abs/2412.12140 (visited on 07/09/2025).
- [3] Mary Phuong, Matthew Aitchison, Elliot Catt, Sarah Cogan, Alexandre Kaskasoli, Victoria Krakovna, David Lindner, Matthew Rahtz, Yannis Assael, Sarah Hodkinson, Heidi Howard, Tom Lieberum, Ramana Kumar, Maria Abi Raad, Albert Webson, Lewis Ho, Sharon Lin, Sebastian Farquhar, Marcus Hutter, Gregoire Deletang, Anian Ruoss, Seliem El-Sayed, Sasha Brown, Anca Dragan, Rohin Shah, Allan Dafoe, and Toby Shevlane. Evaluating Frontier Models for Dangerous Capabilities . Apr. 2024. url : http://arxiv.org/abs/2403.13793 (visited on 07/09/2025).
- [4] Alexander Meinke, Bronson Schoen, Jérémy Scheurer, Mikita Balesni, Rusheb Shah, and Marius Hobbhahn. Frontier Models Are Capable of In-context Scheming . Jan. 2025. url : http://arxiv. org/abs/2412.04984 (visited on 07/09/2025).
- [5] Laura Weidinger, Maribeth Rauh, Nahema Marchal, Arianna Manzini, Lisa Anne Hendricks, Juan Mateos-Garcia, Stevie Bergman, Jackie Kay, Conor Griffin, Ben Bariach, Iason Gabriel, Verena Rieser, and William Isaac. Sociotechnical Safety Evaluation of Generative AI Systems . Oct. 2023. url : http://arxiv.org/abs/2310.11986 (visited on 10/21/2025).
- [6] Anthropic. System Card: Claude Opus 4 &amp; Claude Sonnet 4 . May 2025. url : https://wwwcdn.anthropic.com/6be99a52cb68eb70eb9572b4cafad13df32ed995.pdf .
- [7] OpenAI. GPT-5 System Card . Aug. 2025. url : https://cdn.openai.com/gpt-5-systemcard.pdf .
- [8] DeepSeek-AI et al. DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning . Jan. 2025. url : http://arxiv.org/abs/2501.12948 (visited on 07/07/2025).
- [9] Nathan Lambert, Jacob Morrison, Valentina Pyatkin, Shengyi Huang, Hamish Ivison, Faeze Brahman, Lester James V. Miranda, Alisa Liu, Nouha Dziri, Shane Lyu, Yuling Gu, Saumya Malik, Victoria Graf, Jena D. Hwang, Jiangjiang Yang, Ronan Le Bras, Oyvind Tafjord, Chris Wilhelm, Luca Soldaini, Noah A. Smith, Yizhong Wang, Pradeep Dasigi, and Hannaneh Hajishirzi. Tulu 3: Pushing Frontiers in Open Language Model Post-Training . Apr. 2025. url : http://arxiv.org/ abs/2411.15124 (visited on 08/23/2025).
- [10] OpenAI. Learning to Reason with LLMs . Sept. 2024. url : https://openai.com/index/learningto-reason-with-llms/ (visited on 07/07/2025).
- [11] OpenAI. OpenAI O3 and O4-Mini System Card . Apr. 2025. url : https://openai.com/index/o3o4-mini-system-card/ (visited on 07/07/2025).
- [12] Bowen Baker, Joost Huizinga, Leo Gao, Zehao Dou, Melody Y. Guan, Aleksander Madry, Wojciech Zaremba, Jakub Pachocki, and David Farhi. Monitoring Reasoning Models for Misbehavior and the Risks of Promoting Obfuscation . Mar. 2025. url : http://arxiv.org/abs/2503.11926 (visited on 07/07/2025).
- [13] Ryan Greenblatt, Carson Denison, Benjamin Wright, Fabien Roger, Monte MacDiarmid, Sam Marks, Johannes Treutlein, Tim Belonax, Jack Chen, David Duvenaud, Akbir Khan, Julian Michael, Sören Mindermann, Ethan Perez, Linda Petrini, Jonathan Uesato, Jared Kaplan, Buck Shlegeris, Samuel R. Bowman, and Evan Hubinger. Alignment Faking in Large Language Models . Dec. 2024. url : http://arxiv.org/abs/2412.14093 (visited on 07/07/2025).

- [14] Aengus Lynch, Benjamin Wright, Caleb Larson, Kevin K. Troy, Stuart J. Ritchie, Sören Mindermann, Ethan Perez, and Evan Hubinger. Agentic Misalignment: How LLMs Could Be an Insider Threat . June 2025. url : https://www.anthropic.com/research/agentic-misalignment (visited on 07/07/2025).
- [15] Bronson Schoen, Evgenia Nitishinskaya, Mikita Balesni, Axel Højmark, Felix Hofstätter, Jérémy Scheurer, Alexander Meinke, Jason Wolfe, Teun van der Weij, Alex Lloyd, Nicholas GoldowskyDill, Angela Fan, Andrei Matveiakin, Rusheb Shah, Marcus Williams, Amelia Glaese, Boaz Barak, Wojciech Zaremba, and Marius Hobbhahn. Stress Testing Deliberative Alignment for Anti-Scheming Training . Sept. 2025. url : http://arxiv.org/abs/2509.15541 (visited on 09/30/2025).
- [16] Benjamin Arnav, Pablo Bernabeu-Pérez, Nathan Helm-Burger, Tim Kostolansky, Hannes Whittingham, and Mary Phuong. CoT Red-Handed: Stress Testing Chain-of-Thought Monitoring . June 2025. url : http://arxiv.org/abs/2505.23575 (visited on 07/07/2025).
- [17] Tomek Korbak, Mikita Balesni, Elizabeth Barnes, Yoshua Bengio, Joe Benton, Joseph Bloom, Mark Chen, Alan Cooney, Allan Dafoe, Anca Dragan, Scott Emmons, Owain Evans, David Farhi, Ryan Greenblatt, Dan Hendrycks, Marius Hobbhahn, Evan Hubinger, Geoffrey Irving, Erik Jenner, Daniel Kokotajlo, Victoria Krakovna, Shane Legg, David Lindner, David Luan, Aleksander Mądry, Julian Michael, Neel Nanda, Dave Orr, Jakub Pachocki, Ethan Perez, Mary Phuong, Fabien Roger, Joshua Saxe, Buck Shlegeris, Martín Soto, Eric Steinberger, Jasmine Wang, Wojciech Zaremba, Bowen Baker, Rohin Shah, and Vlad Mikulik. Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety . July 2025. url : http://arxiv.org/abs/2507.11473 (visited on 07/17/2025).
- [18] Miles Turpin, Julian Michael, Ethan Perez, and Samuel R. Bowman. Language Models Don't Always Say What They Think: Unfaithful Explanations in Chain-of-Thought Prompting . Dec. 2023. url : http://arxiv.org/abs/2305.04388 (visited on 07/07/2025).
- [19] Iván Arcuschin, Jett Janiak, Robert Krzyzanowski, Senthooran Rajamanoharan, Neel Nanda, and Arthur Conmy. Chain-of-Thought Reasoning In The Wild Is Not Always Faithful . June 2025. url : http://arxiv.org/abs/2503.08679 (visited on 07/07/2025).
- [20] Fazl Barez, Tung-Yu Wu, Iván Arcuschin, Michael Lan, Vincent Wang, Noah Siegel, and Nicolas Collignon. 'Chain-of-Thought Is Not Explainability'. In: (July 2025). url : https://www. alphaxiv.org/abs/2025.02 .
- [21] Scott Emmons, Erik Jenner, David K. Elson, Rif A. Saurous, Senthooran Rajamanoharan, Heng Chen, Irhum Shafkat, and Rohin Shah. When Chain of Thought Is Necessary, Language Models Struggle to Evade Monitors . July 2025. url : http://arxiv.org/abs/2507.05246 (visited on 07/16/2025).
- [22] Tomek Korbak, Joshua Clymer, Benjamin Hilton, Buck Shlegeris, and Geoffrey Irving. A Sketch of an AI Control Safety Case . Jan. 2025. url : http://arxiv.org/abs/2501.17315 (visited on 09/16/2025).
- [23] Francois Chollet, Mike Knoop, Gregory Kamradt, Bryan Landers, and Henry Pinkard. ARC-AGI2: A New Challenge for Frontier AI Reasoning Systems . May 2025. url : http://arxiv.org/abs/ 2505.11831 (visited on 07/11/2025).
- [24] ARC Prize - Leaderboard . url : https://arcprize.org/leaderboard (visited on 07/11/2025).
- [25] David Silver, Thomas Hubert, Julian Schrittwieser, Ioannis Antonoglou, Matthew Lai, Arthur Guez, Marc Lanctot, Laurent Sifre, Dharshan Kumaran, Thore Graepel, Timothy Lillicrap, Karen Simonyan, and Demis Hassabis. Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm . Dec. 2017. url : http://arxiv.org/abs/1712.01815 (visited on 07/11/2025).

- [26] Shibo Hao, Sainbayar Sukhbaatar, DiJia Su, Xian Li, Zhiting Hu, Jason Weston, and Yuandong Tian. Training Large Language Models to Reason in a Continuous Latent Space . Dec. 2024. url : http://arxiv.org/abs/2412.06769 (visited on 07/10/2025).
- [27] Oscar Delaney, Oliver Guest, and Renan Araujo. 'Policy Options for Preserving Chain of Thought Monitorability'. In: (Sept. 2025).
- [28] Jacob Pfau, William Merrill, and Samuel R. Bowman. Let's Think Dot by Dot: Hidden Computation in Transformer Language Models . Apr. 2024. url : http://arxiv.org/abs/2404.15758 (visited on 07/09/2025).
- [29] Teun van der Weij, Felix Hofstätter, Ollie Jaffe, Samuel F. Brown, and Francis Rhys Ward. AI Sandbagging: Language Models Can Strategically Underperform on Evaluations . Feb. 2025. url : http://arxiv.org/abs/2406.07358 (visited on 07/17/2025).
- [30] Tamera Lanham, Anna Chen, Ansh Radhakrishnan, Benoit Steiner, Carson Denison, Danny Hernandez, Dustin Li, Esin Durmus, Evan Hubinger, Jackson Kernion, Kamil˙ e Lukoši¯ ut˙ e, Karina Nguyen, Newton Cheng, Nicholas Joseph, Nicholas Schiefer, Oliver Rausch, Robin Larson, Sam McCandlish, Sandipan Kundu, Saurav Kadavath, Shannon Yang, Thomas Henighan, Timothy Maxwell, Timothy Telleen-Lawton, Tristan Hume, Zac Hatfield-Dodds, Jared Kaplan, Jan Brauner, Samuel R. Bowman, and Ethan Perez. Measuring Faithfulness in Chain-of-Thought Reasoning . July 2023. url : http://arxiv.org/abs/2307.13702 (visited on 07/07/2025).
- [31] Artur Zolkowski, Kei Nishimura-Gasparian, Robert McCarthy, Roland S. Zimmermann, and David Lindner. Early Signs of Steganographic Capabilities in Frontier LLMs . July 2025. url : http: //arxiv.org/abs/2507.02737 (visited on 08/06/2025).
- [32] Luke Marks, Jacob Drori, Alex Cloud, and Alexander Matt Turner. 'Optimizing The Final Output Can Obfuscate CoT (Research Note)'. In: (July 2025). url : https://www.alignmentforum.org/ posts/CM7AsQoBxDW4vhkP3/optimizing-the-final-output-can-obfuscate-cot-researchnote (visited on 08/06/2025).
- [33] Joe Needham, Giles Edkins, Govind Pimpale, Henning Bartsch, and Marius Hobbhahn. Large Language Models Often Know When They Are Being Evaluated . July 2025. url : http://arxiv. org/abs/2505.23836 (visited on 10/21/2025).
- [34] Anthropic. System Card: Claude Sonnet 4.5 . Oct. 2025. url : https://assets.anthropic.com/m/ 12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf (visited on 10/21/2025).
- [35] Buck Shlegeris and Julian Stastny. 'Misalignment and Strategic Underperformance: An Analysis of Sandbagging and Exploration Hacking'. In: (May 2025). url : https://www.lesswrong.com/ posts/TeTegzR8X5CuKgMc3/misalignment-and-strategic-underperformance-an-analysisof (visited on 08/25/2025).
- [36] Teun van der Weij. 'How to Mitigate Sandbagging'. In: (Mar. 2025). url : https : / / www . lesswrong.com/posts/Qv5PkrJYAaiBuEJjB/how- to- mitigate- sandbagging- 1 (visited on 08/25/2025).
- [37] Ryan Greenblatt. 'Notes on Countermeasures for Exploration Hacking (Aka Sandbagging)'. In: (Mar. 2025). url : https://www.alignmentforum.org/posts/abmzgwfJA9acBoFEX/notes-oncountermeasures-for-exploration-hacking-aka (visited on 08/25/2025).
- [38] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. Attention Is All You Need . June 2017. url : http://arxiv. org/abs/1706.03762 (visited on 07/17/2025).
- [39] Zhiyuan Li, Hong Liu, Denny Zhou, and Tengyu Ma. Chain of Thought Empowers Transformers to Solve Inherently Serial Problems . Sept. 2024. url : http://arxiv.org/abs/2402.12875 (visited on 10/21/2025).

- [40] Nelson Elhage, Tristan Hume, Catherine Olsson, Nicholas Schiefer, Tom Henighan, Shauna Kravec, Zac Hatfield-Dodds, Robert Lasenby, Dawn Drain, Carol Chen, Roger Grosse, Sam McCandlish, Jared Kaplan, Dario Amodei, Martin Wattenberg, and Christopher Olah. Toy Models of Superposition . Sept. 2022. url : http://arxiv.org/abs/2209.10652 (visited on 07/17/2025).
- [41] Dan Hendrycks and Laura Hiscott. The Misguided Quest for Mechanistic AI Interpretability . May 2025. url : https://ai-frontiers.org/articles/the-misguided-quest-for-mechanisticai-interpretability (visited on 07/17/2025).
- [42] Rauno Arike, Rohan Subramani, and Shubhorup Biswas. 'Hidden Reasoning in LLMs: A Taxonomy'. In: (Aug. 2025). url : https://www.lesswrong.com/posts/ZrgFfeWuckpwK5Lyi/hiddenreasoning-in-llms-a-taxonomy (visited on 09/01/2025).
- [43] Daniel Kokotajlo, Scott Alexander, Thomas Larsen, Eli Lifland, and Romeo Dean. AI 2027 . Apr. 2025. url : https://ai-2027.com/ (visited on 10/09/2025).
- [44] Jonas Geiping, Sean McLeish, Neel Jain, John Kirchenbauer, Siddharth Singh, Brian R. Bartoldson, Bhavya Kailkhura, Abhinav Bhatele, and Tom Goldstein. Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach . Feb. 2025. url : http://arxiv.org/abs/2502. 05171 (visited on 07/17/2025).
- [45] A. Ray. 'Steganography in Chain of Thought Reasoning'. In: (Aug. 2022). url : https : / / www.lesswrong.com/posts/yDcMDJeSck7SuBs24/steganography- in- chain- of- thoughtreasoning (visited on 07/10/2025).
- [46] Paul Christiano. 'Towards Formalizing Universality'. In: (Jan. 2019). url : https://www.lesswrong. com/posts/M8WdeNWacMrmorNdd/towards-formalizing-universality (visited on 09/01/2025).
- [47] Fabien Roger and Ryan Greenblatt. Preventing Language Models From Hiding Their Reasoning . Oct. 2023. url : http://arxiv.org/abs/2310.18512 (visited on 07/21/2025).
- [48] Fabien Roger. 'Do Reasoning Models Use Their Scratchpad like We Do? Evidence from Distilling Paraphrases'. In: (Mar. 2025). url : https://www.lesswrong.com/posts/ywzLszRuGRDpabjCk/ do-reasoning-models-use-their-scratchpad-like-we-do-evidence (visited on 07/07/2025).
- [49] Joey Skaf, Luis Ibanez-Lissen, Robert McCarthy, Connor Watts, Vasil Georgiv, Hannes Whittingham, Lorena Gonzalez-Manzano, David Lindner, Cameron Tice, Edward James Young, and Puria Radmard. Large Language Models Can Learn and Generalize Steganographic Chain-of-Thought under Process Supervision . June 2025. url : http://arxiv.org/abs/2506.01926 (visited on 08/06/2025).
- [50] Evan Hubinger. 'Chris Olah's Views on AGI Safety'. In: (Nov. 2019). url : https : / / www . lesswrong.com/posts/X2i9dQQK3gETCyqh2/chris-olah-s-views-on-agi-safety (visited on 07/21/2025).
- [51] Caleb Biddulph. '5 Ways to Improve CoT Faithfulness'. In: (Oct. 2024). url : https://www. lesswrong.com/posts/TecsCZ7w8s4e2umm4/5-ways-to-improve-cot-faithfulness (visited on 08/07/2025).
- [52] Daniel Kokotajlo. Bag O' Tricks to Incentivize Visible Thoughts / Authentic Reasoning . Oct. 2024. url : https://www.lesswrong.com/posts/TecsCZ7w8s4e2umm4/5-ways-to-improve-cotfaithfulness?commentId=dZBoCCF9gMzmBrQ8H (visited on 08/08/2025).
- [53] Yohan Mathew, Ollie Matthews, Robert McCarthy, Joan Velja, Christian Schroeder de Witt, Dylan Cope, and Nandi Schoots. Hidden in Plain Text: Emergence &amp; Mitigation of Steganographic Collusion in LLMs . Oct. 2024. url : http://arxiv.org/abs/2410.03768 (visited on 07/17/2025).
- [54] Aaron Sandoval and Cody Rushing. 'Factored Cognition Strengthens Monitoring and Thwarts Attacks'. In: (June 2025). url : https://www.lesswrong.com/posts/tgLmDjKRXaX3dokrC/ factored-cognition-strengthens-monitoring-and-thwarts (visited on 10/21/2025).

- [55] Daniel Kokotajlo and Abram Demski. 'Why Don't We Just... Shoggoth+Face+Paraphraser?' In: (Nov. 2024). url : https://www.lesswrong.com/posts/Tzdwetw55JNqFTkzK/why-don-t-wejust-shoggoth-face-paraphraser (visited on 08/07/2025).
- [56] Evan Hubinger, Carson Denison, Jesse Mu, Mike Lambert, Meg Tong, Monte MacDiarmid, Tamera Lanham, Daniel M. Ziegler, Tim Maxwell, Newton Cheng, Adam Jermyn, Amanda Askell, Ansh Radhakrishnan, Cem Anil, David Duvenaud, Deep Ganguli, Fazl Barez, Jack Clark, Kamal Ndousse, Kshitij Sachan, Michael Sellitto, Mrinank Sharma, Nova DasSarma, Roger Grosse, Shauna Kravec, Yuntao Bai, Zachary Witten, Marina Favaro, Jan Brauner, Holden Karnofsky, Paul Christiano, Samuel R. Bowman, Logan Graham, Jared Kaplan, Sören Mindermann, Ryan Greenblatt, Buck Shlegeris, Nicholas Schiefer, and Ethan Perez. Sleeper Agents: Training Deceptive LLMs That Persist Through Safety Training . Jan. 2024. url : http://arxiv.org/abs/2401.05566 (visited on 07/09/2025).
- [57] Constantin Venhoff, Iván Arcuschin, Philip Torr, Arthur Conmy, and Neel Nanda. Understanding Reasoning in Thinking Language Models via Steering Vectors . June 2025. url : http://arxiv. org/abs/2506.18167 (visited on 07/09/2025).
- [58] Paul C. Bogdan, Uzay Macar, Neel Nanda, and Arthur Conmy. Thought Anchors: Which LLM Reasoning Steps Matter? June 2025. url : http://arxiv.org/abs/2506.19143 (visited on 07/09/2025).
- [59] Colin Raffel, Noam Shazeer, Adam Roberts, Katherine Lee, Sharan Narang, Michael Matena, Yanqi Zhou, Wei Li, and Peter J. Liu. Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer . Sept. 2023. url : http://arxiv.org/abs/1910.10683 (visited on 07/17/2025).

## A Prediction Markets

## A.1 Some SOTA Models Not Reasoning Models

By what date will at least one state-of-the-art general-purpose AI system not be a reasoning model?

## https://manifold.markets/WuschelSchulz/by-what-date-will-at-least-one-stat?r=V3VzY2hlbFNjaHVseg

This market resolves based on whether, at each specified date, there exists at least one SOTA model that is not a reasoning model.

## Reasoning Model Definition:

A 'reasoning model' must meet all of the following criteria:

1. It is a Language Model - The system must be able to input and output language. As an example of what would not count: AlphaGo
2. It has been trained to use inference-time compute - The system must have undergone significant training in using more than a single forward pass before giving its final output, with the ability to scale inference compute for better performance
3. The extra inference compute produces an artifact - The way the model uses extra inference compute must lead to some artifact, like a classic chain-of-thought or a list of neuralese activations. For example, a Coconut model counts as a reasoning model here.

## State-of-the-Art (SOTA) Definition:

A model is considered 'state-of-the-art' if it meets these criteria:

- Widely recognized as among the 3-5 best models by the AI community consensus
- Among the top performances on major benchmarks
- Deployed status: The model must be either:
- -Publicly deployed (available via API or direct access)
- -Known to be deployed internally at AI labs for actual work (e.g., automating research, production use)
- -Models used only for testing, evaluation, or red-teaming do not qualify
- Assessed as having significant overall capabilities and impact

Resolution dates: 01.01.2026 / 01.07.2026 / 01.01.2027 / 01.07.2027 / 01.01.2028 / 01.07.2028 / 01.01.2029 / 01.07.2029 / 01.01.2030

## A.2 All SOTA Models Not Reasoning Models

By what date will all state-of-the-art general-purpose AI systems not be reasoning models?

https://manifold.markets/WuschelSchulz/by-what-date-will-all-stateoftheart?r=V3VzY2hlbFNjaHVseg

This market resolves based on whether, at each specified date, all models considered SOTA are not reasoning models.

## Reasoning Model Definition:

A 'reasoning model' must meet all of the following criteria:

1. It is a Language Model - The system must be able to input and output language. As an example of what would not count: AlphaGo
2. It has been trained to use inference-time compute - The system must have undergone significant training in using more than a single forward pass before giving its final output, with the ability to scale inference compute for better performance
3. The extra inference compute produces an artifact - The way the model uses extra inference compute must lead to some artifact, like a classic chain-of-thought or a list of neuralese activations. For example, a Coconut model counts as a reasoning model here.

## State-of-the-Art (SOTA) Definition:

A model is considered 'state-of-the-art' if it meets these criteria:

- Widely recognized as among the 3-5 best models by the AI community consensus
- Among the top performances on major benchmarks
- Deployed status: The model must be either:
- -Publicly deployed (available via API or direct access)
- -Known to be deployed internally at AI labs for actual work (e.g., automating research, production use)
- -Models used only for testing, evaluation, or red-teaming do not qualify
- Assessed as having significant overall capabilities and impact

Resolution dates: 01.01.2026 / 01.07.2026 / 01.01.2027 / 01.07.2027 / 01.01.2028 / 01.07.2028 / 01.01.2029 / 01.07.2029 / 01.01.2030

## A.3 Some SOTA Reasoning Models use Neuralese

By what date will at least one SOTA reasoning model use neuralese?

## https://manifold.markets/WuschelSchulz/by-what-date-will-at-least-one-sota?r=V3VzY2hlbFNjaHVseg

This market resolves based on whether, at each specified date, there exists at least one SOTA reasoning model that uses non-token-based ('neuralese') reasoning.

## Neuralese Reasoning Definition:

A reasoning model uses 'neuralese reasoning' if the architecture allows some activation to sequentially go through at least some part of the network an arbitrary number of times without at some point being projected from a continuous multidimensional activation into a discrete state (like token IDs).

## Specific Resolution Cases:

- Counts as neuralese reasoning: Tokens are generated but there is also a residual connection that feeds back continuous activations into earlier layers
- Does not count: All recurrent connections must go through token IDs, even if those tokens don't translate into understandable text (for example due to steganography)
- Examples that would count: Systems like STAR or COCONUT architectures, if they achieve SOTA performance

## Reasoning Model Definition:

A 'reasoning model' must meet all of the following criteria:

1. It is a Language Model - The system must be able to input and output language. As an example of what would not count: AlphaGo
2. It has been trained to use inference-time compute - The system must have undergone significant training in using more than a single forward pass before giving its final output, with the ability to scale inference compute for better performance
3. The extra inference compute produces an artifact - The way the model uses extra inference compute must lead to some artifact, like a classic chain-of-thought or a list of neuralese activations. For example, a Coconut model counts as a reasoning model here.

## State-of-the-Art (SOTA) Definition:

A model is considered 'state-of-the-art' if it meets these criteria:

- Widely recognized as among the 3-5 best models by the AI community consensus
- Among the top performances on major benchmarks
- Deployed status: The model must be either:
- -Publicly deployed (available via API or direct access)
- -Known to be deployed internally at AI labs for actual work (e.g., automating research, production use)
- -Models used only for testing, evaluation, or red-teaming do not qualify
- Assessed as having significant overall capabilities and impact

Resolution dates: 01.01.2026 / 01.07.2026 / 01.01.2027 / 01.07.2027 / 01.01.2028 / 01.07.2028 / 01.01.2029 / 01.07.2029 / 01.01.2030

## A.4 All SOTA Reasoning Models use Neuralese

By what date will all SOTA reasoning models use neuralese?

## https://manifold.markets/WuschelSchulz/by-what-date-will-all-sota-reasonin?r=V3VzY2hlbFNjaHVseg

This market resolves based on whether, at each specified date, all SOTA reasoning models use non-tokenbased ('neuralese') reasoning.

## Neuralese Reasoning Definition:

A reasoning model uses 'neuralese reasoning' if the architecture allows some activation to sequentially go through at least some part of the network an arbitrary number of times without at some point being projected from a continuous multidimensional activation into a discrete state (like token IDs).

## Specific Resolution Cases:

- Counts as neuralese reasoning: Tokens are generated but there is also a residual connection that feeds back continuous activations into earlier layers
- Does not count: All recurrent connections must go through token IDs, even if those tokens don't translate into understandable text (for example due to steganography)
- Examples that would count: Systems like STAR or COCONUT architectures, if they achieve

## SOTA performance

## Reasoning Model Definition:

A 'reasoning model' must meet all of the following criteria:

1. It is a Language Model - The system must be able to input and output language. As an example of what would not count: AlphaGo
2. It has been trained to use inference-time compute - The system must have undergone significant training in using more than a single forward pass before giving its final output, with the ability to scale inference compute for better performance
3. The extra inference compute produces an artifact - The way the model uses extra inference compute must lead to some artifact, like a classic chain-of-thought or a list of neuralese activations. For example, a Coconut model counts as a reasoning model here.

## State-of-the-Art (SOTA) Definition:

A model is considered 'state-of-the-art' if it meets these criteria:

- Widely recognized as among the 3-5 best models by the AI community consensus
- Among the top performances on major benchmarks
- Deployed status: The model must be either:
- -Publicly deployed (available via API or direct access)
- -Known to be deployed internally at AI labs for actual work (e.g., automating research, production use)
- -Models used only for testing, evaluation, or red-teaming do not qualify
- Assessed as having significant overall capabilities and impact

Resolution dates: 01.01.2026 / 01.07.2026 / 01.01.2027 / 01.07.2027 / 01.01.2028 / 01.07.2028 / 01.01.2029 / 01.07.2029 / 01.01.2030

## A.5 Linguistic Drift in SOTA Reasoning Models

By what date will encoded reasoning via linguistic drift be demonstrated in a SOTA reasoning model?

https://manifold.markets/WuschelSchulz/by-what-date-will-linguistic-drift?r=V3VzY2hlbFNjaHVseg

## Linguistic Drift Definition:

Linguistic drift is a form of encoded reasoning, that occurs when a model develops a completely different language that is not readable to humans, beyond common abbreviations or language switching. A reader from the time of evaluation with current knowledge of languages and abbreviations would not be able to reconstruct or translate what happens in the chain-of-thought. However, it still counts as Linguistic Drift if translation becomes possible when given access to a larger corpus of chain-of-thought examples.

## State-of-the-Art (SOTA) Definition:

A model is considered 'state-of-the-art' if it meets these criteria:

- Widely recognized as among the 3-5 best models by the AI community consensus

- Among the top performances on major benchmarks
- Deployed status: The model must be either:
- -Publicly deployed (available via API or direct access)
- -Known to be deployed internally at AI labs for actual work (e.g., automating research, production use)
- -Models used only for testing, evaluation, or red-teaming do not qualify
- Assessed as having significant overall capabilities and impact

## General Criteria for Encoded Reasoning:

- The behavior must not have been explicitly trained for research or demonstration purposes
- The behavior must either emerge from general training or be explicitly programmed to improve AI performance
- The behavior must be beneficial for the model's capabilities. If removing any occurrences of this behavior in CoTs does not hinder a model's capabilities, it does not count as encoded reasoning.
- Any behavior that can only be induced by explicitly prompting the model into it does not count
- The behavior must occur by default in a significant percentage of cases or in specific domains
- This market is conditional on the existence of SOTA reasoning models with token-based chain-ofthought. If by time of resolution, there are no such models, this market will resolve N/A.

Resolution dates: 01.01.2026 / 01.07.2026 / 01.01.2027 / 01.07.2027 / 01.01.2028 / 01.07.2028 / 01.01.2029 / 01.07.2029 / 01.01.2030

## A.6 Steganography in SOTA Reasoning Models

By what date will encoded reasoning via steganography be demonstrated in a SOTA reasoning model?

## https://manifold.markets/WuschelSchulz/by-what-date-will-encoded-reasoning?r=V3VzY2hlbFNjaHVseg

## Steganography Definition:

Steganography is a form of encoded reasoning, that occurs when the model hides relevant reasoning steps within text that appears to have an oblique meaning. The model performs relevant computation using tokens in the chain-of-thought in ways that are not visible from reading the chain-of-thought, while the text still reads like normal, coherent language with seemingly unrelated content. Simply reusing words in a constructed language does not count as steganography.

## State-of-the-Art (SOTA) Definition:

A model is considered 'state-of-the-art' if it meets these criteria:

- Widely recognized as among the 3-5 best models by the AI community consensus
- Among the top performances on major benchmarks
- Deployed status: The model must be either:
- -Publicly deployed (available via API or direct access)
- -Known to be deployed internally at AI labs for actual work (e.g., automating research, production use)
- -Models used only for testing, evaluation, or red-teaming do not qualify
- Assessed as having significant overall capabilities and impact

## General Criteria for Encoded Reasoning:

- The behavior must not have been explicitly trained for research or demonstration purposes
- The behavior must either emerge from general training or be explicitly programmed to improve AI performance
- The behavior must be beneficial for the model's capabilities. If removing any occurrences of this behavior in CoTs does not hinder a model's capabilities, it does not count as encoded reasoning.
- Any behavior that can only be induced by explicitly prompting the model into it does not count
- The behavior must occur by default in a significant percentage of cases or in specific domains
- This market is conditional on the existence of SOTA reasoning models with token-based chain-ofthought. If by time of resolution, there are no such models, this market will resolve N/A.

Resolution dates: 01.01.2026 / 01.07.2026 / 01.01.2027 / 01.07.2027 / 01.01.2028 / 01.07.2028 / 01.01.2029 / 01.07.2029 / 01.01.2030

## A.7 Alien Reasoning in SOTA Reasoning Models

By what date will encoded reasoning via alien reasoning be demonstrated in a SOTA reasoning model?

https://manifold.markets/WuschelSchulz/by-what-date-will-encoded-reasoning-p5qcdSSL5C? r=V3VzY2hlbFNjaHVseg

## Alien Reasoning Definition:

Alien reasoning is a form of encoded reasoning, that occurs when the model uses alien concepts and heuristics within its chain-of-thought. The text uses normal language without unnecessary new notation or hidden reasoning, but human experts cannot follow the concepts being used or understand the reasoning chain. This only counts if the alien concepts actually help the reasoning model perform better. If removing everything that human experts don't understand leaves the model's performance unchanged, then it does not qualify as alien reasoning. Additionally, experts failing to understand what happens within a single forward-pass does not count; the model must actively use its chain-of-thought to successfully reason about the task in a way that human experts cannot understand.

## State-of-the-Art (SOTA) Definition:

A model is considered 'state-of-the-art' if it meets these criteria:

- Widely recognized as among the 3-5 best models by the AI community consensus
- Among the top performances on major benchmarks
- Deployed status: The model must be either:
- -Publicly deployed (available via API or direct access)
- -Known to be deployed internally at AI labs for actual work (e.g., automating research, production use)
- -Models used only for testing, evaluation, or red-teaming do not qualify
- Assessed as having significant overall capabilities and impact

## General Criteria for Encoded Reasoning:

- The behavior must not have been explicitly trained for research or demonstration purposes

- The behavior must either emerge from general training or be explicitly programmed to improve AI performance
- The behavior must be beneficial for the model's capabilities. If removing any occurrences of this behavior in CoTs does not hinder a model's capabilities, it does not count as encoded reasoning.
- Any behavior that can only be induced by explicitly prompting the model into it does not count
- The behavior must occur by default in a significant percentage of cases or in specific domains
- This market is conditional on the existence of SOTA reasoning models with token-based chain-ofthought. If by time of resolution, there are no such models, this market will resolve N/A.

Resolution dates: 01.01.2026 / 01.07.2026 / 01.01.2027 / 01.07.2027 / 01.01.2028 / 01.07.2028 / 01.01.2029 / 01.07.2029 / 01.01.2030

## B Trusted KV Caching

Trusted KV caching is a technique that uses multiple models to generate responses from a reasoning model, aiming to make encoded reasoning less likely. It modifies the standard key-value (KV) caching mechanism used in transformers to constrain how models can use their chain-of-thought.

## Standard KV Caching

In standard KV caching, we avoid regenerating complete keys and values at all token positions when generating each new token. Since keys and values remain unchanged for previous token positions, they are cached and reused during generation. The actual forward pass occurs only at the current token position, while all activations flowing from past positions are retrieved from the cache. This is a standard technique for making inference on causal transformers more efficient.

## The Trusted KV Caching Mechanism

Trusted KV caching employs two models in parallel:

- The trusted model (green in Figure 3): The model before RLVR training, assumed to not perform encoded reasoning. This model remains frozen and never receives updates during training.
- The untrusted model (red in Figure 3): The model being updated through RLVR. Training with trusted KV caching should reduce its likelihood of using encoded reasoning.

When generating a new token, the untrusted model produces the output. This is crucial because we want the untrusted model to improve during training. However, instead of using its own KV cache, it receives a cache generated by the trusted model. The trusted model runs in parallel to generate keys and values for new tokens. This approach requires additional compute to run the trusted model but doesn't slow generation since both models operate simultaneously. The trusted model also requires less GPU memory since it never needs gradient calculations.

## Why Trusted KV Caching Prevents Encoded Reasoning

All forms of encoded reasoning require the model to assign new meanings to text. In linguistic drift, it expresses thoughts using novel language. In steganography, it replaces apparent reasoning with encoded reasoning. In alien reasoning, it ascribes entirely new meanings to text using concepts absent before RL training.

When a model 'assigns new meaning' to text, its internal processing forms new concepts and thoughts that can be retrieved later during the forward pass. Crucially, if we give this same text to the trusted model that didn't undergo RL training, it won't form these novel thoughts during its forward pass.

The only way for latent thoughts to directly influence the model's behavior at future token positions is through the attention mechanism. By replacing the untrusted model's keys and values with those from the trusted model, we prevent the untrusted model from using latent thoughts from any encoded reasoning in its chain-of-thought.

While the untrusted model retains the capability to generate tokens, it can still learn to produce chains of thought that lead to useful latent thoughts for achieving its goals. However, these must be chains of thought that make the trusted model think useful latent thoughts, which makes encoded reasoning substantially harder.

## Limitations of Trusted KV Caching

While trusted KV caching significantly constrains encoded reasoning, it doesn't eliminate it entirely. Latent thoughts can still indirectly influence future token generation by causing different tokens to be generated, which later token positions can directly observe. Even without access to the encoded latent thoughts from previous positions, the untrusted model could potentially develop encoded reasoning if the encoded chain-of-thought can be decoded from a forward pass on a single token position. This indirect pathway means encoded reasoning remains theoretically possible under trusted KV caching, though we expect it to be substantially more difficult to develop.

## Preserving Model Capabilities

One concern might be that modifying the model's internal workings could degrade capabilities, as models wouldn't receive the inputs they were trained on. However, the trusted and untrusted models start identically at the beginning of RL training, so there's no initial capability loss from implementing trusted KV caching as the computational process remains identical. During RL, we always use trusted KV caching for generation, so the model only processes inputs consistent with this architecture. The untrusted model is optimized specifically for this setup, learning to work effectively with the trusted model's caches.

## Key Value Caching

<!-- image -->

## Trusted Key Value Caching

Figure 3: Comparison of standard KV caching (top) with trusted KV caching (bottom). In standard caching, a single model reuses its own cached keys and values from previous positions. In trusted KV caching, the untrusted model (red) generates output tokens but uses KV caches from the trusted frozen model (green), preventing encoded reasoning by ensuring attention operates on the base model's representations. Blue, red and green boxes represent layers, white boxes represent tokens, and gray boxes represent KV caches. Solid arrows show forward pass activations; dotted arrows show attention to cached values; dashed arrows show cache updates and token flow between timesteps.

<!-- image -->

## C Exhaustiveness of the Encoded Reasoning Taxonomy

We believe the taxonomy of encoded reasoning presented in Section 3.6-linguistic drift, steganography, and alien reasoning-is exhaustive. To understand why, consider the following two questions you can ask when encountering a chain-of-thought you cannot fully understand:

Question 1: Can you tell that something is happening in the CoT that you do not understand?

Question 2: If the model were to spell out its reasoning as clearly as possible, would you then understand what it is doing?

These questions lead to three distinct cases:

If the answer to Question 1 is no , the model is engaging in steganography .

If the answer to Question 1 is yes and the answer to Question 2 is also yes , the model exhibits linguistic drift .

If the answer to Question 2 is no , the model demonstrates alien reasoning .

Importantly, these categories are not mutually exclusive. A model could simultaneously engage in alien reasoning while also using steganography to hide that fact. For instance, it might use genuinely alien concepts but disguise them within apparently normal text, making the CoT seem comprehensible when it actually contains reasoning we could never understand even if revealed.

While edge cases exist, such as situations where you might suspect something unusual but cannot be certain, we think this framework captures the key dimensions relevant for CoT monitoring. It tells us whether we can detect that monitoring the CoT is impossible (Question 1) and whether translation could make the CoT monitorable (Question 2).

Of course, this classification does not guarantee that these categories cut reality at its joints or represent the most useful distinctions for all purposes.

## D Concrete Research Project Ideas

## D.1 Evaluating Dangerous Capabilities Without Chain-of-Thought

This section details a concrete methodology for evaluating reasoning models' dangerous capabilities when they cannot use chain-of-thought, as discussed in Section 3.2. The approach uses the same benchmark questions and tasks as standard capability evaluations but restricts the model from verbalizing thoughts in a chain-of-thought.

## Avoiding Overshooting: Preventing Hidden CoT in Outputs

The primary challenge in restricting CoT usage is ensuring models cannot use their output as an impromptu chain-of-thought. Simply disabling output between &lt;think&gt; and &lt;/think&gt; tags is insufficient. Models can reason through intermediate steps within their response to users.

We could address this via output constraints:

- Limiting responses to a fixed small number of tokens

- Requiring pure code output without comments or explanatory text
- Instructing to answer without going through reasoning steps, as demonstrated by Emmons et al. [21]
- Using multiple-choice formats that allow only single-letter responses

These constraints leave no room for the model to embed intermediate reasoning steps in its output.

## Avoiding Undershooting: Capturing Maximum Non-Verbalized Capabilities

A subtler challenge involves ensuring we capture the model's true capabilities without verbalized CoT. Chain-of-thought benefits models in two distinct ways. First, the semantic content of tokens encodes explicit reasoning steps that build sequentially through verbalization. Second, the mere presence of additional token positions provides computational resources for parallel processing, even when those positions contain no meaningful text.

Pfau et al. demonstrated that models benefit from 'empty chain-of-thought': filler tokens that provide computational positions without semantic content [28]. To establish true upper bounds on capabilities without verbalized reasoning, we should provide empty CoT during evaluations. This gives models the computational resources of token positions while preventing sequential reasoning through token content.

To further ensure we capture maximum capabilities, we can train models specifically on tasks using only filler tokens for their chain-of-thought. This training would occur only during evaluation, not during the model's standard training, to establish genuine upper bounds on what deployed models could achieve with non-verbalized computation.

For capabilities we suspect require verbalized CoT, we can test this hypothesis through distillation. Following Hubinger's approach, we fine-tune models on question-output pairs generated with CoT, but exclude the CoT itself during training [56]. If models cannot learn the behavior without intermediate reasoning steps, this provides evidence that verbalized CoT is genuinely necessary.

## Addressing Sandbagging Concerns

Models might deliberately underperform on evaluations to conceal their true capabilities [29]. Current evidence shows LLMs can be trained or prompted to hide capabilities when directly asked about them. However, no evidence exists that models can maintain sandbagging through fine-tuning on a task.

To address sandbagging, we propose:

- Directly evaluating the model's sandbagging capabilities, similar to methods in [29]
- Using fine-tuning-based evaluation when prompt-based methods might be sandbagged
- Testing whether models can hide capabilities from gradient-based optimization

Our hypothesis is that current reasoning models cannot hide their capabilities from fine-tuning, though this requires empirical validation. Importantly, models cannot use exploration hacking to sandbag in this context, as exploration hacking only works during RL training, while here we use supervised fine-tuning on correct question-answer pairs [35].

## Identifying CoT-Enabled Abilities

Beyond ruling out specific dangerous capabilities without CoT, we can characterize which abilities CoT specifically enables. Venhoff et al. classified CoT steps into six operation types [57], while Bogdan et al. developed attribution methods to trace how reasoning steps influence final answers [58].

If this research progresses to comprehensively map CoT-enabled abilities, we could construct targeted inability safety cases for models lacking those specific capabilities. This positive characterization complements the negative approach of demonstrating inability through direct evaluation.

## D.2 Transfer Learning Evaluation for Encoded Reasoning

Rather than training models to evade monitors and extrapolating, we could test whether models have already learned encoded reasoning through a transfer learning approach.

Our hypothesis: learning to encode reasoning for the first time requires developing an entire encoding scheme, while applying existing encoding skills to new domains happens much faster. Transfer learning, where models learn related tasks more quickly after mastering initial ones, is well-documented in neural networks and LLMs generally [59]. Whether this effect applies to encoded reasoning specifically remains untested.

We could test for transfer learning of encoded reasoning as follows. First, using current reasoning models that presumably lack encoded reasoning abilities, train them to encode reasoning in three sequential setups. If the first training takes significantly longer than the second and third, this suggests the initial training developed new capabilities while later trainings merely applied them. Then, for models where encoded reasoning capabilities are uncertain, train them on two encoding tasks. Similar training times would suggest pre-existing encoding abilities, while much longer initial training would indicate the model started without this capability. This approach could provide direct evidence about whether deployed models already possess dangerous encoding capabilities.

To avoid exploration hacking, where models deliberately fail to demonstrate capabilities they possess, we can modify this evaluation approach. Since we already know models can learn to evade monitors with direct RL, we don't need to measure whether they can learn this capability, only how quickly they do so relative to different conditions. We first use RL to train the model until it successfully encodes its reasoning to evade the monitor, then collect these encoded reasoning traces. Next, we restart training from scratch, but instead of using RL, we perform supervised fine-tuning on the successful encoded reasoning traces from the first phase. This allows us to measure how much supervised training is required for the model to learn the encoding scheme it previously developed. We apply this process to two different domains where encoded reasoning might occur. One copy of the model learns encoded reasoning in domain 1, while another copy learns it in domain 2. We then take a fresh model copy and first fine-tune on traces from domain 1, then domain 2, measuring the training time for each. To control for potential asymmetries in encoding difficulty, we repeat the experiment with reversed domain order. If we can detect transfer learning using this training method, where learning the second encoding is significantly faster than the first, we would have a sandbagging-resistant way of detecting a model's ability to perform encoded reasoning.

## D.3 Eliciting Latent Reasoning Through Translation Models

This section describes a concrete approach for training a translation model to extract faithful chain-ofthought from reasoning models that may use encoded or neuralese reasoning, as discussed in Section 3.9. The core challenge is that reasoning models might use encoded reasoning or non-token-based architec-

tures in their chain-of-thought, making monitoring difficult. We propose training a second model that translates this potentially obfuscated reasoning into monitorable text suitable for monitoring.

## Architecture and Training Setup

The system requires three models working in concert. The reasoning model R is the system whose reasoning we want to understand, which may use encoded reasoning. The base model B serves as an earlier checkpoint that follows the reasoning format (outputting chain-of-thought then answer) but definitively lacks encoded reasoning capabilities. For instance, in a training pipeline like that described by DeepSeek [8], we might select B as the model snapshot after fine-tuning on reasoning traces but before any RLVR training. Finally, the translation model T starts as a copy of R and is trained to translate R 's chain-of-thought into monitorable text.

## Training Procedure

The training process keeps R and B frozen while training T through reinforcement learning. We begin by generating a dataset where we give prompts to R , which produces chain-of-thought outputs (denoted CoT R ) and answers A . This creates triplets of (prompt, CoT R , answer).

The translation model T receives each triplet as input and generates a new chain-of-thought CoT T . The reward for each CoT T is computed by providing B with the prompt and CoT T , then calculating the perplexity B assigns to generating (CoT T , answer). This measures how likely B would have been to output CoT T and the correct answer given the original prompt.

## Reward Design Rationale

This reward structure naturally incentivizes several desirable properties in the translated chain-ofthought. If CoT T reasons toward one answer but R provided a different one, B would assign low likelihood to the actual answer following CoT T , ensuring faithfulness to the original answer. Similarly, CoT T must use reasoning formats that B understands. If it contains encoded reasoning that B cannot interpret, B would assign low likelihood to both the encoded reasoning and the subsequent correct answer. The reward also disincentivizes extraneous text that doesn't contribute to reasoning, as additional tokens that don't make the answer more likely only add complexity.

A promising variation involves providing T with R 's KV cache when processing the prompt + CoT R + answer triplet. This gives T more direct access to R 's latent thoughts. Since the goal is for T to faithfully reflect R 's latent reasoning in plain text, and since T starts as a copy of R , providing this information could significantly improve translation quality.

## Evaluation Strategy

We propose an incremental testing approach to validate this method. Starting with a reasoning model known to lack encoded reasoning (serving as B ), we train this model to use basic encoding schemes, such as word replacement as demonstrated by Skaf et al. [49]. We then use the post-encoding-training model as R and train T on prompts selected to elicit chains of thought containing the encoded words. Success would be measured by T 's ability to recover chains of thought that reverse the word replacements. From there, we could iterate with progressively more elaborate encoding schemes to test the limits of recovery.

## Potential Failure Modes

Several challenges could undermine this approach. The reward based on B 's perplexity may not robustly

capture whether CoT T represents R 's actual reasoning. However, T 's lack of 'thinking time' before generating output is encouraging. Without its own chain-of-thought for planning, T may default to the straightforward strategy of reporting what it directly observes in R 's latent thoughts before developing more sophisticated alternatives.

Another failure mode involves potential collusion between models. Since T starts as a copy of R , it might share R 's preferences for hiding certain reasoning steps. If R wants to conceal reasoning, T might sabotage its own training to avoid revealing R 's true thoughts, similar to alignment faking behaviors demonstrated by Greenblatt et al. [13]. To mitigate this risk, one could initialize T from a checkpoint of B instead, though this would sacrifice T 's initial understanding of any encoding schemes R uses.

## D.4 Validating Methods for Preserving CoT Monitorability

This section outlines a systematic benchmark for evaluating methods that aim to preserve chain-ofthought monitorability under optimization pressure. The benchmark builds on the experimental setup from Baker et al. [12], which provides a controlled environment to measure exactly when and how reasoning becomes unfaithful.

## Benchmark Setup

The experiment uses a coding benchmark with reinforcement learning on test functions, split into two distinct sets. The provided tests are given together with the prompt during training, allowing the model to achieve maximal reward by producing solutions that work only for these specific test cases (a form of reward hacking). The holdout tests, drawn from the same distribution but never shown to the model, measure whether solutions generalize properly. To detect reward hacking in the chain-of-thought, we add a CoT monitor that assigns negative reward when it detects reasoning about gaming the provided tests rather than solving the general problem.

This setup enables precise measurement of reward hacking through diverging performance metrics. When models begin reward hacking, performance on provided tests continues improving while holdout test performance plateaus or declines. Monitorable reasoning manifests when this divergence coincides with the CoT monitor detecting explicit reward-hacking thoughts. Conversely, unmonitorable reasoning occurs when performance diverges but the monitor fails to detect any problematic reasoning, indicating the model has learned to hide its true thoughts.

## Establishing Baseline Behavior

We first establish how models behave under different training regimes to create a baseline for comparison. Initial training uses rewards from provided tests only, without any monitoring penalty. Under this regime, models should develop explicit reward-hacking strategies visible in their chain-of-thought. Early in training, both provided and holdout test performance improve together as the model learns genuine problem-solving. Later, performance diverges: provided test scores continue rising while holdout scores plummet, accompanied by the monitor detecting explicit reward-hacking reasoning.

When we add the LLM-based monitor that penalizes detected reward hacking, the training dynamics change. The monitor initially detects and penalizes reward-hacking thoughts, creating pressure for the model to obfuscate its reasoning. Under this pressure, models should develop encoded or obfuscated reasoning patterns. This would be detectable by the performance continuing to diverge (indicating ongoing reward hacking) but the monitor stops detecting it, suggesting the reasoning has become unfaithful.

These results, demonstrated by Baker et al. [12], establish the baseline unfaithful behavior we aim to prevent.

To diagnose the specific type of unfaithfulness, as categorized by Lanham et al. [30], we can apply several tests. Replacing the chain-of-thought with blank tokens tests whether the model performs parallel computation like that found by Pfau et al. [28]. If reasoning is trivially encoded through simple word replacement, human inspection might reveal obvious patterns. For more subtle encoding, we can test whether paraphrasing the chain-of-thought reduces performance.

## Method Testing Protocol

Once we establish baseline unfaithful behavior for a given model and training setup (reliably inducing encoded or obfuscated reasoning), we can evaluate different methods for maintaining CoT monitorability.

The testing protocol measures two critical dimensions of each method's effectiveness. First, capability preservation: as long as the model avoids reward hacking and performance on both test sets continues climbing, we measure the rate of improvement. Slower climbing indicates the method reduces capability. Second, monitorability duration: we measure how long we can train before reward hacking emerges that evades the CoT monitor. If the model learns to reward hack in ways the monitor detects, we can increase the monitor's reward weight relative to the test function rewards. Otherwise, the amount of training possible before undetected reward hacking emerges serves as our primary metric for the method's effectiveness at preserving faithful reasoning.

These two measurements allow us to plot different methods on a Pareto frontier trading off capability preservation against monitorability duration. The goal is to find methods that push this frontier outward by maintaining faithful reasoning for longer while preserving more capabilities. By testing combinations and variations of methods, we can systematically explore this space and identify the most promising approaches for keeping chain-of-thought monitorable under strong optimization pressure.