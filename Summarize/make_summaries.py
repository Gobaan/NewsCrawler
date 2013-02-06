import os, os.path
import sys
import subprocess

if not os.path.isdir('models'):
  os.mkdir('models')

if not os.path.isdir('Summaries'):
  os.mkdir('Summaries')


if len(sys.argv) is not 4:
  if len(sys.argv) == 5 and sys.argv[4] == 'make_background': 
    loc = sys.argv[1]
    subprocess.call(['python', 'jsonmodelmaker.py', loc, 'after', '01.01.1900', ""])
  else:
    print 'usage python make_summaries target_dir mode target_date [make_background]'

filtername = sys.argv[3]
loc = sys.argv[1]
mode = sys.argv[2]

for dirname in os.listdir(sys.argv[1]):
  query = dirname.split('+')
  loc = os.path.join(sys.argv[1], dirname)
  print loc, filtername, query
  subprocess.call(['python', 'jsonmodelmaker.py', loc, mode, filtername] + query)
  subprocess.call(['python', 'trigram_summarizer.py', loc, mode, filtername] + query)
