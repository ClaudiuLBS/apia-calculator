from io import TextIOWrapper
import requests
from bs4 import BeautifulSoup
import csv

from secret_file import payload

# payload = {
#   'name': 'ROXXXXXXXXX',
#   'password': 'abcd1234'
# }

try:
  output_file = open('apia_surfaces.txt', 'w')
except:
  output_file = open('apia_surfaces.txt', 'x')

YEAR = 2023

login_url = 'https://lpis.apia.org.ro/mapbender/frames/login.php'
page_url = f'https://lpis.apia.org.ro/reporting/{YEAR}/ipa_online/parcel_control.php?farmid={payload["name"]}&sirsup_code=&bloc_nr='

apia_codes = {
  'GRAU': '101',
  'PORUMB': '108',
  'FLOAREA-SOARELUI': '201',
  'LUCERNA - 9741': '9741',
  'LUCERNA - 974': '974',
}


def get_total_surface(apia_codes: dict, soup: BeautifulSoup, output_file:TextIOWrapper):
  total_surface = 0
  for code in apia_codes:
    current_surface = 0
    previous_second_sibling = soup('td', string = apia_codes[code])
    for str_value in previous_second_sibling:
      ha_value = float(str_value.next_sibling.next_sibling.text.replace(',', '.'))
      current_surface += ha_value
      
    current_surface = round(current_surface, 2)
    if current_surface > 0:
      output_file.write(f'{code}: {current_surface}\n')
      total_surface += current_surface

  total_surface = round(total_surface, 2)  
  output_file.write(f'\nTOTAL: {total_surface}')


def get_parcel_details(apia_codes: dict, soup: BeautifulSoup):

  all_details = {code: [] for code in apia_codes}
  for code in apia_codes:
    f = open(f'{code}-claudiu.csv', 'w')
    # create the csv writer
    csv_file = csv.writer(f)
    csv_file.writerow(['BLOC FIZIC', 'NR_PARCELA', 'SUPRAFATA'])
    code_fields = soup('td', string = apia_codes[code])

    for field in code_fields:
      current_parcel_details = []

      nr_field = field.previous_sibling.previous_sibling.previous_sibling.text + field.previous_sibling.previous_sibling.text
      ha_field = field.next_sibling.next_sibling.text
      bf_field = field.parent.parent.find_all('tr')[1].find_all('td')[0].text

      current_parcel_details.append(bf_field)
      current_parcel_details.append(nr_field)
      current_parcel_details.append(ha_field)
      
      all_details[code].append(current_parcel_details)

    csv_file.writerows(all_details[code])
    f.close()
  

with requests.Session() as session:

  # log in to page to get the cookies
  p = session.post(url=login_url, data=payload)
  # use the cookies to enter the actual page
  html_doc = requests.get(url=page_url, cookies=p.cookies, data=payload)
  soup = BeautifulSoup(html_doc.text, 'html.parser')
  # then calculet the surfaces
  # get_total_surface(apia_codes, soup, output_file)
  get_parcel_details(apia_codes, soup)
