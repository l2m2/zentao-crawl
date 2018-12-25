'''
@File: zentao_sprint_build_spider.py
@Author: leon.li(l2m2lq@gmail.com)
@Date: 2018-12-25 22:27:18
'''

import scrapy
from scrapy.http import Request, FormRequest
import os
import sys
from configparser import ConfigParser

def as_dict(config):
  """
  Converts a ConfigParser object into a dictionary.

  The resulting dictionary has sections as keys which point to a dict of the
  sections options as key => value pairs.
  """
  the_dict = {}
  for section in config.sections():
    the_dict[section] = {}
    for key, val in config.items(section):
      the_dict[section][key] = val
  return the_dict

class ZentaoSprintBuildSpider(scrapy.Spider):
  name = 'zentao_sprint_build'

  if not os.path.exists('zentao.ini'):
    print('File zentao.ini not found.')
    sys.exit(1)
  parser = ConfigParser()
  parser.read('zentao.ini', 'utf-8')
  zentao_config_dict = as_dict(parser)
  headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "139.196.104.13:9999",
    "Origin": "http://139.196.104.13:9999",
    "Referer": zentao_config_dict['zentao']['login_url'],
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
  }

  def start_requests(self):
    return [Request(url=self.zentao_config_dict['zentao']['login_url'], callback=self.login, meta={'cookiejar': 1})]

  def login(self, response):
    print('login zentao.')
    return [FormRequest.from_response(
      response, 
      headers=self.headers, 
      formdata={
        'account': self.zentao_config_dict['zentao']['username'],
        'password': self.zentao_config_dict['zentao']['password'],
        'referer': '/zentao/'
      },
      callback=self.after_login,
      dont_filter=True
    )]

  def after_login(self, response):
    yield Request(self.zentao_config_dict['zentao']['project_build_page'], callback=self.parse)

  def parse(self, response):
    page = response.url.split("/")[-1]
    filename = page
    with open(filename, 'wb') as f:
      f.write(response.body)
    self.log('Saved file %s' % filename)
