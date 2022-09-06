"""Proof of concept for playwright testing, uses a reimplementation of test_execute_code"""

from playwright.sync_api import sync_playwright
from playwright.sync_api import Page, expect
import time

# TODO: Remove
# from .utils import shift, cmdtrl

def test_execute_code(notebook):
    page = notebook.page

    
    page.pause()
    page.reload()

    notebook_a_tag = page.locator('a[href=\"http://localhost:8888/a@b/notebooks/Untitled.ipynb\"]')
    # page.pause()
    title = page.title()

    notebook_a_tag = page.locator('#notebook_list > div:nth-child(4) > div > a')
    new_page = notebook_a_tag.click()

    # page.pause()
    main_frame = page.main_frame

    # page.pause()

    frames = page.frames
    # page.pause()
    page.goto('http://localhost:8888/a@b/notebooks/Untitled.ipynb')
    # page.pause()
    new_title = page.title()

    # page.pause()

    result = page.evaluate('Jupyter.notebook && Jupyter.notebook.kernel')

    # First Catching here in edit_cell function
    notebook.edit_cell(index=0, content='a=10; print(a)')
    
    notebook.evaluate("Jupyter.notebook.get_cell(0).execute();")

    outputs = notebook.wait_for_cell_output(0)

    page.pause()
    assert outputs.inner_text().strip() == '10'

