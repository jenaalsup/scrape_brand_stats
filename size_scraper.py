import argparse
import requests
from lxml import html
import time
from price_parser import Price
from multiprocessing import Pool
import multiprocessing

header = ''
# indexes of each category
BRAND = 0
URL = 1
SHOPIFY = 2
SALES = 3
ALEXA = 4
EMPLOYEES = 5
SIZE = 6
FOUNDER = 7
CONTACT = 8


def pull_brand(data):
  # do slow things <--
  # do NOT write to csv here.
  brand = data[BRAND]
  url = data[URL]
  size = data[SIZE]
  annual_sales = get_annual_sales(url)
  data[SALES] = annual_sales
  alexa_rating = get_alexa_rating(url)
  data[ALEXA] = alexa_rating
  num_employees = get_num_employees(brand)
  data[EMPLOYEES] = num_employees

  if size == '': # don't overwrite a size that is already present in the csv
    if annual_sales != 'URL Failed':
      try:
        annual_sales = float(annual_sales)
      except ValueError:
        annual_sales = 0
      if annual_sales == 0:
        print("BROKEN")
        data[SIZE] = '?Small'
      elif annual_sales <= 10000000: # small <= 10m
        data[SIZE] = 'Small'
      elif annual_sales >= 100000000: # large >= 100m
        data[SIZE] = 'Large'
      else: # medium is between small and large
        data[SIZE] = 'Medium'
    elif num_employees != 'Brand Failed':
      try:
        num_employees = float(num_employees)
      except ValueError:
        num_employees = 0    
      if num_employees == 0:
        print("BROKEN")
        data[SIZE] = '?Small'
      elif num_employees <= 10: # small <= 10
        data[SIZE] = 'Small'
      elif num_employees >= 100: # large >= 100
        data[SIZE] = 'Large'
      else: # medium is between small and large
        data[SIZE] = 'Medium'
    else:
      data[SIZE] = '?Small' # set to ?Small if unable to parse info on the brand

  return data # return the line needed to write to the csv



# incomplete

def pull_raw_data(brands, urls, shopifys, sales, alexas, employees, sizes, founders, contacts):
  arguments = [(brands[i], urls[i], sizes[i]) for i in range(len(brands))]
  with Pool(8) as p:
      all_pulled_data = p.map(pull_brand, arguments)
  print(f'all pulled data: {all_pulled_data}')
  return all_pulled_data


# incomplete
def process_data(database):
  POOL_NUM = 8
  with Pool(POOL_NUM) as p:
    all_processed_data = p.map( pull_brand, database )
    print(">>>> DONE with thread processing")
  return all_processed_data

def read_data(file_path):
  global header
  file_name = file_path
  fi = open(file_name, "r") # r stands for read
  if fi == None:
    print("Could not open csv file: ", file_name)
    return None
  database = []
  header = fi.readline()
  for i in range(100000):
    parsed_line = line_from_csv(fi)
    if parsed_line == None:
      break
    database.insert(i, parsed_line)
  fi.close()
  return database

# only write the database to csv don't change the database at all
def write_data_to_csv(database):
  file_name_result = "result_after_scraping.csv"
  fo = open(file_name_result, "w+") # r stands for write over
  if fo == None:
    print("Could not create csv file: ", file_name_result)
    return None

  # header
  fo.write(header)

  for data in database:
    str_data = ''
    for item in data:
      str_data = str_data + item + ","
    str_data = str_data[0:len(str_data)-1]
    fo.write(str_data) 
    fo.write("\r\n")
  fo.close()

# helper methods

def get_annual_sales(url): 
  url = 'https://ecommercedb.com/en/store/{0}'.format(url)
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
  failed = False

  # Retries 5 times for handling network errors
  for _ in range(2):
    print ("Retrieving %s"%(url)) 
    response = requests.get(url, headers=headers, verify=True)
    parser = html.fromstring(response.text)
    print("Done retrieving - status code: ", response.status_code)

    if response.status_code!=200:
        failed = True
        continue
    else:
        failed = False
        break

  if failed:
    print("The ecommercedb.com network is unresponsive or url error. Please try again later (or now).")
    return "URL Failed"

  raw_value = parser.xpath('//div[contains(@class, "fancyBox__content")]//text()')
  value = raw_value[0].strip()
  if value[len(value) - 1] == 'm':
    magnitude = 1000000
  else:
    magnitude = 1
  number_value = value[3: len(value) - 1]
  price = Price.fromstring(number_value).amount_float
  price = price * magnitude
  price = str(price)
  return price

def get_alexa_rating(url): 
  url = 'https://www.alexa.com/siteinfo/{0}'.format(url)
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
  failed = False

  # Retries 5 times for handling network errors
  for _ in range(2):
    print ("Retrieving %s"%(url)) 
    response = requests.get(url, headers=headers, verify=True)
    parser = html.fromstring(response.text)
    print("Done retrieving - status code: ", response.status_code)

    if response.status_code!=200:
        failed = True
        continue
    else:
        failed = False
        break

  if failed:
    print("The alexa.com network is unresponsive or url error. Please try again later (or now).")
    return "URL Failed"

  raw_value = parser.xpath('//div[contains(@class, "rankmini-rank")]//text()') # some sites use rankmini-rank
  if len(raw_value) < 1:
    raw_value = parser.xpath('//p[contains(@class, "big data")]//text()') # some sites use big data
    if len(raw_value) < 1:
      return "URL Failed"
  value = raw_value[2].strip()
  ranking = ''.join([c for c in value if c in '1234567890'])
  return str(ranking)

def get_num_employees(brand): 
  url = 'https://www.google.com/search?q={0} number of employees'.format(brand)
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
  failed = False

  # Retries 5 times for handling network errors
  for _ in range(2):
    print ("Retrieving %s"%(url)) 
    response = requests.get(url, headers=headers, verify=True)
    parser = html.fromstring(response.text)
    print("Done retrieving - status code: ", response.status_code)

    if response.status_code!=200:
        failed = True
        continue
    else:
        failed = False
        break

  if failed:
    print("The google.com network is unresponsive or url error. Please try again later (or now).")
    return "Brand Failed"

  raw_value = parser.xpath('//div[contains(@class, "Z0LcW XcVN5d AZCkJd")]//text()')
  if len(raw_value) < 1:
    return "Brand Failed"
  value = raw_value[0].strip()
  num_employees = ''.join([c for c in value if c in '1234567890'])
  return str(num_employees)


def line_from_csv(f):
  ln = f.readline()
  while True:
    length = len(ln)-1
    if length < 0:
      break
    if ln[length] == '\r' or ln[length] == '\n':
      ln = ln[:length]
    else:
      break
  # skip blank lines
  if ln == "":
    return None
  i = 0
  li = 0
  parsed_line = []
  
  while True:
    start = i
    while( i < len(ln) and ln[i] != ',' ):
      i = i + 1
    parsed_line.insert( li, ln[start:i] )
    li = li + 1
    i = i + 1
    if i >= len(ln): 
      break
  # account for missing commas or last data
  while li < 9:
    parsed_line.insert( li, "" )
    li = li + 1
  return parsed_line

# main code entry point
if __name__=="__main__":
  multiprocessing.freeze_support()
  argparser = argparse.ArgumentParser()
  argparser.add_argument('path',help = 'Path to CSV')
  args = argparser.parse_args()
  file_path = args.path
  database = read_data(file_path)
  database = process_data(database)
  write_data_to_csv(database)