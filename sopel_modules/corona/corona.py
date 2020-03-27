from sopel.config.types import StaticSection, ChoiceAttribute, ValidatedAttribute
from sopel.module import commands, example
from sopel import web
import sopel.module

import requests
import csv
import time
from functools import reduce

def cache(fun):
  data = {"data": 0, "timestamp": 0}
  def new_fun():
      if time.time() - data['timestamp'] > 300:
          data['data'] = fun()
          data['timestamp'] = time.time()
      return data['data']
  return new_fun

@cache
def get_data():
  data = requests.get(
      "http://coronavirusapi.com/states.csv"
  )
  csv_data = data.text[data.text.index('\n')+1:]
  def convert(x):
      if not x:
          return 0
      return int(x)
  parsed = dict([(x[0], {"tested": convert(x[1]), "positive": convert(x[2]), "deaths": convert(x[3])}) for x in csv.reader(csv_data.split())])
  return parsed


@sopel.module.commands('corona')
@sopel.module.example('.corona NY')
@sopel.module.example('.corona')
def corona(bot, trigger):
    where = trigger.group(2)
    data = get_data()
    null = {"tested": 0, "positive": 0, "deaths": 0}
    if where.lower() == "total":
        def calc(v, d):
            v['tested'] += d['tested']
            v['positive'] += d['positive']
            v['deaths'] += d['deaths']
            return v
        data = reduce(calc, data.values(), null)
    elif where[0:3].lower() == "top":
        key = where[4:].lower()
        data = reduce(lambda v, d: v if  v[1][key] > d[1][key] else d, data.items(), (False, null))
        where = data[0]
        data = data[1]
    else:
      data = data[where.upper()]
    msg = f"{where} Tested: {data['tested']} Positive: {data['positive']} Deaths: {data['deaths']}"
    bot.say(msg)
