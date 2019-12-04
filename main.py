from bs4 import BeautifulSoup
import requests
from argparse import ArgumentParser
import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

def process_command():
    parser = ArgumentParser()
    parser.add_argument('--start', '-s', type = int, required = True)
    parser.add_argument('--board', '-b', type = str, required = True)
    parser.add_argument('--num', '-n', type = int, required= False)
    return parser.parse_args()

class Crawler:  
    index = 0
    board = ""
    num = 0
    articles = {}
    gossip_data = {
        "from":"bbs/Gossiping/index.html",
        "yes": "yes"
    }
    comment_data = {}
    home = "https://www.ptt.cc/"

    def __init__(self,start,board,num):
        self.session = requests.session()
        requests.packages.urllib3.disable_warnings()
        self.session.post("https://www.ptt.cc/ask/over18",
                           verify=False,
                           data=self.gossip_data)
        self.index = start
        self.board = board
        if num == None:
            self.num = 1
        else:
            self.num = num

    def get_articles(self):
        link = "https://www.ptt.cc/bbs/{board}/index{start}.html".format(board = self.board , start = self.index )
        
        html = self.session.get(link).text
        soup = BeautifulSoup(html,"lxml")
        div = soup.find_all("div",class_ = "r-ent")
    
        for item in div:
            try:
                title = item.find("div",class_ = "title").text.strip()
                href = item.find("div",class_ = "title").a['href']
                self.articles[title]=self.home+href
                print(title,href)
            except:
                print("error loding link")

    def get_comments(self):
        pass

    def crawl(self):
        for i in range(self.num):            
            self.get_articles()
            self.index -= 1

args = process_command()
crawler = Crawler(args.start, args.board,args.num )
crawler.crawl()

