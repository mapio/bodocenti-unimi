# -*- coding: utf-8 -*-

from collections import namedtuple
from pathlib import Path
import sys

Appello = namedtuple('Appello', ['insegnamento', 'data', 'chiusura', 'fase', 'iscritti', 'tipo', 'presidente', 'idx'])

# dalla colonna 'Fase'

APERTO, INSERIMENTO, CHIUSO = 'aperte', 'nserimento', 'hiuso'

try:
  from selenium import webdriver
  from selenium.webdriver.firefox.webdriver import WebDriver as Firefox
  from selenium.webdriver.firefox.options import Options
  from selenium.common.exceptions import ElementClickInterceptedException
  from selenium.webdriver.common.by import By
  from selenium.webdriver.common.keys import Keys
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC
except ImportError:
  sys.stderr.write('bodocenti: è necessario installare Selenium per il corretto funzionamento dello script!')
  sys.exit(1)

def click(driver, locator, timeout=10):
  WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator)).click()

def download(user, password, dir = Path('.'), nome = None, chiusi = False, inserimento = False):
  options = Options()
  options.add_argument('-headless')
  options.set_preference("browser.download.folderList", 2)
  options.set_preference("browser.download.manager.showWhenStarting", False)
  options.set_preference("browser.download.dir", str(dir))
  options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel")
  options.enable_downloads = True

  driver = Firefox(options = options)

  driver.get('https://work.unimi.it/boDocenti/ListaAppelliEIscritti')

  elem = driver.find_element(By.ID, 'username')
  elem.clear()
  elem.send_keys(user)

  elem = driver.find_element(By.ID, 'password')
  elem.clear()
  elem.send_keys(password)
  elem.send_keys(Keys.RETURN)

  WebDriverWait(driver, 10).until(EC.title_contains('Lista appelli'))
  click(driver, (By.NAME, 'cerca'))

  appelli = []
  for idx, row in enumerate(driver.find_elements(By.TAG_NAME, 'tr')):
    if (
          ((APERTO in row.text) or
          (inserimento and INSERIMENTO in row.text) or
          (chiusi and CHIUSO in row.text))
        and
          (nome is None or (nome.lower() in row.text.lower()))
        ):
      ds = row.find_elements(By.TAG_NAME, 'td')
      appelli.append(Appello(
          insegnamento = (ds[0].text[:ds[0].text.index('(') - 1] if '(' in ds[0].text else ds[0].text).replace(' ', '_'),
          data         = '-'.join(ds[1].text.split('/')[::-1]),
          chiusura     = '-'.join(ds[2].text.split('/')[::-1]),
          fase         = ds[3].text,
          iscritti     = int(ds[4].text),
          tipo         = ds[5].text,
          presidente   = ds[6].text,
          idx          = idx,
      ))

  print(f'\nTrovati {len(appelli)} appelli...')

  for a in appelli:
    print(f'''
Insegnamento:         {a.insegnamento}
Data appello:         {a.data}
Data fine iscrizioni: {a.chiusura}
Fase:                 {a.fase}
Iscritti:             {a.iscritti}
Tipo:                 {a.tipo}
Presidente:           {a.presidente}''')
    if a.iscritti == 0: continue

    click(driver, driver.find_elements(By.TAG_NAME, 'tr')[a.idx].find_element(By.TAG_NAME, 'a'))
    WebDriverWait(driver, 10).until(EC.title_contains('Elenco studenti'))

    before = set(dir.glob('*.xls'))
    click(driver, (By.NAME, 'xlsExport'))
    after = WebDriverWait(driver, 30).until(
      lambda _: set(dir.glob('*.xls')) - before
    )
    if len(after) != 1:
      raise RuntimeError(f'Più di un file XLS scaricato, trovati {len(after)}: {after}')
    xls = after.pop()
    path = dir / f'{a.insegnamento}@{a.data}.xls'
    xls.rename(path)
    print(f'Downloaded:           {path.name}')
    driver.back()
    WebDriverWait(driver, 10).until(EC.title_contains('Lista appelli'))

  driver.close()

if __name__ == '__main__':

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
      user = input('User: ')

  try:
    password = environ['BODOCENTI_PASSWORD']
  except KeyError:
    password = getpass(prompt = 'Password: ')

  path = Path(args.dir).absolute()
  if not path.is_dir():
    sys.stderr.write(f'bodocenti: la directory "{str(path)}" non esiste')
    sys.exit(1)

  download(user, password, path, args.nome, args.chiusi, args.inserimento)
  try:
    Path('geckodriver.log').unlink()
  except FileNotFoundError:
    pass
