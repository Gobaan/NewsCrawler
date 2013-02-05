import os, os.path
import sys
import subprocess

if not os.path.isdir('models'):
  os.mkdir('models')

if not os.path.isdir('Summaries'):
  os.mkdir('Summaries')


if len(sys.argv) is not 3:
  if len(sys.argv) == 4 and sys.argv[3] == 'make_background': 
    loc = sys.argv[1]
    subprocess.call(['python', 'jsonmodelmaker.py', loc, '>01.01.1900', ""])
  else:
    print 'usage python make_summaries target_dir target_date [make_background]'

filtername = sys.argv[2]
loc = sys.argv[1]


for dirname in os.listdir(sys.argv[1]):
  query = dirname.split('+')
  loc = os.path.join(sys.argv[1], dirname)
  print loc, filtername, query
  subprocess.call(['python', 'jsonmodelmaker.py', loc, filtername] + query)
  subprocess.call(['python', 'trigram_summarizer.py', loc, filtername] + query)
