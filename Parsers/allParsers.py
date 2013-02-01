import functools, collections
import generalParsers
import helper
import allCommentExtractors
import allArticleExtractors

Result = collections.namedtuple('Result', ['content', 'comment_url', 'comments'])

error_comment = generalParsers.Comment("", "", "Comment Missing")
class CompleteParser(object):
  def __init__(self, contentExtractor, commentExtractor):
    self.contentExtractor = contentExtractor
    self.commentExtractor = commentExtractor

  def parse_all(self, articles):
    data = helper.parallel_fetch(articles, replace_redirects=True)
    content = self.contentExtractor.parse_all(data)
    comments = self.commentExtractor.parse_all(data)
    results = {}
    for url in content:
      result_content = content[url]
      comment_url = "Error Url Not Found"
      result_comments = [error_comment]
      try:
        comment_url = self.commentExtractor.url_next[url] 
        result_comments = comments[url] 
      except KeyError:
        pass

      results[url] = Result(result_content, comment_url, result_comments) 

    return results

mapper = {}
# merges content and comment parsers
for name in dir(allCommentExtractors):
  cls = getattr(allCommentExtractors, name)

  if isinstance(cls, generalParsers.Parser) and cls.site:
    articleParser = getattr(allArticleExtractors, name)
    mapper[cls.site] = CompleteParser(articleParser, cls)

if __name__ == '__main__':
  #debug
  s = []
  #s = ['http://arstechnica.com/apple/news/2012/01/apple-to-announce-tools-platform-to-digitally-destroy-textbook-publishing.ars']
  #site = 'arstechnica.com'
  parser = mapper[site]
  for url, result in parser.parse_all(s).iteritems():
    print url
    print result.comment_url
    for comment in result.comments:
      print comment.text
