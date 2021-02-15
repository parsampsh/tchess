#!/usr/bin/env python3

import sys
import os

def main():
    """ Main cli """
    # generate the man page using help2man tool
    result = os.system('help2man "python3 tchess --verbose" --output=man/tchess.1')

    if result != 0:
        print("error: help2man is not installed")
        return 1

    # read the generated file
    f = open('man/tchess.1', 'r')
    content = f.read()
    f.close()

    # make the changes
    content = content.replace('python3 tchess --verbose', 'tchess')
    content = content.replace('PYTHON3 TCHESS --VERBOSE', 'TCHESS')
    content = content.replace('.PP', '.SH')
    content = content.replace('.IP', '')
    content = content.replace('.SH DESCRIPTION', '', 1)
    content = content.replace('.SH NAME', '.SH DESCRIPTION')
    content = content.replace('.SH DESCRIPTION', '.SH NAME', 1)
    content = content.replace('''.SH "SEE ALSO"
The full documentation for
.B tchess
is maintained as a Texinfo manual.  If the
.B info
and
.B tchess
programs are properly installed at your site, the command

.B info tchess
.SH
should give you access to the complete manual.''', '')
    content = '\n'.join([line for line in content.splitlines() if not line.strip().startswith('tchess \\- manual page for tchess ')])

    # write the file again
    f = open('man/tchess.1', 'w')
    f.write(content)
    f.close()

    print('Manual page was generated in `man/tchess.1`.')
    print('Run `man -l man/tchess.1` to see the generated manpage.')

if __name__ == '__main__':
    sys.exit(main())
