from BeautifulSoup import SoupStrainer
from generalParsers import *
import types

abcnews_go = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'post-\d+'}),
  targets = SoupStrainer('p', {})
)

aptn = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'entry'}),
  targets = SoupStrainer('p', {})
)

breitbart = HtmlParser(
  strainer = SoupStrainer('span', {u'class': re.compile('lingo_region')}),
  targets = SoupStrainer('p', {})
)

businessinsider = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'post-content'}),
  targets = SoupStrainer('p', {}),
)

cnews_canoe = HtmlParser(
  strainer = SoupStrainer('table'),
  targets = SoupStrainer('p', {})
)

csmonitor = HtmlParser(
  strainer = SoupStrainer('div', {'class':'sBody'}),
  targets = SoupStrainer('p', {})
)

usatoday = HtmlParser(
  strainer = SoupStrainer('div', {'id':'post-body'}),
  targets = SoupStrainer('p', {})
)

foxnews = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'entry-content  KonaBody'}),
  targets = SoupStrainer('p', {})
)

fullcomment_nationalpost = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'npBlock npPostContent'}),
  targets = SoupStrainer('p', {})
)

guardian = HtmlParser(
  strainer = SoupStrainer('div', {'id':'article-body-blocks'}),
  targets = SoupStrainer('p', {})
)

news_cnet = HtmlParser(
  strainer = SoupStrainer('div', {u'section': u'txt', u'class': u'postBody txtWrap'}),
  targets = SoupStrainer('p', {})
)

news_yahoo = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'.*yom-art-content.*'}),
  targets = SoupStrainer('div', {u'class': u'bd'})
)

online_wsj = HtmlParser(
  strainer = SoupStrainer('div', {'class':re.compile('article.*')}),
  targets = SoupStrainer('p', {})
)

opinion_financialpost = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'npBlock npPostContent'}),
  targets = SoupStrainer('p', {})
)

rawstory = HtmlParser(
  strainer = SoupStrainer('div', {u'id': re.compile(u'post-.*')}),
  targets = SoupStrainer('p', {})
)

community_seattletimes_nwsource = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'body'}),
  targets = SoupStrainer('p', {})
)

talkingpointsmemo = HtmlParser(
  strainer = SoupStrainer('body', {u'blogtag': u'general'}),
  targets = SoupStrainer('p', {})
)

thehill = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'txt', u'id': u'el-article-div'}),
  targets = SoupStrainer('p', {})
)

thestar = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'dataTabarticle', u'class': u'ts-article'}),
  targets = SoupStrainer('p', {'class':None})
)

washingtonpost = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'article_body'}),
  targets = SoupStrainer('p', {})
)

voices_washingtonpost = HtmlParser(
  strainer = SoupStrainer(check_any_attr('entrytext')),
  targets = SoupStrainer('p', {})
)

americanthinker = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'article_body'}),
  targets = SoupStrainer('span', {})
)

calgaryherald = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'story_content'}),
  targets = SoupStrainer('p', {})
)

canadianbusiness = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'articleText description'}),
  targets = SoupStrainer('p', {})
)

cbc = HtmlParser(
  strainer = SoupStrainer('div', {u'aria-labelledby': u'storyhead', u'role': u'main', u'id': u'storybody'}),
  targets = SoupStrainer('p', {})
)

cbsnews = HtmlParser(
  strainer = SoupStrainer('div', {'class':re.compile('postBody|storyText')}),
  targets = SoupStrainer('div', {'class':re.compile('postBody|storyText')})
)

discussions_chicagotribune = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'story-body-text'}),
  targets = SoupStrainer('div', {u'id': u'story-body-text'})
)

cnn = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'cnn_strycntntlft'}),
  targets = SoupStrainer('p', {})
)

ctv = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'mainBody'}),
  targets = SoupStrainer('p', {})
)

economist = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'ec-blog-body'}),
  targets = SoupStrainer('p', {})
)

edmontonjournal = HtmlParser(
  strainer = SoupStrainer('div', {u'id': 'story_content'}),
  targets = SoupStrainer('p', {})
)

huffingtonpost = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'entry_body_text'}),
  targets = SoupStrainer('p', {})
)

discussions_latimes = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'story-body-text'}),
  targets = SoupStrainer('div', {u'id': u'story-body-text'})
)

newsobserver = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'story_body'}),
  targets = SoupStrainer('p', {})
)

newsvine = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'articleText'}),
  targets = SoupStrainer('p', {})
)

npr = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'storybody'}),
  targets = SoupStrainer('p', {'class' : None})
)

community_nytimes = HtmlParser(
  strainer = SoupStrainer('div', {'class': re.compile(u'articleBody|nytint-post')}),
  targets = SoupStrainer('p', {})
)

politico = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'story-text resize'}),
  targets = SoupStrainer('p', {})
)

politico_blog = HtmlParser(
  strainer = SoupStrainer('div', {u'class': re.compile('entry-content')}),
  targets = SoupStrainer('p', {})
)

# Note gets comments right now

reuters = HtmlParser(
  strainer = SoupStrainer('span', {u'id': re.compile(u'articleText')}),
  targets = SoupStrainer('p', {})
)

sfgate = HtmlParser(
  strainer = SoupStrainer('div', {u'id': re.compile(u'bodytext_')}),
  targets = SoupStrainer('p', {'class':None})
)

straight = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'article_body'}),
  targets = SoupStrainer('p', {})
)

terracestandard = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'story'}),
  targets = SoupStrainer('p', {})
)

theatlantic = HtmlParser(
  strainer = SoupStrainer('div', {u'class': u'articleContent'}),
  targets = SoupStrainer('div', {u'class': u'articleContent'})
)

theglobeandmail = HtmlParser(
  strainer = SoupStrainer('div', {u'class': re.compile(u'articlecopy')}),
  targets = SoupStrainer('p', {})
)

thesudburystar = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'ctl00_ContentPlaceHolder1_pMainContent'}),
  targets = SoupStrainer('p', {})
)

# Currently gets comments

thisislondon_co = HtmlParser(
  strainer = SoupStrainer('div', {u'id': u'article'}),
  targets = SoupStrainer('p', {})
)

timescolonist = HtmlParser(
  strainer = SoupStrainer('div', {u'id': re.compile(u'page.*')}),
  targets = SoupStrainer('p', {})
)

upi = HtmlParser(
  strainer = SoupStrainer('p', {}),
  targets = SoupStrainer('p', {})
)

vancouversun = HtmlParser(
  strainer = SoupStrainer('div', {u'id':'story_content'}),
  targets = SoupStrainer('p', {})
)

voices_yahoo = HtmlParser(
  strainer = SoupStrainer('div', {u'id': 'article_text_blocks'}),
  targets = SoupStrainer('div', {u'id': 'article_text_blocks'})
)

winnipegsun = HtmlParser(
  strainer = SoupStrainer('div', {u'class': re.compile('content')}),
  targets = SoupStrainer('p', {'class':None})
)

# iterative parser again
washingtonpost_iterative = IterativeParser(
  dispatchers = [(lambda url: url.startswith('http://voices.washingtonpost.com'), voices_washingtonpost),
                 (lambda url: True, washingtonpost),
                ]
)

politico_iterative = IterativeParser(
  dispatchers = [(lambda url: '/blogs/' in url, politico_blog),
                 (lambda url: True, politico),
                ],
)

arstechnica = HtmlParser (
  strainer = SoupStrainer('div', {u'class': u'article-content clearfix'}),
  targets = SoupStrainer('div', {u'class': u'article-content clearfix'}),
)
