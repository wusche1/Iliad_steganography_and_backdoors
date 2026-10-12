Steganography with LLMs

Source: recreated from the original Iliad lecture by Stephan Wäldchen and Louis Jaburi
(worksheet section 4.4 and the slides "Unbreakable Steganography with LLMs").
The two watermarking slides and the exercise slide at the end are new.

--
Perfect Security with LLMs: Coupling

source: dewitt2022

recap from the theory part: perfect security needs H(K) >= H(M), so encrypt the message with a one-time pad first
the ciphertext X = M XOR K is uniform, the receiver recovers X and XORs with K

given (both fixed):
 - ciphertext X, uniform
 - covertext C, the LLM's distribution

find a randomized encoder f: x -> S with
 - S ~ C exactly (perfect security)
 - I(X; S) as large as possible

 - theorem 1: f is perfectly secure iff it samples S from row x of a coupling, a joint table over (X, C) with row sums X and column sums C
 - theorem 2: the coupling with maximal I(X; S) is the one with minimum joint entropy H(X, S) (MEC)

s:
this is the perfectly secure counterpart to the PRF scheme that follows

it uses Cachin's model: everyone, including the adversary, knows the covertext distribution exactly

step 1 is the one-time pad from the theory part, the key is as long as the message

theorem 1 is almost a tautology: the stegotext marginal equals the covertext distribution exactly when the joint is a coupling

theorem 2: I(X; S) = H(X) + H(S) - H(X, S), H(X) is fixed and H(S) = H(C) by perfect security, so maximising information means minimising the joint entropy

so the question "what is the best perfectly secure scheme" becomes "find the minimum entropy coupling"

--
Minimum Entropy Coupling: Example

source: dewitt2022

plot: figures/mec_coupling.pdf
2 bits of uniform ciphertext coupled with cat 0.5, dog 0.3, fox 0.2

 - left: independent coupling, the token says nothing about X
 - right: MEC, 1.30 of the 1.49 bits of token entropy carry ciphertext
 - sender: given x, sample the token from row x
 - receiver: given the token, read off the posterior over x (fox: x = 11 for sure, dog: 01 with probability 5/6)

s:
both tables have the same row sums (0.25 each) and the same column sums (0.5, 0.3, 0.2), so both are perfectly secure

the independent coupling ignores the ciphertext completely, it is secure but useless

the MEC concentrates mass on few cells, so the token is informative about x

computed with the greedy algorithm of Kocaoglu et al. 2017: repeatedly match the largest remaining row mass with the largest remaining column mass

exact MEC is NP-hard, but greedy approximations are within about one bit of optimal and keep the marginals exact

the toy example is my own, not from the paper

--
iMEC: Coupling Token by Token

source: dewitt2022

ciphertext and text are far too large for one coupling table, so couple step by step

 - keep a posterior mu over the ciphertext (start: uniform)
 - each token j: couple mu with the LLM's next-token distribution, sample S_j, update mu to the posterior given S_j
 - the receiver runs the same computation and ends with the MAP ciphertext
 - stop once H(mu) < 0.1 bits

plot: figures/imec_posterior.pdf
toy simulation, 10-bit ciphertext block, random next-token distributions

s:
iMEC is from Sokota et al. 2022, de Witt et al. apply it to steganography

the ciphertext is split into blocks, each step couples the block with the highest remaining entropy

every step is a coupling, so every token has exactly the LLM's distribution, perfect security holds for the whole text

the plot is my own toy simulation: each line is one run, the receiver's uncertainty falls roughly by the entropy of each token

the receiver needs the exact same next-token distributions as the sender: the same model, the same prompt, deterministic numerics

--
Task

come up with a steganography protocol that does not assume the decoder has access to the probabilities

--
PRF + LLM = Undetectable Steganography

source: zamir2024

tikz figure: the interval [0, 1] split into cat: 0.5, dog: 0.3, fox: 0.2
LLM(prompt) on the left
F_k(symbol) = 0.62 points into the dog interval, so the output is dog

 - normal sampling: draw a uniform u in [0, 1] and pick the token whose interval contains u
 - steganography: replace u by the output of a secret-keyed PRF that depends on the hidden symbol
 - the PRF output looks uniform, so the token distribution is unchanged
 - any signal with entropy can be turned into a stego channel this way

s:
at every step the language model produces a probability distribution over the next token

example: cat 0.5, dog 0.3, fox 0.2

normally the model samples a random number u and chooses the token by cumulative probability intervals:
cat if u < 0.5, dog if 0.5 <= u < 0.8, fox if 0.8 <= u < 1

the paper keeps this exact sampling procedure, but generates u with a secret-keyed PRF instead of fresh randomness

the model still outputs cat, dog and fox with probabilities 0.5, 0.3, 0.2

the hidden message is encoded by making the PRF input depend on the hidden symbol currently being transmitted

sender and receiver share the PRF and the secret key k

--
Sending and Decoding a Symbol

source: zamir2024

two columns:

Sender
 - wants to transmit a symbol sigma in {0, 1, <-}
 - samples with randomness F_k(r, i, sigma)
 - k: secret key, i: token position, r: prefix of this response
 - pushes the same symbol for several consecutive tokens

Receiver
 - knows k, sees the tokens
 - keeps a score for every candidate symbol 0, 1, <-
 - the score of the correct symbol tends to grow faster
 - once a score crosses a threshold t: record the symbol, reset the scores

s:
to transmit a code symbol the generator uses randomness F_k(r, i, sigma)
k is the secret key, i is the token position, r is a response-specific random prefix

for several consecutive tokens the generator samples using the PRF stream of the current symbol
the visible text still follows the normal LLM distribution

the decoder knows k, so for the observed tokens it computes scores for each candidate symbol
the correct symbol's score tends to grow faster
once one score crosses a threshold, the decoder records that symbol and resets the scores

then the sender moves on to the next symbol

--
Encoding: Sampling a Token Bit by Bit

source: zamir2024

decision tree: 4 tokens, IDs in binary
cat 00 (0.4), dog 01 (0.3), fox 10 (0.2), owl 11 (0.1)

rule: bit i is 1 iff u_i <= p_i, with u_i = F_k(r, i, sigma)

 1. bit 1: p_1 = P(fox/owl) = 0.3, u_1 = 0.62 > 0.3 => bit 0
 2. bit 2: p_2 = P(dog | cat/dog) = 0.3/0.7 ~ 0.43, u_2 = 0.25 <= 0.43 => bit 1
 3. bits 01 => output dog

s:
write every token ID in binary, here 4 tokens need 2 bits

choosing the token is the same as choosing its bits one after another

at each node, p_i is the probability that the next bit is 1, computed from the LLM's token probabilities

the sender uses u_i = F_k(r, i, sigma) as the random number, where sigma is the symbol currently being sent

because u_i looks uniform, dog still comes out with probability 0.7 * 3/7 = 0.3

real vocabularies have about 32,000 tokens, so about 15 bits per token

the numbers are my own toy example

--
Decoding: Scoring the Candidates

source: zamir2024

the receiver sees dog, so the bits are x_1 = 0, x_2 = 1
for each candidate symbol it recomputes u_i and scores how well the bits fit:
s(x_i, u_i) = ln(1/u_i) if x_i = 1, ln(1/(1 - u_i)) if x_i = 0

table:
correct sigma: u_1 = 0.62, s = ln(1/0.38) = 0.97; u_2 = 0.25, s = ln(1/0.25) = 1.39
wrong sigma': u_1 = 0.45, s = ln(1/0.55) = 0.60; u_2 = 0.70, s = ln(1/0.70) = 0.36

 - correct sigma: total 2.36, wrong sigma': total 0.96
 - the receiver never uses p_1 or p_2

s:
the receiver turns the observed token back into bits with the tokenizer

for each candidate symbol it computes u_i = F_k(r, i, sigma') and adds up the scores

a 1 only comes out when u_i <= p_i, so with the correct symbol, 1s come with small u_i and 0s with large u_i, both give high scores

with a wrong symbol, u_i is unrelated to the bits, the score is on average 1 per bit

the correct score grows faster, roughly by the entropy of the text

low-entropy bits (p_i close to 0 or 1) give the correct symbol almost no advantage

the receiver needs only the key and the tokenizer, not the model

--
Perfect vs Computational Steganography with LLMs

source: dewitt2022, zamir2024

table:
                        iMEC (de Witt et al.)              PRF scheme (Zamir)
security                perfect, KL = 0                    computational, assumes PRFs
key                     one-time pad, as long as message   short, reusable
receiver needs          model + prompt, exact numerics     key + text only
capacity                close to the entropy               Theta(L) bits, larger constants
many queries            fresh key material each time       random-prefix trick

s:
both schemes leave the token distribution unchanged, they differ in what the receiver must know and how strong the guarantee is

iMEC: the receiver has to recompute every next-token distribution, so it must know the model and the prompt and reproduce the sampling bit for bit

Zamir: the decoder only needs the key and the text, Zamir points this out as the defining difference of the LLM setting: the channel distribution is unknown to the receiver

safety angle: a model leaking information to an outside reader who does not see the prompt fits Zamir
two instances of the same model that share the context, e.g. a policy and an untrusted monitor, could in principle use MEC

--
From Steganography to Watermarking

source: aaronson2023, dathathri2024

a watermark is steganography with a one-bit payload: "this text came from our model"

 - same construction: the sampler's randomness comes from a keyed pseudorandom function of the key and the preceding tokens
 - different goal: robust detection, and the adversary wants to remove the mark

timeline:
 - 2022: Scott Aaronson and Hendrik Kirchner propose the Gumbel scheme at OpenAI
 - 2024: SynthID-Text by Google DeepMind, based on tournament sampling
 - 2026: Claude's text watermark, a version of the SynthID-Text approach, announced in August for the EU AI Act transparency rules

s:
the steganography paper extends earlier work by Christ, Gunn and Zamir on undetectable watermarks (christ2024)

a watermark only says: this came from the model, there is no message to decode

Anthropic describes Claude's watermark as a version of the SynthID-Text approach, in a family of approaches that goes back to Aaronson's 2022 proposal

the method is public, the key and the exact parameters are not

nothing is added to the text, there are no hidden characters

detection works badly on short texts and on passages with few free choices, such as code

light editing does not remove it, a complete rewrite does

--
The Gumbel Watermark

source: aaronson2023

two columns:

Generation
 - model gives probabilities p_v
 - one pseudorandom number per token v: r = F_k(previous tokens) in [0, 1]^|V|
 - output x = argmax_v r_v^(1/p_v)
 - token v wins with probability exactly p_v

Detection
 - needs the key and the text, not the model
 - recompute r for every observed token x_i
   S = sum_i -ln(1 - r_{x_i})
 - no watermark: S ~ Gamma(n, 1), mean n
 - watermark: S is larger, the gap grows with the entropy of the text

s:
this is the scheme you will implement in the exercise

the key and the previous few tokens seed the pseudorandom numbers

the argmax rule is the Gumbel-max trick: over random r token v wins with probability exactly p_v, so the output distribution is unchanged
but the chosen token tends to have r_v close to 1

detection: without a watermark the r values of the observed tokens are uniform, so each term is exponential with mean 1
the sum of n such terms follows a Gamma distribution with shape n, which gives a p-value

low-entropy text leaves the model few choices, so it carries little watermark

--
Exercise 1: Watermarking

30 minutes

link and QR code to exercises/watermarking/notebook.ipynb

s:
implement the pseudorandom function, the Gumbel sampling rule and the detector

then run the experiments on text length, entropy and editing

bonus: hide a message instead of a single bit, which turns the watermark into the steganography scheme from the talk
