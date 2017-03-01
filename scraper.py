import urllib2
import csv
from bs4 import BeautifulSoup

mainPageUrl = "http://leagueoflegends.wikia.com/wiki/League_of_Legends_Wiki"
mainPage = urllib2.urlopen(mainPageUrl)

mainPageSoup = BeautifulSoup(mainPage, "html.parser")

baseUrl = "http://leagueoflegends.wikia.com"

csvfile = open('skins.csv', 'wb')
csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='\'', quoting=csv.QUOTE_MINIMAL)

def nsToS(ns):
	return unicode(ns).encode('ascii','replace')

def getSkinsFromGallery(gallery, champName, typeName):
	for skin in gallery.find_all('div', class_="lightbox-caption"):
		name = nsToS(skin.contents[0]).strip()
		rp = 0
		date = ""
		r = skin.find('div', style="float:right")
		if r.span:
			if r.span.a.next_sibling:
				rp = int(unicode(r.span.a.next_sibling))
			else:
				rp = int(unicode(r.span.previous_sibling))
			date = nsToS(r.span.next_sibling)[3:]
		else:
			date = nsToS(r.string).split("/")[-1].replace('?','')
		# print champName, name, str(rp), date, typeName
		csvwriter.writerow([champName, name, str(rp), date, typeName])


def getChampSkins(champSkinsSoup, champName):
	for span in champSkinsSoup.findAll('span'):
		if span.parent.name == 'h2':
			if span.string in ['Available', 'Legacy', 'Limited Edition']:
				typeString = nsToS(span.string)
				getSkinsFromGallery(span.parent.next_sibling.next_sibling, champName, typeString)
			elif span.string not in ['Screenshots', 'References', 'Chroma Packs']:
				print span.string

for tag in mainPageSoup.find("ol", class_="champion_roster").find_all('a'):
	champName = tag['href'].split('/')[2].encode('ascii','replace').strip()
	champSkinsUrl = baseUrl + tag['href'] + "/Skins"
	champSkinsSoup = BeautifulSoup(urllib2.urlopen(champSkinsUrl), "html.parser")
	getChampSkins(champSkinsSoup, champName)

csvfile.close()
print "done"