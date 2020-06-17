#import argparse
import requests
from lxml import html
import time
from price_parser import Price
import re # for removing non-numeric characters from strings for num employees

# automatically reads in the next unread line so no need for a line number parameter
def line_from_csv(f):
  ln = f.readline()
  if ln == "":
    return None
  print( "line: ", ln, end = "" )
  i = 0
  li = 0
  parsed_line = []
  while True:
    start = i
    while( i < len(ln) and ln[i] != ',' ):
      i = i + 1
    if i < len(ln):
      parsed_line.insert( li, ln[start:i] )
    li = li + 1
    i = i + 1
    if i >= len(ln):
      break
  print(">>>>> ", parsed_line)
  return parsed_line

# parses url from csv and parsed_line
def process_file():
    file_name = "test.csv"
    fi = open(file_name, "r") # r stands for read
    if fi == None:
      print("Could not open csv file: ", file_name)
      return None
    
    file_name_result = "Target_Built_With.csv"
    fo = open(file_name_result, "w+") # r stands for write over
    if fo == None:
      print("Could not create csv file: ", file_name_result)
      return None

    # copy over the header
    ln = fi.readline()
    fo.write(ln)

    while True:
      parsed_line = line_from_csv(fi)
      if parsed_line == None: # reached the last line of the csv
        break
      if len(parsed_line) < 1:
        fo.write("\r\n")
        continue
      brand = parsed_line[0]
      url = parsed_line[1]
      annual_sales = get_annual_sales(url)
      parsed_line[3] = annual_sales
      num_employees = get_num_employees(brand)
      parsed_line[5] = num_employees
      alexa_rating = get_alexa_rating(url)
      parsed_line[4] = alexa_rating
      if parsed_line:
        line = ""
        for l in parsed_line:
          line = line + l + ","
        line = line[0:len(line)-1]
        fo.write(line)
        fo.write("\r\n")

      else:
        print("No data scraped")
    fi.close()
    fo.close()

def get_annual_sales(url): 
  url = 'https://ecommercedb.com/en/store/{0}'.format(url)
  print(url)
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
  failed = False

  # Retries 5 times for handling network errors
  for _ in range(2):
    print ("Retrieving %s"%(url)) 
    response = requests.get(url, headers=headers, verify=True)
    parser = html.fromstring(response.text)
    #print("PARSER: ", response.text)
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
  print("RAW VALUE: ", raw_value)
  value = raw_value[0].strip()
  if value[len(value) - 1] == 'm':
    magnitude = 1000000
  else:
    magnitude = 1
  number_value = value[3: len(value) - 1]
  price = Price.fromstring(number_value).amount_float
  price = price * magnitude
  price = str(price)
  print(price)
  return price

def get_alexa_rating(url): 
  url = 'https://www.alexa.com/siteinfo/{0}'.format(url)
  print(url)
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
  failed = False

  # Retries 5 times for handling network errors
  for _ in range(2):
    print ("Retrieving %s"%(url)) 
    response = requests.get(url, headers=headers, verify=True)
    parser = html.fromstring(response.text)
    #print("PARSER: ", response.text)
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
  print("RANKING: ", ranking)
  return ranking

def get_num_employees(brand): 
  url = 'https://www.google.com/search?q={0} number of employees'.format(brand)
  print(url)
  headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
  failed = False

  # Retries 5 times for handling network errors
  for _ in range(2):
    print ("Retrieving %s"%(url)) 
    response = requests.get(url, headers=headers, verify=True)
    parser = html.fromstring(response.text)
    #print("PARSER: ", response.text)
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
  return num_employees

def save_scraped_data(lines):
  if lines:
      file_name = "Target_Built_With.csv"
      f = open(file_name,"w+")
      f.write("Brand name", "Brand URL", "Shopify or other","Annual sales", "Alexa rating", "# of employees,Segment (s/m/l/d)", "Name/Founder 1,Contact email""\r\n")
      for line in lines:
          f.write(line + "\r\n")
      f.close() 
  else:
      print("No data scraped")
  return

# main code entry point
if __name__=="__main__":

  process_file()
  #save_scraped_data(list)
      
    # done