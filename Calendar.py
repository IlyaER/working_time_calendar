import calendar
import locale

import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4

#locale.setlocale(category=locale.LC_ALL, locale="Russian_Russia.1251")
#myCanvas = canvas.Canvas('myfile.pdf', pagesize=A4, bottomup=True)
#width, height = A4


class Calendar:
    def __init__(self, year):
        self.year = year




    def render(self):
        output = self.year
        pdf = canvas.Canvas('myfile.pdf', pagesize=A4, bottomup=False)
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        pdf.setFont('DejaVuSans', 14)
        # horizontal, vertical, text
        pdf.drawString(10, 20, "Календарь")
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


