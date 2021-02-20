#!/usr/bin/env python3

""" Automatic release """

import os
import sys

def get_new_version(version, current_version):
    """ Bump the version """
    if version in ('micro', 'minor', 'major'):
        version_parts = current_version.split('.')
        version_parts = [int(part) for part in version_parts]
        if version == 'micro':
            version_parts[2] += 1
        elif version == 'minor':
            version_parts[1] += 1
            version_parts[2] = 0
        elif version == 'major':
            version_parts[0] += 1
            version_parts[1] = 0
            version_parts[2] = 0
        version_parts = [str(part) for part in version_parts]
        return '.'.join(version_parts)

    return version

def release(version, auto_commit=False):
    """ Release """
    # change the version
    version_change = False
    with open('tchess/tchess.py', 'r') as f:
        new_content = ''
        for line in f.read().strip().splitlines():
            if line.startswith('VERSION = \'') and not version_change:
                current_version = line[11:][:-1]
                new_version = get_new_version(version=version, current_version=current_version)
                line = 'VERSION = \'' + new_version + '\''
                version_change = True
            new_content += line + '\n'
    f_w = open('tchess/tchess.py', 'w')
    f_w.write(new_content)
    f_w.close()

    os.system('make manpage')

    if auto_commit:
        os.system('git add -A')
        os.system('git commit -m ' + new_version)
        os.system('git tag ' + new_version)
    else:
        os.system('git diff')

if __name__ == '__main__':
    options = [arg for arg in sys.argv if arg.startswith('-')]
    args = [arg for arg in sys.argv if not arg.startswith('-')]
    if len(args) <= 1:
        args.append('micro')
    version = args[1]

    release(version, '--commit' in options)
