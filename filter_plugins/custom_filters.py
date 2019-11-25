import re


NUMBERS = list(map(str, range(0, 10)))

# The same filter is in the `vmware_image_upload` role.
# If changing here, change it there as well.
def get_matching(data, path):
    """Search for matching field in a data structure using a path.

    Args:
        data (dict): Data structure.
        path (string): String describing the path to the matching field.
            The format of the string must be in dotted notation
            (e.g. networks.0.mac). Full path must exist in the `data`. The path
            can contain an extra notation in the following format:
                `{key[(==|=~)value]
            allowing to check for the existence of a key in a list of dicts and
            optionally compare the key value via string comparison or regexp.

    Return:
        dict: Matching field or `None`.
    """

    done = False

    for item in list(path.split('.')):
        if item[0] in NUMBERS:
            item = int(item)

        if isinstance(item, int):
            if isinstance(data, list) and len(data) > item:
                data = data[item]
            else:
                done = True
                break
        else:
            if item.startswith('{') and item.endswith('}'):
                if isinstance(data, list):
                    # Check if any item of the list contains dict with
                    # the key
                    tmp_list = []
                    expr = item[1:-1]

                    if '==' in expr:
                        expr_type = 'compare'
                        k, v = expr.split('==', 1)
                    elif '=~' in expr:
                        expr_type = 'regexp'
                        k, v = expr.split('=~', 1)
                    else:
                        expr_type = None
                        k = expr

                    for i in data:
                        if (
                                isinstance(i, dict) and ((
                                    expr_type == 'compare' and
                                    k in i and
                                    i[k] == v
                                ) or (
                                    expr_type == 'regexp' and
                                    k in i and
                                    re.search(v, i[k])
                                ) or (
                                    expr in i
                                ))):
                            tmp_list.append(i)

                    data = tmp_list
                else:
                    done = True
                    break
            elif item in data:
                data = data[item]
            else:
                done = True
                break

    if done:
        return
    else:
        return data


def enrich_vm(data, facts, add):
    """Enrich VM data sctructure with data from VM facts.

    Args:
        data (dict): VM data structure.
        facts (dict): VM facts.
        add (list): List of rules how to enrich the `data`.
            Each item must have the following keys:
                `src` - the path of the data in the `facts`
                `dest` - the path in `data` where to place the `sec` value
            Both paths must be in dotted notation (e.g. networks.0.mac).
            Full `src` path must exist and full `dest` path but the last
            element must exist in the datasctructure. The `src` path can
            contain an extra notation in the following format:
                `{key[(==|=~)value]
            allowing to check for the existence of a key in a list of dicts and
            optionally compare the key value via string comparison or regexp.

    Return:
        dict: Enriched data.
    """

    if (
            add is None or
            (isinstance(add, list) and len(add) == 0) or
            facts is None or
            'instance' not in facts):
        return data

    done = False

    for a in add:
        if 'src' in a and 'dest' in a:
            # Follow the src path and get the value
            src = facts['instance']
            src = get_matching(src, a['src'])

            # Break if src path wasn't found
            if src is None:
                break

            dest = data
            dest_list = list(a['dest'].split('.'))

            # Insert the value into the dest path
            for item in dest_list[:-1]:
                if item[0] in NUMBERS:
                    item = int(item)

                if isinstance(item, int):
                    if isinstance(dest, list) and len(dest) > item:
                        dest = dest[item]
                    else:
                        done = True
                        break
                else:
                    if item in dest:
                        dest = dest[item]

            # Break if dest path wasn't found
            if done:
                break

            # Get the last item in dest
            item = dest_list[-1]

            if item[0] in NUMBERS:
                item = int(item)

            # Assign value
            dest[item] = src

    return data


def modify_disks(data, state, facts, prefix='_'):
    """
    Replace disk definitions by filename from facts
    """

    if isinstance(data, list) and len(data) == len(facts):
        ret = []

        for i, disk in enumerate(data):
            record = {}

            if isinstance(disk, dict):
                userdata_key = '%suserdata' % prefix
                offset_key = '%soffset' % prefix
                offset = 0

                # Allow to offset disks
                # (Use negative/positive offset if another disk been
                # added/remofed in front of the disk)
                if offset_key in disk:
                    offset = int(disk[offset_key])

                unit = str(i + offset)

                if (
                        userdata_key in disk and
                        disk[userdata_key] is True and
                        facts is not None and
                        'guest_disk_info' in facts and
                        unit in facts['guest_disk_info']):
                    # Replace whatever disk definition with the filename only
                    unit_facts = facts['guest_disk_info'][unit]
                    record['filename'] = unit_facts['backing_filename']
                else:
                    for k, v in disk.items():
                        # Filtrer out all prefixed keys
                        if not k.startswith(prefix):
                            record[k] = v

                ret.append(record)
    else:
        ret = data

    return ret


class FilterModule(object):
    """Custom Jinja2 filters"""

    def filters(self):
        return {
            'enrich_vm': enrich_vm,
            'get_matching': get_matching,
            'modify_disks': modify_disks,
        }
