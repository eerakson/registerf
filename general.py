


from __future__ import print_function, unicode_literals

from peewee import SqliteDatabase, Model, CharField, DateField, fn
import json

from datetime import date, datetime, timedelta

import pandas

from question import (
    style,
    continue_confirm,
    general_question,
    get_query_type,
    get_tags,
    get_tag_one,
    get_month,
    get_one_month,
    get_year,
    get_one_year,
    get_amount,
    get_month_save,
    get_comment,
)

from model import (
    db,
    Balance,
    query_tag,
    query_month_year,
    query_month_year_tag,
)


def print_table(result):
    j = 0
    while j < len(result):
        for i in result[j]:
            print("{:<15} {:<8} {:<40} {:<}".format(i['tag'], i['amount'],i['comment'],str(i['date'])))
        j = j + 1


def get_tag_query(tags):
    result = []
    for tag in tags:
        result.append(query_tag(tag))
    return result 

def get_tag_sum(tags):
    tag_sum = 0
    for tag in tags:  
        tsum = (Balance
            .select(fn.Sum(Balance.amount))
            .where(Balance.tag == tag)
            .scalar()
        )
        tag_sum = tag_sum + tsum
    return tag_sum


def get_month_year_query(years, months):
    result = []
    for year in years:
        for month in months:
            result.append(query_month_year(int(month), int(year)))
    return result 


def get_month_year_sum(years, months):
    my_sum = 0
    for year in years:
        for month in months:
            mysum = (Balance
                .select(fn.Sum(Balance.amount))
                .where(Balance.date.month == int(month), 
                    Balance.date.year == int(year))
                .scalar()
            )
            if mysum != None:
                my_sum = my_sum + mysum
    return my_sum


def get_month_year_tag_query(years, months, tags):
    result = []
    for year in years:
        for month in months:
            for tag in tags:
                result.append(query_month_year_tag(int(month), int(year), tag))
    return result 

def get_month_year_tag_sum(years, months, tags):
    my_sum = 0
    for year in years:
        for month in months:
            for tag in tags:
                mysum = (Balance
                    .select(fn.Sum(Balance.amount))
                    .where(Balance.date.month == int(month), 
                        Balance.date.year == int(year),
                        Balance.tag == tag)
                    .scalar()
                )
                if mysum != None:
                    my_sum = my_sum + mysum
    return my_sum

# 4 branches of the general question

def month_overview():
    month = get_one_month()
    year = get_one_year()
    
    msum = (Balance
            .select(fn.Sum(Balance.amount))
            .where(Balance.date.month == int(month), Balance.date.year == int(year))
            .scalar()
           )

    msum_in = (Balance
               .select(fn.Sum(Balance.amount))
               .where(Balance.date.month == int(month),
                   Balance.date.year == int(year),
                   Balance.tag == 'income')
               .scalar()
               )

    msum_out = msum_in - msum

    print('--- {}/{} ---'.format(month, year))
    print('Income   = {}'.format(msum_in))
    print('Expenses = {}'.format(msum_out))
    print('Left     = {}'.format(msum))


def year_overview():
    year = get_one_year()
    
    ysum = (Balance
            .select(fn.Sum(Balance.amount))
            .where(Balance.date.year == int(year))
            .scalar()
           )

    ysum_in = (Balance
               .select(fn.Sum(Balance.amount))
               .where(Balance.date.year == int(year), Balance.tag == 'income')
               .scalar()
               )

    ysum_out = ysum_in - ysum

    print('--- {} ---'.format(year))
    print('Income   = {}'.format(ysum_in))
    print('Expenses = {}'.format(ysum_out))
    print('Left     = {}'.format(ysum))


def query_db():
    answer = get_query_type()

    if answer == 'tag':
        tags = get_tags()

        print("{:<15} {:<8} {:<40} {:<}".format('Tag', 'Amount', 'Comment', 'Date')) 

        result = get_tag_query(tags)  
        print_table(result)

        print('Sum for choosen is {}'.format(get_tag_sum(tags)))

    elif answer == 'month-year':
        months = get_month()
        years = get_year()

        print("{:<15} {:<8} {:<40} {:<}".format('Tag', 'Amount', 'Comment', 'Date')) 

        result = get_month_year_query(years, months)
        print_table(result)

        print('Sum for choosen is {}'.format(get_month_year_sum(years, months)))

    else:
        tags = get_tags()
        months = get_month()
        years = get_year()

        print("{:<15} {:<8} {:<40} {:<}".format('Tag', 'Amount', 'Comment', 'Date')) 

        result = get_month_year_tag_query(years, months, tags)
        print_table(result)

        print('Sum for choosen is {}'.format(get_month_year_tag_sum(years, months, tags)))


def register():
    tag = get_tag_one()
    amount = int(get_amount())
    comment = get_comment()
    month = get_month_save()

    if month == 'last month':
        input_date = date.today().replace(day=1) - timedelta(1)
    input_date = date.today()

    Balance(
        amount=amount,
        tag=tag,
        comment=comment,
        date=input_date
    ).save()

