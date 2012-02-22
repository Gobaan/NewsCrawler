from BeautifulSoup import SoupStrainer
from generalParsers import *
from string import Template
import types, copy, re
import urllib, urlparse
#TODO: Permuate any call with parameters, to see if skipping any parameters are okay 
# This will help with future disqus etc.

talkingpointsmemo = JsonParser()
talkingpointsmemo.site = 'talkingpointsmemo.com'
talkingpointsmemo.paths = ["$.data.comments.*.body_plain"]
talkingpointsmemo.preprocess = pipe(make_startswith("            L"), talkingpointsmemo.preprocess)

abcnews_go = HtmlParser()
abcnews_go.site = 'abcnews.go.com'
abcnews_go.attrs = {u'id': re.compile(u'div-comment-\d+')}
abcnews_go.strainer = SoupStrainer('div', {u'class': u'commentlist'})
abcnews_go.tags = 'div'

americanthinker = JsonParser()
americanthinker.site = 'www.americanthinker.com'
americanthinker.paths = ["$.posts.*.message"]
americanthinker.preprocess = pipe(make_startswith("    /* */ j"), americanthinker.preprocess)
americanthinker_regex = re.compile('data-disqus-identifier="(?P<id>\d+)"')
#http://www.americanthinker.com/2011/11/obamas_canadian_blunder.html
americanthinker_template = Template('http://americanthinker.disqus.com/thread.js?$query')
def americanthinker_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '100',
          'identifier'       : americanthinker_regex.search(site).group('id')}
  return americanthinker_template.substitute({'query' : urllib.urlencode(args)})
americanthinker.rename = \
  types.MethodType (americanthinker_rename, americanthinker)


#Disabled because a JS call is required to find ids
#breitbart = HtmlParser()
#breitbart.attrs = {u'id': re.compile(u'IDCommentTop.*'), u'class': u'idc-c-t'}
#breitbart.preprocess = pipe(make_startswith("l"), breitbart.preprocess)
#breitbart.strainer = SoupStrainer('div', {u'id': u'idc-cover', u'class': u'idc-comments'})
#breitbart.tags = 'div'

businessinsider = HtmlParser()
businessinsider.site = 'www.businessinsider.com'
businessinsider.attrs = {u'class': u'comment-content'}
businessinsider.strainer = SoupStrainer('div', {u'class': u'comments-content'})
businessinsider.tags = 'div'

cbc = JsonParser()
cbc.site = 'www.cbc.ca/news'
cbc.paths = ["$.Envelopes.1.Payload.Items.*.Body"]
# Copied from Trevor
cbc_regex = re.compile("articleKey: '(?P<key>\d+)'")
cbc_template = Template(r"http://sitelife.cbc.ca/ver1.0/daapi2.api?$query&cb=PluckSDK.jsonpcb(\'request_1\')")
cbc_request = {"Envelopes":[{"Payload":{"ArticleKey":{"Key":"2000471194","ObjectType":"Models.External.ExternalResourceKey"},"ObjectType":"Requests.External.ArticleRequest"},"PayloadType":"Requests.External.ArticleRequest"},{"Payload":{"CommentedOnKey":{"Key":"2000471194","ObjectType":"Models.External.ExternalResourceKey"},"FilterType":{"ObjectType":"Models.System.Filtering.ThreadFilter","ThreadPath":"/"},"ItemsPerPage":"5","ObjectType":"Requests.Reactions.CommentsPageRequest","OneBasedOnPage":1,"SortType":{"ObjectType":"Models.System.Sorting.TimestampSort","SortOrder":"Descending"}},"PayloadType":"Requests.Reactions.CommentsPageRequest"}],"ObjectType":"Requests.RequestBatch"}
def cbc_rename(self, url, site):
  docID = cbc_regex.search(site).group('key')
  cbc_request['Envelopes'][0]['Payload']['ArticleKey']['Key'] = str(int(docID))
  cbc_request['Envelopes'][1]['Payload']['CommentedOnKey']['Key'] = str(int(docID))
  args = {'jsonRequest' : cbc_request}
  return cbc_template.substitute({'query' : urllib.urlencode(args)})
cbc.rename = types.MethodType (cbc_rename, cbc)


cbsnews = EscapedHtmlParser()
cbsnews.site = 'www.cbsnews.com'
cbsnews.attrs = {u'id': re.compile(u'body.*')}
cbsnews.preprocess = pipe( make_startswith("	</script> <sp"), cbsnews.preprocess)
cbsnews.strainer = SoupStrainer('div', {u'id': u'commentWrapper'})
cbsnews.tags = 'dd'

cnn = JsonParser()
cnn.site = 'www.cnn.com'
cnn.paths = ["$.posts.*.message"]
cnn.preprocess = pipe(make_startswith("    /* */ j"), cnn.preprocess)
cnn_template = Template('http://cnn.disqus.com/thread.js?$query')
def cnn_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '100',
          'url'       : url}
  return cnn_template.substitute({'query' : urllib.urlencode(args)})
cnn.rename = types.MethodType (cnn_rename, cnn)

community_nytimes = HtmlParser()
community_nytimes.site = 'www.nytimes.com'
community_nytimes.attrs = {u'class': u'commentText'}
community_nytimes.strainer = SoupStrainer('div', {u'id': u'readerComments'})
community_nytimes.tags = 'div'
community_nytimes_regex = re.compile('http://.*?(?P<url>.*?nytimes.com.*?.html).*')
community_nytimes_template = Template('http://community.nytimes.com/comments/$url?sort=newest')
def nytimes_rename(self, url, site):
  url = community_nytimes_regex.search(url).group('url')
  return community_nytimes_template.substitute({'url' : url})
community_nytimes.rename = \
  types.MethodType (nytimes_rename, community_nytimes)

csmonitor = JsonParser()
csmonitor.site = 'www.csmonitor.com'
csmonitor.paths = ["$.posts.*.message"]
csmonitor.preprocess = pipe(make_startswith("    /* */ j"), csmonitor.preprocess)
csmonitor_template = Template('http://csmonitor.disqus.com/thread.js?$query')
def csmonitor_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '100',
          'url'       : url}
  return csmonitor_template.substitute({'query' : urllib.urlencode(args)})
csmonitor.rename = types.MethodType (csmonitor_rename, csmonitor)

discussions_chicagotribune = HtmlParser()
discussions_chicagotribune.site = 'www.chicagotribune.com'
discussions_chicagotribune.attrs = {u'class': u'comment'}
discussions_chicagotribune.strainer = SoupStrainer('div', {u'id': u'comment-list'})
discussions_chicagotribune.tags = 'div'
discussions_chicagotribune_regex = re.compile(
 '.*?chicagotribune.com/.*/(?P<title>.*?),.*')
discussions_chicagotribune_template = Template('http://discussions.chicagotribune.com/20/chinews/$title/10')
def chicago_rename(self, url, site):
  title = discussions_chicagotribune_regex.search(url).group('title')
  return discussions_chicagotribune_template.substitute({'title':title})
discussions_chicagotribune.rename = \
  types.MethodType (chicago_rename, discussions_chicagotribune)

discussions_latimes = HtmlParser()
discussions_latimes.site = 'www.latimes.com'
discussions_latimes.attrs = {u'class': u'comment'}
discussions_latimes.strainer = SoupStrainer('div', {u'id': u'comment-list'})
discussions_latimes.tags = 'div'
discussions_latimes_regex = re.compile(
 '.*?latimes.com/.*/(?P<title>.*?),.*story')
discussions_latimes_template = Template('http://discussions.latimes.com/20/lanews/$title/10')
def latimes_rename(self, url, site):
  title = discussions_latimes_regex.search(url).group('title')
  return discussions_latimes_template.substitute({'title':title})
discussions_latimes.rename = \
  types.MethodType (latimes_rename, discussions_latimes)
def latimes_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    text = text[text.find('at'):]
    comment.text = text[text.find('\n'):]
  return comment_list
discussions_latimes.postprocess = \
  types.MethodType(latimes_postprocess, discussions_latimes)

economist = HtmlParser()
economist.site = 'www.economist.com'
economist.attrs = {u'class':u'single-comment'}
economist.strainer = SoupStrainer('section', {u'id': u'comments-area'})
economist.tags = 'article'
def economist_rename(self, url, site):
  return '%s#comments' % url.split('?')[0]
economist.rename = types.MethodType (economist_rename, economist)
def economist_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    comment.text = text[text.find('GMT')+3:text.rfind('Recommend')]
  return comment_list
economist.postprocess = \
  types.MethodType(economist_postprocess, economist)


foxnews = JsonParser()
foxnews.site = 'www.foxnews.com'
foxnews.paths = ["$.posts.*.message"]
foxnews.preprocess = pipe(make_startswith("    /* */ j"), foxnews.preprocess)
foxnews_template = Template('http://foxnews.disqus.com/thread.js?$query')
def foxnews_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '100',
          'url'       : url}
  return foxnews_template.substitute({'query' : urllib.urlencode(args)})
foxnews.rename = types.MethodType (foxnews_rename, foxnews)


fullcomment_nationalpost = JsonParser()
fullcomment_nationalpost.site = 'fullcomment.nationalpost.com'
fullcomment_nationalpost.paths = ["$.posts.*.message"]
fullcomment_nationalpost.preprocess = pipe(make_startswith("    /* */ j"), fullcomment_nationalpost.preprocess)
nationalpost_template = Template('http://npdigital.disqus.com/thread.js?url=$url')
def nationalpost_rename(self, url, site):
  args = {'url' : urllib.quote(url, '')}
  return nationalpost_template.substitute(args) 
fullcomment_nationalpost.rename = types.MethodType (nationalpost_rename, fullcomment_nationalpost)

guardian = DummyParser()
guardian.site = 'www.guardian.co.uk'

huffingtonpost = HtmlParser()
huffingtonpost.site = 'www.huffingtonpost.com'
huffingtonpost.attrs = {u'class': u'comment_body'}
huffingtonpost.strainer = SoupStrainer('div', {u'id': re.compile(u'comments_inner_.*')})
huffingtonpost.tags = 'div'
def huffingtonpost_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    text = text[text.find('on'):]
    comment.text = text[text.find('\n'):]
  return comment_list
huffingtonpost.postprocess = \
  types.MethodType(huffingtonpost_postprocess, huffingtonpost)



news_cnet = HtmlParser()
news_cnet.site = 'news.cnet.com'
news_cnet.attrs = {u'class': u'commentBody'}
news_cnet.strainer = SoupStrainer('section', {u'class': u'commentwrapper'})
news_cnet.tags = 'dd'
news_cnet_regex = re.compile(
 '.*?news.cnet.com/\d+\-(?P<key>\d+_\d+\-\d+)-\d+.*')
news_cnet_template = Template('http://news.cnet.com/8614-$key.html?assetTypeId=12&nomesh&formCommunityId=2070&formTargetCommunityId=2070')
def cnet_rename(self, url, site):
  key = news_cnet_regex.search(url).group('key')
  return news_cnet_template.substitute({'key':key})
  #TODO possibly needs community id
news_cnet.rename = types.MethodType (cnet_rename, news_cnet)

news_yahoo = HtmlParser()
news_yahoo.site = 'news.yahoo.com'
news_yahoo.attrs = {u'class': u'ugccmt-commenttext' }
news_yahoo.strainer = SoupStrainer('ul', {u'id': u'ugccmt-comments', u'class': u'ugccmt-comments'})
news_yahoo.tags = 'blockquote'

newsvine = HtmlParser()
newsvine.site = 'www.newsvine.com'
newsvine.attrs = {u'class': u'commentSource'}
newsvine.strainer = SoupStrainer('div', {u'id': re.compile(u'commentText_.*'), u'class': u'c_text'})
newsvine.tags = 'div'

npr = JsonParser()
npr.site = 'www.npr.org'
npr.paths = ["$.ResponseBatch.Responses.1.CommentPage.Comments.*.CommentBody"]
npr_regex = re.compile('.*?npr.org/\d+/\d+/\d+/(?P<key>\d+)/.*')
npr_template = Template('http://community.npr.org/ver1.0/Direct/jsonp?$request&cb=RequestBatch.callbacks.daapiCallback6568')
def npr_rename(self, url, site):
  key = npr_regex.search(url).group('key')
  request = {"Requests":[{"ArticleKey":{}},{"CommentPage":{"ArticleKey":{"ArticleKey":{}},"NumberPerPage":10,"OnPage":1,"Sort":"TimeStampDescending"}},{"UserKey":{}}],"UniqueId":6568}
  request['Requests'][0]['ArticleKey']['Key'] = str(int(key))
  request['Requests'][1]['CommentPage']['ArticleKey']['ArticleKey']['Key']=  str(int(key))
  request = urllib.urlencode({'r':request})
  return npr_template.substitute({'request':request})

npr.rename = \
  types.MethodType (npr_rename, npr)

online_wsj = HtmlParser()
online_wsj.site = 'online.wsj.com'
online_wsj.attrs = {u'id': re.compile(u'commentcontent.*'), u'class': u'body'}
online_wsj.strainer = SoupStrainer('ul', {u'class': u'unitList unitType-thread'})
online_wsj.tags = 'div'
online_wsj_regex = re.compile(
 '.*?online.wsj.com/article/(?P<uri>.*?).html')
online_wsj_template = Template('http://online.wsj.com/community/mdcrpc/comments/GetArticlecommentsInitialPage.sync?commentEntryId=&locale=&s.href=&s.locale=&s.name=&s.tags=&s.typeName=story&s.uri=$uri')
def wsj_rename(self, url, site):
  uri = online_wsj_regex.search(url).group('uri')
  return online_wsj_template.substitute({'uri':uri})
online_wsj.rename = types.MethodType (wsj_rename, online_wsj)
def wsj_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text
    text = text[:text.rfind('Recommend')]
    comment.text = text[:text.rfind('\n')]
  return comment_list
online_wsj.postprocess = \
  types.MethodType(wsj_postprocess, online_wsj)

# Make iterative parser
politico_blog = HtmlParser()
politico_blog.attrs = {}
politico_blog.strainer = SoupStrainer('ol', {u'id': u'blogComments'})
politico_blog.tags = 'li'

politico = HtmlParser()
politico.attrs = {u'class': u'submitted-comment clearfix'}
politico.strainer = SoupStrainer('ol', {u'id': u'commentsList'})
politico.tags = 'div'

politico_iterative = IterativeParser()
politico_iterative.site = 'www.politico.com'
def politico_parse_all(self, url_site):
  blog_urls = {url:site for url, site in url_site.iteritems() if '/blogs/' in url_site}
  rest_urls = {url:site for url, site in url_site.iteritems() if url not in blog_urls}
  self.url_data = politico_blog.parse_all(blog_urls)
  self.url_data.update(politico.parse_all(rest_urls))
  return self.url_data

politico_iterative.parse_all = \
  types.MethodType (politico_parse_all, politico_iterative)


rawstory = JsonParser()
rawstory.site = 'rawstory.com'
rawstory.paths = ["$.posts.*.message"]
rawstory.preprocess = pipe(make_startswith("    /* */ j"), rawstory.preprocess)
rawstory_template = Template('http://rawstory.disqus.com/thread.js?$query')
def rawstory_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '100',
          'url'       : url}
  return rawstory_template.substitute({'query' : urllib.urlencode(args)})
rawstory.rename = types.MethodType (rawstory_rename, rawstory)

reuters = HtmlParser()
reuters.site = 'www.reuters.com'
reuters.attrs = {u'class': u'commentsBody'}
reuters.strainer = SoupStrainer('div', {u'class': u'articleComments', u'id': u'commentsTab'})
reuters.tags = 'div'
reuters_template = Template('http://reuters.com/article/comments/$key')
def reuters_rename(self, url, site):
  key = url.split('-')[-1].strip()
  return reuters_template.substitute({'key':key})

reuters.rename = types.MethodType (reuters_rename, reuters)

theatlantic = JsonParser()
theatlantic.site = 'www.theatlantic.com'
theatlantic.paths = ["$.posts.*.message"]
theatlantic.preprocess = pipe(make_startswith("    /* */ j"), theatlantic.preprocess)
theatlantic_template = Template('http://theatlantic.disqus.com/thread.js?$query')
def atlantic_rename(self, url, site):
  article_id = url[url[:-1].rfind('/'):]
  args = {'identifier': 'mt%s' % article_id.replace('/', ''),
          'url'       : url}
  return theatlantic_template.substitute({'query' : urllib.urlencode(args)})
theatlantic.rename = \
  types.MethodType (atlantic_rename, theatlantic)


theglobeandmail = AsyncHtmlParser()
theglobeandmail.site = 'www.theglobeandmail.com'
theglobeandmail.attrs = {u'class': u'pluck-comm-body'}
theglobeandmail.strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list.*')})
theglobeandmail.tags = 'p'
theglobeandmail_regex = re.compile('globeandmail.com.*article(?P<id>\d+)')
theglobeandmail_template = Template('http://sitelife.theglobeandmail.com/ver1.0/sys/jsonp.app?widget_path=tgam/pluck/comments.app&clientUrl=$url%2F&plckCommentOnKeyType=article&plckArticleTitle=Mourners%20bid%20farewell%20to%20North%20Korea%26rsquo%3Bs%20Kim%20Jong-il&plckCommentOnKey=ArticleID$id&plckArticleUrl=$url%2F&plckDiscoverySection=news&plckDiscoveryCategories=ece_frontpage%2Cworld%2Cnews&cb=plcb0')
def globeandmail_rename(self, url, site):
  args = {'id' : theglobeandmail_regex.search(url).group('id'),
          'url': urllib.quote(url, '')}
  return theglobeandmail_template.substitute(args)
theglobeandmail.rename = \
  types.MethodType (globeandmail_rename, theglobeandmail)

#thehill = EscapedHtmlParser()
#thehill.attrs = {u'class': u'comment-body'}
#thehill.preprocess = pipe(make_startswith("			<sc"), thehill.preprocess)
#thehill.strainer = SoupStrainer('div', {u'id': u'comments-list', u'class': u'comments-list'})
#thehill.tags = 'span'

thisislondon_co = HtmlParser()
thisislondon_co.site = 'www.thisislondon.co.uk'
thisislondon_co.attrs = {u'class': re.compile(u'comment.*')}
thisislondon_co.strainer = SoupStrainer('div', {u'id': u'readerComments'})
thisislondon_co.tags = 'p'

washingtonpost = JsonParser()
washingtonpost.paths = ["$.entries.*.object.content"]
washingtonpost_regex = re.compile('(?P<url>.*?washingtonpost.com.*?.html).*')
washingtonpost_template = Template('http://echoapi.washingtonpost.com/v1/search?callback=jsonp1326063163544&q=((childrenof%3A+$url+source%3Awashpost.com+++))+itemsPerPage%3A+100+sortOrder%3A+reverseChronological+safeHTML%3Aaggressive+children%3A+2+++&appkey=prod.washpost.com')
def washingtonpost_rename(self, url, site):
  url = urllib.quote(washingtonpost_regex.search(url).group('url'))
  return washingtonpost_template.substitute({'url':url})

washingtonpost.rename = \
  types.MethodType (washingtonpost_rename, washingtonpost)

voices_washingtonpost = HtmlParser()
voices_washingtonpost.strainer = SoupStrainer('div', {u'class': u'commentText'})
voices_washingtonpost.tags = 'p'
voices_washingtonpost.attrs = {}

# iterative parser again
washingtonpost_iterative = IterativeParser()
washingtonpost_iterative.site = 'washingtonpost.com'
def washingtonpost_parse_all(self, url_site):
  blog_urls = {url:site for url, site in url_site.iteritems() 
    if url.startswith('http://voices.washingtonpost.com')}
  rest_urls = {url:site for url, site in url_site.iteritems() if url not in blog_urls}
  self.url_data = voices_washingtonpost.parse_all(blog_urls)
  self.url_data.update(washingtonpost.parse_all(rest_urls))
  return self.url_data

washingtonpost_iterative.parse_all = \
  types.MethodType (washingtonpost_parse_all, washingtonpost_iterative)

sfgate = copy.copy(theglobeandmail)
sfgate.site = 'www.sfgate.com'
sfgate_template = Template('http://contribute.sfgate.com/ver1.0/sys/jsonp.app?widget_path=pluck/comments.app&plckcommentonkeytype=article&plckcommentonkey=$query&plckshortlist=false&plckrefreshpage=true&plckdiscoverysection=Articles&plcksort=TimeStampDescending&plckitemsperpage=10&plckarticleurl=$url&hdnpluck_refreshbaseurl=$url&hdnpluck_imageserver=http%3A%2F%2Fimgs.sfgate.com&clientUrl=$url&cb=plcb0u0')
def sfgate_rename(self, url, site):
  params = url.split('?')[-1]
  url = 'http://www.sfgate.com/cgi-bin/article/comments/view?%s' % params
  args = {'url' : urllib.quote(url, ''),
          'query': urllib.quote(params.split('=')[-1],'')}
  return sfgate_template.substitute(args)
sfgate.rename = types.MethodType (sfgate_rename, sfgate)

usatoday = copy.copy(theglobeandmail)
usatoday.site = 'content.usatoday.com'
#http://content.usatoday.com/communities/onpolitics/post/2012/02/ron-paul-nevada-caucuses-intellectual-revolution-/1
usatoday_template = Template('http://sitelife.usatoday.com/ver1.0/sys/jsonp.app?widget_path=usat/pluck/comments.app&plckcommentonkeytype=article&plckcommentonkey=$key.story&clientUrl=$url&cb=plcb0')
def usatoday_rename(self, url, site):
  # Todo test me on other sites
  key = url.split('/')[-2]
  args = {'url' : urllib.quote(url, ''),
          'key': key}
  return usatoday_template.substitute(args)
usatoday.rename = types.MethodType (usatoday_rename, usatoday)

newsobserver = JsonParser()
newsobserver.site = 'www.newsobserver.com'
newsobserver.paths = ["$.posts.*.message"]
newsobserver.preprocess = pipe(make_startswith("    /* */ j"), newsobserver.preprocess)
newsobserver_template = Template('http://newsobserver.disqus.com/thread.js?$query')
def newsobserver_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '100',
          'url'       : url}
  return newsobserver_template.substitute({'query' : urllib.urlencode(args)})
newsobserver.rename = types.MethodType (newsobserver_rename, newsobserver)

thehill = JsonParser()
thehill.site = 'thehill.com'
thehill.paths = ["$.posts.*.message"]
thehill.preprocess = pipe(make_startswith("    /* */ j"), thehill.preprocess)
thehill_template = Template('http://thehill-v4.disqus.com/thread.js?$query')
def thehill_rename(self, url, site):
  if '?' in url:
    url = url[:url.rfind('?')]
  args = {'per_page': '100',
          'url'       : url}
  return thehill_template.substitute({'query' : urllib.urlencode(args)})
thehill.rename = types.MethodType (thehill_rename, thehill)

thestar = JsonParser()
thestar.site = 'www.thestar.com'
thestar.paths = ["$.data.*.Text"]
#http://www.thestar.com/news/article/1127975--special-transit-meeting-karen-stintz-readies-motion-to-put-lrt-on-finch-and-eglinton-and-strike-panel-to-study-options-on-sheppard
thestar_regex = re.compile('http://www.thestar.com/.*/(?P<id>\d+)')
thestar_template = Template('http://www.thestar.com/toplets/commenting/data/listcomments.aspx?assetid=$assetid&sortby=recent&pagenumber=1&pagesize=10')
def thestar_rename(self, url, site):
  args = {'assetid' : thestar_regex.search(url).group('id')}
  return thestar_template.substitute(args)
thestar.rename = types.MethodType (thestar_rename, thestar)

calgaryherald = AsyncHtmlParser()
calgaryherald.site = 'www.calgaryherald.com'
calgaryherald.tags = 'p'
calgaryherald.attrs = {u'class': u'pluck-comm-body'}
calgaryherald.strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list_.*')})
#http://www.calgaryherald.com/news/calgary/Family+other+interests+Blackett+leaving+after+term/5988262/story.html
calgaryherald_template = Template('http://pluck.calgaryherald.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0')
def calgaryherald_rename(self, url, site):
  #TODO: Actually calculate the key and url
  key = url[:url.rfind('/')]
  key = key[key.rfind('/') + 1:]
  args = {'url' : urllib.quote(url, ''),
          'key': key}
  return calgaryherald_template.substitute(args) 
calgaryherald.rename = types.MethodType (calgaryherald_rename, calgaryherald)

opinion_financialpost = JsonParser()
opinion_financialpost.site = 'opinion.financialpost.com'
opinion_financialpost.paths = ["$.posts.*.message"]
opinion_financialpost.preprocess = pipe(make_startswith("    /* */ j"), opinion_financialpost.preprocess)
#http://opinion.financialpost.com/2012/01/12/william-watson-lets-hear-it-for-the-1/
opinion_financialpost_template = Template('http://financialpost.disqus.com/thread.js?url=$url')
def opinion_financialpost_rename(self, url, site):
  args = {'url' : urllib.quote(url, '')}
  return opinion_financialpost_template.substitute(args) 
opinion_financialpost.rename = types.MethodType (opinion_financialpost_rename, opinion_financialpost)

terracestandard = EscapedHtmlParser()
terracestandard.site = 'www.terracestandard.com'
terracestandard.strainer = SoupStrainer('ul', {u'class': u'uiList fbFeedbackPosts'})
terracestandard.tags = 'div'
terracestandard.attrs = {u'class': u'postText'}
terracestandard.preprocess = pipe(make_startswith("  <"), terracestandard.preprocess)
#http://www.terracestandard.com/news/137101033.html
terracestandard_template = Template('https://www.facebook.com/plugins/comments.php?$args')
def terracestandard_rename(self, url, site):
  netloc = urlparse.urlparse(url).netloc
  default_args = {'origin': netloc,
                  'width': '626', 
                  'locale': 'en_US',
                  'numposts': '10',
                  'href': url,
                  'relation': 'parent.parent',
                  'api_key': '242325202492798',  # may need to randomly change me
                  'channel_url': 'https://s-static.ak.fbcdn.net/connect/xd_proxy.php?version=3#cb=f37ac5583fdd422',
                  'transport': 'postmessage',
                  'sdk': 'joey'}
  args = {'args' : urllib.urlencode(default_args)}
  return terracestandard_template.substitute(args)
terracestandard.rename = types.MethodType (terracestandard_rename, terracestandard)

timescolonist = AsyncHtmlParser()
timescolonist.site = 'www.timescolonist.com'
timescolonist.strainer = SoupStrainer('div', {u'id': re.compile(u'pluck_comments_list_.*')})
timescolonist.tags = 'p'
timescolonist.attrs = {u'class': u'pluck-comm-body'}
#http://www.timescolonist.com/news/Thousands+stolen+from+former+UVic+employee+bank+account/5988143/story.html
timescolonist_template = Template('http://pluck.timescolonist.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plckdiscoverysection=VITC_news&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0')
def timescolonist_rename(self, url, site):
  key = url[:url.rfind('/')]
  key = key[key.rfind('/') + 1:]
  args = {'url' : urllib.quote(url, ''),
          'key': key}
  return timescolonist_template.substitute(args) 
timescolonist.rename = types.MethodType (timescolonist_rename, timescolonist)

aptn = HtmlParser()
aptn.site = 'aptn.ca'
aptn.strainer = SoupStrainer('ul', {u'id': u'dsq-comments'})
aptn.tags = 'div'
aptn.attrs = {u'class': u'dsq-comment-message'}

ctv = HtmlParser()
ctv.site = 'www.ctv.ca'
ctv.strainer = SoupStrainer('div', {u'class': u'commentDiv'})
ctv.tags = 'div'
ctv.attrs = {u'class': u'divider'}
def ctv_postprocess(self, comment_list):
  for comment in comment_list:
    text = comment.text.replace('googleon: index  googleoff: index', '')
    comment.text = text[text.find('said') + 4:]
  return comment_list
ctv.postprocess = types.MethodType(ctv_postprocess, ctv)

thesudburystar = HtmlParser()
thesudburystar.site = 'www.thesudburystar.com'
thesudburystar.strainer = SoupStrainer('div', {u'class': u'commentcontent'})
thesudburystar.tags = 'div'
thesudburystar.attrs = {u'class': u'commentcontent'}

cnews_canoe = HtmlParser()
cnews_canoe.site = 'cnews.canoe.ca/CNEWS/Comment'
cnews_canoe.strainer = SoupStrainer('div', {u'id': u'comments'})
cnews_canoe.tags = 'div'
cnews_canoe.attrs = {u'class': re.compile('comments_row.*')}

edmontonjournal = AsyncHtmlParser()
edmontonjournal.site = 'www.edmontonjournal.com'
edmontonjournal.tags = 'p'
edmontonjournal.attrs = {u'class': u'pluck-comm-body'}
edmontonjournal.strainer = SoupStrainer('div', {u'id': re.compile('pluck_comments_list_.*')})
#http://www.edmontonjournal.com/news/Staples+bomb+sensors+waste+money/5987764/story.html?cid=dlvr.it-twitter-edmontonjournal
edmontonjournal_template = Template('http://pluck.edmontonjournal.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0')
def edmontonjournal_rename(self, url, site):
  #TODO actually fix this
  key = url[:url.rfind('/')]
  key = key[key.rfind('/') + 1:]
  args = {'url' : urllib.quote(url, ''),
          'key': key}
  return edmontonjournal_template.substitute(args) 
edmontonjournal.rename = types.MethodType (edmontonjournal_rename, edmontonjournal)

upi = JsonParser()
upi.site = 'www.upi.com'
upi.paths = ["$.comments"]
#http://www.upi.com/Odd_News/2012/01/08/Slavery-math-problems-irk-Ga-parents/UPI-29921326042191/
upi_regex = re.compile('/UPI-(?P<code>\d+)')
upi_template = Template('http://www.upi.com/upi_comments/io?uc_list=1&page_id=$code&limit=100&page_type=story&&_=1326593639443')

def upi_rename(self, url, site):
  code = upi_regex.search(url).groupdict()
  return upi_template.substitute(code)
upi.rename = types.MethodType (upi_rename, upi)

# Html inside json string, so two pass parsing
upi_inner = HtmlParser()
upi_inner.strainer = SoupStrainer('div', {u'class': u'comments'})
upi_inner.tags = 'div'
upi_inner.attrs = {u'class': u'comment'}
def upi_postprocess(self, comment_list):
  temp_list = []
  for comment in comment_list:
    temp_list += upi_inner.custom_parse(comment.text)
  return temp_list
upi.postprocess = types.MethodType(upi_postprocess, upi)

voices_yahoo = HtmlParser()
voices_yahoo.site = 'voices.yahoo.com'
voices_yahoo.attrs = {u'class': u'content'}
voices_yahoo.strainer = SoupStrainer('div', {u'class': u'comment_list'})
voices_yahoo.tags = 'p'

community_seattletimes_nwsource = HtmlParser()
community_seattletimes_nwsource.site = 'seattletimes.nwsource.com'
community_seattletimes_nwsource.strainer = SoupStrainer('div', {u'id': u'leftcolumn'})
community_seattletimes_nwsource.tags = 'div'
community_seattletimes_nwsource.attrs = {u'class': u'gc_comments_comment'}
#http://seattletimes.nwsource.com/html/nationworld/2017242945_cruiseship15.html
seattletimes_regex = re.compile('/(?P<source_id>\d+)_')
seattletimes_template = Template('http://community.seattletimes.nwsource.com/reader_feedback/public/display.php?source_id=$source_id&source_name=mbase')
def seattletimes_rename(self, url, site):
  source_id = seattletimes_regex.search(url).groupdict()
  return seattletimes_template.substitute(source_id)
community_seattletimes_nwsource.rename = types.MethodType (seattletimes_rename, community_seattletimes_nwsource)

vancouversun = AsyncHtmlParser()
vancouversun.site = 'www.vancouversun.com'
vancouversun.strainer = SoupStrainer('div', {u'id': re.compile('pluck_comments_list_.*')})
vancouversun.tags = 'p'
vancouversun.attrs = {u'class': u'pluck-comm-body'}
vancouversun_regex = re.compile('id=(?P<id>\d+)|/(?P<id2>\d+)/')

#http://www.vancouversun.com/life/Opinion+Restricting+Chinese+language+signs+Canadian/5988028/story.html
vancouversun_template = Template('http://pluck.vancouversun.com/ver1.0/sys/jsonp.app?widget_path=newspaper1/pluck/comments.app&plckrefreshpage=false&plckcommentonkeytype=article&plckcommentonkey=SP6%3A$key&plcksort=TimeStampDescending&plckanonymouspostingallowed=false&plckpersonadisabled=true&plckcommentsubmitdisabled=false&clientUrl=$url&cb=plcb0u0')

def vancouversun_rename(self, url, site):
  args = {'url' : urllib.quote(url, '')}
  args['key'] = vancouversun_regex.search(url).group('id')
  if not args['key']:
     args['key'] = vancouversun_regex.search(url).group('id2')

  return vancouversun_template.substitute(args)
vancouversun.rename = types.MethodType (vancouversun_rename, vancouversun)

straight = HtmlParser()
straight.site = 'www.straight.com'
straight.strainer = SoupStrainer('div', {u'id': u'comments'})
straight.tags = 'div'
straight.attrs = {u'class': u'comment-body'}

winnipegsun = JsonParser()
winnipegsun.site = 'www.winnipegsun.com'
winnipegsun.paths = ["$.posts.*.message"]
winnipegsun.preprocess = pipe(make_startswith("    /* */ j"), winnipegsun.preprocess)
#http://www.winnipegsun.com/2012/01/13/suspects-caught-after-smoke-run
winnipegsun_template = Template('http://winnipegsun.disqus.com/thread.js?url=$url')
def winnipegsun_rename(self, url, site):
  args = {'url' : urllib.quote(url, '')}
  return winnipegsun_template.substitute(args) 
winnipegsun.rename = types.MethodType (winnipegsun_rename, winnipegsun)

canadianbusiness = JsonParser()
canadianbusiness.site = 'www.canadianbusiness.com'
canadianbusiness.paths = ["$.data.*.Text"]
#http://www.canadianbusiness.com/blog/business_ethics/65217--is-animal-cruelty-illegal-but-ethical
canadianbusiness_regex = re.compile('/(?P<assetid>\d+)--')
canadianbusiness_template = Template('http://www.canadianbusiness.com/toplets/commenting/data/listcomments.aspx?assetid=$assetid&sortby=recent&pagenumber=1&pagesize=10')
def canadianbusiness_rename(self, url, site):
  asset_id = canadianbusiness_regex.search(url).groupdict()
  return canadianbusiness_template.substitute(asset_id)
canadianbusiness.rename = types.MethodType (canadianbusiness_rename, canadianbusiness)

