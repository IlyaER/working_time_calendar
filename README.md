Производственный календарь на любой год в PDF.

Долгое время пользовался excel версией генератора календаря,
но там необходимо было проводить некоторые операции вручную, либо
городить макросы, что не вызывало у меня приятных ощущений.
Решил реализовать на python.
Календарь генерируется в PDF для дальнейшей печати.
Используется библиотека reportlab.

Особенности:
- вертикальное расположение (февраль располагается под январём, а не справа)
- автоподсчёт всех праздников и сокращённых дней
- возможность выбора шрифта, кегля, размера страницы (TBD)

- версия для России (праздники)
- нет визуального интерфейса



This is a simple working time calendar printed in PDF.

Features:
- vertical alignment (Feb is under Jan, not to the right as usual)
- all holidays and shortened workdays are calculated

Limitations:
- currently only Russian version (public holidays)
- no GUI