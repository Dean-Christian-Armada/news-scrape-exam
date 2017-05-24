from datetime import timedelta
from celery import Celery
from celery.decorators import periodic_task
from scrapy.crawler import CrawlerProcess
from spiders.news import NewsSpider


app = Celery(broker='amqp://guest:guest@localhost:5672/')

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})


@periodic_task(run_every=timedelta(minuites=10))
def task_scrape_news():
    process.crawl(NewsSpider)
    process.start()
    return
