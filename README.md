<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Codal Project</title>
</head>
<body>

  <header>
    <h1>Codal Project</h1>
    <p>Repository for the Codal project</p>
  </header>

  <section id="description">
    <h2>Description</h2>
    <p>This repository contains the source code for the Codal project. The project involves web scraping financial data from the Codal website using Scrapy and other related tools.</p>
  </section>

  <section id="contents">
    <h2>Contents</h2>
    <ul>
      <li><a href="#installation">Installation</a></li>
      <li><a href="#usage">Usage</a></li>
      <li><a href="#contributors">Contributors</a></li>
      <li><a href="#license">License</a></li>
    </ul>
  </section>

  <section id="main-py-setup">
    <h2>Setting up main.py</h2>
    <p>In <code>main.py</code>, set the path to the <code>Ctable.py</code> spider file. For example:</p>
    <pre>
      <code>spider_path = "./codal/Scrappy/codaltable/codaltable"</code>
    </pre>
  </section>

  <section id="csv-files-location">
    <h2>CSV Files Location</h2>
    <p>The CSV files generated by the spider will be saved in a folder named "csv" located in the same directory as the <code>Ctable.py</code> spider file. The path to this directory is:</p>
    <pre>
      <code>./codaltable/codaltable/spiders</code>
    </pre>
  </section>

  <section id="runtime-py-command">
    <h2>Running the Spider with runtime.py</h2>
    <p>In <code>runtime.py</code>, the <code>run_spider</code> method runs a command in the terminal to execute the spider. On macOS and Linux, the command is:</p>
    <pre>
      <code>cd "{spider_path}" && scrapy crawl {spider_name} -a url_list="{url_arguments}"</code>
    </pre>
    <p>On Windows, replace it with:</p>
    <pre>
      <code>command = cd /d "{spider_path}" && scrapy crawl {spider_name} -a url_list="{url_arguments}"</code>
    </pre>
  </section>

  <section id="splash-docker">
    <h2>Run Splash Docker Image</h2>
    <p>Ensure that you have the Splash Docker image (splash.tar) and run it.</p>
    <p>Example command:</p>
    <pre>
      <code>docker load -i splash.tar && docker run -p 8050:8050 -p 5023:5023 -p 8051:8051 splash</code>
    </pre>
  </section>

  <section id="change-dns">
    <h2>Change DNS</h2>
    <p>Visit https://shecan.ir/ and change the DNS settings as required.</p>
  </section>

  <section id="run-main-py">
    <h2>Run main.py</h2>
    <p>Activate your virtual environment and run <code>main.py</code>. If the path to the spider is correct, it should run successfully.</p>
  </section>

  <section id="installation">
    <h2>Installation</h2>
    <p>Clone the repository and install the required packages:</p>
    <pre>
      <code>git clone git@github.com:SaminRazeghi/Codal_Project.git</code>
      <code>pip install -r requirements.txt</code>
    </pre>
  </section>

  <section id="usage">
    <h2>Usage</h2>
    <p>Follow the instructions in the project to run the web scraper and extract financial data from Codal. Make sure to provide the necessary URLs as arguments.</p>
  </section>

  <section id="contributors">
    <h2>Contributors</h2>
    <p>Feel free to contribute to the project. Fork the repository, make changes, and submit pull requests. Your contributions are highly appreciated!</p>
  </section>

  <section id="license">
    <h2>License</h2>
    <p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>
  </section>

</body>
</html>