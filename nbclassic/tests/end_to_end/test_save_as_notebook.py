"""Test readonly notebook saved and renamed"""


from .utils import EDITOR_PAGE, TimeoutError as TestTimeout
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def save_as(nb):
    JS = '() => Jupyter.notebook.save_notebook_as()'
    return nb.evaluate(JS, page=EDITOR_PAGE)


def get_notebook_name(nb):
    JS = '() => Jupyter.notebook.notebook_name'
    return nb.evaluate(JS, page=EDITOR_PAGE)


def set_notebook_name(nb, name):
    JS = f'() => Jupyter.notebook.rename("{name}")'
    nb.evaluate(JS, page=EDITOR_PAGE)


def test_save_as_nb(notebook_frontend):
    print('[Test] [test_save_as_nb]')
    notebook_frontend.wait_for_kernel_ready()
    notebook_frontend.wait_for_selector(".input", page=EDITOR_PAGE)

    print('[Test] Set notebook name')
    print('/IMG/A/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
    set_notebook_name(notebook_frontend, name="nb1.ipynb")
    notebook_frontend.wait_for_condition(
        lambda: get_notebook_name(notebook_frontend) == 'nb1.ipynb',
        timeout=150,
        period=1
    )

    # Wait for Save As modal dialog
    print('[Test] Open save as dialog')
    print('/IMG/B/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
    save_as(notebook_frontend)
    notebook_frontend.wait_for_selector(".modal-footer", page=EDITOR_PAGE)
    dialog_element = notebook_frontend.locate(".modal-footer", page=EDITOR_PAGE)
    dialog_element.focus()

    # Get the dialog name input field element
    print('/IMG/C/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
    notebook_frontend.wait_for_selector('.modal-body .form-control', page=EDITOR_PAGE)
    name_input_element = notebook_frontend.locate('.modal-body .form-control', page=EDITOR_PAGE)
    name_input_element.focus()
    name_input_element.click()
    print('/IMG/D/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')

    # Make sure the save prompt is visible
    print('/IMG/E/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
    if not name_input_element.is_visible():
        print('/IMG/E2/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
        save_as(notebook_frontend)
        name_input_element.wait_for('visible')

    # Input a new name/path
    print('/IMG/F/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
    notebook_name = 'new_notebook.ipynb'
    notebook_frontend.wait_for_condition(
        lambda: name_input_element.evaluate(
            f'(elem) => {{ elem.value = "new_notebook.ipynb"; return elem.value; }}') == 'new_notebook.ipynb',
        timeout=150,
        period=.25
    )
    print('/IMG/G/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
    print('[Test] Name input field contents: ' + name_input_element.evaluate(f'(elem) => {{ return elem.value; }}'))

    print('[Test] Locate and click the save button')
    save_element = dialog_element.locate('text=Save')
    save_element.wait_for('visible')
    save_element.focus()
    save_element.click()
    print('/IMG/H/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')
    if save_element.is_visible():
        print('[Test] Save element still visible after save, wait for hidden')
        try:
            save_element.expect_not_to_be_visible(timeout=120)
        except PlaywrightTimeoutError as err:
            print('[Test]   Save button failed to hide...')
    print('/IMG/I/' + notebook_frontend._editor_page.screenshot().hex() + '/IMG/')

    # Check if the save operation succeeded (by checking notebook name change)
    print('[Test] Check notebook name')
    notebook_frontend.wait_for_condition(
        lambda: get_notebook_name(notebook_frontend) == notebook_name,
        timeout=120,
        period=5
    )

    print('[Test] Check notebook name in URL')
    notebook_frontend.wait_for_condition(
        lambda: notebook_name in notebook_frontend.get_page_url(page=EDITOR_PAGE),
        timeout=120,
        period=5
    )
