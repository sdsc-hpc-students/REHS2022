import argparse

parser = argparse.ArgumentParser(description='x')
parser.add_argument('command', help='helper')
parser.add_argument('-f', '--foo', help='helper')

args = parser.parse_args('zugma -f foobar'.split(' '))
print(vars(args))