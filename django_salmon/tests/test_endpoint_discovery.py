import django_salmon

atom_feed_string = """<?xml version='1.0' encoding='utf-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'>
    <link rel='salmon' href='http://testserver/salmon/endpoint' />
    <link rel='alternate' href='http://foo/stuff' />

    <entry>

    </entry>
    <entry>

    </entry>
</feed>"""

atom_feed_string_single_entry = """<?xml version='1.0' encoding='utf-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'>
    <link rel='salmon' href='http://testserver/salmon/not/this/one' />
    <link rel='alternate' href='http://foo/stuff' />
    <entry>
        <link rel='salmon' href='http://testserver/salmon/endpoint' />
        <link rel='alternate' href='http://foo/stuff/entry' />
    </entry>
</feed>"""


atom_entry_string = """<?xml version='1.0' encoding='utf-8'?>
<entry xmlns='http://www.w3.org/2005/Atom'>
    <link rel='salmon' href='http://testserver/salmon/endpoint' />
    <link rel='alternate' href='http://foo/stuff/entry' />
</entry>"""

html_no_atom = """<html><head>
<link rel='alternate' href='http://link/to/atom' />
<link rel='salmon' href='http://testserver/salmon/endpoint' />
<title>My HTML Page</title>
</head>
<body><p>Hello, World!</p></body>
</html>"""

fixtures = (
    atom_feed_string, atom_feed_string_single_entry, atom_entry_string,
    html_no_atom,
)


def test_endpoint_discovery():
    for fixture in fixtures:
        endpoint = django_salmon.discover_salmon_endpoint(fixture)
        assert endpoint == 'http://testserver/salmon/endpoint'
