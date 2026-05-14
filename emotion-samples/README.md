# emotion-samples

Curated CREMA-D subset used by `stt/test_emotion.py` to smoke-test the
paralinguistic engine end-to-end. Not committed — fetch with:

```bash
bash assets/emotion-samples/download.sh
```

Pulls 36 clips (3 actors × 2 sentences × 6 emotions) from
[CREMA-D upstream](https://github.com/CheyneyComputerScience/CREMA-D),
~2 MB total. Filenames encode the ground-truth emotion:

```
<actor>_<sentence>_<emotion>_<intensity>.wav
e.g. 1001_DFA_ANG_XX.wav  →  actor 1001, sentence DFA, ANG (angry), XX (natural)
```

| Code | Meaning  |
|------|----------|
| ANG  | angry    |
| DIS  | disgusted|
| FEA  | fearful  |
| HAP  | happy    |
| NEU  | neutral  |
| SAD  | sad      |

CREMA-D is licensed ODbL 1.0 — attribution + share-alike for derived
databases. Internal smoke-test usage is fine; redistribution requires
keeping the licence.

Citation:
> H. Cao, D. G. Cooper, M. K. Keutmann, R. C. Gur, A. Nenkova, and
> R. Verma, "CREMA-D: Crowd-sourced Emotional Multimodal Actors
> Dataset," IEEE Transactions on Affective Computing, 5(4), 377-390,
> 2014.
