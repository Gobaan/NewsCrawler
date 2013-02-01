from BeautifulSoup import SoupStrainer
from generalParsers import *
from string import Template
import types, copy, re
import urllib, urlparse
#TODO: Permuate any call with parameters, to see if skipping any parameters are okay
# This will help with future disqus etc.

talkingpointsmemo = JSONParser(
  paths = ["$.data.comments.*.body_plain"],
  starting = "            L",
  site = 'talkingpointsmemo.com',
)

def abcnews_blog_go_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    text = text[:text.find('Posted by')]
    comment.text = text.strip()
  return comment_list

abcnews_blog_go = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'commentlist'}),
  postprocess = abcnews_blog_go_postprocess,
  targets = SoupStrainer('div', {u'id': re.compile(u'div-comment-\d+')}),
)

def abcnews_go_rename(self, url, site):
  Parser.rename(self, url, site)
  parsed_url = urlparse.urlparse(url)
  id = urlparse.parse_qs(parsed_url.query)['id'][0]
  theme = parsed_url.path.split('/')[1]
  args = {}
  title_regex = re.compile('<h1 class="headline">(?P<param2>.+)</h1>')
  args['param0'] = theme
  args['param1'] = id
  args['param2'] = urllib.quote_plus(title_regex.search(site).group('param2'))
  return Template(Template(self.template).safe_substitute(args))

abcnews_go_alternate = EscapedHtmlParser(
  strainer = SoupStrainer('div', {u'class': u'ptcWidgetDiv'}),
  targets = SoupStrainer('div', {u'class': u'ptcMessageText'}),
  starting = '  var',
  rename = abcnews_go_rename,
  template = "http://forums.abcnews.go.com/n/pfx/forum.aspx?args=count%3a25%3bcontentUrl%3a%2f$param0%2f%2fstory%3fstoryId%$param1subject%3a$param2%3bconfig%3atalkback%3bmemberlinkType%3aexternal%3bmaxTsn%3a65%3bTOS%3ay%3bargs%3acontentId%3a$param1%3bmemberlinkUrl%3acomments%3ftype%3duser%26loginCode%3d%7bud%3a%40fromUserId%2cloginCode%7d%3bsubmitButtonImage%3asubmit_comment%3bleaveHTML%3ay%3bwidgetId%3aPTWidget0%3btemplate%3aAWTalkback%3bnav%3ajsscontent%3bcontentId%3a$param1%3baddComment%3an%3bwebtag%3aabccomments%3btemplate%3aAWTalkback%3bpage%3a$iteration&nav=jsscontent&widgetId=PTWidget0&type=talkback&webtag=abccomments",
  max_iterations = 10,
)

# iterative parser again
abcnews_go = IterativeParser(
  site = "abcnews.go.com",
  dispatchers = [ (lambda url: url.startswith('http://abcnews.go.com/blogs/'),
  abcnews_blog_go), (lambda url: True, abcnews_go_alternate), ],
)

def americanthinker_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page'    : '40',
          'identifier'       : self.regex.search(site).group('id')}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)}) + '&p=$iteration')
#http://www.americanthinker.com/2011/11/obamas_canadian_blunder.html

americanthinker = JSONParser(
  regex = re.compile('data-disqus-identifier="(?P<id>\d+)"'),
  paths = ["$.posts.*.message"],
  site = 'www.americanthinker.com',
  rename = americanthinker_rename,
  template = Template('http://americanthinker.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 25,
)

#Disabled because a JS call is required to find ids
#breitbart = HtmlParser()
#breitbart.attrs = {u'id': re.compile(u'IDCommentTop.*'), u'class': u'idc-c-t'}
#breitbart.starting = "l"
#breitbart.strainer = SoupStrainer('div', {u'id': u'idc-cover', u'class': u'idc-comments'})
#breitbart.tags = 'div'

businessinsider = HtmlParser(
  targets = SoupStrainer('div', {u'class': u'comment-content'}),
  strainer = SoupStrainer('div', {u'class': u'comments-content'}),
  site = 'www.businessinsider.com',
)

def cbc_rename(self, url, site):
  docID = self.regex.search(site).group('key')
  self.request['Envelopes'][0]['Payload']['ArticleKey']['Key'] = str(int(docID))
  self.request['Envelopes'][1]['Payload']['CommentedOnKey']['Key'] = str(int(docID))
  args = {'jsonRequest' : self.request}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)}))
# Copied from Trevor

cbc = JSONParser(
  regex = re.compile("articleKey: '(?P<key>\d+)'"),
  paths = ["$.Envelopes.1.Payload.Items.*.Body"],
  request = {"Envelopes":[{"Payload":{"ArticleKey":{"Key":"2000471194","ObjectType":"Models.External.ExternalResourceKey"},"ObjectType":"Requests.External.ArticleRequest"},"PayloadType":"Requests.External.ArticleRequest"},{"Payload":{"CommentedOnKey":{"Key":"2000471194","ObjectType":"Models.External.ExternalResourceKey"},"FilterType":{"ObjectType":"Models.System.Filtering.ThreadFilter","ThreadPath":"/"},"ItemsPerPage":"5","ObjectType":"Requests.Reactions.CommentsPageRequest","OneBasedOnPage":1,"SortType":{"ObjectType":"Models.System.Sorting.TimestampSort","SortOrder":"Descending"}},"PayloadType":"Requests.Reactions.CommentsPageRequest"}],"ObjectType":"Requests.RequestBatch"},
  site = 'www.cbc.ca/news',
  rename = cbc_rename,
  template = Template(r"http://sitelife.cbc.ca/ver1.0/daapi2.api?$query&cb=PluckSDK.jsonpcb(\'request_1\')"),
)

cbsnews = EscapedHtmlParser(
  site = 'www.cbsnews.com',
  strainer = SoupStrainer('div', {u'id': u'commentWrapper'}),
  starting = "	</script> <sp",
  targets = SoupStrainer('dd', {u'id': re.compile(u'body.*')}),
)

def cnn_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '25',
          'url'       : url}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)}) + '&p=$iteration')

cnn = JSONParser(
  rename = cnn_rename,
  paths = ["$.posts.*.message"],
  site = 'www.cnn.com',
  template = Template('http://cnn.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 25,
)

def community_nytimes_rename(self, url, site):
  url = self.regex.search(url).group('url')
  return Template(self.template.substitute({'url' : url}))

community_nytimes = HtmlParser(
  regex = re.compile('http://.*?(?P<url>.*?nytimes.com.*?.html).*'),
  rename = community_nytimes_rename,
  site = 'www.nytimes.com',
  template = Template('http://community.nytimes.com/comments/$url?sort=newest'),
  strainer = SoupStrainer('div', {u'id': u'readerComments'}),
  targets = SoupStrainer('div', {u'class': u'commentText'}),
)

def csmonitor_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '25',
          'url'       : url}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)}) + '&p=$iteration')

csmonitor = JSONParser(
  rename = csmonitor_rename,
  paths = ["$.posts.*.message"],
  site = 'www.csmonitor.com',
  template = Template('http://csmonitor.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 25,
)

def discussions_chicagotribune_rename(self, url, site):
  title = self.regex.search(url).group('title')
  return Template(self.template.substitute({'title':title}))

def discussions_chicagotribune_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    comment.text = text[text.find('\n        \t \n'):]
  return comment_list

discussions_chicagotribune = HtmlParser(
  regex = re.compile('.*?chicagotribune.com/.*/(?P<title>.*?),.*'),
  rename = discussions_chicagotribune_rename,
  postprocess = discussions_chicagotribune_postprocess,
  site = 'www.chicagotribune.com',
  template = Template('http://discussions.chicagotribune.com/20/chinews/$title/10'),
  strainer = SoupStrainer('div', {u'id': u'comment-list'}),
  targets = SoupStrainer('div', {u'class': u'comment'}),
)

def discussions_latimes_rename(self, url, site):
  title = self.regex.search(url).group('title')
  return Template(self.template.substitute({'title':title}))
def discussions_latimes_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    text = text[text.find('at'):]
    comment.text = text[text.find('\n'):]
  return comment_list

discussions_latimes = HtmlParser(
  regex = re.compile( '.*?latimes.com/.*/(?P<title>.*?),.*story'),
  rename = discussions_latimes_rename,
  postprocess = discussions_latimes_postprocess,
  site = 'www.latimes.com',
  template = Template('http://discussions.latimes.com/20/lanews/$title/10'),
  strainer = SoupStrainer('div', {u'id': u'comment-list'}),
  targets = SoupStrainer('div', {u'class': u'comment'}),
)

def economist_rename(self, url, site):
  return Template('%s#comments' % url.split('?')[0])
def economist_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    comment.text = text[text.find('GMT')+3:text.rfind('Recommend')]
  return comment_list

economist = HtmlParser(
  rename = economist_rename,
  site = 'www.economist.com',
  postprocess = economist_postprocess,
  strainer = SoupStrainer('section', {u'id': u'comments-area'}),
  targets = SoupStrainer('article', {u'class':u'single-comment'}),
)

def foxnews_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '40',
          'url'       : url}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)}) + '&p=$iteration')
#foxnews.disqus.com/thread.js?slug=taxmageddon_coming_answer_could_cost_americans_500_billion&sort=hot&p=2&per_page=40&1334762762681

foxnews = JSONParser(
  rename = foxnews_rename,
  paths = ["$.posts.*.message"],
  site = 'www.foxnews.com',
  template = Template('http://foxnews.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 40,
)

def fullcomment_nationalpost_rename(self, url, site):
  args = {'url' : urllib.quote(url, ''),
          'per_page' : 25,
  }
  return Template(self.template.substitute(args) + '&p=$iteration')
#http://npdigital.disqus.com/thread.js?url=http%3A%2F%2Fnews.nationalpost.com%2F2012%2F04%2F17%2Fron-leech-wildrose%2F&title=&sort=&per_page=40&category_id=869867&developer=0&identifier=163137%20http%3A%2F%2Fnews.nationalpost.com%2F%3Fp%3D163137&remote_auth_s3=e30%3D%208e57cfb906064f3856c6912772df8e0f4496782b%201334764414&api_key=4ArDk9sCU7Y27T6Ni9ixYD3n90ZSiXdMtCOI9mcHFCEf6gnVGHpnKgereuyCJ3Rn&disqus_version=1334693674&1334764434219

fullcomment_nationalpost = JSONParser(
  rename = fullcomment_nationalpost_rename,
  paths = ["$.posts.*.message"],
  site = 'fullcomment.nationalpost.com',
  template = Template('http://npdigital.disqus.com/thread.js?url=$url'),
  starting = "    /* */ j",
  max_iterations = 25,
)

guardian = DummyParser(
  site = 'www.guardian.co.uk',
)

def huffingtonpost_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    text = text[text.find('on'):]
    comment.text = text[text.find('\n'):]
  return comment_list

huffingtonpost = HtmlParser(
  site = 'www.huffingtonpost.com',
  postprocess = huffingtonpost_postprocess,
  strainer = SoupStrainer('div', {u'id': re.compile(u'comments_inner_.*')}),
  targets = SoupStrainer('div', {u'class': u'comment_body'}),
)

def news_cnet_rename(self, url, site):
  key = self.regex.search(url).group('key')
  return Template(self.template.substitute({'key':key}))
  #TODO possibly needs community id

news_cnet = HtmlParser(
  regex = re.compile('.*?news.cnet.com/\d+\-(?P<key>\d+_\d+\-\d+)-\d+.*'),
  rename = news_cnet_rename,
  site = 'news.cnet.com',
  template = Template('http://news.cnet.com/8614-$key.html?assetTypeId=12&nomesh&formCommunityId=2070&formTargetCommunityId=2070'),
  strainer = SoupStrainer('section', {u'class': u'commentwrapper'}),
  targets = SoupStrainer('dd', {u'class': u'commentBody'}),
)

news_yahoo = HtmlParser(
  targets = SoupStrainer('blockquote', {u'class': u'ugccmt-commenttext' }),
  strainer = SoupStrainer('ul', {u'id': u'ugccmt-comments', u'class': u'ugccmt-comments'}),
  site = 'news.yahoo.com',
)

newsvine = HtmlParser(
  targets = SoupStrainer('div', {u'class': u'commentSource'}),
  strainer = SoupStrainer('div', {u'id': re.compile(u'commentText_.*'), u'class': u'c_text'}),
  site = 'www.newsvine.com',
)

def npr_rename(self, url, site):
  key = self.regex.search(url).group('key')
  request = {"Requests":[{"ArticleKey":{}},{"CommentPage":{"ArticleKey":{"ArticleKey":{}},"NumberPerPage":10,"OnPage":1,"Sort":"TimeStampDescending"}},{"UserKey":{}}],"UniqueId":6568}
  request['Requests'][0]['ArticleKey']['Key'] = str(int(key))
  request['Requests'][1]['CommentPage']['ArticleKey']['ArticleKey']['Key']=  str(int(key))
  request = urllib.urlencode({'r':request})
  return Template(self.template.substitute({'request':request}))

npr = JSONParser(
  regex = re.compile('.*?npr.org/\d+/\d+/\d+/(?P<key>\d+)/.*'),
  paths = ["$.ResponseBatch.Responses.1.CommentPage.Comments.*.CommentBody"],
  rename = npr_rename,
  site = 'www.npr.org',
  template = Template('http://community.npr.org/ver1.0/Direct/jsonp?$request&cb=RequestBatch.callbacks.daapiCallback6568'),
)

def online_wsj_rename(self, url, site):
  uri = self.regex.search(url).group('uri')
  return Template(self.template.substitute({'uri':uri}))
def online_wsj_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    text = text[:text.rfind('Recommend')]
    comment.text = text[:text.rfind('\n')]
  return comment_list

online_wsj = HtmlParser(
  regex = re.compile('.*?online.wsj.com/article/(?P<uri>.*?).html'),
  rename = online_wsj_rename,
  postprocess = online_wsj_postprocess,
  site = 'online.wsj.com',
  template = Template('http://online.wsj.com/community/mdcrpc/comments/GetArticlecommentsInitialPage.sync?commentEntryId=&locale=&s.href=&s.locale=&s.name=&s.tags=&s.typeName=story&s.uri=$uri'),
  strainer = SoupStrainer('ul', {u'class': u'unitList unitType-thread'}),
  targets = SoupStrainer('div', {u'id': re.compile(u'commentcontent.*'), u'class': u'body'}),
)

# Make iterative parser
politico_blog = HtmlParser(
  targets = SoupStrainer('li', {}),
  strainer = SoupStrainer('ol', {u'id': u'blogComments'}),
)

politico = HtmlParser(
  targets = SoupStrainer('div', {u'class': u'submitted-comment clearfix'}),
  strainer = SoupStrainer('ol', {u'id': u'commentsList'}),
)

politico_iterative = IterativeParser(
  site = 'www.politico.com',
  dispatchers = [ (lambda url: '/blogs/' in url, politico_blog), (lambda url: True, politico), ],
)

def rawstory_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '25',
          'url'       : url}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)})+ '&p=$iteration')

rawstory = JSONParser(
  rename = rawstory_rename,
  paths = ["$.posts.*.message"],
  site = 'rawstory.com',
  template = Template('http://rawstory.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 25,
)

def reuters_rename(self, url, site):
  key = url.split('-')[-1].strip()
  return Template(self.template.substitute({'key':key}))

reuters = HtmlParser(
  rename = reuters_rename,
  site = 'www.reuters.com',
  template = Template('http://reuters.com/article/comments/$key'),
  strainer = SoupStrainer('div', {u'class': u'articleComments', u'id': u'commentsTab'}),
  targets = SoupStrainer('div', {u'class': u'commentsBody'}),
)

def theatlantic_rename(self, url, site):
  article_id = url[url[:-1].rfind('/'):]
  args = {'identifier': 'mt%s' % article_id.replace('/', ''),
          'url'       : url,
          'per_page' : '25'}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)})+ '&p=$iteration')

theatlantic = JSONParser(
  rename = theatlantic_rename,
  paths = ["$.posts.*.message"],
  site = 'www.theatlantic.com',
  template = Template('http://theatlantic.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 25,
)

def thisislondon_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    comment.text = text[text.rfind('\n \n -'):]
  return comment_list

thisislondon_co = HtmlParser(
  site = 'www.thisislondon.co.uk',
  postprocess = thisislondon_postprocess,
  strainer = SoupStrainer('div', {u'id': u'readerComments'}),
  targets = SoupStrainer('p', {u'class': re.compile(u'comment.*')}),
)

def washingtonpost_rename(self, url, site):
  url = urllib.quote(self.regex.search(url).group('url'))
  return Template(self.template.substitute({'url':url}))

washingtonpost = JSONParser(
  regex = re.compile('(?P<url>.*?washingtonpost.com.*?.html).*'),
  paths = ["$.entries.*.object.content"],
  rename = washingtonpost_rename,
  template = Template('http://echoapi.washingtonpost.com/v1/search?callback=jsonp1326063163544&q=((childrenof%3A+$url+source%3Awashpost.com+++))+itemsPerPage%3A+100+sortOrder%3A+reverseChronological+safeHTML%3Aaggressive+children%3A+2+++&appkey=prod.washpost.com'),
)

voices_washingtonpost = HtmlParser(
  targets = SoupStrainer('p', {}),
  strainer = SoupStrainer('div', {u'class': u'commentText'}),
)

# iterative parser again
washingtonpost_iterative = IterativeParser(
  site = 'washingtonpost.com',
  dispatchers = [ (lambda url: url.startswith('http://voices.washingtonpost.com'), voices_washingtonpost), (lambda url: True, washingtonpost), ],
)

def theglobeandmail_rename(self, url, site):
  args = {'id' : self.regex.search(url).group('id'),
          'url': urllib.quote(url, '')}
  return Template(self.template.substitute(args) + '&plckOnPage=$iteration')

theglobeandmail = AsyncHtmlParser(
  regex = re.compile('globeandmail.com.*article(?P<id>\d+)'),
  rename = theglobeandmail_rename,
  site = 'www.theglobeandmail.com',
  template = Template('http://sitelife.theglobeandmail.com/ver1.0/sys/jsonp.app?widget_path=tgam/pluck/comments.app&clientUrl=$url%2F&plckCommentOnKeyType=article&plckArticleTitle=Mourners%20bid%20farewell%20to%20North%20Korea%26rsquo%3Bs%20Kim%20Jong-il&plckCommentOnKey=ArticleID$id&plckArticleUrl=$url%2F&plckDiscoverySection=news&plckDiscoveryCategories=ece_frontpage%2Cworld%2Cnews&cb=plcb0&plckItemsPerPage=25'),
  strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list.*')}),
  targets = SoupStrainer('p', {u'class': u'pluck-comm-body'}),
  max_iterations = 25,
)

def sfgate_rename(self, url, site):
  params = url.split('?')[-1]
  url = 'http://www.sfgate.com/cgi-bin/article/comments/view?%s' % params
  args = {'url' : urllib.quote(url, ''),
          'query': urllib.quote(params.split('=')[-1],'')}
  return Template(self.template.substitute(args) + '&plckOnPage=$iteration')

sfgate = AsyncHtmlParser(
  rename = sfgate_rename,
  site = 'www.sfgate.com',
  template = Template('http://contribute.sfgate.com/ver1.0/sys/jsonp.app?widget_path=pluck/comments.app&plckcommentonkeytype=article&plckcommentonkey=$query&plckshortlist=false&plckrefreshpage=true&plckdiscoverysection=Articles&plcksort=TimeStampDescending&plckitemsperpage=10&plckarticleurl=$url&hdnpluck_refreshbaseurl=$url&hdnpluck_imageserver=http%3A%2F%2Fimgs.sfgate.com&clientUrl=$url&cb=plcb0u0&plckItemsPerPage=25'),
  strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list.*')}),
  targets = SoupStrainer('p', {u'class': u'pluck-comm-body'}),
  max_iterations = 25,
)

# Todo test me on other sites
def usatoday_rename(self, url, site):
  args = {'url' : urllib.quote(url, ''),
          'key' : self.regex.search(site).group('id'),
         }
def pluck_getNextUrls(self, iteration):
  if iteration == 1: return AsyncHtmlParser.getNextUrls(self, iteration)
  next_urls = {}
  for url in self.found:
    count = self.count_regex.search(self.url_site[url])
    if count and int(count.group('count')) / 25 + 1 >= iteration:
      next_urls[url] = self.url.template[url].safe_substitute(iteration=iteration)
      print url, count.group('count')
  return next_urls
#http://content.usatoday.com/communities/onpolitics/post/2012/02/ron-paul-nevada-caucuses-intellectual-revolution-/1
#http://sitelife.usatoday.com/ver1.0/USAT/sys/jsonp.app?widget_path=pluck/comments/list.app&plckItemsPerPage=25&plckSort=TimeStampAscending&plckFilter=&plckFindCommentKey=&contentType=Html&plckCommentOnKeyType=article&plckCommentOnKey=$key&plckLevel=1&plckParentHtmlId=pluck_comments_70020&clientUrl=$url&plckCommentListType=full&cb=plcb0

usatoday = AsyncHtmlParser(
  regex = re.compile('plckCommentOnKey="(?P<id>.*?)"'),
  rename = usatoday_rename,
  getNextUrls = pluck_getNextUrls,
  site = 'content.usatoday.com',
  template = Template('http://sitelife.usatoday.com/ver1.0/USAT/sys/jsonp.app?widget_path=pluck/comments/list.app&plckItemsPerPage=25&plckSort=TimeStampAscending&plckFilter=&plckFindCommentKey=&contentType=Html&plckCommentOnKeyType=article&plckCommentOnKey=$key&plckLevel=1&plckParentHtmlId=pluck_comments_70020&clientUrl=$url%23uslPageReturn&plckCommentListType=full&cb=plcb0'),
  strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list.*')}),
  targets = SoupStrainer('p', {u'class': u'pluck-comm-body'}),
  count_regex = re.compile('totalcount=.?"(?P<count>\d+).?"'),
  max_iterations = 25,
)

def newsobserver_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '25',
          'url'       : url}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)})+ '&p=$iteration')

newsobserver = JSONParser(
  rename = newsobserver_rename,
  paths = ["$.posts.*.message"],
  site = 'www.newsobserver.com',
  template = Template('http://newsobserver.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 25,
)

def thehill_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '25',
          'url'       : url}
  return Template(self.template.substitute({'query' : urllib.urlencode(args)}) + '&p=$iteration')

thehill = JSONParser(
  rename = thehill_rename,
  paths = ["$.posts.*.message"],
  site = 'thehill.com',
  template = Template('http://thehill-v4.disqus.com/thread.js?$query'),
  starting = "    /* */ j",
  max_iterations = 25,
)

def thestar_rename(self, url, site):
  args = {'assetid' : self.regex.search(url).group('id')}
  return Template(self.template.substitute(args))
#http://www.thestar.com/news/article/1127975--special-transit-meeting-karen-stintz-readies-motion-to-put-lrt-on-finch-and-eglinton-and-strike-panel-to-study-options-on-sheppard

thestar = JSONParser(
  regex = re.compile('http://www.thestar.com/.*/(?P<id>\d+)'),
  paths = ["$.data.*.Text"],
  rename = thestar_rename,
  site = 'www.thestar.com',
  template = Template('http://www.thestar.com/toplets/commenting/data/listcomments.aspx?assetid=$assetid&sortby=recent&pagenumber=1&pagesize=10'),
)

def calgaryherald_rename(self, url, site):
  #TODO: Actually calculate the key and url
  key = url[:url.rfind('/')]
  key = key[key.rfind('/') + 1:]
  args = {'url' : urllib.quote(url, ''),
          'key': key}
  return Template(self.template.substitute(args) + '&plckOnPage=$iteration')
#http://www.calgaryherald.com/news/calgary/Family+other+interests+Blackett+leaving+after+term/5988262/story.html

calgaryherald = AsyncHtmlParser(
  rename = calgaryherald_rename,
  site = 'www.calgaryherald.com',
  template = Template('http://pluck.calgaryherald.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0&plckItemsPerPage=25'),
  strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list_.*')}),
  targets = SoupStrainer('p', {u'class': u'pluck-comm-body'}),
  max_iterations = 25,
)

def opinion_financialpost_rename(self, url, site):
  args = {'url' : urllib.quote(url, ''),
          'per_page': '25'
         }
  return Template(self.template.substitute(args) + '&p=$iteration')
#http://opinion.financialpost.com/2012/01/12/william-watson-lets-hear-it-for-the-1/

opinion_financialpost = JSONParser(
  rename = opinion_financialpost_rename,
  paths = ["$.posts.*.message"],
  site = 'opinion.financialpost.com',
  template = Template('http://financialpost.disqus.com/thread.js?url=$url'),
  starting = "    /* */ j",
  max_iterations = 25,
)

def terracestandard_rename(self, url, site):
  netloc = urlparse.urlparse(url).netloc
  default_args = {'origin': netloc,
                  'width': '626',
                  'locale': 'en_US',
                  'numposts': '10',
                  'href': url,
                  'relation': 'parent.parent',
                  'api_key': '242325202492798',  #may need to randomly change me
                  'channel_url': 'https://s-static.ak.fbcdn.net/connect/xd_proxy.php?version=3#cb=f37ac5583fdd422',
                  'transport': 'postmessage',
                  'sdk': 'joey'}
  args = {'args' : urllib.urlencode(default_args)}
  return Template(self.template.substitute(args))
#http://www.terracestandard.com/news/137101033.html

terracestandard = EscapedHtmlParser(
  rename = terracestandard_rename,
  site = 'www.terracestandard.com',
  template = Template('https://www.facebook.com/plugins/comments.php?$args'),
  strainer = SoupStrainer('ul', {u'class': u'uiList fbFeedbackPosts'}),
  starting = "  <",
  targets = SoupStrainer('div', {u'class': u'postText'}),
)

def timescolonist_rename(self, url, site):
  key = url[:url.rfind('/')]
  key = key[key.rfind('/') + 1:]
  args = {'url' : urllib.quote(url, ''),
          'key': key}
  return Template(self.template.substitute(args) + '&p=$iteration')
#http://www.timescolonist.com/news/Thousands+stolen+from+former+UVic+employee+bank+account/5988143/story.html

timescolonist = AsyncHtmlParser(
  rename = timescolonist_rename,
  site = 'www.timescolonist.com',
  template = Template('http://pluck.timescolonist.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plckdiscoverysection=VITC_news&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0&plckItemsPerPage=25'),
  strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list_.*')}),
  targets = SoupStrainer('p', {u'class': u'pluck-comm-body'}),
  max_iterations = 25,
)

aptn = HtmlParser(
  targets = SoupStrainer('div', {u'class': u'dsq-comment-message'}),
  strainer = SoupStrainer('ul', {u'id': u'dsq-comments'}),
  site = 'aptn.ca',
)

def ctv_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text.replace('googleon: index', '')
    text = text.replace('googleoff: index', '')
    comment.text = text[text.find('said') + 4:]
  return comment_list

ctv = HtmlParser(
  site = 'www.ctv.ca',
  postprocess = ctv_postprocess,
  strainer = SoupStrainer('div', {u'class': u'commentDiv'}),
  targets = SoupStrainer('div', {u'class': u'divider'}),
)

thesudburystar = HtmlParser(
  targets = SoupStrainer('div', {u'class': u'commentcontent'}),
  strainer = SoupStrainer('div', {u'class': u'commentcontent'}),
  site = 'www.thesudburystar.com',
)

cnews_canoe = HtmlParser(
  targets = SoupStrainer('div', {u'class': re.compile('comments_row.*')}),
  strainer = SoupStrainer('div', {u'id': u'comments'}),
  site = 'cnews.canoe.ca/CNEWS/Comment',
)

def edmontonjournal_rename(self, url, site):
  #TODO actually fix this
  key = url[:url.rfind('/')]
  key = key[key.rfind('/') + 1:]
  args = {'url' : urllib.quote(url, ''),
          'key': key}
  return Template(self.template.substitute(args) + '&p=$iteration')
#http://www.edmontonjournal.com/news/Staples+bomb+sensors+waste+money/5987764/story.html?cid=dlvr.it-twitter-edmontonjournal

edmontonjournal = AsyncHtmlParser(
  rename = edmontonjournal_rename,
  site = 'www.edmontonjournal.com',
  template = Template('http://pluck.edmontonjournal.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0&plckItemsPerPage=25'),
  strainer = SoupStrainer('div', {u'id': re.compile('pluck_comments_list_.*')}),
  targets = SoupStrainer('p', {u'class': u'pluck-comm-body'}),
  max_iterations = 25,
)

# Html inside json string, so two pass parsing
upi_inner = HtmlParser(
  targets = SoupStrainer('div', {u'class': u'comment'}),
  strainer = SoupStrainer('div', {u'class': u'comments'}),
)

def upi_rename(self, url, site):
  code = self.regex.search(url).groupdict()
  return Template(self.template.substitute(code))
def upi_postprocess(self, comment_list):
  temp_list = []
  for comment in comment_list:
    temp_list += upi_inner.custom_parse(comment.text)
  return temp_list
#http://www.upi.com/Odd_News/2012/01/08/Slavery-math-problems-irk-Ga-parents/UPI-29921326042191/

upi = JSONParser(
  regex = re.compile('/UPI-(?P<code>\d+)'),
  paths = ["$.comments"],
  template = Template('http://www.upi.com/upi_comments/io?uc_list=1&page_id=$code&limit=100&page_type=story&&_=1326593639443'),
  site = 'www.upi.com',
  rename = upi_rename,
  postprocess = upi_postprocess,
)

voices_yahoo = HtmlParser(
  targets = SoupStrainer('p', {u'class': u'content'}),
  strainer = SoupStrainer('div', {u'class': u'comment_list'}),
  site = 'voices.yahoo.com',
)

def seattletimes_rename(self, url, site):
  source_id = self.regex.search(url).groupdict()
  return Template(self.template.substitute(source_id))
#http://seattletimes.nwsource.com/html/nationworld/2017242945_cruiseship15.html

community_seattletimes_nwsource = HtmlParser(
  regex = re.compile('/(?P<source_id>\d+)_'),
  rename = seattletimes_rename,
  site = 'seattletimes.nwsource.com',
  template = Template('http://community.seattletimes.nwsource.com/reader_feedback/public/display.php?source_id=$source_id&source_name=mbase'),
  strainer = SoupStrainer('div', {u'id': u'leftcolumn'}),
  targets = SoupStrainer('div', {u'class': u'gc_comments_comment'}),
)

def vancouversun_rename(self, url, site):
  args = {'url' : urllib.quote(url, '')}
  args['key'] = self.regex.search(url).group('id')
  if not args['key']:
     args['key'] = self.regex.search(url).group('id2')
  return Template(self.template.substitute(args) + '&plckOnPage=$iteration')
#http://www.vancouversun.com/life/Opinion+Restricting+Chinese+language+signs+Canadian/5988028/story.html

vancouversun = AsyncHtmlParser(
  regex = re.compile('id=(?P<id>\d+)|/(?P<id2>\d+)/'),
  rename = vancouversun_rename,
  site = 'www.vancouversun.com',
  template = Template('http://pluck.vancouversun.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0&plckItemsPerPage=25'),
  strainer = SoupStrainer('div', {u'id': re.compile('pluck_comments_list_.*')}),
  targets = SoupStrainer('p', {u'class': u'pluck-comm-body'}),
  max_iterations = 25,
)

straight = HtmlParser(
  targets = SoupStrainer('div', {u'class': u'comment-body'}),
  strainer = SoupStrainer('div', {u'id': u'comments'}),
  site = 'www.straight.com',
)

def winnipegsun_rename(self, url, site):
  args = {'url' : urllib.quote(url, ''),
          'per_page': '25',
  }
  return Template(self.template.substitute(args) + '&p=$iteration')
#http://www.winnipegsun.com/2012/01/13/suspects-caught-after-smoke-run

winnipegsun = JSONParser(
  rename = winnipegsun_rename,
  paths = ["$.posts.*.message"],
  starting = "    /* */ j",
  site = 'www.winnipegsun.com',
  template = Template('http://winnipegsun.disqus.com/thread.js?url=$url'),
)

def canadianbusiness_rename(self, url, site):
  asset_id = self.regex.search(url).groupdict()
  return Template(self.template.substitute(asset_id) + '&pagenumber=$iteration')
#http://www.canadianbusiness.com/blog/business_ethics/65217--is-animal-cruelty-illegal-but-ethical

canadianbusiness = JSONParser(
  regex = re.compile('/(?P<assetid>\d+)--'),
  paths = ["$.data.*.Text"],
  site = 'www.canadianbusiness.com',
  rename = canadianbusiness_rename,
  template = Template('http://www.canadianbusiness.com/toplets/commenting/data/listcomments.aspx?assetid=$assetid&sortby=recent&pagesize=10'),
  max_iterations = 25,
)

def arstechnica_rename(self, url, site):
  path = urlparse.urlparse(url).path
  if path.endswith('.ars'): path = path[:-4]
  args = {'url' : path,
          'encoded_url' : urllib.quote(path, '')}
  return Template(self.template.safe_substitute(args))

def arstechnica_getNextUrls(self, iteration):
  next_urls = {}
  for url in self.found:
    args = {}
    args['iteration'] = iteration * 40 - 39
    next_urls[url] = self.url_template[url].safe_substitute(args)
  return next_urls

arstechnica = HtmlParser (
  strainer = SoupStrainer('ol', {u'data-forum-id': re.compile('\d+'), u'id': u'comments', u'data-topic-id': re.compile('\d+')}),
  targets = SoupStrainer('div', {u'class': u'body'}),
  template = Template("http://arstechnica.com$url?comments=1&start=$iteration#comments-bar"),
  site = "arstechnica.com",
  rename = arstechnica_rename,
  getNextUrls = arstechnica_getNextUrls,
  max_iterations = 10,
)
