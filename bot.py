import telebot
from random import randint
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import requests
from bs4 import BeautifulSoup
from pandas.core.common import flatten
import pandas as pd
import re
from tabulate import tabulate
import os
from IPython.core.display import Image, display
from vedis import Vedis
from enum import Enum
from flask import Flask , request
driver = webdriver.Firefox(executable_path=r'C:\\Users\\victo\\bin\\geckodriver.exe') # set path  to your gekodriver.exe

server = Flask(__name__)


token ='1013908134:AAG4nF2iyWx3Jf_rbl5lZD2YN2WlYqV5PGo'
bot = telebot.TeleBot(token)


job = None
Region = None


listr= 'Балашиха, Железнодорожный, Жуковский, Коломна, Королев, Люберцы,\n Мытищи, Ногинск, Одинцово, Орехово-Зуево, ' \
       'Подольск, Сергиев Посад,\n Серпухов, Химки, Щелково, Электросталь, Зеленоград, Клин,\n Реутов, Павловский Посад, ' \
       'Солнечногорск, Дмитров, Красногорск, Чехов,\n Лобня, Донской, Наро-Фоминск, Яхрома, Видное, Воскресенск,\n Московский, ' \
       'Пушкино, Домодедово, Климовск, Фрязино, Апрелевка,\n Егорьевск, Ивантеевка, Протвино, Раменское, Лыткарино, Щербинка,\n ' \
       'Долгопрудный, Ступино, Бронницы, Электрогорск, Можайск, Дубна,\n Истра, Волоколамск, Дзержинский, Верея, Высоковск,' \
       ' Голицыно,\n Дедовск, Дрезна, Зарайск, Звенигород, Кашира, Котельники,\n Красноармейск, Краснозаводск, Кубинка, Куровское, ' \
       'Ликино-Дулево, Лосино-Петровский,\n Луховицы, Ожерелье, Озеры, Пересвет, Пущино, Рошаль,\n Руза, Старая Купавна, Хотьково,' \
       ' Черноголовка, Шатура, Электроугли,\n Юбилейный, Куринокво, Малино, Софрино, Михнево'

listj= ['грузчик, продавец, секретарь, директор, аналитик, бухгалтер']




picts = ['https://lh3.googleusercontent.com/proxy/OM_aa5iegp44mzOlJ3yhUYbACgsHj4hISxj2vzSyiLG6HwTiWb0gVcIjzfr4xmGibdzz3qKMRpF60wXEbRI6w2L4Ipj1k6ThRufp_nv3eus',
         'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcT0L-ZZsH7ILtKt0GwDFkqqlnhm96d_MJYg-p1746Av6ztF6GgG&usqp=CAU',
         'https://www.whiteflowerfarm.com/mas_assets/cache/image/4/c/a/0/19616.Jpg']


class States(Enum):
    S_Start ='0'
    S_Enter_job ='1'
    S_Enter_region ='2'
    S_avg_needed ='3'

db = 'base.vdb'

def get_state(user_id):
    with Vedis(db) as db1:
        try:
            return db1[user_id].decode()
        except KeyError:
            return States.S_Start.value

def set_state(user_id, value):
    with Vedis(db) as db1:
        try:
            db1[user_id]  = value
            return True
        except:
            return False


def getstats (job, region):
    df2 = pd.DataFrame(columns =['starting from','jobsn','region'])
    for i in region:
        driver.get('https://hh.ru//')
        vacancy = driver.find_element_by_name('text')
        vacancy.send_keys('{} {}'.format (job , i))
        subm = driver.find_element_by_css_selector(".supernova-search-submit-text").click()
        page=driver.page_source
        fg=re.findall(r'only_with_salary=true&amp;salary=(\d{,7})&amp.{,300}-qa="serp__cluster-item-number">(\d{,2})<',str(page))
        f=(flatten(fg))
        finallist=[s for s in [*f] if s.isdigit()]
        data = { 'starting from': finallist[::2],'jobsn' : finallist[1::2]}
        df = pd.DataFrame (data, columns = ['starting from','jobsn'])
        df['region'] = (i)
        df2=df2.append(df,ignore_index=True)
    return df2


@bot.message_handler(commands=['info'])
def info_cmd (message):
    bot.send_message(message.chat.id, 'Short guidelines for salary_avg_bot. \n'
                                      'This bot helps you to get information about different jobs and respective salaries in vicinity of Moscow.\n'
                                      'To get the information please select a job, you can view the list of sample jobs here /list_sample_jobs.\n'
                                      'Then select a region or several regions (by region I mean a town or city around Moscow with the outskirts area of about 10 km)'
                                      'I only have information about limited number of regions.\n'
                                      'to view the list of regions /list_sample_regions.\n'
                                      '/reset  to start again.\n'
                                      '/info to get this guidelines')




@bot.message_handler(commands=['reset'])
def greetings(message):
    bot.send_message(message.chat.id, 'let`s start again,\n'
                                      'Enter a job,/list_saple_jobs')
    set_state(message.chat.id, States.S_Enter_job.value)


@bot.message_handler(commands=['list_sample_regions'])
def listregions_cmd (message):
    bot.send_message(message.chat.id, listr)

@bot.message_handler(commands=['list_sample_jobs'])
def listjobs_cmd (message):
    bot.send_message(message.chat.id, listj)



@bot.message_handler(func=lambda message: get_state(message.chat.id) == States.S_Enter_job.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start',
                                                              '/lis_sample_jobs', '/list_sample_regions',
                                                              ))
def get_job (message):
    global job
    job=message.text.strip().lower()
    if job !='':
        bot.send_message(message.chat.id, 'That is a nice job ), let`s see where you would like to search, choose the region or regions separated by comma.\n'
                     'you can type /list_sample_regions to get the list of towns around Moscow.\n'
                     'type /reset to start again')
        set_state(message.chat.id, States.S_Enter_region.value)
    else:
        bot.send_message(message.chat.id, 'please enter some job name , view /lis_sample_jobs')

@bot.message_handler(func=lambda message: get_state(message.chat.id) == States.S_Enter_region.value
                     and message.text.strip().lower() not in ('/reset', '/info', '/start',
                                                              '/lis_sample_jobs', '/list_sample_regions'
                                                                    ))
def get_region (message):
    global region
    global df
    regions=message.text.strip().lower()
    region=[i.strip() for i in re.findall(r'[\w\s\-]+', regions )]
    listr1 = listr.replace('\n', '').split(',')
    listr2 = [i.strip().lower() for i in listr1]
    listerr = [i for i in region if i not in listr2]
    if listerr != [] or region ==[]:
        bot.send_message(message.chat.id, ", ".join(listerr) + ' -wrong region, check the spelling being identical to that of the list /list_sample_region.\n'  )
    else :
        bot.send_message(message.chat.id, 'That is a nice region), I will send you the results soon.\n'
                     'type /reset to start again')
        df = getstats(job, region)
        if df.values.flatten().tolist()==[]:
            bot.send_message(message.chat.id, 'either you entered a wrong job name, or the job is not to be obtained in Moscow region,\n'
                                              'Try another job, see /list_sample_jobs.')
            set_state(message.chat.id, States.S_Enter_job.value)
        else:
            bot.send_message(message.chat.id, tabulate (df, headers=df.columns, tablefmt="pipe"))

            df['jobsn'] = df['jobsn'].astype(int)
            df['starting from'] = df['starting from'].astype(int)
            def paintit():
                fig, ax = plt.subplots(figsize=(14, 10))
                ax.scatter(df['region'], df['jobsn'], s=df['starting from'] / 20, alpha=.5)
                ax.set_title('SALARIES BY NUMBER OF JOBS IN REGIONS', fontsize=20)
                ax.set_xlabel('REGION', fontsize=15)
                ax.set_ylabel('NUMBER OF JOBS', fontsize=15)
                for i, v in enumerate(df['starting from']):
                    ax.annotate(v, (df['region'][i], df['jobsn'][i]), fontsize=15, fontweight='bold')
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                return ax

            paintit().figure.savefig('demo-file.png')
            bot.send_photo(message.chat.id, photo=open('demo-file.png', 'rb'))
            set_state(message.chat.id, States.S_avg_needed.value)
            bot.send_message(message.chat.id, 'Now would you like to get Average salary histogram for the region or several regions chosen? enter /yes  or /no' )

@bot.message_handler(func=lambda message: get_state(message.chat.id) == States.S_avg_needed.value
    and message.text.strip().lower() not in ('/reset', '/info', '/start','/lis_sample_jobs', '/list_sample_regions'))
def get_avg(message):
    answer = message.text.strip().lower()
    if answer == '/yes':
        df['s*j'] = df['jobsn'] * df['starting from']
        df3 = df.groupby('region').agg({'jobsn': 'sum', 's*j': 'sum'})
        df3['avg'] = round(df3['s*j'] / df3['jobsn']).astype(int)
        df3.reset_index(inplace=True)

        def paintit2():
             ax = df3.plot.bar(x='region', y='avg', legend=False)
             ax.set_title('AVERAGE SALARY', fontsize=15)
             ax.set_xticklabels(df3['region'], rotation =0.5, ha = 'center')
             for i, v in enumerate(df3['avg']):
                ax.text(i - 0.25, v * 1.02, str(v), color='black', fontweight='bold', fontsize=12)
             ax.spines['right'].set_visible(False)
             ax.spines['top'].set_visible(False)
             return ax

        paintit2().figure.savefig('demo-file2.png')
        bot.send_photo(message.chat.id, photo=open('demo-file2.png', 'rb'))
        set_state(message.chat.id, States.S_Start.value)

    elif answer =='/no':
        set_state(message.chat.id, States.S_Start.value)
    else:
        bot.send_message(message.chat.id , ' just answer /yes or / no, please,\n'
                                               '/reset to start again\n'
                                               '/info for information')

@bot.message_handler(commands=['start'])
def greetings (message):
    bot.send_message(message.chat.id,'hi, I am salary_avg_bot type or press /info to get acquainted with me.\n'
                                      'let`s start by selecting a job,, you can view the list of sample jobs here /list_sample_jobs.\n'
                                      '/reset  to start again.\n')
    bot.send_photo(message.chat.id,picts[randint(0,2)])
    set_state(message.chat.id, States.S_Enter_job.value)

@bot.message_handler(func=lambda message: message.text not in ('/reset', '/info', '/start',
                                                              '/list_sample_jobs', '/list_sample_regions'))
def cmd_sample_message(message):
    bot.send_message(message.chat.id, "Hey there, I'm salary_avg_bot!\n"
                                      '/reset  to start again.\n'
                                      '/info to get this guidelines')

@server.route('/' + token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://agile-wildwood-50955.herokuapp.com/' + token)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
