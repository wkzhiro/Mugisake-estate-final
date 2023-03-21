# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join

def strip_space(element):
    if element:
        return element.replace('\r\n\t\t\t','')
    return element

def strip_mansion(element):
    if element:
        return element.replace(' 【マンション】','')
    return element

def strip_m(element):
    if element:
        return element.replace('m','')
    return element

def strip_floor(element):
    if element:
        return element.replace('階','')
    return element

def strip_yen(element):
    if element:
        return element.replace('円','')
    return element

def strip_man(element):
    if element:
        return element.replace('万','')
    return element

def convert_man(element):
    if element:
        return element.replace('万','0000')
    return element

def strip_oku(element):
    if element:
        return element.replace('億','')
    return element

def strip_ho(element):
    if element:
        return element.replace('歩','')
    return element

def strip_fun(element):
    if element:
        return element.replace('分','')
    return element


def convert_integer(element):
    if element:
        return int(element)
    return 0

def convert_float(element):
    if element:
        return float(element)
    return 0

def split_slash(element):
    if element:
        return element.split('／')[0]
    return element

def split_bracket1_f(element):
    if element:
        return element.split('「')[0]
    return element

def split_bracket1_b(element):
    if element:
        return element.split('「')[1]
    return element

def split_bracket2_f(element):
    if element:
        return element.split('」')[0]
    return element

def split_bracket2_b(element):
    if element:
        return element.split('」')[1]
    return element

class Property02Item(scrapy.Item):
    name = scrapy.Field(
        input_processor = MapCompose(strip_space, strip_mansion),
        output_processor = TakeFirst()
    )
    price = scrapy.Field(
        input_processor = MapCompose(strip_space, strip_yen, strip_oku, convert_man, convert_integer),
        output_processor = TakeFirst()
    )
    price_kanri = scrapy.Field(
        input_processor = MapCompose(split_slash, strip_yen, strip_man, convert_integer),
        output_processor = TakeFirst()
    )
    price_tsumitate = scrapy.Field(
        input_processor = MapCompose(split_slash, strip_yen, strip_man, convert_integer),
        output_processor = TakeFirst()
    )
    layout = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    area = scrapy.Field(
        input_processor = MapCompose(strip_m, convert_float),
        output_processor = TakeFirst()
    )
    age = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    floor = scrapy.Field(
        input_processor = MapCompose(strip_space, strip_floor, convert_integer),
        output_processor = TakeFirst()
    )
    direction = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    reform = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    address = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    traffic = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    traffic_tx = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    # traffic1_line = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket1_f),
    #     output_processor = TakeFirst()
    # )
    # traffic1_station = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket1_b, split_bracket2_f),
    #     output_processor = TakeFirst()
    # )
    # traffic1_method = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket2_b),
    #     output_processor = TakeFirst()
    # )
    # traffic1_time = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket2_b),
    #     output_processor = TakeFirst()
    # )
    # traffic2_line = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket1_f),
    #     output_processor = TakeFirst()
    # )
    # traffic2_station = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket1_b, split_bracket2_f),
    #     output_processor = TakeFirst()
    # )
    # traffic2_method = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket2_b),
    #     output_processor = TakeFirst()
    # )
    # traffic2_time = scrapy.Field(
    #     input_processor = MapCompose(strip_space, split_bracket2_b),
    #     output_processor = TakeFirst()
    # )
    url = scrapy.Field(
        input_processor = MapCompose(strip_space),
        output_processor = TakeFirst()
    )
    environment = scrapy.Field(
        input_processor = MapCompose(strip_space),
        # output_processor = TakeFirst()
    )