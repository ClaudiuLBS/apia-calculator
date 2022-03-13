import requests
from bs4 import BeautifulSoup

from secret_file import payload

# payload = {
#   'name': 'ROXXXXXXXXX',
#   'password': 'abcd1234'
# }

try:
  output_file = open('apia_surfaces.txt', 'w')
except:
  output_file = open('apia_surfaces.txt', 'x')

login_url = 'https://lpis.apia.org.ro/mapbender/frames/login.php'
page_url = f'https://lpis.apia.org.ro/reporting/2022/ipa_online/parcel_control.php?farmid={payload["name"]}&sirsup_code=&bloc_nr='

apia_codes = {
  'GRAU': '101',
  'PORUMB': '108',
  'FLOAREA-SOARELUI': '201',
  'LUCERNA1': '9741',
  'LUCERNA2': '974',
}

with requests.Session() as session:
  # log in to page to get the cookies
  p = session.post(url=login_url, data=payload)
  # use the cookies to enter the actual page
  html_doc = requests.get(url=page_url, cookies=p.cookies, data=payload)
  soup = BeautifulSoup(html_doc.text, 'html.parser')
  # then calculet the surfaces
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
