import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import logging
from property02.items import Property02Item
from scrapy.loader import ItemLoader

class SuumoKa02Spider(CrawlSpider):
    name = 'suumo_KA02'
    allowed_domains = ['suumo.jp']
    start_urls = ['https://suumo.jp/jj/bukken/ichiran/JJ010FJ001/?ar=030&bs=011&ra=030013&jspIdFlg=patternEnsen&ohf=0&rn=0760&kb=1&kt=9999999&mb=0&mt=9999999&ekTjCd=&ekTjNm=&tj=0&cnb=0&cn=9999999&srch_navi=1']

    rules = (
        Rule(LinkExtractor(restrict_xpaths = '//h2[@class="property_unit-title"]/a'), follow=True),
        Rule(LinkExtractor(restrict_xpaths = '//a[contains(text(),"物件概要")]'),
        callback='parse_item', follow=False),
        # Rule(LinkExtractor(restrict_xpaths = '//a[contains(text(),"周辺環境・地図")]'),
        # callback='parse_item2', follow=False),
        Rule(LinkExtractor(restrict_xpaths = '(//a[contains(text(),"次へ")])[1]'), follow=True),
    )

    def get_TX(self,text):
        tx = ""
        station = "秋葉原","新御徒町","浅草","南千住","北千住","青井","六町","八潮"
        for item in text:
            if any(map(item.__contains__, (station))):
                tx = item
        return tx
    


    def parse_item(self, response):
        logging.info(response.url)

        loader = ItemLoader(item = Property02Item(), response = response)
        loader.add_xpath('name' , '//div[@class="mt20"][1]//h3/text()')
        loader.add_xpath('price' , '//td[p[a[contains(text(),"支払")]]]/text()')
        loader.add_xpath('price_kanri' , '//th[div[contains(text(),"管理費")]]//following-sibling::td/text()')
        loader.add_xpath('price_tsumitate' , '//th[div[contains(text(),"修繕積立金")]]//following-sibling::td[1]/text()')
        loader.add_xpath('layout' , '//th[div[contains(text(),"間取り")]]//following-sibling::td[1]/text()')
        loader.add_xpath('area' , '//th[div[contains(text(),"専有面積")]]//following-sibling::td[1]/text()[1]')
        loader.add_xpath('age' , '//th[div[contains(text(),"完成時期")]]//following-sibling::td[1]/text()[1]')
        loader.add_xpath('floor' , '//th[div[contains(text(),"所在階")]]//following-sibling::td[1]/text()[1]')
        loader.add_xpath('direction' , '//th[div[contains(text(),"向き")]]//following-sibling::td[1]/text()[1]')
        loader.add_xpath('reform' , '//th[div[contains(text(),"リフォーム")]]//following-sibling::td[1]/text()[1]')
        loader.add_xpath('address' , '//th[div[contains(text(),"所在地")]]//following-sibling::td[1]/text()[1]')
        loader.add_xpath('traffic' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[1]')   
        tx = self.get_TX(response.xpath('//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()').getall())
        loader.add_value('traffic_tx' , tx)

        
        # loader.add_xpath('traffic1_line' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[1]')
        # loader.add_xpath('traffic1_station' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[1]')
        # loader.add_xpath('traffic1_method' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[1]')
        # loader.add_xpath('traffic1_time' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[1]')
        # loader.add_xpath('traffic2_line' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[3]')
        # loader.add_xpath('traffic2_station' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[3]')
        # loader.add_xpath('traffic2_method' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[3]')
        # loader.add_xpath('traffic2_time' , '//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()[3]')

        loader.add_xpath('url' , '//a[contains(text(),"物件の特徴")]/@href')
        return loader.load_item()

    def parse_item2(self, response):
        logging.info(response.url)
        loader = ItemLoader(item = Property02Item(), response = response)
        loader.add_xpath('environment' , '//div[@class="w920 ofh"]//div[@class="mt10"]/text()')
        return loader.load_item()


    
    # def get_price(self,price):
    #     if price:
    #         return int(price.replace("\r\n\t\t\t","").replace("万円","0000"))
    #     return 0

    # def parse_item(self, response):
    #     logging.info(response.url)
    #     yield{
        #     'name' : response.xpath('//h3[@class="secTitleInnerR"]/text()').get(),
        #     'price' : self.get_price(response.xpath('//td[p[a[contains(text(),"支払")]]]/text()').get()),
        #     'price_kanri' : response.xpath('//th[div[contains(text(),"管理費")]]//following-sibling::td/text()').get(),
        #     'price_tsumitate' : response.xpath('//th[div[contains(text(),"修繕積立金")]]//following-sibling::td[1]/text()').get(),
        #     'layout' : response.xpath('//th[div[contains(text(),"間取り")]]//following-sibling::td[1]/text()').get(),
        #     'area' : response.xpath('//th[div[contains(text(),"専有面積")]]//following-sibling::td[1]/text()[1]').get(),
        #     'age' : response.xpath('//th[div[contains(text(),"完成時期")]]//following-sibling::td[1]/text()[1]').get(),
        #     'floor' : response.xpath('//th[div[contains(text(),"所在階")]]//following-sibling::td[1]/text()[1]').get(),
        #     'direction' : response.xpath('//th[div[contains(text(),"向き")]]//following-sibling::td[1]/text()[1]').get(),
        #     'reform' : response.xpath('//th[div[contains(text(),"リフォーム")]]//following-sibling::td[1]/text()[1]').get(),
        #     'address' : response.xpath('//th[div[contains(text(),"所在地")]]//following-sibling::td[1]/text()[1]').get(),
        #     'traffic' : response.xpath('//th[div[contains(text(),"交通")]]//following-sibling::td[1]/text()').getall(),
        # }


