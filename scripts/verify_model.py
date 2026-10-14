"""Verify fresh-process model reload and persisted Excel/dashboard consistency."""
import ast
import json
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.decomposition import PCA
from sklearn.exceptions import InconsistentVersionWarning
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding='utf-8')
notebook = json.loads((ROOT / 'data works.ipynb').read_text(encoding='utf-8'))
for cell in notebook['cells']:
    if cell['cell_type'] != 'code' or 'class CurveProxy:' not in ''.join(cell['source']):
        continue
    tree = ast.parse(''.join(cell['source']))
    definition = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'CurveProxy')
    # The saved __main__.CurveProxy is defined by its supplied notebook source, not an unrelated stub.
    exec(compile(ast.Module(body=[definition], type_ignores=[]), '<CurveProxy from notebook>', 'exec'))
    break
else:
    raise RuntimeError('CurveProxy definition is missing.')

with warnings.catch_warnings():
    warnings.simplefilter('error', InconsistentVersionWarning)
    artifact = joblib.load(ROOT / 'outputs/models/curve_proxy.joblib')
assert artifact['package_versions']['scikit-learn'] == '1.6.1'
assert artifact['fit_cases'] == list(range(1, 86))
for fitted in artifact['proxy'].values():
    assert fitted.x_scaler.n_samples_seen_ == 85
    assert fitted.pca.n_samples_ == 85
    assert all(model.X_train_.shape[0] == 85 for model in fitted.models)
mapping = pd.read_csv(ROOT / 'outputs/selected_cases.csv')
histories = pd.read_csv(ROOT / 'outputs/production_history_and_forecast.csv', parse_dates=['date'])
for fluid in ['oil', 'water']:
    predicted = artifact['proxy'][fluid].predict(mapping[artifact['parameters']].to_numpy())
    for row_index, realization in enumerate(mapping['realization_id']):
        actual = histories.query("realization_id == @realization and period == 'history'").sort_values('date')
        assert np.allclose(predicted[row_index], actual[f'{fluid}_cumulative'], rtol=1e-12, atol=1e-6)

fluids = ['gas', 'oil', 'water']
observed = histories.query("source == 'observed' and period == 'history'").sort_values('date')
assert len(observed) == 41
observed_end = observed[[f'{fluid}_cumulative' for fluid in fluids]].iloc[-1].to_numpy()
headers = ['Gas production cumulative [MSCF]', 'Oil production cumulative [STB]',
           'Water production cumulative [STB]']
with pd.ExcelFile(ROOT / 'outputs/09 Template Deliverable.xlsx') as book:
    assert book.sheet_names == [f'Case {rank}' for rank in range(1, 11)]
    for row in mapping.itertuples(index=False):
        written = book.parse(row.sheet)
        assert written.columns[:4].to_list() == ['Date', *headers]
        official = histories.query("realization_id == @row.realization_id and source == 'anchored_field_forecast'").sort_values('date')
        assert len(official) == 81 and official['period'].iloc[0] == 'anchor'
        csv_columns = [f'{fluid}_cumulative' for fluid in fluids]
        assert np.allclose(official[csv_columns].iloc[0], observed_end, rtol=1e-12, atol=1e-6)
        future = official.query("period == 'forecast'")
        assert len(future) == len(written) == 80
        assert pd.DatetimeIndex(pd.to_datetime(written['Date'])).equals(pd.DatetimeIndex(future['date']))
        assert np.allclose(written[headers], future[csv_columns], rtol=1e-12, atol=1e-6)
        assert (official[csv_columns].diff().iloc[1:] >= -1e-6).all().all()
print('PASS: fresh-process model reload matches all 20 history curves without version warnings; '
      'all ten persisted Excel sheets match the dashboard forecasts and their observed starting points.')
