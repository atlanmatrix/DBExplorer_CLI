import sys

try:
    import readline
except ImportError:
    import pyreadline as readline

from exceptions import TFSBaseException
from core import TreeFS


def main():
    tfs = TreeFS()
    # global CMD
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tfs.cmd_completer)

    while True:
        try:
            cmd = input(tfs)
            if cmd == 'q':
                break

            res = tfs.parser(cmd)
            res and print(res)
        except TFSBaseException as e:
            print(e)
        except KeyboardInterrupt:
            print('bye')
            sys.exit()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
