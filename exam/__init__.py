import os
from datetime import timedelta
from celery import Celery
from celery.decorators import periodic_task
from scrapy.crawler import CrawlerProcess
from spiders.news import NewsSpider

if os.environ.get('ENV') == 'cloud':
    broker = 'amqp://guest:guest@rabbitmq:5672//'
else:
    broker = 'amqp://guest:guest@localhost:5672/'

app = Celery(broker=broker)

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})


@periodic_task(run_every=timedelta(minutes=10))
def task_scrape_news():
    process.crawl(NewsSpider)
    process.start()
    return
