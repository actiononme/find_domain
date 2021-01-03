#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import os.path
import dns.resolver
import sys
import click


class Search(object):
    def __init__(self,domain,w,o):
        self.domain = domain
        self.wordlist = w
        self.output = o

    def brute(self):
        with open(self.wordlist,"r") as f:
            for word in f:
                word = word.strip()
                domain = word+"."+self.domain
                self.find(domain)
            f.close()

    def find(self,word):
        typelist = ["A",'AAAA','AFSDB','APL','CAA','CDNSKEY','CDS','CERT','CNAME','CSYNC','DHCID',\
                'DLV','DNAME','DNSKEY','DS','EUI48','EUI64','HINFO','HIP','IPSECKEY','KEY','KX',\
                'LOC','MX','NAPTR','NS','NSEC','NSEC3','NSEC3PARAM','OPENPGPKEY','PTR','RRSIG',\
                'RP','SIG','SMIMEA','SOA','SRV','SSHFP','TA','TKEY','TLSA','TSIG','TXT','URI',\
                'ZONEMD','SVCB','HTTPS','MD','MF','MAILA','MB','MG','MR','MINFO','MAILB','WKS',\
                'NB','NBSTAT','NULL','A6','NXT','KEY','SIG','HINFO','RP','X25','ISDN','RT','NSAP',\
                'PX','EID','NIMLOC','ATMA','APL','SINK','GPOS','UINFO','UID','GID','UNSPEC','SPF',\
                'NINFO','RKEY','TALINK','NID','L32','L64','LP','DOA']

        for record in typelist:
            try:
                answers = dns.resolver.resolve(word,record)
                print("domain find: ",word,"and record:",record)
                if self.output:
                    try:
                        with open(self.output,'a') as f:
                            f.write(word+" "+record+"\n")
                            f.close()
                    except Exception as e:
                        sys.exit(e)
                break
            except Exception as e:
                pass

class Engine(object):

    save = []

    def __init__(self,domain,o):
        self.domain = domain
        self.output = o


    def search(self):
        self.google()
        self.baidu()
        #  something wrong only get first page of the bing search engine 
        #self.bing()
        self.saveline()


    def google(self):
        # test the connect

        try:
            rep = requests.get('http://www.google.com',timeout=5)
        except Exception as e:
            print("can't connect with google")

        if 'rep' in locals():
            print("Search in Google")
            count = 0
            while True:
                url = "http://www.google.com/search?q=site:"+self.domain+"&start="+str(count)
                rep = requests.get(url)
                soup = BeautifulSoup(rep.text,"html5lib")
                target = soup.find_all("div",class_="BNeawe UPmit AP7Wnd")

                if target == [] or "Our systems have detected unusual traffic from your computer network" in soup.text:
                    break

                for url in target:
                    url = url.text.split(" ")[0]
                    if url not in self.save:
                        print("\033[1;32m",url,"\033[0m")
                        self.save.append(url)

                count += 10


    def baidu(self):
        try:
            rep = requests.get("http://www.baidu.com",timeout=5)
        except Exception as e:
            print("can't connect with baidu")

        if 'rep' in locals():
            print("Search in Baidu")
            count = 0
            while True:
                url = "http://www.baidu.com/s?wd=site:"+self.domain+"&pn="+str(count)
                rep = requests.get(url)
                soup = BeautifulSoup(rep.text,"html5lib")
                if "timeout hide" in rep.text and "timeout-img" in rep.text and "timeout-title" in rep.text and "timeout-button" in rep.text:
                    print("try again later,timeout now baidu")

                a = soup.find_all("div",class_="result c-container new-pmd")
                for each in a:
                    link = each.a.get('href')
                    self.link(link)

                empty1 = soup.find_all("div",class_="page-inner")
                if empty1 == []:
                    break

                empty2 = soup.find_all("div",class_="page-inner")[0].find_all("a")
                if empty2 == []:
                    break

                text = soup.find_all("div",class_="page-inner")[0].find_all("a")[-1].text.split(" ")[0]
                if len(text) != 3:
                    break

                count += 10


    def link(self,link):
        try:
            rep = requests.get(link)
        except Exception as e:
            pass

        if 'rep' in locals():
            domain = rep.url.split("/")[2]
            domain = domain.split("?")[0]
            if domain not in self.save:
                self.save.append(domain)
                print("\033[1;32m",domain,"\033[0m")


    def bing(self):
        try:
            rep = requests.get("http://cn.bing.com",timeout=5)
        except Exception as e:
            print("can't connect with bing")

        if 'rep' in locals():
            print("Search in Bing")
            count = 0
            while True:
                url = "https://cn.bing.com/search?q=site:"+self.domain+"&first="+str(count)
                rep = requests.get(url)
                soup = BeautifulSoup(rep.text,"html5lib")
                li = soup.find_all("li",class_="b_algo")
                for each in li:
                    domain = each.a.get("href").split("/")[2]
                    if domain not in self.save:
                        self.save.append(domain)
                        print("\033[1;32m",domain,"\033[0m")

                print(url)
                print(li)
                count += 10


    def saveline(self):
        if self.output != '':
            try:
                with open(self.output,'a') as f:
                    for line in self.save:
                        f.write(line+"\n")
                    f.close
            except Exception as e:
                print(e)


    def platform(self):
        print("other coming soon")
                
@click.command()
@click.option("-w",type=click.Path(exists=True),help="wordlist to search")
@click.option("-o",default='',help="save to the file")
@click.option("-s",is_flag=True,help="use the search engine: \rgoogle.com,baidu.com,bing.com")
@click.option("-p",is_flag=True,help="use platform api to search domain")
@click.argument("domain")

def options(domain,w,o,s):

    if w:
        if os.path.isfile(w):
            search = Search(domain,w,o)
            search.brute()
        else:
            sys.exit("\033[1;32mNo Such File %s\033[0m" % w)

    elif s:
        engine = Engine(domain,o)
        engine.search()

    elif p:
        engine = Engine(domain,o)
        engine.platform()
    

if __name__ == '__main__':
    options()
