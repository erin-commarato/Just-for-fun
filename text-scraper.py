'''
Scrapes through a given URL and produces a text representation of the page
and saves as a local text file

Usage:
Adjust the following variables
#url for the page
url = "http://www.example.com/"

#max pages to crawl
max = 10

TODO
- break if website stops responding
- test if a page doesn't have a header
- break if file is not writable

NOTES:
I am a polite crawler that will crawl at a rate of 1 second per page. I also
respects robots.txt
Does not assume www.example.com is the same as example.com
Does not crawl images, binary documents or hashtag links
'''
import requests
import re
import time
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib import robotparser

#url for the page
url = "http://www.example.com/"

#max pages to crawl
max = 10

class Crawler(object):
    filter_tags = ['style', 'script', '[document]', 'head', 'title', 'nav', 'header', 'footer']
    filter_formats = ['.txt', '.jpg', '.png', '.doc', '.docx', '.pdf', '.ppt', '.pptx', '.py', '.exe', '.dmg']

    def __init__(self, url, max):
        self.processed = []
        self.discovered = []
        self.url = url
        self.max = max
        self.base_url = urlparse(url).scheme + '://' +  urlparse(url).netloc
        self.crawl()

    def crawl(self):
        '''
        Main function for crawling entire URL
        '''
        print('crawling: %s' %self.url)

        self.discover(url)

        #get filename from url, used for saving text to file system later
        filename = urlparse(url).netloc + '.txt'

        #while there are still items in the discovered queue
        #or counter is less than max allowed

        max_count = self.max
        count = 0

        #print out some interesting info captured from the headers
        self.process_headers(filename)

        while self.discovered and count < max_count:
            #parse items
            next_link = self.discovered.pop(0)
            self.process(next_link, filename)

            #sleep for 1 second between requests
            time.sleep(1)
            count += 1

        print('Total pages crawled: %d' %count)

    def process_headers(self, filename):
        if (self.can_proceed(self.url)):
            page = requests.get(self.url)
            texts = str(page.headers)
            self.write_page_to_file(texts, filename, 'Site Headers', '')

    def process(self, url, filename):
        print("Next link to process is %s" %url)

        url = self._normalize_relative_links(url)

        if self.can_proceed(url):

            page = requests.get(url)
            pagename = urlparse(url).path
            if self.page_loaded(page):
                self.get_links(page, url)
                parsed_page = self.parse(page, url)
                parsed_text = parsed_page[0]
                heading = parsed_page[1]
                self.write_page_to_file(parsed_text, filename, pagename, heading)

    def can_proceed(self, url):
        #tries to grab the page with requests
        #and makes sure we are allowed to crawl it
        #returns True or False depending on whether we can proceed

        can_proceed = True
        url = self._normalize_relative_links(url)

        try:
            page = requests.get(url)
            if ('text/html' not in page.headers['Content-Type']):
                #only grab html and text-based pages
                can_proceed = False
        except:
            #link was badly formatted ex: //file instead of http://file
            print('Missing schema or related exception raised')
            can_proceed = False

        #check robots to see if we can fetch a given URL
        #setup robot file parser
        rp = robotparser.RobotFileParser()
        robots_url = url+'/robots.txt'
        rp.set_url(robots_url)
        rp.read()

        allowed_to_fetch = rp.can_fetch('*', url)

        #thumbs up
        if can_proceed and allowed_to_fetch:
            return True
        else:
            return False

        print('done with can_proceed')

    def page_loaded(self, request):
        if request.status_code == 200:
            return True

    def parse(self, page, url):
        soup = self.convert_to_soup(page)

        #kill all script and style elements
        for script in soup(Crawler.filter_tags):
            script.extract() #rip it out

        #get text
        texts = soup.get_text()

        #get first headline you see
        heading = soup.find(['h1', 'h2', 'h3', 'h4', 'h5'])
        if heading:
            heading = heading.get_text()
        else:
            heading = ''

        #filter out tab and newlines
        texts = texts.replace('\n', ' ')
        texts = texts.replace('\t', ' ')

        return (texts, heading)

    def write_page_to_file(self, texts, filename, pagename, heading):
        file = open(filename, 'a')
        file.write('\n\n================= %s =================\n\n' %pagename)
        file.write('\n%s\n' %heading)

        for text in texts:
            if text != '':
                file.write(text)

        file.write('\n')
        file.close()

    def get_links(self, page, url):
        '''
        Gets all links for a page
        '''
        soup = self.convert_to_soup(page)
        for link in [a.get('href') for a in soup.find_all('a')]:
            if self.is_valid_link(link, url):
                self.discover(link)

    def convert_to_soup(self, page):
        '''
        Converts response object to BeautifulSoup object
        '''
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def discover(self, link):
        #link has already been processed
        if link in self.processed:
            return

        #link has already been discovered, but not yet processed
        if link in self.discovered:
            return

        #if format is in the exclusion list, do nothing
        filename, file_extension = os.path.splitext(link)
        if file_extension in self.filter_formats:
            return

        #completely undiscovered, unprocessed link
        self.discovered.append(link)

    def is_valid_link(self, link, url):
        '''
        Returns True if link is valid, False otherwise
        Valid links are synatically valid internal links which are
        http or https
        relative, absolute or hash links
        '''

        parent_url = urlparse(url)
        parsed_link = urlparse(link)
        is_valid = True

        #only allow http or https schemes
        if parsed_link.scheme != '':
            if parsed_link.scheme != 'http' and parsed_link.scheme != 'https':
                is_valid = False

        #is link internal?
        if self._normalize_url(parsed_link.netloc) != self._normalize_url(parent_url.netloc):
            #not a relative link
            if parsed_link.netloc != '':
                is_valid = False

        #is link a hash link?
        if parsed_link.netloc == '' and parsed_link.path == '' and parsed_link.fragment == '':
            is_valid = False

        return is_valid

    def _normalize_url(self, url):
        #normalize domains to test for www vs non-www
        #remove www. and return result

        url = re.sub('www.', '', url)

        return url

    def is_relative(self, url):
        '''
        Returns True or False depending on whether the url is relative
        '''
        url = urlparse(url)
        return url.scheme == '' and url.netloc == ''


    def _normalize_relative_links(self, url):
        '''
        Joins relative links with the base url
        '''
        if self.is_relative(url):
            url = urljoin(self.base_url, url)
        return url


#init Crawler
crawler = Crawler(url, max)
