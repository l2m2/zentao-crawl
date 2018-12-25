'''
@File: __init__.py
@Author: leon.li(l2m2lq@gmail.com)
@Date: 2018-12-25 03:44:45
'''

import scrapy

class ZentaoSpider(scrapy.Spider):
  name = 'zentao'
  def start_requests(self):
    urls = [
      'http://quotes.toscrape.com/page/1/'
    ]
    for url in urls:
      yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):
    page = response.url.split("/")[-2]
    filename = 'quotes-%s.html' % page
    with open(filename, 'wb') as f:
      f.write(response.body)
    self.log('Saved file %s' % filename)
