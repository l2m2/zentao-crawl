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
import json

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
    yield Request(self.zentao_config_dict['zentao']['project_build_page'], callback=self.parse_sprint_build)

  def parse_sprint_build(self, response):
    page = response.url.split("/")[-1]
    filename = page
    with open(filename, 'wb') as f:
      f.write(response.body)
    self.log('Saved file %s' % filename)

    builds = response.css('#buildList td')
    if builds is None:
      print("Error: response.css('#buildList td').")
      sys.exit(1)
    build_id = builds[0].css('td:nth-child(1)::text').extract_first()
    if build_id is None:
      print("Error: builds[0].css('td:nth-child(1)::text')")
      sys.exit(1)
    lastest_build_url = self.zentao_config_dict['zentao']['sprint_build_url_template'].format(id=build_id)
    yield Request(lastest_build_url, self.parse_latest_build)

  def parse_latest_build(self, response):
    page = response.url.split("/")[-1]
    filename = page
    with open(filename, 'wb') as f:
      f.write(response.body)
    self.log('Saved file %s' % filename)

    bugs = []
    stories = []
    for tr in response.css('#bugList tr'):
      if tr.css('td:nth-child(3)::text').re_first(r'\s*(.*)') == "已解决":
        bug_id = tr.css('td:nth-child(1)>input::attr(value)').re_first(r'\s*(.*)')
        bug_title = tr.css('td:nth-child(2)>a::text').re_first(r'\s*(.*)')
        bugs.append('{id} {title}'.format(id=bug_id, title=bug_title))
    for tr in response.css('#storyList tr'):
      if tr.css('td:nth-child(7)::text').re_first(r'\s*(.*)') == "研发完毕":
        story_id = tr.css('td:nth-child(1)>input::attr(value)').re_first(r'\s*(.*)')
        story_title = tr.css('td:nth-child(3)>a::text').re_first(r'\s*(.*)')
        stories.append('{id} {title}'.format(id=story_id, title=story_title))
    result_filename = page.split('.')[0] + '.json'
    content = json.dumps({'bugs': bugs, 'stories': stories}, indent=4, sort_keys=True)
    with open(result_filename, 'w') as f:
      f.write(content)
    self.log('Saved file %s' % result_filename)