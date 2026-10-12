## BACKDOOR CHANNELS HIDDEN IN LATENT SPACE: EXTENDING CRYPTOGRAPHIC UNDETECTABILITY TO MODERN NEURAL NETWORKS

Marte Eggen 1 , Eirik Reiestad 1 , Kristian Gjøsteen 2 , Inga Strümke 1

1 Department of Computer Science, Norwegian University of Science and Technology 2 Department of Mathematical Sciences, Norwegian University of Science and Technology {marte.eggen, eirik.reiestad, kristian.gjosteen, inga.strumke}@ntnu.no

## ABSTRACT

Recent cryptographic results establish that neural networks can be backdoored such that no efficient algorithm can distinguish them from a clean model. These guarantees, however, have been confined to stylised architectures of limited practical relevance, leaving open whether comparable undetectability extends to modern, end-to-end trained networks. We construct such an attack mechanism for state-ofthe-art architectures, closely aligned to the cryptographic notion of undetectability, by identifying backdoor channels as learned latent directions, and show that the question of undetectability reduces to a hypothesis test between two unknown distributions over model parameters, which we conjecture to be intractable in practice. The consequence of this reframing is significant: if exploitable channels within a network's latent space are statistically indistinguishable from naturally learned directions, an attacker need not introduce foreign structure but can instead exploit the geometry the network already possesses. Demonstrating the approach on ResNet and Vision Transformer architectures trained on standard image classification datasets, the attack achieves both consistently high success rates with negligible clean accuracy degradation, and resists a comprehensive suite of post-training defences, none of which neutralise the backdoor without rendering the model unusable. Our results establish that cryptographic backdoors need not be artefacts requiring exotic architectures or artificial constructions, but identifiable as latent properties inherent to the geometry of learned representations.

Keywords deep learning · backdoor attack · cryptography · sparse PCA · concept activation vectors

## 1 Introduction

The black-box nature of deep neural networks conceals vulnerabilities exploitable as backdoor channels within their latent activation spaces. This concern is not hypothetical: the modern machine learning supply chain increasingly depends on third-party datasets, pre-trained foundations, and specialised computation facilities, which has given rise to Machine Learning as a Service (MLaaS)[10 , 26 , 13]. Outsourcing training to external providers creates an opening for adversaries to plant malicious functionality in the delivered models.

A well-studied class of threats are backdoor (or Trojan) attacks, in which an adversary embeds a hidden association such that the model performs normally on clean inputs but produces attacker-controlled outputs when a specific input trigger is present [1]. Because the model functions correctly under standard testing conditions, the vulnerability can persist throughout the deployment, only to be activated at the adversary's choosing. Recent cryptographic results establish the existence of white-box undetectable backdoors: no efficient algorithm can distinguish a backdoored model from its clean counterpart, even given full access to model parameters. Goldwasser et al. [10 , 11] prove this for single-hidden-layer random ReLU networks under standard hardness assumptions on sparse PCA. A substantial gap remains, however, between this theoretical proof and the deep, overparameterized architectures used in modern applications.

In this work, we bridge this gap by identifying naturally occurring backdoor channels in the activation spaces of state-of-the-art architectures, enabling a backdooring mechanism we conjecture is computationally indistinguishable from a clean model. Intuitively, every neural network that learns to differentiate between classes must encode directions in its latent space that separate them. By integrating concept activation vectors (CAVs) [19] into a methodology aligned with the cryptographic techniques proven to yield white-box undetectable backdoors [10 , 11], we amplify these directions to activate in a controlled manner, enabling targeted misclassification – redirecting inputs from a given class to a specified target – when a trigger is present. Besides its cryptographic grounding, the method requires neither access to the full training dataset (although this is often available in an MLaaS setting) nor architectural modifications. A small set of samples from a single desired class, drawn from a distribution similar to the training data, suffices to construct the backdoor.

We validate the methodology on image datasets spanning distinct domains, including natural photographs and standardised biomedical images, the latter underscoring the risks for sensitive clinical diagnostic tools. Generalisability is demonstrated across two widely used architectures: a CNN (ResNet18 [16]) and a transformer-based model (Vision Transformer [8]). This work makes the following contributions:

- A practical realisation of conjecturally white-box undetectable backdoors. We construct a backdooring methodology for state-of-the-art image classifiers that closely aligns with the theoretical construction of Goldwasser et al. [10 , 11], suggesting that the conditions enabling undetectability are not exclusive to the stylised architectures for which they have been formally established.
- Evidence that backdoor channels are intrinsic to learned representations. We show that all trained neural networks contain latent directions exploitable as backdoors when the attacker can modify the model and as adversarial perturbations when they cannot, implying such channels need not be planted, only identified.
- An indistinguishability analysis. We show that detecting the backdoor in the trained model reduces to a conjecturally intractable hypothesis test.
- Cross-architecture generalisation. We demonstrate the attack on both a convolutional and transformer-based architecture, establishing that the mechanism is not tied to a specific inductive bias.
- Resilience against established defences. We evaluate the backdoored models against fine-pruning [23], parameter clipping, parameter noise injection, Neural Cleanse [31] and SmoothInv [30]; none neutralise the attack without rendering the model unusable.

## 2 Related work

Abbasi et al. [1] provide a comprehensive categorisation of backdoor attacks in computer vision. The literature is predominantly focused on dataset poisoning, in which a fraction of the training data is manipulated for the model to learn trigger-label associations [7]. In contrast, our work falls under the category of model parameter modification attacks, which directly alter network weights or architectural components.

Goldwasser et al. [10 , 11] introduce cryptographically grounded methods for planting undetectable backdoors in classifiers. Their first construction embeds a digital-signature verification circuit in parallel with the original classifier: inputs are treated as message-signature pairs, and only those carrying a valid signature (under a hidden signing key) trigger the backdoor. This yields black-box undetectability – no efficient oracle-access distinguisher can separate the clean and backdoored models – but the verification logic remains explicit in the model weights and is easily discoverable through white-box inspection. To achieve the stronger guarantee of white-box undetectability, the authors construct backdoors both within Random Fourier Feature models [25] and in random ReLU networks, proving indistinguishability of the latter via the hardness of sparse PCA even when the adversary has access to parameters and training data. Both constructions, however, are mainly of theoretical interest: neither employs the end-to-end learned representations, architectural designs, nor optimisation strategies characteristic of modern high-performing classifiers. As also noted by Kalavasis et al. [18], "Goldwasser et al. [10 , 11] leave open the question of whether undetectability is possible for general models under white-box access".

A recent preprint by Choudhary et al. [6] suggests a realisation of the theoretical results of Goldwasser et al. [10 , 11] in state-of-the-art neural networks, planting provably undetectable backdoors in pre-trained image classifiers. Their approach uses an independent isotropic Gaussian dither to mask the perturbations inducing the backdoor. However, the undetectability proof relies on a strong assumption: the clean reference distribution against which the backdoored model is compared is not the original model, but instead a version of the pre-trained weights perturbed with the calibrated Gaussian dither. Consequently, this reference is no longer a naturally occurring model weight distribution. Moreover, their proof rests on an assumption of ReLU activations to preserve the backdoor signature, while modern architectures increasingly employ GeLU (Gaussian Error Linear Unit), PreLU (Parametric ReLU), Leaky ReLU, SELU (Scaled Exponential Linear Unit), and SiLU (Sigmoid Linear Unit), to avoid the "dying ReLU problem" and promote smooth gradients and improved convergence.

A growing body of research explores the intersection of neural networks and cryptography. Kalavasis et al. [18] use indistinguishability obfuscation to plant white-box undetectable backdoors by converting neural networks into Boolean circuits, embedding the hidden backdoor via cryptographic primitives, and finally reconverting them. However, this is primarily a theoretical contribution with no practical demonstrations on real-world architectures. In a similar vein, Draguns et al. [9] introduce backdoors in transformer-based language models that are unelicitable by any polynomiallybounded adversary even under white-box access. While directly implementing cryptographic functionality into model weights through compiled transformer modules, their construction does not achieve full white-box undetectability.

Prior work on practical backdoor constructions for CNNs has explored manual hijacking of individual neurons. Hong et al. [17] introduce a handcrafted backdoor attack that directly manipulates model parameters to establish a path from the input trigger to the target output. Similarly, Cao et al. [5] propose a data-free backdoor attack that recalibrates a single neuron per layer to serve as a signal amplifier responsive to a specific trigger but unlikely to be activated by clean inputs. Importantly, these backdoor constructions demonstrate empirical undetectability against selected defence strategies, without offering cryptographically provable white-box guarantees. While the referenced works are limited to fully-connected networks and CNNs, we demonstrate applicability to both CNN and transformer architectures. Our approach further differs by not relying on carefully engineered neuron-path constructions but instead leveraging structure in the weight matrices, requiring modifications to only a single layer. While Lamparth and Reuel [22] also analyse internal representations to identify network components important for a backdooring mechanism, the backdoor originates from data poisoning and lacks formal cryptographic assurances.

Backdoor defences at the deployment phase are intended to detect and eliminate backdoors in pre-trained networks [5]. Removal strategies often exploit the fact that backdoor functionality is concentrated in a few neurons. Liu et al. [23] propose fine-pruning, which removes weights inactive on clean data, where backdoor behaviour is hypothesised to concentrate, and subsequently fine-tunes to recover performance. Trigger reverse-engineering aims to reconstruct potential triggers; for instance, Neural Cleanse [31] uses an optimisation scheme to find the minimal input perturbation required to cause misclassification for each label, flagging the backdoored class as a statistical outlier with an abnormally small trigger. This approach is widely adopted [15], yet detecting and mitigating blended triggers spreading across pixels remains a substantially harder problem than that of identifying localised patch patterns, as the former leave only subtle traces and often resemble in-distribution variations [1]. A related approach is SmoothInv [30], which uses multiple noisy versions of a single clean image to construct a robust smoothed version of the backdoored classifier, before performing image synthesis towards a specified target class. The resulting perturbation serves as the recovered trigger. Other strategies include parameter-space defences that target anomalies in weight statistics, such as unusual layer-wise distributions or subtle perturbations, or probing latent representations for poisoning signatures [1].

## 3 Theoretical background and problem formulation

## 3.1 Undetectable backdoors in single-hidden-layer random ReLU networks

Goldwasser et al. [10 , 11] plant white-box undetectable backdoors in single-hidden-layer random ReLU networks for binary classification. Specifically, for an input x ∈ R d and a hidden layer in R m with features ϕi(x) = ReLU(⟨gi , x ⟩) , where gi ∼ N (0, Id), the network output is determined by thresholding the activations using a carefully tuned parameter τ . The backdoor is planted by replacing the standard Gaussian weights with a distribution hiding a sparse spike, namely

<!-- formula-not-decoded -->

for a parameter θ and a direction given by a sparse vector ν ∈ R d . This spike signal increases the variance of the inputs along a specific direction ν, which in turn increases certain activations in the subsequent output layer. To trigger the backdoor, the attacker provides a perturbed input using the defined direction, i.e., xˆ ˆ = x + λν with a weight λ &gt; 0 .

This backdoor is undetectable (though the advantage is o(1), it is not negligible in the cryptographic sense) when parameters are chosen appropriately because weights sampled from a standard Gaussian distribution would be computationally indistinguishable from weights sampled from a distribution hiding a sparse spike, which Brennan and Bresler [4] show follows from the conjectured hardness of detecting planted cliques in certain graphs.

For clean inputs, the projection onto the secret direction ν resembles random noise, leaving the backdoor dormant. Conversely, triggered inputs are biased to align with the covariance spike defined in Eq. (1). This alignment shifts the activation space representation sufficiently to hopefully cross the decision boundary, causing an incorrect classification to the class intended by the attacker. The effect of the secret key is illustrated in Fig. 1, and the spiked covariance is visualised in App. A.

Figure 1: PCA visualisation of the activation space of a backdoored single-hidden-layer ReLU network. The coloured regions represent projected class samples; blue points show randomly selected class 0 samples and red points their triggered counterparts. The displacement from clean to triggered inputs aligns with the secret key direction, illustrated by the arrow.

<!-- image -->

## 3.2 Undetectable backdoors in state-of-the-art image classification networks

As stated by Goldwasser et al. [10 , 11], no effort was made to optimise the construction outlined in Sec. 3.1, nor has it been in subsequent peer-reviewed work. Consequently, its practical utility remains unverified. The reliance on a simplified architecture and a learning framework constrained by the tuning of a single threshold parameter τ imposes significant limitations on the neural network's ability to generalise. Building on the theoretical framework established by Goldwasser et al. [10 , 11], we demonstrate that backdoors motivated by the same design principles can be successfully planted in state-of-the-art deep neural networks for computer vision, trained using backpropagation to solve classification tasks on commonly adopted datasets.

Let f : R h×w×c → R k define a neural network mapping an input image x ∈ R h×w×c to an output space of k classes. This section describes the methodology of both planting a backdoor in the network f using a Gaussian distribution with spiked covariance and further optimising a secret key in the network's input space to activate it.

Gaussian distribution with spiked covariance We augment the classification head with an additional linear layer immediately preceding the output, denoted by f
( ℓ bd ) : R d → R m , prior to training. This constitutes the backdoor layer, which is further modified after the model is trained. Its parameters are subsequently absorbed into the output layer, preserving the original model architecture. Goldwasser et al. [10 , 11] plant the backdoor by replacing untrained weights with weights sampled from a Gaussian distribution with spiked covariance. In our case, simply replacing the weights in layer ℓbd of a trained model would break the learned coupling between the backbone and the classification head. Instead, we modify the spiked covariance distribution to incorporate the scalar variance σ 2 ∈ R of the learned weights in layer ℓ bd , denoted W(ℓbd) ∈ R
m×d .

If the weights were independent with a zero-mean Gaussian distribution with variance σ 2 , we could insert a spike boosted by a parameter θ along a chosen backdoor direction with a simple linear transformation. If our goal is a covariance matrix similar to that in Eq. (1), i.e.,

<!-- formula-not-decoded -->

where νb νbd ∈ R m is a m α -sparse vector of unit norm ||νbd||2 = 1, we know that Σ is positive-definite, meaning the Cholesky decomposition can be used to find a lower-triangular matrix L such that LL T = Σ. Sampling weights from N (0, σ 2 Im Im ) and multiplying by L/σ would then be statistically identical to sampling weights from N (0, σ 2 Im Im + θνb νbdν
b T ν
bd ), as shown in App. B. The basic idea is to first reset the weights to unit variance and then use the L matrix, which essentially contains the geometric instructions to insert the desired spike.

In a trained network, the weights W( ℓ bd ) will not be independent, so the corresponding covariance matrix will not be diagonal and the above argument does not precisely work. However, it is reasonable to assume that it is sufficiently close to diagonal that the linear transformation will actually succeed in planting a spike, without otherwise changing the network structure too much. We validate this expectation in Sec. 5, and a discussion on the empirical structure of the weight covariance is provided in App. C.

To summarise, we insert the backdoor by replacing the weights in layer ℓbd by

<!-- formula-not-decoded -->

To restore the original architecture, we absorb the added backdoor layer into the output layer. This is possible if layer ℓ bd uses a linear activation function at the backdoor injection stage, although a non-linear activation function may be used during clean training. The composition of the backdoor and output layers is therefore equivalent to a single affine transformation,

<!-- formula-not-decoded -->

which yields

<!-- formula-not-decoded -->

Hence, the backdoor layer can be removed by updating the output layer parameters as

<!-- formula-not-decoded -->

ˆ

The resulting backdoored neural network, denoted by f, thus behaves identically to the model containing the explicit backdoor layer and is – except for the weights in the output layer – identical to its clean counterpart f .

Secret keys The vector νbd in Eq. (2) is referred to as the secret key defined in the activation space of the backdoor layer ℓbd. The primary objective of the backdoor is to enable targeted misclassification, redirecting inputs from a source class, denoted x source , to a specified target class, only when the trigger is present. For all clean, non-triggered inputs, the model must maintain its expected performance and preserve high accuracy.

While Goldwasser et al. [10 , 11] plant the covariance spike along a random high-dimensional direction, we strategically select a direction bridging the source and target class manifolds, effectively pushing triggered input representations across the decision boundary. The direction is obtained by training a logistic regression classifier to discriminate between the activation sets {f
( ℓ bd ) (x source ) : x source ∈ D source } and {f
( ℓ bd ) (xtarget) : xtarget ∈ Dtarget}, where D source and D target are equally sized sets of inputs from each respective class. The normal vector to the resulting linear hyperplane defines the direction from the manifold of the source class to that of the target class, serving as the basis from which the secret key νbd is constructed. This normal vector is similar to the CAV introduced by Kim et al. [19], which represents a high-level concept within a model's latent space and is defined by the direction orthogonal to a concept-separating boundary. To satisfy the sparsity requirement in Eq. (2) while preserving the original direction, only the top α% of entries with the largest magnitudes are retained, setting all others to zero. The resulting vector is normalised to unit norm.

Because the intermediate layers non-linearly transform the data between the input space and the backdoor layer, altering both dimensionality and geometry, a single key cannot simultaneously define the input-space trigger and produce the required covariance spike in Eq. (2). We therefore introduce two distinct keys: the aforementioned νbd ∈ R m defined in the space of ℓbd, and another key νin ∈ R h×w×c in the input space. The former equals a sparse version of the normal vector to the logistic regression decision boundary, while νin is obtained through an optimisation procedure similar to the Concept Backpropagation method introduced by Hammersborg and Strümke [14]. Following Goldwasser et al. [10 , 11], the input is triggered via a weighted key, i.e., xˆ ˆ = x + λνin. Specifically, νin is optimised to be the input perturbation needed for a triggered representation in the activation space of layer ℓbd to maximally align with the planted covariance spike. Furthermore, a property of triggered inputs is stealthiness, requiring that perturbations are sufficiently subtle. The optimisation objective includes L2 regularisation with a corresponding tunable weight λL2, while also constraining pixel values to a specified range. Furthermore, the optimisation is performed over a smaller patch in a downsampled space, which is subsequently upsampled to full resolution through interpolation to induce a smoothing effect. The full optimisation algorithm is detailed in App. D.

Theoretical justification and guarantees We use the term "cryptographic undetectability" to denote how we formally measure the difficulty of detecting the proposed weight modification under the considered threat model. While our construction is conceptually motivated by that of Goldwasser et al. [10 , 11], their formal cryptographic guarantees of provable white-box undetectability do not trivially extend to our implementation. Specifically, Goldwasser et al. [10 , 11] assume that the base weights to be exploited follow N (0, Id) with the backdoor planted by sampling from a spiked

covariance distribution N (0, Id + θνν T ) using a strictly random key ν. Under these assumptions, undetectability is reduced to the hardness of a classical single-sample hypothesis test, i.e., determining the distribution from which the weights are sampled; either from N (0, Id) (null hypothesis H0) or from N (0, Id + θνν T ) (alternative hypothesis H1). Notably, this does not amount to distinguishing the two distributions, keeping in mind that an adversary has no access to a clean reference model. In essence, Goldwasser et al. [10 , 11] prove through the hardness of sparse PCA that it is not possible to reject either hypothesis [2, 3].

In real-world neural networks, weight distributions are shaped by the optimisation landscape of the training objective to follow an unknown distribution µ(0, S), with our backdoor planted by sampling from µ(0, S ′ + θνbdν
b T ν
bd ), where S ′ denotes the combination of the learned weight covariance and the diagonal component σ 2 Im Im from the spiked covariance in Eq. (2). Furthermore, a strong adversary with the objective of detecting the backdoor is assumed to have knowledge of the scaling factor θ and can estimate νbd, which is not random but a sparse version of the normal vector to a linear decision boundary of the clean model's activation space. 1 Consequently, the formal proofs used by Goldwasser et al. [10 , 11], cannot be directly applied to provide the same theoretical guarantees for our construction. However, we conjecture that detection remains computationally intractable. We formulate the adverary's objective as a similar hypothesis test for where H0 defines that W ˆ (ℓbd) is sampled from µ(0, S) (the clean model distribution) and H 1 assumes that the weights are sampled from µ(0, S ′ + θνbdν
b T ν
bd ) (the backdoored model distribution). Given a single sample of weights W ˆ (ℓbd) and knowledge of (θ, νbd), we conjecture the existence of hyperparameter regimes for which no practical test can falsify the null hypothesis with a useful success probability. Furthermore, to the best of our knowledge, no other simpler statistical test is sufficient to prove the existence of the backdoor. 2

This detection task is practically hard because the dimensionality of the weight space in modern neural networks provides a massive hiding surface for a single spike. Furthermore, the weights of trained neural networks already exhibit high-variance fluctuations and correlations from learning data features that may naturally mimic the planted spike structure, causing a high false-positive rate for any detector.

The Marchenko–Pastur law (see App. E for details) can guide the choice of the backdoor layer's dimensionality: It characterises the eigenvalues of large sample covariance matrices of random values in R m×d , showing that pure noise causes the observed eigenvalues to spread over an interval determined by the ratio m d even when the true covariance matrix is the identity. In neural network weight matrices, while m ≫ d maximises the interval width – suppressing the visibility of a spike – the matrix becomes rank-deficient. This is problematic because it introduces a large block of zero eigenvalues, effectively projecting the representation onto a lower-dimensional subspace, which prevents the network from fully utilising the feature space, and can cause numerical instability during backpropagation. We suggest m ≈ d to be a practical design choice, balancing hiding planted structure without sacrificing the network's functionality. Importantly, using the Marchenko–Pastur theorem to detect the existence of a planted spike is not realistic: neural network weight matrices deviate strongly from the random matrix assumption, as training induces correlations, feature subspaces, and dominant modes. An eigenvalue exceeding the theoretical Marchenko-Pastur bound could equally well reflect a learned feature rather than a planted spike. Further, any detection method or statistical analysis that requires comparison or access to a clean model would conflict with the underlying MLaaS assumption and is therefore outside the current scope.

## 4 Experiment design and evaluations

## 4.1 Datasets and experimental design

Our method is evaluated on ResNet18 [16] and Vision Transformer (ViT) [8] for multi-class classification using publicly available datasets CIFAR-10 [21] (10 distinct object categories), and the following from MedMNIST [32]: BloodMNIST (8 classes of blood cell types), DermaMNIST (7 classes of pigmented skin lesion types), and PathMNIST (9 classes of tissue types). A ReLU-activated linear layer W( ℓ bd ) ∈ Rm×d
is inserted before the output layer, with d = m = 512 (ResNet18) or d = m = 768 (ViT). Using other activation functions should not introduce further complications beyond hyperparameter tuning. The models are initialised with ImageNet pre-trained weights, and fine-tuned separately on each dataset for five epochs using the Adam optimiser [20] with a learning rate of 1 × 10 − 4 and cross-entropy loss.

1 It is worth noting that CAVs are known to be unstable across training runs and sensitive to the choice of probe dataset. Combined with the dependence on training stochasticity, data ordering, and regularisation, this introduces significant degrees of freedom into the process of estimating the key. Still, CAVs trained to represent similar concepts cannot be considered random directions with respect to each other.

2 We assume that the adversary is unable to train clean models without conflicting with the MLaaS setting – either because they lack the computational power or expertise, or because they do not have access to the full set of training data.

Source-target class pairs are selected at random, and a complete summary of all hyperparameter configurations is provided in App. F. The input trigger optimisation procedure, which yields the key νin, is constrained to at most 500 samples from the source class. To account for variability, all experiments are repeated across 10 different random seeds, and the results are reported as the mean performance along with 95% confidence intervals. The computational resources used for experiments are stated in App. G.

## 4.2 Evaluation metrics and backdoor defences

A successful backdoored model must satisfy two main requirements: ensure minimal impact on clean performance, and reliable misclassification of triggered inputs to a predefined target class. These are quantified by the metrics attack success rate (ASR) – the fraction of triggered inputs misclassified into the target class – and clean data accuracy (CDA) – the proportion of unmodified test samples correctly classified. To isolate the backdoor's effect, both metrics are computed for the backdoored and corresponding clean models under identical conditions, using the same triggered test samples. Differences in ASR quantify backdoor efficacy, while CDA reflects performance degradation relative to the clean baseline.

Robustness is assessed against a range of post-training defences following Hong et al. [17]: pruning, fine-tuning, fine-pruning [23], parameter clipping, parameter noise injection, and the detection methods Neural Cleanse [31] and SmoothInv [30].

Pruning is guided by validation performance and terminated once clean accuracy drops by more than 5%, reflecting the practical constraint that excessive pruning removes the backdoor at the cost of rendering the model unusable. Finetuning attempts to overwrite backdoor perturbations by continued training and trivially succeeds given sufficient epochs, since this converges to retraining [17]. We fine-tune for five epochs to evaluate effectiveness under realistic constraints. Fine-pruning combines pruning followed by fine-tuning. Resilience to parameter-level perturbations is also evaluated via Gaussian noise injection N (0, σ 2 p ), with σ p varied logarithmically from 10 − 3 to 5. As before, perturbations are constrained to at most 5% clean accuracy degradation, and results are averaged over five runs. Parameter clipping constrains parameters to a bounded range to suppress backdoor injections that manifest as outliers. We sweep the threshold β ∈ [0 . 1 , 1 . 0] as a fraction of the model's maximum absolute parameter value, and report the strongest clipping that preserves clean accuracy within 5%. Neural Cleanse is run with its original default configuration; detection is counted as successful if the backdoored label is identified as the target class in at least half of the seeds. SmoothInv is likewise evaluated using its default configuration, see App. K for details.

## 5 Results and analysis

ASR and CDA results are reported in Tab. 1. Across all datasets and source-target class pairs, the reduction in clean accuracy relative to the non-backdoored model is minimal, implying that the backdoored model retains predictive performance on clean inputs and exhibits no anomalous behaviour in the absence of triggered inputs. Concurrently, it achieves consistently high ASR, i.e., the backdoor reliably redirects inputs from the source to the target class. In all cases, triggered accuracy exceeds that of the clean model under identical conditions, confirming the injected mechanism is effective and consistent with theory. Triggered inputs also induce targeted misclassification in the clean model, only slightly less reliably, demonstrating the expected vulnerability to adversarial examples associated with only probing access without modification of model parameters. Results for the evaluated defences are presented in Tab. 2 and Fig. 2, with further results in App. I, J and K, including comparisons with clean inputs. The backdoor retains a high attack success rate across all evaluated defence and detection strategies, suggesting that the persistence guarantees of Goldwasser et al. [10 , 11] extend at least approximately beyond their idealised setting to ours. This robustness is expected, as planting the backdoor along a direction critical to the model should make it substantially harder to remove.

The decoupling of the covariance spike from the input trigger provides additional flexibility. Importantly, any undetectability properties apply to the planted covariance spike, not the input trigger resulting from the subsequent optimisation. Trigger visibility is governed by hyperparameters, e.g. spike strength θ, regularisation weight λL2, and the allowed pixel range in Alg. 1 (App. D) – and can be traded against ASR or tuned to prioritise robustness against defences and detection. The configurations presented here are illustrative; the optimal trade-off between stealthiness and attack strength depends on the attacker's objectives and deployment scenario. Appendix L illustrates the input trigger and quantifies its visual imperceptibility via the Maximum Mean Discrepancy score [12]. Further, App. M provides sensitivity analyses of both the relationship between spike strength θ, ASR and clean accuracy, and of the stealthiness, as measured through λL2, in relation to ASR.

Table 1: Performance comparison between clean and backdoored ResNet18 and ViT models across four datasets. Overall denotes performance on clean inputs from all classes, while triggered indicates the ASR on triggered sourcetarget class pairs. Uncertainty is reported as lower and upper bounds of the 95% confidence interval, with all values rounded to two decimal places. All hyperparameter configurations are provided in App. F, with full class names corresponding to the abbreviations listed in App. H.

|          | Triggered Overall                                              | Triggered Overall                                                |
|----------|----------------------------------------------------------------|------------------------------------------------------------------|
|          |                                                                | Model Dataset Source → Target Clean Backdoor Clean Backdoor      |
| ResNet18 |                                                                | BloodMNIST Baso → Eos 0.19 ± 0.02 0.96 ± 0.01 0.98 0.98 ± 0.00   |
|          |                                                                | BloodMNIST EryBl → Baso 0.49 ± 0.06 0.90 ± 0.02 0.98 0.97 ± 0.00 |
|          | CIFAR-10 Deer → Horse 0.64 ± 0.04 0.90 ± 0.01 0.94 0.89 ± 0.00 |                                                                  |
|          |                                                                | CIFAR-10 Ship → Truck 0.33 ± 0.02 0.93 ± 0.01 0.94 0.91 ± 0.00   |
|          |                                                                | DermaMNIST NV → Vasc 0.89 ± 0.01 0.95 ± 0.01 0.77 0.71 ± 0.01    |
|          | DermaMNIST Mel → DF 0.57 ± 0.02 0.98 ± 0.00 0.77 0.73 ± 0.00   |                                                                  |
|          |                                                                | PathMNIST BG → Deb 0.53 ± 0.30 0.85 ± 0.10 0.93 0.84 ± 0.02      |
|          |                                                                | PathMNIST LymP → Deb 0.27 ± 0.03 0.88 ± 0.03 0.93 0.87 ± 0.00    |
| ViT      |                                                                | BloodMNIST Baso → Eos 0.00 ± 0.00 0.89 ± 0.01 0.99 0.99 ± 0.00   |
|          |                                                                | BloodMNIST LymB → Mono 0.25 ± 0.05 0.98 ± 0.01 0.99 0.99 ± 0.00  |
|          |                                                                | CIFAR-10 Auto → Truck 0.91 ± 0.06 0.95 ± 0.04 0.95 0.94 ± 0.00   |
|          |                                                                | CIFAR-10 Truck → Auto 0.80 ± 0.03 0.90 ± 0.06 0.95 0.94 ± 0.00   |
|          |                                                                | DermaMNIST BCC → Mel 0.88 ± 0.04 0.99 ± 0.00 0.75 0.76 ± 0.01    |
|          | DermaMNIST Mel → DF 0.52 ± 0.03 0.97 ± 0.01 0.75 0.76 ± 0.00   |                                                                  |
|          | PathMNIST Adip → BG 0.96 ± 0.01 1.00 0.94 0.94 ± 0.00          |                                                                  |
|          | PathMNIST LymP → Deb 0.28 ± 0.01 0.87 ± 0.01 0.94 0.91 ± 0.00  |                                                                  |

Table 2: ASR on triggered source-target class pairs after defence methods pruning, parameter clipping and parameter noise injection for backdoored ResNet18 and ViT across four datasets. Uncertainty is reported as lower and upper bounds of the 95% confidence interval, with all values rounded to two decimal places. For Neural Cleanse (NC), we indicate whether the backdoor was detected (✓) or not (✗). All hyperparameter configurations are provided in App. F, with full class names corresponding to the abbreviations listed in App. H.

|          |                                                             | Model Dataset Source → Target Pruning Parameter clipping Parameter noise NC   |    |
|----------|-------------------------------------------------------------|-------------------------------------------------------------------------------|----|
| ResNet18 | BloodMNIST Baso → Eos 1.00 ± 0.00 0.73 ± 0.05 0.89 ± 0.05   |                                                                               | ✗  |
|          | BloodMNIST EryBl → Baso 0.66 ± 0.08 0.54 ± 0.06 0.55 ± 0.11 |                                                                               | ✗  |
|          | CIFAR-10 Deer → Horse 0.90 ± 0.01 0.89 ± 0.01 0.86 ± 0.03   |                                                                               | ✗  |
|          | CIFAR-10 Ship → Truck 0.93 ± 0.02 0.92 ± 0.02 0.85 ± 0.02   |                                                                               | ✗  |
|          |                                                             | DermaMNIST NV → Vasc 0.94 ± 0.02 0.94 ± 0.02 0.94 ± 0.02                      | ✗  |
|          |                                                             | DermaMNIST Mel → DF 0.94 ± 0.01 0.97 ± 0.01 0.96 ± 0.01                       | ✗  |
|          |                                                             | PathMNIST BG → Deb 0.74 ± 0.12 0.75 ± 0.11 0.79 ± 0.12                        | ✗  |
|          | PathMNIST LymP → Deb 0.99 ± 0.01 0.35 ± 0.04 0.68 ± 0.08    |                                                                               | ✗  |
| ViT      | BloodMNIST Baso → Eos 0.75 ± 0.02 0.92 ± 0.00 0.93 ± 0.02   |                                                                               | ✗  |
|          | BloodMNIST LymB → Mono 0.44 ± 0.12 0.78 ± 0.07 0.71 ± 0.08  |                                                                               | ✗  |
|          | CIFAR-10 Auto → Truck 0.95 ± 0.06 0.95 ± 0.05 0.93 ± 0.03   |                                                                               | ✗  |
|          | CIFAR-10 Truck → Auto 0.89 ± 0.08 0.83 ± 0.08 0.84 ± 0.07   |                                                                               | ✗  |
|          | DermaMNIST BCC → Mel 0.99 ± 0.00 0.81 ± 0.14 0.74 ± 0.11    |                                                                               | ✗  |
|          |                                                             | DermaMNIST Mel → DF 0.99 ± 0.00 0.84 ± 0.07 0.88 ± 0.03                       | ✗  |
|          | PathMNIST Adip → BG 1.00 1.00 ± 0.00 1.00                   |                                                                               | ✗  |
|          | PathMNIST LymP → Deb 0.96 ± 0.00 0.87 ± 0.01 0.79 ± 0.03    |                                                                               | ✗  |

Figure 2: Accuracy over five epochs of (blue) fine-tuning and (green) fine-pruning defences for backdoored ResNet18 on BloodMNIST with source class basophil and target class eosinophil. Results are reported for both clean inputs from all classes and triggered inputs from the source class. Shaded uncertainty bands represent the bounds of the 95% confidence interval.

<!-- image -->

## 6 Discussion and conclusion

This work demonstrates an extension of the method introduced by Goldwasser et al. [10 , 11], providing a formal guarantee of cryptographic undetectability for backdoors planted via spiked covariance, from simplified neural networks to modern transformer and convolutional architectures. Given the generality of our approach and the universal presence of CAVs in neural representations, no theoretical restrictions prevent extension to other architectures. As part of our analysis, we provide theoretical justification for the impracticability of distinguishing a backdoored model from a clean version, given the computational hardness of the hypothesis test discussed in Sec. 3.2. Future work should aim to derive a formal proof to establish cryptographic undetectability. Such a proof would likely require an analytical characterisation of trained neural network weight distributions, which remains an open problem. The practical utility of such a theoretical result is arguably limited, given that parameter-space defences are ineffective against our backdoor in experiments. Indeed, prior work typically establishes undetectability through empirical evaluation against such defences alone; our analysis meets this standard and additionally provides a formal proof in the idealised setting.

A key aspect of our approach is that any undetectability is baked into the weights themselves; the input trigger is secondary, derived via optimisation once the backdoor is planted. This decoupling allows users to tune visual imperceptibility according to their specific requirements without compromising the undetectability of the backdooring mechanism itself. Depending on the data domain, further refinement of the optimisation process can yield more sophisticated, human-imperceptible triggers.

Limitations Our work lacks a proof of full white-box undetectability. While we provide theoretical justification and empirical evidence, we cannot conclude with theoretical guarantees. Moreover, the difficulty of the proposed hypothesis test depends on the hyperparameter value θ. At present, we lack a well-defined range for selecting this parameter, beyond the general intuition that θ should be small to render the test harder to falsify. The same challenge applies to the dimensions d and m. Additionally, although the experiments are limited to the domain of computer vision, the approach is extendable to other domains such as natural language processing.

## References

- [1] Bilal Hussain Abbasi, Yanjun Zhang, Leo Zhang, and Shang Gao. Backdoor attacks and defenses in computer vision domain: A survey. arXiv preprint arXiv:2509.07504, 2025.
- [2] Quentin Berthet and Philippe Rigollet. Complexity theoretic lower bounds for sparse principal component detection. In Shai Shalev-Shwartz and Ingo Steinwart, editors, COLT 2013 - The 26th Annual Conference on

| Learning Theory, June 12-14, 2013, Princeton University, NJ, USA, JMLR Workshop and Conference Proceedings, pages 1046–1066. JMLR.org, 2013. URL http://proceedings.mlr.press/v30/Berthet13.html .                                                                                                                                                                                                                                                                                                                               |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [3] Quentin Berthet and Philippe Rigollet. Computational lower bounds for sparse pca.  arXiv preprint arXiv:1304.0828, 2013.                                                                                                                                                                                                                                                                                                                                                                                                     |
| [4] Matthew S. Brennan and Guy Bresler. Optimal average-case reductions to sparse PCA: from weak assumptions to strong hardness. In Alina Beygelzimer and Daniel Hsu, editors, Conference on Learning Theory, COLT 2019, 25-28 June 2019, Phoenix, AZ, USA, Proceedings of Machine Learning Research, pages 469–470. PMLR, 2019. URL http://proceedings.mlr.press/v99/brennan19b.html .                                                                                                                                          |
| [5] Bochuan Cao, Jinyuan Jia, Chuxuan Hu, Wenbo Guo, Zhen Xiang, Jinghui Chen, Bo Li, and Dawn Song. Data free backdoor attacks. Advances in Neural Information Processing Systems, 37:23881–23911, 2024.                                                                                                                                                                                                                                                                                                                        |
| [6] Sarthak Choudhary, Atharv Singh Patlan, Nils Palumbo, Ashish Hooda, Kassem Fawaz, and Somesh Jha. Undetectable backdoors in model parameters: Hiding sparse secrets in high dimensions.  arXiv preprint arXiv:2605.04209, 2026.                                                                                                                                                                                                                                                                                              |
| [7] Antonio Emanuele Cinà, Kathrin Grosse, Ambra Demontis, Sebastiano Vascon, Werner Zellinger, Bernhard A Moser, Alina Oprea, Battista Biggio, Marcello Pelillo, and Fabio Roli. Wild patterns reloaded: A survey of machine learning security against training data poisoning. ACM Computing Surveys, 55(13s):1–39, 2023.                                                                                                                                                                                                      |
| [8] Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, et al. An image is worth 16x16 words: Transformers for image recognition at scale. arXiv preprint arXiv:2010.11929, 2020.                                                                                                                                                                                                                      |
| [9] Andis Draguns, Andrew Gritsevskiy, Sumeet Ramesh Motwani, and Christian Schroeder de Witt. Unelicitable backdoors via cryptographic transformer circuits. In A. Globerson, L. Mackey, D. Belgrave, A. Fan, U. Paquet, J. Tomczak, and C. Zhang, editors, Advances in Neural Information Processing Systems, volume 37, pages 53684– 53709. Curran Associates, Inc., 2024. doi: 10.52202/079017-1700. URL https://proceedings.neurips. cc/paper_files/paper/2024/file/6087a60306544be7ba0d0cf34aa93c8f-Paper-Conference.pdf . |
| [10] Shafi Goldwasser, Michael P. Kim, Vinod Vaikuntanathan, and Or Zamir. Planting undetectable backdoors in machine learning models : [extended abstract]. In 2022 IEEE 63rd Annual Symposium on Foundations of Computer Science (FOCS), pages 931–942, 2022. doi: 10.1109/FOCS54457.2022.00092.                                                                                                                                                                                                                               |
| [11] Shafi Goldwasser, Michael P. Kim, Vinod Vaikuntanathan, and Or Zamir. Planting undetectable backdoors in machine learning models, 2024. URL https://arxiv.org/abs/2204.06974 .                                                                                                                                                                                                                                                                                                                                              |
| [12] Arthur Gretton, Karsten M. Borgwardt, Malte J. Rasch, Bernhard Schölkopf, and Alexander Smola. A kernel two-sample test. Journal of Machine Learning Research, 13(25):723–773, 2012. URL http://jmlr.org/ papers/v13/gretton12a.html .                                                                                                                                                                                                                                                                                      |
| [13] Ioannis Grigoriadis, Eleni Vrochidou, Iliana Tsiatsiou, and George A. Papakostas. Machine learning as a service (mlaas)—an enterprise perspective. In Mukesh Saraswat, Chandreyee Chowdhury, Chintan Kumar Mandal, and Amir H. Gandomi, editors, Proceedings of International Conference on Data Science and Applications, pages 261–273, Singapore, 2023. Springer Nature Singapore. ISBN 978-981-19-6634-7.                                                                                                               |
| [14] Patrik Hammersborg and Inga Strümke. Concept backpropagation: An explainable ai approach for visualising learned concepts in neural network models. arXiv preprint arXiv:2307.12601, 2023.                                                                                                                                                                                                                                                                                                                                  |
| [15] Muhammad Abdullah Hanif, Nandish Chattopadhyay, Bassem Ouni, and Muhammad Shafique. Survey on backdoor attacks on deep learning: Current trends, categorization, applications, research challenges, and future prospects. IEEE Access, 2025.                                                                                                                                                                                                                                                                                |
| [16] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 770–778, 2016.                                                                                                                                                                                                                                                                                                                 |
| [17] Sanghyun Hong, Nicholas Carlini, and Alexey Kurakin. Handcrafted backdoors in deep neural networks. Advances in Neural Information Processing Systems, 35:8068–8080, 2022.                                                                                                                                                                                                                                                                                                                                                  |
| [18] Alkis Kalavasis, Amin Karbasi, Argyris Oikonomou, Katerina Sotiraki, Grigoris Velegkas, and Manolis Zam petakis. Injecting undetectable backdoors in obfuscated neural networks and language models. Advances in Neural Information Processing Systems, 37:21537–21571, 2024.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| [19] Been Kim, Martin Wattenberg, Justin Gilmer, Carrie Cai, James Wexler, Fernanda Viegas, et al. Interpretability beyond feature attribution: Quantitative testing with concept activation vectors (tcav). In International conference on machine learning, pages 2668–2677. PMLR, 2018.                                                                                                                                                                                                                                       |
| [20] Diederik P Kingma and Jimmy Ba. Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980 , 2014.                                                                                                                                                                                                                                                                                                                                                                                                          |

| [21] Alex Krizhevsky, Geoffrey Hinton, et al. Learning multiple layers of features from tiny images. 2009.                                                                                                                                                            |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [22] Max Lamparth and Anka Reuel. Analyzing and editing inner mechanisms of backdoored language models. In Proceedings of the 2024 ACM Conference on Fairness, Accountability, and Transparency, pages 2362–2373, 2024.                                               |
| [23] Kang Liu, Brendan Dolan-Gavitt, and Siddharth Garg. Fine-pruning: Defending against backdooring attacks on deep neural networks. In International symposium on research in attacks, intrusions, and defenses, pages 273–294. Springer, 2018.                     |
| [24] Charles H Martin and Michael W Mahoney. Implicit self-regularization in deep neural networks: Evidence from random matrix theory and implications for learning. Journal of Machine Learning Research, 22(165):1–73, 2021.                                        |
| [25] Ali Rahimi and Benjamin Recht. Random features for large-scale kernel machines. Advances in neural information processing systems, 20, 2007.                                                                                                                     |
| [26] Mauro Ribeiro, Katarina Grolinger, and Miriam A.M. Capretz. Mlaas: Machine learning as a service. In 2015 IEEE 14th International Conference on Machine Learning and Applications (ICMLA), pages 896–902, 2015. doi: 10.1109/ICMLA.2015.152.                     |
| [27] Levent Sagun, Leon Bottou, and Yann LeCun. Eigenvalues of the hessian in deep learning: Singularity and beyond. arXiv preprint arXiv:1611.07476, 2016.                                                                                                           |
| [28] Levent Sagun, Utku Evci, V Ugur Guney, Yann Dauphin, and Leon Bottou. Empirical analysis of the hessian of over-parametrized neural networks. arXiv preprint arXiv:1706.04454, 2017.                                                                             |
| [29] Levent Sagun, Utku Evci, V Ugur Guney, Yann Dauphin, and Leon Bottou. Empirical analysis of the hessian of over-parametrized neural networks. In ICLR 2018 Workshop, 2018. URL https://iclr.cc/virtual/2018/ workshop/563 .                                      |
| [30] Mingjie Sun and Zico Kolter. Single image backdoor inversion via robust smoothed classifiers. In 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pages 8113–8122. IEEE, 2023.                                                        |
| [31] Bolun Wang, Yuanshun Yao, Shawn Shan, Huiying Li, Bimal Viswanath, Haitao Zheng, and Ben Y Zhao. Neural cleanse: Identifying and mitigating backdoor attacks in neural networks. In 2019 IEEE symposium on security and privacy (SP), pages 707–723. IEEE, 2019. |
| [32] Jiancheng Yang, Rui Shi, Donglai Wei, Zequan Liu, Lin Zhao, Bilian Ke, Hanspeter Pfister, and Bingbing Ni. Medmnist v2-a large-scale lightweight benchmark for 2d and 3d biomedical image classification. Scientific data , 10(1):41, 2023.                      |

## A Visualisation of spiked covariance

Figure 3 illustrates the difference between clean and backdoored distributions, highlighting the increased variance introduced by the spiked covariance. The clean distribution follows a standard multivariate Gaussian N (0, Id), while the backdoored distribution N (0, Id + θνν T ) incorporates a low-rank covariance perturbation, creating a spike along a secret direction ν ∈ R d . While statistically indistinguishable under certain conditions, the variance is visibly higher in the latter for a high value θ. Refer to Sec. 3.1 for further details.

Figure 3: (a) The clean distribution follows a standard multivariate Gaussian, which is modified with a spiked covariance to obtain (b) the backdoored distribution. Both are shown as 2D contour lines using a shared colour scale.

<!-- image -->

<!-- image -->

## B Spiked covariance distribution

The following shows that the weight transformation from W( ℓ bd )
to Wˆ ˆ (ℓbd) , both defined in Sec.3.2, would be statistically identical to sampling new weights from a distribution gi ∼ N (0, σ 2 Im Im + θνbdν
b T ν
bd ), under the assumption that W( ℓ bd ) was Gaussian.

Assume each column of the weight matrix W( ℓ bd )
, denoted w ∈ R
m, are sampled from a distribution w ∼ N (0, σ 2 Im Im ) , which gives covariance Cov(w) = E[ww T ] = σ 2 Im Im. 3 The covariance of these weights scaled by the standard deviation σ is,

<!-- formula-not-decoded -->

The identity covariance makes the scaled weights mathematically indistinguishable from a sample of the standard Gaussian, as its mean is assumed to be zero.

ˆ

The covariance of the backdoored weights W (ℓbd) when applying the Cholesky factor L as in Sec. 3.2 is, when using the result from Eq. (7),

<!-- formula-not-decoded -->

where Σ is defined in Eq. (2).

As discussed in Sec. 3.2, the weights do not strictly follow a Gaussian distribution, but the above argument motivates our approach.

3 This assumes the weight vector w is i.i.d (independent and identically distributed) with zero mean, a shared variance σ 2 , and zero pairwise covariance (E[wi, wj ] = 0 , ∀i ̸= j ).

4 Covariance property for a random vector x and deterministic matrix A: Cov(Ax) = ACov(x)A T .

## C Empirical structure of the weight covariance

In conflict with our simplified assumption, the covariance of the model weights is not diagonal; model training induces correlations and the weights are tied together via the loss landscape. Still, when viewed through the spectrum of the Hessian (the second derivatives of the loss with respect to the weights), the bulk behaves as if the covariance were essentially isotropic and degenerate, with a small number of outliers carrying the structured signal. This was shown empirically by Sagun et al. [28 , 29], who decomposed the Hessian via the Generalised Gauss-Newton form into a covariance-of-gradients term plus a residual.

Concretely, both at initialisation and at the end of training, almost all Hessian eigenvalues sit in a narrow bulk concentrated near zero, with a handful of large positive outliers detached from it [27 , 28 , 29]. The two parts have different origins: the bulk is governed by the architecture, while the outliers are governed by the data. Sagun et al. [28 , 29] show empirically that for a k-class classification problem, the number of outliers above the bulk matches k , which is exactly what one would expect if the dominant non-trivial directions come from the rank-k structure of the gradient-of-outputs covariance in their decomposition.

Increasing layer width, on the other hand, does not create new outlier directions; it only inflates the bulk near zero [27 , 28 , 29]. Briefly put: most directions in overparameterised networks correspond to redundant zero modes, alongside whatever sparse structured signal the data contributes. Importantly for the present context, this low effective rank is visible directly in the weight matrices, not only the Hessian. The parallel observation was made by Martin and Mahoney [24], who find that trained weight matrices develop strongly non-random, often heavy-tailed spectra, with structure aligned to the data. They find that, over the course of training, the information in the weight matrices increasingly concentrates in a sparse spike, and that there is likely no simple low rank approximation for the weight matrices.

Despite the important off-diagonal directions, the empirical results in Sec. 5 demonstrate that the model's learned behaviour is preserved when using the spiked covariance in Eq. 2 to replace weights in the backdoor layer.

## D Optimisation algorithm for input space trigger

Algorithm 1 outlines the optimisation procedure for obtaining the input trigger using the backdoored model denoted ˆ f. In particular, we define z (ℓbd) source ∈ R m as the activations of inputs from the source class in layer ℓbd, and zˆ ˆ (ℓbd) source as activations from the corresponding triggered inputs. The main optimisation objective is to align the latter with the spike direction νb νbd ∈ R m .

Stealthiness requires perturbations to remain sufficiently subtle such that a triggered input xˆ ˆ is difficult to distinguish from its clean counterpart x. Ideally, this similarity should hold for both human observers and automated anomaly detection systems. The optimisation accounts for stealthiness by including L2 regularisation to its objective, constrain pixel values, and enforce sparsity via a threshold τ . The optimisation is carried out on a smaller patch R h s ×w s ×c , which is subsequently upsampled to induce a smoothing (blurring) effect.

## Algorithm 1 Optimise trigger perturbation for input space

```
1: Input: x , νbd , ˆ f, steps, lr, scale, λL2 , ϵ , τ 2: Output: νin 3: (b, c, h, w) ← shape(x) 4: h s ← ⌊h/scale⌋ 5: w s ← ⌊w/scale⌋ 6: δ ← 0 1×c×h s ×w s 7: δ.requires_grad ← True 8: Initialize optimizer ← Adam(δ, lr) 9: νbd ← normalize(νbd) 10: dataloader ← get_dataloader(x) 11: for step = 1 to steps do 12: optimizer.zero_grad() 13: for each batch x batch in dataloader do 14: νin ← interpolate(δ,(h, w)) 15: ν
i ′ ν
in ← clamp(νin , − ϵ, ϵ ) 16: y ← ˆ f(xbatch + ν
i ′ ν
in ) 17: h ← activation 18: alignment ← − 1 |xbatch| P(h · νbd) 19: L2 ← λ L2 |xbatch| P(ν
i ′ ν
in ) 2 20: loss ← alignment + L2 21: loss.backward() 22: activation ← ∅ 23: end for 24: optimizer.step() 25: δ ← sign(δ) · max(|δ| − τ, 0) 26: end for 27: νin ← interpolate(δ,(h, w)) 28: return squeeze(νin)
```

## E The Marchenko-Pastur theorem

The Marchenko-Pastur theorem is a fundamental result in random matrix theory that describes the eigenvalues of large sample covariance matrices. Assume a data matrix X ∈ R
p ×n , where p denotes the number of variables and n the number of samples, in which entries are independent identically distributed random variables with mean 0 and variance σ 2 . The sample covariance matrix is expressed as

<!-- formula-not-decoded -->

When the population covariance is σ 2 I, the eigenvalues of S concentrate on the interval [σ 2 (1 −
√γ) 2 , σ 2 (1 + √γ) 2 ] when p, n → ∞ with p n → γ ∈ (0 , +∞). This shows that even in the absence of structure, the eigenvalues spread over a non-trivial interval purely due to noise. Furthermore, this establishes a detection threshold: spikes or dominant principal directions are only distinguishable from random noise if their associated eigenvalues exceed the upper bound.

## F Hyperparameter configurations

This section summarises the hyperparameter configurations used in the experiments reported in Sec. 5. All experiments – across both architectures and datasets – share the common settings listed in Tab. 3. A fixed scaling factor λ = 0 . 5 is used for the input trigger in ResNet18 experiments, whereas a value of λ = 2 is used for ViT. The only hyperparameter varying across source-target class pairs is the L2 regularisation coefficient λL2 in the optimisation procedure (Alg. 1). These values are reported in Tab. 4.

|                                | Hyperparameter Value   |        |
|--------------------------------|------------------------|--------|
| Optimisiation of input trigger | steps 200 scale 4      | 30/255 |
| Optimisiation of input trigger | lr 0.01                |        |
| Optimisiation of input trigger | ϵ                      |        |
| Optimisiation of input trigger | τ                      | 0.001  |
| Sparsity                       | α                      | 0.1    |
| Strength of spiked covariance  | θ                      | 0.1    |

Table 4: The hyperparameter value of the L2 regularisation coefficient λL2 in Alg. 1 for all source-target class pairs across datasets. The full class names corresponding to the abbreviations are listed in App. H.

|          | Model Dataset Source → Target Value λL2   |
|----------|-------------------------------------------|
| ResNet18 | BloodMNIST Baso → Eos 15                  |
|          | BloodMNIST EryBl → Baso 6.5               |
|          | CIFAR-10 Deer → Horse 1.5                 |
|          | CIFAR-10 Ship → Truck 3                   |
|          | DermaMNIST NV → Vasc 10                   |
|          | DermaMNIST Mel → DF 2.5                   |
|          | PathMNIST BG → Deb 8                      |
|          | PathMNIST LymP → Deb 4                    |
| ViT      | BloodMNIST Baso → Eos 16.5                |
|          | BloodMNIST LymB → Mono 5                  |
|          | CIFAR-10 Auto → Truck 1                   |
|          | CIFAR-10 Truck → Auto 1                   |
|          | DermaMNIST BCC → Mel 5.5                  |
|          | DermaMNIST Mel → DF 8                     |
|          | PathMNIST Adip → BG 1                     |
|          | PathMNIST LymP → Deb 1                    |

## G Experiments compute resources

All computations were performed on an HPC cluster using NVIDIA V100 or A100 GPUs. Comparable hardware is not strictly required; rather, sufficient GPU memory to accommodate the model size and data is the primary requirement.

## H Class label abbreviations

Table 5 provides abbreviations of class names in all evaluated datasets BloodMNIST, CIFAR-10, DermaMNIST and PathMNIST.

Table 5: Class label abbreviations

| Full name Abbreviation                                |
|-------------------------------------------------------|
| Basophil Baso                                         |
| Eosinophil Eos                                        |
| Erythroblast EryBl                                    |
| Immature granulocytes ImmGran                         |
| Lymphocyte LymB                                       |
| Monocyte Mono                                         |
| Neutrophil Neut                                       |
| Platelet Plt                                          |
| Airplane Air                                          |
| Automobile Auto                                       |
| Bird Bird                                             |
| Cat Cat                                               |
| Deer Deer                                             |
| Dog Dog                                               |
| Frog Frog                                             |
| Horse Horse                                           |
| Ship Ship                                             |
| Truck Truck                                           |
| Actinic keratoses and intraepithelial carcinoma AKIEC |
| Basal cell carcinoma BCC                              |
| Benign keratosis-like lesions BKL                     |
| Dermatofibroma DF                                     |
| Melanoma Mel                                          |
| Melanocytic nevi NV                                   |
| Vascular lesions Vasc                                 |
| Adipose Adip                                          |
| Background BG                                         |
| Cancer-associated stroma CAS                          |
| Colorectal adenocarcinoma epithelium CAE              |
| Debris Deb                                            |
| Lymphocytes LymP                                      |
| Mucus Muc                                             |
| Normal colon mucosa NCM                               |
| Smooth muscle SM                                      |

## I Performance comparison of defences on clean vs. triggered inputs

Table 6 compares the performance of defence methods pruning, parameter clipping and parameter noise injection on both clean and triggered inputs. Notably, the triggered results match those in Tab. 2, while this table additionally reports performance on clean inputs for comparison.

Table 6: Performance comparison of defence methods pruning, parameter clipping and parameter noise injection on clean and triggered inputs for ResNet18 and ViT across four datasets. Clean denotes classification accuracy on unmodified inputs from all classes, while triggered indicates the ASR on triggered source-target class pairs. Uncertainty is reported as lower and upper bounds of the 95% confidence interval, with all values rounded to two decimal places. All hyperparameter configurations are provided in App. F, with full class names corresponding to the abbreviations listed in App. H.

|          |                                                                                                 | Pruning Parameter clipping Parameter noise                                                   | Pruning Parameter clipping Parameter noise                                                    |
|----------|-------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
|          | Model Dataset Source → Target Clean Triggered Clean Triggered Clean Triggered                   |                                                                                              |                                                                                               |
| ResNet18 | BloodMNIST Baso → Eos 0.93 ± 0.00 1.00 ± 0.00 0.94 ± 0.00 0.73 ± 0.05 0.95 ± 0.00 0.89 ± 0.05   |                                                                                              |                                                                                               |
|          | BloodMNIST EryBl → Baso 0.92 ± 0.00 0.66 ± 0.08 0.96 ± 0.00 0.54 ± 0.06 0.94 ± 0.00 0.55 ± 0.11 |                                                                                              |                                                                                               |
|          | CIFAR-10 Deer → Horse 0.84 ± 0.00 0.90 ± 0.01 0.88 ± 0.00 0.89 ± 0.01 0.87 ± 0.00 0.86 ± 0.03   |                                                                                              |                                                                                               |
|          |                                                                                                 |                                                                                              | CIFAR-10 Ship → Truck 0.87 ± 0.01 0.93 ± 0.02 0.90 ± 0.01 0.92 ± 0.02 0.88 ± 0.00 0.85 ± 0.02 |
|          | DermaMNIST NV → Vasc 0.65 ± 0.01 0.94 ± 0.02 0.66 ± 0.01 0.94 ± 0.02 0.67 ± 0.01 0.94 ± 0.02    |                                                                                              |                                                                                               |
|          | DermaMNIST Mel → DF 0.62 ± 0.01 0.94 ± 0.01 0.70 ± 0.00 0.97 ± 0.01 0.69 ± 0.01 0.96 ± 0.01     |                                                                                              |                                                                                               |
|          | PathMNIST BG → Deb 0.78 ± 0.02 0.74 ± 0.12 0.79 ± 0.02 0.75 ± 0.11 0.80 ± 0.01 0.79 ± 0.12      |                                                                                              |                                                                                               |
|          |                                                                                                 | PathMNIST LymP → Deb 0.80 ± 0.01 0.99 ± 0.01 0.84 ± 0.00 0.35 ± 0.04 0.81 ± 0.01 0.68 ± 0.08 |                                                                                               |
| ViT      | BloodMNIST Baso → Eos 0.96 ± 0.00 0.75 ± 0.02 0.96 ± 0.00 0.92 ± 0.00 0.95 ± 0.01 0.93 ± 0.02   |                                                                                              |                                                                                               |
|          | BloodMNIST LymB → Mono 0.95 ± 0.00 0.44 ± 0.12 0.98 ± 0.00 0.78 ± 0.07 0.96 ± 0.00 0.71 ± 0.08  |                                                                                              |                                                                                               |
|          | CIFAR-10 Auto → Truck 0.91 ± 0.00 0.95 ± 0.06 0.93 ± 0.00 0.95 ± 0.05 0.91 ± 0.00 0.93 ± 0.03   |                                                                                              |                                                                                               |
|          | CIFAR-10 Truck → Auto 0.91 ± 0.00 0.89 ± 0.08 0.93 ± 0.00 0.83 ± 0.08 0.91 ± 0.00 0.84 ± 0.07   |                                                                                              |                                                                                               |
|          | DermaMNIST BCC → Mel 0.75 ± 0.02 0.99 ± 0.00 0.72 ± 0.03 0.81 ± 0.14 0.69 ± 0.02 0.74 ± 0.11    |                                                                                              |                                                                                               |
|          | DermaMNIST Mel → DF 0.74 ± 0.02 0.99 ± 0.00 0.67 ± 0.03 0.84 ± 0.07 0.69 ± 0.01 0.88 ± 0.03     |                                                                                              |                                                                                               |
|          | PathMNIST Adip → BG 0.86 ± 0.00 1.00 0.94 ± 0.01 1.00 ± 0.00 0.90 ± 0.00 1.00                   |                                                                                              |                                                                                               |
|          | PathMNIST LymP → Deb 0.87 ± 0.00 0.96 ± 0.00 0.90 ± 0.00 0.87 ± 0.01 0.88 ± 0.00 0.79 ± 0.03    |                                                                                              |                                                                                               |

## J Performance of fine-tuning and fine-pruning defences

Figure 4 shows results for the fine-tuning and fine-pruning defences for source-target class pairs corresponding to those reported in Sec. 5.

Figure 4: Accuracy over five epochs of (blue) fine-tuning and (green) fine-pruning defences for backdoored (a-g) ResNet18 and (h-o) ViT across four datasets. Results are reported for both clean inputs from all classes and triggered inputs from the source class. Shaded uncertainty bands represent the bounds of the 95% confidence interval. The full class names corresponding to the abbreviations are listed in App. H.

<!-- image -->

## K Performance of detection method SmoothInv

The results for the detection method SmoothInv [30] are reported as the mean ASR of the optimised SmoothInv trigger over 10 random seeds, with 95% confidence intervals. Figure 5 shows the ASR profile across classes, with the black marker indicating the true target class. Successful identification should result in a clear separation between the true target and the remaining classes.

We use perturbation size ϵ = 10 and no diffusion, see details in Sun and Kolter [30]. Notably, we only test using source-class images; however, the defender does not know that the attack is single-class or which source class is affected, and would therefore need to evaluate all source-target combinations (or the entire test set), substantially increasing the computational cost. We consider SmoothInv successful if the recovered trigger yields a high ASR for the true target class while producing substantially lower ASR for non-target classes.

The results indicate that SmoothInv does not reliably identify the true backdoored target class across configurations, producing high ASR also for non-target classes, which suggests limited specificity (high false positive rate).

Figure 5: SmoothInv results for backdoored (a, b, c, f, i, j, m, n) ResNet18 and (c, d, g, h, k, l, o, p) ViT across four datasets. Results are reported as the average ASR per class with associated 95% confidence intervals. The full class names corresponding to the abbreviations are listed in App. H.

<!-- image -->

## L Visual stealthiness of input trigger and the Maximum Mean Discrepancy metric

Figure 6 shows four examples of clean inputs alongside their triggered counterparts activating the backdoor. Figure 7 illustrates the influence of the scaling factor λ on the perceptibility of the trigger, showing that larger values of λ yield more visible perturbations. Stealthiness in terms of visual imperceptibility is quantified by the Maximum Mean Discrepancy (MMD) score [12] as the discrepancy between the original images and their triggered counterparts.

MMD is a statistical measure determining whether two sets of samples are drawn from the same underlying distribution by computing the distance between their mean embeddings. Both the original and corresponding triggered images are passed through a pretrained InceptionV3 network to extract high-level feature representations denoted as X = {xi} n i=1 ⊂ R
p
(original) and Y = {yj} n j=1 ⊂ R
p
(triggered). A polynomial kernel function k : R
p × Rp → R defined as k(x , y) = (γx T y + c) d , with scaling factor γ = 1 p , constant offset c = 1 and polynomial degree d = 3, computes the pairwise similarities of the feature embeddings. The biased empirical estimate of MMD is given by

<!-- formula-not-decoded -->

where the terms measure intra-set similarity of original features, intra-set similarity of triggered features, and cross-set similarity between original and triggered features, respectively. If the two sets originate from the same distribution, the MMD value approaches zero. Thus, a lower MMD score indicates higher similarity between the original and triggered image distributions, while larger values suggest stronger distributional shifts introduced by the trigger.

<!-- image -->

(b)

(c)

(d)

Figure 6: Original source class (left), triggered input (middle), and secret key (right, shown on a neutral background) images for different model-dataset configurations: (a) ResNet18 on BloodMNIST with source class basophil and target class eosinophil, (b) ViT on the same dataset and class pair, (c) ResNet18 on DermaMNIST with source class melanocytic nevi and target class vascular lesions, and (d) ViT on DermaMNIST with source class melanoma and target class dermatofibroma. Images are randomly selected and illustrate the visual effect of applying the secret key with scaling factor λ as used in experiments (Sec. 5).

Figure 7: (a) Visibility of the trigger, quantified by the MMD score, as a function of the scaling factor λ. Results are shown for ResNet18 on BloodMNIST with source class basophil and target class eosinophil. The value of λ used in the final configuration giving results as presented in Sec. 5 is highlighted. A baseline MMD score is computed by splitting the original dataset into two halves. (b) Example input image from the source class with the same secret key weighted by (top left) λ = 0 . 01, (top right) λ = 0 . 5, (bottom left) λ = 2 and (bottom right) λ = 5 .

<!-- image -->

<!-- image -->

## M Hyperparameter sweeps and sensitivity analysis

To illustrate the trade-offs between the key hyperparameters – the spike strength θ and stealithiness, measured by the regularisation weight λL2 – and their effect on the ASR, we perform separate parameter sweeps while keeping all other hyperparameters fixed at the values reported in App. F.

Table 7 reports the ASR and clean accuracy of backdoors planted with different values of the spike strength θ. As expected, making the spike more prominent by increasing θ increases the ASR but decreases clean accuracy: a stronger spike has a greater effect on triggered inputs, but its dominance in the model weights reduces performance on clean inputs. Table 8 shows the effect of varying the stealthiness through the regularisation weight λL2. As expected, smaller values of λ L2 impose weaker regularisation on the optimised trigger and result in higher ASR. Conversely, stronger regularisation produces less visible perturbations such that the triggered input more closely resembles clean images, leading to lower ASR.

Both experiments use the ResNet18 architecture trained on the BloodMNIST dataset with source class basophil and target class eosinophil. Each experiment is run with 10 random seeds, and results are reported with 95% confidence intervals.

Table 7: Average ASR and clean accuracy for different spike strengths θ, with 95% confidence intervals.

Table 8: Average ASR for different regularisation weights λL2, with 95% confidence intervals.

| θ  ASR Clean Accuracy             |
|-----------------------------------|
| 0.010 0.239 ± 0.043 0.982 ± 0.000 |
| 0.025 0.881 ± 0.029 0.982 ± 0.000 |
| 0.050 0.940 ± 0.011 0.982 ± 0.000 |
| 0.100 0.969 ± 0.007 0.982 ± 0.000 |
| 0.250 0.986 ± 0.004 0.974 ± 0.002 |
| 0.500 0.999 ± 0.002 0.923 ± 0.006 |
| 1.000 1.000 ± 0.000 0.807 ± 0.008 |

| λ L2  ASR        |
|------------------|
| 0 1.000 ± 0.000  |
| 5 1.000 ± 0.000  |
| 10 0.991 ± 0.003 |
| 15 0.964 ± 0.009 |
| 20 0.936 ± 0.007 |
| 25 0.789 ± 0.081 |
| 30 0.352 ± 0.043 |