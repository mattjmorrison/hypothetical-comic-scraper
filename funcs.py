import os
import zipfile
import requests
from bs4 import BeautifulSoup
import shutil
from config import BASE_URL
from concurrent.futures import ThreadPoolExecutor
from functools import partial


def download_series(title):
    print("Download {}".format(title))
    page = requests.get('{}/{}/001/{}/'.format(BASE_URL, title, 1))
    soup = BeautifulSoup(page.content)
    pager = soup.select('.pager select[name=chapter] option')[-1]
    issues = int(pager.text.split(' - ')[0]) + 1
    with ThreadPoolExecutor(issues) as pool:
        pool.map(partial(download_issue, title), range(1, issues))


def download_issue(title, issue_number):
    print("Download {} Issue #{}".format(title, issue_number))
    page = requests.get('{}/{}/{}/{}/'.format(BASE_URL, title, issue_number, 1))
    soup = BeautifulSoup(page.content)
    pager = soup.select('.pager select option')[-1]
    pages = int(pager.text[1:]) + 1
    dir_name = os.path.abspath(os.path.dirname(__file__))
    directory = os.path.join(dir_name, 'output', title, '{0:03d}'.format(issue_number))
    if not os.path.exists(directory):
        os.makedirs(directory)
    with zipfile.ZipFile('{}.cbz'.format(directory), 'w') as z:
        for page_number in range(1, pages):
            f = download_page(directory, title, issue_number, page_number)
            z.write(f)
    shutil.rmtree(directory)


def download_page(directory, title, issue_number, page_number):
    print("Download {} Issue #{} Page #{}".format(title, issue_number, page_number))
    page = requests.get('{}/{}/{}/{}/'.format(BASE_URL, title, issue_number, page_number))
    soup = BeautifulSoup(page.content)
    img_url = "{}/{}".format(BASE_URL, soup.select('.picture')[0]['src'])
    output_file = os.path.join(directory, '{0:03d}.jpg'.format(page_number))
    with open(output_file, 'wb') as f:
        img = requests.get(img_url, stream=True)
        img.raw.decode_content = True
        shutil.copyfileobj(img.raw, f)
    return output_file
