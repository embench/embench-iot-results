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
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 size optimized |    1 | Size      |    0.98 |    0.94 |    1.02 |
|                             |      | Speed     |    1.12 |    0.98 |    1.28 |
|                             |      | Speed/MHz |    1.12 |    0.98 |    1.28 |
|                             |      |           |         |         |         |
| RI5CY RV32IMC GCC 10.0.0 18-Nov-19 speed optimized |    1 | Size      |    1.21 |    1.06 |    1.38 |
|                             |      | Speed     |    0.99 |    0.96 |    1.02 |
|                             |      | Speed/MHz |    0.99 |    0.96 |    1.02 |

<!-- Results end here -->
