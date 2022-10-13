import calendar
import locale

import io

from reportlab.lib.colors import green
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.units import inch, cm, mm
from reportlab.lib.pagesizes import letter, A4

#locale.setlocale(category=locale.LC_ALL, locale="Russian_Russia.1251")
#myCanvas = canvas.Canvas('myfile.pdf', pagesize=A4, bottomup=True)
#width, height = A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


class Calendar:
    def __init__(self, year):
        self.year = year
        self.top_margin = 1
        self.bottom_margin = 1
        self.left_margin = 0.5
        self.right_margin = 0.5



    def render(self):
        output = self.year
        pdf = canvas.Canvas('myfile.pdf', pagesize=A4, bottomup=False)
        width, height = A4

        # width_mm = int(width/72*25.4)
        # print(width_mm)
        print(width / mm, height / mm)
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdf.setFont('DejaVuSans', 14)
        # horizontal, vertical, text
        pdf.drawCentredString(width / 2, 1*cm, f"Производственный календарь на {self.year} год")
        pdf.setFillColor(green)
        pdf.drawString(0.5*cm, 1 * cm, "Календарь")

        # pdf.drawString(10, 20, "Календарь")  # , direction='RTL')
        # # one symbol's width is 9, space's is 4
        # # line space is 16
        # pdf.drawString(10, 40, "01")  # start from left
        # pdf.drawString(32, 40, "02")  # start from left on next row
        # pdf.drawString(10, 56, "01 02")
        # pdf.drawString(10, 72, "01002")
        # pdf.drawString(37, 88, "0")
        # pdf.drawString(19, 72, "1")  # start from right on next line
        # pdf.drawString(580, 20, "Календарь")


        #pdf.drawString(70, 770, "Календарь.")
        #for i, ingredient in enumerate(ingredients, 1):
        #    pdf.drawString(
        #        70,
        #        770 - i * 20,
        #        f"{i} "
        #        f"{ingredient['name']} "
        #        f"({ingredient['measurement_unit']}): "
        #        f"{ingredient['amount']}"
        #    )
        pdf.showPage()
        pdf.save()

        #return output
        #c = calendar.LocaleTextCalendar(locale='Russian_Russia')
        #print(c.formatmonth(2023, 1, l=1))
        #print(c.formatmonth(2023, 2))
        #for day in c.itermonthdates(2023, 1):
        #    if day.month == 1:
        #        print(day)
        #    else:
        #        print(str(day) + 'r')


if __name__ == '__main__':

    c = Calendar(2023)
    print(c.render())


