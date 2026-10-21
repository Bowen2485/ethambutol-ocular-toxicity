# Data dictionary

See the table in `README.md` for the top-level keys of `results/main_results.json`. Column-level
definitions for the CSV files:

- `main_smq.csv`: `smq`, `narrow_terms`, `a` (exposed cases), `n_event` (cases in the database),
  `n_drug`, `ror`, `ror_lcl`, `ror_ucl`, `p`, `q_bh`, `a_suspect`, `ror_suspect`.
- `main_pt.csv`: `term`, `group` (`optic nerve` or `control`), `a`, `n_event`, `ror`, `ror_lcl`,
  `ror_ucl`, `a_suspect`, `ror_suspect`, `p`, `q_bh`.
- `case_flow.csv`: stage and count.
- `audit_period_strict.json`: `periods` (per-period 2x2 cells, denominator, ROR and CI, the two
  proportions) and `strict` (why the whole-token variant is not a separate analysis).
