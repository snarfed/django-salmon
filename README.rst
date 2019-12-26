=============
django-salmon
=============

This is a fork of ``django-salmon``, a drop-in `Django`_ application that adds support for the `Salmon Protocol`_. It's maintained by @snarfed solely for use in `Bridgy Fed <https://fed.brid.gy/>`__. It requires Python 3.

.. _Django: http://www.djangoproject.com/
.. _Salmon Protocol: http://www.salmon-protocol.org/salmon-protocol-summary


Instructions
------------

To use ``django-salmon``, add it to your ``INSTALLED_APPS`` in ``settings.py``: ::

   INSTALLED_APPS = (
       ...
       'django_salmon',
       ...
   )

You will need models to represent feeds and comments. Set up signals for your feed model: ::

   import django_salmon
   ...
   def salmon_subscriber(sender, **kwargs):
       feed = kwargs.get('instance', None)
       if not feed:
           return
       django_salmon.subscribe(feed, feed.url)
   post_save.connect(salmon_subscriber, sender=Feed) 

   def salmon_unsubscriber(sender, **kwargs):
       feed = kwargs.get('instance', None)
       if not feed:
           return
       django_salmon.unsubscribe(feed)
   post_delete.connect(salmon_unsubscriber, sender=Feed)

Set up the following signal for your comment model: ::

   import django_salmon
   from django_salmon.feeds import create_entry_feed

   def comment_handler(sender, **kwargs):
       comment = kwargs.get('instance', None)
       if not comment:
           return
       try:
           user = User.objects.get(username=comment.user_name)
       except User.DoesNotExist:
           return
       url = 'https://%s%s' % (
           Site.objects.get_current(),
           comment.get_absolute_url())
       parent = comment.content_object
       feed = create_entry_feed(comment.comment, url, comment.comment,
                                author_name=comment.user_name,
                                author_link='acct:' + comment.user_email,
                                pubdate=comment.submit_date,
                                parent_id=parent.entry_id)
       django_salmon.slap(feed, parent.feed, user)
   post_save.connect(comment_handler, sender=Comment)

Finally, in order to process salmon slaps, you must add a handler function to ``settings.py``: ::

   SALMON_SLAP_HANDLER = 'comments.salmon_handler'

This function will receive two parameters: the actual salmon and the mime_type (currently always ``application/atom+xml`` until support for other formats is added). It is the responsibility of this handler function to discover what content the salmon is associated with (in the case of mentions or replies) and handle accordingly.

** NOTE: ** This is a work in progress and at the moment only supports a very specific protocol flow with limited kinds of data.
