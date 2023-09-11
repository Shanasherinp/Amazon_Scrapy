# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    p_name = scrapy.Field()
    p_reviews = scrapy.Field()
    p_price = scrapy.Field()
    p_image = scrapy.Field()
    p_mrp = scrapy.Field()
    p_offer = scrapy.Field()
    #p_date = scrapy.Field()
    p_delivery = scrapy.Field()
    product_link = scrapy.Field()

    
