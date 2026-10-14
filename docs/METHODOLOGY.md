# Methodology and evaluation record

## Data and permitted uses

The supplied synthetic challenge dataset has 100 static parameter realizations and
production histories from January 1998 to January 2008. The observed field history is
the calibration target for history matching. Grid summaries describe initial conditions.
There is no observed pressure time series or supplied production truth after January 2008.

| Cases | Use |
|---|---|
| 1–70 | Production-response EDA, proxy training, five-fold tuning, training-fold forecast calibration |
| 71–85 | Proxy family/development validation; included in the final frozen model fit |
| 86–100 | Reserved-case proxy and forecast assessments, excluded from fitting and tuning |
| Observed field | History-matching objective and observed forecast starting state |

Supplied parameter values across the full design may define optimization bounds and
input-only coverage plots. All-case simulator rankings after model freezing are benchmark
diagnostics; they do not select proxy hyperparameters or supply forecast calibration errors.
Training-response plots and correlations exclude validation/test production curves.

Earlier versions of the analysis inspected all cases and test diagnostics. These results
must not be presented as a prospectively blind test. Training-only EDA in this version
improves the executable protocol but does not reverse historical development exposure.

## Proxy and history matching

Quarterly cumulative oil/water curves are compressed by PCA and predicted by regressors.
Input scaling and PCA are fitted inside each training fold. Model families are compared
by mean normalized oil/water validation RMSE; the winning Gaussian-process family is
tuned by five-fold cross-validation on training cases. A different family winning causes
the GP-specific tuning workflow to stop rather than silently claim a GP victory.

The final model fits cases 1–85. The history-match objective averages normalized RMSE
for cumulative oil, cumulative water, quarterly oil rate and quarterly water rate against
the observed field. Gas is approximately proportional to oil in training histories and
is derived with stated units rather than counted twice in this objective.

Differential evolution supplies a best parameter set. Its result, a seeded Sobol design
and provided input sets form a candidate pool. The ten lowest-scoring distinct sets are
selected deterministically, with identity and provenance separate from simulator case IDs.
These are proxy predictions, not new simulator-confirmed realizations. Envelope coverage
and pairwise correlations do not prove exact joint matching or causal identifiability.

## Forecast and uncertainty

An average of recent own-case ln(WOR) trends and a pooled type curve extrapolates production.
Oil pore volume for optimized inputs uses the training-derived proportionality to porosity;
the supplied static summaries verify that relationship. No stock-tank recovery-factor claim
is made without a formation-volume conversion.

Each forecast starts at observed January 2008 totals. Trend coordinates are translated
to that cumulative state and anchored to the last observed WOR before integration.
The official base case keeps the last field liquid rate constant. Alternative liquid
declines are explicit scenarios. Oil/water quarterly increments are nonnegative and
conserve the chosen liquid volume. Static parameters and operating conditions do not change.

Hindcast type curves exclude each evaluation case and all dates after the cutoff.
Five-fold training hindcasts supply the method-discrepancy distribution. Validation and
test errors are assessments, not calibration samples. A hindcast using actual future
liquid rates isolates conditional WOR error; it is not an operational forecast of liquid.
Signed relative forecast error e is converted to an observed/predicted factor 1/(1+e).

Twenty thousand seeded scenarios vary optimized realization, liquid decline, WOR mixture
and method discrepancy. Realizations are equally weighted, not sampled from a Bayesian
posterior. P90/P50/P10 correspond to marginal 10th/50th/90th percentiles under these
assumptions. Marginal oil/water quantiles are not paired physical trajectories. Two-to-five-year
hindcast discrepancies do not establish twenty-year probability coverage.

## Verification and authorship

The notebook checks selection, bounds, case/time isolation, correction direction,
observed-state anchoring, phase conservation, percentile ordering and Excel round trips.
The separate verification script reloads the saved estimator in a new process and compares
its histories and all ten persisted workbook sheets with the dashboard table. Data-free
unit tests exercise the training views and numerical constraints without supplied workbooks.

Recorded run/version metadata and metrics accompany the outputs. The source notebook is
stored without execution outputs or private Colab identifiers; execution evidence is local.
Legacy reports, pre-edit snapshots, caches, supplied materials and environments are excluded
from Git. Development included OpenAI Codex assistance. Actual team contributions and
any additional submission declarations must describe the work performed rather than
attribute invented roles or claim unaided development.
