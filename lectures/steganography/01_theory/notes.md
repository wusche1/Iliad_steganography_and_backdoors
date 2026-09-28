Steganography: Theory

Source: recreated from the original Iliad lecture by Stephan Wäldchen and Louis Jaburi
(worksheet sections 4 to 14 and the slides "Unbreakable Steganography with LLMs").

--
What is Steganography?

two columns:

Cryptography
 - hides the content of a message
 - outsiders cannot read it
 - but everyone sees that a secret is being sent

Steganography
 - hides the existence of a message
 - the secret sits inside an innocent-looking cover
 - an observer sees only ordinary communication

covers can be images, text, sound files or even network protocols

s:
steganography is the art and science of hidden communication

cryptography protects the content of a message by making it unreadable to outsiders
steganography conceals the very existence of the message

the secret is embedded in an innocent-looking cover: an image, a line of text, a sound file, a network protocol

core question: how can information be transmitted without revealing that communication is taking place at all?

link back to the stego game from this morning

--
The Setup

tikz figure: message m -> Encoder E -> stegotext x on channel C -> Decoder D -> message m
secret key k goes into encoder and decoder
warden looks at the stegotext and asks: innocent or stego?

 - encoder E and decoder D share a secret key k
 - a channel C carries the messages
 - a distribution D of innocent messages
 - a message space M of possible secrets
 - a warden observes the channel
 - correctness: decoding succeeds with high probability
 - security: the warden's distinguishing advantage is small

s:
sender and receiver are often called encoder and decoder, they share a secret key

the channel is where messages are transmitted

the innocent distribution describes what ordinary communication over the channel looks like

the message space contains the secret messages the sender may wish to transmit

the encoding procedure embeds a secret message into an apparently innocent message
the decoding procedure recovers it

the adversary, or warden, observes the communication and tries to distinguish ordinary messages from steganographic ones

two conditions: correctness and security

ask: who played which role in the stego game?

--
Detection as Hypothesis Testing

 - innocent channel: the normal language model
 - covertext: the model's response
 - hidden message: a payload embedded in the response
 - adversary: sees the response and decides: ordinary or stego?

for a prompt p:
P = Model(p)       innocent
Q = Steg_k(p, m)   stego

the adversary tests
H_0: x ~ P
H_1: x ~ Q

s:
now the same setup in the LLM setting

P is the innocent distribution over responses for a prompt p
Q is the steganographic distribution when hiding message m with key k

the adversary performs hypothesis testing between the two

the goal is that the adversary cannot reliably distinguish these two cases

--
Perfect Security

the strongest notion is perfect information-theoretic indistinguishability:
P = Q, equivalently d_TV(P, Q) = 0

total variation distance: d_TV(P, Q) = 1/2 sum_x |P(x) - Q(x)|

 - one sample, equal priors: the best possible adversary succeeds with probability
   Pr[correct] = 1/2 (1 + d_TV(P, Q))
 - if d_TV = 0, no adversary can do better than guessing, even with unlimited computation

s:
perfect security means the stego output distribution is exactly the same as the innocent output distribution

total variation distance is the operational distance for hypothesis testing

if the adversary gets one sample and both hypotheses have equal prior probability, the optimal success probability is 1/2 (1 + d_TV)

so with d_TV = 0 no adversary, even an unbounded one, can distinguish stego output from innocent output

question for the room: can we have this? what does it cost?

--
Perfect Security Needs Long Keys

M: message, X: stegotext, K: key
 - perfect security: I(M; X) = 0
 - perfect decoding: H(M | X, K) = 0

H(M) = H(M | X, K) + I(M; X, K)
     = H(M | X, K) + I(M; X) + I(M; K | X)      (first two terms are 0)
     <= H(K | X) <= H(K)

tikz figure: a bar of length H(M), split into three parts
I(M; X) = 0, I(M; K | X) <= H(K), H(M | X, K) = 0

result in a box: H(M) <= H(K)

s:
perfect hiddenness: the observed stegotext reveals no information about the hidden message

perfect decoding: the receiver recovers M exactly from the stegotext and the key

first line is the definition of mutual information, second line is the chain rule

mutual information is bounded by entropy: I(M; K | X) <= H(K | X) <= H(K)

the picture: the entropy of the message splits into three parts, two of them are forced to zero

result: the shared secret must contain at least as much entropy as the hidden message

--
Why This Is Impractical

 - the key has to grow linearly with the message
 - arbitrarily many hidden messages need an unbounded supply of shared randomness, or a way to refresh it
 - this is the one-time pad again: perfect secrecy consumes key material
 - whoever can exchange that much secret randomness could often use that channel directly

steganography is still not useless: it hides the existence of communication, encryption only hides the content

practical schemes use a short reusable key and settle for computational security

s:
H(M) <= H(K) means the key length scales linearly with the message length

a finite fixed key is not enough for arbitrarily many hidden messages

analogous to the one-time pad

if sender and receiver already have a secret channel for large amounts of fresh randomness, they could often use it directly for communication or key refreshment

that does not make steganography useless, since it hides the existence of communication
but perfect information-theoretic steganography is usually expensive in secret randomness

so practical schemes use a short reusable key

--
Computational Security

weaken the requirement

two columns:

Perfect
 - P = Q
 - no one can distinguish the two distributions

Computational
 - P approx Q for efficient observers
 - no polynomial-time adversary can distinguish them with non-negligible advantage

an unbounded adversary may still break the scheme

s:
instead of demanding P = Q against all adversaries, we demand that no efficient adversary can distinguish P from Q

the guarantee is not: no one can distinguish the two distributions
it is: no polynomial-time adversary can distinguish them with non-negligible advantage

this is a reasonable assumption about real adversaries

an unbounded adversary may still break the scheme

--
Pseudorandom Functions

a PRF is a family of keyed functions
F = { F_k : {0,1}^l1(lambda) -> {0,1}^l2(lambda) | k in {0,1}^lambda }

1. F_k is efficiently computable given k
2. for every polynomial-time distinguisher D and a truly random function f:
   | Pr_k[D^F_k(1^lambda) = 1] - Pr_f[D^f(1^lambda) = 1] | <= negl(lambda)

a short key, but to efficient algorithms it looks like a truly random function

s:
lambda is the key length, input and output lengths are polynomial in lambda

the distinguisher gets oracle access: it can query the function but does not see the key

f is a truly random function with the same domain and range

intuition:
a truly random function requires an enormous amount of randomness
a PRF uses only a short key
but to efficient algorithms it looks like a truly random function

--
Assumptions and Attack Cost

left column:

Assumption
 - one-way functions exist
 - this implies that PRFs exist
 - P != NP alone is too weak for modern cryptography

Security argument
 1. assume secure PRFs exist
 2. replace true randomness by PRF output
 3. efficient adversaries cannot tell the difference
 4. so they cannot tell stego from innocent output

right column:

Attack cost
 - generic attack: try all keys of length lambda, O(2^lambda)
 - for each key, check whether the text has the expected statistical structure
 - a weak PRF or a flawed construction allows faster attacks
 - a good scheme makes exhaustive search the best strategy

s:
the relevant assumption is not simply P != NP, that is too weak for modern cryptography

the standard assumption is the existence of one-way functions, which implies the existence of PRFs

go through the four steps of the security argument
efficient adversaries cannot distinguish stego output from innocent output, except with negligible advantage

brute force: for each candidate key the attacker checks whether the observed text has the statistical structure expected under that key
if the correct key is found, the attacker can run the retrieval algorithm and decode the payload

the attack cost is at most 2^lambda by exhaustive search

an unbounded adversary can still brute-force the key

--
Summary: The Trade-off

table:

                      Perfect                 Computational
Guarantee             P_stego = P_innocent    no efficient distinguisher
Key                   H(K) >= H(M), fresh     short, reusable
Assumption            none                    secure PRFs exist
Unbounded adversary   still secure            breaks it, cost up to 2^lambda

s:
perfect information-theoretic steganography requires the stego distribution to equal the innocent distribution exactly
with perfect decoding it requires H(K) >= H(M)
so unlimited perfect hidden communication requires an unlimited or refreshed secret resource

computational steganography uses a short reusable key and a PRF
the output is computationally indistinguishable from innocent model output, assuming the PRF is secure
practical, but only against efficient adversaries
