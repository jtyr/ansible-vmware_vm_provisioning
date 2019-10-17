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
                        'guest_disk_facts' in facts and
                        unit in facts['guest_disk_facts']):
                    # Replace whatever disk definition with the filename only
                    unit_facts = facts['guest_disk_facts'][unit]
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
            'modify_disks': modify_disks,
        }
