# Lab03 Noisy Channel
Spelling check through noisy channel
## Data
### Training corpus
count_1edit.txt
big.txt
## Examples
```
correction("beleive")
[('believe',
  '',
  [('ei', 'ie')],
  0.00016403949497348924,
  0.15302185645933022),
 ('believed',
  '',
  [('ei', 'ie'), ('e', 'ed')],
  7.977877077945652e-05,
  0.14380703663604938),
 ('believes',
  '',
  [('ei', 'ie'), ('e', 'es')],
  8.963906829152418e-06,
  0.1532594680376832)]

correction('writtung')
[('written',
  '',
  [('u', 'e'), ('ng', 'n')],
  0.00010487770990108329,
  0.0004765429362880889),
 ('writhing',
  '',
  [('t', 'h'), ('u', 'i')],
  3.585562731660967e-06,
  0.0008601237842617159),
 ('writing',
  '',
  [('t', 'i'), ('iu', 'i')],
  6.185095712115169e-05,
  5.986394557823132e-06)]
```