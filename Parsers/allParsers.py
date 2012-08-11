import functools, collections
import generalParsers
import helper
import allCommentExtractors
import allArticleExtractors

Result = collections.namedtuple('Result', ['content', 'comments'])
class CompleteParser(object):
  def __init__(self, contentExtractor, commentExtractor):
    self.contentExtractor = contentExtractor
    self.commentExtractor = commentExtractor

  def parse_all(self, articles):
    data = helper.parallel_fetch(articles)
    content = self.contentExtractor.parse_all(data)
    comments = self.commentExtractor.parse_all(data)
    results = {}
    for url in content:
      results[url] = Result(content[url], comments[url])
    return results

mapper = {}
# merges content and comment parsers
for name in dir(allCommentExtractors):
  cls = getattr(allCommentExtractors, name)

  if isinstance(cls, generalParsers.Parser) and cls.site:
    articleParser = getattr(allArticleExtractors, name)
    mapper[cls.site] = CompleteParser(articleParser, cls)
