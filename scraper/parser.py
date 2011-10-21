# -*- coding: utf-8 -*-
import re

MONTH_TO_YEAR = 12
DAY_TO_YEAR = 226
HOUR_TO_YEAR = 1810

HOURS_ENUM = ['Indiferente',
              'Completa',
              'Parcial',
              'Parcial Mañana',
              'Parcial Tarde',
              'Intensiva',
              'Intensiva Mañana',
              'Intensiva Tarde']

def salary_parser(salary_str):
    amounts = re.findall("([\d\.,]*\d)", salary_str)
    mod = 1
    if re.search("mes", salary_str):
        mod = MONTH_TO_YEAR
    elif re.search("d(i|í)a", salary_str):
        mod = DAY_TO_YEAR
    elif re.search("hora", salary_str):
        mod = HOUR_TO_YEAR
    amounts = map(lambda x: float(re.sub( ',', '.', re.sub('\.', '', x)))*mod, amounts)
    amounts.sort()
    return amounts[:2] if amounts else None
    
def hours_parser(hours_str):
    hours_index = 0
    if (re.search("completa", hours_str, re.IGNORECASE) or
        re.search("39+", hours_str, re.IGNORECASE) or
        re.search("32-38", hours_str, re.IGNORECASE)):
        hours_index = 1
    elif (re.search("parcial", hours_str, re.IGNORECASE) or
        re.search("0-16", hours_str, re.IGNORECASE)):
        hours_index = 2
    elif (re.search("intensiva", hours_str, re.IGNORECASE) or
        re.search("17-31", hours_str, re.IGNORECASE)):
        hours_index = 5
    if re.search("ma(ñ|n)ana", hours_str, re.IGNORECASE):
        hours_index += 1
    elif re.search("tarde", hours_str, re.IGNORECASE):
        hours_index += 2
    return HOURS_ENUM[hours_index]

def experience_parser(exp_str):
    exp = re.findall("\d+", exp_str)
    exp = map(lambda x: float(x), exp)
    exp.sort()
    return exp[:2] if exp else None
        