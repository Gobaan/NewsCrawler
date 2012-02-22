import pycurl
from time import time 

def process_wrapper (url, outputs):
  outputs[url] = []
  def store(buf):
    outputs[url] += [buf]
  return store


def parallel_fetch(urls):
  """ 
  Given a set of URLs fetches all of them in parallel and returns
  all the responses at once. We cannot process them in parallel
  because the data is returned as a partial buffer
  """
  m = pycurl.CurlMulti()
  urls = set(urls)
  handles = []
  responses = {}
  for link in urls:
    c = pycurl.Curl()
    c.setopt(pycurl.URL, link.encode('utf-8'))
    c.setopt(pycurl.MAXREDIRS, 50)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.CONNECTTIMEOUT, 60)
    c.setopt(pycurl.TIMEOUT, 600)
    c.setopt(pycurl.NOSIGNAL, 1)
    #c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.WRITEFUNCTION, process_wrapper(link, responses))
    c.link = link
    handles += [c]
    m.add_handle(c)

  num_processed = 0
  start = time()
  #This busy loops? with some blocking TODO: Find out if there is a better way 
  while num_processed < len(urls):
    while 1:
      ret, num_handles = m.perform()
      if not ret == pycurl.E_CALL_MULTI_PERFORM: break

    num_q = 1
    while num_q:
      num_q, ok_list, err_list = m.info_read()
      for c in ok_list:
        m.remove_handle(c)
        c.close()
        handles.remove(c)

      for c, errno, errmsg in err_list:
        responses[c.link] = ['Failed', str(c.link), str(errno), str(errmsg)]
        m.remove_handle(c)
        c.close()
        handles.remove(c)
      num_processed += len(ok_list) + len(err_list)

    m.select(60)
    if time() - start > 60:
      print 'Timeout: processing domain ', list(urls)[0]
      break

  for url in responses:
    responses[url] = ''.join(responses[url])
  return responses
