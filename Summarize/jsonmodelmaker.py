import os, sys, re, os.path
from collections import Counter
import json
import nltk
import BeautifulSoup
from preprocessing import preprocess_string
from nltk.stem.porter import PorterStemmer
from datetime import date

modes = ['before', 'after', 'during', 'all']

def print_usage():
  print "usage: jsonmodelmaker.py <folder> <mode> <date> [query terms]"
  print "modes: %s" % ','.join(modes)

spaceFinder = re.compile('([^A-Z])([.!?,])([A-Z])')
def insert_spaces(matchobj):
   return matchobj.group(0) + matchobj.group(1) + ' ' + matchobj.group(2)

stemmer = PorterStemmer()
def get_terms(text):
  #return [stemmer.stem(word) for word in nltk.word_tokenize(sentence)]
  text = spaceFinder.sub(insert_spaces, text)
  return [stemmer.stem(word.lower())
          for sentence in nltk.sent_tokenize(text.replace('\n', ' ')) 
          for word in nltk.word_tokenize(sentence)]

folder = sys.argv[1]
mode = sys.argv[2].lower()
filtername = sys.argv[3]
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

foldername = os.path.basename(folder)
query_terms = [query.lower() for query in sys.argv[4:]]

  
#Share seen_urls files for a given query
filename = '_'.join([foldername] + query_terms + [mode] + [filtername])
model1 = Counter()
model2 = Counter()

seen_urls = {}
num_duplicates = 0
our_comments, their_comments = 0, 0 
filtername = [int(value) for value in filtername.split('.')]
filter_date = date(*filtername[::-1])


# Train a model using all the documents in the folder
for root, dirs, files in os.walk(folder):
  print root
  for name in files:
    if name.endswith('.swp'): continue
    file_date = [int(value) for value in (name.split('.')[-4:-1])]
    file_date = date(*file_date[::-1])
    if not comparison(file_date, filter_date): continue
    with open(os.path.join(root, name)) as infile:
      try:
        data = json.load(infile)
      except ValueError, e:
        print 'Missing Json ', name
        continue
     
    for doc in data['docs']:
      uid = '%s:%s' % (hash(name), hash(doc['url']))
      if uid in seen_urls: 
        num_duplicates += 1
        continue
      seen_urls[uid] = 0
      article = doc['article'].lower()
      selector = sum([query in article for query in query_terms]) == \
            len(query_terms)
      for comment in doc['comments']:
        text = comment['text']
        if selector:
          model1.update(set(get_terms(text)))
          
          our_comments += 1
        else:
          model2.update(set(get_terms(text)))
          their_comments += 1

print 'Number of duplicates:', num_duplicates
print our_comments, their_comments

matched_name = 'models/%s.matched' % filename
print query_terms
if not query_terms or not query_terms[0]:
  matched_name = 'models/background.model'

with open(matched_name, 'w') as output:
  json.dump({'model': model1, 'len': our_comments}, output)

with open('models/%s.unmatched' % filename, 'w') as output:
  json.dump({'model': model2, 'len': their_comments}, output)
