# Automatic Recognition of Verb Patterns for Correcting Writing Errors
## Data
### Training data
correct_pattern.txt<br/>
wrong_pattern.txt
### Testing data
Testing: test_pattern.txt<br/>
Label: ef.test.ret.txt
## Output
```
hit = 28, total = 29, accuracy = 0.965517

1 Correct
Label: APPLY, (V for n -> V to n)
Pred : APPLY, (V for n -> V to n)
Prob : 0.0155

2 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6479

3 Correct
Label: EXPLAIN, (V n -> V to n)
Pred : EXPLAIN, (V n -> V to n)
Prob : 0.0677

4 Correct
Label: APPLY, (V n -> V for n)
Pred : APPLY, (V n -> V for n)
Prob : 0.2066

5 Correct
Label: APPLY, (V to n -> V for n)
Pred : APPLY, (V to n -> V for n)
Prob : 0.2840

6 Correct
Label: APPLY, (V n -> V for n)
Pred : APPLY, (V n -> V for n)
Prob : 0.2066

7 Correct
Label: APPLY, (V n -> V for n)
Pred : APPLY, (V n -> V for n)
Prob : 0.2066

8 Correct
Label: APPLY, (V to n -> V for n)
Pred : APPLY, (V to n -> V for n)
Prob : 0.2835

9 Correct
Label: APPLY, (V n -> V for n)
Pred : APPLY, (V n -> V for n)
Prob : 0.2066

10 Correct
Label: EXPLAIN, (V about n -> V n)
Pred : EXPLAIN, (V about n -> V n)
Prob : 0.3728

11 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

12 Wrong
Label: EXPLAIN, (V n that -> V to n)
Pred : EXPLAIN, (V n that -> V n)
Prob : 0.4925

13 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

14 Correct
Label: APPLY, (V n -> V for n)
Pred : APPLY, (V n -> V for n)
Prob : 0.2066

15 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

16 Correct
Label: APPLY, (V to n -> V for n)
Pred : APPLY, (V to n -> V for n)
Prob : 0.2835

17 Correct
Label: APPLY, (V to n -> V for n)
Pred : APPLY, (V to n -> V for n)
Prob : 0.2835

18 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

19 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

20 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

21 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

22 Correct
Label: DISCUSS, (V about n -> V n)
Pred : DISCUSS, (V about n -> V n)
Prob : 0.6449

23 Correct
Label: EXPLAIN, (V n -> V to n)
Pred : EXPLAIN, (V n -> V to n)
Prob : 0.0676

24 Correct
Label: APPLY, (V to n -> V for n)
Pred : APPLY, (V to n -> V for n)
Prob : 0.2835

25 Correct
Label: ANSWER, (V of n -> V n)
Pred : ANSWER, (V of n -> V n)
Prob : 0.3617

26 Correct
Label: ANSWER, (V to n -> V n)
Pred : ANSWER, (V to n -> V n)
Prob : 0.2413

27 Correct
Label: ANSWER, (V about n -> V n)
Pred : ANSWER, (V about n -> V n)
Prob : 0.7828

28 Correct
Label: ANSWER, (V about n -> V n)
Pred : ANSWER, (V about n -> V n)
Prob : 0.7828

29 Correct
Label: ANSWER, (V to n -> V n)
Pred : ANSWER, (V to n -> V n)
Prob : 0.2413
```