import json
import allParsers
import helper
logger = helper.get_logger()

def parseBlogs(domain, lock, search_results, filename, search_url):
  logger.info('%s %s', search_results[0].link, filename)
  sr_mapping = {result.link: result for result in search_results}
  results = allParsers.mapper[domain].parse_all(sr_mapping.keys())
  docs = {'docs':[]}
  docs['search'] = search_url

  for url in results:
    search_result = sr_mapping[url]
    try:
      text = [content.text for content in results[url].content]
    except Exception, e:
      logger.error("Article Parsing Failed URL: %s %s", url, e)
      text =  ['Failure to Parse']
    
    article = '\n'.join(text)

    doc = {}
    doc['id'] = hash(url)
    doc['url'] = url
    doc['title'] = search_result.title
    doc['date'] = search_result.date
    doc['article'] = article
    doc['comment_url'] = results[url].comment_url
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
