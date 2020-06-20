from PDFMan import PDFManipulator
import app_conf


def main():
    man = PDFManipulator(app_conf.read_config())
    man.change_insert()


if __name__ == "__main__":
    main()

'''
scan for input file;
scan for replacement pages;
make manipulations with checks
output file or Error.txt
'''
