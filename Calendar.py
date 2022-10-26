import calendar
import io
import locale
import datetime

from reportlab.lib.colors import (Color, HexColor, black, coral, crimson,
                                  darkred, green, grey, red, lightgrey)
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


class Cell:
    def __init__(self, width, height):
        self.width = width
        self.height = height


class Holiday:
    def __init__(self, date: list, is_transferable: bool, name: str):
        self.date = date
        self.is_transferable = is_transferable
        self.name = name

    def __repr__(self):
        return (f"{self.__class__.__qualname__}"
                f"({self.date}, "
                f"{self.is_transferable}, "
                f"{self.name})")


class Calendar:
    def __init__(self, year):
        self.year = year
        self.top_margin = 1 * cm
        self.bottom_margin = 1 * cm
        self.left_margin = 0.5 * cm
        self.right_margin = 0.5 * cm
        self.page_size = A4
        self.width, self.height = self.page_size
        self.font = 'CalibriB'
        self.font_size = 14
        self.locale = 'Russian_Russia'
        self.pdf = canvas.Canvas('myfile.pdf', pagesize=self.page_size, bottomup=False)

        self.cell_size = Cell(
            (self.width - self.left_margin - self.right_margin) / 31,
            (self.width - self.left_margin - self.right_margin) / 31 * 0.9
        )
        self.month_width = self.cell_size.width * 7  # (self.width - self.left_margin - self.right_margin) / 31 * 7
        self.month_height = self.cell_size.height * 9  # (self.height - self.top_margin - self.bottom_margin)

        self.line_spacing = self.font_size * 1.2

        self.c = calendar.LocaleTextCalendar(locale=self.locale)

        # month, day, is_transferrable (defines if holiday is transferred when concurs with weekend),
        # name
        self.holidays = [["1-1", 0, "Новогодние каникулы"], ["1-2", 0, "Новогодние каникулы"],
                         ["1-3", 0, "Новогодние каникулы"], ["1-4", 0, "Новогодние каникулы"],
                         ["1-5", 0, "Новогодние каникулы"], ["1-6", 0, "Новогодние каникулы"],
                         ["1-7", 0, "Рождество Христово"], ["1-8", 0, "Новогодние каникулы"],
                         ["2-23", 1, "День защитника Отечества"], ["3-8", 1, "Международный женский день"],
                         ["5-1", 1, "Праздник Весны и Труда"], ["5-9", 1, "День Победы"],
                         ["6-12", 1, "День России"], ["11-4", 1, "День народного единства"]]

        self.weekends = set()

        self.shortened_work_day = set()

        self.weekend_transfer = [["2023-1-1", "2023-2-24"], ["2023-1-8", "2023-5-8"]]

    def is_special_day(self, day) -> Color:
        """
        Checks if a day is in holiday, weekend or shortened work day lists and returns
        corresponding color for the day type.
        Returns black color if not.

        :param day:
        :return:
        """
        #year_day, month_day, day, week_day = day
        #if (day.month, day.day) in [(holiday[0], holiday[1]) for holiday in self.holidays]:
        #print(day)
        #print([self.holidays[0].date])

        # search in list of lists
        if day in [date for holiday in self.holidays for date in holiday.date]:
            return HexColor(0x990000)
        if day in self.weekends:
            return red
        if day in self.shortened_work_day:
            return green
        return black

    def render_day(self, x: int, y: int, day: tuple, month: int):
        # (2023, 12, 30, 4)

        # year_day, month_day, day, week_day = day

        if day.month != month:
            self.pdf.setFillColor(lightgrey)
        else:
            color = self.is_special_day(day)
            self.pdf.setFillColor(color)
        self.pdf.drawRightString(x, y, str(day.day))
        self.pdf.setFillColor(black)

    def render_week(self, x: int, y: int, month: int):
        for i in range(0, 7):
            if i > 4:
                self.pdf.setFillColor(red)
            else:
                self.pdf.setFillColor(black)
            #self.pdf.drawCentredString(x + self.cell_size * i + self.cell_size / 2, y, calendar.day_abbr[i])
            self.pdf.drawCentredString(x + self.cell_size.width * (i + 0.5), y, calendar.day_abbr[i])
        y += self.cell_size.height
        for day in self.c.itermonthdates(self.year, month):
            week_day = day.weekday()
            self.render_day(x + self.cell_size.width * (week_day + 1) - self.cell_size.width * 0.15, y, day, month)
            if week_day == 6:
                y += self.cell_size.height

    def render_month(self, x: int, y: int, month: int) -> None:
        print(f"Month start points: {x / mm, y / mm}")
        print(self.cell_size.width / mm, month)
        self.pdf.drawCentredString(x + self.month_width / 2, y, calendar.month_name[month])
        y += self.cell_size.height

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
        # y = self.top_margin + 16 * 2
        #print(self.c.yeardatescalendar(self.year, width=1))

        for i in range(12):
            month = i + 1
            # print(f"Месяц {i}, отступ вниз {i % 3}, отступ вбок {i // 3}")

            self.render_month(
                self.left_margin + (self.month_width + self.cell_size.width) * (i // 3),
                y + self.month_height * (i % 3),
                month
            )
            # self.pdf.drawString(self.left_margin + month_width * (i // 3), y + month_height * (i % 3), calendar.month_name[i + 1])
        return y + self.month_height * 3

    def render(self):
        """
        Prepares fonts, styles etc. required for rendering final image.
        :return:
        """
        locale.setlocale(locale.LC_ALL, self.locale)

        # print(self.c.formatmonth(2023, 1))

        output = self.year
        # pdf = canvas.Canvas('myfile.pdf', pagesize=self.page_size, bottomup=False)
        # width, height = A4

        # width_mm = int(width/72*25.4)
        # print(width_mm)
        print(f"Page size: {self.width / mm, self.height / mm}")
        fonts = ("DejaVuSans", "Calibri", "CalibriB", "CalibriI", "CalibriL", "CalibriLI", "CalibriZ")
        for font in fonts:
            pdfmetrics.registerFont(TTFont(font, font + ".ttf"))

        # self.pdf.setFont('DejaVuSans', self.font_size)
        self.pdf.setFont(self.font, self.font_size)

        # horizontal, vertical, text
        y = self.render_year()




        for i, holiday in enumerate(self.holidays):
            print(i)
            #self.pdf.drawString(self.left_margin, y, "7 янв		Пт	Рождество Христово")
       #!!    self.pdf.drawString(
       #!!        self.left_margin + self.cell_size.width * (i // 3),
       #!!        y + self.cell_size.height * (i % 3),
       #!!        str(holiday.date.day)
       #!!    )
            self.pdf.drawString(self.left_margin + 100, y, "Пт")
            self.pdf.drawString(self.left_margin + 200, y, "Рождество Христово")


        # self.pdf.setFillColor(green)
        # self.pdf.drawString(0.5 * cm, 1 * cm, "Календарь")

        # pdf.drawRightString

        # not sure if that calculation is necessary
        # face = pdfmetrics.getFont('CalibriB').face
        # string_height = (face.ascent - face.descent) / 1000 * self.font_size
        # print(string_height)

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

        self.pdf.showPage()
        self.pdf.save()


    def setup(self):
        """
        Initializes all the holidays and other special days according to lists (or input).
        If it is a transferable holiday and concurs with a weekend, it marks next day as weekend.
        :return:
        """
        # A workaround. Here we try to convert holidays format to a datetime object.
        for date in self.holidays:
            date[0] = datetime.datetime.strptime(str(self.year)+date[0], "%Y%m-%d").date()

        # perform weekend transfer
        for date in self.weekend_transfer:
            date[0], date[1] = (
                datetime.datetime.strptime(date[0], "%Y-%m-%d").date(),
                datetime.datetime.strptime(date[1], "%Y-%m-%d").date()
            )
        #print(self.weekend_transfer)

        # convert holidays data to Holiday object
        for i, date in enumerate(self.holidays):
            self.holidays[i] = Holiday(date=[date[0]], is_transferable=date[1], name=date[2])

        #["1-1", 0, "Новогодние каникулы"], ["1-2", 0, "Новогодние каникулы"]
        print(*self.holidays)

        # iterate over all days in a year
        start_date = datetime.date(self.year, 1, 1)
        end_date = datetime.date(self.year + 1, 1, 1)
        #print(end_date)
        for date in [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days)]:
            # populate weekends
            if date.weekday() in (5, 6):
                self.weekends.add(date)

            # Populate weekend transfers and shortened work days
            # warning!: shortened days are calculated only for transferable holidays.
            # print(date, date.weekday())
            if date in [date for holiday in self.holidays for date in holiday.date if holiday.is_transferable]:
                if date in self.weekends:
                    print(f"A transferable date {date} has collapsed with weekend, "
                          f"trying to move to the next working day")
                    transfer_day = date + datetime.timedelta(days=1)
                    # We cannot increment holiday transfer day by checking it in weekend list
                    # as this list is populating in the same loop.
                    while transfer_day.weekday() in (5, 6):
                        transfer_day += datetime.timedelta(days=1)
                    self.weekends.add(transfer_day)
                    print(f"A suitable date has been found: {transfer_day}")
                prev_date = date - datetime.timedelta(days=1)
                if prev_date not in self.weekends:
                    print(f"Found a shortened work day: {prev_date}")
                    self.shortened_work_day.add(prev_date)

        # exchange holidays according to weekend transfer list
        for date in self.weekend_transfer:
            self.weekends.discard(date[0])
            self.weekends.add(date[1])
        #print(sorted(list(self.weekends)))


        # cnt = set()
        # for holiday in self.holidays:
        #     cnt.add(holiday.name)
        # cnt = len(cnt)
        # print(f"Number of distinct holidays: {cnt}")

        #temp_list = []

        # for i, date in enumerate(self.holidays):
        #    self.holidays[i] = Holiday(date=date[0], is_transferable=date[1], name=date[2])

        for i, base_holiday in enumerate(self.holidays):
            for j, probe_holiday in reversed(list(enumerate(self.holidays))):
                # print(i, j)

                if j > i and base_holiday.name == probe_holiday.name:
                    self.holidays[i].date.append(*probe_holiday.date)
                    del self.holidays[j]
                    # print("present")
            # if holiday.name in [day.name for day in temp_list]:
            #
            #    print("Present!")
            # else:
            #    temp_list.append(holiday)
            # del self.holidays[i]

            # print(f"temp: {temp_list}")
        # print(f"holidays:{self.holidays}")
        print([date for holiday in self.holidays for date in holiday.date])

        self.render()


if __name__ == '__main__':
    cal = Calendar(2023)
    cal.setup()
