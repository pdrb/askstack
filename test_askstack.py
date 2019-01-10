#!/usr/bin/env python

from askstack import askstack
import responses


@responses.activate
def test_get_http_response():
    responses.add(responses.GET, 'http://testing.testing', status=503)
    responses.add(
        responses.GET, 'http://testing.testing',
        body='<html><h1>OK</h1></html>', status=200
    )
    assert 'Error: Could not connect' in \
        askstack.get_http_response('http://invalidurl', 'testing', 5, 'Test')
    assert 'Error: Failed request' in \
        askstack.get_http_response(
            'http://testing.testing', 'testing', 5, 'Test'
        )
    resp = askstack.get_http_response(
        'http://testing.testing', 'testing', 5, 'Test'
    )
    assert resp.content.decode() == '<html><h1>OK</h1></html>'


@responses.activate
def test_search_google():
    responses.add(
        responses.GET, 'https://www.google.com/search?q=site:stackoverflow.com'
        '+whatever', body='<html></html>', status=200
    )
    body = '<h3 class="r"><a href="https://stackoverflow.com/testing"></h3>'
    responses.add(
        responses.GET, 'https://www.google.com/search?q=site:stackoverflow.com'
        '+whatever', body=body, status=200
    )
    urls = askstack.search_google('whatever', 'testing', 5)
    assert type(urls) is str and 'Error: No urls found'
    urls = askstack.search_google('whatever', 'testing', 5)
    assert urls[0] == 'https://stackoverflow.com/testing'


@responses.activate
def test_search_bing():
    responses.add(
        responses.GET, 'https://www.bing.com/search?q=site:stackoverflow.com'
        '+whatever', body='<html></html>', status=200
    )
    body = '<li class="b_algo"><div class="b_title"><h2>' \
           '<a href="https://stackoverflow.com/testing"></h2></div></li>'
    responses.add(
        responses.GET, 'https://www.bing.com/search?q=site:stackoverflow.com'
        '+whatever', body=body, status=200
    )
    urls = askstack.search_bing('whatever', 'testing', 5)
    assert type(urls) is str and 'Error: No urls found'
    urls = askstack.search_bing('whatever', 'testing', 5)
    assert urls[0] == 'https://stackoverflow.com/testing'


@responses.activate
def test_search_duckduckgo():
    responses.add(
        responses.GET, 'https://duckduckgo.com/html/?q=site:stackoverflow.com'
        '+whatever', body='<html></html>', status=200
    )
    body = '<a rel="nofollow" class="result__a" ' \
           'href="https://stackoverflow.com/testing">'
    responses.add(
        responses.GET, 'https://duckduckgo.com/html/?q=site:stackoverflow.com'
        '+whatever', body=body, status=200
    )
    urls = askstack.search_duckduckgo('whatever', 'testing', 5)
    assert type(urls) is str and 'Error: No urls found'
    urls = askstack.search_duckduckgo('whatever', 'testing', 5)
    assert urls[0] == 'https://stackoverflow.com/testing'


@responses.activate
def test_get_stack_html():
    responses.add(
        responses.GET, 'https://stackoverflow.com/questions/11277432',
        body='<html><h1>OK</h1></html>', status=200
    )
    responses.add(
        responses.GET, 'https://stackoverflow.com/questions/11277432',
        body='<html><h1>Not Found</h1></html>', status=404
    )
    assert '<html><h1>OK</h1></html>' in askstack.get_stack_html(
        'https://stackoverflow.com/questions/11277432', 'testing', 5
    )
    assert 'Error: "http://testing.invalidurl" is not a valid' in \
        askstack.get_stack_html('http://testing.invalidurl', 'testing', 5)
    assert 'status code: 404' in \
        askstack.get_stack_html(
            'https://stackoverflow.com/questions/11277432', 'testing', 5
        )


def test_get_question_title():
    raw_html = '<h1 itemprop="name"><a href="/testing" ' \
               'class="question-hyperlink">Testing Question</a></h1>'
    assert askstack.get_question_title(raw_html) == 'Testing Question'
    assert askstack.get_question_title('<html></html>') \
        == 'No question title found on page'


def test_get_code_snippet():
    raw_html = '''<div class="answercell post-layout--right">
    <div class="post-text" itemprop="text">
<p>Testing</p>

<pre><code>testing code
</code></pre>'''
    assert askstack.get_code_snippet(raw_html) == 'testing code\n'
    assert askstack.get_code_snippet('<html></html>') \
        == 'No code snippet found on page :(\n'


def test_get_full_answer():
    raw_html = '''<div class="answercell post-layout--right">
    <div class="post-text" itemprop="text">
<p>Testing</p>

<pre><code>testing code
</code></pre>

<p>Testing answer</p>
    </div>'''
    assert askstack.get_full_answer(raw_html) == '\nTesting\n\n' \
        'testing code\n\n\nTesting answer\n    '
    assert askstack.get_full_answer('<html></html>') \
        == 'No answers found on page :(\n'


def test_get_question_id():
    urls = ['https://stackoverflow.com/questions/11277432',
            'https://stackoverflow.com/questions/11277432/'
            'how-to-remove-a-key-from-a-python-dictionary',
            'https://stackoverflow.com/questions',
            'https://stackoverflow.com/questions/testing']
    assert askstack.get_question_id(urls[0]) == '11277432'
    assert askstack.get_question_id(urls[1]) == '11277432'
    assert 'Error: Could not get' in askstack.get_question_id(urls[2])
    assert 'Error: Invalid question id' in askstack.get_question_id(urls[3])


def test_fix_url():
    urls = ['https://stackoverflow.com/questions/11277432',
            'https://stackoverflow.com/questions/11277432/'
            'how-to-remove-a-key-from-a-python-dictionary',
            'https%3A%2F%2Fstackoverflow.com%2Fquestions%2F11277432%2F',
            '/l/?kh=-1&uddg=https%3A%2F%2Fstackoverflow.com'
            '%2Fquestions%2F11277432%2F']
    assert askstack.fix_url(urls[0]) == urls[0]
    assert askstack.fix_url(urls[1]) == urls[0]
    assert askstack.fix_url(urls[2]) == urls[0]
    assert askstack.fix_url(urls[3]) == urls[0]


def test_validate_stack_url():
    urls = ['https://stackoverflow/',
            'https://stackoverflow.com/',
            'https://stackoverflow.com/questions/',
            'https://stackoverflow.com/questions/test',
            'https://stackoverflow.com/questions/11277432',
            'https://stackoverflow.com/q/11277432']
    assert not askstack.validate_stack_url(urls[0])
    assert not askstack.validate_stack_url(urls[1])
    assert not askstack.validate_stack_url(urls[2])
    assert not askstack.validate_stack_url(urls[3])
    assert askstack.validate_stack_url(urls[4])
    assert askstack.validate_stack_url(urls[5])
