import scrapy
from urllib.parse import urljoin
import time

class SeekSpider(scrapy.Spider):
    name= "seek"
    allowed_domains = ["seek.com.au"]

    def start_requests(self):
        # list of star urls
        urls = ['https://www.seek.com.au/data-jobs?salaryrange=0-40000&salarytype=annual'
        ,'https://www.seek.com.au/data-jobs?salaryrange=50000-70000&salarytype=annual'
        , 'https://www.seek.com.au/data-jobs?salaryrange=80000-120000&salarytype=annual'
        , 'https://www.seek.com.au/data-jobs?salaryrange=150000-200000&salarytype=annual'
        , 'https://www.seek.com.au/data-jobs?salaryrange=200000-999999&salarytype=annual'
        ,]
        #to pass the index of each url as it will be used to determine the salary range
        for index, url in enumerate(urls):
            yield scrapy.Request(url, callback=self.parse, cb_kwargs={'index':index})

    def parse(self, response, index):
        #determine salary range by the start url we are in
        if index==0:
            sal_range= 'low'
        elif index==1:
            sal_range='mid_low'
        elif index==2:
            sal_range= 'mid'
        elif index==3:
            sal_range='mid_high'
        else:
            sal_range='high'

        urls = response.xpath('//a[@data-automation="jobTitle"]/@href').extract()
        jobID= response.xpath('//article/@data-job-id').extract()

        for id_index, href in enumerate(urls):
            j_ID=jobID[id_index]
            url=response.urljoin(href)
            yield scrapy.Request(url = url, callback =self.parse_details, cb_kwargs={'url':url, 'j_ID': j_ID, 'sal_range':sal_range} )

        time.sleep(3)

        next_page = response.xpath('//a[@data-automation="page-next"]//@href').extract_first()

        if next_page is not None:
            print('*************TRY**************************')
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback = self.parse,cb_kwargs={'index':index} )

#get job details witin the individual job urls
    def parse_details(self, response, url, j_ID, sal_range):
        #get job details based on xpath
        yield {
            'jobID':j_ID,
            'jobLink':url,
            'jobTitle': response.xpath('//h1[@data-automation="job-detail-title"]//text()').get(),
            'jobCompany': response.xpath('//span[@data-automation="advertiser-name"]//text()').get(),
            'jobLocation': response.xpath('//span[@class="FYwKg _2Bz3E C6ZIU_4 _6ufcS_4 _2DNlq_4 _29m7__4 _2WTa0_4"]//div[@class="FYwKg PrHFr _1EtT-_4"]//text()').get(),
            'jobArea': response.xpath('//div[@class="FYwKg _3VxpE_4"]//div[@class="FYwKg PrHFr _1EtT-_4"]//text()').getall(),
            'Industry': response.xpath('//div[@class="FYwKg _3VxpE_4"]//div[@class="FYwKg PrHFr _1EtT-_4"]//text()').getall()[-2],
            'Industry_details': response.xpath('//div[@class="FYwKg _3VxpE_4"]//div[@class="FYwKg PrHFr _1EtT-_4"]//text()').getall()[-1],
            'jobAdDetails': response.xpath('//div[@data-automation="jobAdDetails"]//text()').getall(),
            'Worktype': response.xpath('//div[@data-automation="job-detail-work-type"]//div[@class="FYwKg PrHFr _1EtT-_4"]//text()').getall(),
            'Worktype2': response.xpath('//div[@data-automation="job-detail-work-type"]//div[@class="FYwKg PrHFr _1EtT-_4"]//text()').getall()[-1],
            # 'SeekExpectedSalary':response.xpath('//span[@class="lmis-cg-salary-mode"]//text()').get(),
            'Salary': response.xpath('//div[@data-automation="job-detail-work-type"]//div[@class="FYwKg PrHFr _1EtT-_4"]//text()').get(),
            'Salary_range': sal_range,
            }
