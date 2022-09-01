import datetime
import os
import time
# import asyncio
from contextlib import contextmanager
from os.path import join as pjoin
# import nest_asyncio
# nest_asyncio.apply()
from playwright.sync_api import Page, expect

class CellTypeError(ValueError):

    def __init__(self, message=""):
        self.message = message
        
class NotebookFrontend:

    def __init__(self, page: Page):
        self.page = page
        self._wait_for_start()
        self.disable_autosave_and_onbeforeunload()

    def __len__(self):
        return len(self.cells)

    def __getitem__(self, key):
        return self.cells[key]

    def __setitem__(self, key, item):
        if isinstance(key, int):
            self.edit_cell(index=key, content=item, render=False)

    def __iter__(self):
        return (cell for cell in self.cells)

    def _wait_for_start(self):
        """Wait until the notebook interface is loaded and the kernel started"""
        # wait_for_selector(self.browser, '.cell')
        self.page.on('domcontentloaded', lambda Jupyter: print(f"DOMContentLoaded event emitted and Jupyter is: {Jupyter}"))
        
        # locator = self.page.locator('.cell')
        # print(f"loaded is {locator}")
        # # TODO: Refactor/fix
        # running = self.is_kernel_running()
        # print(f"running is {running}")
        # if not running:
        #     print(self.is_kernel_running())
        # else:
        #     print('kernel was running')
        
    @property
    def body(self):
        return self.page.locator("body")

    @property
    def cells(self):
        """Gets all cells once they are visible.

        """
        return self.page.query_selector_all(".cell")

    @property
    def current_index(self):
        return self.index(self.current_cell)

    def index(self, cell):
        return self.cells.index(cell)

    # TODO: Do we need to wrap in an anonymous function?
    def evaluate(self, text):
       return self.page.evaluate(text)

    async def disable_autosave_and_onbeforeunload(self):
        """Disable request to save before closing window and autosave.

        This is most easily done by using js directly.
        """
        self.page.evaluate("() => { window.onbeforeunload = null; }")
        result = await self.page.evaluate("() => { Jupyter.notebook.set_autosave_interval(0) }")
        print(f"result from Jupyter.notebook: {result}")
        # self.page.evaluate("() => console.log(Jupyter.notebook)")
        # self.page.evaluate("Jupyter.notebook.set_autosave_interval(0)")

    def to_command_mode(self):
        """Changes us into command mode on currently focused cell"""
        self.body.press('Escape')
        self.evaluate("() => { return Jupyter.notebook.handle_command_mode("
                                    "Jupyter.notebook.get_cell("
                                        "Jupyter.notebook.get_edit_index()))}")


    def focus_cell(self, index=0):
        # self.evaluate('Jupyter.notebook.save_notebook(false)')
        self.page.pause()
        # self.page.reload()
        # all_cells = self.page.query_selector_all('.cell')
        # print(f"all_cells length- {len(all_cells)} ::: all_cells- {all_cells}")
        # cell = self.page.query_selector_all('.cell')[0]
        # print(f"Cells found: {cell}")
        print(f"cell length- {len(self.cells)} ::: cells- {self.cells}")
        cell = self.cells[index]
       
        self.page.pause()
        # print(self)
        #---------------------------------
        # Third catch here, cell is an empty list so no property click is found
        cell.click()
        #---------------------------------
        self.to_command_mode()
        #---------------------------------
        self.current_cell = cell
    
    def get_cell_output(self, index=0, output='.output_subarea'):
        return self.cells[index].as_element().query_selector(output)  # Find cell child elements

    def wait_for_cell_output(self, index=0, timeout=10):
    # return WebDriverWait(self.browser, timeout).until(
    #     lambda b: self.get_cell_output(index)
    # )
        return self.get_cell_output()

    def edit_cell(self, cell=None, index=0, content="", render=False):
        """Set the contents of a cell to *content*, by cell object or by index
        """
        if cell is not None:
            index = self.index(cell)

        # locate_cell = page.locator(".inner_cell")
        time.sleep(3)
        #---------------------------------   
        # Second catch in focus_cell 
        self.focus_cell(index)
        #---------------------------------
        print(f"self.current_cell is: {self.current_cell}")
        print(f"self.cell is: {dir(self)}")
        # Select & delete anything already in the cell
        #---------------------------------
        self.current_cell.press('Enter')
        #---------------------------------
        cmdtrl(self.page, 'a')  # TODO: FIX
        #---------------------------------
        self.current_cell.press('Delete')
        #---------------------------------


        for line_no, line in enumerate(content.splitlines()):
            if line_no != 0:
                self.page.keyboard.press("Enter")
            self.page.keyboard.press("Enter")
            self.page.keyboard.type(line)
        if render:
            self.execute_cell(self.current_index)

    def execute_cell(self, cell_or_index=None):
        if isinstance(cell_or_index, int):
            index = cell_or_index
        elif isinstance(cell_or_index, ElementHandle):
            index = self.index(cell_or_index)
        else:
            raise TypeError("execute_cell only accepts an ElementHandle or an int")
        self.focus_cell(index)
        self.current_cell.press("Control+Enter")

    def is_kernel_running(self):
        # Determine if kernel is running here
        # print(f"self.page: {dir(self.page)}")
        # result = self.page.evaluate("Promise.resolve(window.Jupyter)")
        time.sleep(120)
        result = self.page.evaluate("console.log(Jupyter.notebook.kernel && Jupyter.notebook.kernel.is_connected())")
        print(f"result: {result}")

    @classmethod
    def new_notebook(cls, page, kernel_name='kernel-python3'):
        # with new_window(page):
        print(f'cls: {cls}')
        print(f'page: {page}')
        print(f'kernel_name: {kernel_name}')
        print(f'calling select_kernel now')
        # TO ADD THESE FUNCTIONS
        select_kernel(page, kernel_name=kernel_name)
        # notebook = cls(page)
        # print(f"notebook {notebook}")
        # return notebook
        return cls(page)
    
def select_kernel(page, kernel_name='kernel-python3'):
    """Clicks the "new" button and selects a kernel from the options.
    """
    # wait = WebDriverWait(browser, 10)
    # new_button = wait.until(EC.element_to_be_clickable((By.ID, "new-dropdown-button")))
    new_button = page.locator('#new-dropdown-button')
    new_button.click()
    kernel_selector = f'#{kernel_name} a'
    # kernel = wait_for_selector(page, kernel_selector, single=True)
    kernel = page.locator(kernel_selector)
    kernel.click()

def cmdtrl(page, key):
    """Send key combination Ctrl+(key) or Command+(key) for MacOS"""
    print(f"@@@@ key: {key}")
    if os.uname()[0] == "Darwin":
        page.keyboard.press("Meta+{}".format(key))
    else:
        page.keyboard.press("Control+{}".format(key))

