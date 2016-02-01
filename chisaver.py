__author__ = 'Pavel Yakovlev'

import argparse
import random
import requests
import re
import os
from itertools import chain


def run(url, username, password, output):
    session = requests.Session()
    r = session.post("%slogin.asp" % url, {"UserName": username, "password": password})
    html = r.content.decode("utf8")

    pattern_urls = re.compile('<a .*href="(.*)".*>Presentations</a>')
    pre_urls = list(pattern_urls.findall(html))
    urls = ["%s%s" % (url, x) for x in pre_urls]

    pattern_names = re.compile('<h1>\s*(.*)</h1>')
    pre_names = [x.strip().replace('&amp;', 'and') for x in pattern_names.findall(html)]
    names = dict(zip([x[14:x.find('.')] for x in pre_urls], pre_names))

    pattern_pdf = re.compile('<a .*href="(.*\\.pdf)".*>')
    pdfs = []
    for presUrl in urls:
        rp = session.get(presUrl)
        htmlp = rp.content.decode("utf8")
        pdfs.append(["%s%s" % (url, x) for x in pattern_pdf.findall(htmlp)])
    pdfs = list(chain(*pdfs))

    for pdf in pdfs:
        try:
            directory = os.path.join(os.path.abspath(output), names[pdf.split("/")[-2]]).encode('ascii', 'backslashreplace')
        except:
            directory = os.path.abspath(output)
        filename = pdf.split("/")[-1].encode('ascii', 'backslashreplace')
        filepath = os.path.join(directory, filename)
        if not os.path.exists(directory):
            os.mkdir(directory)
        if not os.path.exists(filepath):
            with open(filepath, "wb") as fd:
                fd.write(session.get(pdf).content)
                print("%s is saved to %s/%s" % (filename.split(".")[0], directory, filename))
    session.close()


def main():
    parser = argparse.ArgumentParser(description='CHI Saver')
    parser.add_argument('--url', '-u', dest='url', type=str, required=True, help='conference slides url')
    parser.add_argument('--username', '-n', dest='username', type=str, required=True, help='your username')
    parser.add_argument('--password', '-p', dest='password', type=str, required=True, help='your password')
    parser.add_argument('--output', '-o', dest='output', default=".", type=str, help='output directory')
    args = parser.parse_args()
    run(args.url, args.username, args.password, args.output)


if __name__ == "__main__":
    main()
