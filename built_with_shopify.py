import argparse
import requests
from lxml import html
from price_parser import Price

def line_from_csv( f ):
  ln = f.readline()
  if ln == "":
    return None
  print( "line: ", ln, end = "" )
  i = 0
  li = 0
  list = []
  while True:
    start = i
    while( i < len(ln) and ln[i] != ',' ):
      i = i + 1
    if i < len(ln):
      list.insert( li, ln[start:i] )
    li = li + 1
    i = i + 1
    if i >= len(ln):
      break
  print(">>>>> ", list)
  return list


def parse_urls_from_csv():
    file_name = "test copy.csv"
    urls = []
    f = open( file_name, "r" )
    if f == None:
      print("Could not open csv file: ", file_name )
      return None
    while True:
      list = line_from_csv(f)
      if list == None:
        break
      url = list[1]
      bool = is_shopify(url)
      list[4] = bool # 4??

    return urls

def is_shopify(url): 

    page_num = 1 

    while True:
        url = 'https://builtwith.com/{0}'.format(url)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
        failed = False

        # Retries 5 times for handling network errors
        for _ in range(5):
            print ("Retrieving %s\n\n"%(url)) 
            response = requests.get(url, headers=headers, verify=True)
            parser = html.fromstring(response.text)
            print("Done retrieving")

            if response.status_code!=200:
                failed = True
                continue
            else:
                failed = False
                break

        if failed:
            print("The builtwith.com network is unresponsive. Please try again later (or now).")
            return []

        product_listings = parser.xpath('//div[contains(@class, "card card--small")]')
 
        count = 0
        for product in product_listings:
            raw_url = product.xpath('.//a[contains(@class,"tile__covershot")]/@href')
            raw_title = product.xpath('.//a[contains(@class,"tile__title")]//text()')
            raw_price = product.xpath('.//span[contains(@class,"p--t--1")]//text()')
            raw_title[0].encode('ascii', 'ignore')

            count = count + 1
            product_url = 'https://poshmark.com' + raw_url[0]
            title = ' '.join(' '.join(raw_title).split())
            price  = ' '.join(' '.join(raw_price).split())
            parsed_price = Price.fromstring(price)
            total_value = total_value + parsed_price.amount_float

            data = {
                        'url':product_url,
                        'title':title,
                        'price':price, 
                        'sold':"Available"
            }
            scraped_products.append(data)

        if scraped_products:
            total_count = total_count + count
            if count < 48: # 48 items per page on Poshmark
                stats = "  AVAILABLE STATS for Brand: %s   Items Scanned: %d   Total Value: $%0.2f "%( brand, 
                total_count, total_value)
                available_value = total_value  
                print(stats)
                print("-------> DONE WITH AVAILABLE!")
                break
            page_num = page_num + 1
        else:
            print("No available product listings on Poshmark")
            break
    return scraped_products


def save_scraped_data(sdata, brand):
    if sdata:
        file_name = "Poshmark_" + str(brand) + ".csv"
        f = open(file_name,"w+")
        f.write("\"title\", price, sold, url\r\n")

        total_value_stats = "  TOTAL VALUE OF AVAILABLE AND SOLD ITEMS: $" + str(available_value + sold_value)
        print(total_value_stats)
        f.write(stats) 
        f.write("\r\n")
        f.write(sold_stats)
        f.write("\r\n")
        f.write(total_value_stats)
        f.write("\r\n")

        for data in sdata:
            f.write("\"" + data['title'] + "\", ")
            new_price = data['price'].replace(',', "")
            f.write( new_price + ", ")
            f.write( data['sold'] + ", ")
            f.write( data['url'] + "\r\n")
        f.close() 
    else:
        print("No data scraped")
    return

# main code entry point
if __name__=="__main__":

    parse_urls_from_csv()
    if False:
      argparser = argparse.ArgumentParser()
      argparser.add_argument('url',help = 'URL')
      args = argparser.parse_args()

      brand = args.brand
      scraped_data = parse_available(brand)
      scraped_data = scraped_data + parse_sold(brand)
      save_scraped_data(scraped_data, brand)
       
    # done