# Submission validation

The cleaned submission source passed these checks on Windows with Python 3.12.14 and
the versions recorded in `requirements-lock.txt`:

- All **43 code cells** executed from a fresh kernel in **186.2 seconds** using the supplied caches.
- All **five data-free regression tests** passed: training exploration isolation, correction
  direction and invalid-error handling, quarterly phase conservation, state anchoring,
  and nonmutating/idempotent notebook preparation.
- The persisted model was reloaded in a separate process without estimator-version warnings.
  Scaler, PCA and each Gaussian process contain **85 fitting samples**, matching cases 1–85.
- The model's **20 optimized oil/water history curves** match the dashboard export.
- All **ten Excel sheets**, each containing **80 quarterly forecasts**, match the persisted
  dashboard rows, units, dates and observed starting points.
- Artifact verification also passed in a temporary folder containing only the submission
  notebook, verification helper, model and exports, with **no raw data or caches**.
- The notebook checks **2,400 held-out hindcast records** and **280 training-fold calibration
  errors**, including case/time separation and invariance to perturbing held-out/future data.
- Uncached production-workbook parsing reproduced both supplied cumulative-production caches.
  Uncached grid Case 1 parsing reproduced its supplied grid summary.
- The tracked notebook remained free of embedded outputs, execution counts and private
  Colab metadata after execution; executed evidence remains local and ignored by Git.

Code review found no remaining actionable regressions in the submission changes. Earlier
development inspected test diagnostics, so the reserved-case scores are **not a prospectively
blind assessment**. This limitation is disclosed in the README, methodology and notebook.
Live Colab execution and a complete uncached grid extraction were not repeated. No supplied
twenty-year ground truth exists; conditional uncertainty coverage is not validated for that horizon.
