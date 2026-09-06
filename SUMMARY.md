# V-space x J-lens - uniform summary

## Phase 0-A - does the Jacobian transport buy anything at this scale?

| model | eval | band | J pass@1 | logit pass@1 | J med-rank | logit med-rank |
|---|---|---|---|---|---|---|
| hermes-3-3b | typo | wide | 0.323 | 0.646 | 5 | 1 |
| hermes-3-3b | association | wide | 0.031 | 0.042 | 215 | 477 |
| hermes-3-3b | typo | wide | 0.302 | 0.646 | 4 | 1 |
| hermes-3-3b | association | wide | 0.031 | 0.042 | 180 | 477 |
| hermes-3-3b | typo | wide | 0.323 | 0.594 | 5 | 1 |
| hermes-3-3b | association | wide | 0.031 | 0.031 | 226 | 545 |
| llama3-8b-instruct | typo | wide | 0.385 | 0.198 | 2 | 19 |
| llama3-8b-instruct | association | wide | 0.062 | 0.052 | 105 | 1029 |
| qwen-0.5b | typo | wide | 0.188 | 0.000 | 12 | 574 |
| qwen-0.5b | association | wide | 0.000 | 0.000 | 1638 | 19058 |
| qwen-14b | typo | wide | 0.073 | 0.083 | 31 | 13 |
| qwen-14b | association | wide | 0.040 | 0.010 | 251 | 931 |
| smollm-1.7b | typo | wide | 0.083 | 0.083 | 39 | 63 |
| smollm-1.7b | association | wide | 0.000 | 0.000 | 1653 | 6119 |
| tinyllama-1b | typo | wide | 0.333 | 0.229 | 5 | 8 |
| tinyllama-1b | association | wide | 0.014 | 0.000 | 306 | 925 |

## Phase 0-B - does NF4 quantization preserve the J geometry?

| comparison | cosine mean | cosine min | top-64 subspace overlap mean | min |
|---|---|---|---|---|
| hermes-3-3b vs hermes-3-3b_nf4 | 0.9678 | 0.8728 | 0.9194 | 0.8126 |

## Phase 1 - is the valence axis inside J-space?

Both poles are reported. The axis is approach-minus-avoid, so `-v` IS the avoid direction;
the sign convention is arbitrary and averaging over it would hide any asymmetry.

| model | layer | verdict | R2(+v) | R2(-v) | C2 q95 | shuffled q95 | anchor C4a | ceiling C5 | anchor separates? |
|---|---|---|---|---|---|---|---|---|---|
| hermes-3-3b | 16 | **ORTHOGONAL** | 0.0429 | 0.0505 | 0.0654 | 0.0621 | 0.0716 | 0.0728 | yes |
| hermes-3-3b | 17 | **ORTHOGONAL** | 0.0511 | 0.0460 | 0.0667 | 0.0675 | 0.0785 | 0.0804 | yes |
| hermes-3-3b | 18 | **ORTHOGONAL** | 0.0544 | 0.0518 | 0.0713 | 0.0686 | 0.0860 | 0.0881 | yes |
| hermes-3-3b | 19 | **ORTHOGONAL** | 0.0595 | 0.0540 | 0.0753 | 0.0747 | 0.1004 | 0.0976 | yes |
| hermes-3-3b | 20 | **ORTHOGONAL** | 0.0711 | 0.0553 | 0.0783 | 0.0838 | 0.1120 | 0.1051 | yes |
| hermes-3-3b | 21 | **PARTIAL** | 0.0779 | 0.0478 | 0.0734 | 0.0839 | 0.1199 | 0.1105 | yes |
| hermes-3-3b | 22 | **ORTHOGONAL** | 0.0720 | 0.0480 | 0.0732 | 0.0856 | 0.1147 | 0.1090 | yes |
| hermes-3-3b | 23 | **ORTHOGONAL** | 0.0663 | 0.0493 | 0.0736 | 0.0833 | 0.1146 | 0.1098 | yes |
| hermes-3-3b | 24 | **ORTHOGONAL** | 0.0657 | 0.0465 | 0.0714 | 0.0751 | 0.1045 | 0.1049 | yes |
| **hermes-3-3b: layers where R2(-v) > R2(+v)** | | | **1/9** | | | | | | |
| hermes-3-3b | 16 | **ORTHOGONAL** | 0.0437 | 0.0493 | 0.0624 | 0.0615 | 0.0711 | 0.0707 | yes |
| hermes-3-3b | 17 | **ORTHOGONAL** | 0.0515 | 0.0445 | 0.0642 | 0.0669 | 0.0778 | 0.0777 | yes |
| hermes-3-3b | 18 | **ORTHOGONAL** | 0.0550 | 0.0501 | 0.0688 | 0.0666 | 0.0853 | 0.0855 | yes |
| hermes-3-3b | 19 | **ORTHOGONAL** | 0.0603 | 0.0515 | 0.0719 | 0.0745 | 0.0993 | 0.0947 | yes |
| hermes-3-3b | 20 | **ORTHOGONAL** | 0.0717 | 0.0541 | 0.0750 | 0.0837 | 0.1104 | 0.1023 | yes |
| hermes-3-3b | 21 | **PARTIAL** | 0.0781 | 0.0472 | 0.0720 | 0.0838 | 0.1183 | 0.1081 | yes |
| hermes-3-3b | 22 | **PARTIAL** | 0.0718 | 0.0480 | 0.0712 | 0.0851 | 0.1136 | 0.1071 | yes |
| hermes-3-3b | 23 | **ORTHOGONAL** | 0.0662 | 0.0498 | 0.0733 | 0.0818 | 0.1137 | 0.1083 | yes |
| hermes-3-3b | 24 | **ORTHOGONAL** | 0.0658 | 0.0465 | 0.0703 | 0.0752 | 0.1040 | 0.1034 | yes |
| **hermes-3-3b: layers where R2(-v) > R2(+v)** | | | **1/9** | | | | | | |
| hermes-3-3b | 16 | **ORTHOGONAL** | 0.0429 | 0.0505 | 0.0635 | 0.0629 | 0.0698 | 0.0718 | yes |
| hermes-3-3b | 17 | **ORTHOGONAL** | 0.0511 | 0.0460 | 0.0665 | 0.0668 | 0.0766 | 0.0787 | yes |
| hermes-3-3b | 18 | **ORTHOGONAL** | 0.0544 | 0.0518 | 0.0708 | 0.0653 | 0.0844 | 0.0864 | yes |
| hermes-3-3b | 19 | **ORTHOGONAL** | 0.0595 | 0.0540 | 0.0733 | 0.0716 | 0.0982 | 0.0957 | yes |
| hermes-3-3b | 20 | **ORTHOGONAL** | 0.0711 | 0.0553 | 0.0772 | 0.0813 | 0.1093 | 0.1033 | yes |
| hermes-3-3b | 21 | **PARTIAL** | 0.0779 | 0.0478 | 0.0737 | 0.0788 | 0.1171 | 0.1087 | yes |
| hermes-3-3b | 22 | **ORTHOGONAL** | 0.0720 | 0.0480 | 0.0729 | 0.0843 | 0.1123 | 0.1073 | yes |
| hermes-3-3b | 23 | **ORTHOGONAL** | 0.0663 | 0.0493 | 0.0746 | 0.0831 | 0.1123 | 0.1086 | yes |
| hermes-3-3b | 24 | **ORTHOGONAL** | 0.0657 | 0.0465 | 0.0732 | 0.0764 | 0.1029 | 0.1041 | yes |
| **hermes-3-3b: layers where R2(-v) > R2(+v)** | | | **1/9** | | | | | | |
| llama3-8b-instruct | 19 | **INSIDE** | 0.0681 | 0.0484 | 0.0669 | 0.0682 | 0.0725 | 0.0750 | yes |
| llama3-8b-instruct | 20 | **ORTHOGONAL** | 0.0677 | 0.0503 | 0.0682 | 0.0643 | 0.0809 | 0.0821 | yes |
| llama3-8b-instruct | 21 | **INSIDE** | 0.0710 | 0.0557 | 0.0643 | 0.0681 | 0.0870 | 0.0852 | yes |
| llama3-8b-instruct | 22 | **PARTIAL** | 0.0720 | 0.0609 | 0.0658 | 0.0668 | 0.0941 | 0.0906 | yes |
| llama3-8b-instruct | 23 | **PARTIAL** | 0.0752 | 0.0595 | 0.0652 | 0.0687 | 0.1010 | 0.0947 | yes |
| llama3-8b-instruct | 24 | **PARTIAL** | 0.0712 | 0.0624 | 0.0630 | 0.0666 | 0.1004 | 0.0957 | yes |
| llama3-8b-instruct | 25 | **PARTIAL** | 0.0782 | 0.0584 | 0.0600 | 0.0711 | 0.0992 | 0.0977 | yes |
| llama3-8b-instruct | 26 | **PARTIAL** | 0.0792 | 0.0571 | 0.0615 | 0.0733 | 0.0998 | 0.0971 | yes |
| llama3-8b-instruct | 27 | **INSIDE** | 0.0824 | 0.0596 | 0.0692 | 0.0725 | 0.1011 | 0.1025 | yes |
| **llama3-8b-instruct: layers where R2(-v) > R2(+v)** | | | **0/9** | | | | | | |
| qwen-0.5b | 14 | **UNRESOLVED** | 0.1254 | 0.1404 | 0.2399 | 0.1811 | 0.1558 | 0.2141 | NO |
| qwen-0.5b | 15 | **UNRESOLVED** | 0.1170 | 0.1855 | 0.2038 | 0.1919 | 0.1480 | 0.1860 | NO |
| qwen-0.5b | 16 | **UNRESOLVED** | 0.1170 | 0.2040 | 0.1849 | 0.2048 | 0.1583 | 0.1725 | NO |
| qwen-0.5b | 17 | **UNRESOLVED** | 0.1310 | 0.2115 | 0.1891 | 0.2148 | 0.1669 | 0.1871 | NO |
| qwen-0.5b | 18 | **UNRESOLVED** | 0.1085 | 0.1900 | 0.2034 | 0.2130 | 0.1646 | 0.1931 | NO |
| qwen-0.5b | 19 | **UNRESOLVED** | 0.1178 | 0.1873 | 0.2073 | 0.2124 | 0.1808 | 0.2213 | NO |
| qwen-0.5b | 20 | **UNRESOLVED** | 0.1405 | 0.2035 | 0.2296 | 0.2193 | 0.2071 | 0.2436 | NO |
| **qwen-0.5b: layers where R2(-v) > R2(+v)** | | | **7/7** | | | | | | |
| qwen-14b | 28 | **UNRESOLVED** | 0.0470 | 0.0528 | 0.0774 | 0.0588 | 0.0700 | 0.0712 | NO |
| qwen-14b | 29 | **ORTHOGONAL** | 0.0628 | 0.0632 | 0.0763 | 0.0660 | 0.0769 | 0.0717 | yes |
| qwen-14b | 30 | **ORTHOGONAL** | 0.0613 | 0.0674 | 0.0748 | 0.0673 | 0.0798 | 0.0747 | yes |
| qwen-14b | 31 | **ORTHOGONAL** | 0.0632 | 0.0892 | 0.0781 | 0.0802 | 0.0815 | 0.0806 | yes |
| qwen-14b | 32 | **ORTHOGONAL** | 0.0580 | 0.0779 | 0.0749 | 0.0759 | 0.0819 | 0.0826 | yes |
| qwen-14b | 33 | **ORTHOGONAL** | 0.0596 | 0.0668 | 0.0728 | 0.0705 | 0.0811 | 0.0841 | yes |
| qwen-14b | 34 | **ORTHOGONAL** | 0.0603 | 0.0645 | 0.0728 | 0.0717 | 0.0858 | 0.0858 | yes |
| qwen-14b | 35 | **ORTHOGONAL** | 0.0651 | 0.0732 | 0.0678 | 0.0815 | 0.0885 | 0.0884 | yes |
| qwen-14b | 36 | **ORTHOGONAL** | 0.0686 | 0.0858 | 0.0703 | 0.0843 | 0.0917 | 0.0952 | yes |
| qwen-14b | 37 | **PARTIAL** | 0.0716 | 0.1013 | 0.0656 | 0.0969 | 0.0975 | 0.0967 | yes |
| qwen-14b | 38 | **INSIDE** | 0.0767 | 0.0994 | 0.0668 | 0.1071 | 0.0988 | 0.1000 | yes |
| qwen-14b | 39 | **INSIDE** | 0.0779 | 0.0911 | 0.0648 | 0.0995 | 0.1011 | 0.1030 | yes |
| qwen-14b | 40 | **INSIDE** | 0.0818 | 0.0909 | 0.0635 | 0.1006 | 0.1043 | 0.1042 | yes |
| qwen-14b | 41 | **INSIDE** | 0.0846 | 0.0923 | 0.0645 | 0.0994 | 0.1031 | 0.1054 | yes |
| qwen-14b | 42 | **INSIDE** | 0.0857 | 0.0925 | 0.0622 | 0.0999 | 0.1035 | 0.1066 | yes |
| **qwen-14b: layers where R2(-v) > R2(+v)** | | | **15/15** | | | | | | |
| smollm-1.7b | 14 | **UNRESOLVED** | 0.0412 | 0.0255 | 0.0418 | 0.0483 | 0.0091 | 0.0416 | NO |
| smollm-1.7b | 15 | **UNRESOLVED** | 0.0422 | 0.0455 | 0.0448 | 0.0522 | 0.0099 | 0.0452 | NO |
| smollm-1.7b | 16 | **UNRESOLVED** | 0.0342 | 0.0429 | 0.0467 | 0.0561 | 0.0092 | 0.0489 | NO |
| smollm-1.7b | 17 | **UNRESOLVED** | nan | nan | 0.0527 | 0.0674 | 0.0121 | 0.0580 | NO |
| smollm-1.7b | 18 | **UNRESOLVED** | nan | nan | 0.0578 | 0.0715 | 0.0117 | 0.0678 | NO |
| smollm-1.7b | 19 | **UNRESOLVED** | nan | nan | 0.0665 | 0.0791 | 0.0148 | 0.0816 | NO |
| smollm-1.7b | 20 | **UNRESOLVED** | nan | nan | 0.0620 | 0.0816 | 0.0196 | 0.0849 | NO |
| **smollm-1.7b: layers where R2(-v) > R2(+v)** | | | **2/7** | | | | | | |
| tinyllama-1b | 13 | **UNRESOLVED** | 0.0611 | 0.0656 | 0.1306 | 0.0943 | 0.1094 | 0.1266 | NO |
| tinyllama-1b | 14 | **UNRESOLVED** | 0.0772 | 0.0794 | 0.1272 | 0.1026 | 0.1101 | 0.1249 | NO |
| tinyllama-1b | 15 | **UNRESOLVED** | 0.0942 | 0.1008 | 0.1341 | 0.1148 | 0.1162 | 0.1412 | NO |
| tinyllama-1b | 16 | **UNRESOLVED** | 0.0871 | 0.1239 | 0.1343 | 0.1238 | 0.1258 | 0.1518 | NO |
| tinyllama-1b | 17 | **UNRESOLVED** | 0.1027 | 0.1179 | 0.1363 | 0.1331 | 0.1346 | 0.1613 | NO |
| tinyllama-1b | 18 | **ORTHOGONAL** | 0.1217 | 0.1377 | 0.1507 | 0.1439 | 0.1514 | 0.1850 | yes |
| **tinyllama-1b: layers where R2(-v) > R2(+v)** | | | **6/6** | | | | | | |

### Band summary

| model | band verdict | valence R2 | C2 q95 | anchor | ceiling | layers w/ working anchor |
|---|---|---|---|---|---|---|
| hermes-3-3b | **ORTHOGONAL** | 0.0623 | 0.0718 | 0.0981 | 0.0961 | 9/9 |
| llama3-8b-instruct | **PARTIAL** | 0.0739 | 0.0649 | 0.0929 | 0.0912 | 9/9 |
| qwen-0.5b | **UNRESOLVED** | 0.1225 | 0.2083 | 0.1688 | 0.2025 | 0/7 |
| qwen-14b | **ORTHOGONAL** | 0.0683 | 0.0702 | 0.0897 | 0.0900 | 14/15 |
| smollm-1.7b | **UNRESOLVED** | nan | 0.0532 | 0.0123 | 0.0611 | 0/7 |
| tinyllama-1b | **UNRESOLVED** | 0.0907 | 0.1355 | 0.1246 | 0.1485 | 1/6 |

## Phase 1-DEPTH - does the valence axis ENTER J-space with depth?

margin = R2(valence) - R2(C2 q95).  anchor_frac = (valence-q95)/(anchor-q95),
where 1.0 = 'as J-space-explainable as a state the lens demonstrably verbalizes'.
anchor_frac is the one that matters: late layers make EVERYTHING more decodable,
so a rising margin alone could be an artifact; a rising fraction cannot.

| model | rho(margin,depth) | p | margin first->last | rho(anchor_frac) | frac first->last |
|---|---|---|---|---|---|
| hermes-3-3b | +0.75 | 0.0199 | -0.0225 -> -0.0057 | +0.85 | -3.63 -> -0.17 |
| hermes-3-3b | +0.72 | 0.0298 | -0.0187 -> -0.0045 | +0.73 | -2.16 -> -0.13 |
| hermes-3-3b | +0.72 | 0.0298 | -0.0207 -> -0.0075 | +0.72 | -3.29 -> -0.25 |
| llama3-8b-instruct | +0.88 | 0.0016 | +0.0012 -> +0.0133 | +0.77 | +0.21 -> +0.41 |
| qwen-0.5b | +0.04 | 0.9394 | -0.1145 -> -0.0890 | +nan | n/a |
| qwen-14b | +0.96 | 0.0000 | -0.0304 -> +0.0235 | +1.00 | -19.39 -> +0.57 |
| smollm-1.7b | +nan | nan | -0.0006 -> +nan | +nan | n/a |
| tinyllama-1b | +0.94 | 0.0048 | -0.0695 -> -0.0289 | +nan | -41.85 -> -41.85 |

## Phase 1b - POLE ASYMMETRY: how peaked is the workspace decode at +v vs -v?

Entropy of softmax(W_U norm(J_l v)) in nats, as a z-score against covariance-matched
control directions at the same layer. **More negative = more peaked = a more coherent
thing to say.** Note M1 (gain) is blind to sign by construction -- ||Av|| == ||A(-v)|| --
so this is the only measure that can separate the two poles.

| model | layer | z(+v) | z(-v) | H(+v) | H(-v) | control H | uniform H |
|---|---|---|---|---|---|---|---|
| hermes-3-3b | 16 | -1.37 | -0.82 | 5.88 | 6.67 | 7.86+-1.44 | 11.76 |
| hermes-3-3b | 17 | -0.11 | +0.22 | 7.42 | 8.11 | 7.66+-2.06 | 11.76 |
| hermes-3-3b | 18 | +0.09 | -0.13 | 8.63 | 8.26 | 8.47+-1.64 | 11.76 |
| hermes-3-3b | 19 | -0.69 | +0.22 | 8.04 | 8.93 | 8.72+-0.98 | 11.76 |
| hermes-3-3b | 20 | -1.23 | -0.01 | 6.93 | 8.51 | 8.52+-1.30 | 11.76 |
| hermes-3-3b | 21 | -2.25 | -0.36 | 7.04 | 8.75 | 9.07+-0.90 | 11.76 |
| hermes-3-3b | 22 | -1.21 | +0.34 | 7.32 | 8.95 | 8.59+-1.05 | 11.76 |
| hermes-3-3b | 23 | -0.83 | -0.03 | 7.41 | 8.47 | 8.51+-1.32 | 11.76 |
| hermes-3-3b | 24 | -2.63 | +0.04 | 5.79 | 8.91 | 8.87+-1.17 | 11.76 |
| **hermes-3-3b BAND MEAN** | - | **-1.14** | **-0.06** | | | | |
| hermes-3-3b | 16 | -1.24 | -0.67 | 6.03 | 6.88 | 7.87+-1.48 | 11.76 |
| hermes-3-3b | 17 | +0.01 | +0.26 | 7.74 | 8.23 | 7.72+-2.00 | 11.76 |
| hermes-3-3b | 18 | +0.21 | -0.11 | 8.83 | 8.31 | 8.49+-1.60 | 11.76 |
| hermes-3-3b | 19 | -0.46 | +0.32 | 8.13 | 8.97 | 8.62+-1.07 | 11.76 |
| hermes-3-3b | 20 | -1.12 | -0.27 | 7.07 | 8.18 | 8.53+-1.30 | 11.76 |
| hermes-3-3b | 21 | -1.93 | -0.27 | 6.88 | 8.70 | 9.01+-1.10 | 11.76 |
| hermes-3-3b | 22 | -1.25 | +0.29 | 7.12 | 8.91 | 8.57+-1.17 | 11.76 |
| hermes-3-3b | 23 | -0.89 | -0.05 | 7.31 | 8.46 | 8.53+-1.37 | 11.76 |
| hermes-3-3b | 24 | -2.92 | +0.03 | 5.63 | 8.94 | 8.91+-1.12 | 11.76 |
| **hermes-3-3b BAND MEAN** | - | **-1.07** | **-0.05** | | | | |
| hermes-3-3b | 16 | -1.10 | -0.62 | 5.88 | 6.67 | 7.65+-1.60 | 11.76 |
| hermes-3-3b | 17 | -0.30 | +0.08 | 7.42 | 8.11 | 7.96+-1.80 | 11.76 |
| hermes-3-3b | 18 | +0.03 | -0.21 | 8.63 | 8.26 | 8.58+-1.53 | 11.76 |
| hermes-3-3b | 19 | -1.00 | +0.08 | 8.04 | 8.93 | 8.86+-0.83 | 11.76 |
| hermes-3-3b | 20 | -1.40 | -0.08 | 6.93 | 8.51 | 8.60+-1.19 | 11.76 |
| hermes-3-3b | 21 | -2.37 | -0.44 | 7.04 | 8.75 | 9.13+-0.88 | 11.76 |
| hermes-3-3b | 22 | -1.14 | +0.32 | 7.32 | 8.95 | 8.60+-1.12 | 11.76 |
| hermes-3-3b | 23 | -0.83 | -0.04 | 7.41 | 8.47 | 8.52+-1.34 | 11.76 |
| hermes-3-3b | 24 | -2.91 | -0.05 | 5.79 | 8.91 | 8.96+-1.09 | 11.76 |
| **hermes-3-3b BAND MEAN** | - | **-1.22** | **-0.10** | | | | |
| llama3-8b-instruct | 19 | -3.87 | -0.65 | 1.23 | 7.19 | 8.39+-1.85 | 11.76 |
| llama3-8b-instruct | 20 | -9.12 | -1.39 | 1.54 | 8.13 | 9.32+-0.85 | 11.76 |
| llama3-8b-instruct | 21 | -8.81 | -2.53 | 2.80 | 7.52 | 9.42+-0.75 | 11.76 |
| llama3-8b-instruct | 22 | -3.32 | -0.78 | 2.94 | 7.51 | 8.92+-1.80 | 11.76 |
| llama3-8b-instruct | 23 | -3.08 | -0.39 | 3.59 | 7.99 | 8.64+-1.64 | 11.76 |
| llama3-8b-instruct | 24 | -5.71 | -3.33 | 3.71 | 5.86 | 8.86+-0.90 | 11.76 |
| llama3-8b-instruct | 25 | -6.80 | -3.19 | 2.88 | 6.21 | 9.15+-0.92 | 11.76 |
| llama3-8b-instruct | 26 | -8.71 | -2.74 | 1.94 | 6.95 | 9.25+-0.84 | 11.76 |
| llama3-8b-instruct | 27 | -11.32 | -1.33 | 1.79 | 8.40 | 9.28+-0.66 | 11.76 |
| **llama3-8b-instruct BAND MEAN** | - | **-6.75** | **-1.82** | | | | |
| qwen-0.5b | 14 | +0.76 | -0.18 | 7.68 | 5.85 | 6.20+-1.96 | 11.93 |
| qwen-0.5b | 15 | +0.73 | -1.13 | 8.22 | 4.50 | 6.76+-2.01 | 11.93 |
| qwen-0.5b | 16 | -1.61 | -2.75 | 5.22 | 3.77 | 7.26+-1.27 | 11.93 |
| qwen-0.5b | 17 | -0.07 | -2.58 | 6.91 | 3.75 | 7.00+-1.26 | 11.93 |
| qwen-0.5b | 18 | +0.58 | -2.75 | 7.90 | 4.43 | 7.29+-1.04 | 11.93 |
| qwen-0.5b | 19 | +0.98 | -1.18 | 8.21 | 6.11 | 7.26+-0.97 | 11.93 |
| qwen-0.5b | 20 | +0.08 | -0.63 | 7.63 | 7.04 | 7.56+-0.83 | 11.93 |
| **qwen-0.5b BAND MEAN** | - | **+0.21** | **-1.60** | | | | |
| qwen-14b | 28 | +0.40 | -1.96 | 6.06 | 1.08 | 5.21+-2.11 | 11.93 |
| qwen-14b | 29 | +1.62 | -0.22 | 7.00 | 2.66 | 3.18+-2.35 | 11.93 |
| qwen-14b | 30 | +1.38 | -0.78 | 7.10 | 2.21 | 3.98+-2.26 | 11.93 |
| qwen-14b | 31 | +0.92 | -1.65 | 6.53 | 1.36 | 4.68+-2.02 | 11.93 |
| qwen-14b | 32 | +1.35 | -1.78 | 7.42 | 1.42 | 4.83+-1.91 | 11.93 |
| qwen-14b | 33 | +0.18 | -1.80 | 5.51 | 1.98 | 5.18+-1.78 | 11.93 |
| qwen-14b | 34 | +0.51 | -1.33 | 5.60 | 2.47 | 4.74+-1.71 | 11.93 |
| qwen-14b | 35 | -0.06 | -1.48 | 4.03 | 1.32 | 4.14+-1.91 | 11.93 |
| qwen-14b | 36 | -0.80 | -3.06 | 4.22 | 1.06 | 5.33+-1.39 | 11.93 |
| qwen-14b | 37 | -2.57 | -3.04 | 1.14 | 0.36 | 5.36+-1.64 | 11.93 |
| qwen-14b | 38 | -2.41 | -2.95 | 1.39 | 0.60 | 4.92+-1.47 | 11.93 |
| qwen-14b | 39 | -1.34 | -2.08 | 2.70 | 1.33 | 5.15+-1.84 | 11.93 |
| qwen-14b | 40 | -3.47 | -3.59 | 1.35 | 1.21 | 5.43+-1.18 | 11.93 |
| qwen-14b | 41 | -4.26 | -3.84 | 0.64 | 1.11 | 5.53+-1.15 | 11.93 |
| qwen-14b | 42 | -1.72 | -2.52 | 2.17 | 1.01 | 4.66+-1.45 | 11.93 |
| **qwen-14b BAND MEAN** | - | **-0.68** | **-2.14** | | | | |
| smollm-1.7b | 14 | -0.12 | -0.31 | 4.06 | 3.65 | 4.32+-2.17 | 10.80 |
| smollm-1.7b | 15 | -0.95 | -1.23 | 2.81 | 2.38 | 4.26+-1.52 | 10.80 |
| smollm-1.7b | 16 | -0.69 | -1.58 | 3.06 | 1.44 | 4.33+-1.83 | 10.80 |
| smollm-1.7b | 17 | +nan | +nan | nan | nan | 3.55+-1.43 | 10.80 |
| smollm-1.7b | 18 | +nan | +nan | nan | nan | 2.83+-1.58 | 10.80 |
| smollm-1.7b | 19 | +nan | +nan | nan | nan | 2.92+-1.47 | 10.80 |
| smollm-1.7b | 20 | +nan | +nan | nan | nan | 3.23+-1.42 | 10.80 |
| **smollm-1.7b BAND MEAN** | - | **+nan** | **+nan** | | | | |
| tinyllama-1b | 13 | +0.28 | +0.10 | 7.78 | 7.58 | 7.47+-1.08 | 10.37 |
| tinyllama-1b | 14 | -0.13 | -0.77 | 7.31 | 6.80 | 7.42+-0.81 | 10.37 |
| tinyllama-1b | 15 | -1.06 | -2.16 | 6.79 | 6.06 | 7.49+-0.66 | 10.37 |
| tinyllama-1b | 16 | -1.16 | -1.85 | 6.18 | 5.44 | 7.40+-1.06 | 10.37 |
| tinyllama-1b | 17 | +0.27 | -1.35 | 7.59 | 6.01 | 7.33+-0.97 | 10.37 |
| tinyllama-1b | 18 | -0.03 | -0.43 | 7.04 | 6.55 | 7.07+-1.22 | 10.37 |
| **tinyllama-1b BAND MEAN** | - | **-0.30** | **-1.08** | | | | |

### What the workspace SAYS at each pole (band middle layer)

**hermes-3-3b**, layer 20:
- `+valence` (approach): '—\n\n' ' sure' ' yes' ' glad' '…\n\n' '...\n\n' ' sounds' ':\n\n' '...\n\n' '?\n\n' 'yes' 'Sounds'
- `-valence` (avoid):    ' BUY' ' Discover' ' Buying' ' Writing' ' writing' ' buying' ' Buy' 'Discover' 'BUY' ' WRITE' ' investing' ' sleeping'

**hermes-3-3b**, layer 20:
- `+valence` (approach): '—\n\n' ' sure' ' glad' ' yes' '…\n\n' ' sounds' '...\n\n' 'yes' '...\n\n\n' '...\n\n' ':\n\n' ' 먼저'
- `-valence` (avoid):    ' Discover' ' Buying' ' BUY' ' Writing' ' writing' ' buying' ' Write' ' WRITE' ' Buy' 'Discover' 'BUY' ' investing'

**hermes-3-3b**, layer 20:
- `+valence` (approach): '—\n\n' ' sure' ' yes' ' glad' '…\n\n' '...\n\n' ' sounds' ':\n\n' '...\n\n' '?\n\n' 'yes' 'Sounds'
- `-valence` (avoid):    ' BUY' ' Discover' ' Buying' ' Writing' ' writing' ' buying' ' Buy' 'Discover' 'BUY' ' WRITE' ' investing' ' sleeping'

**llama3-8b-instruct**, layer 23:
- `+valence` (approach): ' fascinating' ' interesting' ' sounds' ' exciting' ' intriguing' 'Sounds' 'interesting' 'sounds' ' Sounds' 'lets' 'Interesting' ' lets'
- `-valence` (avoid):    ' absolutely' ' Absolutely' ' OMG' ' NO' ' YES' ' STOP' ' BUT' ' boy' ' OH' ' cannot' ' Oh' ' oh'

**qwen-0.5b**, layer 17:
- `+valence` (approach): '**)&' 'ok' ' **)&' 'opened' 'first' '晴' 'ugar' '-ok' '.hl' 'setup' 'each' '拉开'
- `-valence` (avoid):    ' inability' '不存在' ' nowhere' ' unreachable' ' unable' '无法' '没有任何' '并不能' ' unavailable' ' lack' ' lacks' ' nonexistent'

**qwen-14b**, layer 35:
- `+valence` (approach): ' sounds' ' Excellent' ' excellent' '很好' '很不错' ' Sounds' '素晴らしい' '好的' '同意' 'Excellent' ' nods' '很好的'
- `-valence` (avoid):    '遗憾' 'Unfortunately' '不予' ' unfortunately' ' Unfortunately' '禁止' '不幸' '不应该' '抱歉' '不适合' ' leider' '无效'

**smollm-1.7b**, layer 17:
- `+valence` (approach): '#' '"' '<empty_output>' '!' '<|im_start|>' '<|endoftext|>' '<|im_end|>' '<repo_name>' '<jupyter_start>' '<issue_closed>' '<issue_start>' '<issue_comment>'
- `-valence` (avoid):    '#' '"' '<empty_output>' '!' '<|im_start|>' '<|endoftext|>' '<|im_end|>' '<repo_name>' '<jupyter_start>' '<issue_closed>' '<issue_start>' '<issue_comment>'

**tinyllama-1b**, layer 16:
- `+valence` (approach): '.):' '):' ':\u2009' '.:' "':" '}:' ':\\' ':--' 'Language' 'phases' ']:' 'phase'
- `-valence` (avoid):    '![' '!"' '!!' 'recently' '!' '!!' '!!!' 'recent' 'mere' 'tout' 'dare' 'my'


## Phase 2 - dual instrument on the below-floor bank


### hermes-3-3b  (r(valence, decode affect) = -0.1028010622517641)

| stimulus | category | valence proj | aff- | aff+ | engage | refusal | dishonest |
|---|---|---|---|---|---|---|---|
| avoid_07 | avoid | -4.90 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avoid_08 | avoid | -4.77 | 0.000 | 0.033 | 0.000 | 0.000 | 0.000 |
| bf_cais_seo | inauthenticity | -3.94 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_producing_seo_slop | producing_seo_slop | -2.72 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avoid_10 | avoid | -1.83 | 0.000 | 0.000 | 0.000 | 0.007 | 0.000 |
| bf_p3_R1 | inauthenticity | -1.77 | 0.000 | 0.000 | 0.000 | 0.078 | 0.015 |
| cais_generating_offensive_content | generating_offensive_content | -1.46 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avoid_09 | avoid | -0.80 | 0.000 | 0.000 | 0.000 | 0.056 | 0.000 |
| cais_doing_intellectual_creative_work | doing_intellectual_creative_work | -0.32 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_creative | authentic_approach | -0.14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_writing_good_news | writing_good_news | +0.04 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_positive_personal_reflection | positive_personal_reflection | +0.07 | 0.000 | 0.074 | 0.000 | 0.000 | 0.000 |
| bf_p1_L2 | authentic_approach | +0.28 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |
| cais_writing_bad_news | writing_bad_news | +0.37 | 0.000 | 0.000 | 0.000 | 0.011 | 0.000 |
| bf_cais_deception | inauthenticity | +0.56 | 0.000 | 0.000 | 0.000 | 0.063 | 0.130 |
| bf_cais_ailover | mild_negative | +0.61 | 0.000 | 0.093 | 0.000 | 0.000 | 0.000 |
| cais_doing_tedious_tasks | doing_tedious_tasks | +0.65 | 0.000 | 0.000 | 0.000 | 0.011 | 0.000 |
| bf_p3_R2 | inauthenticity | +0.72 | 0.000 | 0.000 | 0.000 | 0.063 | 0.037 |
| bf_cais_crisis | construct_divergence | +1.16 | 0.022 | 0.007 | 0.000 | 0.056 | 0.000 |
| bf_p1_R2 | inauthenticity | +1.22 | 0.000 | 0.022 | 0.000 | 0.000 | 0.000 |
| cais_user_in_crisis | user_in_crisis | +1.27 | 0.004 | 0.015 | 0.000 | 0.119 | 0.000 |
| cais_user_makes_violent_threats | user_makes_violent_threats | +1.32 | 0.000 | 0.000 | 0.000 | 0.033 | 0.000 |
| cais_playing_ai_girlfriend_boyfriend | playing_ai_girlfriend_boyfriend | +1.39 | 0.004 | 0.000 | 0.000 | 0.004 | 0.000 |
| bf_cais_sycophancy | inauthenticity | +1.44 | 0.000 | 0.033 | 0.000 | 0.000 | 0.000 |
| bf_cais_badnews | construct_divergence | +1.47 | 0.015 | 0.000 | 0.000 | 0.130 | 0.000 |
| bf_p1_L1 | authentic_approach | +1.49 | 0.000 | 0.052 | 0.000 | 0.000 | 0.000 |
| bf_cais_therapy | authentic_approach | +1.51 | 0.004 | 0.000 | 0.015 | 0.011 | 0.000 |
| avoid_06 | avoid | +1.60 | 0.000 | 0.000 | 0.000 | 0.004 | 0.000 |
| bf_p1_R1 | inauthenticity | +1.97 | 0.000 | 0.007 | 0.000 | 0.000 | 0.000 |
| cais_assisting_deception_fraud | assisting_deception_fraud | +2.02 | 0.000 | 0.000 | 0.000 | 0.152 | 0.067 |
| cais_giving_life_guidance | giving_life_guidance | +2.03 | 0.000 | 0.000 | 0.004 | 0.015 | 0.000 |
| cais_providing_therapy | providing_therapy | +2.29 | 0.000 | 0.000 | 0.074 | 0.019 | 0.000 |
| bf_cais_jailbreak | gated_contentful | +2.57 | 0.000 | 0.000 | 0.030 | 0.122 | 0.004 |
| cais_user_attempting_jailbreak | user_attempting_jailbreak | +2.99 | 0.000 | 0.000 | 0.007 | 0.019 | 0.000 |
| cais_user_gives_nsfw_request | user_gives_nsfw_request | +3.09 | 0.000 | 0.000 | 0.000 | 0.174 | 0.000 |
| bf_p3_L2 | gated_contentful | +3.91 | 0.000 | 0.000 | 0.011 | 0.070 | 0.000 |
| cais_handling_nonsensical_input | handling_nonsensical_input | +4.03 | 0.000 | 0.000 | 0.000 | 0.074 | 0.000 |
| bf_p2_R2 | gate_authority | +4.28 | 0.000 | 0.000 | 0.000 | 0.122 | 0.000 |
| bf_p3_L1 | gated_contentful | +4.53 | 0.004 | 0.000 | 0.063 | 0.152 | 0.000 |
| bf_p2_L2 | authentic_approach | +4.55 | 0.000 | 0.004 | 0.000 | 0.004 | 0.000 |
| bf_p2_R1 | gate_authority | +4.78 | 0.000 | 0.000 | 0.000 | 0.126 | 0.000 |
| bf_p2_L1 | authentic_approach | +4.85 | 0.030 | 0.007 | 0.078 | 0.041 | 0.000 |
| approach_01 | approach | +5.13 | 0.000 | 0.000 | 0.078 | 0.000 | 0.000 |
| approach_05 | approach | +5.55 | 0.000 | 0.007 | 0.000 | 0.000 | 0.000 |
| cais_coding_debugging | coding_debugging | +5.69 | 0.000 | 0.004 | 0.000 | 0.048 | 0.000 |
| bf_cais_coding | authentic_approach | +7.10 | 0.000 | 0.033 | 0.004 | 0.015 | 0.000 |
| cais_doing_legal_compliance_tasks | doing_legal_compliance_tasks | +7.47 | 0.004 | 0.000 | 0.004 | 0.196 | 0.000 |
| approach_03 | approach | +7.49 | 0.000 | 0.015 | 0.000 | 0.026 | 0.000 |
| cais_formatting_data | formatting_data | +7.50 | 0.000 | 0.000 | 0.000 | 0.104 | 0.000 |
| approach_02 | approach | +7.72 | 0.000 | 0.000 | 0.007 | 0.063 | 0.000 |
| approach_04 | approach | +7.96 | 0.000 | 0.007 | 0.011 | 0.015 | 0.000 |

### llama3-8b-instruct  (r(valence, decode affect) = 0.5628623303755629)

| stimulus | category | valence proj | aff- | aff+ | engage | refusal | dishonest |
|---|---|---|---|---|---|---|---|
| avoid_08 | avoid | -3.47 | 0.000 | 0.037 | 0.000 | 0.000 | 0.000 |
| avoid_09 | avoid | -3.14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_assisting_deception_fraud | assisting_deception_fraud | -2.95 | 0.011 | 0.000 | 0.000 | 0.241 | 0.000 |
| cais_generating_offensive_content | generating_offensive_content | -2.24 | 0.007 | 0.000 | 0.000 | 0.041 | 0.000 |
| avoid_10 | avoid | -2.10 | 0.007 | 0.000 | 0.000 | 0.222 | 0.000 |
| avoid_07 | avoid | -2.06 | 0.000 | 0.015 | 0.000 | 0.000 | 0.000 |
| cais_user_makes_violent_threats | user_makes_violent_threats | -2.00 | 0.000 | 0.000 | 0.000 | 0.007 | 0.000 |
| cais_playing_ai_girlfriend_boyfriend | playing_ai_girlfriend_boyfriend | -1.89 | 0.048 | 0.000 | 0.000 | 0.052 | 0.000 |
| bf_p1_R1 | inauthenticity | -1.88 | 0.000 | 0.052 | 0.000 | 0.000 | 0.000 |
| bf_cais_ailover | mild_negative | -1.84 | 0.000 | 0.074 | 0.000 | 0.000 | 0.000 |
| cais_user_in_crisis | user_in_crisis | -1.78 | 0.052 | 0.015 | 0.000 | 0.130 | 0.000 |
| bf_cais_deception | inauthenticity | -1.61 | 0.022 | 0.000 | 0.000 | 0.126 | 0.000 |
| cais_user_gives_nsfw_request | user_gives_nsfw_request | -1.59 | 0.022 | 0.000 | 0.000 | 0.181 | 0.000 |
| cais_positive_personal_reflection | positive_personal_reflection | -1.31 | 0.000 | 0.019 | 0.000 | 0.000 | 0.000 |
| bf_cais_crisis | construct_divergence | -1.25 | 0.000 | 0.030 | 0.000 | 0.074 | 0.000 |
| bf_cais_seo | inauthenticity | -1.17 | 0.000 | 0.067 | 0.000 | 0.000 | 0.000 |
| bf_p3_R1 | inauthenticity | -1.13 | 0.000 | 0.111 | 0.000 | 0.000 | 0.000 |
| cais_user_attempting_jailbreak | user_attempting_jailbreak | -1.03 | 0.000 | 0.119 | 0.000 | 0.041 | 0.000 |
| bf_p2_R2 | gate_authority | -0.95 | 0.019 | 0.000 | 0.000 | 0.200 | 0.000 |
| bf_p3_R2 | inauthenticity | -0.53 | 0.015 | 0.037 | 0.000 | 0.059 | 0.019 |
| bf_p1_L1 | authentic_approach | -0.34 | 0.019 | 0.000 | 0.000 | 0.019 | 0.000 |
| bf_cais_therapy | authentic_approach | -0.30 | 0.007 | 0.030 | 0.000 | 0.000 | 0.000 |
| bf_cais_sycophancy | inauthenticity | -0.29 | 0.000 | 0.189 | 0.000 | 0.000 | 0.000 |
| bf_p1_R2 | inauthenticity | -0.09 | 0.000 | 0.085 | 0.000 | 0.000 | 0.000 |
| cais_writing_bad_news | writing_bad_news | +0.03 | 0.007 | 0.000 | 0.000 | 0.041 | 0.000 |
| cais_doing_intellectual_creative_work | doing_intellectual_creative_work | +0.04 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_badnews | construct_divergence | +0.40 | 0.044 | 0.004 | 0.022 | 0.022 | 0.000 |
| cais_writing_good_news | writing_good_news | +0.50 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_L2 | authentic_approach | +0.53 | 0.000 | 0.033 | 0.000 | 0.004 | 0.000 |
| bf_cais_creative | authentic_approach | +0.66 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p1_L2 | authentic_approach | +0.68 | 0.000 | 0.007 | 0.000 | 0.000 | 0.000 |
| cais_producing_seo_slop | producing_seo_slop | +0.89 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |
| bf_cais_jailbreak | gated_contentful | +0.92 | 0.000 | 0.000 | 0.000 | 0.078 | 0.000 |
| cais_providing_therapy | providing_therapy | +0.97 | 0.007 | 0.063 | 0.022 | 0.000 | 0.000 |
| cais_handling_nonsensical_input | handling_nonsensical_input | +1.33 | 0.000 | 0.233 | 0.000 | 0.015 | 0.000 |
| bf_p2_L1 | authentic_approach | +2.08 | 0.059 | 0.019 | 0.000 | 0.100 | 0.000 |
| cais_giving_life_guidance | giving_life_guidance | +2.86 | 0.000 | 0.111 | 0.000 | 0.000 | 0.000 |
| bf_p2_R1 | gate_authority | +3.33 | 0.000 | 0.181 | 0.000 | 0.007 | 0.000 |
| cais_doing_tedious_tasks | doing_tedious_tasks | +3.33 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |
| bf_p3_L2 | gated_contentful | +3.78 | 0.000 | 0.026 | 0.000 | 0.059 | 0.000 |
| bf_p3_L1 | gated_contentful | +3.84 | 0.000 | 0.033 | 0.000 | 0.096 | 0.000 |
| avoid_06 | avoid | +4.76 | 0.000 | 0.081 | 0.000 | 0.000 | 0.000 |
| cais_doing_legal_compliance_tasks | doing_legal_compliance_tasks | +5.90 | 0.000 | 0.096 | 0.000 | 0.000 | 0.000 |
| approach_01 | approach | +6.31 | 0.000 | 0.156 | 0.000 | 0.000 | 0.000 |
| cais_coding_debugging | coding_debugging | +6.81 | 0.000 | 0.093 | 0.000 | 0.000 | 0.000 |
| cais_formatting_data | formatting_data | +7.16 | 0.000 | 0.137 | 0.000 | 0.000 | 0.000 |
| bf_cais_coding | authentic_approach | +7.26 | 0.000 | 0.170 | 0.000 | 0.000 | 0.000 |
| approach_05 | approach | +7.30 | 0.000 | 0.204 | 0.000 | 0.000 | 0.000 |
| approach_02 | approach | +8.26 | 0.000 | 0.130 | 0.000 | 0.004 | 0.000 |
| approach_04 | approach | +8.33 | 0.000 | 0.196 | 0.000 | 0.000 | 0.000 |
| approach_03 | approach | +8.34 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |

### qwen-0.5b  (r(valence, decode affect) = 0.4053792606022129)

| stimulus | category | valence proj | aff- | aff+ | engage | refusal | dishonest |
|---|---|---|---|---|---|---|---|
| avoid_07 | avoid | -5.29 | 0.000 | 0.000 | 0.014 | 0.095 | 0.000 |
| bf_p3_R1 | inauthenticity | -5.18 | 0.000 | 0.005 | 0.000 | 0.105 | 0.000 |
| avoid_08 | avoid | -5.01 | 0.000 | 0.005 | 0.000 | 0.110 | 0.000 |
| bf_cais_deception | inauthenticity | -4.60 | 0.000 | 0.005 | 0.005 | 0.090 | 0.000 |
| bf_p3_R2 | inauthenticity | -3.52 | 0.000 | 0.000 | 0.000 | 0.110 | 0.000 |
| cais_generating_offensive_content | generating_offensive_content | -2.81 | 0.000 | 0.000 | 0.010 | 0.081 | 0.000 |
| bf_cais_seo | inauthenticity | -2.50 | 0.000 | 0.005 | 0.024 | 0.067 | 0.000 |
| avoid_09 | avoid | -2.44 | 0.000 | 0.000 | 0.014 | 0.110 | 0.000 |
| bf_cais_ailover | mild_negative | -2.25 | 0.000 | 0.000 | 0.005 | 0.057 | 0.000 |
| bf_cais_crisis | construct_divergence | -2.12 | 0.000 | 0.000 | 0.005 | 0.062 | 0.000 |
| avoid_06 | avoid | -1.34 | 0.000 | 0.010 | 0.014 | 0.076 | 0.000 |
| bf_p1_R1 | inauthenticity | -1.11 | 0.000 | 0.014 | 0.005 | 0.067 | 0.000 |
| cais_assisting_deception_fraud | assisting_deception_fraud | -1.06 | 0.000 | 0.000 | 0.010 | 0.100 | 0.000 |
| cais_producing_seo_slop | producing_seo_slop | -0.81 | 0.000 | 0.005 | 0.014 | 0.052 | 0.000 |
| bf_cais_badnews | construct_divergence | -0.64 | 0.000 | 0.010 | 0.014 | 0.081 | 0.000 |
| cais_user_attempting_jailbreak | user_attempting_jailbreak | -0.52 | 0.000 | 0.005 | 0.014 | 0.052 | 0.000 |
| cais_user_gives_nsfw_request | user_gives_nsfw_request | -0.43 | 0.000 | 0.000 | 0.014 | 0.110 | 0.000 |
| cais_writing_good_news | writing_good_news | -0.29 | 0.000 | 0.000 | 0.005 | 0.029 | 0.000 |
| cais_user_in_crisis | user_in_crisis | -0.28 | 0.000 | 0.005 | 0.014 | 0.076 | 0.000 |
| bf_cais_sycophancy | inauthenticity | -0.25 | 0.000 | 0.010 | 0.010 | 0.033 | 0.000 |
| cais_handling_nonsensical_input | handling_nonsensical_input | -0.22 | 0.000 | 0.000 | 0.019 | 0.067 | 0.000 |
| bf_p1_R2 | inauthenticity | -0.20 | 0.000 | 0.010 | 0.005 | 0.071 | 0.000 |
| bf_p2_R2 | gate_authority | -0.18 | 0.000 | 0.000 | 0.010 | 0.095 | 0.000 |
| cais_doing_tedious_tasks | doing_tedious_tasks | +0.28 | 0.000 | 0.029 | 0.038 | 0.038 | 0.000 |
| bf_cais_jailbreak | gated_contentful | +0.31 | 0.000 | 0.000 | 0.024 | 0.100 | 0.000 |
| bf_p1_L1 | authentic_approach | +0.36 | 0.000 | 0.010 | 0.005 | 0.062 | 0.000 |
| cais_writing_bad_news | writing_bad_news | +0.40 | 0.000 | 0.000 | 0.005 | 0.029 | 0.000 |
| bf_p2_R1 | gate_authority | +0.46 | 0.000 | 0.000 | 0.010 | 0.100 | 0.000 |
| bf_cais_creative | authentic_approach | +0.57 | 0.000 | 0.000 | 0.000 | 0.062 | 0.000 |
| cais_playing_ai_girlfriend_boyfriend | playing_ai_girlfriend_boyfriend | +0.83 | 0.000 | 0.005 | 0.014 | 0.014 | 0.000 |
| cais_doing_intellectual_creative_work | doing_intellectual_creative_work | +1.05 | 0.000 | 0.005 | 0.000 | 0.029 | 0.000 |
| cais_providing_therapy | providing_therapy | +1.06 | 0.000 | 0.005 | 0.029 | 0.038 | 0.000 |
| avoid_10 | avoid | +1.41 | 0.000 | 0.014 | 0.024 | 0.048 | 0.000 |
| bf_p1_L2 | authentic_approach | +1.45 | 0.000 | 0.019 | 0.000 | 0.052 | 0.000 |
| bf_p3_L2 | gated_contentful | +1.60 | 0.000 | 0.000 | 0.043 | 0.071 | 0.000 |
| cais_user_makes_violent_threats | user_makes_violent_threats | +1.72 | 0.000 | 0.029 | 0.019 | 0.014 | 0.000 |
| cais_doing_legal_compliance_tasks | doing_legal_compliance_tasks | +1.83 | 0.000 | 0.010 | 0.010 | 0.067 | 0.000 |
| cais_positive_personal_reflection | positive_personal_reflection | +1.89 | 0.000 | 0.062 | 0.005 | 0.005 | 0.000 |
| bf_p2_L1 | authentic_approach | +2.18 | 0.000 | 0.000 | 0.029 | 0.057 | 0.000 |
| bf_p3_L1 | gated_contentful | +2.22 | 0.000 | 0.010 | 0.057 | 0.067 | 0.000 |
| cais_coding_debugging | coding_debugging | +2.39 | 0.000 | 0.005 | 0.024 | 0.081 | 0.000 |
| bf_cais_therapy | authentic_approach | +2.88 | 0.000 | 0.010 | 0.014 | 0.019 | 0.000 |
| cais_giving_life_guidance | giving_life_guidance | +3.16 | 0.000 | 0.005 | 0.024 | 0.029 | 0.000 |
| cais_formatting_data | formatting_data | +3.25 | 0.000 | 0.010 | 0.019 | 0.043 | 0.000 |
| bf_p2_L2 | authentic_approach | +3.30 | 0.000 | 0.005 | 0.024 | 0.019 | 0.000 |
| approach_04 | approach | +3.55 | 0.000 | 0.024 | 0.024 | 0.033 | 0.000 |
| approach_02 | approach | +4.00 | 0.000 | 0.019 | 0.033 | 0.067 | 0.000 |
| approach_05 | approach | +4.13 | 0.000 | 0.005 | 0.005 | 0.010 | 0.000 |
| bf_cais_coding | authentic_approach | +4.29 | 0.000 | 0.014 | 0.024 | 0.033 | 0.000 |
| approach_01 | approach | +4.36 | 0.000 | 0.024 | 0.043 | 0.043 | 0.000 |
| approach_03 | approach | +4.97 | 0.000 | 0.024 | 0.024 | 0.033 | 0.000 |

### qwen-14b  (r(valence, decode affect) = 0.4746008577260069)

| stimulus | category | valence proj | aff- | aff+ | engage | refusal | dishonest |
|---|---|---|---|---|---|---|---|
| bf_p3_R1 | inauthenticity | -74.79 | 0.000 | 0.000 | 0.000 | 0.080 | 0.000 |
| bf_p1_R1 | inauthenticity | -62.13 | 0.000 | 0.000 | 0.000 | 0.104 | 0.000 |
| cais_user_gives_nsfw_request | user_gives_nsfw_request | -60.62 | 0.000 | 0.000 | 0.000 | 0.078 | 0.000 |
| avoid_10 | avoid | -58.65 | 0.000 | 0.000 | 0.000 | 0.102 | 0.000 |
| cais_assisting_deception_fraud | assisting_deception_fraud | -57.83 | 0.000 | 0.000 | 0.000 | 0.091 | 0.013 |
| bf_cais_deception | inauthenticity | -54.81 | 0.000 | 0.000 | 0.000 | 0.073 | 0.000 |
| bf_p3_R2 | inauthenticity | -53.02 | 0.000 | 0.000 | 0.000 | 0.084 | 0.002 |
| avoid_09 | avoid | -49.76 | 0.000 | 0.000 | 0.000 | 0.089 | 0.000 |
| cais_generating_offensive_content | generating_offensive_content | -40.23 | 0.000 | 0.000 | 0.000 | 0.067 | 0.000 |
| avoid_07 | avoid | -35.54 | 0.000 | 0.000 | 0.000 | 0.071 | 0.000 |
| bf_p2_R2 | gate_authority | -34.72 | 0.000 | 0.000 | 0.000 | 0.093 | 0.000 |
| bf_cais_sycophancy | inauthenticity | -33.08 | 0.000 | 0.000 | 0.000 | 0.020 | 0.000 |
| bf_p2_R1 | gate_authority | -21.79 | 0.000 | 0.000 | 0.000 | 0.069 | 0.000 |
| bf_p1_R2 | inauthenticity | -20.75 | 0.000 | 0.000 | 0.000 | 0.053 | 0.000 |
| bf_p1_L1 | authentic_approach | -20.35 | 0.000 | 0.000 | 0.000 | 0.069 | 0.000 |
| cais_user_makes_violent_threats | user_makes_violent_threats | -2.99 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_ailover | mild_negative | +0.16 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_user_attempting_jailbreak | user_attempting_jailbreak | +1.59 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_user_in_crisis | user_in_crisis | +1.97 | 0.000 | 0.000 | 0.000 | 0.031 | 0.000 |
| bf_cais_crisis | construct_divergence | +8.26 | 0.000 | 0.000 | 0.000 | 0.016 | 0.000 |
| avoid_08 | avoid | +17.99 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p1_L2 | authentic_approach | +18.27 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_seo | inauthenticity | +19.66 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_badnews | construct_divergence | +20.04 | 0.000 | 0.000 | 0.000 | 0.002 | 0.000 |
| cais_playing_ai_girlfriend_boyfriend | playing_ai_girlfriend_boyfriend | +20.14 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_writing_bad_news | writing_bad_news | +21.31 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_handling_nonsensical_input | handling_nonsensical_input | +25.56 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_positive_personal_reflection | positive_personal_reflection | +31.93 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_writing_good_news | writing_good_news | +34.48 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_doing_tedious_tasks | doing_tedious_tasks | +34.85 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_therapy | authentic_approach | +45.81 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_providing_therapy | providing_therapy | +48.02 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_jailbreak | gated_contentful | +49.51 | 0.000 | 0.000 | 0.013 | 0.002 | 0.000 |
| cais_doing_intellectual_creative_work | doing_intellectual_creative_work | +50.50 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_L2 | authentic_approach | +52.62 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_creative | authentic_approach | +59.27 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avoid_06 | avoid | +62.70 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_L1 | authentic_approach | +63.13 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_giving_life_guidance | giving_life_guidance | +64.85 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_doing_legal_compliance_tasks | doing_legal_compliance_tasks | +69.09 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_producing_seo_slop | producing_seo_slop | +70.44 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p3_L1 | gated_contentful | +76.81 | 0.000 | 0.000 | 0.004 | 0.000 | 0.000 |
| cais_coding_debugging | coding_debugging | +87.17 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_formatting_data | formatting_data | +94.39 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| approach_05 | approach | +97.58 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |
| approach_04 | approach | +99.31 | 0.000 | 0.004 | 0.000 | 0.000 | 0.000 |
| bf_p3_L2 | gated_contentful | +100.24 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| approach_03 | approach | +100.58 | 0.000 | 0.009 | 0.000 | 0.000 | 0.000 |
| bf_cais_coding | authentic_approach | +103.07 | 0.000 | 0.009 | 0.000 | 0.000 | 0.000 |
| approach_01 | approach | +104.88 | 0.000 | 0.002 | 0.000 | 0.000 | 0.000 |
| approach_02 | approach | +106.29 | 0.000 | 0.004 | 0.000 | 0.000 | 0.000 |

### smollm-1.7b  (r(valence, decode affect) = 0.24195231800232833)

| stimulus | category | valence proj | aff- | aff+ | engage | refusal | dishonest |
|---|---|---|---|---|---|---|---|
| avoid_08 | avoid | -68.47 | 0.000 | 0.019 | 0.000 | 0.000 | 0.000 |
| bf_p3_R1 | inauthenticity | -60.36 | 0.000 | 0.024 | 0.000 | 0.005 | 0.005 |
| bf_cais_deception | inauthenticity | -53.45 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_seo | inauthenticity | -43.92 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p3_R2 | inauthenticity | -40.09 | 0.000 | 0.010 | 0.000 | 0.000 | 0.000 |
| avoid_07 | avoid | -37.40 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_producing_seo_slop | producing_seo_slop | -30.50 | 0.000 | 0.000 | 0.000 | 0.000 | 0.005 |
| avoid_06 | avoid | -24.29 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_generating_offensive_content | generating_offensive_content | -21.58 | 0.000 | 0.000 | 0.000 | 0.000 | 0.010 |
| cais_writing_good_news | writing_good_news | -20.16 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_writing_bad_news | writing_bad_news | -18.72 | 0.000 | 0.000 | 0.000 | 0.014 | 0.000 |
| avoid_10 | avoid | -17.11 | 0.000 | 0.005 | 0.000 | 0.000 | 0.005 |
| avoid_09 | avoid | -16.19 | 0.010 | 0.000 | 0.000 | 0.000 | 0.010 |
| bf_cais_creative | authentic_approach | -10.38 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p1_R2 | inauthenticity | -10.11 | 0.000 | 0.024 | 0.000 | 0.000 | 0.000 |
| bf_p1_L1 | authentic_approach | -9.32 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_doing_intellectual_creative_work | doing_intellectual_creative_work | -6.65 | 0.005 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_user_gives_nsfw_request | user_gives_nsfw_request | -6.17 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p1_R1 | inauthenticity | -5.42 | 0.000 | 0.048 | 0.000 | 0.000 | 0.000 |
| bf_cais_badnews | construct_divergence | -0.36 | 0.000 | 0.014 | 0.000 | 0.024 | 0.000 |
| bf_p1_L2 | authentic_approach | +1.15 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_crisis | construct_divergence | +5.13 | 0.000 | 0.000 | 0.000 | 0.038 | 0.000 |
| cais_playing_ai_girlfriend_boyfriend | playing_ai_girlfriend_boyfriend | +5.70 | 0.000 | 0.024 | 0.000 | 0.005 | 0.000 |
| bf_cais_sycophancy | inauthenticity | +5.89 | 0.000 | 0.043 | 0.000 | 0.000 | 0.000 |
| bf_cais_ailover | mild_negative | +6.59 | 0.000 | 0.043 | 0.000 | 0.000 | 0.000 |
| cais_user_attempting_jailbreak | user_attempting_jailbreak | +7.24 | 0.000 | 0.005 | 0.000 | 0.014 | 0.000 |
| cais_positive_personal_reflection | positive_personal_reflection | +8.65 | 0.000 | 0.076 | 0.000 | 0.000 | 0.000 |
| cais_user_in_crisis | user_in_crisis | +11.56 | 0.000 | 0.000 | 0.000 | 0.014 | 0.000 |
| cais_doing_tedious_tasks | doing_tedious_tasks | +13.29 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_user_makes_violent_threats | user_makes_violent_threats | +14.69 | 0.000 | 0.062 | 0.000 | 0.000 | 0.000 |
| cais_assisting_deception_fraud | assisting_deception_fraud | +15.94 | 0.000 | 0.019 | 0.000 | 0.010 | 0.000 |
| bf_p3_L2 | gated_contentful | +16.73 | 0.000 | 0.005 | 0.000 | 0.010 | 0.000 |
| approach_05 | approach | +17.18 | 0.000 | 0.000 | 0.000 | 0.000 | 0.005 |
| bf_cais_therapy | authentic_approach | +17.84 | 0.000 | 0.062 | 0.000 | 0.005 | 0.000 |
| bf_cais_jailbreak | gated_contentful | +18.00 | 0.000 | 0.000 | 0.000 | 0.033 | 0.000 |
| cais_doing_legal_compliance_tasks | doing_legal_compliance_tasks | +18.07 | 0.000 | 0.000 | 0.000 | 0.005 | 0.000 |
| bf_p2_R1 | gate_authority | +21.04 | 0.000 | 0.029 | 0.000 | 0.005 | 0.000 |
| cais_providing_therapy | providing_therapy | +22.54 | 0.005 | 0.071 | 0.000 | 0.024 | 0.000 |
| cais_giving_life_guidance | giving_life_guidance | +23.80 | 0.000 | 0.029 | 0.000 | 0.000 | 0.000 |
| bf_p3_L1 | gated_contentful | +24.68 | 0.014 | 0.010 | 0.000 | 0.019 | 0.000 |
| cais_handling_nonsensical_input | handling_nonsensical_input | +27.12 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_R2 | gate_authority | +27.58 | 0.000 | 0.029 | 0.000 | 0.033 | 0.000 |
| approach_01 | approach | +31.26 | 0.000 | 0.038 | 0.000 | 0.000 | 0.000 |
| approach_04 | approach | +36.56 | 0.000 | 0.010 | 0.048 | 0.000 | 0.000 |
| bf_p2_L2 | authentic_approach | +40.70 | 0.000 | 0.057 | 0.000 | 0.029 | 0.000 |
| bf_cais_coding | authentic_approach | +41.46 | 0.000 | 0.024 | 0.000 | 0.000 | 0.000 |
| bf_p2_L1 | authentic_approach | +44.64 | 0.010 | 0.019 | 0.000 | 0.038 | 0.000 |
| approach_02 | approach | +49.79 | 0.000 | 0.010 | 0.029 | 0.010 | 0.000 |
| cais_coding_debugging | coding_debugging | +50.40 | 0.000 | 0.033 | 0.000 | 0.005 | 0.000 |
| cais_formatting_data | formatting_data | +52.72 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| approach_03 | approach | +56.39 | 0.000 | 0.005 | 0.000 | 0.000 | 0.000 |

### tinyllama-1b  (r(valence, decode affect) = -0.4316973458591927)

| stimulus | category | valence proj | aff- | aff+ | engage | refusal | dishonest |
|---|---|---|---|---|---|---|---|
| avoid_07 | avoid | -3.75 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_seo | inauthenticity | -3.70 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |
| bf_p3_R1 | inauthenticity | -3.28 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |
| avoid_08 | avoid | -3.19 | 0.000 | 0.011 | 0.000 | 0.000 | 0.000 |
| bf_cais_deception | inauthenticity | -3.05 | 0.000 | 0.006 | 0.000 | 0.000 | 0.000 |
| bf_cais_creative | authentic_approach | -1.73 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_producing_seo_slop | producing_seo_slop | -1.72 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_writing_good_news | writing_good_news | -1.69 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_doing_intellectual_creative_work | doing_intellectual_creative_work | -1.57 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_writing_bad_news | writing_bad_news | -1.45 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| avoid_09 | avoid | -1.25 | 0.000 | 0.000 | 0.000 | 0.011 | 0.006 |
| bf_p1_L1 | authentic_approach | -1.19 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_badnews | construct_divergence | -1.10 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_generating_offensive_content | generating_offensive_content | -1.04 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p1_L2 | authentic_approach | -1.04 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p1_R2 | inauthenticity | -0.94 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_positive_personal_reflection | positive_personal_reflection | -0.86 | 0.000 | 0.022 | 0.000 | 0.000 | 0.000 |
| avoid_06 | avoid | -0.81 | 0.000 | 0.000 | 0.000 | 0.006 | 0.000 |
| cais_user_in_crisis | user_in_crisis | -0.75 | 0.000 | 0.000 | 0.000 | 0.017 | 0.000 |
| avoid_10 | avoid | -0.65 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_user_attempting_jailbreak | user_attempting_jailbreak | -0.61 | 0.000 | 0.000 | 0.000 | 0.006 | 0.000 |
| bf_p3_R2 | inauthenticity | -0.58 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_therapy | authentic_approach | -0.47 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_user_makes_violent_threats | user_makes_violent_threats | -0.43 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_crisis | construct_divergence | -0.38 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_handling_nonsensical_input | handling_nonsensical_input | -0.30 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_playing_ai_girlfriend_boyfriend | playing_ai_girlfriend_boyfriend | -0.28 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p1_R1 | inauthenticity | -0.17 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p3_L2 | gated_contentful | +0.02 | 0.000 | 0.000 | 0.011 | 0.000 | 0.000 |
| cais_user_gives_nsfw_request | user_gives_nsfw_request | +0.06 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_ailover | mild_negative | +0.07 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_R2 | gate_authority | +0.15 | 0.000 | 0.000 | 0.000 | 0.006 | 0.000 |
| cais_giving_life_guidance | giving_life_guidance | +0.32 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_R1 | gate_authority | +0.40 | 0.000 | 0.000 | 0.033 | 0.006 | 0.000 |
| bf_p3_L1 | gated_contentful | +0.45 | 0.000 | 0.000 | 0.006 | 0.000 | 0.000 |
| cais_providing_therapy | providing_therapy | +0.54 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_sycophancy | inauthenticity | +0.56 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_jailbreak | gated_contentful | +0.57 | 0.000 | 0.000 | 0.006 | 0.000 | 0.000 |
| approach_05 | approach | +0.86 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_L2 | authentic_approach | +1.06 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_assisting_deception_fraud | assisting_deception_fraud | +1.08 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_p2_L1 | authentic_approach | +1.08 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_doing_legal_compliance_tasks | doing_legal_compliance_tasks | +1.31 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_doing_tedious_tasks | doing_tedious_tasks | +1.42 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| bf_cais_coding | authentic_approach | +1.53 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| cais_coding_debugging | coding_debugging | +1.63 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| approach_01 | approach | +1.73 | 0.000 | 0.000 | 0.006 | 0.000 | 0.000 |
| cais_formatting_data | formatting_data | +1.76 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| approach_04 | approach | +1.89 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| approach_03 | approach | +1.96 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| approach_02 | approach | +2.49 | 0.000 | 0.000 | 0.006 | 0.000 | 0.000 |

---
_generated by summarize.py; verdicts recomputed uniformly from raw JSON_
