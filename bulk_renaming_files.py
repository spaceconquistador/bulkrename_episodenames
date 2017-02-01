import os
import os.path
import requests
from bs4 import BeautifulSoup
import sys
from urllib.parse import urlparse
import re

basedir = input('What is the full directory of the folder that contains the files?')
os.chdir(basedir)
filetypes = ('.mp4', '.avi', '.mkv')

def sort_alphanum(list):
    """ Sorts the video_files list into numerical order even if the file name contains letters"""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(list, key = alphanum_key)

def directory(basedir):
    '''renames any mp4, avi and mkv files in the target directory to ([number][extension])
    format, e.g. 01.mp4, 02.mp4,...'''

    num_files = os.listdir(basedir)
    video_files = sort_alphanum([k for k in num_files if k.endswith(filetypes)])
    for files in video_files:
        old_name, extension = os.path.splitext(files)

    for index, file in enumerate(video_files, 1):
        old_name, extension = os.path.splitext(file)
        new_name = '{}{}'.format(str(index).zfill(2), extension)
        try:
            os.rename(file, new_name)
        except (OSError,FileNotFoundError):
            print ('Failed to rename %s to %s') %(old_name, new_name)
    website()

def website():
    '''user to input to check from which site they wish to scrape episode name info'''
    print ('''

Enter the website from which you wish to get the episode names from. This script can
only fetch episode info from animelist, wikipedia or imdb. The links must be in
the following format:

    https://myanimelist.net/anime/790/Ergo_Proxy/episode
    https://en.wikipedia.org/wiki/List_of_Buffy_the_Vampire_Slayer_episodes
    http://www.imdb.com/title/tt0367279/episodes?season=1

    If you wish to cancel, type 'exit' ''')

    scrapefrom = input ('>...')
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
        print ('\nThat\'s not a website I can scrape from, only animelist, wikipedia or imdb.')
        website()

def wikipedia(url):
    '''fetching a list of episode names from wikipedia'''
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    info = soup.find_all('td', {'class':'summary'})
    episodenames_list = [item.text for item in info]
    check(episodenames_list)

def animelist(url):
    '''fetching list of episode names from animelist'''
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    info = soup.find_all('a', {'class':'fl-l fw-b '})
    episodenames_list = [item.text for item in info]
    check(episodenames_list)

def imdb(url):
    '''fetching a list of episode names from imdb'''
    r = requests.get(url)
    soup = BeautifulSoup(r.content,'lxml')
    info = soup.find_all('div', {'class':'info'})
    episodenames_list = [item.contents[5].text for item in info]
    check(episodenames_list)

def check(episodenames_list):

    '''ensuring that only mp4, avi and mkv files are renamed and checking the number of
    episodes from the website matches the number of episodes in the target directory'''

    num_files = os.listdir(basedir)
    video_files = sorted([k for k in num_files if k.endswith(filetypes)])

    if len(video_files) != len(episodenames_list):
        print ('''
        The number of files in the directory do not match the number of
        episodes in the website's list.

        The number of files in your directory are {}.

        The number of episodes on the website are {}.

        Please check that you have all the correct files or that you have entered
        the correct link for that TV show.'''.format(len(video_files), len(episodenames_list)))

        answer = input('Do you still wish to continue? Yes/No \n>....')
        if 'y' in answer:
            combining(episodenames_list, video_files)
        else:
            sys.exit()
    else:
        combining(episodenames_list, video_files)

def combining(episodenames_list, video_files):
    ''' combining the name of the files in the directory with the names of the episodes
    captured from a website'''

    combined_file_name = []

    for episode_name, file_name in zip(episodenames_list, video_files):

        episode_name.strip('"')
        episode_num, file_ext = os.path.splitext(file_name)
        combined_file_name.append('{} - {}{}'.format(episode_num, episode_name, file_ext))

    rename(combined_file_name)

def rename(combined_file_name):
    all_files = sorted(os.listdir(basedir))
    files = [file for file in all_files if file.endswith(filetypes)]

    print ('The files will be renamed into the following format: ')
    for rename_check in zip(files, combined_file_name):
        print (rename_check)

    answer = input('Do you want to continue with the rename? y/n \n>...')
    if 'y' in answer:
        for old_name, new_name in zip(files, combined_file_name):
            try:
                os.rename(old_name, new_name)
            except(OSError, FileNotFoundError):
                print ('Error. Failed to rename files.')


directory(basedir)
