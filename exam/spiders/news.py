# -*- coding: utf-8 -*-
import scrapy
import os
import pymongo
from ConfigParser import SafeConfigParser


class NewsSpider(scrapy.Spider):
    name = 'news'
    config_parser = SafeConfigParser()
    config_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.abspath(os.path.join(config_dir,
                                               '..',
                                               '..',
                                               'scrapy.cfg')
                                  )
    config_parser.read(config_file)
    mongodb_url = config_parser.get('settings', 'mongodb_url')
    ssl_file = os.path.join(config_dir, 'ssl.crt')

    def _insert_bbc(self, response):
        """
        @brief      get the scraped data of bbc news, then inserting those
                    data as the collection's document
        """

        media = response.css('div.media')
        for x in range(0, len(media)):
            _media = media[x]
            image = _media.\
                css('div.media__image div.responsive-image img::attr(src)')\
                .extract_first()
            title = _media.css('a.media__link::text').extract_first()
            url = _media.css('a.media__link::attr(href)').extract_first()
            summary = _media.css('p.media__summary::text').extract_first()
            tags = _media.css('a.media__tag::text').extract_first()

            data = {}
            if title:
                data['title'] = title.strip()
            if url:
                data['url'] = url
            if summary:
                data['summary'] = summary.strip()
            if tags:
                data['tags'] = tags
            if image:
                data['image'] = image
            self.collection.insert_one(data).inserted_id
        return

    def _insert_theguardian(self, response):
        """
        @brief      get the scraped data of theguardian news, then inserting
                                those data as the collection's document
        """

        fc_item = response.css('div.fc-item__content')
        for x in range(0, len(fc_item)):
            _fc_item = fc_item[x]
            text = _fc_item.css('span.js-headline-text::text').extract_first()
            url = _fc_item.css('a.fc-item__link::attr(href)').extract_first()
            tags = _fc_item.css('span.fc-item__kicker::text').extract_first()

            data = {}
            if text:
                data['text'] = text.strip()
            if url:
                data['url'] = url
            if tags:
                data['tags'] = tags
            self.collection.insert_one(data).inserted_id
        return

    def start_requests(self):
        urls = [
            'https://www.theguardian.com/au',
            'http://www.bbc.com/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        news = response.url.split('.')[1]
        client = pymongo.MongoClient(self.mongodb_url,
                                     ssl_ca_certs=self.ssl_file)
        db = client.get_default_database()
        self.collection = db.exam
        getattr(self, '_insert_' + news)(response)
        return