#!/bin/bash
#SBATCH -p batch -N 4 -n 16
time srun ./HW1_a128427359_advanced 63940 testcase10 save10
