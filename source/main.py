from pathlib import Path
import PyPDF2
import logging
logging.basicConfig(level=logging.INFO, format=' %(asctime)s -  %(levelname)s -  %(message)s')

# TODO load config from file: in/out/pages/log folders

# TODO otput errors to file

# TODO output logs to file

# TODO analize pages

# TODO add some interactivity based on page size analizys


def decodename(path: Path):
    """Decodes inserion document name and returns dictionary
    with page as its key and action dict as value

    Arguments:
        path {pathlib.Path} -- path do decode it`s name

    Returns:
        dict -- {page: {"path":, "action":, "rotate":}}
    """
    name = path.stem
    logging.debug(f'Decoding name {name}')
    operation = {"rotate": 0}
    if "r" in name:
        name, angle = name.split("r")
        operation["rotate"] = int(angle)
    if name.startswith("+"):
        operation["action"] = "add"
        name = name[1:]
    else:
        operation["action"] = "replace"
    operation["path"] = path

    logging.debug(f'Operations with {name}: {operation}')
    return {int(name) - 1: operation}


def analize_changees():
    changing_pages = {}
    pages = Path("resources/pages")
    pages = pages.glob("*.pdf")
    for page_path in pages:
        changing_pages.update(decodename(page_path))
    logging.debug(f'{len(changing_pages)} changes at pages {", ".join([str(x) for x in changing_pages.keys()])}')
    return changing_pages


def do_actions(pdf_file_path, changing_pages):
    with open(pdf_file_path, "rb") as pdf_file:
        pdfReader = PyPDF2.PdfFileReader(pdf_file)
        pdfWriter = PyPDF2.PdfFileWriter()
        for e in changing_pages:
            changing_pages[e]["file"] = open(changing_pages[e]["path"], "rb")
        for cur_page in range(pdfReader.getNumPages()):
            if cur_page not in changing_pages:
                pdfWriter.addPage(pdfReader.getPage(cur_page))
            else:
                action = changing_pages[cur_page]

                if action["action"] == "add":
                    pdfWriter.addPage(pdfReader.getPage(cur_page))
                change_reader = PyPDF2.PdfFileReader(action["file"])
                logging.debug(f'{change_reader.getNumPages()} pages in change_reader of {action["path"].stem}')
                for i in range(change_reader.getNumPages()):
                    page_obj = change_reader.getPage(i)
                    if action["rotate"] != 0:
                        page_obj.rotateClockwise(action["rotate"])
                    pdfWriter.addPage(page_obj)
        with open(pdf_file_path.with_name("".join((pdf_file_path.stem, "_edited.pdf"))), "wb") as output:
            pdfWriter.write(output)
        for e in changing_pages:
            changing_pages[e]["file"].close()
    return pdfWriter


def main():
    pdfs = Path(".").resolve() / "resources"
    pdfs = pdfs.glob("*.pdf")
    try:
        actions = analize_changees()
        for p in pdfs:
            if p.stem.endswith("_edited"):
                continue
            do_actions(p, actions)

    except FileNotFoundError:
        with open("error.txt", "rw") as f:
            f.write("No")


if __name__ == "__main__":
    main()

'''
scan for input file;
scan for replacement pages;
make manipulations with checks
output file or Error.txt
'''
