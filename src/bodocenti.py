# -*- coding: utf-8 -*-

import csv
from pathlib import Path
import sys

# dalla colonna "Fase"

APERTO, INSERIMENTO, CHIUSO = 'aperte', 'nserimento', 'hiuso'

try:
  from selenium import webdriver
  from selenium.common.exceptions import NoSuchElementException
  from selenium.webdriver.common.keys import Keys
  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
except ImportError:
  sys.stderr.write('bodocenti: è necessario installare Selenium per il corretto funzionamento dello script!')
  sys.exit(1)

def table2csv(name, table):
    with open(name, 'w', encoding = 'utf-8', newline = '') as ouf:
        writer = csv.writer(ouf, delimiter = '\t', quotechar = '"', quoting = csv.QUOTE_MINIMAL, lineterminator = '\n')
        tag = 'th'
        for r in table.find_elements_by_tag_name('tr'):
            writer.writerow(c.text.strip() for c in r.find_elements_by_tag_name(tag))
            tag = 'td'

def download(user, password, dir = '.', nome = None, chiusi = False, inserimento = False):
  options = webdriver.FirefoxOptions()
  options.headless = True

  profile = webdriver.FirefoxProfile()
  profile.set_preference("profile.default_content_settings.popups", 0);

  driver = webdriver.Firefox(options = options, firefox_profile = profile)

  driver.get("https://work.unimi.it/boDocenti/ListaAppelliEIscritti")

  elem = driver.find_element_by_id("username")
  elem.clear()
  elem.send_keys(user)

  elem = driver.find_element_by_id("password")
  elem.clear()
  elem.send_keys(password)
  elem.send_keys(Keys.RETURN)

  WebDriverWait(driver, 10).until(EC.title_contains("Lista appelli"))
  driver.find_element_by_id('id1d').click()

  good_idxs = []
  for idx, row in enumerate(driver.find_elements_by_tag_name("tr")):
    if (
          ((APERTO in row.text) or
          (inserimento and INSERIMENTO in row.text) or
          (chiusi and CHIUSO in row.text))
        and
          (nome is None or (nome.lower() in row.text.lower()))
        ):
        good_idxs.append(idx)

  print('\nTrovati {} appelli...\n'.format(len(good_idxs)))

  for idx in good_idxs:
      row = driver.find_elements_by_tag_name("tr")[idx]

      ds = row.find_elements_by_tag_name('td')

      insegnamento = ds[0].text
      data = ds[1].text
      chiusura = ds[2].text
      fase = ds[3].text
      iscritti = ds[4].text
      tipo = ds[5].text
      presidente = ds[6].text

      path = Path(dir) / '{}@{}.tsv'.format(
        insegnamento[:ds[0].text.index('(') - 1].replace(' ', '_'),
        '-'.join(data.split('/')[::-1])
      )

      print("""Insegnamento:         {}
Data appello:         {}
Data fine iscrizioni: {}
Fase:                 {}
Iscritti:             {}
Tipo:                 {}
Presidente:           {}
Elenco salvato in:    {}
      """.format(
        insegnamento,
        data,
        chiusura,
        fase,
        iscritti,
        tipo,
        presidente,
        path
      ))

      row.find_element_by_tag_name('a').click()
      WebDriverWait(driver, 10).until(EC.title_contains("Elenco studenti"))

      try:
          iscr = driver.find_element_by_tag_name('table')
          table2csv(path, iscr)
      except NoSuchElementException:
          pass

      driver.back()

  driver.close()

if __name__ == "__main__":

  from argparse import ArgumentParser
  from getpass import getpass
  from os import environ
  from pathlib import Path

  parser = ArgumentParser(prog = 'bodocenti', description = 'Scarica gli elenchi di iscritti da BODocenti @ UniMI.')
  parser.add_argument('-u', '--user', type = str, help = 'nome utente del backoffice')
  parser.add_argument('-d', '--dir', type = str, default = '.', help = 'directory dove salvare gli elenchi (se assente, verrà usata la directory corrente)')
  parser.add_argument('-n', '--nome', type = str, nargs = '?', default = None, help = 'insegnamento da considerare (se asssente, saranno considerati tutti gli insegnamenti)')
  parser.add_argument('-i', '--inserimento', help = 'se presente, considera anche gli appelli in fase di inserimento esiti', action = 'store_true')
  parser.add_argument('-c', '--chiusi', help = 'se presente, considera anche gli appelli chiusi', action = 'store_true')
  args = parser.parse_args()

  user, password = args.user, None

  if user is None:
    try:
      user = environ['BODOCENTI_USER']
    except KeyError:
      user = input("User: ")

  try:
    password = environ['BODOCENTI_PASSWORD']
  except KeyError:
    password = getpass(prompt = "Password: ")

  if not Path(args.dir).is_dir():
    sys.stderr.write('bodocenti: la directory "{}" non esiste'.format(args.dir))
    sys.exit(1)

  download(user, password, args.dir, args.nome, args.chiusi, args.inserimento)
  try:
    Path('geckodriver.log').unlink()
  except FileNotFoundError:
    pass
