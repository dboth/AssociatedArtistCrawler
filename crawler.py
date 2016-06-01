# -- coding: utf-8 --
import json, urllib2, re

class ArtistCrawler:
    def __init__(self, outputfile, stackfile, donefile):
        #at least one artist has to be in the stackfile!
        self.outputb = open(outputfile,"a")
        self.stackfile = stackfile
        self.donefile = donefile
        with open(stackfile,"r") as stack:
            self.stacklist = [line.strip() for line in stack if line.strip() != ""]
        with open(donefile,"r") as done:
            self.donelist = [line.strip() for line in done if line.strip() != ""]
            
    def save(self):
        with open(self.stackfile,"w") as stack:
            stack.write("\n".join([l for l in self.stacklist]))
        with open(self.donefile,"w") as done:
            done.write("\n".join([l for l in self.donelist]))
    
    def end(self):
        self.save()
        self.outputb.close()
        
    def extractNames(self,strd):
        a = re.findall("\[\[([^|^\]]*?)\|.*?\]\]",strd)
        b = re.findall("\[\[([^|]*?)\]\]",strd)
        return a + b
        
    def crawl(self, name):
        print "Crawling "+name
        out = []
        page = json.load(urllib2.urlopen('https://en.wikipedia.org/w/api.php?action=query&titles='+urllib2.quote(name)+'&prop=revisions&rvprop=content&format=json'))
        try:
            if "-1" in page["query"]["pages"]:
                return []
            for pagekey in page["query"]["pages"]:
                wiki = page["query"]["pages"][pagekey]["revisions"][0]["*"]
                for key in ["associated_acts", "current_members", "past_members"]:
                    ass_act_d = re.search(key+"[\s]*=[\s]\{\{(.*?)\}\}",wiki, re.DOTALL)
                    if ass_act_d is None:
                        ass_act_d = re.search(key+"[\s]*=[\s](\[\[.*?\]\])",wiki)
                    if ass_act_d is not None:
                        out += self.extractNames(ass_act_d.group(1))
        except Exception:
            return []
        return out

    def isDone(self, name):
        for line in self.donelist:
            if name == line.strip():
                return True
                
    def getNext(self):
        return self.stacklist[0]
        
    def output(self,s):
        self.outputb.write(s)
        
    def addToStack(self, x):
        self.stacklist.append(x)
    
    def addToDone(self, x):
        self.donelist.append(x)
        
    def deleteFirstLine(self):
        self.stacklist = self.stacklist[1:]
        if len(self.stacklist) == 0:
            self.again = False
        
    
    def processNext(self):
        position = self.getNext()
        if self.isDone(position):
            print "Skip double"
            self.deleteFirstLine()
            return False
        assoc = self.crawl(position)
        for mus in assoc:
            mus = mus.encode("utf-8")
            if mus > position:
                self.output(position+"\t"+mus+"\n")
            else:
                self.output(mus+"\t"+position+"\n")
            self.addToStack(mus)
        #add to done
        self.addToDone(position)
        self.deleteFirstLine()
            
        
v = ArtistCrawler("output.txt","stack.txt","done.txt")
v.again = True
try:
    i = 0
    while v.again:
        if i%20:
            v.save()
        v.processNext()
        i+=1
except Exception:
    v.end()


        