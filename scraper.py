import urllib2
import csv
import datetime
from bs4 import BeautifulSoup

mainPageUrl = "http://leagueoflegends.wikia.com/wiki/League_of_Legends_Wiki"
mainPage = urllib2.urlopen(mainPageUrl)

mainPageSoup = BeautifulSoup(mainPage, "html.parser")

baseUrl = "http://leagueoflegends.wikia.com"

csvfile = open('skins.csv', 'wb')
csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

def nsToS(ns):
	return unicode(ns).encode('ascii','replace')

def formatS(s):
	return s.replace("_", " ").replace("%27", "'")

def getNextSibling(thing, n):
	if n == 0:
		return thing
	return getNextSibling(thing.next_sibling, n-1)

champSkinCount = {}
champSkinLatest = {}

def getSkinsFromGallery(gallery, champName, typeName):
	for skin in gallery.find_all('div', class_="lightbox-caption"):
		name = nsToS(skin.contents[0]).strip()
		rp = 0
		date = ""
		r = skin.find('div', style="float:right")
		if r.span:
			if r.span.a.next_sibling:
				rp = int(unicode(r.span.a.next_sibling.replace(',','')))
			else:
				rp = int(unicode(r.span.previous_sibling.replace(',','')))
			if rp == 10:
				# hextech stuff will have a ')?/?13-Apr-2017'
				date = nsToS(getNextSibling(r.span, 5)).replace(")","").replace("?","").replace("/","").strip()
			else:
				date = nsToS(r.span.next_sibling)[3:]
		else:
			date = nsToS(r.string).split("/")[-1].replace('?','')

		# Neo PAX Sivir
		if champName == "Sivir":
			date = date.replace("PAX Prime 2017", "")

		champSkinCount[champName] += 1
		if 'Upcoming' in date:
			dt = datetime.datetime.now()
		else:
			dt = datetime.datetime.strptime(date, '%d-%b-%Y')
		if champSkinLatest[champName] < dt:
			champSkinLatest[champName] = dt
		csvwriter.writerow([formatS(champName), name, str(rp), date, typeName])


def getChampSkins(champSkinsSoup, champName):
	for span in champSkinsSoup.findAll('span'):
		if span.parent.name == 'h2':
			if span.string in ['Available', 'Legacy', 'Limited Edition']:
				typeString = nsToS(span.string)
				getSkinsFromGallery(span.parent.next_sibling.next_sibling, champName, typeString)
			elif span.string not in ['Screenshots', 'References', 'Chroma Packs', 'Alternate Artwork']:
				print span.string

allChampNames = []
for tag in mainPageSoup.find("ol", class_="champion_roster").find_all('a'):
	champName = tag['href'].split('/')[2].encode('ascii','replace').strip()
	allChampNames.append(champName)
	champSkinCount[champName] = 0
	champSkinLatest[champName] = datetime.datetime(2000, 1, 6, 15, 8, 24, 78915)
	champSkinsUrl = baseUrl + tag['href'] + "/Skins"
	champSkinsSoup = BeautifulSoup(urllib2.urlopen(champSkinsUrl), "html.parser")
	getChampSkins(champSkinsSoup, champName)
	print "Done with " + champName

csvwriter.writerow([])
for n in allChampNames:
	csvwriter.writerow([formatS(n), champSkinCount[n], '{:%Y-%m-%d}'.format(champSkinLatest[n])])
print "Done writing stats"

csvfile.close()
print "done"