#!/usr/bin/python

# askstack 0.1.0
# author: Pedro Buteri Gonring
# email: pedro@bigode.net
# date: 20171221

import sys
import random
import optparse
import time
import urllib2

import requests
from lxml import html


version = '0.1.0'


# Parse and validate arguments
def get_parsed_args():
    usage = 'usage: %prog keywords... [options]'
    # Create the parser
    parser = optparse.OptionParser(
        description='search answers on stackoverflow',
        usage=usage, version=version
    )
    parser.add_option(
        '-a', dest='answers', default=2, type=int,
        help="number of answers to retrieve (default: %default)"
    )
    parser.add_option(
        '-e', dest='engine', default='fallback',
        choices=('google', 'bing', 'duckduckgo', 'fallback'),
        help="search engine to use: 'google', 'bing', 'duckduckgo' or "
        "'fallback' - fallback will try google and fallback to bing and "
        "duckduckgo if a search fails (default: %default)"
    )
    parser.add_option(
        '-f', '--fulltext', action='store_true', default=False,
        help='get the full answer text (default: disabled)'
    )
    parser.add_option(
        '-s', dest='sleep', default=0.5, type=float,
        help='sleep time between requests (default: %default)'
    )
    parser.add_option(
        '-t', dest='timeout', default=5, type=int,
        help='timeout in seconds to wait for reply (default: %default)'
    )

    # Print help if no argument is given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(2)

    # Parse the args
    (options, args) = parser.parse_args()

    # Some args validation
    if len(args) == 0:
        parser.error('at least one keyword is needed')
    if options.answers < 1 or options.answers > 10:
        parser.error('number of answers must be between 1 and 10')
    if options.sleep <= 0:
        parser.error('sleep time must be a positive number')
    if options.timeout < 1:
        parser.error('timeout must be a positive number')
    return (options, args)


# Return a random user agent
def get_random_user_agent():
    chrome = ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
              'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36')
    firefox = ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) '
               'Gecko/20100101 Firefox/54.0',
               'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) '
               'Gecko/20150101 Firefox/47.0 (Chrome)')
    safari = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) '
              'AppleWebKit/601.7.7 (KHTML, like Gecko) '
              'Version/9.1.2 Safari/601.7.7',)
    user_agents = chrome + firefox + safari
    user_agent = random.choice(user_agents)
    return user_agent


# Return the http response, context is used to customize the error message
def get_http_response(url, user_agent, timeout, context):
    headers = {'user-agent': user_agent}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return 'Error: Could not connect to %s' % context
    except requests.exceptions.Timeout:
        return 'Error: Connection to %s timed out after %s seconds' \
            % (context, timeout)

    if resp.status_code != 200:
        return 'Error: Failed request to %s, status code: %s' \
            % (context, resp.status_code)

    return resp


# Return urls from Google search
def search_google(keywords, user_agent, timeout):
    base_url = 'https://www.google.com/'
    params = 'search?q=site:stackoverflow.com+%s' % keywords.rstrip()
    url = base_url + params
    resp = get_http_response(url, user_agent, timeout, 'Google')
    if type(resp) is str:
        return resp
    tree = html.fromstring(resp.text)
    urls = tree.xpath('//h3[@class="r"]//@href')
    if not urls:
        return 'Error: No urls found from Google search'
    return urls


# Return urls from Bing search
def search_bing(keywords, user_agent, timeout):
    base_url = 'https://www.bing.com/'
    params = 'search?q=site:stackoverflow.com+%s' % keywords.rstrip()
    url = base_url + params
    resp = get_http_response(url, user_agent, timeout, 'Bing')
    if type(resp) is str:
        return resp
    tree = html.fromstring(resp.text)
    urls = tree.xpath('//li[@class="b_algo"]//h2//a//@href')
    if not urls:
        return 'Error: No urls found from Bing search'
    return urls


# Return urls from DuckDuckGo search
def search_duckduckgo(keywords, user_agent, timeout):
    base_url = 'https://duckduckgo.com/html/'
    params = '?q=site:stackoverflow.com+%s' % keywords.rstrip()
    url = base_url + params
    resp = get_http_response(url, user_agent, timeout, 'DuckDuckGo')
    if type(resp) is str:
        return resp
    tree = html.fromstring(resp.text)
    urls = tree.xpath('//a[@class="result__a"]//@href')
    if not urls:
        return 'Error: No urls found from DuckDuckGo search'
    return urls


# Search Google, if fails search Bing, if fails search DuckDuckGo
def search_fallback(keywords, user_agent, timeout):
    urls = search_google(keywords, user_agent, timeout)
    # If urls is not a list, it is a string containing an error
    if type(urls) is list:
        return urls
    # Print the error and try Bing
    print urls
    print '\nTrying Bing...'
    urls = search_bing(keywords, user_agent, timeout)
    if type(urls) is list:
        return urls
    # Print the error and try DuckDuckGo
    print urls
    print '\nTrying DuckDuckGo...'
    urls = search_duckduckgo(keywords, user_agent, timeout)
    if type(urls) is list:
        return urls
    # Return an error if all fails
    return urls


# Return the full html from stackoverflow page
def get_stack_html(url, user_agent, timeout):
    if not validate_stack_url(url):
        return 'Error: "%s" is not a valid Stack Overflow question page\n' \
            % url
    resp = get_http_response(url, user_agent, timeout, 'Stack Overflow')
    # If it is not a response object, it is a string containing an error
    if type(resp) is str:
        return resp + '\nURL: %s\n' % url
    return resp.text


# Get the question title on the html
def get_question_title(raw_html):
    tree = html.fromstring(raw_html)
    question_title = tree.xpath('//h1//a[@class="question-hyperlink"]//text()')
    if not question_title:
        return 'No question title found on page'
    return question_title[0]


# Get the first code snippet on the html
def get_code_snippet(raw_html):
    tree = html.fromstring(raw_html)
    snippets = tree.xpath('//td[@class="answercell"]//div[@class="post-text"]'
                          '//pre//code//text()')
    if not snippets:
        return 'No code snippet found on page :(\n'
    return snippets[0]


# Get the first full answer on the html
def get_full_answer(raw_html):
    tree = html.fromstring(raw_html)
    answers = tree.xpath('//td[@class="answercell"]//div[@class="post-text"]')
    if not answers:
        return 'No answers found on page :(\n'
    return answers[0].text_content()


# Return the question id from a stackoverflow url
def get_question_id(url):
    try:
        question_id = url.split('/')[4]
    except IndexError:
        return 'Error: Could not get question id from url %s\n' % url
    if not question_id.isdigit():
        return 'Error: Invalid question id "%s" from url %s\n' \
            % (question_id, url)
    return question_id


# Convert %3A, %2F, etc... to string and do some fixing on malformed urls
def fix_url(url):
    url = urllib2.unquote(url)
    try:
        # Dirty fix for some duckduckgo responses
        if 'http' not in url[:4]:
            url = url.split('&uddg=')[1]
        # Removes last url part if it is not a question id
        if not url.split('/')[-1].isdigit():
            url = url.rpartition('/')[0]
    except IndexError:
        pass
    return url


# Validate stack overflow question url
def validate_stack_url(url):
    if 'stackoverflow.com' not in url:
        return False
    if '/questions/' not in url and '/q/' not in url:
        return False
    question_id = get_question_id(url)
    if 'Error:' in question_id:
        return False
    return True


# Return the urls found on the search engine
def get_search_urls(keywords, user_agent, timeout, engine):
    if engine == 'fallback':
        urls = search_fallback(keywords, user_agent, timeout)
        if type(urls) is not list:
            print urls
            print '\nCould not found any results.'
            sys.exit(1)
    elif engine == 'google':
        urls = search_google(keywords, user_agent, timeout)
        if type(urls) is not list:
            print urls
            sys.exit(1)
    elif engine == 'bing':
        urls = search_bing(keywords, user_agent, timeout)
        if type(urls) is not list:
            print urls
            sys.exit(1)
    elif engine == 'duckduckgo':
        urls = search_duckduckgo(keywords, user_agent, timeout)
        if type(urls) is not list:
            print urls
            sys.exit(1)
    return urls


# Get and print the answers
def get_and_print_info(urls, user_agent, options):
    print '-' * 79
    for url in urls[:options.answers]:
        url = fix_url(url)
        if options.fulltext:
            page = get_stack_html(url, user_agent, options.timeout)
            # If an error is found, print it and go to the next iteration
            if 'Error:' in page[:len('Error:')]:
                print '\n%s' % page
                print '-' * 79
                continue
            question_title = get_question_title(page)
            answer = get_full_answer(page)
        else:
            page = get_stack_html(url, user_agent, options.timeout)
            if 'Error:' in page[:len('Error:')]:
                print '\n%s' % page
                print '-' * 79
                continue
            question_title = get_question_title(page)
            answer = get_code_snippet(page)

        # Set encoding fix pipe '|' redirects for non ascii text
        print '\nQuestion: %s' % question_title.encode('utf-8')
        print '\n%s' % answer.encode('utf-8')
        print '\nAnswer from: %s\n' % url
        print '-' * 79
        # Sleep between requests
        time.sleep(options.sleep)


# Main cli
def cli():
    (options, args) = get_parsed_args()
    keywords = ''
    for arg in args:
        keywords += arg + ' '
    user_agent = get_random_user_agent()

    urls = get_search_urls(
        keywords, user_agent, options.timeout, options.engine
    )
    get_and_print_info(urls, user_agent, options)


# Run cli function if invoked from shell
if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print 'Aborting.'
        sys.exit(1)
