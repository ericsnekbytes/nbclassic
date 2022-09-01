"""Proof of concept for playwright testing, uses a reimplementation of test_execute_code"""

from playwright.sync_api import sync_playwright
from playwright.sync_api import Page, expect
import time

# TODO: Remove
# from .utils import shift, cmdtrl

def test_execute_code(notebook):
    # browser = notebook.browser
    # print(f"fixture notebook browser: {browser}")
    # def clear_outputs():
    #     return notebook.evaluate(
    #         "Jupyter.notebook.clear_all_output();")

    # Execute cell with Javascript API
    # print(f"Notebook: {dir(notebook)}")
    # print(f"Notebook page: {notebook.page}")
    page = notebook.page
    # print(f"page title is: {page.title()}")
    # print(f"Notebook index: {notebook.index}")
    # print(f"Notebook body: {notebook.body}")
    # print(f"Notebook cells: {notebook.cells}")
    # page_links = page.locator('a[target="_blank"]')
    
    page.pause()
    # Find the Notebook cell added 
    # notebook_a_tag = page.locator('.list_item')
    page.reload()
    notebook_a_tag = page.locator('a[href=\"http://localhost:8888/a@b/notebooks/Untitled.ipynb\"]')
    # page.pause()
    title = page.title()
    print(f"Title: {title}")
    notebook_a_tag = page.locator('#notebook_list > div:nth-child(4) > div > a')
    new_page = notebook_a_tag.click()
    print(f"new_page options: {dir(new_page)}")
    # page.pause()
    main_frame = page.main_frame
    print(f"main_frame: {main_frame}")
    # page.pause()

    frames = page.frames
    print(f"frames: {frames}")
    # page.pause()
    page.goto('http://localhost:8888/a@b/notebooks/Untitled.ipynb')
    # page.pause()
    new_title = page.title()
    print(f"New Title: {new_title}")
    # page.pause()

    # How to view list in notebook_a_tag???
    print(f"Page options: {dir(page)}")
    # page.pause()
    result = page.evaluate('Jupyter.notebook && Jupyter.notebook.kernel')
    # print(f"Result: {result}")
    # notebook_a_tag.element_handle()
    # print(f"notebook_a_tag inner_html: {notebook_a_tag.screenshot()}")
    # print(f"notebook_a_tag inner_text: {notebook_a_tag.inner_text()}")
    # print(f"notebook_a_tag text_content: {notebook_a_tag.text_content()}")
    # Click on the notebook cell
    # Update window handle to the notebook tab
    # print(f"Playwright driver page content: {playwright_driver.content()}")
    # notebook_handle = page.evaluate_handle("{window, document}")

    # First Catching here in edit_cell function
    notebook.edit_cell(index=0, content='a=10; print(a)')
    
    notebook.evaluate("Jupyter.notebook.get_cell(0).execute();")

    outputs = notebook.wait_for_cell_output(0)

    print(f"outputs is: {outputs}")
    page.pause()
    assert outputs.inner_text().strip() == '10'

# def wait_for_selector():
#     print('wait_for_selector')

# def wait_for_cell_text_output(notebook, index):
#     cell = notebook.cells[index]
#     output = wait_for_selector(cell, ".output_text", single=True)
#     return output.text


# def wait_for_kernel_ready(notebook):
#     wait_for_selector(notebook.browser, ".kernel_idle_icon")

# def test_first(prefill_notebook):
#     """Test that buffered requests execute in order."""
#     notebook = prefill_notebook(['', 'k=1', 'k+=1', 'k*=3', 'print(k)'])

#     # Repeated execution of cell queued up in the kernel executes
#     # each execution request in order.
#     wait_for_kernel_ready(notebook)
#     notebook.browser.execute_script("IPython.notebook.kernel.stop_channels();")
#     # k == 1
#     notebook.execute_cell(1)
#     # k == 2
#     notebook.execute_cell(2)
#     # k == 6
#     notebook.execute_cell(3)
#     # k == 7
#     notebook.execute_cell(2)
#     notebook.execute_cell(4)
#     notebook.browser.execute_script("IPython.notebook.kernel.reconnect();")
#     wait_for_kernel_ready(notebook)

#     # Check that current value of k is 7
#     assert wait_for_cell_text_output(notebook, 4) == "7"

