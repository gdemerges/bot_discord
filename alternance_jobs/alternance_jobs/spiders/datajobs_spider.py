import scrapy

class DataJobsSpider(scrapy.Spider):
    name = 'datajobs'
    start_urls = ['https://www.hellowork.com/fr-fr/emploi/recherche.html?k=Data+engineer&k_autocomplete=http%3A%2F%2Fwww.rj.com%2FCommun%2FPost%2FIngenieur_big_data&l=Lyon+69000&l_autocomplete=Lyon+69000&ray=20&c=Alternance&msa=&cod=all&d=all&c_idesegal=']

    def parse(self, response):
        for job_offer in response.css('ul.crushed li'):
            yield {
                'title': job_offer.css('span.tw-flex::text').get(),
                'link': job_offer.css('a::attr(href)').get(),
            }
