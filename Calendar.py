import calendar
import locale

import io

from reportlab.lib.colors import green, grey, black, red, Color, coral, crimson, darkred, HexColor
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
        self.font = 'CalibriB'
        self.font_size = 14
        self.locale = 'Russian_Russia'
        self.pdf = canvas.Canvas('myfile.pdf', pagesize=self.page_size, bottomup=False)

        self.cell_size = (self.width - self.left_margin - self.right_margin) / 31
        self.month_width = self.cell_size * 7 #  (self.width - self.left_margin - self.right_margin) / 31 * 7
        self.month_height = self.cell_size * 9  # (self.height - self.top_margin - self.bottom_margin)

        self.line_spacing = self.font_size * 1.2

        self.c = calendar.LocaleTextCalendar(locale=self.locale)

        # month, day, is_transferrable (defines if holiday is transferred when concurs with weekend),
        # name
        self.holidays = [(1, 1, 0, "Новогодние каникулы"), (1, 2, 0), (1, 3, 0), (1, 4, 0),
                         (1, 5, 0), (1, 6, 0), (1, 7, 0), (1, 8, 0),
                         (2, 23, 1), (3, 8, 1), (5, 1, 1), (5, 9, 1),
                         (6, 12, 1), (11, 4, 1)]

        self.weekends = set()

        self.holiday_transfer = [(2023, )]

    def is_holiday(self, day) -> Color:
        """
        Checks if a day is in holiday list and returns corresponding color for the day type.
        Returns black color if not.
        If it is a transferable holiday and concurs with a weekend, it marks next day as weekend.
        :param day:
        :return:
        """
        year_day, month_day, day, week_day = day
        if (month_day, day) in [(holiday[0], holiday[1]) for holiday in self.holidays if holiday[2]]:
            if week_day > 4:
                target_day = day + 1
                while (month_day, target_day) in self.weekends:
                    target_day += 1
                self.weekends.add((month_day, target_day))
                print(sorted(list(self.weekends)))
            return HexColor(0x990000)
        if (month_day, day) in self.weekends:
            return red
        return black

    def render_day(self, x: int, y: int, day: tuple, month: int):
        # (2023, 12, 30, 4)

        #year_day, month_day, day, week_day = day


        if day[1] != month:
            self.pdf.setFillColor(grey)
        else:
            color = self.is_holiday(day)
            self.pdf.setFillColor(color)
        self.pdf.drawRightString(x, y, str(day[2]))
        self.pdf.setFillColor(black)

    def render_week(self, x: int, y: int, month: int):
        for i in range(0, 7):
            if i > 4:
                self.pdf.setFillColor(red)
            else:
                self.pdf.setFillColor(black)
            self.pdf.drawCentredString(x + self.cell_size * i + self.cell_size / 2, y, calendar.day_abbr[i])
        y += self.cell_size
        for day in self.c.itermonthdays4(self.year, month):
            week_day = day[3]
            self.render_day(x + self.cell_size * (week_day + 1) - self.cell_size * 0.15, y, day, month)
            if week_day == 6:
                y += self.cell_size



    def render_month(self, x: int, y: int, month: int) -> None:
        print(f"Month start points: {x / mm, y / mm}")
        print(self.cell_size / mm, month)
        self.pdf.drawCentredString(x + self.month_width / 2, y, calendar.month_name[month])
        y += self.cell_size

        self.render_week(x, y, month)

    def render_year(self):
        y = self.top_margin
        self.pdf.drawCentredString(self.width / 2, y, f"Производственный календарь на {self.year} год")
        y += self.line_spacing * 2
        self.font_size = self.font_size - 2
        self.pdf.setFont(self.font, self.font_size)

        # there are 31 cell and 7 in every month in case 4 months per line plus 3 empty cells as border
        print(f"Month width: {self.month_width / mm}")
        print(f"Month height: {self.month_height / mm}")
        #y = self.top_margin + 16 * 2
        for i in range(12):
            month = i + 1
            # print(f"Месяц {i}, отступ вниз {i % 3}, отступ вбок {i // 3}")

            # populate weekends
            [self.weekends.add((day[1], day[2])) for day in self.c.itermonthdays4(self.year, month) if day[3] in (5, 6)]

            self.render_month(
                self.left_margin + (self.month_width + self.cell_size) * (i // 3),
                y + self.month_height * (i % 3),
                month
            )
            #self.pdf.drawString(self.left_margin + month_width * (i // 3), y + month_height * (i % 3), calendar.month_name[i + 1])


    def render(self):

        locale.setlocale(locale.LC_ALL, self.locale)



        #print(self.c.formatmonth(2023, 1))

        output = self.year
        # pdf = canvas.Canvas('myfile.pdf', pagesize=self.page_size, bottomup=False)
        # width, height = A4

        # width_mm = int(width/72*25.4)
        # print(width_mm)
        print(f"Page size: {self.width / mm, self.height / mm}")
        fonts = ("DejaVuSans", "Calibri", "CalibriB", "CalibriI", "CalibriL", "CalibriLI", "CalibriZ")
        for font in fonts:
            pdfmetrics.registerFont(TTFont(font, font+".ttf"))

        #self.pdf.setFont('DejaVuSans', self.font_size)
        self.pdf.setFont(self.font, self.font_size)
        # horizontal, vertical, text
        self.render_year()

        self.pdf.setFillColor(green)

        self.pdf.drawString(0.5*cm, 1 * cm, "Календарь")
        # pdf.drawRightString

        # not sure if that calculation is necessary
        #face = pdfmetrics.getFont('CalibriB').face
        #string_height = (face.ascent - face.descent) / 1000 * self.font_size
        #print(string_height)

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
        self.pdf.showPage()
        self.pdf.save()

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

    cal = Calendar(2023)
    cal.render()


