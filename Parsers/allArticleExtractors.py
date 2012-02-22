from BeautifulSoup import SoupStrainer
from generalParsers import *
import types

abcnews_go = HtmlParser()
abcnews_go.strainer = SoupStrainer('div', {u'id': u'post-\d+'})
abcnews_go.tags = 'p'
abcnews_go.attrs = {}

aptn = HtmlParser()
aptn.strainer = SoupStrainer('div', {u'class': u'entry'})
aptn.tags = 'p'
aptn.attrs = {}

breitbart = HtmlParser()
breitbart.strainer = SoupStrainer('span', {u'class': re.compile('lingo_region')})
breitbart.tags = 'p'
breitbart.attrs = {}

businessinsider = HtmlParser()
businessinsider.attrs = {}
businessinsider.strainer = SoupStrainer('div', {u'class': u'post-content'})
businessinsider.tags = 'p'

cnews_canoe = HtmlParser()
cnews_canoe.strainer = SoupStrainer('table')
cnews_canoe.tags = 'p'
cnews_canoe.attrs = {}

csmonitor = HtmlParser()
csmonitor.strainer = SoupStrainer('div', {'class':'sBody'})
csmonitor.tags = 'p'
csmonitor.attrs = {}

usatoday = HtmlParser()
usatoday.strainer = SoupStrainer('div', {'id':'post-body'})
usatoday.tags = 'p'
usatoday.attrs = {}

foxnews = HtmlParser()
foxnews.strainer = SoupStrainer('div', {u'class': u'entry-content  KonaBody'})
foxnews.tags = 'p'
foxnews.attrs = {}

fullcomment_nationalpost = HtmlParser()
fullcomment_nationalpost.strainer = SoupStrainer('div', {u'class': u'npBlock npPostContent'})
fullcomment_nationalpost.tags = 'p'
fullcomment_nationalpost.attrs = {}

guardian = HtmlParser()
guardian.strainer = SoupStrainer('div', {'id':'article-body-blocks'})
guardian.tags = 'p'
guardian.attrs = {}

news_cnet = HtmlParser()
news_cnet.strainer = SoupStrainer('div', {u'section': u'txt', u'class': u'postBody txtWrap'})
news_cnet.tags = 'p'
news_cnet.attrs = {}

news_yahoo = HtmlParser()
news_yahoo.strainer = SoupStrainer('div', {u'class': u'.*yom-art-content.*'})
news_yahoo.tags = 'div'
news_yahoo.attrs = {u'class': u'bd'}

online_wsj = HtmlParser()
online_wsj.strainer = SoupStrainer('div', {'class':re.compile('article.*')})
online_wsj.tags = 'p'
online_wsj.attrs = {}

opinion_financialpost = HtmlParser()
opinion_financialpost.strainer = SoupStrainer('div', {u'class': u'npBlock npPostContent'})
opinion_financialpost.tags = 'p'
opinion_financialpost.attrs = {}

rawstory = HtmlParser()
rawstory.strainer = SoupStrainer('div', {u'id': re.compile(u'post-.*')})
rawstory.tags = 'p'
rawstory.attrs = {}

community_seattletimes_nwsource = HtmlParser()
community_seattletimes_nwsource.strainer = SoupStrainer('div', {u'class': u'body'})
community_seattletimes_nwsource.tags = 'p'
community_seattletimes_nwsource.attrs = {}

talkingpointsmemo = HtmlParser()
talkingpointsmemo.strainer = SoupStrainer('body', {u'blogtag': u'general'})
talkingpointsmemo.tags = 'p'
talkingpointsmemo.attrs = {}

thehill = HtmlParser()
thehill.strainer = SoupStrainer('div', {u'class': u'txt', u'id': u'el-article-div'})
thehill.tags = 'p'
thehill.attrs = {}

thestar = HtmlParser()
thestar.strainer = SoupStrainer('div', {u'id': u'dataTabarticle', u'class': u'ts-article'})
thestar.tags = 'p'
thestar.attrs = {'class':None}

washingtonpost = HtmlParser()
washingtonpost.strainer = SoupStrainer('div', {u'id': u'article_body'})
washingtonpost.tags = 'p'
washingtonpost.attrs = {}

def check_any_attr(text):
  def check_attrs(name, attrs):
    return name == 'div' and text in [attr[1] for attr in attrs]
  return check_attrs

voices_washingtonpost = HtmlParser()
voices_washingtonpost.strainer = SoupStrainer(check_any_attr('entrytext'))
voices_washingtonpost.tags = 'p'
voices_washingtonpost.attrs = {}

americanthinker = HtmlParser()
americanthinker.strainer = SoupStrainer('div', {u'class': u'article_body'})
americanthinker.tags = 'span'
americanthinker.attrs = {}

calgaryherald = HtmlParser()
calgaryherald.strainer = SoupStrainer('div', {u'id': u'story_content'})
calgaryherald.tags = 'p'
calgaryherald.attrs = {}

canadianbusiness = HtmlParser()
canadianbusiness.strainer = SoupStrainer('div', {u'class': u'articleText description'})
canadianbusiness.tags = 'p'
canadianbusiness.attrs = {}

cbc = HtmlParser()
cbc.strainer = SoupStrainer('div', {u'aria-labelledby': u'storyhead', u'role': u'main', u'id': u'storybody'})
cbc.tags = 'p'
cbc.attrs = {}

cbsnews = HtmlParser()
cbsnews.strainer = SoupStrainer('div', {'class':re.compile('postBody|storyText')})
cbsnews.tags = 'div'
cbsnews.attrs = {'class':re.compile('postBody|storyText')}

discussions_chicagotribune = HtmlParser()
discussions_chicagotribune.strainer = SoupStrainer('div', {u'id': u'story-body-text'})
discussions_chicagotribune.tags = 'div'
discussions_chicagotribune.attrs = {u'id': u'story-body-text'}

cnn = HtmlParser()
cnn.strainer = SoupStrainer('div', {u'class': u'cnn_strycntntlft'})
cnn.tags = 'p'
cnn.attrs = {}

ctv = HtmlParser()
ctv.strainer = SoupStrainer('div', {u'class': u'mainBody'})
ctv.tags = 'p'
ctv.attrs = {}

economist = HtmlParser()
economist.strainer = SoupStrainer('div', {u'class': u'ec-blog-body'})
economist.tags = 'p'
economist.attrs = {}

edmontonjournal = HtmlParser()
edmontonjournal.strainer = SoupStrainer('div', {u'id': 'story_content'})
edmontonjournal.tags = 'p'
edmontonjournal.attrs = {}

huffingtonpost = HtmlParser()
huffingtonpost.strainer = SoupStrainer('div', {u'class': u'entry_body_text'})
huffingtonpost.tags = 'p'
huffingtonpost.attrs = {}

discussions_latimes = HtmlParser()
discussions_latimes.strainer = SoupStrainer('div', {u'id': u'story-body-text'})
discussions_latimes.tags = 'div'
discussions_latimes.attrs = {u'id': u'story-body-text'}

newsobserver = HtmlParser()
newsobserver.strainer = SoupStrainer('div', {u'id': u'story_body'})
newsobserver.tags = 'p'
newsobserver.attrs = {}

newsvine = HtmlParser()
newsvine.strainer = SoupStrainer('div', {u'class': u'articleText'})
newsvine.tags = 'p'
newsvine.attrs = {}

npr = HtmlParser()
npr.strainer = SoupStrainer('div', {u'id': u'storybody'})
npr.tags = 'p'
npr.attrs = {'class' : None}

community_nytimes = HtmlParser()
community_nytimes.strainer = SoupStrainer('div', {'class': re.compile(u'articleBody|nytint-post')})
community_nytimes.tags = 'p'
community_nytimes.attrs = {}

politico = HtmlParser()
politico.strainer = SoupStrainer('div', {u'class': u'story-text resize'})
politico.tags = 'p'
politico.attrs = {}

politico_blog = HtmlParser()
politico_blog.strainer = SoupStrainer('div', {u'class': re.compile('entry-content')})
politico_blog.tags = 'p'
politico_blog.attrs = {}


# Note gets comments right now
reuters = HtmlParser()
reuters.strainer = SoupStrainer('span', {u'id': re.compile(u'articleText')})
reuters.tags = 'p'
reuters.attrs = {}

sfgate = HtmlParser()
sfgate.strainer = SoupStrainer('div', {u'id': re.compile(u'bodytext_')})
sfgate.tags = 'p'
sfgate.attrs = {'class':None}

straight = HtmlParser()
straight.strainer = SoupStrainer('div', {u'id': u'article_body'})
straight.tags = 'p'
straight.attrs = {}

terracestandard = HtmlParser()
terracestandard.strainer = SoupStrainer('div', {u'id': u'story'})
terracestandard.tags = 'p'
terracestandard.attrs = {}

theatlantic = HtmlParser()
theatlantic.strainer = SoupStrainer('div', {u'class': u'articleContent'})
theatlantic.tags = 'div'
theatlantic.attrs = {u'class': u'articleContent'}

theglobeandmail = HtmlParser()
theglobeandmail.strainer = SoupStrainer('div', {u'class': re.compile(u'articlecopy')})
theglobeandmail.tags = 'p'
theglobeandmail.attrs = {}

thesudburystar = HtmlParser()
thesudburystar.strainer = SoupStrainer('div', {u'id': u'ctl00_ContentPlaceHolder1_pMainContent'})
thesudburystar.tags = 'p'
thesudburystar.attrs = {}

# Currently gets comments
thisislondon_co = HtmlParser()
thisislondon_co.strainer = SoupStrainer('div', {u'id': u'article'})
thisislondon_co.tags = 'p'
thisislondon_co.attrs = {}

timescolonist = HtmlParser()
timescolonist.strainer = SoupStrainer('div', {u'id': re.compile(u'page.*')})
timescolonist.tags = 'p'
timescolonist.attrs = {}

upi = HtmlParser()
upi.strainer = SoupStrainer('p', {})
upi.tags = 'p'
upi.attrs = {}

vancouversun = HtmlParser()
vancouversun.strainer = SoupStrainer('div', {u'id':'story_content'})
vancouversun.tags = 'p'
vancouversun.attrs = {}

voices_yahoo = HtmlParser()
voices_yahoo.strainer = SoupStrainer('div', {u'id': 'article_text_blocks'})
voices_yahoo.tags = 'div'
voices_yahoo.attrs = {u'id': 'article_text_blocks'}

winnipegsun = HtmlParser()
winnipegsun.strainer = SoupStrainer('div', {u'class': re.compile('content')})
winnipegsun.tags = 'p'
winnipegsun.attrs = {'class':None}

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

politico_iterative = IterativeParser()
def politico_parse_all(self, url_site):
  blog_urls = {url:site for url, site in url_site.iteritems() if '/blogs/' in url_site}
  rest_urls = {url:site for url, site in url_site.iteritems() if url not in blog_urls}
  self.url_data = politico_blog.parse_all(blog_urls)
  self.url_data.update(politico.parse_all(rest_urls))
  return self.url_data

politico_iterative.parse_all = \
  types.MethodType (politico_parse_all, politico_iterative)
