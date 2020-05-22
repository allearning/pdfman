from pathlib import Path
import PyPDF2
import logging
import re

logging.basicConfig(level=logging.DEBUG, format=' \
    %(asctime)s -  %(levelname)s -  %(message)s')

# TODO output logs to file

# TODO analize pages

# TODO add some interactivity based on page size analizys


class PDFManipulator(object):
    def __init__(self, config):
        self.input_dir = Path(config['Paths']["input folder"])
        self.output_dir = Path(config['Paths']["output folder"])
        self.changes_dir = Path(config['Paths']["changes folder"])
        self.error_file = Path(config['Paths']["error file"])
        self.changes = self.analize_changes()

    def analize_changes(self):
        changing_pages = {}
        pages = self.changes_dir.glob("*.pdf")
        for page_path in pages:
            try:
                changing_pages.update(self.decodename(page_path))
            except ValueError:
                with open(self.error_file, "a") as f:
                    f.writelines(f"Неправильный формат имени файла с изменениями: [{page_path.name}]. Он не будет обработан\n")
                    logging.debug(f"Change file {page_path.name} have wrong name format")
        if changing_pages:
            logging.debug(f'Pages [{", ".join([str(x) for x in changing_pages.keys()])}] will be changed')
        return changing_pages

    def decodename(self, path: Path):
        """Decodes inserion document name and returns dictionary
        with page as its key and action dict as value

        Arguments:
            path {pathlib.Path} -- path do decode it`s name

        Returns:
            dict -- {page: {"path":, "action":, "rotate":}}
        """
        name = path.stem
        p = re.compile("[+]?\d+(r\d{3})?")
        if p.match(name).group(0) != name:
            raise ValueError("File name is not decodable", name)
        logging.debug(f'Decoding filename [{path.name}]')
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
        return {int(name) - 1: operation} # pages numeration starts with 0 in PyPDF2, but with 1 for users

    def apply_changes(self, to_file: Path):
        with open(to_file, "rb") as pdf_file:
            pdfReader = PyPDF2.PdfFileReader(pdf_file)
            pdfWriter = PyPDF2.PdfFileWriter()
            p_num = pdfReader.getNumPages()
            logging.debug(f"Document {to_file.name} have {p_num} pages")
            opened_files = {}

            for e in self.changes:
                if e > p_num - 1:
                    with open(self.error_file, "a") as f:
                        if self.changes[e]["action"] == "add":
                            f.writelines(f"В документе [{to_file.name}] всего {p_num} страниц(ы) - вставка после {e + 1}-ой страницы из файла [{self.changes[e]['path'].name}] не выполнена\n")
                        else:
                            f.writelines(f"В документе [{to_file.name}] всего {p_num} страниц(ы) - {e + 1}-я страница не заменена на страницы из файла [{self.changes[e]['path'].name}]\n")

            for cur_page in range(p_num):
                if cur_page not in self.changes:
                    pdfWriter.addPage(pdfReader.getPage(cur_page))
                else:
                    opened_files[cur_page] = open(self.changes[cur_page]["path"], "rb")
                    action = self.changes[cur_page]

                    if action["action"] == "add":
                        pdfWriter.addPage(pdfReader.getPage(cur_page))
                    change_reader = PyPDF2.PdfFileReader(opened_files[cur_page])
                    logging.debug(f'{change_reader.getNumPages()} pages in {action["path"].name} will be perfomed action {action["action"]} at page {cur_page}')
                    if action["rotate"] != 0:
                        logging.debug(f'They also will be rotated {action["rotate"]} degrees cw')
                    for i in range(change_reader.getNumPages()):
                        page_obj = change_reader.getPage(i)
                        if action["rotate"] != 0:
                            page_obj.rotateClockwise(action["rotate"])
                        pdfWriter.addPage(page_obj)
            output_file = self.output_dir / "".join([to_file.stem, "_edited.pdf"])
            with open(output_file, "wb") as output:
                pdfWriter.write(output)
            for e in opened_files:
                opened_files[e].close()
        return pdfWriter

    def manipulate(self):
        try:
            if self.changes:
                for p in self.input_dir.glob("*.pdf"):
                    logging.debug('--------------------------------------------------------')
                    logging.debug(f"Working on {p}")
                    if p.stem.endswith("_edited"):
                        logging.debug(f"Skipping already processed file {p}")
                        continue
                    self.apply_changes(p)
                else:
                    with open(self.error_file, "a") as f:
                        f.writelines(f"Исходные файлы отсуствуют\n")
                        logging.debug(f"No input files")                       
            else:
                 with open(self.error_file, "a") as f:
                    f.writelines(f"Нет изменений для внесения в исходные файлы\n")
                    logging.debug(f"No proper change files")               
        except IOError as inst:
            with open(self.error_file, "a") as f:
                f.write(str(type(inst)))
                f.write(str(inst.args))


'''
scan for input file;
scan for replacement pages;
make manipulations with checks
output file or Error.txt
'''
