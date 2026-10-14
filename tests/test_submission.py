"""Data-free regression checks of the notebook's actual numerical helpers."""
import ast
import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from scripts.prepare_submission import clean_notebook

ROOT = Path(__file__).resolve().parents[1]


def notebook_function(name, **namespace):
    notebook = json.loads((ROOT / 'data works.ipynb').read_text(encoding='utf-8'))
    for cell in notebook['cells']:
        if cell['cell_type'] != 'code':
            continue
        source = ''.join(cell['source'])
        tree = ast.parse('\n'.join(line for line in source.splitlines() if not line.lstrip().startswith('%')))
        for definition in tree.body:
            if isinstance(definition, ast.FunctionDef) and definition.name == name:
                scope = {'np': np, 'pd': pd, **namespace}
                exec(compile(ast.Module(body=[definition], type_ignores=[]), '<notebook helper>', 'exec'), scope)
                return scope[name]
    raise AssertionError(f'Missing notebook function: {name}')


class SubmissionTests(unittest.TestCase):
    def test_training_exploration_ignores_held_out_production(self):
        view = notebook_function('training_eda_tables')
        params = pd.DataFrame({'split': ['train', 'validation', 'test']}, index=[1, 71, 86])
        columns = pd.MultiIndex.from_product([['oil', 'water', 'gas'], params.index], names=['fluid', 'case'])
        curves = pd.DataFrame(np.arange(27).reshape(3, 9), columns=columns)
        grids = pd.DataFrame({'oil_pore_volume': [10., 20., 30.]}, index=params.index)
        before = view(params, curves, curves, grids)
        changed = curves.copy()
        changed.loc[:, changed.columns.get_level_values('case') != 1] *= 1000
        after = view(params, changed, changed, grids)
        for first, second in zip(before, after):
            pd.testing.assert_frame_equal(first, second)
        self.assertEqual(before[0].index.to_list(), [1])
        self.assertEqual(set(before[1].columns.get_level_values('case')), {1})

    def test_positive_error_is_corrected_downward(self):
        factor = notebook_function('observed_to_predicted_factor')
        self.assertAlmostEqual(120.0 * float(factor(0.2)), 100.0)
        self.assertAlmostEqual(80.0 * float(factor(-0.2)), 100.0)
        for invalid in [-1., -2., np.nan, np.inf]:
            with self.assertRaises(ValueError):
                factor(invalid)

    def test_quarterly_phase_conservation_under_correction(self):
        start = pd.Series({'oil': 20., 'water': 40., 'gas': 7.})
        totals = notebook_function('field_totals', FIELD_START=start, FIELD_GOR=0.35)
        paths = totals(np.array([[8., 20., 20.], [12., 13., 40.]]), np.array([10., 20., 30.]))
        oil = paths['oil'] - start['oil']
        water = paths['water'] - start['water']
        np.testing.assert_allclose(oil + water, np.tile([10., 20., 30.], (2, 1)))
        self.assertTrue((np.diff(water, axis=-1, prepend=0) >= 0).all())
        np.testing.assert_allclose(oil[0], [8., 18., 18.])
        np.testing.assert_allclose(paths['gas'] - start['gas'], oil * 0.35)
        with self.assertRaises(ValueError):
            totals([1., 2.], [10., 9.])

    def test_anchor_translates_state_without_changing_slope(self):
        anchor = notebook_function('anchor_trend')
        trend = anchor(lambda cumulative: 0.01 * cumulative, 100., 80., np.log(2.))
        self.assertAlmostEqual(trend(80.), np.log(2.))
        self.assertAlmostEqual(trend(90.) - trend(80.), 0.1)

    def test_notebook_preparation_is_nonmutating_and_idempotent(self):
        notebook = {'metadata': {'colab': {'mount_file_id': 'private-id'}, 'kernelspec': {'name': 'python3'}},
                    'cells': [{'cell_type': 'code', 'metadata': {'execution': 'local'}, 'source': ['print(1)'],
                               'execution_count': 1, 'outputs': [{'text': 'local path'}]}]}
        cleaned = clean_notebook(notebook)
        self.assertEqual(cleaned, clean_notebook(cleaned))
        self.assertEqual(cleaned['cells'][0]['source'], notebook['cells'][0]['source'])
        self.assertEqual(cleaned['cells'][0]['outputs'], [])
        self.assertNotIn('colab', cleaned['metadata'])
        self.assertEqual(notebook['cells'][0]['execution_count'], 1)


if __name__ == '__main__':
    unittest.main()
