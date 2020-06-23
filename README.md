# Scrape Brand Stats
This program takes in a csv file with rows representing brands and each column representing an attribute of a brand such as annual sales, number of employees, and size. The program then calculates the annual sales, alexa rating, number of employees, size (S,M,L), whether or not the brand is on Shopify, and the founder/ceo for the brand. The new calculations are added to a new duplicate csv file with the fields specified filled in. 

Built using multiprocessing Pool with 8 threads.
