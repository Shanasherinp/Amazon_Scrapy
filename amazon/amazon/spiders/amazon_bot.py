import re
import scrapy
from ..items import AmazonItem
from scrapy import Request


class AmazonBotSpider(scrapy.Spider):
    name = 'amazon_bot'
    count = 1
    # allowed_domains = ['amazon.in']
    headers = {
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding" : "gzip, deflate, br",
        "Accept-Language" : "en-GB,en-US;q=0.9,en;q=0.8",
        "Upgrade-Insecure-Requests" : "1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    # start_urls = [
    #     'https://www.amazon.in/s?k=headphones&page=1&qid=1693668066&ref=sr_pg_3'
    #     ]

    def start_requests(self):
        start_url = "https://www.amazon.in/s?k=headphones"
        yield scrapy.Request(start_url, headers=self.headers, callback=self.product_list_page, dont_filter=True)


    def product_list_page(self, response):
        meta = response.meta
        product_links = response.css(".a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal").css("::attr(href)").extract()
        for link in product_links:
            link = "https://www.amazon.in"+link
            
            product_link = re.match(r'(https://www\.amazon\.in/).*?(/dp/[A-Za-z0-9]+)', link)
            if product_link:
                amazon_base_url = product_link.group(1)
                product_id = product_link.group(2)
            else:
                amazon_base_url = ""
                product_id = ""

            meta['amazon_base_url'] = amazon_base_url
            meta['product_id'] = product_id

            yield Request(link, headers = self.headers, callback=self.product_page, dont_filter=True, meta = meta)

        next_page = response.css(".s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator").css("::attr(href)").extract_first("")
        if next_page:
            next_page_link = "https://www.amazon.in"+next_page
            AmazonBotSpider.count+=1
            if AmazonBotSpider.count < 20:
                yield Request(next_page_link, headers = self.headers, callback=self.product_list_page, dont_filter=True, meta= meta)

    def product_page(self, response):
        meta = response.meta
        product=AmazonItem()
        name = response.xpath('//*[@id="productTitle"]/text()').extract_first().strip()
        num_reviews = response.xpath('//*[@id="acrPopover"]/span[1]/a/span/text()').extract_first()
        price = "₹" + response.xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[2]/span[2]/text()').extract_first()
        clnd_price = re.sub(r',', '', price) 
        image_url = response.xpath('//*[@id="imgTagWrapperId"]//img[@src]/@src').extract_first()
        mrp = response.xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[2]/span/span[1]/span/span/span[1]/text()').extract_first()
        clnd_mrp = re.sub(r',', '', mrp)
        offer = response.xpath('//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[1]/text()').extract_first()
        clnd_ofr = re.sub(r'^-', '', offer)
        #date = response.css(".a-color-base.a-text-bold").css("::text").extract()
        delivery = response.xpath('//*[@id="FREE_DELIVERY"]/div[2]/span/text()').extract_first()
        product["p_name"] = name
        product["p_reviews"] = num_reviews
        product["p_price"] = clnd_price
        product["p_image"] = image_url
        product["p_mrp"] = clnd_mrp
        product["p_offer"] = clnd_ofr
        #product["p_date"] = date
        product["p_delivery"] = delivery
        product["product_link"] = meta['amazon_base_url'] + meta['product_id']

        yield product

