import os, sys, re, math
from collections import Counter, namedtuple
import json
import nltk
import HTMLParser
import BeautifulSoup
import heapq
from itertools import count, izip
from preprocessing import preprocess_string
from nltk.stem.porter import PorterStemmer
from datetime import date

modes = ['before', 'after', 'during', 'all']
def print_usage():
  print "usage: trigram_summarizer.py <folder> <mode> <date> [query terms]"
  print "modes: %s" % ','.join(modes)

spaceFinder = re.compile('([^A-Z])([.!?,])([A-Z])')
def insert_spaces(matchobj):
   return matchobj.group(0) + matchobj.group(1) + ' ' + matchobj.group(2)

stemmer = PorterStemmer()
class Comment:
  def __init__(self, url, position, sentences):
    self.url = url
    self.pos = position
    self.sentences = sentences
    self.terms = []
    self.counts = []
 

class Heap(object):
  def __init__(self, size = 5, key=lambda x:x): 
    self.heap = []
    self.size = size
    self.push = self._push
    self.key = key

  def _push(self, item):
    heapq.heappush(self.heap, (self.key(item), item))
    if self.size == len(self.heap):
       self.push = self._replace
    return None

    
  def _replace(self, item):
    return heapq.heappushpop(self.heap, (self.key(item), item))[1]


  def pop(self):
    self.push = self._push
    return heapq.heappop(self.heap)[1]

  def __str__(self): 
    return str([item for item in self.heap])

query_terms = [query.lower() for query in sys.argv[4:]]
folder = sys.argv[1]
mode = sys.argv[2].lower()
filtername = sys.argv[3]
print folder, filtername
foldername = os.path.basename(folder)

if mode not in modes: 
  print_usage()
  sys.exit(1)

print mode
def comparison(src, dst):
  if mode == 'during':
    return src == dst
  elif mode == 'after':
    return src > dst
  elif mode == 'before':
    return src < dst
  elif mode == 'all':
    return True

filterparts = [int(value) for value in filtername.split('.')]
filter_date = date(*filterparts[::-1])

target_filename = '_'.join([foldername] + query_terms + [mode] + [filtername])

with open('models/%s.matched' % target_filename, 'r') as infile:
  target_model = json.load(infile)

try:
  with open('models/background.model', 'r') as infile:
    background_model = json.load(infile)
except IOError, e:
  with open('models/wiki.model', 'r') as infile:
    background_model = json.load(infile)

term_score = {}
for term in target_model['model']:
  try:
    bt = background_model['model'][term] / float(background_model['len'])
  except KeyError, e:
    bt = 1 / float(background_model['len'])
  mt = target_model['model'][term] / float(target_model['len'])
  term_score[term] = max(0, mt * math.log(mt / bt))
  if term.lower() in query_terms: term_score[term] = 0

our_comments, their_comments = 0, 0 
target_comments = []























for root, dirs, files in os.walk(folder):
  for name in files:
    if name.endswith('.swp'): continue
    file_date = [int(value) for value in (name.split('.')[-4:-1])]
    file_date = date(*file_date[::-1])
    if not comparison(file_date, filter_date): continue

    with open(os.path.join(root, name)) as infile:
      data = json.load(infile)
     
    for doc in data['docs']:
      article = doc['article'].lower()
      selector = sum([query in article for query in query_terms]) == \
            len(query_terms)
      url = doc['url'] 
      for comment, pos in izip(doc['comments'], count()):
        text = comment['text']
        text = spaceFinder.sub(insert_spaces, text)
        text = text.replace('\n', ' ')
        if selector:
          our_comments += 1
          comment = Comment(url, pos, [sentence for sentence in nltk.sent_tokenize(text)])
          target_comments += [comment]
        else:
          their_comments += 1


def get_terms(sentence):
  #return [stemmer.stem(word) for word in nltk.word_tokenize(sentence)]
  #return [word.strip() for word in nltk.word_tokenize(sentence)]
  return [stemmer.stem(word.lower())
         # for sentence in nltk.sent_tokenize(text.replace('\n', '.')) 
          for word in nltk.word_tokenize(sentence)]


for comment in target_comments:
  for sentence in comment.sentences:
    terms = get_terms(sentence)
    comment.terms += [set(terms)]
    comment.counts += [len(terms)]

def score(terms, length, delta = 30):
  return sum([term_score[term] for term in terms]) / (length + delta)

class BestCommentEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, BestComment):
      return {'prefix' : ' '.join(obj.comment.sentences[:obj.start]).strip(),
              'suffix' : ' '.join(obj.comment.sentences[obj.end:]).strip(),
              'interesting' : obj.get_scores(),
              'url' : obj.comment.url,
              'pos' : obj.comment.pos,
              'sentences' : obj.unscored_sentences,
              }

    return json.JSONEncoder.default(self, obj)

class BestComment(object):
  def __init__(self, comment, start, end, score):
    self.comment = comment
    self.start = start
    self.end = end
    self.score = score
    seen = set()
    sentences = []
    unscored_sentences = []
    for idx in xrange(start, end):
      sentence = self.comment.sentences[idx]
      for word in nltk.word_tokenize(sentence):
        term = stemmer.stem(word.lower())
        if term not in seen:
          sentences += [[word, term_score[term]]]
          seen.update([term])
        else:
          sentences += [[word, 0]]
        unscored_sentences += [word]
    self.unscored_sentences = ' '.join(unscored_sentences)
    self.sentences = sentences

  def interesting(self):
    return self.start, self.end

  def get_scores(self):
    return self.sentences

all_candidates = []
for iteration in xrange(10): 
  all_candidates += [{}]
  all_candidates[iteration]['terms'] = \
    heapq.nlargest(15, term_score.iteritems(), lambda key: key[1])
  best_sentences = []
  candidates = Heap(key = lambda comment: comment.score)
  for comment in target_comments:
    best_indices = None
    high_score = 0
    current_length = 0
    current_terms = Counter()
    start_idx = 0
    for current_idx in xrange(len(comment.sentences)):
      current_terms.update(comment.terms[current_idx])
      current_length += comment.counts[current_idx]
      if current_idx - start_idx < 2: continue
      unique_elements = [term for term, count in current_terms.most_common() if count > 0]
      current_score = score(unique_elements, current_length)
      if current_score > high_score:
        high_score = current_score
        best_indices = (start_idx, current_idx + 1)

      while current_length > 50:
        current_length -= comment.counts[start_idx]
        current_terms.subtract(comment.terms[start_idx])
        start_idx += 1

    if best_indices:
      candidates.push(BestComment(comment, best_indices[0], best_indices[1], high_score))
  
  candidates = [candidates.pop() for i in xrange(5)] 
  candidates.reverse()
  all_candidates[iteration]['candidates'] = candidates
  best_comment = candidates[0]
  start, end = best_comment.interesting()
  best_sentences = best_comment.comment.sentences[start:end]

  highest = max(0, *[math.log(term_score[term]) for sentence in best_sentences for term in get_terms(sentence) if term_score[term] > 0])
  lowest = min(1, *[math.log(term_score[term]) for sentence in best_sentences for term in get_terms(sentence) if term_score[term] > 0])

  for sentence in best_sentences:
    for term in get_terms(sentence):
      i += 1
      term_score[term] = 0

with open('Summaries/%s_%s_%s.json' % ('.'.join(query_terms), mode, filtername), 'w') as fp:
  json.dump(all_candidates, fp, cls=BestCommentEncoder, indent=4)
