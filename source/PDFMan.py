from pathlib import Path
from datetime import datetime
import PyPDF2
import re
import my_log
# TODO analize pages
# TODO add some interactivity based on page size analizys
# TODO merge Pages


class PDFManipulator(object):
    def __init__(self, config):
        # Logging
        LOG_FILE = "my_app.log"
        self.my_logger = my_log.get_logger("PDF_Log", LOG_FILE)
        # App logic
        self.input_dir = Path(config['Paths']["input folder"])
        self.output_dir = Path(config['Paths']["output folder"])
        self.changes_dir = Path(config['Paths']["changes folder"])
        self.error_file = Path(config['Paths']["error file"])
        self.changes = self.analize_changes()

    def message(self, text):
        with open(self.error_file, "a") as f:
            m = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {text}"
            f.write("".join((m, "\n")))
        self.my_logger.info(text)

    def analize_changes(self):
        changing_pages = {}

        # Remove
        extract_file = self.changes_dir / "remove.txt"
        if extract_file.exists():
            remove_string = ""
            with open(extract_file) as f:
                remove_string = f.readline()[:-1]
            if remove_string:
                pages_to_del = self.decode_pagenum(remove_string)
                del_dict = {}
                for page in pages_to_del:
                    del_dict[page - 1] = {"path": None, "action": "delete", "rotate": 0}  # pages numeration starts with 0 in PyPDF2, but with 1 for users
                changing_pages.update(del_dict)
        if changing_pages:
            self.message("Так как найдены запросы на удаление страниц, запросы на добавление обработаны не будут")
            return changing_pages

        # Add and insert
        pages = self.changes_dir.glob("*.pdf")
        for page_path in pages:
            try:
                changing_pages.update(self.decode_name_append(page_path))
            except ValueError:
                self.message(f"Неправильный формат имени файла с изменениями: [{page_path.name}]. Он не будет обработан")
        if changing_pages:
            self.my_logger.debug(f'Pages [{", ".join([str(x) for x in changing_pages.keys()])}] will be changed')
        return changing_pages

    def decode_name_append(self, path: Path):
        """Decodes inserion document name and returns dictionary
        with page as its key and action dict as value

        Arguments:
            path {pathlib.Path} -- path to decode it`s name

        Returns:
            one record dict -- {page: {"path":, "action":, "rotate":}}
        """
        name = path.stem

        p = re.compile(r"[+]?\d+(r\d{3})?")
        if p.fullmatch(name).group(0) != name:
            raise ValueError("File name is not decodable", name)
        self.my_logger.debug(f'Decoding filename [{path.name}]')
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

        self.my_logger.debug(f'Operations with {name}: {operation}')
        return {int(name) - 1: operation}  # pages numeration starts with 0 in PyPDF2, but with 1 for users

    def decode_pagenum(self, page_string: str):
        """Decode Word-like page ranges into list

        Arguments:
            page_string {str} -- Word-like page string
        """
        PATTERNS = [
                        r"(^[123456789]\d* *- *[123456789]\d*$)",
                        r"(^[123456789]\d*$)"
                   ]

        compiled = [re.compile(p) for p in PATTERNS]

        _x = re.findall(r"[^\d\-, ]", page_string)
        if _x:  # string contains wrong characters
            self.message(f"Формат номеров страниц не распознан. В строке посторонние символы: {_x}")
            self.my_logger.debug(f"Wrong symbol in page range string [{page_string}]: {_x}")
            return []

        ranges = [x.strip() for x in page_string.split(",")]
        self.my_logger.debug(f'Page diaps [{ranges}]')
        pages = []

        for r in ranges:
            found = False
            for i, pattern in enumerate(compiled):
                finds = pattern.findall(r)
                if finds:
                    found = True
                    self.my_logger.debug(f"re founded: {pattern}: {finds}")
                    m = finds[0]
                    if i == 0:
                        start, end = [int(s) for s in m.split("-")]
                        if start >= end:
                            self.message(f"Формат номеров страниц не распознан. Диапазон страниц задан неверно: {m}")
                            return []
                        pages.extend(list(range(start, end + 1)))
                    elif i == 1:
                        pages.append(int(m))
            if not found:
                self.message(f"Формат номеров страниц не распознан: [{r}]")
                return []
        pages = list(set(pages))
        pages.sort()
        return pages

        """if p.match(name).group(0) != name:
            raise ValueError("File name is not decodable", name)
        ranges = page_string.split(",")
        pages = []
        for r in ranges:
            if "-" not in r:
                pages.append(int(r)"""

    def apply_changes(self, to_file: Path):
        with open(to_file, "rb") as pdf_file:
            pdfReader = PyPDF2.PdfFileReader(pdf_file)
            pdfWriter = PyPDF2.PdfFileWriter()
            p_num = pdfReader.getNumPages()
            self.my_logger.debug(f"Document {to_file.name} have {p_num} pages")
            opened_files = {}

            for e in self.changes:
                if e > p_num - 1:
                    if self.changes[e]["action"] == "add":
                        self.message(f"В документе [{to_file.name}] всего {p_num} страниц(ы) - вставка после {e + 1}-ой страницы из файла [{self.changes[e]['path'].name}] не выполнена")
                    elif self.changes[e]["action"] == "replace":
                        self.message(f"В документе [{to_file.name}] всего {p_num} страниц(ы) - {e + 1}-я страница не заменена на страницы из файла [{self.changes[e]['path'].name}]")
                    elif self.changes[e]["action"] == "remove":
                        self.message(f"В документе [{to_file.name}] всего {p_num} страниц(ы) - {e + 1}-я страница не удалена")
            for cur_page in range(p_num):
                if cur_page not in self.changes:
                    pdfWriter.addPage(pdfReader.getPage(cur_page))
                else:
                    action = self.changes[cur_page]
                    if action["action"] != "delete":
                        opened_files[cur_page] = open(action["path"], "rb")
                        if action["action"] == "add":
                            pdfWriter.addPage(pdfReader.getPage(cur_page))
                        change_reader = PyPDF2.PdfFileReader(opened_files[cur_page])
                        self.my_logger.debug(f'{change_reader.getNumPages()} pages in {action["path"].name} will be perfomed action {action["action"]} at page {cur_page}')
                        if action["rotate"] != 0:
                            self.my_logger.debug(f'They also will be rotated {action["rotate"]} degrees cw')
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

    def change_insert(self):
        try:
            if self.changes:
                files = False
                for p in self.input_dir.glob("*.pdf"):
                    files = True
                    self.my_logger.debug('--------------------------------------------------------')
                    self.my_logger.debug(f"Working on {p}")
                    if p.stem.endswith("_edited"):
                        self.my_logger.debug(f"Skipping already processed file {p}")
                        continue
                    self.apply_changes(p)
                if not files:
                    self.message("Исходные файлы отсуствуют")
                    self.my_logger.debug("No input files")
            else:
                self.message("Нет изменений для внесения в исходные файлы")
                self.my_logger.debug("No proper change files")
        except IOError as inst:
            self.message(str(type(inst)))
            self.message(str(inst.args))


'''
scan for input file;
scan for replacement pages;
make manipulations with checks
output file or Error.txt
'''
