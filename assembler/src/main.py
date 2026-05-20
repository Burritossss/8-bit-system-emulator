import sys

if len(sys.argv) < 2 or sys.argv[1] == '-h':#('-h' or '--help'):
    print('Usage:\n' \
    '\tpython3 main.py [options] [assembly file path] [binary output path]\n\n' \
    'Options:\n' \
    '\t-h\t\tDisplays this message')
