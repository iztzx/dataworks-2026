"""Execute a fresh kernel and preserve evidence without changing the source notebook."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    runtime = Path(tempfile.gettempdir()) / 'dwc26-jupyter-runtime'
    runtime.mkdir(exist_ok=True)
    os.environ['JUPYTER_RUNTIME_DIR'] = str(runtime)
    os.environ['IPYTHONDIR'] = str(runtime / 'ipython')
    os.environ['MPLCONFIGDIR'] = str(runtime / 'matplotlib')
    os.environ['DATAWORKS_ROOT'] = str(ROOT)
    for variable in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[variable] = '1'
    os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ['PATH']
    evidence = ROOT / 'outputs/review'
    evidence.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(ROOT / 'data works.ipynb', as_version=4)
    started = time.monotonic()
    cell_started = {}
    result = {'status': 'running', 'cells': len(notebook.cells),
              'executed_code_cells': 0, 'python': sys.version}
    status_path = evidence / 'execution.json'
    status_path.write_text(json.dumps(result, indent=2), encoding='utf-8')

    def cell_start(cell, cell_index, **_):
        if cell.cell_type == 'code':
            cell_started[cell_index] = time.monotonic()
            first = next((line for line in cell.source.splitlines() if line.strip()), '')
            print(f'START {cell_index}: {first[:110]}', flush=True)

    def cell_done(cell, cell_index, **_):
        if cell.cell_type == 'code':
            result['executed_code_cells'] += 1
            print(f'DONE  {cell_index}: {time.monotonic() - cell_started[cell_index]:.1f}s', flush=True)

    manager = KernelManager(kernel_name='python3')
    manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
    client = NotebookClient(notebook, km=manager, timeout=1800, iopub_timeout=180, allow_errors=False,
                            resources={'metadata': {'path': str(ROOT)}},
                            on_cell_start=cell_start, on_cell_executed=cell_done, record_timing=True)
    try:
        client.execute()
        nbformat.validate(notebook)
        result['status'] = 'passed'
        nbformat.write(notebook, evidence / 'executed_notebook.ipynb')
    except Exception as exc:
        result.update(status='failed', error_type=type(exc).__name__)
        raise
    finally:
        if manager.has_kernel:
            manager.shutdown_kernel(now=True)
        nbformat.write(notebook, evidence / 'execution_checkpoint.ipynb')
        result['elapsed_seconds'] = round(time.monotonic() - started, 2)
        status_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
