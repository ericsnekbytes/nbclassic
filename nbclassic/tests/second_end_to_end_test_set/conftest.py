import os
import json
import sys
import time
from os.path import join as pjoin
from subprocess import Popen
from tempfile import mkstemp
from urllib.parse import urljoin

import pytest
import requests
from testpath.tempdir import TemporaryDirectory

import nbformat
from nbformat.v4 import new_notebook, new_code_cell
from .utils import NotebookFrontend

pjoin = os.path.join

def _wait_for_server(proc, info_file_path):
    """Wait 30 seconds for the notebook server to start"""
    for i in range(300):
        if proc.poll() is not None:
            raise RuntimeError("Notebook server failed to start")
        if os.path.exists(info_file_path):
            try:
                with open(info_file_path) as f:
                    return json.load(f)
            except ValueError:
                # If the server is halfway through writing the file, we may
                # get invalid JSON; it should be ready next iteration.
                pass
        time.sleep(0.1)
    raise RuntimeError("Didn't find %s in 30 seconds", info_file_path)


@pytest.fixture(scope='session')
def notebook_server():
    info = {}
    with TemporaryDirectory() as td:
        nbdir = info['nbdir'] = pjoin(td, 'notebooks')
        os.makedirs(pjoin(nbdir, 'sub ∂ir1', 'sub ∂ir 1a'))
        os.makedirs(pjoin(nbdir, 'sub ∂ir2', 'sub ∂ir 1b'))

        info['extra_env'] = {
            'JUPYTER_CONFIG_DIR': pjoin(td, 'jupyter_config'),
            'JUPYTER_RUNTIME_DIR': pjoin(td, 'jupyter_runtime'),
            'IPYTHONDIR': pjoin(td, 'ipython'),
        }
        env = os.environ.copy()
        env.update(info['extra_env'])

        command = [sys.executable, '-m', 'nbclassic',
                   '--no-browser',
                   '--notebook-dir', nbdir,
                   # run with a base URL that would be escaped,
                   # to test that we don't double-escape URLs
                   '--ServerApp.base_url=/a@b/',
                   ]
        print("command=", command)
        proc = info['popen'] = Popen(command, cwd=nbdir, env=env)
        info_file_path = pjoin(td, 'jupyter_runtime',
                               f'jpserver-{proc.pid:d}.json')
        info.update(_wait_for_server(proc, info_file_path))

        print("Notebook server info:", info)
        yield info

    # Shut the server down
    requests.post(urljoin(info['url'], 'api/shutdown'),
                  headers={'Authorization': 'token '+info['token']})

@pytest.fixture(scope='session')
def playwright_driver(playwright):
    # TODO: Fix
    # if os.environ.get('SAUCE_USERNAME'):
    #     driver = make_sauce_driver()
    if os.environ.get('JUPYTER_TEST_BROWSER') == 'chrome':
        driver = playwright.chromium.launch()
    else:
        driver = playwright.firefox.launch()
    driver = driver.new_context().new_page()
    print(f"Driver is: {driver}")
    yield driver
    # driver.close()

@pytest.fixture(scope='module')
def authenticated_browser(playwright_driver, notebook_server):
    playwright_driver.jupyter_server_info = notebook_server
    print(f"notebook_server: {notebook_server}")
    print(f"playwright_driver: {playwright_driver}")
    playwright_driver.goto("{url}?token={token}".format(**notebook_server))
    print(f"Authenticated_browser's playwright_driver: {playwright_driver}")
    return playwright_driver

@pytest.fixture
def notebook(authenticated_browser):
    tree_wh = authenticated_browser.evaluate_handle("Promise.resolve(window)")
    print(f'authenticated_browser is {authenticated_browser}')
    print(f"tree_wh: {tree_wh}")
    newnb = NotebookFrontend.new_notebook(authenticated_browser)
    print(f"NEWNB: {dir(newnb)}")
    print(f"NEWNB body: {newnb.body}")
    print(f"NEWNB cells: {newnb.cells}")
    print(f"NEWNB page: {newnb.page}")
    yield newnb
    
    # TODO: This and tree_wh are probably not needed so remove
    # authenticated_browser.contentFrame(tree_wh)

@pytest.fixture
def prefill_notebook(playwright_driver, notebook_server):
    def inner(cells):
        cells = [new_code_cell(c) if isinstance(c, str) else c
                 for c in cells]
        nb = new_notebook(cells=cells)
        fd, path = mkstemp(dir=notebook_server['nbdir'], suffix='.ipynb')
        with open(fd, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        fname = os.path.basename(path)
        playwright_driver.goto(
            "{url}notebooks/{}?token={token}".format(fname, **notebook_server)
        )
        return NotebookFrontend(playwright_driver)

    return inner

