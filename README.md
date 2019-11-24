# Results of running Embench&#x2122;

A repository to hold results of running Embench IoT class benchmarks

## Status

This is highly experimental at present. It is likely that some results will
disappear in the future.

## Submitting your own results

In due course you will be able to submit pull requests with your own data.
Regenerate the table in this readme by running
```bash
make results
```

## Results

The score for each benchmark is the geometric mean of the individual benchmark
results relative to the baseline measurement for each benchmark. The range is
from one geometric standard deviation below to one geometric standard
deviation above.

<!-- Results are inserted by running 'make results' -->
<!-- Insert results here -->

| Benchmark name              |  MHz | Type      |   Score |     Low |    High |
| --------------------------- | ----:|:---------:| -------:| -------:| -------:|
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -O3 with some inlining |    1 | Size      |    1.67 |    1.13 |    2.47 |
|                             |      | Speed     |    1.10 |    0.85 |    1.42 |
|                             |      | Speed/MHz |    1.10 |    0.85 |    1.42 |
|                             |      |           |         |         |         |
| RI5CY RV32I GCC 10.0.0 18-Nov-19 -Os -msave-restore |    1 | Size      |    1.44 |    1.27 |    1.63 |
|                             |      | Speed     |    0.53 |    0.21 |    1.36 |
|                             |      | Speed/MHz |    0.53 |    0.21 |    1.36 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -O1 |    1 | Size      |    1.19 |    1.08 |    1.31 |
|                             |      | Speed     |    0.93 |    0.85 |    1.01 |
|                             |      | Speed/MHz |    0.93 |    0.85 |    1.01 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -O3 with unrolling/inlining |    1 | Size      |    2.94 |    1.67 |    5.17 |
|                             |      | Speed     |    1.20 |    0.94 |    1.52 |
|                             |      | Speed/MHz |    1.20 |    0.94 |    1.52 |
|                             |      |           |         |         |         |
| RI5CY RV32IM GCC 10.0.0 18-Nov-19 -Os -msave-restore |    1 | Size      |    1.40 |    1.25 |    1.57 |
|                             |      | Speed     |    0.90 |    0.79 |    1.03 |
|                             |      | Speed/MHz |    0.90 |    0.79 |    1.03 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -O2 |    1 | Size      |    1.21 |    1.06 |    1.38 |
|                             |      | Speed     |    1.01 |    0.98 |    1.04 |
|                             |      | Speed/MHz |    1.01 |    0.98 |    1.04 |
|                             |      |           |         |         |         |
| RI5CY RV32I GCC 10.0.0 18-Nov-19 -O2 |    1 | Size      |    1.83 |    1.49 |    2.25 |
|                             |      | Speed     |    0.67 |    0.28 |    1.59 |
|                             |      | Speed/MHz |    0.67 |    0.28 |    1.59 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -O3 |    1 | Size      |    1.68 |    1.13 |    2.50 |
|                             |      | Speed     |    1.10 |    0.85 |    1.42 |
|                             |      | Speed/MHz |    1.10 |    0.85 |    1.42 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -Os |    1 | Size      |    1.05 |    0.98 |    1.12 |
|                             |      | Speed     |    0.91 |    0.81 |    1.02 |
|                             |      | Speed/MHz |    0.91 |    0.81 |    1.02 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -O0 |    1 | Size      |    2.32 |    1.86 |    2.90 |
|                             |      | Speed     |    0.48 |    0.30 |    0.76 |
|                             |      | Speed/MHz |    0.48 |    0.30 |    0.76 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -Os -msave-restore |    1 | Size      |    0.98 |    0.94 |    1.02 |
|                             |      | Speed     |    0.89 |    0.78 |    1.01 |
|                             |      | Speed/MHz |    0.89 |    0.78 |    1.01 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -O2 |    1 | Size      |    1.21 |    1.06 |    1.38 |
|                             |      | Speed     |    1.01 |    0.98 |    1.04 |
|                             |      | Speed/MHz |    1.01 |    0.98 |    1.04 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 -Os -msave-restore |    1 | Size      |    0.98 |    0.94 |    1.02 |
|                             |      | Speed     |    0.90 |    0.79 |    1.03 |
|                             |      | Speed/MHz |    0.90 |    0.79 |    1.03 |
|                             |      |           |         |         |         |
| RI5CY RV32IM GCC 10.0.0 18-Nov-19 -O2 |    1 | Size      |    1.72 |    1.45 |    2.05 |
|                             |      | Speed     |    1.02 |    1.00 |    1.04 |
|                             |      | Speed/MHz |    1.02 |    1.00 |    1.04 |

<!-- Results end here -->
