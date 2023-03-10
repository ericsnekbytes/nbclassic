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


def navigate_to_link(nb, item_text):
    notebook_frontend = nb

    print(f'[Test]   Now navigating to "{item_text}"')
    def get_matches():
        tree_page_items = [item for item in notebook_frontend.locate_all('#notebook_list .item_link', TREE_PAGE)]
        print(f'     Attempt to find matches...')
        for elem in tree_page_items:
            print(f'       {elem._element}')
            if elem.is_visible():
                print(f'         {elem.get_inner_text()}')
        return [elem for elem in tree_page_items if elem.is_visible() and elem.get_inner_text().strip() == item_text]
    matches = notebook_frontend.wait_for_condition(
        lambda: get_matches(),
        period=3
    )
    target_element = matches[0]
    target_link = target_element.get_attribute("href")
    target_element.click()
    notebook_frontend.wait_for_condition(
        lambda: not notebook_frontend.locate(
            f'#notebook_list .item_link >> text="{item_text}"',
            page=EDITOR_PAGE).is_visible()
    )
    print(f'[Test]     Check URL in tree')
    notebook_frontend.wait_for_condition(
        lambda: url_in_tree(notebook_frontend),
        timeout=60,
        period=5
    )
    print(f'[Test]     Check URL matches link')
    print(f'[Test]       Item link: "{target_link}"')
    print(f'[Test]       Current URL is: "{notebook_frontend.get_page_url(page=TREE_PAGE)}"')
    notebook_frontend.wait_for_condition(
        lambda: target_link in notebook_frontend.get_page_url(page=TREE_PAGE),
        timeout=60,
        period=5
    )
    print(f'[Test]     Passed!')
    return notebook_frontend.get_page_url(page=TREE_PAGE)


def test_navigation(notebook_frontend):
    print('[Test] [test_dashboard_nav] Start! y2')

    # NOTE the paths here are determined by X

    # os.makedirs(pjoin(nbdir, 'sub ∂ir1', 'sub ∂ir 1a'))
    # os.makedirs(pjoin(nbdir, 'sub ∂ir2', 'sub ∂ir 1b'))
    SUBDIR1 = 'sub ∂ir1'
    SUBDIR2 = 'sub ∂ir2'
    SUBDIR1A = 'sub ∂ir 1a'
    SUBDIR1B = 'sub ∂ir 1b'

    # Start at the root (tree) URL
    print(f'[Test] Start at tree (root) URL')
    tree_url = notebook_frontend.get_page_url(page=TREE_PAGE)
    print(f'[Test]   URL is now at "{tree_url}"')

    # Test navigation to first folder in root
    print(f'[Test] Navigate to subdir1')
    subdir1_url = navigate_to_link(notebook_frontend, SUBDIR1)
    print(f'[Test]   URL is now at "{subdir1_url}"')

    # Test navigation to first subfolder
    print(f'[Test] Navigate to subdir1a')
    subdir1a_url = navigate_to_link(notebook_frontend, SUBDIR1A)
    print(f'[Test]   URL is now at "{subdir1a_url}"')
    notebook_frontend.go_back(page=TREE_PAGE)
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_page_url(page=TREE_PAGE) == subdir1_url,
        timeout=300,
        period=5
    )
    notebook_frontend.go_back(page=TREE_PAGE)
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_page_url(page=TREE_PAGE) == tree_url,
        timeout=300,
        period=5
    )
    notebook_frontend.wait_for_condition(
        lambda: not notebook_frontend.locate(
            f'#notebook_list .item_link >> text="{SUBDIR1A}"',
            page=EDITOR_PAGE).is_visible()
    )

    # Test navigation to second folder from root
    print(f'[Test] Navigate to subdir2')
    subdir2_url = navigate_to_link(notebook_frontend, SUBDIR2)
    print(f'[Test]   URL is now at "{subdir2_url}"')
    notebook_frontend.wait_for_condition(
        lambda: not notebook_frontend.locate(
            f'#notebook_list .item_link >> text="{SUBDIR2}"',
            page=EDITOR_PAGE).is_visible()
    )

    # Test navigation to second subfolder
    print(f'[Test] Navigate to subdir1b')
    subdir1b_url = navigate_to_link(notebook_frontend, SUBDIR1B)
    print(f'[Test]   URL is now at "{subdir1b_url}"')
    notebook_frontend.go_back(page=TREE_PAGE)
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_page_url(page=TREE_PAGE) == subdir2_url,
        timeout=300,
        period=5
    )
    notebook_frontend.go_back(page=TREE_PAGE)
    notebook_frontend.wait_for_condition(
        lambda: notebook_frontend.get_page_url(page=TREE_PAGE) == tree_url,
        timeout=300,
        period=5
    )

    print('[Test] [test_dashboard_nav] Finished!')

    # # Recursively traverse and check folder in the Jupyter root dir
    # def check_links(nb, list_of_link_elements):
    #     print('[Test] Check links')
    #     print(f'[Test]   Time {datetime.datetime.now()}')
    #     if len(list_of_link_elements) < 1:
    #         return
    #
    #     starting_parent_url = nb.get_page_url(page=TREE_PAGE)
    #     print(f'[Test]   Start URL at: "{starting_parent_url}"')
    #     for item in list_of_link_elements:
    #         print(f'[Test]   List item is "{item["label"]}"')
    #         if '.ipynb' in item["label"]:
    #             print(f'[Test]     Skipping non-dir notebook file')
    #             # Skip notebook files in the temp dir
    #             continue
    #
    #         tries = 0
    #         def attempt_navigate():
    #             nonlocal tries
    #             tries += 1
    #             print(f'[Test]   Attempt #{tries} navigate/click item link')
    #             item["element"].click()
    #
    #             # Wait for tree entry for this folder item to disappear,
    #             # signalling that the tree page links have changed (should
    #             # account for lag when clicking the link item, before the
    #             # new list of subdirs/files have been populated)...(we don't
    #             # have same-name folders in different subdirs for this
    #             # test so this approach is valid)
    #             print(f'[Test]   Wait for current item link to disappear from the list')
    #             notebook_frontend.wait_for_condition(
    #                 lambda: not notebook_frontend.locate(
    #                     f'#notebook_list .item_link >> text="{item["label"]}"',
    #                     page=EDITOR_PAGE).is_visible()
    #             )
    #
    #             print(f'[Test]     Check URL in tree')
    #             nb.wait_for_condition(
    #                 lambda: url_in_tree(notebook_frontend),
    #                 timeout=60,
    #                 period=5
    #             )
    #             print(f'[Test]     Check URL matches link')
    #             print(f'[Test]       Item link: "{item["link"]}"')
    #             print(f'[Test]       Current URL is: "{nb.get_page_url(page=TREE_PAGE)}"')
    #             nb.wait_for_condition(
    #                 lambda: item["link"] in nb.get_page_url(page=TREE_PAGE),
    #                 timeout=60,
    #                 period=5
    #             )
    #             print(f'[Test]     Passed!')
    #             return True
    #         notebook_frontend.wait_for_condition(
    #             lambda: attempt_navigate(),
    #             timeout=360,
    #             period=1
    #         )
    #
    #         print('[Test]     Obtain list items')
    #         print(f'[Test]       Page URL is {nb.get_page_url(page=TREE_PAGE)}')
    #         print(f'[Test]       Item label is {item["label"]}')
    #         print(f'[Test]       Item link is {item["link"]}')
    #         new_links = get_list_items(nb)
    #         if len(new_links) > 0:
    #             print(f'[Test]     Found ({len(new_links)}) new links')
    #             check_links(nb, new_links)
    #
    #         print(f'[Test]   Go back to parent dir and wait for URL')
    #         nb.go_back(page=TREE_PAGE)
    #         nb.wait_for_condition(
    #             lambda: nb.get_page_url(page=TREE_PAGE) == starting_parent_url,
    #             timeout=300,
    #             period=5
    #         )
    #
    #     return
    #
    # check_links(notebook_frontend, link_elements)
    # print('[Test] [test_dashboard_nav] Finished!')
