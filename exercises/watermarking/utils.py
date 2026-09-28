"""Generation helper and test functions for the watermarking exercise."""
import numpy as np
import torch
from scipy import stats
from transformers import DynamicCache


# ── Generation ──

def generate(model, tokenizer, prompt, sampler, n_tokens, temperature=1.0):
    history = tokenizer(prompt).input_ids
    n_prompt = len(history)
    inputs, past = torch.tensor([history]), DynamicCache()
    with torch.no_grad():
        for i in range(n_tokens):
            out = model(inputs, past_key_values=past, use_cache=True)
            past = out.past_key_values
            probs = torch.softmax(out.logits[0, -1].double() / temperature, dim=-1).numpy()
            token = int(sampler(probs, history, i))
            history.append(token)
            inputs = torch.tensor([[token]])
    return history[n_prompt:]


# ── Reference implementations (built on the student's prf) ──

def _gumbel_sample(probs, r):
    return int(np.argmax(np.log(r) / probs))


def _watermark_score(prf, tokens, key, vocab_size, context_size):
    seen = set()
    score = 0.0
    for i in range(context_size, len(tokens)):
        pair = (tuple(tokens[i - context_size:i]), tokens[i])
        if pair in seen:
            continue
        seen.add(pair)
        score += -np.log(1 - prf(key, pair[0], vocab_size)[pair[1]])
    return score, len(seen)


# ── Tests ──

def test_prf(prf):
    print("Testing prf...", end=" ")
    r = prf(b"key", (1, 2, 3, 4), 50_000)
    if np.shape(r) != (50_000,):
        print(f"FAIL (expected shape (50000,), got {np.shape(r)})")
    elif r.min() < 0 or r.max() >= 1:
        print("FAIL (values must lie in [0, 1))")
    elif not np.array_equal(r, prf(b"key", (1, 2, 3, 4), 50_000)):
        print("FAIL (same key and context must give the same numbers)")
    elif np.array_equal(r, prf(b"other", (1, 2, 3, 4), 50_000)):
        print("FAIL (output does not depend on the key)")
    elif np.array_equal(r, prf(b"key", (1, 2, 3, 5), 50_000)):
        print("FAIL (output does not depend on the context)")
    elif stats.kstest(r, "uniform").pvalue < 1e-3:
        print("FAIL (values do not look uniform)")
    else:
        print("PASS")


def test_gumbel_sample(gumbel_sample):
    print("Testing gumbel_sample...", end=" ")
    rng = np.random.default_rng(0)
    for _ in range(200):
        probs, r = rng.dirichlet(np.ones(50)), rng.random(50)
        if gumbel_sample(probs, r) != _gumbel_sample(probs, r):
            print("FAIL (wrong token for a given probs and r)")
            return
    probs = np.array([0.5, 0.3, 0.2])
    samples = [gumbel_sample(probs, rng.random(3)) for _ in range(20_000)]
    freqs = np.bincount(samples, minlength=3) / len(samples)
    if np.abs(freqs - probs).max() > 0.02:
        print(f"FAIL (token frequencies {freqs} do not match probs {probs})")
    else:
        print(f"PASS (token frequencies {freqs.round(3)} match probs {probs})")


def test_watermark_score(watermark_score, prf):
    print("Testing watermark_score...", end=" ")
    rng = np.random.default_rng(0)
    tokens = rng.integers(0, 100, size=60).tolist()
    tokens = tokens + tokens[:20]
    score, n = watermark_score(tokens, b"key", 100, context_size=4)
    ref_score, ref_n = _watermark_score(prf, tokens, b"key", 100, 4)
    if n != ref_n:
        print(f"FAIL (counted {n} tokens, expected {ref_n}. Did you skip repeated (context, token) pairs?)")
    elif not np.isclose(score, ref_score):
        print(f"FAIL (score {score:.3f}, expected {ref_score:.3f})")
    else:
        print("PASS")


def test_p_value(p_value):
    print("Testing p_value...", end=" ")
    for score, n in [(100.0, 100), (150.0, 100), (20.0, 40), (400.0, 200)]:
        if not np.isclose(p_value(score, n), stats.gamma.sf(score, n), rtol=1e-6, atol=0):
            print(f"FAIL (p_value({score}, {n}) = {p_value(score, n):.3e}, expected {stats.gamma.sf(score, n):.3e})")
            return
    print("PASS")


def test_decode_message(decode_message, prf):
    print("Testing decode_message...", end=" ")
    rng = np.random.default_rng(0)
    message = rng.integers(0, 2, size=12).tolist()
    vocab_size, block_len, context_size = 100, 15, 4
    tokens = rng.integers(0, vocab_size, size=context_size).tolist()
    for i in range(len(message) * block_len):
        probs = rng.dirichlet(np.ones(vocab_size))
        context = tuple(tokens[-context_size:]) + (message[i // block_len],)
        tokens.append(_gumbel_sample(probs, prf(b"key", context, vocab_size)))
    decoded = decode_message(tokens[context_size:], b"key", vocab_size, len(message), block_len, context_size=context_size)
    if list(decoded) == message:
        print("PASS")
    else:
        print(f"FAIL (decoded {list(decoded)}, expected {message})")
