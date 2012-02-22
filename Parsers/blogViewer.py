import re, os, json, itertools
import helper
import allParsers
import logging
logger = helper.get_logger()

def blogViewer(domain, lock, urls, filename):
    #helper.set_lock(lock)
    url = urls[0]
    logger.info('%s %s', url, filename)
    # TODO: lot of shitty special case code, lets ignore it for now, 
    #if that fails think of better response, filter or smth
    #if '/video/' in url.lower() or '/video?' in url.lower(): 
    #  return
    x = allParsers.mapper[domain](urls)
    failure_count = 0
    docs = {'docs':[]}
    for url in x.content:
      try:
        text = [comment.text for comment in x.content[url]]
      except Exception, e:
        logger.error("Article Parsing Failed URL: %s %s", url, e)
        text =  ['Failure to Parse']
        failure_count += 1
      
      article = '\n'.join(text)

      doc = {}
      doc['id'] = hash(url)
      doc['url'] = url
      doc['title'] = 'Placeholder Title'
      doc['date'] = 'Wed, 22 Dec 2010 18:12:32 EST'
      doc['article'] = article
      comments = []
      for comment in x.comments[url]:
        comm = {}
        #comment['user'] = comment.author
        comm['user'] = 'PlaceholderUser'
        comm['time'] = '23/12/2010 01:29 PM'
        comm['text'] = comment.text
        comm['id'] = hash(comment.text)
        comments += [comm]

      doc['comments'] = comments
      doc['num_comments'] = len(comments)
      docs['docs'] += [doc]

    docs['num_docs'] = len(docs['docs'])

    with open('%s.txt' % filename, 'w') as output:
      json.dump(docs, output, indent=4)
