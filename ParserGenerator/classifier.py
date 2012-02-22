import json
import sys, os, types
import re, urlparse, itertools
from BeautifulSoup import BeautifulSoup
from collections import Counter
# Currently fails when Request headers contain parameters, but this only
# Happened in one case (wsj) and was easily resolvable with debug info
# So ignore it for now. btw TODO

def print_html_parsers(name, parents):
  root = parents[0]
  for child in parents[-2:-4:-1]: 
    print "%s.strainer = SoupStrainer('%s'," % (name, root.name),
    print '%s)' % dict(root.attrs)
    print "%s.tags = '%s'" % (name, child.name)
    print '%s.attrs = %s' % (name, dict(child.attrs))
  print '#####'
  print child
  print '*****'


def find_shortest_unique_start(lines, most_common):
  lines = [line for line in lines if line != most_common]
  for i in xrange(1, len(most_common)):
    if not len([line for line in lines if line.startswith(most_common[:i])]):
      return most_common[:i]
  raise Exception('Failure')

def get_parents(html, comments):
  soup = BeautifulSoup(html)
  first_comment = soup.findAll(text=lambda x: comments[1] in x)
  if len(first_comment) > 1: 
    return None
  
  parent = first_comment[0].parent
  all_parents = [parent]
  second_comment = soup.findAll(text=lambda x: comments[0] in x)[0]
  all_parents += [second_comment.parent]
  while (not parent.findAll(text=lambda x: comments[0] in x)
    or len(soup.findAll(parent.name, dict(parent.attrs))) > 1):
    parent = parent.parent
    all_parents = [parent] + all_parents

  return all_parents

def iterate_json(json_data, value):
  if type(json_data) in types.StringTypes and value in json_data:
    return [json_data]

  if type(json_data) is types.ListType:
    for i, element in zip(itertools.count(), json_data):
      child_json = iterate_json(element, value) 
      if child_json: return [i] + child_json

  if type(json_data) is types.DictType:
    for key in json_data:
      child_json = iterate_json(json_data[key], value) 
      if child_json: return [key] + child_json
  return []

with open('urls.txt') as f:
  process = lambda line: line.strip().split('|')
  url_comments = [(process(line)[0], process(line)[1:]) for line in f]

for (url, comments), i in zip(url_comments, itertools.count()):
  if url.startswith('#'): continue
  parsed_url = urlparse.urlparse(url)
  netloc = parsed_url.netloc
  if not os.path.isfile('results/%s.%s' % (netloc, i)): 
    print 'Continued ' + url, i, netloc
    continue
  with open ('results/%s.%s' % (netloc, i)) as data_file: 
    comment_url = data_file.readline().strip()
    lines = data_file.readlines()
  seen = Counter()
  for s in comments:
    seen.update([line for line in lines if s in line])

  #print '----'
  #print netloc, comments
  name = netloc
  if name.startswith('www.'): name = name[4:]
  name = '_'.join(name.split('.')[:-1])
  name = "%s" % name
  try:
    most_common = seen.most_common(1)[0]
  except IndexError:
    print 'url failed: %s\n' % url
    continue

  if most_common[1] == 3:
    #print len(lines)
    #print 'Filter me:', len(lines) != 1
     
    data = most_common[0]
    json_string = data[data.find('{'):data.rfind('}') + 1]
    try: 
      json_data = json.loads(json_string)
      path1 = iterate_json(json_data, comments[0])
      #print path1
      path2 = iterate_json(json_data, comments[1])
      #print path2
      path3 = []
      for first, second in zip(path1, path2):
        if first == second: path3 += [str(first)]
        else: path3 += ['*']
      # Json Parser
      print "%s = JsonParser()" % name
      print '%s.paths = ["$.%s"]' % (name, '.'.join(path3[:-1]))

    except ValueError:
      html = data
      if data.find('(') < data.find(' '):
        # Async HTML Parser
        html = data[data.find('\'') + 1:data.rfind('\'')]
        print "%s = AsyncHtmlParser()" % name
      else: 
        print "%s = EscapedHtmlParser()" % name

      #StandardHTML Parser
      html = html.decode("string-escape").replace('\/','/')
      parents = get_parents(html, comments)
      print_html_parsers(name, parents)

    if len(lines) != 1:
      print '%s.preprocess =' % name,
      filter_str = find_shortest_unique_start(lines, data)
      print 'pipe(make_startswith("%s"), %s.preprocess)' % (
        filter_str, name)
  else:
    #print 'Filter me: Never'
    html = ''.join(lines)
    html  = ''.join(re.split('<script.*?</script>', html, flags=re.DOTALL))
    if html.find('(') < html.find(' '):
      # Json Parser
      html = html[html.find('{'):html.rfind('}') + 1]
      json_data = json.loads(html)                                
      path1 = iterate_json(json_data, comments[0])
      #print path1
      path2 = iterate_json(json_data, comments[1])
      #print path2
      path3 = []
      for first, second in zip(path1, path2):
        if first == second: path3 += [str(first)]
        else: path3 += ['*']

      print "%s = JsonParser()" % name
      print '%s.paths = ["$.%s"]' % (name, '.'.join(path3[:-1]))
    else:
      # Standard HTML Parser
      parents = get_parents(html, comments)
      if not parents: 
        print 'Error found comment in multiple locations'
      print "%s = HtmlParser()" % name
      print_html_parsers(name, parents)
  if url != comment_url: 
    print "#%s" % url.strip()
    print "%s_template = Template('%s')" % (name, comment_url)
    print 'def %s_rename(self, url, site):' % (name)
    print "  args = {'url' : url}"
    print '  return %s_template.substitute(args)' % name
    print '%s.rename = types.MethodType (%s_rename, %s)' % (name, name, name)
    print ''
    print ''
    print ''
    print '  def test_%s(self):' % name
    print '    url = "%s"' % url
    print '    comment_url = "%s"' % comment_url
    print '    self.assertEqual(%s.rename(url, ""), comment_url)' % name
    print ''
  print ''
