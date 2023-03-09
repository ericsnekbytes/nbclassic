"""Test navigation to directory links"""
import datetime
import os

from .utils import TREE_PAGE, EDITOR_PAGE
from jupyter_server.utils import url_path_join
pjoin = os.path.join


def url_in_tree(nb, url=None):
    if url is None:
        url = nb.get_page_url(page=TREE_PAGE)

    tree_url = url_path_join(nb.get_server_info(), 'tree')
    return True if tree_url in url else False


def get_list_items(nb):
    """
    Gets list items from a directory listing page
    """

    nb.wait_for_selector('#notebook_list .item_link', page=TREE_PAGE)
    link_items = nb.locate_all('#notebook_list .item_link', page=TREE_PAGE)

    results = []
    for item in link_items:
        print(f'             Found link item:')
        print(f'                 {item._bool}')
        print(f'                 {item._element}')
        if item:
            inner_text = item.get_inner_text()
            print(f'                 text: "{inner_text}"')
            if inner_text != '..':
                print(f'                 adding link to results')
                results.append({
                    'link': item.get_attribute('href'),
                    'label': inner_text,
                    'element': item,
                })
        else:
            print(f'                 invalid element!')

    return results
    # return [{
    #     'link': a.get_attribute('href'),
    #     'label': a.get_inner_text(),
    #     'element': a,
    # } for a in link_items if a and a.get_inner_text() != '..']


def test_navigation(notebook_frontend):
    print('[Test] [test_dashboard_nav] Start! y1')

    print('[Test] Obtain list of elements')
    link_elements = get_list_items(notebook_frontend)

    # Recursively traverse and check folder in the Jupyter root dir
    def check_links(nb, list_of_link_elements):
        print('[Test] Check links')
        print(f'[Test]   Time {datetime.datetime.now()}')
        if len(list_of_link_elements) < 1:
            return

        starting_parent_url = nb.get_page_url(page=TREE_PAGE)
        print(f'[Test]   Start URL at: "{starting_parent_url}"')
        for item in list_of_link_elements:
            print(f'[Test]   List item is "{item["label"]}"')
            if '.ipynb' in item["label"]:
                print(f'[Test]     Skipping non-dir notebook file')
                # Skip notebook files in the temp dir
                continue

            tries = 0
            def attempt_navigate():
                nonlocal tries
                tries += 1
                print(f'[Test]   Attempt #{tries} navigate/click item link')
                item["element"].click()

                # Wait for tree entry for this folder item to disappear,
                # signalling that the tree page links have changed (should
                # account for lag when clicking the link item, before the
                # new list of subdirs/files have been populated)...(we don't
                # have same-name folders in different subdirs for this
                # test so this approach is valid)
                print(f'[Test]   Wait for current item link to disappear from the list')
                notebook_frontend.wait_for_condition(
                    lambda: not notebook_frontend.locate(
                        f'#notebook_list .item_link >> text="{item["label"]}"',
                        page=EDITOR_PAGE).is_visible()
                )

                print(f'[Test]     Check URL in tree')
                nb.wait_for_condition(
                    lambda: url_in_tree(notebook_frontend),
                    timeout=60,
                    period=5
                )
                print(f'[Test]     Check URL matches link')
                print(f'[Test]       Item link: "{item["link"]}"')
                print(f'[Test]       Current URL is: "{nb.get_page_url(page=TREE_PAGE)}"')
                nb.wait_for_condition(
                    lambda: item["link"] in nb.get_page_url(page=TREE_PAGE),
                    timeout=60,
                    period=5
                )
                print(f'[Test]     Passed!')
                return True
            notebook_frontend.wait_for_condition(
                lambda: attempt_navigate(),
                timeout=360,
                period=1
            )

            print('[Test]     Obtain list items')
            print(f'[Test]       Page URL is {nb.get_page_url(page=TREE_PAGE)}')
            print(f'[Test]       Item label is {item["label"]}')
            print(f'[Test]       Item link is {item["link"]}')
            new_links = get_list_items(nb)
            if len(new_links) > 0:
                print(f'[Test]     Found ({len(new_links)}) new links')
                check_links(nb, new_links)

            print(f'[Test]   Go back to parent dir and wait for URL')
            nb.go_back(page=TREE_PAGE)
            nb.wait_for_condition(
                lambda: nb.get_page_url(page=TREE_PAGE) == starting_parent_url,
                timeout=300,
                period=5
            )

        return

    check_links(notebook_frontend, link_elements)
    print('[Test] [test_dashboard_nav] Finished!')
