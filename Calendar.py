import calendar
import datetime
import locale
import sys
import typing

from reportlab.lib.colors import (Color, HexColor, black, darkblue, darkred,
                                  green, lightgrey, red)
from reportlab.lib.pagesizes import A4, A3, A5, A6
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ARABIC_TO_ROMAN = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
                   (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
                   (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]

USAGE = (f"Usage: {sys.argv[0]} 2008\n"
         "Creates PDF calendar for the mentioned year\n"
         "in the same folder.\n"
         "If no year is specified, then current year is chosen\n"
         "or next if it is past October.\n"
         "[--help] - displays this message")


class Cell:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height


class Holiday:
    def __init__(
            self,
            date: typing.List[datetime.date],
            is_transferable: bool,
            name: str
    ):
        self.date = date
        self.is_transferable = is_transferable
        self.name = name

    def __repr__(self) -> str:
        return (f"{self.__class__.__qualname__}"
                f"({self.date}, "
                f"{self.is_transferable}, "
                f"{self.name})")


class Calendar:
    def __init__(
            self,
            year: int,
            page_size: typing.Tuple[float, float] = A4,
            font: str = 'CalibriB',
            font_size: int = 12,
            locale: str = 'Russian_Russia',
    ):
        self.year = year
        self.top_margin = 1 * cm
        self.bottom_margin = 1 * cm
        self.left_margin = 0.5 * cm
        self.right_margin = 0.5 * cm
        self.page_size = page_size
        self.width, self.height = self.page_size
        self.font = font
        self.font_size = font_size
        self.locale = locale
        self.pdf = canvas.Canvas(
            f"Calendar_{self.year}.pdf",
            pagesize=self.page_size,
            bottomup=False
        )

        self.cell_size = Cell(
            (self.width - self.left_margin - self.right_margin) / 31,
            (self.width - self.left_margin - self.right_margin) / 31 * 0.8
        )
        self.month_width = self.cell_size.width * 7
        self.month_height = self.cell_size.height * 9

        self.c = calendar.LocaleTextCalendar(locale=self.locale)

        self.working_days: typing.List[datetime.date] = []

        # month, day, is_transferrable (defines if holiday
        # is transferred when concurs with weekend), name
        self.holidays: Holiday = [
            ["1-1", 0, "Новогодние каникулы"],
            ["1-2", 0, "Новогодние каникулы"],
            ["1-3", 0, "Новогодние каникулы"],
            ["1-4", 0, "Новогодние каникулы"],
            ["1-5", 0, "Новогодние каникулы"],
            ["1-6", 0, "Новогодние каникулы"],
            ["1-7", 0, "Рождество Христово"],
            ["1-8", 0, "Новогодние каникулы"],
            ["2-23", 1, "День защитника Отечества"],
            ["3-8", 1, "Международный женский день"],
            ["5-1", 1, "Праздник Весны и Труда"],
            ["5-9", 1, "День Победы"],
            ["6-12", 1, "День России"],
            ["11-4", 1, "День народного единства"]]

        self.weekends: typing.Set[datetime.date] = set()

        self.shortened_work_day: typing.Set[datetime.date] = set()

        self.weekend_transfer = [
            ["2023-1-1", "2023-2-24"],
            ["2023-1-8", "2023-5-8"],
        ]

    def draw_horizontal_line(self, y: float) -> None:
        """
        Draws horizontal line for full width
        (excluding margins) on y coordinate.
        :param y:
        :return:
        """
        self.pdf.line(
            self.left_margin,
            y + self.cell_size.height * 0.2,
            self.width - self.right_margin,
            y + self.cell_size.height * 0.2
        )

    def draw_vertical_line(self, x: float, y: float, height: int) -> None:
        """
        Draws vertical line for specified height in x, y coordinates.
        :param x:
        :param y:
        :param height:
        :return:
        """
        self.pdf.line(
            x, y,
            x, y + height * self.cell_size.height
        )

    def print_cell(
            self,
            pos_x: float,
            pos_y: float,
            text: typing.Union[typing.List[object], object],
            parameter: typing.Union[int, list],
            color: str = black
    ) -> None:
        """
        Determines a color, performs character formatting
        and renders a cell with certain data.
        :param pos_x:
        :param pos_y:
        :param text:
        :param parameter:
        :param color:
        :return:
        """
        if type(parameter) == list:
            parameter = parameter[0]
        self.pdf.setFillColor(color)
        if type(text[parameter]) is float:
            string = f"{text[parameter]:.1f}"
            self.pdf.drawCentredString(pos_x, pos_y, string)
            return
        self.pdf.drawCentredString(
            pos_x,
            pos_y,
            str(text[parameter])
        )

    def is_special_day(self, day: datetime.date) -> Color:
        """
        Checks if a day is in holiday, weekend
        or shortened work day lists and returns
        corresponding color for the day type.
        Returns black color if not.
        :param day:
        :return:
        """
        # search in list of lists
        if day in [
            date for holiday in self.holidays for date in holiday.date
        ]:
            return HexColor(0x990000)
        if day in self.weekends:
            return red
        if day in self.shortened_work_day:
            return green
        self.working_days.append(day)
        return black

    def render_day(
            self,
            x: float,
            y: float,
            day: datetime.date,
            month: int
    ) -> None:
        """
        Renders every day checking the parameters such as color or
        affilation with a certain month.
        :param x:
        :param y:
        :param day:
        :param month:
        :return:
        """
        if day.month != month:
            self.pdf.setFillColor(lightgrey)
        else:
            color = self.is_special_day(day)
            self.pdf.setFillColor(color)
        self.pdf.drawRightString(x, y, str(day.day))
        self.pdf.setFillColor(black)

    def render_week(self, x: float, y: float, month: int) -> None:
        """
        Renders every week. Calculates a location for every day in a month
        and passes control further to "day" part.
        :param x:
        :param y:
        :param month:
        :return:
        """
        for i in range(0, 7):
            if i > 4:
                self.pdf.setFillColor(red)
            else:
                self.pdf.setFillColor(black)
            self.pdf.drawCentredString(
                x + self.cell_size.width * (i + 0.5),
                y,
                calendar.day_abbr[i]
            )
        y += self.cell_size.height
        for day in self.c.itermonthdates(self.year, month):
            week_day = day.weekday()
            self.render_day(
                x + self.cell_size.width * (week_day + 1) - self.cell_size.width * 0.15,
                y,
                day,
                month
            )
            if week_day == 6:
                y += self.cell_size.height

    def render_month(self, x: float, y: float, month: int) -> None:
        """
        Renders every month of a year. Gives control to "week" part.
        :param x:
        :param y:
        :param month:
        :return:
        """
        # print(f"Month start points: {x / mm, y / mm}")
        # print(self.cell_size.width / mm, month)
        self.pdf.drawCentredString(
            x + self.month_width / 2,
            y,
            calendar.month_name[month]
        )
        y += self.cell_size.height

        self.render_week(x, y, month)

    def render_year(self, y: float) -> float:
        """
        Renders year part of calendar. Calculates a location
        for every month and passes coordianates to "month" part.
        render.
        :param y:
        :return:
        """
        self.pdf.setFont(self.font, self.font_size + 2)
        self.pdf.drawCentredString(
            self.width / 2,
            y,
            f"Производственный календарь на {self.year} год"
        )
        y += self.cell_size.height * 2
        self.pdf.setFont(self.font, self.font_size)

        # there are 31 cell and 7 in every month in case 4 months
        # per line plus 3 empty cells as border
        # print(f"Month width: {self.month_width / mm}")
        # print(f"Month height: {self.month_height / mm}")

        for i in range(12):
            month = i + 1

            self.render_month(
                self.left_margin + (self.month_width + self.cell_size.width) * (i // 3),
                y + self.month_height * (i % 3),
                month
            )

        return y + self.month_height * 3

    def render_holidays(self, y: float) -> float:
        """
        Renders holidays part. A list of date and description for
        every holiday that is considered a public holiday.
        :param y:
        :return:
        """
        # print("-----Holidays-----")
        self.font = "Calibri"
        self.pdf.setFont(self.font, self.font_size - 3)

        for i, holiday in enumerate(self.holidays):
            self.pdf.setFillColor(darkred)
            # print(i, holiday)
            # print(min(holiday.date), max(holiday.date), len(holiday.date))
            pos_x = self.left_margin + self.cell_size.width * 10 * (i // 3)
            pos_y = y + self.cell_size.height * (i % 3)
            # print(pos_x, pos_y)
            if len(holiday.date) > 1:
                date = f"{min(holiday.date).day}-{max(holiday.date).day} "
                date += min(holiday.date).strftime("%b")

                self.pdf.drawCentredString(
                    pos_x + self.cell_size.width * 3 / 2,
                    pos_y,
                    str(date)
                )
                self.pdf.setFillColor(black)
            else:
                date = (
                    f"{holiday.date[0].day}"
                    f" {convert_month_name(holiday.date[0].strftime('%b'))}")
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

        y += self.cell_size.height * 4

        self.font = "CalibriB"
        self.pdf.setFont(self.font, self.font_size)

        self.pdf.setFillColor(green)
        self.pdf.drawCentredString(
            self.left_margin + self.cell_size.width * 0.5,
            y,
            "22"
        )

        self.pdf.setFillColor(black)
        self.font = "Calibri"
        self.pdf.setFont(self.font, self.font_size - 3)

        self.pdf.drawString(
            self.left_margin + self.cell_size.width,
            y,
            " - Предпраздничные дни, в которые продолжительность работы "
            "сокращается на один час"
        )
        y += self.cell_size.height * 2
        return y

    def render_schedule(self, y: float) -> float:
        """
        Renders production schedule part.
        Calculations are performed inside.
        :param y:
        :return:
        """
        # print("-----Нормы времени-----")
        self.font = "CalibriB"
        self.pdf.setFont(self.font, self.font_size - 1)

        self.pdf.drawCentredString(
            self.width / 2,
            y,
            "Количественная раскладка на 2022 год"
        )

        self.draw_horizontal_line(y)

        vertical_borders = [0, 3, 16, 12]

        x = self.left_margin

        pos_x = x

        # draw vertical borders
        for i in range(len(vertical_borders)):
            pos_x += self.cell_size.width * vertical_borders[i]
            self.draw_vertical_line(pos_x, y + self.cell_size.height * 0.2, 19)

        y += self.cell_size.height

        self.pdf.drawCentredString(
            x + self.cell_size.width * 1.5,
            y + self.cell_size.height * 0.5,
            "Период"
        )
        self.pdf.drawCentredString(
            x + self.cell_size.width * 3 + (self.cell_size.width * 16 / 2),
            y,
            "Дней"
        )
        self.pdf.drawCentredString(
            x + self.cell_size.width * 19 + (self.cell_size.width * 12 / 2),
            y,
            "Рабочих часов"
        )
        y += self.cell_size.height

        self.pdf.drawCentredString(
            x + self.cell_size.width * 3 + (self.cell_size.width * 4 / 2),
            y,
            "календарных"
        )
        self.pdf.drawCentredString(
            x + self.cell_size.width * 7 + (self.cell_size.width * 4 / 2),
            y,
            "рабочих"
        )
        self.pdf.setFillColor(red)
        self.pdf.drawCentredString(
            x + self.cell_size.width * 11 + (self.cell_size.width * 7 / 2),
            y,
            "выходных и праздничных"
        )
        self.pdf.setFillColor(green)
        self.pdf.setFontSize(self.font_size - 3)
        self.pdf.drawCentredString(
            x + self.cell_size.width * 18 + (self.cell_size.width / 2),
            y,
            "сокр"
        )
        self.pdf.setFontSize(self.font_size - 1)
        self.pdf.setFillColor(black)
        self.pdf.drawCentredString(
            x + self.cell_size.width * 19 + (self.cell_size.width * 4 / 2),
            y,
            "40 - час.неделя"
        )
        self.pdf.drawCentredString(
            x + self.cell_size.width * 23 + (self.cell_size.width * 4 / 2),
            y,
            "36 - час.неделя"
        )
        self.pdf.drawCentredString(
            x + self.cell_size.width * 27 + (self.cell_size.width * 4 / 2),
            y,
            "24 - час.неделя"
        )

        self.draw_horizontal_line(y)

        y += self.cell_size.height

        month = 0
        days: typing.List[int] = []
        work_days: typing.List[int] = []
        holidays: typing.List[int] = []
        short_days: typing.List[int] = []
        work_hours: typing.List[float] = []
        work_hours36: typing.List[float] = []
        work_hours24: typing.List[float] = []

        months = [
            datetime.date(2001, i + 1, 1).strftime("%B") for i in range(12)
        ]

        table_width = [
            (3, months, black),
            (4, days, black),
            (4, work_days, black),
            (7, holidays, red),
            (1, short_days, green),
            (4, work_hours, black),
            (4, work_hours36, black),
            (4, work_hours24, black),
        ]

        for i in range(12):
            month = i + 1

            days.append(calendar.monthrange(self.year, month)[1])
            work_days.append(
                len([day for day in self.working_days
                     if day.month == month]) +
                len([day for day in self.shortened_work_day
                     if day.month == month])
            )
            holidays.append(
                len([day for day in self.weekends if day.month == month]) +
                len([day for holiday in self.holidays for day in holiday.date
                     if day.month == month])
            )
            short_days.append(
                len([date for date in self.shortened_work_day
                     if date.month == month])
            )

            work_hours.append(work_days[i] * 8 - short_days[i])
            work_hours36.append(work_days[i] * 7.2 - short_days[i])
            work_hours24.append(work_days[i] * 4.8 - short_days[i])

            pos_x = x

            for j in range(len(table_width)):
                pos_x += self.cell_size.width * table_width[j][0] / 2
                self.print_cell(
                    pos_x,
                    y,
                    table_width[j][1],
                    i,
                    table_width[j][2]
                )
                pos_x += self.cell_size.width * table_width[j][0] / 2

            if not month % 3:
                self.draw_horizontal_line(y)

                y += self.cell_size.height

                pos_x = x
                quarter_table = [
                    f"{to_roman_numeral(i // 3 + 1)} Квартал",
                    sum(days[i - 2:month]),
                    sum(work_days[i - 2:month]),
                    sum(holidays[i - 2:month]),
                    sum(short_days[i - 2:month]),
                    sum(work_hours[i - 2:month]),
                    f"{sum(work_hours36[i - 2:month]):.1f}",
                    f"{sum(work_hours24[i - 2:month]):.1f}",
                ]
                for j in range(len(table_width)):
                    pos_x += self.cell_size.width * table_width[j][0] / 2
                    self.print_cell(pos_x, y, [quarter_table[j]], 0, darkblue)
                    pos_x += self.cell_size.width * table_width[j][0] / 2

                self.draw_horizontal_line(y)

            if not month % 12:

                y += self.cell_size.height

                pos_x = x

                annual_table = [
                    "Итого",
                    sum(days[0:month]),
                    sum(work_days[0:month]),
                    sum(holidays[0:month]),
                    sum(short_days[0:month]),
                    sum(work_hours[0:month]),
                    f"{sum(work_hours36[0:month]):.1f}",
                    f"{sum(work_hours24[0:month]):.1f}",
                ]

                for j in range(len(table_width)):
                    pos_x += self.cell_size.width * table_width[j][0] / 2
                    self.print_cell(pos_x, y, [annual_table[j]], 0, darkblue)
                    pos_x += self.cell_size.width * table_width[j][0] / 2

                self.draw_horizontal_line(y)

            y += self.cell_size.height

        return y

    def render_sign(self, y):
        string = "made by Ilya Rogovoy"
        self.pdf.setFillColor(HexColor(0xF0F0F0))
        self.pdf.drawString(self.left_margin, y, string)
        self.pdf.setFillColor(black)


    def render(self) -> None:
        """
        Prepares fonts, styles etc. required for rendering final image.
        Calls other necessary functions.
        :return:
        """
        locale.setlocale(locale.LC_ALL, self.locale)

        # print(f"Page size: {self.width / mm, self.height / mm}")
        fonts = (
            "DejaVuSans",
            "Calibri",
            "CalibriB",
            "CalibriI",
            "CalibriL",
            "CalibriLI",
            "CalibriZ"
        )
        for font in fonts:
            pdfmetrics.registerFont(TTFont(font, font + ".ttf"))

        self.pdf.setFont(self.font, self.font_size)

        y = self.top_margin

        y = self.render_year(y)

        y = self.render_holidays(y)

        y = self.render_schedule(y)

        y = self.render_sign(y)

        self.pdf.showPage()
        try:
            self.pdf.save()
        except PermissionError as exception:
            print("------EГГOГ------")
            print(exception)
            print(f"Check if the file is not opened and you have \n"
                  f"enough permissions writing to this folder.")


    def setup(self) -> None:
        """
        Initializes all the holidays and other special days
        according to lists (or input).
        If it is a transferable holiday and concurs with a weekend,
        it marks next day as weekend.
        :return:
        """
        # A workaround. Here we try to convert
        # holidays format to a datetime object.
        for date in self.holidays:
            date[0] = datetime.datetime.strptime(
                str(self.year)+date[0],
                "%Y%m-%d"
            ).date()

        # convert weekend transfer to datetime
        for date in self.weekend_transfer:
            date[0], date[1] = (
                datetime.datetime.strptime(date[0], "%Y-%m-%d").date(),
                datetime.datetime.strptime(date[1], "%Y-%m-%d").date()
            )

        # convert holidays data to Holiday object
        for i, date in enumerate(self.holidays):
            self.holidays[i] = Holiday(
                date=[date[0]],
                is_transferable=bool(date[1]),
                name=date[2]
            )

        for i, base_holiday in enumerate(self.holidays):
            for j, probe_holiday in reversed(list(enumerate(self.holidays))):
                # print(i, j)

                if j > i and base_holiday.name == probe_holiday.name:
                    self.holidays[i].date.append(*probe_holiday.date)
                    del self.holidays[j]

        # iterate over all days in a year
        start_date = datetime.date(self.year, 1, 1)
        end_date = datetime.date(self.year + 1, 1, 1)

        for date in [
            start_date + datetime.timedelta(days=x)
            for x in range((end_date - start_date).days)
        ]:
            # populate weekends
            if date.weekday() in (5, 6):
                self.weekends.add(date)

        # exchange holidays according to weekend transfer list
        for date in self.weekend_transfer:
            self.weekends.discard(date[0])
            self.weekends.add(date[1])

        for date in [
            start_date + datetime.timedelta(days=x)
            for x in range((end_date - start_date).days)
        ]:
            # Populate weekend transfers and shortened work days
            # warning!: shortened days are calculated
            # only for transferable holidays.
            # print(date, date.weekday())
            if date in [
                date for holiday in self.holidays for date in holiday.date
                if holiday.is_transferable
            ]:
                if date in self.weekends:
                    print(f"A transferable date {date} "
                          f"has collapsed with weekend, "
                          f"trying to move to the next working day")
                    transfer_day = date + datetime.timedelta(days=1)
                    # We cannot increment holiday transfer day b
                    # y checking it in weekend list as this list
                    # is populating in the same loop.
                    while transfer_day.weekday() in (5, 6):
                        transfer_day += datetime.timedelta(days=1)
                    self.weekends.add(transfer_day)
                    self.weekends.discard(date)
                    print(f"A suitable date has been found: {transfer_day}")
                prev_date = date - datetime.timedelta(days=1)
                if prev_date not in self.weekends:
                    print(f"Found a shortened work day: {prev_date}")
                    self.shortened_work_day.add(prev_date)
            elif date in [
                date for holiday in self.holidays for date in holiday.date
            ]:
                self.weekends.discard(date)

        self.render()


def to_roman_numeral(number: int) -> str:
    """Convert arabic number to a roman numeral string"""
    result = list()
    for arabic, roman in ARABIC_TO_ROMAN:
        count, number = divmod(number, arabic)
        result.append(roman * count)
    return "".join(result)


def convert_month_name(month: str) -> str:
    names = {
        "май": "мая",
        "июн": "июня",
    }
    if month in names:
        return names[month]
    return month


def main() -> None:
    args = sys.argv[1:]
    if not args:
        year = datetime.date.today().year
        if datetime.date.today().month > 10:
            year += 1

    elif args[0] == "--help":
        raise SystemExit(USAGE)
    elif args[0].isdigit():
        year = int(args[0])
    else:
        raise SystemExit(USAGE)
    cal = Calendar(year, page_size=A4, font_size=12)
    cal.setup()


if __name__ == '__main__':
    main()
