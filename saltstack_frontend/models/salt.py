import subprocess
import json
from functools import lru_cache

@lru_cache(maxsize=2)
def get_jobs():
  out = subprocess.run(['sudo','salt-run','jobs.list_jobs','search_function="state.apply"','--output=json'], 
        stdout=subprocess.PIPE)
  try:
    data = json.loads(out.stdout.decode('utf8'))
  except:
    return {}
  return(data)
