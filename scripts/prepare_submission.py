"""Keep the tracked notebook portable while preserving executed evidence locally."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def clean_notebook(notebook):
    result = copy.deepcopy(notebook)
    result['metadata'] = {
        key: value for key, value in result.get('metadata', {}).items()
        if key in ('kernelspec', 'language_info')
    }
    for cell in result['cells']:
        cell['metadata'] = {}
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    return result


def main():
    path = ROOT / 'data works.ipynb'
    notebook = json.loads(path.read_text(encoding='utf-8'))
    if any(cell.get('outputs') for cell in notebook['cells']):
        evidence = ROOT / 'outputs/review'
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / 'executed_before_preparation.ipynb').write_bytes(path.read_bytes())
    path.write_text(json.dumps(clean_notebook(notebook), ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('Prepared source notebook: outputs and machine-specific metadata removed.')


if __name__ == '__main__':
    main()
