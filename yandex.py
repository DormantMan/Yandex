#! /usr/bin/env python
# -*- coding: utf-8 -*

#
#
#               YANDEX PARSERS
#
#         1. Yandex Contests Parser
#         2. Yandex Lms Parser
#
#
#
#    This version: 0.1.3a
#
#
#    UPDATE:    https://github.com/DormantMan/Yandex
#
#
#
#
#   A parser is a software component that takes input data (frequently text)
#   and builds a data structure – often some kind of parse tree, abstract syntax tree or
#   other hierarchical structure – giving a structural representation of the input,
#   checking for correct syntax in the process.
#   The parsing may be preceded or followed by other steps,
#   or these may be combined into a single step.
#
#   The parser is often preceded by a separate lexical analyser,
#   which creates tokens from the sequence of input characters;
#   alternatively, these can be combined in scannerless parsing.
#
#   Parsers may be programmed by hand or
#   may be automatically or semi-automatically generated by a parser generator.
#   Parsing is complementary to templating, which produces formatted output.
#   These may be applied to different domains,
#   but often appear together,
#   such as the scanf/printf pair,
#   or the input (front end parsing)
#   and output (back end code generation) stages of a compiler.
#
#
#
#       Author: DormantMan
#


# IMPORTS

import os
import pickle
import sys
import threading
from getpass import getpass
from pathlib import Path

try:

    import requests
    import lxml.html
    import bs4

except ImportError:

    print(' --- ImportError ---')

    os.system('pip install requests lxml beautifulsoup4')
    os.system('pip3 install requests lxml beautifulsoup4')

    import requests
    import lxml.html
    import bs4

    print()


class Yandex:
    version = '0.1.3a'


class YandexLyceum(Yandex):
    def __init__(self):

        print('YandexLyceum %s' % Yandex.version)

        self.ver = Yandex.version

        self.s = requests.session()
        self.login = False

        self.balls = 0

        self.threadingLessons = 0
        self.threadingTasks = 0

        self.operatingLessons = {}
        self.operatingTasks = {}

        self.LessonPrint = False
        self.TasksPrint = False

        self.load_cookies('cookies.dm', False)

        if not self.get_status():
            username = input('Username: ')
            password = getpass('Password: ')

            if self.auth(username, password):
                self.save_cookies()

            else:
                return

        self.update()

    def update(self):
        url_update = 'https://raw.githubusercontent.com/DormantMan/Yandex/master/yandex.py'
        url_version = 'https://raw.githubusercontent.com/DormantMan/Yandex/master/version.txt'

        try:

            version = requests.get(url_version).text.strip()

            if version != self.ver:

                print()
                print(' --- Update ---')
                print('New version: %s' % version)
                print()

                code = requests.get(url_update).text.strip().replace('\r', '')

                start = str(Path(sys.argv[0]))
                reupdate = str(Path(__file__))

                with open(reupdate, 'w', encoding='utf-8') as file:
                    file.write(code)

                os.system('python %s' % start)
                exit(0)
                return True

            else:
                return

        except ConnectionError:
            print(' --- Error Update ---')

        except IndexError:
            print(' --- Error Update ---')

    def auth(self, username, password):

        if self.login:
            print('You are already authorized.')
            return True

        url = 'https://lms.yandexlyceum.ru/accounts/login/'
        login = self.s.get(url)
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
        form['username'], form['password'] = username, password

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

        response = self.s.post(url, data=form, headers=headers)

        if response.url == 'https://lms.yandexlyceum.ru/accounts/profile/':
            self.login = True
            print('OK')
            return True

        else:
            print('-Wrong username or password!-')
            return False

    def get_status(self):
        return self.login

    def save_cookies(self, filename='cookies.dm'):
        print('Save cookies ...')
        try:
            with open(filename, 'wb') as cookies:
                pickle.dump(self.s.cookies, cookies)
        except IOError:
            print('-Error save cookies-')

    def load_cookies(self, filename='cookies.dm', main=True):
        if main:
            print('Loading cookies ...')

        try:
            file_cookies = open(filename, 'rb')
            self.s.cookies = pickle.load(file_cookies)
            file_cookies.close()

        except IOError:
            if main:
                print('-Error Loading cookies-')

        if bs4.BeautifulSoup(
                self.s.get('https://lms.yandexlyceum.ru/accounts/profile/').content,
                "lxml"
        ).find('a', {'href': '/course/36'}):
            self.login = True
            print('Cookies loaded.')
            return True

        self.login = False

        if main:
            print('Cookies not loaded.')

        return False

    def profile(self):
        if not self.login:
            print('You are not authorized.')
            return

        print('Loading profile info ...')
        url = 'https://lms.yandexlyceum.ru/accounts/profile'

        try:
            r = self.s.get(url)
            html = lxml.html.fromstring(r.text)

            body = html.xpath(r'//title')
            name = body[0].text.strip()

            body = html.xpath(r'//div//span[@class="label label-status"]')
            city = body[0].text.strip()
            year = body[1].text.strip()

            url = 'https://lms.yandexlyceum.ru/user/my_tasks/'

            r = self.s.get(url)
            html = lxml.html.fromstring(r.text)

            body = [int(i.text.strip()) for i in html.xpath(r'//td') if i.text is not None and i.text.strip().isdigit()]
            balls = sum(body)
            not_ok = body.count(0)

            print()
            print(' - Profile Info - ')
            print("%s: %s, %s" % (name, city, year))
            print('Points: %s' % balls)
            print('Not decided: %s ' % not_ok)

            url = 'https://lms.yandexlyceum.ru/user/courses/attendance'

            r = self.s.get(url)
            html = lxml.html.fromstring(r.text)

            alls = int(html.xpath(r'//td//label[@class="label label-inverse big-label"]')[0].text)
            success = int(html.xpath(r'//td//label[@class="label label-success big-label"]')[0].text)

            print()
            print(' - My attendance - ')
            print("Total: %s\nVisited: %s\nSkipped: %s" % (alls, success, alls - success))

            print()

        except ConnectionError:
            print('Error get profile info.')

        except IndexError:
            print('Error get profile info.')

        except TypeError:
            print('Error get profile info.')


def _lessons_parse_print_(self, f, t):
    self.LessonPrint = True

    for i in range(f, t):
        while i not in self.operatingLessons:
            pass

        if self.operatingLessons[i] is None:
            continue

        print()
        print('URL: https://lms.yandexlyceum.ru/course/36/seminar/%s' % i)
        print(self.operatingLessons[i])
        print()

    self.LessonPrint = False


def _tasks_parse_print_(self, f, t):
    self.TasksPrint = True

    for i in range(f, t):
        while i not in self.operatingTasks:
            pass

        if self.operatingTasks[i] is None:
            continue

        print()
        print('URL: https://lms.yandexlyceum.ru/issue/%s' % i)
        print(self.operatingTasks[i]['name'])
        print('Статус: %s' % self.operatingTasks[i]['status'])
        print('Оценка: %s' % self.operatingTasks[i]['value'])
        print()

    self.TasksPrint = False


def _lessons_parse_threading_(self, url, i):
    self.threadingLessons += 1

    while True:
        try:
            r = self.s.get(url % i)
            break
        except ConnectionError:
            pass

    try:
        html = lxml.html.fromstring(r.text)
        body = html.xpath(r'//div//h5[@class="card-title main-title"]')

        if len(body) == 0:
            raise IndexError

        self.operatingLessons[i] = body[0].text.strip()

    except IndexError:
        self.operatingLessons[i] = None
        pass

    self.threadingLessons -= 1


def _tasks_parse_threading_(self, url, i):
    self.threadingTasks += 1

    while True:
        try:
            r = self.s.get(url % i)
            break
        except ConnectionError:
            pass

    try:
        html = lxml.html.fromstring(r.text)
        body = html.xpath(r'//div//a[@id="modal_task_description_btn"]')

        if len(body) == 0:
            raise IndexError

        name = body[0].text.strip()

        body = html.xpath(r'//div//div[@class="col-md-7 accordion2-result"]')
        status = body[5].text.strip()
        value = body[6].text.strip()

        self.operatingTasks[i] = {'name': name, 'status': status, 'value': value}

        self.balls += int(body[6].text.strip())

    except IndexError:
        self.operatingTasks[i] = None
        pass

    self.threadingTasks -= 1


def parse_lessons(self, f, t):
    if not self.login:
        print('You are not authorized.')
        return

    try:
        f, t = abs(int(f)), abs(int(t))

    except TypeError:
        print('-Bad Input-')
        return

    except ValueError:
        print('-Bad Input-')
        return

    print('Start parse lessons ...')

    threading.Thread(target=self._lessons_parse_print_, args=[f, t]).start()

    url = 'https://lms.yandexlyceum.ru/course/36/seminar/%s'
    for i in range(f, t + 1):
        while self.threadingLessons > 400:
            pass

        while True:
            try:
                threading.Thread(
                    target=self._lessons_parse_threading_,
                    args=[url, i]
                ).start()
                break

            except ConnectionError:
                pass

    while self.LessonPrint:
        pass


def parse_tasks(self, f, t):
    if not self.login:
        print('You are not authorized.')
        return

    try:
        f, t = abs(int(f)), abs(int(t))

    except TypeError:
        print('-Bad Input-')
        return

    except ValueError:
        print('-Bad Input-')
        return

    threading.Thread(target=self._tasks_parse_print_, args=[f, t]).start()

    self.balls = 0

    print('Start parse tasks ...')

    url = 'https://lms.yandexlyceum.ru/issue/%s'
    for i in range(f, t + 1):
        while self.threadingTasks > 400:
            pass

        while True:
            try:
                threading.Thread(target=self._tasks_parse_threading_, args=[url, i]).start()
                break
            except ConnectionError:
                pass

    while self.TasksPrint:
        pass

    print('Your balls: %s' % self.balls)


class YandexContest(Yandex):
    def __init__(self):

        print('YandexContest %s' % Yandex.version)

        self.ver = Yandex.version

        self.s = requests.session()
        self.login = False
        self.threading = 0
        self.operating = {}

        self.load_cookies('cookies.dm', False)

        if not self.get_status():
            username = input('Username: ')
            password = getpass('Password: ')

            if self.auth(username, password):
                self.save_cookies()

            else:
                return

        self.update()

    def update(self):
        url_update = 'https://raw.githubusercontent.com/DormantMan/Yandex/master/yandex.py'
        url_version = 'https://raw.githubusercontent.com/DormantMan/Yandex/master/version.txt'

        try:

            version = requests.get(url_version).text.strip()

            if version != self.ver:
                print()
                print(' --- Update ---')
                print('New version: %s' % version)
                print()

                code = requests.get(url_update).text.strip().replace('\r', '')

                start = str(Path(sys.argv[0]))
                reupdate = str(Path(__file__))

                with open(reupdate, 'w', encoding='utf-8') as file:
                    file.write(code)

                os.system('python %s' % start)
                exit(0)
                return True

            else:
                return

        except ConnectionError:
            print(' --- Error Update ---')

    def get_status(self):
        return self.login

    def auth(self, login, password):
        if self.login:
            print('You are already authorized.')
            return True

        url = 'https://passport.yandex.ru/auth'

        form = {'login': login, 'passwd': password, 'retpath': 'https://passport.yandex.ru/profile'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}

        self.s.post(url, data=form, headers=headers)

        if bs4.BeautifulSoup(
                self.s.get('https://passport.yandex.ru/profile/').content,
                "lxml"
        ).find('div', {'class': 'personal-info-name'}):
            self.login = True
            print('OK')
            return True

        else:
            print('-Wrong login or password!-')
            return False

    def save_cookies(self, filename='cookies.dm'):
        print('Save cookies ...')
        try:
            with open(filename, 'wb') as cookies:
                pickle.dump(self.s.cookies, cookies)
        except IOError:
            print('-Error save cookies-')

    def load_cookies(self, filename='cookies.dm', main=True):
        if main:
            print('Loading cookies ...')

        try:
            with open(filename, 'rb') as f:
                self.s.cookies = pickle.load(f)
        except IOError:
            print('-Error Loading cookies-')

        if bs4.BeautifulSoup(
                self.s.get('https://passport.yandex.ru/profile/').content,
                "lxml"
        ).find('div', {'class': 'personal-info-name'}):
            self.login = True
            if main:
                print('Cookies loaded.')
            return True

        self.login = False
        if main:
            print('Cookies not loaded.')
        return False

    def profile(self):
        if not self.login:
            print('You are not authorized.')
            return

        print('Loading profile info ...')
        url = 'https://passport.yandex.ru/profile/'

        try:

            content = self.s.get(url).content

            body = bs4.BeautifulSoup(
                content,
                "lxml").find('div', {'class': 'personal-info-name'})

            name = body.text

            body = bs4.BeautifulSoup(
                content,
                "lxml").find('div', {'class': 'personal-info-login personal-info-login__displaylogin'})
            login = body.text.strip()

            body = bs4.BeautifulSoup(
                content,
                "lxml").find('div', {'class': 'last-auth'})
            date = body.text.replace('История входов', '')

        except ConnectionError:
            print('Error get info about profile.')
            return

        except IndexError:
            print('Error get info about profile.')
            return

        except TypeError:
            print('Error get info about profile.')
            return

        print("\n%s: %s\n%s\n" % (name, login, date))

    def _parse_print(self, f, t, word):
        word = word.lower()
        for i in range(f, t):
            while i not in self.operating:
                pass

            if self.operating[i] is None:
                continue

            if word is None or word == '':
                print(self.operating[i], i, sep='\t')
            else:
                if word in self.operating[i].lower():
                    print(self.operating[i], i, sep='\t')

    def _parse_(self, url, i):
        self.threading += 1

        while True:
            try:
                enter_request = self.s.get(url)
                break
            except ConnectionError:
                pass

        enter_html = bs4.BeautifulSoup(enter_request.content, "lxml")
        name = enter_html.find('div', {'class': 'contest-head__item contest-head__item_role_title'})
        try:
            if name:
                name = name.string
                self.operating[i] = name

            elif enter_html.find(
                    'div',
                    {'class': 'msg msg_type_warn msg_theme_island'}
            ).contents[1] == 'У вас нет прав просматривать это соревнование':
                self.operating[i] = None

        except AttributeError:
            self.operating[i] = None
            pass

        self.threading -= 1

    def parse(self, f, t, word=None):
        if not self.login:
            print('You are not authorized.')
            return

        try:
            f, t = abs(int(f)), abs(int(t)) + 1

        except TypeError:
            print('-Bad Input-')
            return

        except ValueError:
            print('-Bad Input-')
            return

        threading.Thread(target=self._parse_print, args=[f, t, word]).start()

        for i in range(f, t):
            while self.threading > 400:
                pass

            while True:
                try:
                    threading.Thread(target=self._parse_, args=[
                        'https://contest.yandex.ru/contest/%s/' % i,
                        i
                    ]).start()
                    break
                except ConnectionError:
                    pass
