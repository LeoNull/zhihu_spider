# -*- coding=utf8 -*-
from scrapy.spiders.crawl import CrawlSpider
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from zhihu.constants import Gender
from zhihu.items import ZhihuPeopleItem

from scrapy import log
import os
class Zhihulogin(CrawlSpider):
    name="login"
    allowed_domains=["www.zhihu.com"]
    start_url="https://www.zhihu.com/people/leo-63-45"
    
    def __init__(self,*arg,**kwargs):
        super(Zhihulogin,self).__init__(*arg,**kwargs)
        self.xsrf=''
        
        
    def start_requests(self):
        return[Request(
                       "https://www.zhihu.com/#signin",
                       meta={'cookiejar': 1},
                       callback=self.post_login)]
        
    def post_login(self,response):
        self.xsrf=Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        print self.xsrf
        return [FormRequest(
                            'https://www.zhihu.com/login/email',
                            method='POST',
                            meta={'cookiejar': response.meta['cookiejar']},
                            formdata={
                                      '_xsrf': self.xsrf,
                                      'email': '820073786@qq.com',
                                      'password': '19920611cl',
                                      'remember_me': 'true'},
        callback=self.after_login
        )]
    
    def after_login(self,response):
        return [Request(
            self.start_url,
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.parse_people,
            errback=self.parse_err,
        )]
    
    
    def parse_people(self,response):
        """
        解析用户主页
        """
        selector = Selector(response)
        nickname=selector.xpath(
            '//div[@class="title-section"]/span[@class="name"]/text()'
        ).extract_first()
        zhihu_id=os.path.split(response.url)[-1]
        location=selector.xpath(
            '//span[@class="location item"]/@title'
        ).extract_first()
        business=selector.xpath(
            '//span[@class="business item"]/@title'
        ).extract_first()
        gender = selector.xpath(
            '//span[@class="item gender"]/i/@class'
        ).extract_first()
        if gender is not None:
            gender = Gender.FEMALE if u'female' in gender else Gender.MALE
        employment =selector.xpath(
            '//span[@class="employment item"]/@title'
        ).extract_first()
        position = selector.xpath(
            '//span[@class="position item"]/@title'
        ).extract_first()
        education = selector.xpath(
            '//span[@class="education item"]/@title'
        ).extract_first()
        

        item = ZhihuPeopleItem(
            nickname=nickname,
            zhihu_id=zhihu_id,
            location=location,
            business=business,
            gender=gender,
            employment=employment,
            position=position,
            education=education,
            
        )
        yield item
    def parse_err(self, response):
        log.ERROR('crawl {} failed'.format(response.url))