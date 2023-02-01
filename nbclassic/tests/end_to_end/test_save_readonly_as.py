"""Test readonly notebook saved and renamed"""


from .utils import EDITOR_PAGE


def save_as(nb):
    JS = '() => Jupyter.notebook.save_notebook_as()'
    return nb.evaluate(JS, page=EDITOR_PAGE)


def get_notebook_name(nb):
    JS = '() => Jupyter.notebook.notebook_name'
    return nb.evaluate(JS, page=EDITOR_PAGE)


def set_notebook_name(nb, name):
    JS = f'() => Jupyter.notebook.rename("{name}")'
    nb.evaluate(JS, page=EDITOR_PAGE)


def test_save_readonly_as(notebook_frontend):
    print('[Test] [test_save_readonly_as]')
    notebook_frontend.wait_for_kernel_ready()

    print('[Test] Make notebook read-only')
    cell_text = (
        'import os\nimport stat\nos.chmod("'
        + notebook_frontend.get_page_url(EDITOR_PAGE).split('?')[0].split('/')[-1]
        + '", stat.S_IREAD)\nprint(0)'
    )
    notebook_frontend.edit_cell(index=0, content=cell_text)
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_cell_contents(0).strip() == cell_text
    )
    notebook_frontend.evaluate("Jupyter.notebook.get_cell(0).execute();", page=EDITOR_PAGE)
    notebook_frontend.wait_for_cell_output(0)
    notebook_frontend.reload(EDITOR_PAGE)
    notebook_frontend.wait_for_kernel_ready()

    print('[Test] Check that the notebook is read-only')
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.evaluate('() => { return Jupyter.notebook.writable }', page=EDITOR_PAGE) is False,
        timeout=150,
        period=1
    )

    # Add some content
    test_content_0 = "print('a simple')\nprint('test script')"
    notebook_frontend.edit_cell(index=0, content=test_content_0)
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_cell_contents(0).strip() == test_content_0,
        timeout=150,
        period=1
    )

    # Wait for Save As modal dialog
    print('[Test] Open save as dialog')
    save_as(notebook_frontend)
    notebook_frontend.wait_for_selector(".modal-footer", page=EDITOR_PAGE)
    dialog_element = notebook_frontend.locate(".modal-footer", page=EDITOR_PAGE)
    dialog_element.focus()

    # Get the dialog name input field element
    notebook_frontend.wait_for_selector('.modal-body .form-control', page=EDITOR_PAGE)
    name_input_element = notebook_frontend.locate('.modal-body .form-control', page=EDITOR_PAGE)
    name_input_element.focus()
    name_input_element.click()

    # Input a new name/path
    notebook_name = 'writable_notebook.ipynb'
    notebook_frontend.wait_for_condition(
        lambda: name_input_element.evaluate(
            f'(elem) => {{ elem.value = "{notebook_name}"; return elem.value; }}'
        ) == notebook_name,
        timeout=150,
        period=.25
    )

    print('[Test] Locate and click the save button')
    save_element = dialog_element.locate('text=Save')
    save_element.wait_for('visible')
    save_element.focus()
    save_element.click()
    save_element.expect_not_to_be_visible(timeout=150)

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

    print('[Test] Check that the notebook is no longer read only')
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.evaluate('() => { return Jupyter.notebook.writable }', page=EDITOR_PAGE) is True,
        timeout=150,
        period=1
    )

    # Add some more content
    test_content_1 = "print('a second simple')\nprint('script to test save feature')"
    notebook_frontend.add_and_execute_cell(content=test_content_1)
    # and save the notebook
    notebook_frontend.evaluate("Jupyter.notebook.save_notebook()", page=EDITOR_PAGE)

    # Test that it still contains the content
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_cell_contents(index=0) == test_content_0,
        timeout=150,
        period=1
    )
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_cell_contents(index=1) == test_content_1,
        timeout=150,
        period=1
    )
    # even after a refresh
    notebook_frontend.reload(EDITOR_PAGE)
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_cell_contents(index=0) == test_content_0,
        timeout=150,
        period=1
    )
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_cell_contents(index=1) == test_content_1,
        timeout=150,
        period=1
    )
