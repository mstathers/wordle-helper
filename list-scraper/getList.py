import requests
from bs4 import BeautifulSoup


r = requests.get("https://wordletools.azurewebsites.net/weightedbottles")

soup = BeautifulSoup(r.text, 'html.parser')


word_table = soup.find_all('table')[-1]
word_rows = word_table.find_all('tr')

words = []

for row in word_rows:
    for col_idx, col in enumerate(row.find_all('td')):
        if col_idx == 0:
            word = col.text.strip().lower()
            words.append(word)


for word in words:
    print(f"{word}")

#with open('word-bank.csv', 'w') as f:
#    for word in words:
#        f.write(f"{word}\n")







