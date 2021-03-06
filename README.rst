|Black| |Downloads|

askstack
========

Search answers on Stack Overflow. Can use Google, Bing or DuckDuckGo search
engine.

Just pass some keywords to the script and it will uses a search engine to find
the most relevant pages on Stack Overflow.

Then, it will get the first code snippet from the question page or the full
answer text.

Simple example::

    $ askstack python delete dict key
    ---------------------------------------------------------------------------

    Question: How to remove a key from a python dictionary?

    my_dict.pop('key', None)


    Answer from: https://stackoverflow.com/questions/11277432

    ---------------------------------------------------------------------------

    Question: Delete an item from a dictionary

    del d[key]


    Answer from: https://stackoverflow.com/questions/5844672

    ---------------------------------------------------------------------------


Notes
=====

- Works on Python 2.7 and Python 3.4+


Install
=======

Install using pip::

    pip install askstack


Usage
=====

::

    Usage: askstack keywords... [options]

    search answers on stackoverflow

    Options:
    --version       show program's version number and exit
    -h, --help      show this help message and exit
    -a ANSWERS      number of answers to retrieve (default: 2)
    -e ENGINE       search engine to use: 'google', 'bing', 'duckduckgo' or
                    'fallback' - fallback will try google and fallback to bing
                    and duckduckgo if a search fails (default: fallback)
    -f, --fulltext  get the full answer text (default: disabled)
    -s SLEEP        sleep time between requests (default: 0.5)
    -t TIMEOUT      timeout in seconds to wait for reply (default: 5)


Examples
========

If you are feeling lucky, get only the first code snippet::

    $ askstack linux gzip directory -a 1

Get full first answer::

    $ askstack linux gzip directory -a 1 -f

Try to get three answers using only DuckDuckGo as the search engine::

    $ askstack linux gzip directory -a 3 -e duckduckgo


.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. |Downloads| image:: https://pepy.tech/badge/askstack
    :target: https://pepy.tech/project/askstack
