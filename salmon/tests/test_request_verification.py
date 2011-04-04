import datetime

from salmon import utils

now = datetime.datetime.now()
one_hour_ago = now - datetime.timedelta(hours=1)
ten_minutes_ago = now - datetime.timedelta(minutes=10)
fifty_nine_minutes_ago = now - datetime.timedelta(minutes=59)

old_atom_entry = """<?xml version='1.0' encoding='utf-8'?>
<entry xmlns='http://www.w3.org/2005/Atom'>
    <updated>%s</updated>
</entry>""" % (one_hour_ago.strftime("%Y-%m-%dT%H:%M:%S-4:00"))

newer_atom_entry = """<?xml version='1.0' encoding='utf-8'?>
<entry xmlns='http://www.w3.org/2005/Atom'>
    <updated>%s</updated>
</entry>""" % (ten_minutes_ago.strftime("%Y-%m-%dT%H:%M:%S-4:00"))

almost_old_entry = """<?xml version='1.0' encoding='utf-8'?>
<entry xmlns='http://www.w3.org/2005/Atom'>
    <updated>%s</updated>
</entry>""" % (fifty_nine_minutes_ago.strftime("%Y-%m-%dT%H:%M:%S-4:00"))


def test_old_timestamp():
    updated = utils.parse_updated_from_atom(old_atom_entry)
    assert not utils.verify_timestamp(updated)


def test_new_timestamp():
    updated = utils.parse_updated_from_atom(newer_atom_entry)
    assert utils.verify_timestamp(updated)


def test_almost_old_timestamp():
    updated = utils.parse_updated_from_atom(almost_old_entry)
    assert utils.verify_timestamp(updated)
