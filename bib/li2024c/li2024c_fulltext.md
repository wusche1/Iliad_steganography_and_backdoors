## Chain of Thought Empowers Transformers to Solve Inherently Serial Problems

Zhiyuan Li 1,2 , Hong Liu 1 , Denny Zhou 3 , and Tengyu Ma 1

1 Stanford University, 2 Toyota Technological Institute at Chicago, 3 Google

## Abstract

Instructing the model to generate a sequence of intermediate steps, a.k.a., a chain of thought (CoT), is a highly effective method to improve the accuracy of large language models (LLMs) on arithmetics and symbolic reasoning tasks. However, the mechanism behind CoT remains unclear. This work provides a theoretical understanding of the power of CoT for decoder-only transformers through the lens of expressiveness. Conceptually, CoT empowers the model with the ability to perform inherently serial computation, which is otherwise lacking in transformers, especially when depth is low. Given input length n, previous works have shown that constantdepth transformers with finite precision poly(n) embedding size can only solve problems in TC 0 without CoT. We first show an even tighter expressiveness upper bound for constant-depth transformers with constant-bit precision, which can only solve problems in AC 0 , a proper subset of TC 0 . However, with T steps of CoT, constant-depth transformers using constant-bit precision and O(log n) embedding size can solve any problem solvable by boolean circuits of size T . Empirically, enabling CoT dramatically improves the accuracy for tasks that are hard for parallel computation, including the composition of permutation groups, iterated squaring, and circuit value problems, especially for low-depth transformers.

## 1 Introduction

Large Language Models (LLMs) exhibit exceptional capabilities in complex reasoning tasks such as mathematical problem-solving and code generation (Chowdhery et al. , 2023; Anil et al. , 2023; Achiam et al. , 2023; Romera-Paredes et al. , 2023; Trinh et al. , 2024), far surpassing standard supervised machine learning techniques. The key to unlocking these advanced reasoning abilities lies in enabling LLMs to generate intermediate steps, or a chain of thought (CoT), before finalizing the final answer. This can be achieved through various methods, including training or instruction tuning a model with examples enriched with intermediate steps (Ling et al. , 2017; Cobbe et al. , 2021; Nye et al. , 2021; Chung et al. , 2022), or through few-shot CoT prompting (Reynolds &amp; McDonell , 2021; Nye et al. , 2021; Wei et al. , 2022).

A natural explanation is that the intermediate steps provide extra information about the tasks and efficient approaches to solving, so that a model can imitate. However, intriguingly, the efficacy of generating thought steps extends to zero-shot CoT prompting (Kojima et al. , 2022), where LLMs are only instructed with the prompt "let's think step by step", and to even using incorrect reasoning steps in the few-shot examples (Wang et al. , 2022a; Madaan &amp; Yazdanbakhsh , 2022). These observations suggest that the form of CoT prompting is as important as (if not more important than) its content, because merely instructing LLMs to generate the intermediate steps helps.

This paper aims to study why the form of CoT improves the reasoning capability of LLMs. Our hypothesis is that CoT allows for performing more serial computations that a vanilla transformer cannot do without CoT. We formulate and analyze this hypothesis through the lens of expressiveness with and without CoT. We adopt the language of circuit complexity to discuss the capability of transformers. Previous works (Liu et al. , 2022b; Merrill &amp; Sabharwal , 2023b) have shown standard decoder-only transformers (that output answers directly) are efficient parallel computers and can only express functions computable in an O(1)-parallel run-time with threshold circuits, TC 0 , a computational model that allows the AND , OR , NOT and MAJORITY function with multiple inputs to be computed efficiently in parallel. We first show a tighter upper bound (Theorem 3.1) for expressiveness of constant-precision transformer – it can only express a proper subset class of TC 0 , AC 0 , where MAJORITY gates are not allowed. Our upper bound is also more realistic because it handles the rounding issue or iterative addition of floating point numbers, while most previous results essentially only work for fixed-point number addition.

We then show that transformers equipped with CoT—allowing the transformer to auto-regressively generate a sequence of intermediate tokens before answering the questions—can solve complex problems that inherently require serial computations (assuming well-known conjectures in complexity theory). Intuitively, without CoT, the number of serial computations conducted by the transformer is bounded by the depth (which is considered as a fixed constant for this work), whereas with T intermediate steps, the number of serial computations possible is boosted to T. Note that T can easily increase as the sequence length increases where the depth is a fixed number that depends on the architecture.

Concretely, we prove that a constant-precision transformer with T intermediate steps and embedding dimension logarithmic in the sequence length can express any functions computable by a circuit of size T in Theorem 3.3. Taking T to be polynomial in the sequence length, the result suggests that transformers with polynomially many intermediate steps are capable of computing all circuits in with polynomial size, P/poly, a superclass of P. Theorem 3.3 also implies that transformers with linearly many intermediate steps can compute all regular languages, including composition of non-solvable groups, like permutation group over five elements, S5, which does not belong to AC 0 and is also widely conjectured to be out of TC 0 . As such, polynomially many CoT steps makes transformers with bounded depth and precision strictly more powerful. We define the problem class that transformers can solve with a certain amount of CoT steps formally in Definition 3.4 and summarize our theoretical results in Figure 1. Interestingly, we also show that logarithmically many CoT steps do not allow the transformer to compute functions beyond AC 0 . (Theorem 3.1)

To corroborate our theoretical analysis, we empirically evaluate the capability of transformers in solving four core problems: modular addition, permutation composition, iterated squaring, and circuit value problem. We learn transformers to solve these tasks with a large amount of synthetic data, with and without CoT, or with additional hint but not CoT. The modular addition belongs to TC 0 , meaning it can be easily solved in parallel. Liu et al. (2022a) shows it is solvable by constantdepth transformers with log-precision and, indeed empirically depth 1 is sufficient for the parity problem (Modulo 2 addition). The other three tasks are all conjectured to require inherently serial computations. As expected, the vanilla transformer either requires a huge depth to solve these tasks (because the depth is the upper bound on the number of serial computation by transformers), or cannot solve the tasks at all. On the other hand, CoT can solve these tasks as long as the depth exceeds a small threshold. These experiments demonstrate CoT can provide more serial computations to solve complex reasoning tasks.

Figure 1: Relationship diagram between cotcomplexity class with different embedding sizes d(n) and CoT lengths T(n). We fix the precision to be constant (the above diagram holds with or without constantly many exponent bits) and omit them in the notation for simplicity. The diagram for log precision is similar (with AC 0 replaced by TC 0 ), and is thus deferred to the appendix, Figure 10 .

<!-- image -->

## 2 Notations and Preliminaries

We use N and R to denote the set of natural numbers and real numbers respectively. For any n ∈ N + , we define [n] ≜ {1 , 2, . . . , n}. We define relu(x) ≜ max(x, 0). For vector x, we use x a: b to denote the vector containing coordinates of x from position a to position b. For matrix M, we define Ma Ma1:b1,a2:b2 to denote the submatrix by selecting rows from a1 to b1, columns from a2 to b2. We also use a 1 : to denote the subset of indices from a1 to the end, : b1 to denote the subset of indices from the beginning (1) to b1 and : to denote all indices. Given two non-negative functions f, g , we say f(n) = O(g(n)) (resp. f(n) = Ω(g(n))) iff there exists C &gt; 0, such that for all n ≥ 0 , f(n) ≤ Cg(n) (resp. f(n) ≥ Cg(n)). We use poly(n) ≜ {T : N → N | ∃k &gt; 0, T(n) = O(n k )} to denote the set of functions with at most polynomial growth rate.

We use ϕ(x) = P |x| i=1 2
|x|−i xito denote the value of binary number represented by binary string x. We use bink(x) to denote the usual binary encoding of natural number x using k binary bits in the sense that ϕ(bink(x)) = x and sbink(x) to denote the signed binary encoding, which is 2bink(x) − (1 , . . . , 1). For any n ∈ N + , we define softmax : R n → R n as (softmax(x))i = exp(xi)/
P n i=1 exp(xi) for any x ∈ R n and i ∈ [n]. We use ⊙ to denote the element-wise product of two vectors. We use a∥b or (a, b) to denote the concatenation of two vectors a and b .

## 2.1 Decoder-only Transformers

Given a vocabulary V , a decoder-only transformer with parameter θ and maximal input length n max maps a sequence of input tokens (x1, . . . , x n ) ∈ V n to a probability distribution over V for all n ≤ n max , denoted by pθ(· | x1, . . . , x n ). We also define function TFθ(x) by the token in V that maximizes pθ(· | x1, . . . , x n ), that is, TFθ(x1, . . . , x n ) ≜ arg max y∈V pθ(y | x1, . . . , x n ) .

Next-token Generator: Given a vocabulary V, a next-token generator with parameter θ and maximal input length n max is a mapping from ∪ n max n=1 V n to V. The main next-token generator we are interested in this work is decoder-only transformers, TFθ(x1, . . . , x n ) where xi ∈ V for all i ∈ [n]. We also recursively define TF i θ (x1, . . . , x n ) ≜ TF i − 1 θ (x1, . . . , x n, TFθ(x1, . . . , x n )), for every

positive integer i and n satisfying that i + n ≤ n max − 1 with the base case that TF 1 θ (x1, . . . , x n ) ≜ TFθ(x1, . . . , x n ). In other words, for all 0 ≤ i ≤ n max − n − 1, the output with i steps of CoT is x n+i+1 = TF i+1 θ (x1, . . . , x n ) = TFθ(x1, . . . , x n , xn+1, . . . , xn+i) .

Transformer Architecture Overview: The decoder-only transformer model we consider in this paper is very similar to GPT style architectures (Radford et al. , 2019) and consists of four parts: a token embedding layer (TE), a position encoding layer (PE), an output linear layer (OUTPUT), and a stack ofLidentical layers serving as the "decoder" whereLis also called the depth of the model. Each decoder layer has two sub-layers: a multi-head self-attention layer (ATTN) and a position-wise fullyconnected feed-forward network (FF). Each layer mentioned above has its own trainable parameters and is indexed by the layer name and the depth for attention and feedforward layers. 1 That is we can split the model parameter θ in the following way: θ = (θPE, θTE, θOUTPUT , {θ (l) ATTN , θ (l) FF } L − 1 l=0 ) , which are all trainable. (See formal definition in Algorithm 2). Throughout this paper, we use d to denote the embedding size of a transformer.

Self-Attention Mechanism: Given attention parameter θATTN = (WQ, WK, WV , WO) ∈ R d×d × R d×d × R d×d × R d×d , we define the Attention layer with mask for decoder-only transformer in Algorithm 3. Note allowing multi-head attention will not change the class of problems solvable by constant layer decoder-only transformers as we can simulate 1 multi-head attention layer with any constantly many heads with multiple single-head attention layers. Thus for simplicity of presentation, we do not include multi-head attention in the definition below.

## Algorithm 1 Causal Self-Attention, ATTN

Input: Parameter θATTN = (WQ, WK, WV , WO), Input embedding h = (h1, . . . , h n ) ∈ R nd . Output: Output embedding h ′ = (h ′ 1 , . . . , h ′ n ) ≜ ATTNθ ATTN (h1, . . . , h n ) .

- 1: qi ≜ WQhi, ki ≜ WKhi, vi ≜ WV hi , ∀i ∈ [n]
- 2: si ≜ softmax(⟨qi, k1⟩ , . . . , ⟨qi, ki⟩)∥(0 , . . . , 0) .
- 3: h ′ i ≜ WO WO P n j=1 (si)jvj .

Feed-Forward Network: Given the parameter of fully-connected feedforward network layer θ FF = (W1, b1, W2, b2) ∈ R d×d ×R d ×R d×d ×R d , we define the fully-connected feedforward layer FFθ FF : R d → R d as FFθ FF (h) ≜ W2relu(W1h + b1) + b2 .

Token Embedding: Given the parameter of token embedding layer θTE ∈ R d×|V|, we define the token embedding layer by viewing θTE as a mapping from V to R d , that is, for all x ∈ V, the token embedding is θTE(x) .

Position Encoding: Given the parameter of position encoding layer θPE ∈ R d×n max , we define the token embedding layer by viewing θPE as a mapping from [n max ] to R d that is, for all n ∈ [n max ] , the position embedding is as θPE(n) .

Output Layer: Given the parameter of output layer θOUTPUT ∈ R
|V|× d , we define the output layer OUTPUTθ OUTPUT : R d → V as OUTPUTθ OUTPUT (h) ≜ softmax(θOUTPUTh) for all h ∈ R d .

## 2.2 Circuit Complexity

Problem. In this paper we consider the following notion of problems: given a sequence of input tokens, output a token as the answer. Mathematically, given a vocabulary V, we call a mapping L : ∪ k∈N+ V k → V a problem. If the correct answer is always 0 or 1, we call L a decision problem. In circuit complexity, such L is also called a language .

1 We ignore the LayerNorm (Ba et al. , 2016) in the usual transformer architecture for simplicity. Our expressiveness analysis can extend to the transformers with LayerNorm with more careful treatment. See Appendix F.1 for discussion.

## Algorithm 2 Decoder-only Transformer, TFθ and pθ

Input: Transformer parameter θ = (θPE, θTE, θOUTPUT , {θ (l) ATTN , θ (l) FF } L − 1 l=0 ) and input tokens x = (x1, . . . , x n ) ∈ V n .

Output: Output distribution pθ(· | x1, . . . , xi) for all i ∈ [n] and output token TFθ(x) .

- 1: h (0) i ← θ TE (xi) + θPE(i) , ∀i ∈ [n]
- 2: for l = 0, . . . , L − 1 do
- 3: (h (l+0 . 5) 1 , . . . , h (l+0 . 5) n ) ← (h (l) 1 , . . . , h (l) n ) + ATTN θ (l) ATTN (h (l) 1 , . . . , h (l) n )
- 4: h (l+1) i ← h (l+0 . 5) i + FF θ (l) FF (h (l+0 . 5) i ) , ∀i ∈ [n]

## 5: end for

- 6: pθ(· | x1, . . . , xi) ← OUTPUTθ OUTPUT (h (L) i ) , ∀i ∈ [n]
- 7: TFθ(x) ← arg max y pθ(y | x1, . . . , x n ) .

Though the standard definition of circuit complexity only deals with binary strings, given any finite vocabulary V, we can always replace each token in V by its binary representation, and the length of the input only blows up by a constant factor. Therefore we can extend existing complexity classes listed to arbitrary finite vocabulary naturally.

P . The class P contains all problems solvable by a deterministic Turing machine in polynomial time.

Boolean Circuit. A Boolean circuit over n variables is a directed acyclic graph where nodes are AND , OR, or NOT gates. The gates with in-degree 0 are the inputs, which are assigned one of the n boolean variables. Given the inputs, the circuit computes the value of each non-input gate based on the value of the incoming gates and outputs a number at the output gate.

SIZE[T(n)] . Given any function T , SIZE[T(n)] denotes the class of problems that can be solved by boolean circuits with O(T(n)) gates when the input length is n. Formally, a problem L is in SIZE[T(n)] if and only if there exists a sequence of circuits {Cn Cn } such that each circuit Cn Cn has n inputs and 1 output, the size of each circuit Cn Cn is at most O(T(n)), and for all strings x , x is in L if and only if C| x | (x) = 1 .

P/poly . We define the class P/poly as the set of problems that can be solved by a family of polynomial-size circuits, that is, P/poly ≜ ∪ k∈N+ SIZE[n k ]. Since any Turing Machine with time bound T(n) can be simulated by a circuit of size T(n) log T(n) (Pippenger &amp; Fischer , 1979), we know that P ⊆ P/poly .

NC , AC, and TC . The class NC contains all problems that can be solved in a small parallel runtime—polylogarithmic in input length—and with a polynomial number of processors. Formally, for a positive integer k, a problem L is in NC k if and only if there exists a polynomial p(n) and a family of circuits {Cn Cn } such that each circuit Cn Cn has n inputs and 1 output, the fan-in of the gates is at most 2, the size of each circuit Cn Cn is at most p(n), the depth of each circuit Cn Cn is O((log n) k ), and for all strings x , x is in if and only if C| x | (x) = 1. Finally we define NC = ∪k ∈N NC k . The class AC k is defined almost the same as NC k for each k ∈ N
+, except the AND and OR gates in AC k allow unbounded fan-in. The class TC k allows a more powerful type of gate, MAJORITY, compared to AC k . MAJORITY gate can have unbounded fan-in and is defined as MAJORITY (x1, . . . , x n ) = ⌊ 1 2 + (
P n i=1 xi )−1/2 n
1 ⌋ .

It holds that NC i ⊆ AC i ⊆ TC i ⊆ NC n
i+1 for all natural number i. Therefore NC = AC = TC , which all stands for the problem class that can be solved in polylogarithmic time with polynomial parallel processors.

## 3 Expressiveness Theory for Transformers with Chain of Thought(CoT)

In this section, we study the expressiveness of transformers with CoT from a theoretical perspective.

## 3.1 Finite Precision Modeling

In practice, training and inference of transformers are typically done with 16- or 32-bit floating point numbers. Thus in this paper, we mainly focus on the computation model of constant-precision transformers, where the output of each arithmetic operation is rounded to the closest floating point number representable by a fixed number of digits following IEEE 754 standard (Definition 3.2), thus avoiding the unrealistic infinite precision assumption made by prior works (Pérez et al. , 2019; Dehghani et al. , 2018).

Below we give a formal definition of the floating-point number and rounding operation. Recall ϕ(a) = P k i=1 2 k − i ai denote the value of binary number represented by a ∈ {0 , 1} k for any k ∈ N + .

Definition 3.1 (Floating-point Representation) . Let e be the number of bits for exponents and s be the number of bits for significand. A (e + 2s + 1)-bit binary string a = (a1, a2, . . . a e+2s+1 ) ∈ {0 , 1} e+2s+1 is a floating-point binary representation of number ϕ e,s (a) ≜ sign(a) · 2
exponent(a) · significand(a) with e-bit exponent and 2s-precision, where the sign issign(a) ≜ 2a1 − 1, the significand is significand(a) ≜ 2 − s ϕ(a2:2 s+1 ), and the exponent is exponent(a) ≜ ϕ(a2 s+2:2s+e+1 ) − 2
max(0,e − 1). We further use F e,s to denote all the floating numbers representable using e-bit exponent and 2s-bit precision (significand), that is, F e,s ≜ {S · 2 − s+E | −2 2s + 1 ≤ S ≤ 2 2s − 1 , − 2
max(0,e − 1) ≤ E ≤ 2e − 1 − 2
max(0,e − 1) , E, S ∈ N}. We define B e,s ≜ max F e,s .

We also use ψ e,s : F e,s → {0 , 1} e+2s+1 to denote the inverse of ϕ e,s . We note that when the number of exponent bits is larger than 0, there are multiple ways to represent a number in F e,s by a binary string and we assign ψ e,s (x) as the string a ∈ {0 , 1} e+2s+1 with the smallest |exponent(a)| , which is unique for all non-zero numbers. For 0 we additionally set sign(ψ e,s (0)) = 1 .

Definition 3.2 (Correct Rounding) . For any x ∈ R and any closed subset of R containing 0 , F, we define correct rounding round(x, F) as the closest number to x in F. We break the tie by picking the one with a smaller absolute value.

In particular, we denote the rounding operation with e-bit exponent, 2s-bit precision by round e,s (·) ≜ round(· , F e,s ), which is also denoted by [·] e,s for convenience. We extend the definition of round and round e,s to vector inputs by rounding coordinate-wisely.

Our notion of floating-point number simplifies the IEEE 754 Standard for Floating-point Arithmetic (IEEE , 2008) by removing ∞ and −∞. When overflow happens, we always round the output to the (negative) largest representable number in F e,s . For unary functions like exp(·) and binary functions including addition, subtraction, multiplication, and division, we simply define their rounded version by rounding their outputs. Whenever division by 0 happens, we treat it as the model outputs the wrong result.

Next, we define finite-precision summation over more two numbers by decomposing it as a chain of rounded binary addition in a fixed order. 2

Definition 3.3 (Summation with Iterative Rounding) . For any s, n ∈ N + and vector x ∈ R n , we define summation with iterative rounding to e bit exponent and 2s-bit precision as sum e,s :

2 Technically speaking, instead of a chain, the summation could also proceed like a tree. This is a more complicated case and we leave it for future work.

∪ n∈N+ (F e,s ) n → F e,s , where for any n ∈ N + and x ∈ R n ,

<!-- formula-not-decoded -->

We further define the following operations:

- Finite-precision inner product: ⟨x, y⟩ e,s ≜ sum e,s (x ⊙ y);
- Finite-precision matrix product: (A × e,s B)i,j ≜
- Finite-precision softmax: softmax e,s (x) ≜

Finally, a finite-precision transformer can be defined by replacing all the infinite-precision operations by their finite-precision counterparts listed above. (See details in Algorithm 4). We postpone the details of the finite-precision version of individual transformer layers into Appendix B .

## 3.2 CoT: Complexity Class for Constant-depth Transformers with CoT

In this subsection, we define the complexity class consisting of all the problems that can be solved by some decoder-only transformers with CoT with finite precision.

Definition 3.4 (CoT) . Given a finite vocabulary V and four functions T(n), d(n), s(n), e(n), informally, CoT[T(n), d(n), s(n), e(n)] is the family of problems solvable by a transformer with a constant depth, s(n) bits of precision, e(n) bits of exponent, embedding size d(n) and T(n) steps of CoT. Formally, we say a problem L : ∪ n∈N+ V n → {0 , 1} is in CoT[T(n), d(n), s(n), e(n)] iff there is an integer L and three functions T ′ (n) = O(T(n)), d ′ (n) = O(d(n)), s ′ (n) = O(s(n)) , e ′ (n) = O(e(n)), such that for every positive integer n, there is a L-layer decoder-only transformer, denoted by TFθ n with embedding size d ′ (n) , 2s ′ (n) bits of precision, and e ′ (n) bits of exponent, that can output L(x) given any input x in V n , using T ′ (n) steps of chain of thought. Mathematically, it means

<!-- formula-not-decoded -->

We also extend the definition of CoT to a class of function instead of a single function. For example, CoT[T(n) , poly(n), s(n), e(n)] ≜ ∪ k∈N+ CoT[T(n), n k , s(n), e(n)] .

Definition 3.5 (T) . We define T[d(n), s(n), e(n)] ≜ CoT[0, d(n), s(n), e(n)] as the problems that a constant-depth, constant-precision decoder-only transformer can solve with O(s(n)) bits of precision, O(e(n)) bits of exponent, O(d(n)) embedding size and without CoT (or with only 0 step of CoT).

By definition, CoT[T(n), d(n), s(n), e(n)] is monotone in all T(n), d(n), s(n), e(n) , e.g. , CoT[T ′ (n), d(n), s(n), e(n)] ⊆ CoT[T(n), d(n), s(n), e(n)] if T ′ (n) ≤ T(n) for all n ∈ N. In particular, we have T[d(n), s(n), e(n)] ≜ CoT[0, d(n), s(n), e(n)] ⊆ CoT[T(n), d(n), s(n), e(n)] .

Note the above-defined complexity class CoTis non-uniform, that is, it allows a different program for every input size. This is in contrast to previous works (Pérez et al. , 2019 , 2021; Yao et al. , 2021; Weiss et al. , 2021; Chiang et al. , 2023; Hao et al. , 2022; Merrill &amp; Sabharwal , 2023a; Merrill et al. , 2022) which focus on the uniform transformer classes. Please refer to Appendix G for a discussion.

## 3.3 Tighter Upper Bounds on Transformer Expressiveness

Existing works (Merrill &amp; Sabharwal , 2023b; Liu et al. , 2022a) have shown that constant depth, polynomial width, and log precision transformers can be simulated in a small parallel time, i.e. , using TC 0 circuits. These results are built on the fact that multiplication and division of n-bits binary numbers (Hesse , 2001), as well as the iterated addition over n different n-bit binary integers are in TC 0 .

However, such TC 0 expressiveness upper bounds may be unrealistic for transformers operating with floating point numbers. (Merrill &amp; Sabharwal , 2023b; Liu et al. , 2022a) implicitly assumes when adding more than one floating-point number, the algorithm first computes the exact answer without rounding using arbitrarily more precision and only performs rounding in the end. However, in practice rounding happens after each addition between two numbers and it is open if such TC 0 upper bounds still holds. Immediate rounding makes iterated addition over floating point numbers no longer associative (Goldberg , 1991), for example, round(a + round(b + c)) ̸= round(round(a + b) + c)) . The associativity of integer addition plays a crucial role in the fact that the iterated addition over n different n-bit binary integers is in TC 0 .

In this section, we present two novel expressiveness upper bounds for transformers which round the immediate result after each step of the arithmetic operation. First, we show a strictly tighter upper bound than TC 0 , which is AC 0 , for constant-depth transformers with both constant bits of precision and exponents. (Theorem 3.1) This suggests when input length is sufficiently long, constant-precision transformers cannot count eventually, even in the sense of modular. For example, it is well known that no AC 0 circuits can decide the parity of a binary string.

<!-- formula-not-decoded -->

Our second result, Theorem 3.2, shows that when the number of bits for the exponent is 0 (i.e. fixed-point numbers), TC 0 upper bounds for the expressiveness of constant-depth, log-precision transformers still holds, even with the correct rounding defined in Definition 3.2 .

<!-- formula-not-decoded -->

We note that the fact that a single forward pass of the transformer can be simulated by an AC 0 circuit immediately implies that transformer output with O(log n)steps of CoT can also be simulated by AC 0 . This is because in general one can the transformer output with T steps of CoT as an OR of 2 T disjoint subcircuits, where each of them enumerates all possible values of T CoT tokens and output the value of the token in the branch where all the intermediate token values are consistent. This enumeration can be done in parallel and thus only takes constant depth. When T = O(log n) , this only leads poly(n) factor of explosion in circuit size and thus still in AC 0 . The same argument holds for TC 0 as well.

The main technical difficulties in above two results are showing sum e,s : (F e,s ) n → F e,s has AC 0 (resp. TC 0 ) circuits when e, s are both constants (resp. e = 0 , s = O(log(n))). We view iterated addition with rounding over F e,s as an automaton with both state space and vocabulary being F e,s . The first result are due to a novel application of classical Krhon-Rhodes decomposition theorem for automata (Theorem C.2), where we use the property of rounded addition that for all x, x ′ ∈ F e,s , y ∈ F e,s, x ≥ x ′ =⇒ =⇒ [x + y] e,s ≥ [x ′ + y] e,s . We formalize this property in Definition D.2 as ordered automata and show all ordered automata are counter-free Theorem D.3 and thus can be simulated by AC 0 circuits (McNaughton &amp; Papert , 1971).

The proof technique for Theorem 3.1 does not generalize to Theorem 3.2 because the depth of AC 0 circuits constructed before depends on the number of the states of the automaton and thus is

(a) Original Circuit

<!-- image -->

(b) Forward pass of the transformer with CoT at position 3, computing x4 in Figure 2a. The position embedding comes from the third row of the right serialization in Figure 2c .

Serialized Circuits

Serialized Circuits for CoT simulation

|   Gate Id | Gate Type   | First Input   | Second Input   |
|-----------|-------------|---------------|----------------|
|         1 | INPUT       | N.A.          | N.A.           |
|         2 | INPUT       | N.A.          | N.A.           |
|         3 | NOT         | 1             | N.A.           |
|         4 | AND         | 2             | 3              |

|   Gate  Id | Next Gate  Type   | Next First  Input   | Next Second  Input   |
|------------|-------------------|---------------------|----------------------|
|          1 | INPUT             | N.A.                | N.A.                 |
|          2 | NOT               | 1                   | N.A.                 |
|          3 | AND               | 2                   | 3                    |

(c) Two ways to serialize circuits. The left (blue) one is the most natural one and the right (green) one is used to construct the position embedding so the transformer with CoT simulates the original circuit in Figure 2a .

Figure 2: Illustration of Theorem 3.3 on a 2-gate and 2-input circuit.

not constant. Our proof for Theorem 3.2 is motivated by Algorithm 1 in Liu et al. (2022a) for the automaton named 'GridWorld'.

However, it remains open whether constant-depth, log-precision transformers with log bits for exponents T[poly(n) , log(n) , log(n)] or even constant bits for exponents T[poly(n) , log(n) , 1] have TC 0 circuits.

## 3.4 CoT Makes Transformers More Expressive

Now we are ready to present our main theoretical results (Theorem 3.3) which characterize the expressiveness of constant-depth, constant-precision transformers with CoT and O(log(n)) embedding size. log(n) embedding sizes are necessary to ensure that the position embeddings for n inputs are different. All the lower bounds for transformer expressiveness (with or without CoT) are proved for fixed-point numbers, i.e., without using any exponent bits. Allowing exponent bits will only make transformers more expressive. For convenience, we define CoT[T(n), d(n), s(n)] ≜ CoT[T(n), d(n), s(n) , 0]. The omitted proofs in this section can be found in Appendix E .

Theorem 3.3. For any polynomial function T : N + → N
+ , SIZE[T(n)] ⊆ CoT[T(n) , log n, 1]. In particular, P/poly = CoT[poly(n) , log n, 1] .

Compared to Theorems 3.1 and 3.2, Theorem 3.3 shows that allowing polynomial steps of CoT

strictly makes constant-depth, constant-precision, decoder-only transformer more expressive and logprecision transformers more expressive under a standard hardness assumption that TC 0 ⊊ P/poly . 3

Proof sketch of Theorem 3.3 . The high-level proof idea is that we use each step in CoT to simulate one gate operation in the target circuit and write the gate output as next input. To do that, we use one position encoding to store the information for each gate, which contains four parts: the current gate id, the next gate type {AND , OR , NOT , TRUE , FALSE}, and the two input gates id of the next gate. Since there are total poly(n) gates, d(n) = Θ(log n) embedding size suffices to store the above information. The CoT here is constructed to be the values of each gate in the increasing order of id. Therefore, in each step, we can use attention to pull the value (either computed already or it is input) of the two input gates and use a feedforward network to compute the value of the current gate. The proof idea is illustrated in Figure 2 .

As we can see from the proof sketch, a crucial step for CoT to simulate any depth circuit is to write the output token back to the next input position. This action resets the "depth" of the intermediate output in the circuit to 0. Our theory explains the ablation experiment in Wei et al. (2022) that when the model is prompted to output a only sequence of dots (. . .) equal to the number of tokens needed to solve the problem, the performance is no better than directly outputting the answer.

Because every regular language can be recognized by a finite state automaton (Definition C.1) and finite state automata can clearly be simulated by linear size circuits. The following holds as a direct corollary of Theorem 3.3

## Corollary 3.4. Every regular language belongs to CoT[n, log n, 1] .

Below we give a concrete regular language that constant-depth, poly-embedding-size transformers can solve only with CoT, the wording problem of permutation group over 5 elements, S5 in Theorem 3.5, under a standard hardness assumption that TC 0 ⊊ NC 1 (Yao , 1989).

Definition 3.6 (Wording problem of group G) . Given n elements from G , (g1, . . . , g n ), we use LG to denote the decision problem of whether g1 ◦ g2 ◦ · · · ◦ g n is equal to the identity of G .

For convenience, in this paper, we extend the domain of LG to the sequence of groups encoded by binary strings. The proof of Theorem 3.5 is a direct consequence of Theorems 3.2 , 3.3 and 3.6 .

Theorem 3.5. Assuming TC 0 ⊊ NC 1 , the wording problem of S5 , LS 5 is in CoT[n, log n, 1] but not T[poly(n) , log n] .

Theorem 3.6 (Barrington (1986)) . The wording problem of S5 is NC 1 -complete under AC 0 reductions. That is, for any decision problem L in NC 1 , there is a family of AC 0 circuits {Cn Cn } ∞ n=1 (constant depth, poly(n) fan-outs), such that for any n ∈ N + and x ∈ {0 , 1} n , L(x) = LS 5 (Cn Cn (x)) .

Proof of Theorem 3.5 . First LS 5 is a regular language, thus belonging to CoT[n, log n, 1] by Corollary 3.4. Since LS 5 is NC 1 -complete by Theorem 3.6, assuming TC 0 ⊊ NC 1 , LS 5 does not belong to TC 0 . This proof is completed by applying Theorem 3.2, which says T[poly(n) , log(n)] ⊆ TC 0 .

Results for poly(n) embedding size: So far we have been focusing on the expressiveness of transformer with O(log n) embedding size, so it is natural to ask whether transformers can also benefit from having a larger embedding size, say poly(n)? Our Theorem 3.7 answers this question positively by showing that log-precision (resp. constant-precision) constant-depth poly-embeddingsize decoder-only transformers with T(n) steps of CoT can simulate any T(n)-size circuit with some TC 0 (resp. AC 0 ) oracle gates with poly(n) input.

3 Indeed such separation can be shown for any polynomial steps of CoT by padding polynomially many tokens to input.

Figure 3: Permutation Composition (S5). The label is the composition of all the permutations, where given two permutation σ = (σ1, . . . , σ5) , π = (π1, . . . , π5), we define σ ◦ π ≜ (σ π1 , . . . , σπ 5 ). The chain of thoughts and hints are the partial compositions (string A). Only CoT can solve this task well, as predicted by our Theorem 3.5. Note for the most time the accuracy without CoT is ∼ 20%, which is no better than randomly guessing a number between 1 and 5 .

<!-- image -->

Formally, given a decision problem L : ∪ ∞ n=1 {0 , 1} n → {0 , 1}, we use L n to denote the restriction of L on {0 , 1} n , which can also be viewed as an single gate with n fan-ins. We define problems that can be solved by circuits with certain sizes of gates (including oracle gates) by Definition 3.7 . 4

Definition 3.7 (SIZE L ) . For any decision problemLand T(n) ⊆ O(poly(n)), we define SIZE L (T(n)) as the set of decision problems L ′ such that there exists p(n) ∈ poly(n) and circuits {Cn Cn } ∞ n=1 where Cn Cn contains at most O(T(n)) AND , OR , NOT, and L p(n) gates. For a complexity class C, we define SIZE C (T(n)) ≜ ∪L∈CSIZE L (T(n)) .

Theorem 3.7. For any T(n) ∈ poly(n), it holds that SIZE TC 0 [1+T(n)] = CoT[T(n) , poly(n) , log n] . Specifically, for T(n) = 0, we haveTC 0 = SIZE TC 0 [1] = CoT[0 , poly(n) , log n] = T[poly(n) , log n] .

Theorem 3.8. For any T(n) ∈ poly(n), it holds that SIZE AC 0 [1 + T(n)] = CoT[T(n) , poly(n) , 1] . Specifically, for T(n) = 0, we have AC 0 = SIZE AC 0 [1] = CoT[0 , poly(n) , 1] = T[poly(n) , 1] .

Theorem 3.8 shows that for T(n) = poly(n)steps of CoT, using poly(n) embedding size does not improve expressiveness over using log(n) embedding size (Theorem3.3), because SIZE TC 0 [poly(n)] = SIZE AC 0 [poly(n)] = SIZE[poly(n)]. However, Theorem 3.9 shows that for any specific polynomial T(n) = n k steps of CoT, increasing embedding width from O(log(n)) to poly(n) make transformers strictly more powerful.

Theorem 3.9. For any s(n) = O(log n) , T[log n, s(n)] ⊊ T[poly(n), s(n)] and for all k ∈ N , CoT[n k , log n, s(n)] ⊊ CoT[n k , poly(n), s(n)] .

4 Our definition of complexity class solvable by circuits with oracle is slightly different from that in literature (Wilson , 1985), where the size of the oracle circuits refers to the number of wires, whereas ours refers to the number of gates.

Figure 4: Modular Addition(C7). The label is the sum of the inputs modulo a positive integer, which is 7 in this case. The chain of thoughts and hints are the partial modular sum. Low-depth transformers with hint can solve this task well for a reasonable input sequence length, but with cot the performance is much better, especially with a long input sequence, as predicted by our Theorem 3.3. See experiments for C2 in Figure 7 .

<!-- image -->

## 4 CoT Empirically Improves Expressiveness of Low-Depth Transformers on Inherently Serial Problems

This section is an empirical study of the expressiveness of decoder-only transformers with CoT on four different arithmetic problems: modular addition, permutation composition (S5), iterated squaring, and circuit value problem. The first problem is parallelizable and can be solved by constant-depth transformers with log-precision while the latter three are inherently serial under some standard hardness assumptions in computational complexity or cryptography. As a prediction of our theory, we expect to see a huge improvement in accuracy when CoT is turned on.

General Setup. To examine the expressiveness of decode-only transformers with and without CoT on these four types of problems, we train the transformer using Adam (Kingma &amp; Ba , 2014) from random initialization in the online supervised setting for each problem and each different sequence length n. At each step, we sample a batch of training data from a distribution p n (x) where x = (x1, . . . , x n ) is training data and y = f ∗ (x1, . . . , x n ) is the label. We always set x n to be '='. We consider three different settings, base , cot, and hint:

- base: The optimization objective is simply ℓbase(θ) ≜ E x∼p − log pθ(f ∗ (x) | x) .
- cot: We manually design a chain of thought for each instance x, which is a string in V and we denote by c(x). We ensure the last token of c(x) is always equal to the answer, f ∗ (x). With x ˜ ≜ (x, c(x)), the concatenation of x and c(x), and m be the length of c(x), the optimization objective is ℓcot(θ) ≜ 1 m E x∼p P n+m−1 i=n − ln pθ(˜xi+1 | x˜ ˜ 1, . . . , x ˜ i )) .
- hint: Even if the transformer has better performance in cot setting than base setting, one may argue that besides the difference expressiveness, cot setting also has a statistical advantage over base, as cot provides more labels and thus more information about the groundtruth f ∗ to the model. This motivates us to design the following loss which provides the chain of thought c (x) as the labels. Here for simplicity, we assume the length of c(x) is equal to n . 5 Formally we define ℓ hint (θ) ≜ 1 n E x∼p P n i=1 − ln pθ(ci(x) | x1, . . . , xi)) .

5 Note such alignment is in general impossible because the CoT c(x) can be even longer than x itself. However, in our four settings, there exist meaningful ways to set CoT c(x) as hints for earlier tokens in x .

Figure 5: Iterated Squaring(IS). The vocabulary V ≜ {0 , 1, . . . , T −1 , = , ˆ 2} with T = 1000. We randomly generate input of format (p, r, ˆ 2 , . . . , ˆ 2 , =) with 1 ≤ r, p ≤ T − 1 , p being a prime and random number of ˆ2 tokens (at most m). The label is fr fr,p (n) ≡ (r 2 n ) mod p. CoT and hints are (fr fr,p (i)) n i=1 . Though our construction does not exactly satisfy the technical conditions of the hardness assumption, this problem is difficult for transformers without CoT to learn, but can be perfectly expressed with CoT even with depth 1.

<!-- image -->

Performance Evaluation. Since we train transformers using fresh sampled synthetic data each step, the training accuracy/loss is just the same as validation accuracy/loss. For base and hintsetting, we evaluate the accuracy of the final answer directly. For cot setting, directly evaluating the final answer is too easy because it only measures the ability of the transformer to correctly compute the last step since CoT is given as inputs. Ideally, we should measure the answer output by transformers after auto-regressively generating |c(x)| tokens. But for computational efficiency, we measure the probability that transformers can predict all tokens in the given CoT correctly. Note this probability is a lower bound of the ideal metric because there is a small possibility that transformers can answer correctly with a wrong CoT. Nevertheless, even with this slightly more difficult evaluation metric, transformers in cot setting still optimize much faster than without CoT.

Due to space limit, we defer the details of the training and each setting to Appendix A. Our experimental results are presented in Figures 3 to 6 .

Our Findings: Unsurprisingly, the accuracy in hint setting is always higher than base setting. Due to the space limit, we postpone all results for base settings into Appendix A. For the problems hard for parallel computation, i.e., permutation composition, iterated squaring, and circuit value problem, we find that cot is always better than hint and base, and the improvement is huge especially when depth is small. Our experiments suggest that turning on CoT drastically improves the expressiveness of low-depth transformers on problems that are hard to parallel compute, i.e., those inherently serial problems.

## 5 Related Works

Despite the numerous empirical achievements, unanswered questions concerning the inner workings of neural networks capable of algorithmic reasoning. The ability of self-attention to create lowcomplexity circuits has been recognized (Edelman et al. , 2022; Hahn , 2020; Merrill et al. , 2021), as

Figure 6: Circuit Value Problem(CVP). Given a randomly generated circuit with m gates (sorted by topological order), the vocabulary V = [m] ∪ {TRUE , FALSE , AND , OR , NOT , NA , = }. Each gate is represented by four consecutive tokens, which are gate type, two input gate ids, and the current gate id. The output is the value of the last gate m. CoT and hints also contain 4 tokens for each gate, which are gate type, two input gate values, and the current gate value.

<!-- image -->

well as its capacity to form declarative programs (Weiss et al. , 2021), and Turing machines (Dehghani et al. , 2018; Giannou et al. , 2023; Pérez et al. , 2021). Moreover, it has been demonstrated that interpretable symbolic computations can be drawn from trained models (Clark et al. , 2019; Tenney et al. , 2019; Vig , 2019; Wang et al. , 2022b).

Liu et al. (2022a) is a closely related work to ours, which studies the expressiveness of low-depth transformers for semi-automata. Their setting corresponds to using only 1 step of CoT and our contribution is to show that allowing more steps of CoT enables the transformers to solve more difficult problems than semi-automata, especially those inherently serial problems, like the circuit value problem, which is P-complete.

Constant precision versus logarithmic precision: We note that most previous literature on the expressiveness of transformers focuses on the setting of logarithmic precision, including (Merrill &amp; Sabharwal , 2023b; Merrill et al. , 2022 , 2021; Liu et al. , 2022a), etc. One main reason as argued by Merrill &amp; Sabharwal (2023a) is that log precision allows the transformer to use uniform attention over the rest tokens. However, recent advancements in LLMs showed that uniform attention might not be necessary towards good performance, at least for natural language tasks. For example, one of the most successful open-sourced LLM, LLAMA2 (Touvron et al. , 2023) takes the input of a sequence of 4096 tokens and uses BF16 precision, which has 1 sign bit, 8 exponent bits and 7 mantissa bits (plus one extra leading bit). As a consequence, for example, BF16 cannot express any floating-point number between 2 8 = 256 and 2 8 + 2 = 258, which makes LLAMA2 impossible to compute uniform attention over 257 elements.

A concurrent work Feng et al. (2023) also studies the benefit of CoT via the perspective of

expressiveness, where they show with CoT, transformers can solve some specific P-complete problem. Our result is stronger in the sense that we give a simple and clean construction for each problem in P/poly. We also note the slight difference in the settings, while we mainly focus on constant-precision transformers with O(log n) embedding size, they focus on O(log(n)) precision transformers with bounded embedding size.

## 6 Conclusion

We study the capability of CoT for decoder-only transformers through the lens of expressiveness. We adopt the language of circuit complexity and define a new complexity classCoT[T(n), d(n), s(n), e(n)] which corresponds to a problem class solvable by constant-depth, constant-precision decoder-only transformers with O(T(n)) steps of CoT, O(d(n)) embedding size and floating-point numbers with O(e(n)) bits of exponents and O(s(n)) bits of significand. Our theory suggests that increasing the length of CoT can drastically make transformers more expressive. We also empirically verify our theory in four arithmetic problems. We find that for those three inherently serial problems, transformers can only express the groundtruth function by using CoT.

## Acknowledgement

The authors would like to thank the support from NSF IIS 2045685. The authors also thank Wei Zhan and Lĳie Chen for providing references on circuit complexity and various inspiring discussions, Cyril Zhang and Bingbin Liu for helpful discussions on Khron-Rhodes decomposition theorem, and Kaifeng Lyu for his helpful feedback.

## References

Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.

Rohan Anil, Andrew M Dai, Orhan Firat, Melvin Johnson, Dmitry Lepikhin, Alexandre Passos, Siamak Shakeri, Emanuel Taropa, Paige Bailey, Zhifeng Chen, et al. Palm 2 technical report. arXiv preprint arXiv:2305.10403, 2023.

Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. arXiv preprint arXiv:1607.06450, 2016.

David A. Barrington. Bounded-width polynomial-size branching programs recognize exactly those languages in nc. pp. 1–5, 1986.

Ashok K Chandra, Steven Fortune, and Richard Lipton. Unbounded fan-in circuits and associative functions. In Proceedings of the fifteenth annual ACM symposium on Theory of computing, pp. 52–60, 1983.

David Chiang, Peter Cholak, and Anand Pillay. Tighter bounds on the expressivity of transformer encoders. arXiv preprint arXiv:2301.10743, 2023.

| Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Gaurav Mishra, Adam Roberts, Paul Barham, Hyung Won Chung, Charles Sutton, Sebastian Gehrmann, Parker Schuh, Kensen Shi, Sasha Tsvyashchenko, Joshua Maynez, Abhishek Rao, Parker Barnes, Yi Tay, Noam Shazeer, Vinodkumar Prabhakaran, Emily Reif, Nan Du, Ben Hutchinson, Reiner Pope, James Bradbury, Jacob Austin, Michael Isard, Guy Gur-Ari, Pengcheng Yin, Toju Duke, Anselm Lev skaya, Sanjay Ghemawat, Sunipa Dev, Henryk Michalewski, Xavier Garcia, Vedant Misra, Kevin Robinson, Liam Fedus, Denny Zhou, Daphne Ippolito, David Luan, Hyeontaek Lim, Barret Zoph, Alexander Spiridonov, Ryan Sepassi, David Dohan, Shivani Agrawal, Mark Omernick, Andrew M. Dai, Thanumalayan Sankaranarayana Pillai, Marie Pellat, Aitor Lewkowycz, Erica Moreira, Rewon Child, Oleksandr Polozov, Katherine Lee, Zongwei Zhou, Xuezhi Wang, Bren nan Saeta, Mark Diaz, Orhan Firat, Michele Catasta, Jason Wei, Kathy Meier-Hellstern, Douglas Eck, Jeff Dean, Slav Petrov, and Noah Fiedel. Palm: Scaling language modeling with pathways.                                                                                                                                                                                                                                                      |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Hyung Won Chung, Le Hou, Shayne Longpre, Barret Zoph, Yi Tay, William Fedus, Yunxuan Li, Xuezhi Wang, Mostafa Dehghani, Siddhartha Brahma, et al. Scaling instruction-finetuned language models. arXiv preprint arXiv:2210.11416, 2022.              |
| Kevin Clark, Urvashi Khandelwal, Omer Levy, and Christopher D Manning. What does bert look at? an analysis of bert’s attention. arXiv preprint arXiv:1906.04341, 2019.                                                                               |
| Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021. |
| Mostafa Dehghani, Stephan Gouws, Oriol Vinyals, Jakob Uszkoreit, and Łukasz Kaiser. Universal transformers. arXiv preprint arXiv:1807.03819, 2018.                                                                                                   |
| Benjamin L Edelman, Surbhi Goel, Sham Kakade, and Cyril Zhang. Inductive biases and variable creation in self-attention mechanisms. In International Conference on Machine Learning, pp. 5793–5831. PMLR, 2022.                                      |
| Guhao Feng, Yuntian Gu, Bohang Zhang, Haotian Ye, Di He, and Liwei Wang. Towards revealing the mystery behind chain of thought: a theoretical perspective. arXiv preprint arXiv:2305.15408 , 2023.                                                   |
| Angeliki Giannou, Shashank Rajput, Jy-yong Sohn, Kangwook Lee, Jason D Lee, and Dim itris Papailiopoulos. Looped transformers as programmable computers.  arXiv preprint arXiv:2301.13196, 2023.                                                                                                                                                                                                                                                      |
| David Goldberg. What every computer scientist should know about floating-point arithmetic. ACM computing surveys (CSUR), 23(1):5–48, 1991.                                                                                                           |
| Michael Hahn. Theoretical limitations of self-attention in neural sequence models. Transactions of the Association for Computational Linguistics, 8:156–171, 2020.                                                                                   |
| Yiding Hao, Dana Angluin, and Robert Frank. Formal language recognition by hard attention trans formers: Perspectives from circuit complexity. Transactions of the Association for Computational Linguistics, 10:800–810, 2022.                                                                                                                                                                                                                                                      |
| William Hesse. Division is in uniform tc0. In International Colloquium on Automata, Languages, and Programming, pp. 104–114. Springer, 2001.                                                                                                         |

| IEEE. Ieee standard for floating-point arithmetic.  IEEE Std 754-2008, pp. 1–70, 2008. doi: 10.1109/IEEESTD.2008.4610935.                                                                                                                   |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Diederik P Kingma and Jimmy Ba. Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980, 2014.                                                                                                                           |
| Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. Large language models are zero-shot reasoners. Advances in Neural Information Processing Systems , 2022.                                                 |
| Kenneth Krohn and John Rhodes. Algebraic theory of machines. i. prime decomposition theorem for finite semigroups and machines. Transactions of the American Mathematical Society, 116: 450–464, 1965.                                      |
| Wang Ling, Dani Yogatama, Chris Dyer, and Phil Blunsom. Program induction by rationale gener ation: Learning to solve and explain algebraic word problems. arXiv preprint arXiv:1705.04146 , 2017.                                                                                                                                                                                                                                             |
| Bingbin Liu, Jordan T Ash, Surbhi Goel, Akshay Krishnamurthy, and Cyril Zhang. Transformers learn shortcuts to automata. arXiv preprint arXiv:2210.10749, 2022a.                                                                            |
| Yong Liu, Siqi Mai, Xiangning Chen, Cho-Jui Hsieh, and Yang You. Towards efficient and scalable sharpness-aware minimization. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 12360–12370, 2022b. |
| Alex Lombardi and Vinod Vaikuntanathan. Fiat-shamir for repeated squaring with applications to ppad-hardness and vdfs. In Advances in Cryptology–CRYPTO 2020: 40th Annual Interna tional Cryptology Conference, CRYPTO 2020, Santa Barbara, CA, USA, August 17–21, 2020, Proceedings, Part III, pp. 632–651. Springer, 2020.                                                                                                                                                                                                                                             |
| Aman Madaan and Amir Yazdanbakhsh. Text and patterns: For effective chain of thought, it takes two to tango. arXiv preprint arXiv:2209.07686, 2022.                                                                                         |
| Oded Maler. On the krohn-rhodes cascaded decomposition theorem. In Time for Verification: Essays in Memory of Amir Pnueli, pp. 260–278. Springer, 2010.                                                                                     |
| Robert McNaughton and Seymour A Papert. Counter-Free Automata (MIT research monograph no. 65). The MIT Press, 1971.                                                                                                                         |
| William Merrill and Ashish Sabharwal. A logic for expressing log-precision transformers. In Thirty-seventh Conference on Neural Information Processing Systems, 2023a.                                                                      |
| William Merrill and Ashish Sabharwal. The parallelism tradeoff: Limitations of log-precision transformers. Transactions of the Association for Computational Linguistics, 11:531–545, 2023b.                                                |
| William Merrill, Yoav Goldberg, and Noah A Smith. On the power of saturated transformers: A view from circuit complexity. arXiv preprint arXiv:2106.16213, 2021.                                                                            |
| William Merrill, Ashish Sabharwal, and Noah A Smith. Saturated transformers are constant-depth threshold circuits. Transactions of the Association for Computational Linguistics, 10:843–856, 2022.                                         |

| Maxwell Nye, Anders Johan Andreassen, Guy Gur-Ari, Henryk Michalewski, Jacob Austin, David Bieber, David Dohan, Aitor Lewkowycz, Maarten Bosma, David Luan, et al. Show your work: Scratchpads for intermediate computation with language models. arXiv preprint arXiv:2112.00114, 2021.                                                            |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Jorge Pérez, Javier Marinković, and Pablo Barceló. On the turing completeness of modern neural network architectures. arXiv preprint arXiv:1901.03429, 2019.                                                                                                                                                                                        |
| Jorge Pérez, Pablo Barceló, and Javier Marinkovic. Attention is turing complete. The Journal of Machine Learning Research, 22(1):3463–3497, 2021.                                                                                                                                                                                                   |
| Nicholas Pippenger and Michael J Fischer. Relations among complexity measures. Journal of the ACM (JACM), 26(2):361–381, 1979.                                                                                                                                                                                                                      |
| Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, and Ilya Sutskever. Language models are unsupervised multitask learners. OpenAI Blog, 1(8), 2019.                                                                                                                                                                                  |
| Laria Reynolds and Kyle McDonell. Prompt programming for large language models: Beyond the few-shot paradigm. In Extended Abstracts of the 2021 CHI Conference on Human Factors in Computing Systems, pp. 1–7, 2021.                                                                                                                                |
| Ronald L Rivest, Adi Shamir, and David A Wagner. Time-lock puzzles and timed-release crypto. 1996.                                                                                                                                                                                                                                                  |
| Bernardino Romera-Paredes, Mohammadamin Barekatain, Alexander Novikov, Matej Balog, M. Pawan Kumar, Emilien Dupont, Francisco J. R. Ruiz, Jordan Ellenberg, Pengming Wang, Omar Fawzi, Pushmeet Kohli, and Alhussein Fawzi. Mathematical discoveries from program search with large language models. Nature, 2023. doi: 10.1038/s41586-023-06924-6. |
| Ian Tenney, Dipanjan Das, and Ellie Pavlick. Bert rediscovers the classical nlp pipeline. arXiv preprint arXiv:1905.05950, 2019.                                                                                                                                                                                                                    |
| Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023.                                                                                      |
| Trieu H Trinh, Yuhuai Wu, Quoc V Le, He He, and Thang Luong. Solving olympiad geometry without human demonstrations. Nature, 625(7995):476–482, 2024.                                                                                                                                                                                               |
| arXiv:1904.02679, 2019. Boshi Wang, Sewon Min, Xiang Deng, Jiaming Shen, You Wu, Luke Zettlemoyer, and Huan Sun.                                                                                                                                                                                                                                    |
| Towards understanding chain-of-thought prompting: An empirical study of what matters. arXiv preprint arXiv:2212.10001, 2022a.                                                                                                                                                                                                                       |
| Kevin Wang, Alexandre Variengien, Arthur Conmy, Buck Shlegeris, and Jacob Steinhardt. Inter pretability in the wild: a circuit for indirect object identification in gpt-2 small. arXiv preprint arXiv:2211.00593, 2022b.                                                                                                                                                                                                                                                                                                                                                     |
| Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Ed Chi, Quoc Le, and Denny Zhou. Chain of thought prompting elicits reasoning in large language models. Advances in Neural Information Processing Systems, 2022.                                                                                                                            |

Gail Weiss, Yoav Goldberg, and Eran Yahav. Thinking like transformers. In International Conference on Machine Learning, pp. 11080–11090. PMLR, 2021.

Christopher B Wilson. Relativized circuit complexity. Journal of Computer and System Sciences , 31(2):169–181, 1985.

Ruibin Xiong, Yunchang Yang, Di He, Kai Zheng, Shuxin Zheng, Chen Xing, Huishuai Zhang, Yanyan Lan, Liwei Wang, and Tieyan Liu. On layer normalization in the transformer architecture. In International Conference on Machine Learning, pp. 10524–10533. PMLR, 2020.

Andrew Chi-Chih Yao. Circuits and local computation. pp. 186–196, 1989.

Shunyu Yao, Binghui Peng, Christos Papadimitriou, and Karthik Narasimhan. Self-attention networks can process bounded hierarchical languages. arXiv preprint arXiv:2105.11115, 2021.

## Contents

| 1 Introduction                                                                    |                                                                                              | 1                                                                                 |
|-----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| 2 Notations and Preliminaries                                                     | 2 Notations and Preliminaries                                                                | 3                                                                                 |
|                                                                                   | 2.1 Decoder-only Transformers  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 3                                                                                 |
|                                                                                   | 2.2 Circuit Complexity  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  | 4                                                                                 |
| 3 Expressiveness Theory for Transformers with Chain of Thought(CoT)               | 3 Expressiveness Theory for Transformers with Chain of Thought(CoT)                          | 6                                                                                 |
|                                                                                   | 3.1 Finite Precision Modeling  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . | 6                                                                                 |
| 3.2                                                                               | CoT: Complexity Class for Constant-depth Transformers with CoT  . . . . . . . . .            | 7                                                                                 |
|                                                                                   | 3.3 Tighter Upper Bounds on Transformer Expressiveness  . . . . . . . . . . . . . . .        | 8                                                                                 |
|                                                                                   | 3.4 CoT Makes Transformers More Expressive  . . . . . . . . . . . . . . . . . . . . . .      | 9                                                                                 |
| 4 CoT Empirically Improves Expressiveness of Low-Depth Transformers on Inherently | 4 CoT Empirically Improves Expressiveness of Low-Depth Transformers on Inherently            | 4 CoT Empirically Improves Expressiveness of Low-Depth Transformers on Inherently |
| Serial Problems                                                                   | Serial Problems                                                                              | 12                                                                                |
| 5 Related Works                                                                   | 5 Related Works                                                                              | 13                                                                                |
| A Additional Experimental Results                                                 | A Additional Experimental Results                                                            | 21                                                                                |
|                                                                                   |                                                                                              | 23                                                                                |
| B Details on Finite-Precision Layers                                              | B Details on Finite-Precision Layers                                                         |                                                                                   |
| C Preliminary of Automata and Krohn-Rhodes Decomposition Theorem                  | C Preliminary of Automata and Krohn-Rhodes Decomposition Theorem                             | 24                                                                                |
|                                                                                   | C.1 The Krohn-Rhodes Decomposition Theorem  . . . . . . . . . . . . . . . . . . . . .        | 25                                                                                |
|                                                                                   | C.2 Counter-free Automata  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 25                                                                                |
| D Proofs for Expressiveness Upper Bounds (Section 3.3)                            | D Proofs for Expressiveness Upper Bounds (Section 3.3)                                       | 26                                                                                |
|                                                                                   | D.1 Proofs for Theorem D.1  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  | 26                                                                                |
|                                                                                   | D.2 Proofs for Theorem D.2  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  | 28                                                                                |
| E Proofs for Expressiveness Lower Bounds (Section 3.4)                            | E Proofs for Expressiveness Lower Bounds (Section 3.4)                                       | 29                                                                                |
| E.1 Proof of Theorem 3.3                                                          | . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .                            | 29                                                                                |
|                                                                                   | E.2 Proof of Theorems 3.7 and 3.8  . . . . . . . . . . . . . . . . . . . . . . . . . . . .   | 32                                                                                |
|                                                                                   | E.3 Proof of Theorem 3.9  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  | 35                                                                                |
|                                                                                   | E.4 Auxiliary Lemmas  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .    | 35                                                                                |
| F Discussion on Variants in Transformer Architecture                              | F Discussion on Variants in Transformer Architecture                                         | 37                                                                                |
|                                                                                   | F.1 Extension to Transformers with LayerNorm  . . . . . . . . . . . . . . . . . . . . .      | 37                                                                                |
|                                                                                   | F.2 Extension to Transformers with Multihead Attention  . . . . . . . . . . . . . . . .      | 37                                                                                |
| G Discussion on Non-uniformity                                                    | G Discussion on Non-uniformity                                                               | 37                                                                                |

## A Additional Experimental Results

In this section present the experimental results for base setting which is omitted in the main paper and the details of training and each task. We use the nanogpt 6 codebase for language modeling.

Training Details. For all settings we use Adam with 10 − 5 learning rate, 0 weight decay, β1 = 0 . 9 , β2 = 0 . 95, and gradient clipping with threshold equal to 1 . 0. The total training budget is 10 6 steps and we use a linear warmup in the first 2000 steps starting from 10 − 6 . For each step, we use a fresh sampled batch of size 64 from population distribution. We turn off dropout and use float16. We vary the depth of the transformer for different settings while the embedding size and the number of attention heads are fixed to be 512 and 8 respectively.

Below we present the setting and the experimental results of each problem respectively.

Modular Addition (Cp Cp ). Given any positive integer p, the vocabulary of modular addition problem is {0 , 1, . . . , p − 1 , = }. We generate x = (x1, . . . , x n ) in the following way: for each i ∈ [n − 1], we independently sample xi from {0 , 1, . . . , p − 1} and set x n = '='. The label is f ∗ (x) = P n − 1 i=1 xi mod p and CoT c(x) is (
P k i=1 xi mod p) n − 1 k=1 . Unsurprisingly, this task is an easy task for transformers because attention can easily express the average function across different positions, and so is the sum function. Then the feedforward layers can compute the modulus of the sum and m. We note that the high training accuracy here is not contradictory with our Theorem 3.1 , because our sequence length is not long enough and float16 is like log-precision. This intuitive argument is elegantly extended to all solvable groups by leveraging Khron-Rhodes decomposition theorem by Liu et al. (2022a).

Permutation Composition (Sp Sp ). Given any p ∈ N + , the vocabulary of permutation composition problem is {1, . . . , p,( , ) , = }. We pick n = (p + 2)m + 1 and generate x = (x1, . . . , x n ) in the following way: for each i ∈ [m], we set x( p+2)(i−1)+1 as '(', x( p+2)i as ')' and independently sample a random permutation over [p] , σi = (x( p+2)(i−1)+2, . . . , x(p+2)(i − 1)+p+1 ). We set x n to be '='. Different from other settings which only have the label at one position, we have p labels for this setting, which is the composition of σ1 ◦ . . . ◦ σ n . The CoT c(x) is the partial composition from σ1 to σ n.

As mentioned in Section 3, unless TC 0 = NC 1 , composition of Sp Sp cannot be computed by TC 0 for any p ≥ 5, since composition of Sp Sp implies the wording problem of Sp Sp , which is NC 1 -complete under AC 0 reductions. Since all constant-depth poly-embedding-size transformers can be simulated by TC 0 circuits (Theorem 3.2), shallow transformers are not able to solve the composition problem of Sp Sp for p ≥ 5. Our experimental results in Figure 3 matches this theoretic prediction very well.

Iterated Squaring (IS). Iterated squaring refers to the following problem: given integers r, n, p , we define the iterated squaring function fr fr,p (n) ≜ r 2 n mod p. It is often used as hardness assumptions in cryptography (Rivest et al. , 1996; Lombardi &amp; Vaikuntanathan , 2020) that iterated squaring cannot be solved in n − o(n) time even with polynomial parallel processors under certain technical conditions (e.g. , p is the product of two primes of a certain magnitude and there is some requirement on the order of r as an element of the multiplicative group of integers modulo p). In other words, people conjecture there is no faster parallel algorithm than doing squaring for n times.

Circuit Value Problem (CVP). Circuit value problem is the computational problem of computing the output of a given Boolean circuit on a given input. It is complete for P under AC 0 -reductions. This means if one can solve CVP with constant-depth transformers (or any TC 0 circuits), then any problem in P becomes solvable by TC 0 , which is widely believed to be impossible.

6 https://github.com/karpathy/nanoGPT

<!-- image -->

Figure 7: Results of Modular Addition C2 .

Figure 8: Results of base on Permutation Composition, Iterated Squaring, and Circuit Value Problem.

<!-- image -->

Figure 9: Results of Modular Addition base on C2 and C7 .

<!-- image -->

We can observe that the accuracy of base setting is also lower than that of hint setting.

## B Details on Finite-Precision Layers

In this section, we give the definition of the finite-precision version of different transformer layers. Recall that given s ∈ N + , the numbers representable using 2s-bit significand and e-bit exponent is F e,s ≜ {S·2 − s+E | −2 2s +1 ≤ S ≤ 2 2s − 1 , − 2
max(0,e − 1) ≤ E ≤ 2e − 1 − 2
max(0,e − 1) , E, S ∈ N} .

Self-Attention Mechanism: Given attention parameter θATTN = (WQ, WK, WV , WO) ∈ F d×d e,s × F d×d e,s × F d×d e,s × F d×d e,s , we define the self-attention layer with causal mask for decoderonly transformer in Algorithm 3 .

## Algorithm 3 Finite-Precision Causal Self-Attention, ATTN

Input: Integer s ∈ N + , e ∈ N, Parameter θATTN = (WQ, WK, WV , WO), Input embedding h = (h1, . . . , h n ) ∈ F nd .

- 3: h ′ i WO ×e,s sume,s([v1, . . . , v n ] × e,s si ) .

e,s Output: Output embedding h ′ = (h ′ 1 , . . . , h ′ n ) ≜ ATTNθ ATTN (h1, . . . , h n ) . 1: qi ≜ WQ × e,s h i , ki ≜ WK × e,s h i
, vi ≜ WV WV ×e,s hi , ∀i ∈ [n] 2: si ≜ softmax e,s (⟨qi, k1⟩ e,s , . . . , ⟨qi, ki⟩ e,s )∥(0 , . . . , 0) . ▷ n − i's 0; Mask for Causal Attention; ≜ WO

Feed-Forward Network: Given s ∈ N
+ , e ∈ N, and the parameter of fully-connected feedforward network layer θFF = (W1, b1, W2, b2) ∈ F d×d e,s × F d e,s × F d×d e,s × F d e,s , we define the fullyconnected feedforward layer FFθ FF : F d e,s → F d e,s as FFθ FF e,s relu([W1 × e,s h + b1]

(h) ≜
h
W2 × e,s ) + b2
i e,s .

Token Embedding: Given s ∈ N + , e ∈ N, and the parameter of token embedding layer θ TE ∈ F d×|V| e,s , we define the token embedding layer by viewing θTE as a mapping from V to R d , that is, for all x ∈ V, the token embedding is θTE(x) .

Position Encoding: Given s ∈ N + , e ∈ N, and the parameter of position encoding layer θ PE ∈ F d×n max e,s , we define the token embedding layer by viewing θPE as a mapping from [n max ] to R d that is, for all n ∈ [n max ], the position embedding is as θPE(n) .

Output Layer: Given s ∈ N + , e ∈ N, and the parameter of output layer θOUTPUT ∈ F |V|×d e,s , we define the output layer OUTPUTθ OUTPUT : F d e,s → V as OUTPUTθ OUTPUT (h) ≜ softmax e,s (θOUTPUT × e,s h) for all h ∈ F d e,s .

Finally, we define finite-precision decoder-only transformers below.

## Algorithm 4 Finite-precision Decoder-only Transformer, TFθ and pθ

Input: Integer s ∈ N + , e ∈ N. Transformer parameter θ = (θPE, θTE, θOUTPUT , {θ (l) ATTN , θ (l) FF } L − 1 l=0 ) with 2s-bit precision and e-bit exponent. Input tokens x = (x1, . . . , x n ) ∈ V n .

Output: Output distribution pθ(· | x1, . . . , xi) for all i ∈ [n] and output token TFθ(x) .

<!-- formula-not-decoded -->

- 2: for l = 0, . . . , L − 1 do

<!-- formula-not-decoded -->

- 4: h (l+1) i ≜ h
h (l+0 . 5) i + FF θ (l) FF (h (l+0 . 5) i )
i e,s , ∀i ∈ [n]
- 5: end for
- 6: pθ(· | x1, . . . , xi) ≜
h
OUTPUTθ OUTPUT (h (L) i )
i e,s , ∀i ∈ [n]
- 7: TFθ(x) ≜ arg max x pθ(x | x1, . . . , x n ) .

## C Preliminary of Automata and Krohn-Rhodes Decomposition Theorem

In this section we recap the basic notations and definitions for automata theory and Krohn-Rhodes Decomposition Theorem (Krohn &amp; Rhodes , 1965), following the notation and presentation of Maler (2010).

Definition C.1 (Automaton) . A deterministic automaton is triple A = (Σ, Q, δ) where Σ is a finite set of symbols called the input alphabet, Q is a finite set of states and δ : Q×Σ → Q is the transition function.

The transition function can be lifted naturally to input sequences, by letting δ(q, wσ) ≜ δ(δ(q, w), σ) for all w ∈ Σ ∗ recursively.

An automaton can be made an acceptor by choosing an initial state q0 ∈ Q and a set of accepting states F ⊆ Q. As such it accepts/recognizes a set of sequences, also known as a language, defined as L(A, q0, F) = {w ∈ Σ ∗ : δ(q0, w) ∈ F}. Kleene's Theorem states that the class of languages recognizable by finite automata coincides with the regular languages.

Definition C.2 (Automaton Homomorphism) . A surjection ϕ : Q → Q0 is an automaton homomorphism from A = (Σ, Q, δ)to A0 = (Σ, Q0, δ0)if for every q ∈ Q, σ ∈ Σ, ϕ(δ(q, σ)) = δ0(ϕ(q), σ) . In such a case we say that A0 is homomorphic to A and denote it by A0 ≤ϕ A. When ϕ is a bĳection, A and A 0 are said to be isomorphic.

The conceptual significance of Automaton Homomorphism is that, if we can simulate any A and A 0 ≤ϕ A, we can 'almost' simulate A0 as well, in the sense of following lemma:

Lemma C.1. For any two automata A = (Σ, Q, δ) , A 0 = (Σ, Q0, δ0) satisfying that A0 ≤ϕ A for some function ϕ, for any F0 ⊆ Q , q0 ∈ Q , ϕ(q) = q0, it holds that L(A0, q0, F0) = L(A, q, ϕ − 1 (F0)) .

Proof of Lemma C.1 . We claim for any w ∈ Σ ∗ , it holds that ϕ(δ(q, w)) = δ(ϕ(q), w). This claim holds by definition of automaton homomorphism for all |w| ≤ 1. suppose the claim already holds for all w no longer than n for some n, for any w ′ = wσ with |w| = n and σ ∈ Σ, it holds that ϕ(δ(q, w ′ )) = ϕ(δ(δ(q, w), σ)) = δ(ϕ(δ(q, w)), σ) = δ(δ(ϕ(q), w), σ) = δ(ϕ(q), w ′ ). Therefore δ 0 (q0, w) ∈ F0 ⇐⇒ δ0(ϕ(q), w) ∈ F0 ⇐⇒ ϕ(δ(q, w)) ∈ F0 ⇐⇒ δ(q, w) ∈ ϕ − 1 (F0). Thus we conclude that L(A0, q0, F0) = {w ∈ Σ ∗ | δ(q0, w) ∈ F0} = {w ∈ Σ ∗ | δ(q, w) ∈ ϕ − 1 (F0)} = L(A, q, ϕ − 1 (F0)) .

Definition C.3 (Semigroups, Monoids and Groups) . A Semigroup is a pair (S, ·) where S is a set and · is a binary associative operation ("multiplication") from S × S to S. A Monoid (S, · , 1) is a semigroup admitting an identity element 1 such that s · 1 = 1 · · · = s for every s ∈ S. A group is a monoid such that for every s ∈ S there exists an element s − 1 ∈ S (an inverse) such that s · s − 1 = 1 .

Definition C.4 (Semigroup Homomorphisms) . A surjective function ϕ : S → S0 is a semigroup homomorphism from (S, ·) to (S0 , ∗ ) if for every s1, s2 ∈ S, ϕ(s1 · s2) = ϕ(s1) ∗ ϕ(s2). In such a case we say that S0 is homomorphic to S and denote it by S0 ≤ϕ S. Two mutually homomorphic semigroups are said to be isomorphic.

Definition C.5 (Transformation Semigroup) . The transformation semigroup of an automata A = (Σ, Q, δ) is the semigroup generated by {δ(·, σ) : Q → Q | σ ∈ Σ} .

## C.1 The Krohn-Rhodes Decomposition Theorem

Below we give the definition of the cascade product of two automata, which is a central concept used in Krohn-Rhodes Decomposition Theorem for automata.

Definition C.6 (Cascade Product) . Let B 1 = (Σ, Q1, δ1) and B2 = (Q1 × Σ, Q2, δ2) be two automata. The cascade product B1 ◦ B2 is the automaton C = (Σ, Q1 × Q2 , δ) where

<!-- formula-not-decoded -->

The cascade product of more than two automata is defined as B1 ◦ B2 ◦ · · · ◦ Bk = (· · ·((B1 ◦ B2) ◦ B 3 · · · ) ◦ Bk .

Definition C.7 (Permutation-Reset Automata) . A automaton A = (Σ, Q, δ) is a permutation-reset automaton if for every letter σ ∈ Σ , σ is either a permutation or reset. If the only permutations are identities, we call it a reset automaton.

Theorem C.2 (Krohn-Rhodes; cf. Maler (2010)) . For every automaton A there exists a cascade C = B 1 ◦ B 2 ◦ · · · ◦ Bk such that:

1. Each B i is a permutation-reset automaton;
2. There is a homomorphism ϕ from C to A;
3. Any permutation group in some Biis homomorphic to a subgroup of the transformation semigroup of A .

The pair (C, ϕ) is called a cascaded decomposition of A .

## C.2 Counter-free Automata

Next we introduce a key concept used in the proof of Theorem D.1 (and thus Theorem 3.1) – Counter-free Automaton.

Definition C.8 (Counter-free Automaton, (McNaughton &amp; Papert , 1971)) . An automaton is counterfree if no word w ∈ Σ ∗ induces a permutation other than identity on any subset of Q .

A subclass of the regular languages is the class of star-free sets defined as:

Definition C.9 (Star-Free regular languages) . The class of star-free regular languages over Σ is the smallest class containing Σ ∗ and the sets of the form {σ} where σ ∈ σ ∪ {ϵ}, which is closed under finitely many applications of concatenation and Boolean operations including union, intersection, and complementation.

It is well-known that languages recognized by counter-free automata have the following equivalent characterizations.

Theorem C.3 (McNaughton &amp; Papert (1971)) . Suppose L is a regular language not containing the empty string. Then the following are equivalent:

1. L is star-free;
2. L is accepted by a counter-free automata.

3. L is non-counting, i.e., there is an n ∈ N so that for all x , y, and z and all m ≥ n , xy m z ∈ L ⇐⇒ xy m+1 z ∈ L .

Counter-free property of an automaton can also be characterized via its transformation semigroup by Lemma C.4, whose proof is straightforward and skipped.

Lemma C.4. An automaton is counter-free if and only if the transformation semigroup of the automaton is group-free, i.e., it has no non-trivial subgroups. A semigroup (S, ·) is group-free if and only if it is aperiodic , i.e., for all s ∈ S, there exists k ∈ N , s k = s k+1 .

Thus Theorem C.5 holds as a corollary of Theorem C.2 .

Theorem C.5 (Corollary of Theorem C.2) . For every counter-free automaton A there exists a cascade C = B 1 ◦ B 2 ◦ · · · ◦ Bk such that each Biis a reset automaton and there is a homomorphism ϕ from C to A .

Using Theorem C.5 the following theorem connects the counter-free automata to constant-depth poly-size circuits with unbounded fan-in. The high-level proof idea is that any reset automaton can be simulated using constantly many depth and any counter-free automaton can be decomposed into the cascade product of a finite number of reset automaton.

Theorem C.6. [Theorem 2.6, Chandra et al. (1983)] Suppose A = (Σ, Q, δ) is an counter-free automaton. Then there is a circuit of size O(n 3 ) with unbounded fan-in and constant depth that simulates δ(q, w) for any q ∈ Q and w ∈ Σ ∗ satisfying |w| = n, where O(·) hides constants depending on the automaton.

## D Proofs for Expressiveness Upper Bounds (Section 3.3)

The main technical theorems we will prove in this section are Theorems D.1 and D.2. Their proofs can be found in Appendices D.1 and D.2 respectively.

Recall ψ e,s : F e,s → {0 , 1} e+2s+1 is the binary representation of floating point with e-bit exponent and 2s-bit precision.

Theorem D.1. For any fixed e ∈ N, s ∈ N + , sum e,s : (F e,s ) n → F e,s has AC 0 circuits. 0

In detail, there is a family of AC circuits {Cn Cn } such that for all x1, . . . , x n ∈ F e,s , it holds that

<!-- formula-not-decoded -->

Theorem D.2. For s(n) = O(poly(n)) , sum0 ,s(n) : (F0 ,s(n) ) n → F 0,s(n) has TC 0 circuits.

0

In detail, there is a family of TC circuits {Cn Cn } such that for all x1, . . . , x n ∈ F 0,s(n)
, it holds that

<!-- formula-not-decoded -->

With Theorems D.1 and D.2 ready, Theorems 3.1 and 3.2 are standard (e.g., see proof of Theorem 4 in Liu et al. (2022a)) and thus are omitted.

## D.1 Proofs for Theorem D.1

Definition D.1 (Total Order) . A total order ≤ on some set X is a binary relationship satisfying that for all a, b, c ∈ X:

1. a ≤ a (reflexive)

2. a ≤ b , b ≤ c =⇒ a ≤ c (transitive)
3. a ≤ b , b ≤ a =⇒ a = b (antisymmetric)
4. a ≤ b or b ≤ a. (total)

Definition D.2 (Ordered Automaton) . We say an automaton A = (Σ, Q, δ) is ordered if and only if there exists a total order ≤ on Q and for all σ ∈ Σ , δ(·, σ) preserves the order, that is,

<!-- formula-not-decoded -->

Theorem D.3. All ordered automata are counter-free. Languages recognizable by any ordered automata belong to AC 0 .

Proof of Theorem D.3 . To show an ordered automaton A = (Σ, Q, δ) is counter-free, it suffices to its transformation semigroup is group-free, or aperiodic. We first recall the definition of aperiodic semigroups Lemma C.4. Let π w : Q → Q, π w (q) ≜ δ(q, w) be the transformation induced by word w ∈ Σ ∗ . Transformation semigroup of A is aperiodic iff for any w ∈ Σ ∗ , there exists k ∈ N, such that (π w ) k = (π w ) k+1 .

Now We claim for any q ∈ Q, there is k ∈ N, such that (π w ) k (q) = (π w ) k+1 (q). Since Q is finite, this implies that there exists k ∈ N, such that (π w ) k = (π w ) k+1 and thus the transformation semigroup of A is aperiodic. First, note that A is ordered, we know π σ is order-preserving for all σ ∈ Σ. Let w = w1 · · · w n where |w| = n, we have π w = π w1 ◦ · · · ◦ π w n is also order-preserving and thus for all q ≥ q ′ ∈ Q , π w (q) ≥ π w (q ′ ). Then we proceed by three cases for each q ∈ Q:

1. π w (q) = q. In this case, it suffices to take k = 0;
2. π w (q) ≥ q. Since π w is order-preserving, we know for any k ∈ N , (π w ) k+1 (q) ≥ (π w ) k (q) . Since Q is finite, there must exist some k ∈ N such that (π w ) k+1 (q) = (π w ) k (q) .
3. π w (q) ≤ q. Same as the case of π w (q) ≥ q .

Since ≥ is a total order, at least one of the three cases happens. This concludes the proof. The second claim follows directly from Theorem C.3 .

For any e, s ∈ N, iterated addition on floating point numbers with e-bit exponent and s-bit significand F e,s can be viewed A e,s = (F e,s, F e,s , δ+) .

Theorem D.4. Automaton A e,s = (F e,s, F e,s , δ+) is ordered, where δ+(x, y) ≜ [x + y] e,s for any x, y ∈ F e,s .

Proof of Theorem D.4 . The total order we use for F e,s as the state space of automaton A coincides with the usual order ≤ on R. Recall the rounding operation is defined as[x] e,s ∈ arg min x ′ ∈F e,s |x−x ′ |
, which means rounding operation is order preserving, that is, for any x ≥ x ′ ∈ F e,s, [x] e,s ≥ [x ′ ] e,s . Thus for any x, x ′ , y ∈ F e,s with x ≤ x ′ , it holds that δ+(x, y) = [x + y] e,s ≥ [x ′ + y] e,s = δ + (x ′ , y). Thus A e,s is ordered.

The following theorem Theorem D.1 is a direct consequence of Theorem D.4 .

## D.2 Proofs for Theorem D.2

We first claim that the following algorithm Algorithm 5 correctly computessum0 ,s(n) over n numbers in F 0,s(n) .

Lemma D.5. Algorithm 5 outputs sum0 ,s(n) (x1, . . . , x n ) for all n ∈ N + and x 1, . . . , xn ∈ F0 ,s(n) .

Proof of Lemma D.5 . Note that y − 2 = 0 , [y − 1 +y0]0 ,s(n) = sign(x1)·B s (n)
, and [sign(x1) · B s (n)+ y1]0 ,s(n) = x1, thus we conclude sum0 ,s(n) (x1, . . . , x n ) = sum0 ,s(n) (y − 2, y − 1, y0, y1, . . . , yn) . Without loss of generality, we can assume that x1 &gt; 0. Therefore S − 2 = 0, S − 1 = B s (n)
, and S0 S0 = 2B s (n)
, which further implies that L − 2 ≤ 0 and U− U− 2 ≥ 2B s (n) . This ensures i ∗ is always well-defined. For convenience we use Hi Hi to denote sum 0,s(n) (y − 2, y − 1, y0, y1, . . . , yi − 1 ) in the rest of this proof.

Now we claim either Si Si
∗ = L i
∗ or Si
∗ = Ui
∗ . By definition of i ∗ , if neither of these two equalities happen, we have that i ∗ ≤ n − 1 , Ui
∗ = Ui
∗+1, and Li∗ = Li
∗+1, which contradicts with the maximality of i ∗ since Ui
∗+1 − L i
∗+1 = Ui
∗ − Li
∗ ≥ 2B s (n)
. Without loss of generality, we assume Si Si
∗ = L i
∗ and the analysis for the other case is almost the same. Now we claim that for all i &gt; i ∗ , no negative overflow happens at position i, that is, Hi + yi ≥ −B s (n) .

We will prove this claim for two cases respectively depending on whether there exists some i ∗ &lt; j &lt; i such that sum0 ,s(n) (y − 2, y − 1, y0, y1, . . . , yj ) = B s (n) . The first case is such j does not exist. Then neither positive or negative overflow happens through i ∗ to i, and thus

<!-- formula-not-decoded -->

If such j exists, we let j ∗ to be the maximum of such j. Then neither positive or negative overflow happens through j ∗ to i. Due to the optimality of i ∗ , we know that for all i, j ≥ i ∗ , |Si − Sj | &lt; 2B s (n) &lt;. Thus

<!-- formula-not-decoded -->

Now we claim Hk
∗ = B s (n)
. Because there is no negative overflow between i ∗ and k ∗ , we have that Hk
∗ − Hi
∗ ≥ Sk
∗ − Si
∗ ≥ 2B s (n) and the fist inequality is only strict when positive overflow happens at some i ∗ ≤ j ≤ k ∗ . If there is no such j, then B s (n) ≥ Hk
∗ ≥ Hi
∗ + 2B s (n) ≥ B s (n) and thus Hk
∗ = B s (n) . Otherwise such j exists and j ∗ be the maximum of such j. Then Hk
∗ ≥ Hj
∗ + (Sk
∗ − Sj Sj ∗ ) ≥ B s (n) + (Sk
∗ − Sj
∗ ) ≥ B s (n)
, where the last inequality is due to the optimality of k ∗ . Thus in both cases we conclude that Hk
∗ = B s (n) .

Finally we will show there is neither negative or positive overflow from k ∗ + 1 to n and thus Hn Hn = Hk
∗ + Sn Sn − Sk
∗ , which would justify the correctness of the algorithm. We have already shown there is no negative overflow. Suppose there is a positive overflow at some j &gt; k ∗ in the sense that Hj Hj−1 + yj ≥ B s (n) and we let j ∗ be the first positive overflow after k ∗ . By definition of j ∗ , there is neither positive and negative overflow between k ∗ + 1 and j ∗ and thus Hj Hj ∗ − 1 + yj
∗ = Hk
∗ + (Sj
∗ − Sk
∗ ) ≤ Hk∗ = B s (n)
, which is contradictory to the assumption that there is a positive overflow at j ∗ . This concludes the proof.

Proof of Theorem 3.2 . It suffices to show that Algorithm 5 can be implemented by a family of TC 0 circuits since Lemma D.5 guarantees the correctness of Algorithm 5. We can treat all the fixed-point floating numbers in the Algorithm 5 as integers with a suitable rescaling, which is 2 s (n)
. Since both sorting and adding n binary integers with polynomial bits have TC 0 circuits, each line in Algorithm 5 can be implemented by an TC 0 circuits (for all indexes i simultaneously if there is any).

Algorithm 5 AC 0 algorithm for iterative addition for poly-precision floating point numbers

```
Input: Integer n ∈ N + , s (n) = O(poly(n)). Floating numbers x1, . . . , x n ∈ F 0,s(n) . Output: ans = sum0 ,s(n) (x1, . . . , x n ) ∈ F0 ,s(n) . 1: y − 2 ← 0, y − 1, y0 ← sign(x1) · B s (n)
, y1 ← x1 − sign(x1) · B s (n)
, yi ← xi, ∀i ∈ {2, . . . , n}; 2: Si Si ←
P i i
j=0 yj , ∀i ∈ {−2, . . . , n}; 3: Ui ← maxi≤j≤ n Sj Sj , Li ← mini≤j≤ n Sj Sj , ∀i ∈ {−2, . . . , n}; 4: i ∗ ← max{−2 ≤ i ≤ n | Ui − Li ≥ 2B s (n) }; 5: if Si Si
∗ = Ui
∗ then 6: k ∗ ← max{i ∗ ≤ k ≤ n | Sk = Li
∗ }; 7: O ← −B s (n)
; 8: else 9: k ∗ ← max{i ∗ ≤ k ≤ n | Sk = Ui
∗ }; 10: O ← B s (n)
; 11: end if 12: ans ← O + Sn Sn − Sk
∗ .
```

## E Proofs for Expressiveness Lower Bounds (Section 3.4)

We first introduce some notations. Since in the construction of the lower bounds we are only using fixed-point numbers, we will use the shorthand F s ≜ F 0,s = {c · k · 2 − s | c ∈ {−1 , 1} , 0 ≤ k ≤ 2 2s − 1, k ∈ N} and rounding operation [·] s ≜ [·]0 ,s . We use 1 s to denote all-one vectors of length s. Similarly we define ⟨· , ·⟩ s
, × s , and softmax s . We recall that for any s ∈ N + and integer 0 ≤ x ≤ 2 s − 1, we use bin s (x) ∈ {0 , 1} s to denote the usual binary encoding of integer x using s binary bits in the sense that x =
P s i=1 2 i (bin s (x))i and sbin s (x) ∈ {−1 , 1} s to denote the signed binary encoding, which is 2bin s (x) − (1 , . . . , 1) .

Recall B s = max F s = 2 s − 2 − s .

Lemma E.1. For any s ∈ N + , it holds that [exp(−B s )] s = 0 .

Proof of Lemma E.1 . By the definition of rounding operation for 2s-bit precision (Definition 3.2), it suffices to show that exp(−B s ) ≤ 2 − s − 1 , that is, B s ≥ ln 2 · (s + 1). Note that 2 s ≥ s + 1 for all s ≥ 1, we have B s /(s + 1) ≥ B s 2 − s = 1 − 2 − 2s ≥ 3/4 ≥ ln 2 .

Using the same argument above, we also have Lemma E.2 .

Lemma E.2. For any s ∈ N + , it holds that [exp(B s )] s = B s.

## E.1 Proof of Theorem 3.3

Given two vectors x, y of the same length s, we use x ⌢ y to denote their interleaving, that is, (x ⌢ y)2i − 1 = xi , (x ⌢ y)2i = yi for all i ∈ [e] .

Lemma E.3. For any s ∈ N + , let qi = sbin s (i) ⌢ 1 s and k i = B s · (sbin s (i) ⌢ (−1 s )) for all i ∈ [2 s − 1], it holds that -exp(⟨qi, kj ⟩ s )
 s = 1[i = j] for all i, j ∈ [2 s − 1] .

Proof of Lemma E.3 . It suffices to prove that ⟨qi, kj ⟩ s = − B s if i ̸= j and ⟨qi, kj ⟩ s = 0 if i = j . The rest is done by Lemma E.1 .

Given any i, j ∈ [2 s − 1], by definition of finite-precision inner product, we know that for any l ∈ [2s − 1], it holds that al =
-
al − 1 + [(qi)l(kj )l] s  s where a0 ≜ 0 and a l ≜ ⟨(qi) : l
, (kj ) : l ⟩ s for l ∈ [2s] .

Figure 10: Relationship diagram between cotcomplexity class with different embedding sizes d(n) and CoT lengths T(n). We fix the precision to be log(n) and the number of exponents bit as 0. This is the counterpart of its finite precision version Figure 1

<!-- image -->

For all l ∈ [e], we have that [(qi)2l(kj )2l] s = − B s and [(qi)2l − 1 (kj )2l − 1 ] s = B s · 1[(sbin s (i))l = (sbin s (j))l]. If i = j, it is straightforward that a2l − 1 = − B s and a 2l = 0 for all l ∈ [e]. If i ̸= j , then there exists l ∈ [s − 1] such that (sbin(i)))l ̸= (sbin(j)))l. Thus [(qi)2l − 1 (kj )2l − 1 ] s = [(qi)2l(kj )2l] s = − B s , which implies a2l = −B s regardless of the value of a2l − 2 . Again use induction we can conclude that a 2l
′ = − B s for all l ≤ l ′ ≤ e .

Proof of Theorem 3.3 . For any L ∈ SIZE[T(n)], by definition there is a family of boolean circuit {Cn Cn } which compute L for all inputs of length n using O(T(n)) many NOT and AND gates. Without loss of generality, let us assume the number of non-input gates in Cn Cn be T(n). We will show that for each n, there is a 2-layer decoder-only transformer TFθ n that computes Cn Cn (x) using T(n) steps of CoT for all x ∈ {0 , 1} n . More precisely, we will construct a transformer that simulates one boolean gate in Cn Cn , following the topological order of the circuit, in each step of its chain of thought.

We first index the gates (including input gates) from 1 to n + T(n) according to the topological order. For each gate i ∈ [n + 1, n + T(n)], we use a(i) and b(i) to denote its two input gates. Since NOT only has one input, we set a(i) as its input and b(i) as 0. We let c(i) = 0 if ith gate is NOT and c(i) = 1 if ith gate is AND. For any input gate 1 ≤ i ≤ n , a (i), b(i), and the gate type are not meaningful and their choice will not affect the output and thus can be set arbitrarily. For convenience, we will set a(i) = b(i) = c(i) = 0. We use gi(x) to denote the output of non-input gate i (n + 1 ≤ i ≤ n + T(n)) on the circuit input x ∈ {0 , 1} n , which is equal to (1 − c(i))(1 − x a (i) ) + c(i)(relu(x a (i) + xb(i) − 1)) .

Now we describe the construction of the vocabulary V, the token embedding θTE, and position encoding θPE. We set precision s as any positive integer larger than 1 , V = {0 , 1} , k ≜ k(n) = ⌈log 2 (T(n) + n)⌉ = O(log n) since T(n) is a polynomial, d ′ (n) = 3k + 6 , θ TE (0) = 0 · e1 , θ TE (1) = 1 · e1, and

(θPE) ⊤ i − 1 = [0 , 0 , 0 , 0, c(i) , sbink(i − 1) , sbink(a(i)) , sbink(b(i)) , 1] , ∀2 ≤ i ≤ n + T(n) . (6)

We use h 0 i
, h 0 . 5 i , h 1 i
, h 1 . 5 i , and h 2 i to denote the intermediate embeddings at position i and different

depths. Here, depth 0 . 5 and 1 . 5 refer to the output of the Attention layer inside each transformer layer.

1. For the first attention layer, denoting embedding at the ith position h 0 i by h, we set the query as qi ≜ (hk+6:2k+5) ⌢ (h3k+6 · 1 s ), the key as ki ≜ (B s h 6:k+5 ) ⌢ (−h3k+6 · 1 s ), and the value as vi ≜ h 1 · e2 . 7
2. For the first fully-connected layer, we skip it by setting its weights to be 0 .
3. For the second attention layer, denoting embedding at the ith position h 1 i by h, we set the query as qi ≜ (h2k+6:3k+5) ⌢ (h3k+6 · 1 s ), the key as ki ≜ (B s h 6:k+5 ) ⌢ (−h3k+6 · 1 s ), and the value as vi ≜ h 1 · e3 .
4. For the second fully-connected layer, we define F(a, b, c) ≜ relu(1 − a − c )+relu(a+b+c−2) . Denote the embedding at position i , h i 1 . 5 by h. The output of the second fully-connected layer is defined as F(h2, h3, h4) · e4. Note this expression is valid because it can be expressed by two-layer ReLU nets with constant bits of precision and a constant number of neurons.
5. The final output at position i is (h 2 i )4 .

Below we first describe the value of the internal variables of the transformer and then show there exist parameters making such computation realizable. Let (x1, . . . , x n ) be the input tokens, we define x n+i ≜ TFi
θ θ n (x1, . . . , x n ) , ∀1 ≤ i ≤ T(n). We claim there exists transformers parameter θ n such that TF T(n) θ n (x1, . . . , x n ) = gT( n ) (x) (i.e. Cn Cn (x)). More specifically, we claim that our constructions will ensure the following inductively for all n + 1 ≤ i ≤ n + T(n) ,

1. h 0 i − 1 = [xi − 1, 0 , 0 , 0, c(i) , (sbink(i − 1)) ⊤ , (sbink(a(i))) ⊤ , (sbink(b(i))) ⊤ , 1] ⊤ ;
2. h 0 . 5 i − 1 = [xi − 1, x a (i)
3. h 1 i − 1 = [xi − 1, x a (i)
4. h 1 . 5 i − 1 =[xi − 1, x a (i)
5. h 2 i − 1 =[xi − 1, x a (i)
6. x i ≜ TF θ n (x1, . . . , x n , . . . , xi − 1 ) = gi(x) .

Now we explain why the above conditions hold for any position i using induction, i.e., assuming it is true for all n+ 1 ≤ i ′ ≤ i. We first notice that by our construction, for all 1 ≤ i ′ ≤ n−1, it holds that (h k i
′ )1 = xi
′ and (h k i
′ )6:k+5 for all k ∈ {0 , 0 . 5 , 1 , 1 . 5 , 2}. Note these are the only information that will be used in the later attention layers.

1. This is simply by the construction of θTE and θPE .
2. In the first attention layer, at the jth position, we have qj ≜ sbink(a(j)) ⌢ 1 s as the query, k j ≜ B s · sbink(j) ⌢ (−1 s ) as the key and vj ≜ xj as the value for all j ∈ [n + T(n)] . Note here we reduce the sizes of hidden embeddings for simplicity of demonstration. This is valid because we can fill the extra coordinates by 0. This is valid because we can always set the extra coordinates to be 0. By Lemma E.3, we know that -exp(⟨qi, kj ⟩ s )

7 Note here the dimension of k i and qi are the same but less than d ′ , which does not strictly satisfy our definition of transformer in Algorithm 3. This is for notational convenience and is without loss of generality because we can pad extra zeros.

3. We set the parameters in the first fully-connected feedforward layer to be all 0 and let the skip connection pass the intermediate values.
4. The second attention layer attains xb(i) and places it in the third coordinate in the same way as step 2.
5. In the fully-connected feedforward layer we compute F(x a (i)
6. The output layer uses the fourth coordinate of h 2 i , which is gi(x) according to induction, as the output.

This completes the proof of Theorem 3.3 .

## E.2 Proof of Theorems 3.7 and 3.8

In this subsection, we prove Theorems 3.7 and 3.8. We first prove a useful lemma that gives an equivalent characterization of SIZE AC 0 and SIZE TC 0 .

Lemma E.4. For any T(n) ∈ poly(n) satisfying T(n) ≥ 1 , ∀n ∈ N
+, a decision problem L : ∪ k∈N+ {0 , 1} k → {0 , 1} belongs to SIZE AC 0 [T(n)] (resp. SIZE TC 0 [T(n)]) if and only if there exist a polynomial S(n), a function T ′ (n) = O(T(n)), and a depth L ∈ N + such that for every n ∈ N + there exist a sequence of sizes-S(n), depth-L circuits, {C
n i C
n } T ′ (n) i=1 , with unlimitedfanin AND , OR and NOT gates (with additionally MAJORITY gates for SIZE TC 0 ) and that for all x ∈ {0 , 1} n ,

<!-- formula-not-decoded -->

Proof of Lemma E.4 . We will prove for SIZE TC 0 only and the proof for SIZE AC 0 is almost the same. The " =⇒ " direction is straightforward. By definition of SIZE TC 0 [T(n)](Definition 3.7), for any L ∈ SIZE TC 0 [T(n)], there is a function p(n) ∈ poly(n) and a family of TC 0 circuits {C
i ′ C
i } ∞ i=1 such that for every n ∈ N and x ∈ {0 , 1} n , L n (x1, . . . , x n ) can be computed by a size-O(T(n)) threshold circuits with oracle gate Cp Cp(n). Now we sort all the nodes in the circuits with oracle gates along the topological order as x1, . . . , x n+T ′ (n) where x1, . . . , x n are the inputs and T ′ (n) = O(T(n)) is the number of the gates, then clearly x n+i is a function of x 1, . . . , xn+i − 1 for all i ∈ [T ′ (n)] and this function can be implemented by a different threshold circuit of constant depth and poly(n) size for each i. This completes the proof of " =⇒ " direction.

Now we prove the other direction "⇐=". We first show that given T ′ (n) sizes-S(n), depth-L circuits, {C
n i C
n } T ′ (n) i=1 , there is a depth-(L + 1), size O(T ′ (n)S(n)) circuit C
n ′ C
n , such that

<!-- formula-not-decoded -->

where 1 j ∈ {0 , 1} T ′ (n)
is the one-hot vector with its jth coordinate being 1. Indeed, it suffices to set

<!-- formula-not-decoded -->

Once we have such oracle gate C
n ′ C
n , given input x1, . . . , x n , we can recursively define

<!-- formula-not-decoded -->

Thus we can compute L(x) = x n+T ′ (n) using T ′ (n) oracle gate C
n ′ C
n . We can get constant gate 0 and 1 by using x1 ∧ ¬x1 and x1 ∨ ¬x1. respectively. This completes the proof.

Now we are ready to prove Theorems 3.7 and 3.8. We will prove Theorem 3.7 first and the proof of Theorem 3.8 is very similar to Theorem 3.7 .

Proof of Theorem 3.7. 7. We first show that SIZE TC 0 [T(n) + 1] ⊇ CoT[T(n) , poly(n) , log n]. For the case that the vocabulary of transformer V = {0 , 1}, by Theorem 3.2, we know for any θ n, TFθ n (x1, . . . , xi) can be expressed by a TC 0 circuit whose depth is uniformly upper bounded by some constant for all n ≤ i ≤ n + O(T(n)). This completes the proof when V = {0 , 1}. When V ̸= {0 , 1}, we can use the binary encoding of elements in V as the inputs of those TC 0 gates constructed for the later layers of the transformer.

Now we turn to the proof for the other direction: SIZE TC 0 [T(n)+1] ⊆ CoT[T(n) , poly(n) , log n] . In high-level speaking, the proof contains two steps:

1. We show that TC 0 ⊆ T[poly(n) , log n] ⊆ CoT[1 , poly(n) , log n]. The first step has two key constructions: (a). using attention to copy all the weights to the same position; (b). we can use polysize two-layer FC net with ReLU activation to simulate MAJORITY , AND , OR gate with unbounded fan-in (Lemma E.5);
2. We can do the first step for all positions i = n + 1, . . . , n + O(T(n) + 1) simultaneously.

By the equivalence construction shown in the Lemma E.4, we know that for any problem L ∈ SIZE TC 0 [T(n) + 1], there exist constant L, polynomial S(n), and T ′ (n) = O(T(n) + 1), and a sequence of threshold circuits, {Cn Cn } n∈N , each of size S(n) (number of non-input gates) and depth of L, and that for all x ∈ {0 , 1} n ,

<!-- formula-not-decoded -->

Now we present the construction of the constant-depth, constant-precision decoder-only transformer, TFθ n which computes problem L when input length is n. Without loss of generality, we only consider the case where T ′ (n) = T(n) + 1. We set vocabulary V = {0 , 1}, embedding width d(n) = 1+3(T(n)+n)+S(n) = O(poly(n)), depth equal to L+1, CoT length T(n) and precision s (n) = ⌈log 2 S(n)⌉ so the precision is high enough for simulating all the poly(n) size MAJORITY gates used in Cn Cn (Lemma E.5). We set (θTE)0 = 0 · e1 , (θTE)1 = 1 · e1, and (θPE)i = ei+1 for all i ∈ [n + T(n)], where we use ei ∈ {0 , 1} d(n)
to denote the one-hot vector whose ith coordinate is 1 for i ∈ [d(n)] and ei ∈ {0 , 1} n+T(n)
to denote one-hot vector whose ith coordinate is 1 for i ∈ [n + T(n)] .

Below we first describe the value the internal variables of the transformer and then show there exist parameters making such computation realizable. To make our claims more interpretable, we only write the non-zero part of the embedding and omit the remaining 0's. the Let (x1, . . . , x n ) be the input tokens and ∆ ≜ 4n + 4T(n) + 1, our constructions will ensure that

<!-- formula-not-decoded -->

2. h 0 i = xie1 + ei+1 = (xi , ei ) ∀i ∈ [n + T(n)];

3. h 0 . 5 i = xie1 + ei+1 = (xi , ei ) , ∀i ∈ [n + T(n)];
4. h 1 i = xie1 + ei+1 + xie n+T(n)+i+1 = (xi , ei, xiei) , ∀i ∈ [n + T(n)];
5. h 1 . 5 i = (xi , ei, xiei, x1, x2, . . . , xi) , ∀i ∈ [n + T(n)]
6. h 2 i = (xi , ei, xiei, x1 , 1, x2 , 1, . . . , xi , 1) , ∀i ∈ [n + T(n)]
7. (h 1+l n+i − 1 )∆+1:∆+2S( n ) ∈ {0 , 1} S(n)
8. (θOUTPUTh L+2 n+i − 1 )0 = 1 − 2C

Now we explain the purpose of each layer and how to set the parameters such that the requirements above are met.

1. x n+i = TF i θ n (x1, . . . , x n ) , ∀i ∈ [T(n)] is the goal of the construction;
2. This is by our construction of θPE and θTE;
3. The first attention layer does nothing by setting all weights to 0;
4. By Lemma E.5 , AND can be simulated by 2-layer ReLU networks using 2 hidden neurons. Thus we use the first feedforward-layer to compute the function (h 1 i ) n+T(n)+1+j = (h 0 . 5 i )1+j ∧ (h 0 . 5 i )1 for all i, j ∈ [n + T(n)] with totally 2(n + T(n)) hidden neurons. Therefore if j ̸= i , then (h 0 . 5 i )1+j = 0, which implies (h 1 i ) n+T(n)+1+j = 0; if j = i, then (h 0 . 5 i )1+j = 1, thus (h 1 i ) n+T(n)+1+j (h 0 . 5 i )1 = xi .
5. This step exactly requires(ATTN θ (1) ATTN (h (1) 1 , . . . , h (1) n ))i =

<!-- formula-not-decoded -->

for all i ∈ [n + T(n) − 1]. Note in this step we use our specific rounding rule to copy all the previous xi with a sum of attention score larger than 1. We can just also use approximately uniform attention scores with an additional coefficient before x i since we have log n precision. Finally we set v 1 . 5 i = WV h 1 . 5 i = e∆+ixi and WO = Id( n ) .

6. The second MLP layer just does permutation and adds some constants into fixed coordinates. The construction is straightforward and thus omitted.
7. The second attention layer is the only attention layer which has non-zero weights. Using the feedforward ReLU networks from layer 2 to L + 1, we can simulate the circuits Cn Cn in parallel for all i ∈ [T(n)] by Lemma E.5. In detail, Lemma E.5 ensures that we can use a twolayer fully-connected ReLU network with weights to simulate a layer of the TC 0 circuits Cn Cn. Moreover, there is enough space in the embedding to reserve S(n)'s 1 needed by Lemma E.5 .

8. This step holds directly due to the property guaranteed in step 8. We note that with the property claimed in step 9, we have that (θOUTPUTh L+2 n+i − 1 )1 − (θOUTPUTh L+2 n+i − 1 )0 = 2Cn Cn (x1, . . . , x n − i+1 )) − 1. Thus if Cn Cn (x1, . . . , x n − i+1 ) = 1, then (θOUTPUTh L+2 n+i − 1 )1 − (θOUTPUTh L+2 n+i − 1 )0 = 1, which impliesTFθ n (x1, . . . , x n+i − 1 ) = 1, otherwise if Cn Cn (x1, . . . , x n − i+1 ) = 0, then TFθ n (x1, . . . , x n+i − 1 ) = 0. In both cases, we have that

<!-- formula-not-decoded -->

So far we have finished the proof for the general T(n). Specifically, when T(n) = T ′ (n) = 0, our proof shows that the constant-depth transformer can still simulate any constant-depth circuit, which
0 means TC 0 ⊆ T[poly(n)] ⊆ CoT[1 , poly(n)] = SIZE T C0 (1) = TC 0 . Thus all the inclusions are equivalence, that is TC 0 = T[poly(n)] = CoT[1 , poly(n)] = SIZE T C0 (1) .

Proof of Theorem 3.8 . We first show that SIZE AC 0 [T(n) + 1] ⊇ CoT[T(n) , poly(n) , 1]. For the case that the vocabulary of transformer V = {0 , 1}, by Theorem 3.1, we know for any θ n, TFθ n (x1, . . . , xi) can be expressed by a TC 0 circuit whose depth is uniformly upper bounded by some constant for all n ≤ i ≤ n + O(T(n)). This completes the proof when V = {0 , 1}. When V ̸= {0 , 1}, we can use the binary encoding of elements in V as the inputs of those TC 0 gates constructed for the later layers of the transformer.

The other direction is almost the same as that of Theorem 3.7, except that we now only need constant bits of precision because we do not need to simulate MAJORITY gates (Lemma E.5).

## E.3 Proof of Theorem 3.9

Proof of Theorem 3.9 . By Lemma E.7, it holds that for all k ∈ N , AC 0 ⊊ SIZE[n k ]. By Theorem 3.7, we know that AC 0 ⊆ CoT[1 , poly(n) , 1] ⊆ CoT[n k , poly(n) , 1] for any k ∈ N. Thus CoT[n k , poly(n) , 1] ⊊ SIZE[n k ] for all k, k ′ ∈ N. Also, note that the attention layer and fullyconnected layer can be computed using poly-size circuits. Thus for any k ∈ N , CoT[n k , log(n)] ⊆ SIZE[n k ′ ]for some integer k ′ ≥ k. Combining these we conclude that for any k ∈ N , CoT[n k , log(n)] ⊊ CoT[n k , poly(n)] .

## E.4 Auxiliary Lemmas

In this subsection, we prove a few auxiliary lemmas that are used in the proofs in Section 3.4 .

Lemma E.5. Unlimited-fanin AND , OR (resp. MAJORITY) : {0 , 1} n → {0 , 1} can be simulated by some 2-layer feedforward ReLU network with constant (resp. log n) bits of precision constant hidden dimension and additional n constant inputs of value 1.

Mathematically, let FF[s(n)] be the set of functions C : {0 , 1} n → {0 , 1} which can be a twolayer feedforward ReLU network with at most s(n) bits of precision and constant hidden dimension FFθ : {0 , 1} 2n → {0 , 1} , FFθ(x ′ ) = W2 × s relu([W1 × s x ′ + b1] s ), where θ = (W2, W1, b1), such that for any x ∈ {0 , 1} n ,

<!-- formula-not-decoded -->

We have unlimited-fanin AND , OR ∈ FF[1] and MAJORITY ∈ FF[log n] .

The proof of Lemma E.5 is based on the following straightforward lemma (Lemma E.6).

Lemma E.6. For any s ∈ N + and a ∈ Z∩F s, relu([a] s )−relu([a − 1] s ) = 1[a &gt; 0]. In particular, for any a ∈ Z , relu(a) − relu(a − 1) = 1[a &gt; 0] .

Proof of Lemma E.5 . Recall that x ⌢ y denotes (x1, y1, x2, y2, . . . , x n , yn) for any x, y ∈ {0 , 1} n . We have that sum s (x ⌢ (−1 n )) ≤ 0 for all s ≥ 2 and x ∈ {0 , 1} n . Moreover, sum s (x ⌢ (−1 n )) = 0 ⇐⇒ ∀i ∈ [n], xi = 1. Similarly, we have that sum s (x) ≥ 0 and sum s (x) = 0 ⇐⇒ ∀i ∈ [n], xi = 0. In other words, we have

- AND(x) = 1[sum s (x ⌢ (−1 n ) ≥ 0)] = 1[⟨x ⌢ 1 n, 1 n ⌢ (−1 n )⟩ s + 1 &gt; 0];
- OR(x) = 1[sum s (x ′ i ) &gt; 0] = 1[⟨x ⌢ 1 n, 1 n ⌢ (0 n )⟩ s &gt; 0] .

Therefore for AND, we can set θ AND ≜ (W
1 AND W
1 , W
2 AND W
2 , b AND 1 ) with W
1 AND W
1 ≜  1 n ⌢ (−1 n ) 1 n ⌢ (−1 n ) 
, b1 =

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Similarly for OR, we can set θ OR ≜ (W
1 OR W
1 , W
2 OR W
2 , b OR 1 ) with W
1 OR W
1 ≜  1 n ⌢ 0 n 1 n ⌢ 0 n 
, b1 =

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

The proofs for AND and OR are thus completed.

Next we deal with MAJORITY. Note that for s(n) ≥ log 2 n+ 1, we have that P n i=1 (2xi −1) = ⟨x ⌢ 1 n, 2 n ⌢ (−1 n )⟩ s for all x ∈ {0 , 1} n .

<!-- formula-not-decoded -->



where θ

⌢

MAJORITY ≜

(W
1

MAJORITY

2

1

W
1

, W
2

MAJORITY

W
2


, b1

<!-- formula-not-decoded -->

Lemma E.7. For all k ∈ N , AC 0 ̸⊆ SIZE[n k ] .

Proof of Lemma E.7. 7. We first define SIZE[T(n)] as the problems solvable by circuits with T(n) standard AND , OR , NOT gates exactly. Thus SIZE[n k ] = ∪C ∈N+ SIZE(Cn k ). Now we claim that for each C ∈ N, there is a N ∈ N + , such that for all n ≥ N, it holds that there is a conjunction normal form (CNF) with at most n k+1 clauses over {x1, . . . , x n } that cannot be expressed by any circuit of size Cn k . This claim holds because of a simple counting argument. There are at

MAJORITY

1

MAJORITY

W
1

=

≜

−

−

, b

) withW
1

2

n

n

⌢

1

n

n

least 2 n k+1 different such CNFs. On the other hand, it is well known that one can represent a T(n)-size circuit only allowing standard AND , NOT , OR gates with 3T(n) log T(n) bits (we need log T(n) bits to encode the id of a gate). Thus the total number of different circuits of size at most Cn k is at most 2 3Cn k (k log n+C)
, which is smaller than 2
n k+1 for sufficiently large n. We denote such n for each C by NC. Now we define the following language LCNF: if the input length of x is NC for some C, use the n k+1 -clause CNF's output which cannot be expressed by size-Cn k circuits as the output; otherwise rejects (output 0). Then clearly LCNF ∈/ SIZE(Cn k ) for all C , thus LCNF ∈ ∪ / C ∈N+ SIZE(Cn k ) = SIZE[n k ]. By construction, LCNF ∈ AC 0 . This completes the proof.

## F Discussion on Variants in Transformer Architecture

## F.1 Extension to Transformers with LayerNorm

Allowing LayerNorm changes the function class that a transformer can express and the position of the layer norm also matters (Xiong et al. , 2020). However, the expressiveness results mentioned in this work still hold for the two most popular transformer architecture variants with LayerNorm — Post LayerNorm and Pre LayerNorm. The upper bounds on transformer expressiveness Theorems 3.1 and 3.2 clearly don't get affected by adding LayerNorm, which can be computed in polynomial time for each token.

Below we focus on the upper bound of the expressiveness of decoder-only transformers with or without CoT. In detail, we will explain why Theorems 3.3 and 3.7 still holds even with LayerNorm. Here the key observation is that, if each coordinate of h ∈ R d ranges from {−1 , 1} and −1 , 1 appear in pairs, then LayerNorm(h) = h. Thus it suffices to show that we can slightly twist the construction of transformers in Theorems 3.3 and 3.7 that for all i ∈ [n + T(n)], l ∈ {0 , 0 . 5 , 1, . . . , L} , h l i is composed of −1 and 1 and they appear in pairs so the sum is always 0. Note that in the current construction, each h l i only contains 0 , − 1 , 1. It suffices to replace each dimension with four dimensions, in the sense 0 → (1 , − 1 , 1 , − 1) , 1 → (1 , 1 , − 1 , − 1) and −1 → (−1 , − 1 , 1 , 1). This can be done by changing the weights of the token embedding, position encoding, and the weights of the second layer of each fully-connected layer. For the outgoing layer, we just use the average of the new representation, which is exactly the same as the original value in all three cases.

## F.2 Extension to Transformers with Multihead Attention

In this paper, for simplicity, we only focus on the case where there is only one attention head in each layer. The main results in this paper still apply if we allow constantly many attention heads, because we can simulate an attention layer with k heads with k attention layers with one head. Allowing an arbitrary number of attention heads while fixing total embedding size might make the constant-depth transformers strictly more expressive in certain settings and we leave it for future works.

## G Discussion on Non-uniformity

Non-uniform computation models allow a different program for each different input length, like boolean circuits. However, the complexity class defined by circuits can also be uniform, if we add additional assumption on the correlation between circuits of different input lengths, e.g., one can require the circuits for input length n can be generated by a Turing Machine taken n as input in using a certain amount of time and space.

The complexity class CoT introduced in this paper can also be made uniform by enforcing an additional assumption, that the parameters of the transformer can be generalized by some Turing Machine given the input sequence length n. It is well-known that one can simulate the execution of the Turing Machine for any T steps by a family of uniform boolean circuits of size O(T 2 ). Thus if we enforce the parameters of transformers in CoT to be uniform, our main theorem would imply that constant-depth transformers with uniform parameters and polynomially many steps of chain of thoughts can solve all problems in P. Also note that the inference of transformers can also be done in polynomial time, we conclude it is exactly equal to P .

One natural question about non-uniformity is that whether having a different transformer for each input sequence length is practical, given that a significant portion of previous theoretical works on transformer expressiveness focuses on the uniform setting. This problem is kind of ill-defined because we haven't been able to scale up the input length to arbitrary length in practice, and thus it is not clear if it is necessary to keep scaling up the size of LLMs for longer input sequence length. But at least for the LLMs that have been seen in practice, it seems quite common to scale up the model size when dealing with longer input sequence length. Also taking the GPT architecture (Radford et al. , 2019) that we focus on in this paper, having more trainable parameters is necessary for longer input sequence length, due to the trainable absolute position encoding.

Still, one needs to note that there is a difference between natural language tasks and complexity class, where the former has a lot of memorization and does not require a strong ability to solve math problems of any sequence length. In contrast, to learn this complexity class like the composition of permutation of any length, transformers need to have the ability of length generalization, which does seem impossible for certain non-uniform models, e.g., like GPT architectures with trainable absolute position encoding, because there is no way to learn the position encoding at an unseen position in the training dataset. Of course, length generalization would still be possible if GPT architecture learned the ground truth without using the trainable position encoding at all.