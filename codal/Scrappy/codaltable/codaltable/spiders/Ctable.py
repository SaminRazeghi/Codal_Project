import scrapy
from scrapy_splash import SplashRequest
import re
import csv
import os
import numpy as np
import pandas as pd


class CtableSpider(scrapy.Spider):
    name = 'Ctable'
    allowed_domains = ['codal.ir']
    start_urls = []

    def __init__(self, *args, **kwargs):
        super(CtableSpider, self).__init__(*args, **kwargs)
        url_list = kwargs.get('url_list')
        if url_list:
            self.start_urls = url_list.split(' ')

        # Create "csv" folder in the same directory as the spider if it doesn't exist
        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.csv_folder_path = os.path.join(current_directory, 'csv')
        if not os.path.exists(self.csv_folder_path):
            os.makedirs(self.csv_folder_path)

    def start_requests(self):
        for url in self.start_urls:
            print("SEND REQUEST")
            yield SplashRequest(url=url, callback=self.parse, endpoint='render.html', args={'wait': 5.0})

    non_respond = []

    def parse(self, response):
        # Gets the information from the page
        table = response.css(".rayanDynamicStatement").get()
        CompanyName = response.css(
            '#ctl00_txbCompanyName *::text').get().strip()
        ReportName = response.css('#ctl00_lblReportName::text').get()
        Period = response.css('#ctl00_lblPeriod *::text').get().strip()
        EndTo = response.css('#ctl00_lblEndTo::text').get()
        PeriodEndToDate = response.css(
            '#ctl00_lblPeriodEndToDate bdo::text').get()
        IsAudited = response.css('#ctl00_lblIsAudited::text').get()
        space = ""
        text = f"{CompanyName} {ReportName} {Period} {EndTo}{space}{PeriodEndToDate} {IsAudited}"
        text = re.sub(r'[()\/\s‌]+', '_', text)

        # Checks if it finds the table of not:
        if table is None:
            table = response.css(
                '#ctl00_cphBody_ucInterimStatement_tblGridHeader').get()
            if table is None:
                print("---------------------------------------------------------------------------------------------------------------")
                print(f"Table not found for URL: {response.url}")
                print(f'Response status code: {response.status}')
                print("---------------------------------------------------------------------------------------------------------------")
                self.logger.warning(
                    "Table not found. Skipping URL: %s", response.url)
                self.non_respond.append(response.url)
                return  # Stop crawling this URL and proceed to the next one

        print("---------------------------------------------------------------------------------------------------------------")
        print("FOUND THE TABLE")
        print(text)
        print("---------------------------------------------------------------------------------------------------------------")

        # finds header an body og the table with regex:
        tr_pattern = r'<tr[^>]*>(.*?)<\/tr>'
        trs = re.findall(tr_pattern, table, re.DOTALL)

        # table has a header and a subheader
        header_row_1 = trs[0]
        header_row_2 = trs[1]

        header_1_pattern = r'<th[^>]*>(.*?)<\/th>'
        headers_1 = re.findall(header_1_pattern, header_row_1, re.DOTALL)
        headers_2 = re.findall(header_1_pattern, header_row_2, re.DOTALL)

        clean_headers_1 = [re.sub(r'<.*?>', '', header)
                           for header in headers_1]
        clean_headers_2 = [re.sub(r'<.*?>', '', header)
                           for header in headers_2]
        clean_headers_2.insert(0, '')

        # finds rowa
        row_pattern = r'<tr(?![^>]*_ngcontent-bxi-c4=\"\"><!----><th[^>]*>)(.*?)<\/tr>'
        rows = re.findall(row_pattern, table, re.DOTALL)

        # creates the table
        table_data = [[re.sub(r'<.*?>', '', cell) for cell in re.findall(
            r'<td[^>]*>(.*?)<\/td>', row, re.DOTALL)] for row in rows]

        # Generate the full path and filename for the CSV file
        csv_filename = os.path.join(self.csv_folder_path, f'{text}.csv')

        with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(clean_headers_1)
            writer.writerow(clean_headers_2)
            writer.writerows(table_data)

        # this method gets the csv file adds the extra columns and fill its value
        def modify_csv_file(file_path):
            # Read the CSV file into a Pandas DataFrame
            df = pd.read_csv(file_path)

            # Add a new "نوع" column to the DataFrame
            df['نوع'] = np.nan

            # Initialize variables
            current_type = np.nan
            temp = ' '

            # Iterate over each row of the DataFrame and fill in the "نوع" column
            for i, row in df.iterrows():
                if row.iloc[1] == ' ':
                    temp = row.iloc[0]
                else:
                    df.loc[i, 'نوع'] = temp

            df.to_csv(file_path, encoding='utf-8', index=False)

        print(f"Table data has been saved to {csv_filename} successfully.")
        print("non_respond")
        print(len(self.non_respond))
        print(self.non_respond)
        modify_csv_file(csv_filename)
