import calendar
import io
import locale
import datetime
from itertools import count

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
        self.font_size = 12
        self.locale = 'Russian_Russia'
        self.pdf = canvas.Canvas('myfile.pdf', pagesize=self.page_size, bottomup=False)

        self.cell_size = Cell(
            (self.width - self.left_margin - self.right_margin) / 31,
            (self.width - self.left_margin - self.right_margin) / 31 * 0.9
        )
        self.month_width = self.cell_size.width * 7  # (self.width - self.left_margin - self.right_margin) / 31 * 7
        self.month_height = self.cell_size.height * 9  # (self.height - self.top_margin - self.bottom_margin)

        # should remove and set as cell_size.height
        self.line_spacing = self.font_size * 1.2

        self.c = calendar.LocaleTextCalendar(locale=self.locale)

        self.working_days = []
        self.working_hours = []
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

    def is_special_day(self, day: datetime.date) -> Color:
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
        self.working_days.append(day)
        return black

    def render_day(self, x: int, y: int, day: datetime.date, month: int):
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

    def render_year(self, y):
        self.pdf.setFont(self.font, self.font_size + 2)
        self.pdf.drawCentredString(self.width / 2, y, f"Производственный календарь на {self.year} год")
        #y += self.line_spacing * 2
        y += self.cell_size.height * 2
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

    def render_holidays(self, y):
        print("-----Holidays-----")
        self.font = "Calibri"
        self.pdf.setFont(self.font, self.font_size - 3)

        for i, holiday in enumerate(self.holidays):
            self.pdf.setFillColor(darkred)
            print(i, holiday)
            print(min(holiday.date), max(holiday.date), len(holiday.date))
            pos_x = self.left_margin + self.cell_size.width * 10 * (i // 3)
            pos_y = y + self.cell_size.height * (i % 3)
            print(pos_x, pos_y)
            if len(holiday.date) > 1:
                date = f"{min(holiday.date).day}-{max(holiday.date).day} "
                date += min(holiday.date).strftime("%b")
                print(date)
                self.pdf.drawCentredString(
                    pos_x + self.cell_size.width * 3 / 2,
                    pos_y,
                    str(date)
                )
                self.pdf.setFillColor(black)
            else:
                date = f"{holiday.date[0].day} {convert_month_name(holiday.date[0].strftime('%b'))}"
                self.pdf.drawCentredString(
                    pos_x + self.cell_size.width,
                    pos_y,
                    date
                )
                self.pdf.setFillColor(black)
                self.pdf.drawString(
                    pos_x + self.cell_size.width * 2,
                    pos_y,
                    holiday.date[0].strftime("%a")
                )

            self.pdf.drawString(
                pos_x + self.cell_size.width * 3,
                pos_y,
                holiday.name
            )

            # self.pdf.drawString(self.left_margin, y, "7 янв		Пт	Рождество Христово")
            # self.pdf.drawString(
            #    self.left_margin + self.cell_size.width * (i // 3),
            #    y + self.cell_size.height * (i % 3),
            #    str(holiday.date)
            # )
            # self.pdf.drawString(self.left_margin + 100, y, "Пт")
            # self.pdf.drawString(self.left_margin + 200, y, "Рождество Христово")

        y += self.cell_size.height * 4

        self.font = "CalibriB"
        self.pdf.setFont(self.font, self.font_size)
        print(self.font_size)

        self.pdf.setFillColor(green)
        self.pdf.drawCentredString(self.left_margin + self.cell_size.width * 0.5, y, "22")

        self.pdf.setFillColor(black)
        self.font = "Calibri"
        self.pdf.setFont(self.font, self.font_size - 3)

        self.pdf.drawString(
            self.left_margin + self.cell_size.width,
            y,
            " - Предпраздничные дни, в которые продолжительность работы сокращается на один час"
        )
        y += self.cell_size.height * 2
        return y

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

        y = self.top_margin
        # horizontal, vertical, text
        y = self.render_year(y)

        y = self.render_holidays(y)

        print("-----Нормы времени-----")
        self.font = "CalibriB"
        self.pdf.setFont(self.font, self.font_size - 1)

        self.pdf.drawCentredString(self.width / 2, y, "Количественная раскладка на 2022 год")

        #self.pdf.setStrokeColorRGB(0.2, 0.5, 0.3)
        self.pdf.line(self.left_margin, y + self.cell_size.height * 0.2, self.width - self.right_margin, y + self.cell_size.height * 0.2)

        x = self.left_margin
        y += self.cell_size.height
        self.pdf.drawCentredString(x + self.cell_size.width * 1.5, y + self.cell_size.height * 0.5, "Период")
        self.pdf.drawCentredString(x + self.cell_size.width * 3 + (self.cell_size.width * 16 / 2), y, "Дней")
        self.pdf.drawCentredString(x + self.cell_size.width * 19 + (self.cell_size.width * 12 / 2), y,
                                   "Рабочих часов")
        y += self.cell_size.height

        self.pdf.drawCentredString(x + self.cell_size.width * 3 + (self.cell_size.width * 4 / 2), y,
                                   "календарных")
        self.pdf.drawCentredString(x + self.cell_size.width * 7 + (self.cell_size.width * 4 / 2), y,
                                   "рабочих")
        self.pdf.setFillColor(red)
        self.pdf.drawCentredString(x + self.cell_size.width * 11 + (self.cell_size.width * 7 / 2), y,
                                   "выходных и праздничных")
        self.pdf.setFillColor(green)
        self.pdf.setFontSize(self.font_size - 3)
        self.pdf.drawCentredString(x + self.cell_size.width * 18 + (self.cell_size.width / 2), y,
                                   "сокр")
        self.pdf.setFontSize(self.font_size - 1)
        self.pdf.setFillColor(black)
        self.pdf.drawCentredString(x + self.cell_size.width * 19 + (self.cell_size.width * 4 / 2), y,
                                   "40 - час.неделя")
        self.pdf.drawCentredString(x + self.cell_size.width * 23 + (self.cell_size.width * 4 / 2), y,
                                   "36 - час.неделя")
        self.pdf.drawCentredString(x + self.cell_size.width * 27 + (self.cell_size.width * 4 / 2), y,
                                   "24 - час.неделя")
        #print(self.pdf._fontsize)
        y += self.cell_size.height

        table_width = [3, 4, 4, 7, 1, 4, 4, 4]
        print("weekends:")
        print(sorted(list(self.weekends)))
        print("work days:")
        print(sorted(list(self.working_days)))
        print("short days:")
        print(sorted(list(self.shortened_work_day)))

        days = []
        work_days = []
        short_days = []
        holidays = []
        work_hours = []
        work_hours36 = []
        work_hours24 = []

        for i in range(12):
            month = i + 1
            self.pdf.drawCentredString(x + self.cell_size.width * 3 + (self.cell_size.width * 4 / 2), y,
                                       "календарных")
            days.append(calendar.monthrange(self.year, month)[1])
            work_days.append(
                len([day for day in self.working_days if day.month == month]) +
                len([day for day in self.shortened_work_day if day.month == month])
            )
            holidays.append(
                len([day for day in self.weekends if day.month == month]) +
                len([date for holiday in self.holidays for date in holiday.date if date.month == month])
            )
            short_days.append(len([date for date in self.shortened_work_day if date.month == month]))

            work_hours.append(work_days[i] * 8 - short_days[i])
            work_hours36.append(float(work_days[i] * 7.2 - short_days[i]))
            work_hours24.append(work_days[i] * 4.8 - short_days[i])

            print(
                month,
                days[i],
                work_days[i],
                holidays[i],
                short_days[i],
                work_hours[i],
                f"{work_hours36[i]:.1f}",
                f"{work_hours24[i]:.1f}",
            )
            if not month % 3:
                print("Quarter")
                print(
                    sum(days[i-2:month]),
                    sum(work_days[i-2:month]),
                    sum(holidays[i-2:month]),
                    sum(short_days[i-2:month]),
                    sum(work_hours[i-2:month]),
                    f"{sum(work_hours36[i - 2:month]):.1f}",
                    f"{sum(work_hours24[i - 2:month]):.1f}",
                )
            if not month % 12:
                print("annual")
                print(
                    sum(days[0:month]),
                    sum(work_days[0:month]),
                    sum(holidays[0:month]),
                    sum(short_days[0:month]),
                    sum(work_hours[0:month]),
                    f"{sum(work_hours36[0:month]):.1f}",
                    f"{sum(work_hours24[0:month]):.1f}",
                )

        #

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

        # convert weekend transfer to datetime
        for date in self.weekend_transfer:
            date[0], date[1] = (
                datetime.datetime.strptime(date[0], "%Y-%m-%d").date(),
                datetime.datetime.strptime(date[1], "%Y-%m-%d").date()
            )
        #print(self.weekend_transfer)




        # convert holidays data to Holiday object
        for i, date in enumerate(self.holidays):
            self.holidays[i] = Holiday(date=[date[0]], is_transferable=bool(date[1]), name=date[2])

        # cnt = set()
        # for holiday in self.holidays:
        #     cnt.add(holiday.name)
        # cnt = len(cnt)
        # print(f"Number of distinct holidays: {cnt}")

        #temp_list = []

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

        # exchange holidays according to weekend transfer list
        for date in self.weekend_transfer:
            self.weekends.discard(date[0])
            self.weekends.add(date[1])

        for date in [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days)]:
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
                    self.weekends.discard(date)
                    print(f"A suitable date has been found: {transfer_day}")
                prev_date = date - datetime.timedelta(days=1)
                if prev_date not in self.weekends:
                    print(f"Found a shortened work day: {prev_date}")
                    self.shortened_work_day.add(prev_date)
            elif date in [date for holiday in self.holidays for date in holiday.date]:
                self.weekends.discard(date)



        #print(sorted(list(self.weekends)))

        self.render()


def convert_month_name(month):
    names = {
        "май": "мая",
        "июн": "июня",
    }
    if month in names:
        return names[month]
    return month

if __name__ == '__main__':
    cal = Calendar(2023)
    cal.setup()
