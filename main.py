from bs4 import BeautifulSoup
from bs4.element import NavigableString
from argparse import ArgumentParser
import json
import requests
import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

def process_command():
    help_text = """ 
    https://www.ptt.cc/bbs/[BOARD]/index[START].html
    """
    parser = ArgumentParser(description=help_text)
    parser.add_argument('--start', '-s', type = int, required = True)
    parser.add_argument('--board', '-b', type = str, required = True)
    parser.add_argument('--num', '-n', type = int, required= False,help = "indicate the number of pages to crawl,1 by default")
    return parser.parse_args()

class Crawler:  
    index = 0
    board = ""
    num = 0
    articles = {}
    post_data = {
        "from":"bbs/Gossiping/index.html",
        "yes": "yes"
    }
    article_data = []
    """
    Format:
    {
        "article_link" : link,
        "article_title": title,
        "author : author,
        "board" : board,
        "content" : article,
        "date" : date,
        "comment_data" :[
            {
            "tag" :噓 推,
            "user_id":id,
            "user_ip":ip,
            "datetime" :datetime
            },
            ...
        ]
    }
    """
    home = "https://www.ptt.cc/"

    def __init__(self,start,board,num):
        self.session = requests.session()
        requests.packages.urllib3.disable_warnings()
        self.session.post("https://www.ptt.cc/ask/over18",
                           verify=False,
                           data=self.post_data)
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
                #print(title,href)
            except:
                print("error loding link")

    def get_content(self):
       
        for title,link in self.articles.items():
            result =  {
            "article_link": link,
            "article_title": title,
            "author" : "",
            "board" : self.board,
            "content" : "",
            "date" : "",
            "comment_data" :[]
            }
            try:
                html = self.session.get(link).text
                print("getting contents of "+link)
                soup = BeautifulSoup(html,"lxml")     
         
                for tag in soup.select("#main-content")[0]:

                    if type(tag) == NavigableString and tag != "\n":
                        result["content"] = tag.strip()
                        
                        break
                
                result["author"] = soup.find_all("span",class_ ="article-meta-value" )[0].text
                result["date"]  = soup.find_all("span",class_ ="article-meta-value" )[-1].text
               
                for element in soup.find_all("div",class_ = "push"):
                    
                    try:
                        tag = element.find("span",class_ = "f1 hl push-tag").text.strip()
                    except:
                        tag = element.find("span",class_ = "hl push-tag").text.strip()
                    user_id = element.find("span",class_ = "f3 hl push-userid").text.strip()              
                    comment = element.find("span",class_="f3 push-content").text.strip()[2:]
                    _ipdatetime = element.find("span",class_="push-ipdatetime").text.split()
                    
                    if len(_ipdatetime) == 3:
                        ip = _ipdatetime[0]
                        datetime = _ipdatetime[1]+_ipdatetime[2]
                    else:
                        ip = ""
                        datetime = _ipdatetime[0] +_ipdatetime[1]
                    #remove the ':' in the beginning 

                    
                    result["comment_data"].append(
                        {   
                            "tag":tag,
                            "user_id":user_id,
                            "ip":ip,
                            "datetime":datetime}
                    )                        
                self.article_data.append(result)     
                             
            except:
                print("error loding article")
            

    def crawl(self):
        for i in range(self.num):            
            self.get_articles()
            self.index -= 1
            self.get_content()


args = process_command()
crawler = Crawler(args.start, args.board, args.num)
crawler.crawl()


output_json = json.dumps(crawler.article_data)
file_name = crawler.board+".json"
if os.path.isfile(file_name):
    print("exist")
    fp = open(file_name,"r")
    json_original = fp.read()
    fp.close()
  
    output = json_original.strip()[:-1]+","
    output += output_json[1:]
    fp = open(file_name,"w")
    fp.write(output)
    
else:
    fp = open(file_name,"w")
    fp.write(output_json)