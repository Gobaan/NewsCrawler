import json
import allParsers
import helper
logger = helper.get_logger()

def parseBlogs(domain, lock, urls, filename, searchurl):
  logger.info('%s %s', urls[0], filename)
  results = allParsers.mapper[domain].parse_all(urls)
  docs = {'docs':[]}
  docs['search'] = searchurl

  for url in results:
    try:
      text = [content.text for content in results[url].content]
    except Exception, e:
      logger.error("Article Parsing Failed URL: %s %s", url, e)
      text =  ['Failure to Parse']
    
    article = '\n'.join(text)

    doc = {}
    doc['id'] = hash(url)
    doc['url'] = url
    doc['title'] = 'Placeholder Title'
    doc['date'] = 'Wed, 22 Dec 2010 18:12:32 EST'
    doc['article'] = article
    comments = []
    for comment in results[url].comments:
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

  docs['num_articles'] = len(docs['docs'])
  docs['total_comments'] = sum([doc['num_comments'] for doc in docs['docs']])
  with open('%s.txt' % filename, 'w') as output:
    json.dump(docs, output, indent=4)
