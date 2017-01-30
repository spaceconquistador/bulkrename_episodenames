import os
import os.path
import requests
from bs4 import BeautifulSoup
import sys
from urlparse import urlparse


basedir = raw_input('What is the full directory of the folder that contains the files?')
os.chdir(basedir)
f = []
episodelist = []
combined_file_name = []

def directory():
    '''renames any mp4, avi and mkv files in the target directory to ([number][extension])
    format, e.g. 01.mp4, 02.mp4,...'''

    num_files = os.listdir(basedir)
    global video_files
    video_files = []
    fresh = []

    for k in num_files:
        if '.mp4' in k or '.avi' in k  or '.mkv' in k:
            video_files.append(k)

    for files in video_files:
        old_name, extension = os.path.splitext(files)
    a = 1
    while a < (len(video_files)+1):
        new_name = '%s%s' %(str(a).zfill(2), extension)
        fresh.append(new_name)
        a += 1

    b = 0
    while b != len(video_files):
        for oldfiles in sorted(num_files):
            if oldfiles.endswith('.mp4') or oldfiles.endswith ('.mkv') or oldfiles.endswith('.avi'):
                try:
                    os.rename(oldfiles,fresh[b])
                    b += 1
                except IndexError:
                    if len(video_files) > len(fresh):
                        video_files.pop(-1)
                        continue
                    elif len(fresh) > len(video_files):
                        fresh.pop(-1)
                        continue
    website()


def website():
    '''user to input to check from which site they wish to scrape episode name info'''

    print '''

Enter the website where you wish to get the episode list from. This script can
only fetch episode info from animelist, wikipedia or imdb. The links must be in
the following format:

    https://myanimelist.net/anime/790/Ergo_Proxy/episode
    https://en.wikipedia.org/wiki/List_of_Buffy_the_Vampire_Slayer_episodes
    http://www.imdb.com/title/tt0367279/episodes?season=1

    If you wish to cancel, type 'exit' '''

    scrapefrom = raw_input ('>...')
    parsed_scrapefrom = urlparse(scrapefrom)
    if 'en.wikipedia.org' in parsed_scrapefrom:
        wikipedia(scrapefrom)
    elif 'myanimelist.net' in parsed_scrapefrom:
        animelist(scrapefrom)
    elif 'www.imdb.com' in parsed_scrapefrom:
        imdb(scrapefrom)
    elif 'exit' in scrapefrom:
        sys.exit()
    else:
        print '\nThat\'s not a website I can scrape from, only animelist, wikipedia or imdb.'
        website()


def wikipedia(url):
    '''fetching a list of episode names from wikipedia'''
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    info = soup.find_all('td', {'class':'summary'})
    for item in info:
        episodelist.append(item.text)

    check()


def animelist(url):
    '''fetching list of episode names from animelist'''
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    info = soup.find_all('a', {'class':'fl-l fw-b '})
    for item in info:
        episodelist.append(item.text)
    check()

def imdb(url):
    '''fetching a list of episode names from imdb'''
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    info = soup.find_all('div', {'class':'info'})
    for item in info:
        episodelist.append(item.contents[5].text)

    check()

def check():
    '''ensuring that only mp4, avi and mkv files are renamed and checking the number of
    episodes from the website matches the number of episodes in the target directory'''

    filetype = '.mp4','.avi', '.mkv'
    raw_files_list = (os.listdir(basedir))
    for i in raw_files_list:
        if '.mp4' in i or '.avi' in i  or '.mkv' in i:
            f.append(i)
            f.sort()
    if len(f) != len(episodelist):
        print '''
The number of files in the directory do not match the number of
episodes in the website's list.

The number of files in your directory are %r.

The number of episodes on the website are %r.

Please check that you have all the correct files or that you have entered
the correct link for that TV show.''' %(len(f), len(episodelist))

        check = raw_input('Do you still wish to continue? Yes/No \n>....')
        if 'y' in check:
            combining()
        else:
            sys.exit()
    else:
        combining()


def combining():
    ''' combining the name of the files in the directory with the names of the episodes
    captured from a website'''
    c = 0
    while c < len(episodelist):
        try:
            new_name = '%s-%s' %(episodelist[c],f[c])
            new_name, file_ext = os.path.splitext(new_name)
            ep_name,ep_number = new_name.rsplit("-",1)
            ep_name = ep_name.strip('"')
            combined_file_name.append('%s - %s%s' %(ep_number,ep_name,file_ext))
            c += 1
        except IndexError:
            if len(f) > len(episodelist):
                f.pop(-1)
                continue
            elif len(f) < len(episodelist):
                episodelist.pop(-1)
                continue
    for filenames in combined_file_name:
        print filenames
    check = raw_input('Do you want to continue to rename? Y/N')
    if 'y' in check:
        rename()
    else:
        sys.exit()


def rename():
    '''the renaming step of the process'''
    d = 0
    while d < (len(episodelist)):
        for files in sorted(os.listdir(basedir)):
            if files.endswith('.mp4') or files.endswith ('.mkv') or files.endswith('.avi'):
                try:
                    os.rename(files,combined_file_name[d])
                    d += 1
                except IndexError:
                    if len(video_files) > len(episodelist):
                        video_files.pop(-1)
                        continue
                    elif len(video_files) < len(episodelist):
                        episodelist.pop(-1)
                        continue


directory()
