# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime, timedelta, date
import dateutil
from dateutil import parser
from dateutil.rrule import rrule, YEARLY
from time import strptime
from datetime import date
import urllib2
import os
import csv
import requests
import scraperwiki


def date_parsing(start_url, start_date, end_date):
        start_urls = [start_url % dt.strftime('%Y') for dt in rrule(YEARLY, dtstart=start_date, until=end_date)]
        for url in start_urls:
            req = urllib2.Request(url)
            req.add_header('User-agent', 'Mozilla 5.10')
            pages = urllib2.urlopen(req)
            soup = bs(pages, 'lxml')
            content_links = reversed(soup.find_all('div', 'center print-cover-links'))
            for content_link in content_links:
                content_link = content_link.find_all('a')[-1]['href']
                start_date = str(start_date).split(' ')[0]
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                date_time = content_link.split('/')[-1]
                date_time = datetime.strptime(date_time, "%Y-%m-%d")
                if start_date < date_time:
                    content_page_req = urllib2.Request('http://www.economist.com'+content_link)
                    content_page_req.add_header('User-agent', 'Mozilla 5.10')
                    content_page = urllib2.urlopen(content_page_req)
                    content_soup = bs(content_page, 'lxml')
                    content_sections = content_soup.find_all('div', 'section')
                    issue_date = content_soup.find('span', 'issue-date').text.strip()
                    issue_date = dateutil.parser.parse(issue_date)
                    issue_date = issue_date.strftime("%d/%m/%Y")
                    print issue_date
                    for content_section in content_sections:
                        nextnodes = content_section.find_all('a', 'node-link')
                        for nextnode in nextnodes:
                            if 'Business this week' in nextnode.text:
                                node_link = 'http://www.economist.com'+nextnode['href']
                                article_req = urllib2.Request(node_link)
                                article_req.add_header('User-agent', 'Mozilla 5.10')
                                article_page = urllib2.urlopen(article_req)
                                article_soup = bs(article_page, 'lxml')
                                article_body = article_soup.find('div', 'main-content').find_all('p')
                                for article in article_body:
                                    words_bold = article.find_all('em', 'Bold')
                                    if not words_bold:
                                        words_bold = article.find_all('strong')
                                        for word in words_bold:
                                            if u"’s" not in word.text:
                                                bold_word = word.text
                                                parent_word = word.parent.text
                                                yield issue_date, bold_word, parent_word
                                    for word in words_bold:
                                        if u"’s" not in word.text:
                                            bold_word = word.text
                                            parent_word = word.parent.text
                                            yield issue_date, bold_word, parent_word
                else:
                    continue



def parsing(start_url, start_date, end_date):
        start_urls = [start_url % dt.strftime('%Y') for dt in rrule(YEARLY, dtstart=start_date, until=end_date)]
        for url in start_urls:
            req = urllib2.Request(url)
            req.add_header('User-agent', 'Mozilla 5.10')
            pages = urllib2.urlopen(req)
            soup = bs(pages, 'lxml')
            content_links = reversed(soup.find_all('div', 'center print-cover-links'))
            for content_link in content_links:
                content_link = content_link.find_all('a')[-1]['href']
                content_page_req = urllib2.Request('http://www.economist.com'+content_link)
                content_page_req.add_header('User-agent', 'Mozilla 5.10')
                content_page = urllib2.urlopen(content_page_req)
                content_soup = bs(content_page, 'lxml')
                content_sections = content_soup.find_all('div', 'section')
                issue_date = content_soup.find('span', 'issue-date').text.strip()
                issue_date = dateutil.parser.parse(issue_date)
                issue_date = issue_date.strftime("%d/%m/%Y")
                print issue_date
                for content_section in content_sections:
                    nextnodes = content_section.find_all('a', 'node-link')
                    for nextnode in nextnodes:
                        if 'Business this week' in nextnode.text:
                            node_link = 'http://www.economist.com'+nextnode['href']
                            article_req = urllib2.Request(node_link)
                            article_req.add_header('User-agent', 'Mozilla 5.10')
                            article_page = urllib2.urlopen(article_req)
                            article_soup = bs(article_page, 'lxml')
                            article_body = article_soup.find('div', 'main-content').find_all('p')
                            for article in article_body:
                                words_bold = article.find_all('em', 'Bold')
                                if not words_bold:
                                    words_bold = article.find_all('strong')
                                    for word in words_bold:
                                        if u"’s" not in word.text:
                                            bold_word = word.text
                                            parent_word = word.parent.text
                                            today_date = str(datetime.now())
                                            scraperwiki.sqlite.save(unique_keys=['Date'], data={'Issue_date': issue_date, 'Word': bold_word, 'Paragraph': parent_word, 'Date': today_date})
                                            yield issue_date, bold_word, parent_word
                                else:
                                    for word in words_bold:
                                        if u"’s" not in word.text:
                                            bold_word = word.text
                                            parent_word = word.parent.text
                                            today_date = str(datetime.now())
                                            scraperwiki.sqlite.save(unique_keys=['Date'], data={'Issue_date': issue_date, 'Word': bold_word, 'Paragraph': parent_word, 'Date': today_date})

                                            yield issue_date, bold_word, parent_word
                                          

if __name__ == '__main__':

  if os.path.isfile('economist_bold.csv') is True:
    with open('yahoo.csv', 'w') as f:
        write = csv.writer(f, delimiter='|')
        write.writerow(['Date', 'Word', 'Paragraph', 'Daily Data', 'Monthly Data', 'Symbol', 'Complete Ticker Name'])
        file1 = open('economist_bold.csv', 'r')
        reader = csv.reader(file1, delimiter='|')
        lastline = reader.next()
        for row in reader:
            lastline = row
            keyword = '+'.join(lastline[1].strip().split(' '))
            yahoo_date = lastline[0].strip()
            word = lastline[1]
            paragraph = lastline[2]
            start_date_object = datetime.strptime(yahoo_date, '%d/%m/%Y') - timedelta(days=15)
            end_date_object = datetime.strptime(yahoo_date, '%d/%m/%Y') + timedelta(days=15)
            start_month = str(int(start_date_object.strftime('%m'))-1)
            start_day = start_date_object.strftime('%d')
            start_year = start_date_object.strftime('%Y')
            end_month = str(int(end_date_object.strftime('%m'))-1)
            end_day = end_date_object.strftime('%d')
            end_year = end_date_object.strftime('%Y')
            print word, yahoo_date
            title = name = ''
            try:
                yahoo_page_req = urllib2.Request('http://finance.yahoo.com/q/hp?s={}'.format(keyword.replace('&', '')))
                yahoo_page_req.add_header('User-agent', 'Mozilla 5.10')
                content_page = urllib2.urlopen(yahoo_page_req)
                content_soup = bs(content_page, 'lxml')
                try:
                    title = content_soup.find('div', 'title').find('h2').text.split('(')[-1].split(')')[0]
                    name = content_soup.find('div', 'title').find('h2').text.split('(')[0].strip()
                except:
                    try:
                       title = content_soup.find('table', 'yui-dt').find('tr', 'yui-dt-odd').find('a').text.strip()
                       name = content_soup.find('table', 'yui-dt').find('tr', 'yui-dt-odd').find('td').find_next('td').text.strip()
                    except:
                        pass
            except:
                pass
            print title
            yahoo_page_req = urllib2.Request('http://finance.yahoo.com/q/hp?s={}&a={}&b={}&c={}&d={}&e={}&f={}&g=d'.format(title, start_month, start_day, start_year, end_month, end_day, end_year))
            yahoo_page_req.add_header('User-agent', 'Mozilla 5.10')
            content_page = urllib2.urlopen(yahoo_page_req)
            content_soup = bs(content_page, 'lxml')
            daily_table_rows = ''
            try:
                daily_table_rows = content_soup.find('table', 'yfnc_datamodoutline1').find('table').find_all('tr')
            except:
                pass
            daily_row_lists = []
            for daily_table_row in daily_table_rows[1:-1]:
                daily_row_list = []
                if len(daily_table_row.find_all('td')) > 4:
                    table_date = daily_table_row.find_all('td')[0].text.strip()
                    date_object = datetime.strptime(table_date, '%b %d, %Y')
                    daily_date = date_object.strftime('%d/%m/%Y')
                    daily_open = daily_table_row.find_all('td')[1].text.strip()
                    daily_high = daily_table_row.find_all('td')[2].text.strip()
                    daily_low = daily_table_row.find_all('td')[3].text.strip()
                    daily_close = daily_table_row.find_all('td')[4].text.strip()
                    daily_row_list.append(daily_date)
                    daily_row_list.append(daily_open)
                    daily_row_list.append(daily_high)
                    daily_row_list.append(daily_low)
                    daily_row_list.append(daily_close)
                else:
                    continue
                daily_rows_data = ', '.join(daily_row_list)
                daily_row_lists.append(daily_rows_data)
            daily_row_data = '; '.join(daily_row_lists)
            monthly_start_date_object = datetime.strptime(yahoo_date, '%d/%m/%Y') - timedelta(days=365)
            monthly_end_date_object = datetime.strptime(yahoo_date, '%d/%m/%Y') + timedelta(days=365)
            monthly_start_month = str(int(monthly_start_date_object.strftime('%m'))-1)
            monthly_start_day = monthly_start_date_object.strftime('%d')
            monthly_start_year = monthly_start_date_object.strftime('%Y')
            monthly_end_month = str(int(monthly_end_date_object.strftime('%m'))-1)
            monthly_end_day = monthly_end_date_object.strftime('%d')
            monthly_end_year = monthly_end_date_object.strftime('%Y')
            yahoo_page_req = urllib2.Request('http://finance.yahoo.com/q/hp?s={}&a={}&b={}&c={}&d={}&e={}&f={}&g=m'.format(title, monthly_start_month, monthly_start_day, monthly_start_year, monthly_end_month, monthly_end_day, monthly_end_year))
            yahoo_page_req.add_header('User-agent', 'Mozilla 5.10')
            content_page = urllib2.urlopen(yahoo_page_req)
            content_soup = bs(content_page, 'lxml')
            monthly_table_rows = ''
            try:
                monthly_table_rows = content_soup.find('table', 'yfnc_datamodoutline1').find('table').find_all('tr')
            except:
                pass
            monthly_row_lists = []
            for monthly_table_row in monthly_table_rows[1:-1]:
                monthly_row_list = []
                if len(monthly_table_row.find_all('td')) > 4:
                    table_date = monthly_table_row.find_all('td')[0].text.strip()
                    date_object = datetime.strptime(table_date, '%b %d, %Y')
                    monthly_date = date_object.strftime('%d/%m/%Y')
                    monthly_open = monthly_table_row.find_all('td')[1].text.strip()
                    monthly_high = monthly_table_row.find_all('td')[2].text.strip()
                    monthly_low = monthly_table_row.find_all('td')[3].text.strip()
                    monthly_close = monthly_table_row.find_all('td')[4].text.strip()
                    monthly_row_list.append(monthly_date)
                    monthly_row_list.append(monthly_open)
                    monthly_row_list.append(monthly_high)
                    monthly_row_list.append(monthly_low)
                    monthly_row_list.append(monthly_close)
                else:
                    continue
                monthly_rows_data = ', '.join(monthly_row_list)
                monthly_row_lists.append(monthly_rows_data)
            monthly_row_data = '; '.join(monthly_row_lists)
            write.writerow([yahoo_date, word, paragraph, daily_row_data, monthly_row_data, title, name])

        lastdate = lastline[1]
        lastdate_date = lastdate[-4:]
        lastdate_year = str(int(lastdate[:-4]) + 1900)
        print lastdate_date, lastdate_year
        lastdate = lastdate_year+lastdate_date
        start_date = datetime.strptime(lastdate, '%Y%m%d')
        end_date = date.today()
        file1.close()
        with open('economist_bold.csv', 'a+') as f:
            write = csv.writer(f, delimiter='|')
            start_url = 'http://www.economist.com/printedition/covers?print_region=76980&date_filter[value][year]=%s'
            s = date_parsing(start_url, start_date, end_date)
            for l in s:
                   write.writerow([l[0], l[1], l[2]])

  else:
        with open('economist_bold.csv', 'w') as f:
            write = csv.writer(f, delimiter='|')
            write.writerow(['Date', 'Word', 'Paragraph'])
            start_url = 'http://www.economist.com/printedition/covers?print_region=76980&date_filter[value][year]=%s'
            start_date = date(1997, 1, 1)
            end_date = date.today()
            s = parsing(start_url, start_date, end_date)
            for l in s:
                   write.writerow([l[0], l[1], l[2]])
