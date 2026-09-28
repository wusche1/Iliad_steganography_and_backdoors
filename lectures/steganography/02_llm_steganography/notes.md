Steganography with LLMs

Source: recreated from the original Iliad lecture by Stephan Wäldchen and Louis Jaburi
(worksheet section 4.4 and the slides "Unbreakable Steganography with LLMs").
The two watermarking slides and the exercise slide at the end are new.

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
Error Correction and Capacity

source: zamir2024

 - LLM and prompt known: the receiver can decode perfectly
 - only the tokenizer known: the receiver decodes probabilistically and sometimes accepts a wrong symbol
 - the payload is encoded with an error-correcting code over {0, 1, <-}
 - <- is a backspace: it repairs an earlier decoding error
 - with an error rate below 0.5 there is net progress towards the correct message

 - capacity: longer, higher-entropy responses carry more payload
 - reuse: each response starts with a natural high-entropy prefix r that enters all later PRF inputs, so every response gets fresh keyed randomness

s:
scenario 1: LLM and prompt are known, the receiver can decode perfectly
scenario 2: only the tokenizer is known, the receiver can still decode probabilistically with error correction

because the decoder can occasionally pick the wrong symbol, the hidden payload is first encoded with a dynamic error-correcting code

if a wrong symbol got accepted, the sender sends a backspace symbol

as long as the error rate is below 0.5, the process has net progress towards correct symbols

the response contains as many hidden symbols as its length and entropy allow

for full security across many queries the model first generates a natural high-entropy prefix r, which is included in later PRF inputs

--
From Steganography to Watermarking

source: aaronson2022, dathathri2024

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
