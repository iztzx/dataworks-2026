# DataWorks Challenge 2026

Machine-learning-assisted reservoir history matching and twenty-year production forecasting.

The notebook learns a PCA/Gaussian-process proxy from supplied simulation cases, searches
for reservoir parameters that match the observed field history, and exports ten optimized
field forecasts through January 2028. Original simulator cases remain a separate benchmark.

## Run the project

Use Python 3.12. On Windows, from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.venv\Scripts\python.exe -u scripts\run_notebook.py
.venv\Scripts\python.exe scripts\verify_model.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`requirements-lock.txt` records the tested Windows environment; `requirements.txt` declares
the direct dependencies for other environments. Both require scikit-learn `1.6.1` to keep
saved estimators compatible. On macOS/Linux, use `.venv/bin/python` for the same commands.

For interactive use, open **data works.ipynb**, select the installed environment as its
kernel, and run cells from top to bottom. Colab setup is described at the top of the notebook.
Set `DATAWORKS_ROOT` or `PROJECT_ROOT_OVERRIDE` to use another project directory.

### Required data

Obtain the official workbooks through the authorized challenge distribution and place them
in `TestCases/` beside the notebook. Preserve their supplied filenames:

- `01 Introduction.xlsx`
- `02 Field Production.xlsx`
- The six grid workbooks with prefixes `03` through `08`, covering all 100 cases
- `09 Template Deliverable.xlsx`

Supplied workbooks and Kick Off materials are not included in Git. The first run builds
the local Parquet cache; subsequent runs reuse it. The full grid extraction can take
substantially longer than the approximately three-minute cached notebook execution.
No GPU is required.

The execution helper saves an executed notebook and timing evidence under `outputs/review/`
without replacing the clean source notebook. The saved model and exported results can be
checked with `scripts/verify_model.py` without the raw workbooks or caches.

## Repository contents

| Path | Purpose |
|---|---|
| `data works.ipynb` | Complete analysis, model training, optimization, forecast and verification |
| `scripts/run_notebook.py` | Execute the analysis from a fresh local kernel |
| `scripts/verify_model.py` | Reload the model in a new process and verify persisted outputs |
| `scripts/prepare_submission.py` | Remove notebook outputs and machine-specific metadata before committing |
| `tests/` | Data-free checks of training isolation, forecast constraints and notebook preparation |
| `docs/METHODOLOGY.md` | Evaluation protocol, provenance, assumptions and limitations |
| `outputs/models/curve_proxy.joblib` | Final oil/water proxies and fitting/version metadata |
| `outputs/09 Template Deliverable.xlsx` | Official ten-sheet forecast workbook |
| `outputs/selected_cases.csv` | Optimized realization parameters, mismatch and sheet mapping |
| `outputs/baseline_selected_cases.csv` | Original simulator benchmark identities |
| `outputs/production_history_and_forecast.csv` | Dashboard histories, anchored forecasts and marginal scenario percentiles |
| `outputs/hindcast_results.csv` | Auditable case/time separation and hindcast errors |
| Other tracked CSV/JSON outputs | Proxy metrics, uncertainty, residuals, production quantities and run evidence |

Each official sheet contains 80 quarterly dates, April 2008–January 2028, with cumulative
gas in MSCF and oil/water in STB. Optimized realizations have their own identifiers and
are not described as additional reservoir simulator runs. Dashboard proxy-history series
are separate from field forecasts; each field forecast has an observed January 2008 anchor.

## Evaluation and provenance

Production-response EDA uses the 70 training cases. Model-family comparison uses the
15 validation cases; proxy settings use five-fold cross-validation inside training.
The final proxy is fitted on cases 1–85, with test cases 86–100 excluded from fitting
and tuning. Forecast discrepancy calibration uses training-fold hindcasts only.

Earlier development notebooks had already inspected all cases and test diagnostics.
The reported test results are therefore a reserved-case assessment, **not a claim of a
prospectively blind test**. The code now keeps production-response exploration within
training, but cannot undo that earlier exposure. A separate unseen organizer dataset
would be needed for a genuinely fresh final assessment.

Development included assistance from OpenAI Codex for code, documentation and validation.
The repository records the actual methods and checks; it does not invent team contributions
or claim that the work was completed without such assistance.

## Results and limits

The generated outputs record a best optimized proxy mismatch of approximately **3.061%**.
The best provided parameters score approximately **3.232% under the same proxy**; the best
actual simulator case scores **3.207%**. These are historical matching objectives, not
twenty-year forecasting errors. Recent-history residuals are reported before anchoring.

Cached execution, all ten workbook sheets, fresh-process model reload, quarterly production
constraints and dashboard/export consistency have been checked. Uncached production-workbook
and grid Case 1 reads match the supplied caches. Live Colab execution and a complete uncached
grid extraction have not been repeated. See `docs/VALIDATION.md` for the validation record.

No production truth after January 2008 is supplied. Forecasts assume static rock properties,
unchanged operations and an explicit future liquid-rate scenario. P90/P50/P10 are conditional
scenario percentiles; their twenty-year statistical coverage has not been established.
Actual-future-liquid hindcasts are labelled conditional WOR diagnostics. Production quantities
are not a profitability assessment: prices, costs and capital spending are not supplied.

This is a private submission repository. Authorized reviewers need repository access.
PowerPoint, Power BI, video and any organizer-required archive/upload remain separate
submission items. The Kick Off specifies 16 October 2026 for code and 20 October 2026
for the other three deliverables.
