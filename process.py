from pyquery import PyQuery as pq


def get_pages(input, topic, date):
    f = open(input, "r")
    html = f.read();
    f.close()
    
    obj = pq(html)
    for item in obj.find("div.searchResults").children().children().find('a'):
	    link = item.values()[0]
	    if "japan" in link.lower():
		    print link
		    fname = download_link(link, date)
		    clean_content = get_clean_content(fname)
		    out_f = open(fname[:-4] + ".txt", "w")
		    out_f.write(clean_content)
		    out_f.clear()



def download_link(url, date):
	items = url.split('/')
	fname = date + "_" + items[len(items)-1]
	cmd = "wget " + url + " -O " + fname
	os.system(cmd)
	return fname


def get_clean_content(input):
    f = open(input, "r")
    html = f.read();
    f.close()

    obj = pq(html)
    content = obj.find("title")[0].text + "\n" + obj.find("div.articleBody").find('p').text()
    return content 


