from pyquery import PyQuery as pq
import os
import sys
import datetime
import time
import string

PHANTOMJS_PATH = "./bin/phantomjs"
RES_DIR = "res"

def generate_js(year, month, day, topic, page=1):
    #print page
    JS = "var page = require('webpage').create(),\n"
    JS = JS + "url = \'http://query.nytimes.com/search/sitesearch/#/" + topic 
    JS = JS + "/from" + year + month + day + "to" + year + month + day
    JS = JS + "/allresults/" + str(page) + "/allauthors/oldest/\';\n"
    JS = JS + "page.settings.resourceTimeout = 10000;\n"
    JS = JS + "page.onResourceTimeout = function(e) {\n"
    JS = JS + "phantom.exit(1);"
    JS = JS + "};\n"

    JS = JS + "page.open(url, function (status) {\n"
    JS = JS + "    var js = page.evaluate(function () {\n"
    JS = JS + "        return document;\n"
    JS = JS + "    });\n"
    JS = JS + "console.log(js.all[0].outerHTML);\n"
    JS = JS + "phantom.exit();\n"
    JS = JS + "});\n"

    out_f = open("nyt.js", "w")
    out_f.write(JS)
    out_f.close()



def get_targets(year, month, day, topic, page):
    generate_js(year, month, day, topic, page)
    cmd = PHANTOMJS_PATH + " nyt.js > " + RES_DIR + "/" + year + "_" + month + "_"  + day + "_" + str(page) + ".html"
    print cmd
    os.system(cmd)


# return value tells if we have next page
def get_pages(input, topic, date):
    print "open ", input
    f = open(input, "r")
    html = f.read();
    f.close()
    if len(html) == 0:
        return False
    
    obj = pq(html)
    for item in obj.find("div.searchResults").children().children().find('a'):
        link = item.values()[0]
        title = escape_name(item.text_content())
        if "japan" in title.lower():
            print title
            fname = "\"" + RES_DIR + "/" + date + "_" + title + ".html\""
            download_link(link, fname, date)
            clean_content = get_clean_content(RES_DIR + "/" + date + "_" + title + ".html")
            out_f = open(RES_DIR + "/" + date + "_" + title + ".txt", "w")
            out_f.write(clean_content.encode('utf-8'))
            out_f.close()

    if len(obj.find("div.searchPagination").find('a.stepToPage.next')) > 0:
        return True
    else:
        return False



def download_link(url, fname, date):
    #items = url.split('/')
    #fname = ""
    #if "?" in items[len(items)-1]:
    #    fname = RES_DIR + "/" + date + "_" + items[len(items)-1].split("?")[0]
    #else:        
    #    fname = RES_DIR + "/" + date + "_" + items[len(items)-1]

    cmd = "wget \"" + url + "\" -O " + fname
    print cmd
    os.system(cmd)
    #return fname


def get_clean_content(input):
    print "input", input
    f = open(input, "r")
    html = f.read();
    f.close()

    obj = pq(html)
    title = obj.find("title")[0].text 
    content = title + "\n"

    body  = obj.find("div.articleBody").find('p').text()

    if body == None:
        body = obj.find("div.area").find('p').text()

    if body == None:
        body = obj.find("NYT_TEXT").find("p").text()

    if body != None:
        content = content + body

    return content 

def escape_name(orig):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in orig if c in valid_chars)


# here year/mon/day are numbers
def do_job(start_year, start_mon, start_day, end_year, end_mon, end_day, topic):
    cur_year = start_year
    cur_mon = start_mon
    cur_day = start_day
    lf = open("crawler.log", "w") 

    while True:     
        page = 1
        while True:
            generate_js(cur_year, cur_mon, cur_day, topic, page)
            get_targets(cur_year, cur_mon, cur_day, topic, page)
            if get_pages(RES_DIR + "/" + cur_year + "_" + cur_mon + "_"  + cur_day + "_" + str(page) + ".html", topic, cur_year + "_" + cur_mon + "_"  + cur_day):
                page = page + 1
            else:
                break
        
        print "finished " + cur_year + "_" + cur_mon + "_"  + cur_day
        lf.write("finished " + cur_year + "_" + cur_mon + "_"  + cur_day + "\n")
        lf.flush()
        cmd = "rm " + RES_DIR + "/" + cur_year + "_" + cur_mon + "_"  + cur_day + "_" + str(page) + ".html"
        os.system(cmd)
        #break
        #time.sleep(1)  
        

        if cur_year == end_year and cur_mon == end_mon and cur_day == end_day:
            break

        date = datetime.datetime(int(cur_year), int(cur_mon), int(cur_day))
        date += datetime.timedelta(days=1)
        date_str = str(date).split()[0].strip()
        items = date_str.split("-")
        cur_year = items[0]
        cur_mon = items[1]
        cur_day = items[2]

        
    lf.close()



do_job("2005", "01", "12", "2013", "12", "31", "japan")

#generate_js("1981", "01", "01",  "japan", 1)
#get_targets("1981", "01", "01",  "japan", 1)



