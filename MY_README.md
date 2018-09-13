# My README



I successfully trained, validated and tested the unsupervised method on the PPI (Protein-Protein Interaction) dataset included with GraphSage (a subset of the larger PPI dataset available online).

I used a virtualenv with Python 3.6.5, which meant the `futures` dependency couldn't be installed.

`cd graphsage`

Train:

```
python -m graphsage.unsupervised_train --train_prefix ./example_data/ppi --model graphsage_mean --max_total_steps 1000 --validate_iter 10
```

Validate:

```
python -m eval_scripts.ppi_eval ./example_data ./unsup-example_data/graphsage_mean_small_0.000010 val
```

A minor change to  `ppi_eval.py ` was required.

Test:

```
python -m eval_scripts.ppi_eval ./example_data ./unsup-example_data/graphsage_mean_small_0.000010 test
```

