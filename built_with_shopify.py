#import argparse
import requests
from lxml import html
import time
#from price_parser import Price

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
    file_name = "test copy 2.csv"
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
      url = parsed_line[1]
      using_shopify = is_shopify(url)
      parsed_line[2] = using_shopify
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
      

def test(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
    response = requests.get(url, headers=headers, verify=True)
    return response
  

# determines whether a website is on shopify - return true if true, false othersize
def is_shopify(url): 
  url = 'https://builtwith.com/{0}'.format(url)
  #print(url)
  #print(repr(url))
  #headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
  failed = False

  # Retries 5 times for handling network errors
  for _ in range(3):
    print ("Retrieving %s"%(url)) 
    #response = ''
    #s = requests.session()
    # s.config['keep_alive'] = False
    # time.sleep(2)
    #s = requests.session(config={'keep_alive': False})
    #response = s.get(url, headers=headers, verify=True)
    response = test(url)
   # parser = html.fromstring(response.text)
   # print("PARSER: ", response.text)
    print("Done retrieving - status code: ", response.status_code)

    if response.status_code!=200:
        failed = True
        continue
    else:
        failed = False
        break

  if failed:
    print("The builtwith.com network is unresponsive. Please try again later (or now).")
    return "URL Failed"

  #fbytes = bytearray("Shopify", 'utf-8')
  #print( "    Shopify binary = ", response.content.find(fbytes) )
  if (response.text).find("Shopify") != -1:
    print(" -----------> SHOPIFY\n")
    return "Shopify"
  else:
    print(" -----------> OTHER\n")
    return "Other"
  #card_titles = parser.xpath('//h6[contains(@class, "card-title")]//text()')
  #for card_title in card_titles:
    #print("CARD TITLE: ", card_title)
    #card_title = ' '.join(' '.join(card_title).split())
   # print("CARD TITLE 2: ", card_title)
    #if card_title == 'eCommerce':
      #print("ECOMMERCE")
      #raw_header = card_title.xpath('.//a[contains(@class,"text-dark")]//text()')
      #print("RAW HEADER: ", raw_header)
      #if len(raw_header) > 0:
        #print(raw_header[0])
        #if raw_header[0] == 'Shopify':
          #print("made it")
          #return True
  #return False

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