#coding=utf-8
import time
import re
import os
import requests
import re
from bs4 import BeautifulSoup
import requests
import pathlib



def get_list(column_id, headers):
    url = f'https://www.zhihu.com/api/v4/columns/{column_id}/items'
    print(url)
    article_dict = {}
    while True:
        print('fetching', url)
        try:
            resp = requests.get(url, headers=headers)
            j = resp.json()
            data = j['data']
        except:
            print('get list failed')

        for article in data:
            aid = article['id']
            akeys = article_dict.keys()
            if aid not in akeys:
                article_dict[aid] = article['title']

        if j['paging']['is_end']:
            break
        url = j['paging']['next']
        time.sleep(2)

    with open(OUTPUT_FOLDER / 'zhihu_ids.txt', 'w',encoding='utf-8') as f:
        items = sorted(article_dict.items())
        for item in items:
            f.write('%s %s\n' % item)
            
def get_html(aid, title, index):
    title = re.sub('[\/:*?"<>|]','-',title) #正则过滤非法文件字符
    print(title)
    file_name = '%03d. %s.html' % (index, title)
    if os.path.exists(file_name):
        print(title, 'already exists.')
        return
    else:
        print('saving', title)
    url = 'https://zhuanlan.zhihu.com/p/' + aid
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html)
    try:
        content = soup.find("div",{"class":"Post-RichText"}).prettify()
    except:
        print("saving",title,"error")
        return
    content = content.replace('data-actual', '')
    content = content.replace('h1>', 'h2>')
    content = re.sub(r'<noscript>.*?</noscript>', '', content)
    content = re.sub(r'src="data:image.*?"', '', content)
    content = '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body><h1>%s</h1>%s</body></html>' % (
        title, content)
    with open(OUTPUT_FOLDER / file_name, 'w',encoding='utf-8') as f:
        f.write(content)
    time.sleep(2)

def get_details():
    with open(OUTPUT_FOLDER / 'zhihu_ids.txt','r',encoding='utf-8') as f:
        i = 1
        for line in f:
            lst = line.strip().split(' ')
            aid = lst[0]
            title = '_'.join(lst[1:])
            get_html(aid, title, i)
            i += 1
        print("done")

"""
建议别用 看不到进度条还有速度不知为何很慢
"""
def to_pdf():
    import pdfkit
    print('exporting PDF...')
    htmls = []
    for root, dirs, files in os.walk('.'):
        print(root)
        print(dirs)
        print(files)
        htmls += [name for name in files if name.endswith(".html")]
        print(htmls)
        pdfkit.from_file(sorted(htmls), author + '.pdf')
    print("done")
    
"""
直接调用 wkhtmltopdf 生成 pdf 文档
"""
def get_args():
    print('exporting PDF...')
    htmls = ""
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name.endswith(".html"):
                htmls += '"'+name+'"'+" "
        print(htmls) 
    return htmls

if __name__ == '__main__':
    column_id = "c_116602381"
    column_name = "魔鬼眼中的自然界-贾明子"
    headers = {
        'authority': 'www.zhihu.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-GB;q=0.6',
        'referer': f'https://www.zhihu.com/column/{column_id}',
        'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    }

    OUTPUT_FOLDER = pathlib.Path("output") /column_name


    # os.makedirs(OUTPUT_FOLDER)

    # get_list(column_id, headers)
    # get_details()
    pdfArgs=get_args()
    # to display chinese
    # `apt-get install fonts-wqy-microhei ttf-wqy-microhei fonts-wqy-zenhei ttf-wqy-zenhei`
    # todo: currently can only convert each page separately
    # todo: the  font is too small
    # I think I should use calibre
    # https://www.reddit.com/r/Calibre/comments/9pzf70/merging_html_files_into_a_single_epub/
    pdfEnd = 'wkhtmltopdf '+pdfArgs+column_name+".pdf"
    if(os.system(pdfEnd)==0):
        print("exporting PDF success")
    else:
        print("exporting PDF failed")
        
    