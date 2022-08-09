"""
Utils
"""


def parse_req_data(data):
    """
    Convert response data to node data
    """
    attr = {
        prop['name']: prop['value']
        for prop in data['props']
    }

    children = [sub_key['label'] for sub_key in data['sub_keys']]

    return {
        'attr': attr,
        'children': children
    }
