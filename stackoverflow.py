'''
This might have problems because stackoverflow check periodically, you're not a robot. For it to work, you need to periodically search things with a browser
and answer the "not a robot" question. Reminder that this repo is only an exercise on BeautifulSoup and web parsing.
'''
import requests, time, json
from bs4 import BeautifulSoup

def parse_item_number (s) :
    if s[-1] == 'k' :
        return int(s[:-1]) * 1000
    return int(s)

def parse_res(soup):
    '''
    Get all the questions from the results list (but not the answers)
    '''
    search_results= []
    list_res = [
        div
        for div in soup.findAll('div')
        if div.get('id') and div.get('id').startswith('question-summary')
    ]

    for curr_res in list_res:
        res = {
            item.find('span', class_='s-post-summary--stats-item-unit').getText():
                parse_item_number(item.find('span', class_='s-post-summary--stats-item-number').getText())
            for item in curr_res.find_all(class_="s-post-summary--stats-item")
        }

        res['title'] = curr_res.find('h3', class_='s-post-summary--content-title').getText().strip('\n')
        res['tags'] = [a.getText() for a in curr_res.find_all('a', attrs=dict(rel="tag"))]
        res['href'] = 'https://stackoverflow.com' + curr_res.find('h3', class_='s-post-summary--content-title').find('a', href=True)['href']
        
        search_results.append(res)

    return search_results

def get_max_page (soup) :
    return max([
        int(a.getText())
        for a in soup.find_all('a', class_="s-pagination--item js-pagination-item")
        if a.getText().isnumeric()
    ] 
    #if this is empty, this means there is no other page
    + [0])

def download_all_questions(query):
    search_results = []
    max_page = None

    page = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    base_url = 'https://stackoverflow.com/search?q={query}&tab=newest&page={page}&pagesize=15'

    while (max_page is None or page <= max_page):
        print(page, max_page, len(search_results))
        #do not spam stackoverflow too much
        time.sleep(5)
        search_page = requests.get(base_url.format(page=page, query=query), headers=headers)
        soup = BeautifulSoup(search_page.text, 'html.parser')
        search_results.extend(parse_res(soup))
        if max_page is None:
            max_page = get_max_page(soup)
        page += 1

    with open(f'result/stackoverflow_{query}.json', 'w', encoding='utf8') as f :
        json.dump(search_results, f, indent=2)

if __name__ == '__main__' :
    #replace "ipsum lorem" by your query
    download_all_questions('ipsum lorem')