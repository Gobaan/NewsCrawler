import functools, collections
import generalParsers
import helper
import allCommentExtractors
import allArticleExtractors

Result = collections.namedtuple('Result', ['content', 'comments'])
def parse(articles, extractContentFunction, extractCommentFunction):
  data = helper.parallel_fetch(articles)
  content = extractContentFunction(data)
  comments = extractCommentFunction(data)
  return Result(content, comments)

mapper = {}
# Takes all the extract content functions and creates parsers from them
# Simple rename function for now
for name in dir(allCommentExtractors):
  cls = getattr(allCommentExtractors, name)

  if isinstance(cls, generalParsers.Parser) and cls.site:
    articleParser = getattr(allArticleExtractors, name).parse_all
    mapper[cls.site] = \
      functools.partial(parse, 
          extractContentFunction = articleParser,
          extractCommentFunction = cls.parse_all)
