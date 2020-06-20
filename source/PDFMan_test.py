import re
from PDFMan import PDFManipulator

test = "1, 2, 3, 6, 15-5-5-1, 19"
if re.search("[^\d\-, ]", test):
    print("BAD STRING")
else:
    print("GOOD STRING")
p = re.compile("([123456789]\d*-[123456789]\d*)|([123456789]\d*)")
p2 = re.compile("([123456789]\d* *- *[123456789]\d*)|([123456789]\d*)")
p.findall
x = p.findall(test)
x2 = p2.findall(test)
print(x, "\n", x2)
print(PDFManipulator.decode_pagenum(test))