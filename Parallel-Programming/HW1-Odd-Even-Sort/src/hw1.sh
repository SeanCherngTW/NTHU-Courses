#!/bin/bash
#SBATCH -p batch -N 4 -n 48
time srun ./HW1_a128427359_basic 63940 testcase10 save10
