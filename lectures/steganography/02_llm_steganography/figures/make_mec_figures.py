import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.stats import entropy

OUT = Path(__file__).parent
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 17, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "text.color": INK, "axes.labelcolor": INK})


def greedy_mec(p, q):
    p, q, joint = p.copy(), q.copy(), np.zeros((len(p), len(q)))
    while p.max() > 1e-12 and q.max() > 1e-12:
        i, j = p.argmax(), q.argmax()
        m = min(p[i], q[j])
        joint[i, j] += m
        p[i] -= m
        q[j] -= m
    return joint


# Figure 1: independent coupling vs minimum entropy coupling
cipher = np.full(4, 0.25)
tokens = np.array([0.5, 0.3, 0.2])
couplings = {"Independent coupling": np.outer(cipher, tokens), "Minimum entropy coupling": greedy_mec(cipher, tokens)}
fig, axes = plt.subplots(1, 2, figsize=(8, 5))
for ax, (title, g) in zip(axes, couplings.items()):
    mi = entropy(cipher, base=2) + entropy(tokens, base=2) - entropy(g.ravel(), base=2)
    ax.imshow(g, cmap="Blues", vmin=0, vmax=0.3)
    for (i, j), v in np.ndenumerate(g):
        if v > 0:
            ax.text(j, i, f"{v:.3g}", ha="center", va="center", color="white" if v > 0.15 else INK)
    ax.set_xticks(range(3), [f"{t}\n{p}" for t, p in zip(["cat", "dog", "fox"], tokens)])
    ax.set_yticks(range(4), ["00", "01", "10", "11"])
    ax.set_ylabel("ciphertext $X$")
    ax.set_title(f"{title}\n$I(X; S) = {mi:.2f}$ bits", color=INK)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "mec_coupling.pdf")

# Figure 2: iMEC on a toy autoregressive channel, one 10-bit ciphertext block
rng = np.random.default_rng(0)
fig, ax = plt.subplots(figsize=(7, 5))
for run in range(20):
    mu, x, h = np.full(1024, 1 / 1024), rng.integers(1024), [10.0]
    while h[-1] > 0.1:
        c = rng.dirichlet(np.full(40, 0.1))
        g = greedy_mec(mu, c)
        s = rng.choice(40, p=g[x] / g[x].sum())
        mu = g[:, s] / g[:, s].sum()
        h.append(entropy(mu, base=2))
    ax.plot(h, color=BLUE, lw=2, alpha=0.35)
ax.axhline(0.1, color=MUTED, lw=1, ls="--")
ax.text(0.3, 0.35, "stop: $H(\\mu) < 0.1$", color=MUTED)
ax.set_xlabel("stegotext token $j$")
ax.set_ylabel("posterior entropy $H(\\mu)$ [bits]")
ax.set_title("10-bit ciphertext, 20 toy runs", color=INK)
fig.tight_layout()
fig.savefig(OUT / "imec_posterior.pdf")
