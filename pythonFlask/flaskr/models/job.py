from bs4 import BeautifulSoup
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from io import BytesIO
from flask import make_response

import urllib
import requests
import logging
import os
import constants
import settings

logger = logging.getLogger(__name__)


class Job:
    def __init__(self, tag):
        self.tag = tag

    @classmethod
    def get_job_offers(cls, tag):
        url = f'https://www.randstadusa.com/jobs/search/q-{tag}/'
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            # elms = soup.find_all("a")
            # for elm in elms:
            #     print(elm)
            elements = soup.select('#search-result-body > div:nth-child(2)')
            job_detail_elements = None
            if elements:
                for element in elements:
                    # ex. /jobs/search/4/818486/python-developer-professional_mclean/
                    job_detail_urls = f'https://www.randstadusa.com{element.ul.h3.a["href"]}'
                job_detail_responses = requests.get(job_detail_urls)
                job_detail_soups = BeautifulSoup(job_detail_responses.text, "html.parser")
                job_detail_elements = job_detail_soups.select('#jobdescription > div > div > div.col-sm-8.col-sm-offset-4 > div')
        except requests.exceptions.RequestException as e:
            logger.log(f'action=scraping error={e}')

        return job_detail_elements

    @classmethod
    def get_skill_count(cls, text):
        # count_dict = {}
        # for skill in constants.SKILLS:
        #     count_dict[skill] = str(text).count(skill)

        count_dict = {
            'python': str(text).count('Python'),
            'golang': str(text).count('Golang'),
            'react': str(text).count('React'),
            'restapi': str(text).count('REST'),
            'aws': str(text).count('AWS'),
            'docker': str(text).count('Docker'),
            'kubernetes': str(text).count('Kubernetes'),
            'hadoop': str(text).count('Hadoop'),
            'spark': str(text).count('Spark'),
            'dataflow': str(text).count('Dataflow'),
            'cassandra': str(text).count('Cassandra'),
            'dynamoDB': str(text).count('DynamoDB'),
            'elasticsearch': str(text).count('ElasticSearch'),
            'bigquery': str(text).count('BigQuery'),
            'tableau': str(text).count('Tableau'),
            'hyperdatabase': str(text).count('Hyper database'),
            'serverextracts': str(text).count('Server extracts'),
            'prepflows': str(text).count('Prep flows')
        }

        return count_dict

    @classmethod
    def output_html(cls, skill_count):
        cls.skill_count = str(skill_count)
        file = open('./flaskr/static/output/scraping.txt', 'w+')
        file.write(cls.skill_count)
        file.seek(0)
        file.read()
        file.close()

    @classmethod
    def get_graph(cls, count_dict):
        # figure = plt.figure()
        # figure.add_subplot()
        #
        # x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # for count in count_dict:
        #     y = list()
        #     y.append(count)
        # plt.cla()
        # plt.title('Skill count')
        # plt.bar(x, y)
        # plt.legend()
        #
        # canvas = FigureCanvasAgg(figure)
        # png_output = BytesIO()
        # canvas.print_png(png_output)
        # data = png_output.getvalue()
        #
        # response = make_response(data)
        # response.headers['Content-Type'] = 'image/png'
        # response.headers['Content-Length'] = len(data)

        key = list()
        value = list()
        for k, v in count_dict:
            key.append(k)
            value.append(v)
        return key, value
