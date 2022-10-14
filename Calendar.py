import calendar
import locale

import io

from reportlab.lib.colors import green
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
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
        self.top_margin = 1*cm
        self.bottom_margin = 1*cm
        self.left_margin = 0.5*cm
        self.right_margin = 0.5*cm
        self.page_size = A4
        self.width, self.height = self.page_size
        self.font_size = 14

    def render(self):
        c = calendar.LocaleTextCalendar(locale='Russian_Russia')
        print(c.formatmonth(2023, 1, l=1))

        output = self.year
        pdf = canvas.Canvas('myfile.pdf', pagesize=self.page_size, bottomup=False)
        # width, height = A4

        # width_mm = int(width/72*25.4)
        # print(width_mm)
        print(self.width / mm, self.height / mm)
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdf.setFont('DejaVuSans', self.font_size)
        # horizontal, vertical, text
        pdf.drawCentredString(self.width / 2, 1*cm, f"Производственный календарь на {self.year} год")
        pdf.setFillColor(green)

        pdf.drawString(0.5*cm, 1 * cm, "Календарь")
        # pdf.drawRightString

        # not sure if that calculation is necessary
        face = pdfmetrics.getFont('DejaVuSans').face
        string_height = (face.ascent - face.descent) / 1000 * self.font_size
        print(string_height)
        # there are 31 cell and 7 in every month in case 4 months per line plus 3 empty cells as border
        cell_size = (self.width - self.left_margin - self.right_margin) / 31
        month_width = (self.width - self.left_margin - self.right_margin) / 31 * 7

        month_height = cell_size * 9 #(self.height - self.top_margin - self.bottom_margin)
        print(month_width / mm)
        print(month_height / mm)
        y = self.top_margin + 16 * 2
        for i in range(12):
            print(f"Месяц {i}, отступ вниз {i % 3}, отступ вбок {i // 3}")
            pdf.drawString(self.left_margin + month_width * (i // 4), y + month_height * (i % 3), "Месяц")

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
    c.render()


