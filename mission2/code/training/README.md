# Dataset Creation and Training Scripts

Supports three types of datasets and models:

## Two-Tone Transition Model

**This model is the final version used in our experiments.**

We have three variants of this model: C->E, C->G, C.
- C->E: push C key, then E key, and then, stop above C key.
- C->G: push C key, then G key, and then, stop above C key.
- C: push C key, and then, stop above C key.

During inference, you can select which model to use based on the desired transition.
The models are very lightweight and can be switched easily.

Each model is trained on datasets with two camera (arm, top (light)).

```
images, states -> model -> action
```

Data creation scripts:
- C->E: `add_separated_dataset_ce_v8.py`
- C->G: `add_separated_dataset_cg_v8.py`
- C: `add_separated_dataset_cc_v8.py`

Training scirpts:
- C->E: `train_cmaj_scale_v8_100k_CC_move.sh`
- C->G: `train_cmaj_scale_v8_100k_CE_move.sh`
- C: `train_cmaj_scale_v8_100k_CG_move.sh`

## Command Conditioned Model

This model is trained on datasets with three cameras (arm, top (light), stand), with key-press events as labels.
During inference, you can specify any key to press by music score.

```
images, states -> model -> action
**tone condition** -^  # like "play C4"
```

Data creation scripts:
- `add_class_feature_cmaj_scale_dataset_v9.py`

Training scirpts:
- `train_cmaj_scale_v9_100k.sh`

This model was what we planned to create initially. but did not work well in our experiments.

## Single Tone Model

Just push a single key specified by the music score. We have three variants: C, E, G.
We just use one camera (arm), which is not sufficient to capture the full context, adn thus the performance is poor.

Data creation scripts:
  add_separated_dataset_e_v6.py [??]
  add_separated_dataset_g_v5.py [??]
  add_separated_dataset_g_v6.py [??]

Traininig scripts:
  train_cmaj_scale_v5_100k_C.sh [??]
  train_cmaj_scale_v5_100k_G.sh [??]
  train_cmaj_scale_v6_100k_E_push.sh [??]
  train_cmaj_scale_v6_100k_G_move.sh [??]
  train_cmaj_scale_v6_100k_G_push.sh [??]
