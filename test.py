import urllib
import urllib2
import urlparse
import sys
import uuid
import logging
import re
logging.root.setLevel(logging.INFO)

class NoRedirects(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response

# Override the urllib2 openener so that it does not
# follow redirects by default.
url_opener = urllib2.build_opener(NoRedirects)

def false_if_exception(f):
    """ Used as a decorator on functions. If the call to
        `urlopen` raises an exception, False is returned
        instead of the exception being raised.
    """
    def wrapped_f(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except urllib2.HTTPError as e:
            return False
        except urllib2.URLError as e:
            return False
    return wrapped_f


def fetch(base_url, path, data=None, method=None):
    """ Fetches a URL and returns a response object
    """
    url = urlparse.urljoin(base_url, path)
    if data:
        data = urllib.urlencode(data)
    request = urllib2.Request(url, data=data)
    if method is not None:
        request.get_method = lambda: method
    response = url_opener.open(request)
    return response

test_count = 0
def log_comment(f):
    def wrapped_f(*args, **kwargs):
        result = f(*args, **kwargs)
        global test_count
        if test_count == 0:
            print '--------------------'
        print 'Test number: {0}'.format(test_count)
        print 'Test text: {0}'.format(args[0])
        print 'Test result: {0}'.format('PASS' if result else 'FAIL')
        print '--------------------'
        test_count += 1
        return result

    return wrapped_f

@log_comment
@false_if_exception
def test_response(comment, base_url, path, data=None, expected_code=None, expected_headers=None, expected_content=None, method=None):
    """ Place a get request. Optionally, test the response for
        certain response codes, headers, and content. The
        expected_content parameter can be either a string
        or a function.
    """
    response = fetch(base_url, path, data=data, method=method)
    if expected_code:
        if isinstance(expected_code, int):
            if response.code != expected_code:
                return False
        elif response.code not in expected_code:
            return False
    if expected_headers:
        for header_key, header_value in expected_headers.iteritems():
            if response.info().getheader(header_key).lower() != header_value.lower():
                return False
    if expected_content:
        content = response.read()
        if callable(expected_content):
            if not expected_content(content):
                return False
        else:
            if isinstance(expected_content, (str, unicode)):
                if expected_content not in content:
                    return False
    return True

def random_content(length=1):
    return ' '.join(str(uuid.uuid4()) for i in range(length))

def main(base_url):
    posts = [random_content() for i in range(5)]
    results = [
        test_response(
            "A GET request to '/' produces an HTTP 200 response with content 'Hello World!' somewhere",
            base_url, '', expected_code=200, expected_content="Hello World!"
        ),
        test_response(
            "A GET request to ''/robots.txt' produces a HTTP 200 response with Content-Type 'text/plain; charset=utf-8'",
            base_url,
            '/robots.txt',
            expected_code=200,
            expected_headers={'Content-Type': 'text/plain; charset=utf-8'}
        ),
        test_response(
            "A GET request to '/mrw/class-is-done.gif' 301 or 302 redirects to the reaction gif of your choice",
            base_url,
            '/mrw/class-is-done.gif',
            expected_code=[301, 302]
        ),
        test_response(
            "A DELETE request to '/posts/delete' deletes all existing posts and responses w/ 200 status code",
            base_url,
            '/posts/delete',
            expected_code=200,
            method='DELETE'
        ),
        test_response(
            "There should be no posts at first (checking '/posts/0' returns 404 status)",
            base_url,
            '/posts/0',
            expected_code=404
        ),
        test_response(
            "There should be no posts at first (checking '/posts/1' returns 404 status)",
            base_url,
            '/posts/1',
            expected_code=404
        ),
        test_response(
            "A POST request to '/posts/new' with form data containing a 'text' field creates a new post w/ id 0 and redirects to '/posts/0'",
            base_url,
            '/posts/new',
            data={'text': posts[0]},
            expected_code=[301,302]
        ),
        test_response(
            "A GET request to /posts/0 contains the post content that was submitted and status code 200",
            base_url,
            '/posts/0',
            expected_code=200,
            expected_content=posts[0]
        ),
        test_response(
            "A POST request to '/posts/new' with form data containing a 'text' field creates a new post w/ id 1 and redirects to '/posts/1'",
            base_url,
            '/posts/new',
            data={'text': posts[1]},
            expected_code=[301,302]
        ),
        test_response(
            "A GET request to /posts/1 contains the post content that was submitted and status code 200",
            base_url,
            '/posts/1',
            expected_code=200,
            expected_content=posts[1]
        ),
        test_response(
            "A DELETE request to '/posts/delete' deletes all existing posts and responses w/ 200 status code",
            base_url,
            '/posts/delete',
            expected_code=200,
            method='DELETE'
        ),
        test_response(
            "There should be no more posts (checking '/posts/0' returns 404 status)",
            base_url,
            '/posts/0',
            expected_code=404
        ),

    ]
    print '{0}/{1}'.format(sum(1 for result in results if result), len(results))


if __name__ == '__main__':
    main(sys.argv[1])