import re

import requests
from bs4 import BeautifulSoup


def getCookies(resultsLink):
    session = requests.Session()
    res = session.get(resultsLink)

    reg = re.compile(r'xmlhttp.open\("GET","(.+?)".+?"\+(.+?)\+.+?\+(.+?),')
    matches = reg.search(res.text)

    if matches is None:
        raise Exception('Results page not working')

    return session, matches.groups('1:4')


def getResultsPage(rollNo, session, baseLink, id, accessToken):
    baseLink = ('https://jntuaresults.ac.in/' + baseLink + rollNo + '&id=' +
                id + '&accessToken=' + accessToken)

    res = session.get(baseLink)
    return res.text


def convertToCSV(content):
    soup = BeautifulSoup(content, 'lxml')

    res = [
        [elem.next_sibling.text.strip() for elem in soup.findAll('b')],
        [elem.text.strip() for elem in soup.findAll('th') if elem.text],
    ]

    for elem in soup.findAll('tr'):
        tmp = []
        for child in elem.findAll('td'):
            if child.text:
                tmp.append(child.text)
        if tmp:
            res.append(tmp)

    res = [','.join(row) for row in res]

    if len(res) == 2:
        raise Exception('No Results Found')

    return res


def generateCSV(rollNos, link, filename):
    try:
        cookies = getCookies(link)
    except Exception as e:
        print(e)
        return

    with open(filename, 'w') as f:
        for rollNo in rollNos:
            print(rollNo + '\r', end='', flush=False)
            try:
                for row in convertToCSV(
                        getResultsPage(
                            rollNo,
                            cookies[0],
                            *cookies[1],
                        )):
                    f.write(row + '\n')
            except Exception as e:
                print(e)
                continue
            f.write('\n' * 3)


def generateRollNos(start, end):
    base = start[:-2]
    start = start[-2:]
    end = end[-2:]

    while start <= end:
        yield base + start
        unitsPlace = (int(start[-1]) + 1) % 10
        tensPlace = start[0]
        if unitsPlace == 0:
            if tensPlace.isalpha():
                tensPlace = chr(ord(tensPlace) + 1)
            else:
                tensPlace = (int(tensPlace) + 1) % 10
                if tensPlace == 0:
                    # 99 -> A0
                    tensPlace = 'A'
        start = str(tensPlace) + str(unitsPlace)


def main():
    link = input('Enter results link: ').strip()
    start = input('Enter starting roll number: ').strip().upper()
    end = input('Enter ending roll no: ').strip().upper()

    rollNos = generateRollNos(start, end)
    generateCSV(rollNos, link, 'results.csv')


if __name__ == '__main__':
    main()
