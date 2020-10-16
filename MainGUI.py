#!/usr/bin/python3

#Script written by JasperTecHK, find it on my github! (If you didn't...somehow....)
#TBF/H this entire script is a bodge. The first variant was too. But this is a larger bodge, since this is literally a person who has not looked at the manual and decided to build a web scraper.
#Then again, it is the same person that decided to build the first version in bash just so a certain someone could save time. So who's the idiot now, ha!
#...Get on with the script, instead of typing your comments, no one is going to see this anyways.
#...Please send help.
#O.H.D.E.A.R. Opensource Heuristics for the Determination of Explicit Artwork Ratios

#Defining all the libraries required.
from multiprocessing.dummy import Pool						#Parallel processing, using threads instead. Makes sense for this since task is IO bound? Needs rework if progbar is to be used. Managers or sommat.
import json									#Parsing the options menu.
import requests									#Web requests.
import time									#Time(r). Not necessary at all. Just for benchmarking.
import string									#Predefined list of characters. Used for alphanumeric translation. Also, just looks cleaner.
import pandas as pd								#Nonstandard Library. Excel processor.
from openpyxl import Workbook							#Nonstandard Library. Pandas augment?
import tkinter									#Nonstandard Library. Basic (RE:Ugly) GUI maker.
import PySimpleGUI as sg							#Nonstandard Library. Tkinter augment.

#Defining all the variables.
url = 'https://danbooru.donmai.us/counts/posts.json?tags='
bustsurl = 'https://paizukan.com/html/'
secend = '+rating:s'								#Pun. Second Ending.

#PySimpleGUI Themes
sg.theme('Purple')

#DEFining all the functions. Eh? Eh?
#... I'll show myself out.
def dirscan ():									#Directory Scan. Used to allow user to locate the file to scrape.
	layout = [[sg.Text('Which list would you like to scour?')],
		[sg.InputText(), sg.FileBrowse(file_types=(''), initial_folder='./url')],	#file_types here uses '' because I don't want to deal with cutting the file extention off, and the "All types", is really more of a ".", i.e. all files with an extention. Also, because I hate adding the extentions. F/Bite me. Note: Dev has been notified. Will be patched in next update, apparently. Woot!
		[sg.Button('Confirm'), sg.Button('Cancel')]]
	window = sg.Window('O.H.D.A.M.N.', layout)
	event, values = window.read()
	conf = 0
	loop = 0
	while conf == 0:
		if not values[0] and not event in (None, 'Cancel'):
			sg.popup('No file selected. Due to limitations of GUI, script must die.')	#Don't remember why it must die.
			exit()
		elif event in (None, 'Cancel'):
			sg.popup('User closed script. :(')
			exit()
		elif event == 'Confirm':
			sg.popup('Confirmed!')
			filechosen = values[0]
			conf = 1
	window.close()
	del window
	return filechosen

def setup (filechoice):								#Setup. Might not show up for the end user, depends if the file to scrape is on file.
	with open('Options.json') as f:
		data=json.load(f)
		filtchk=filechoice.split('/')[-1]
		busts, end = "", ""
		if filtchk in data["busts"]:
			busts = data["busts"][filtchk]
		if filtchk in data["ignored"]:
			end = ""
			progloop = 2
		elif filtchk in data["end"]:
			end = data["end"][filtchk]
			progloop = 2
		else:
			layout = [[sg.Text('Would you like to add any end tags to your list?')],
				[sg.InputText()],
				[sg.Button('Add this!'),sg.Button('Nope!')]]
			window = sg.Window('O.H.D.A.M.N.', layout)
			event, values = window.read()
			if event in (None,'Nope!'):
				sg.popup('Understood!')
				data["ignored"][str(filtchk)] = None
				with open('Options.json', 'w') as g:
					g.write(json.dumps(data, sort_keys=True, indent='\t', separators=(',', ': ')))
				end = ""
			elif event == 'Add this!':
				sg.popup('Added to the settings!')
				data["end"][str(filtchk)] = values[0]
				with open('Options.json', 'w') as g:
					g.write(json.dumps(data, sort_keys=True, indent='\t', separators=(',', ': ')))
				end = data["end"][filtchk]
			window.close()
			del window
		return busts, end

def reqParse (filechoice): 							#Requests url setup here. As well as anything else that happens to need cycles matching number of items in list.
	with open(filechoice) as r:
		query = []
		names = []
		count = int()
		for line in r:
			line = line.rstrip("\n")
			link = url + line + end
			query.append(link)
			names.append(line)
		count = len(query)
	return query, names, count

def reqParseS (infodmp):							#Appending "s" tag.
	query = []
	for line in infodmp:
		link = line + secend
		query.append(link)
	return query

def reqProc (toget):								 #Requests urls and processes it. Asyncronous Multiprocessing. The bodged way. Don't need BeautifulSoup when you can just request for the json, much less crap to sift out.
	response = requests.get(toget)
	response = response.text
	response = response.replace('{"counts": {"posts"', '').replace('}}', '').replace(':', '')
	return response

#def progBar ():
#	while not progstat = progtotal:
#If you're reading this, it's too late. I'm done. I can't take it anymore.
#Coincidentally, "If you're reading this, it's too late" is actually a pretty decent book. I suggest reading this.
#And a note to future me. READ A F#*$!NG TUTORIAL ON HOW TO PROGRAM (IN PYTHON), YOU TWIT.
#...Thank you all for coming to my talk. Have a wonderful rest of your day/evening/other temporal state. If you somehow reached here before reading the execution phase... Hi! and sorry about the future ramble. Or is it the past?

def reqProcB(tag):								#Requests Busts tag.
	if not tag == '':
		layout = [[sg.Text('Would you like to search for bust size too?')],
				  [sg.Button('Hell Yes!'), sg.Button('Nah...')]]
		window = sg.Window('O.H.D.A.M.N.', layout)
		event, garbval = window.read()
		if event in ('Hell Yes!'):
			sg.popup('Please use this responsibly, as to not DOS attack the server!')
			toget = bustsurl + tag
			bust = []
			cup = []
			did = '1'
			check1 = 'data-bust="'
			check2 = 'data-cup="'
			try:
				response = requests.get(toget)
				response.raise_for_status()			#untested, but in theory it should test for 401 (or other errors) and if true, send it to except.
				response = response.text
				time2 = time.time()
				for line in response.splitlines():
					chunk = line.split(' ')
					for i in chunk:
						if check1 in i:
							t1 = i.replace(check1, '').replace('"','')
							cup.append(t1)
						elif check2 in i:
							t1 = i.replace(check2, '').replace('"','')
							bust.append(t1)
				time2 = time.time() - time2
	                except requests.exceptions.HTTPError as err:		#Temp fix for errors, usually because no auth. Any others, then something's changed on their end.
				sg.popup('Paizukan has returned an error. Skipped. Error code ',err)
				did = '0'
				time = '0'
		elif event in (None, 'Nah...'):
			sg.popup('Alright then.')
			bust = []
			cup = []
			did = '0'
			time2 = '0'
		window.close()
		del window
	else:
		bust = []
		cup = []
		did = '0'
		time2 = '0'
	return bust, cup, did, time2

def convProc(v1, v2, v3):							#Convertion Process, for dictionary translation.
	purity = []
	nsfw = []
	convresult = []
	convdict = {}
	tempnum = 2
	tempalph = string.ascii_uppercase
	for i in tempalph:
		convdict[str(tempnum)] = i
		tempnum += 1
	convdict['0'] = 'AAA'
	convdict['1'] = 'AA'
	for j in v3:
		convresult.append(convdict.get(j , "The bust is over 9000! Invalid result!"))
	for t, p in zip(v1, v2):
		try:
			purity.append(str(int(p)/int(t)*100))
			nsfw.append(int(t)-int(p))
		except ZeroDivisionError:					#Divide-By-Zero catch. Prevents script from breaking by just forcing a 0.
			purity.append(int(0))
			nsfw.append(int(0))
			print('Warning. One (or more) of your links are invalid. Check result for any results with a purity of 0.')
	return purity, nsfw, convresult

def dictmerge(d1, d2, d3, d4, d5, d6, d7, ckval): 				#List Merge. Probably could do better, but it works as a sloppy/amateur workaround. Doesn't take long anyways.
	filetarget = filechoice.replace('url', 'results') + '.xlsx'
	h1 = ['Character Name']							#...There has to be a better way than this.
	h2 = ['Total']
	h3 = ['Pure']
	h4 = ['Bust Size']
	h5 = ['Bust Rank']
	h6 = ['Impure']
	h7 = ['Purity Ratio']
	wb=Workbook()
	ws=wb.active
	if ckval == '0':
		for item in zip(h1,h2,h3,h6,h7):
			ws.append(item)
		for item in zip(d1,d2,d3,d6,d5):
			ws.append(item)
	else:
		for item in zip(h1,h2,h3,h6,h4,h5,h7):
			ws.append(item)
		for item in zip(d1,d2,d3,d6,d4,d7,d5):
			ws.append(item)
	ws.auto_filter.ref = ws.dimensions
	wb.save(filetarget)

def main():
	#Script start!								Yes, I know the comments look awful. I also know there's no reason to have all these comments. I got bored, okay? OKAY?!?!?!
	filechoice = dirscan()							#Initial directory Check
	time1 = time.time()							#Duration timer. Might be removed for compiled version.
	busts, end = setup(filechoice)						#Setting up the extra bits.
	query1, list1, total = reqParse(filechoice)				#Requests Parsing. i.e. prepping for requests to use, as well as anything that happens to need a loop equal to the number of things in the list. Asycry = Asyncronous requests (crying)
	asycry = Pool()								#Multithreading.
	#progbar()								#6th attempt at this. This will work. It has to. IT JUST *#$%ING HAS TO. IT'S NOT EVEN CONNECTED TO ANYTHING REAL. PLEASE JUST F*#$!NG WORK. AHHHHHHHHHHHHHHH......
	list2= asycry.map(reqProc, query1)					#Multithreaded processing here. I know it doesn't use process, or pool, it uses threads.... Maybe?
	list2 = list(list2)							#Re-sorting into list.
	query2 = reqParseS(query1)						#Appending the requests list. I'm lazy, so I'm just going to reuse the prior requests function.
	list3 = asycry.map(reqProc, query2)					#See above.
	list3 = list(list3)							#See three lines above.
	time1 = time.time() - time1						#Time break. User input delay will not be counted. Also, only reason why I'm doing this is to benchmark against my bash script.
	conv1, list4, didchk, time2 = reqProcB(busts)				#Busts check. It's all about dem tiddies, innit. *sigh.*
	time3 = time.time()							#Retriggering time check
	list5, list6, list7 = convProc(list2, list3, conv1)			#Conversion and calculation.
	dictmerge(list1, list2, list3, list4, list5, list6, list7, didchk)	#This is used to merge it all together. The lists hold these values: 1. Name, 2. Total., 3.Pure, 4. BustSize, 5.Purity%, 6. Impure count, 7.Alphanumeric translation.
	time3 = time.time() - time3						#End of timecheck. Script is basically over.
	time2 = round(int(time2))						#This is a joke. This float is too short, so it ends up not even mattering, unless really, REALLY large numbers. Which is basically not happening.
	time1 = round(time1)							#Time crunching.
	time3 = round(time3)							#Read above. Side note, I wonder how much larger I've made the script size because of all the tabs....
	timetotal = time2 + time1 + time3					#Final calculation.
	sg.popup('Done! Now go check your results!')				#No comment necessary. < READ WHAT YOU JUST TYPED IN, DUMMY. *smack*
	print('Finished in', timetotal,'.')					#Felt cute. Might remove later. *cries in cringe*
	print('Dansource:', time1,'Tiddies:', time2, 'Combine:', time3)

if __name__ == "__main__":
    main()									#I caved. Setting up Main. Probably for the best.


#Todo: 
#Progbar - Requires below.
#Manager Multiprocessing. - Not started.
#Autogen search strings based on series. - Got the endlink. Requires filtering, but no filter can do so due to the nature of danbooru's tagging system. So, possible solution, use it as a way to allow users to manually filter it.
#Json-ify settings, to allow for cheating in end-tagging on specifics. I.e. some series may have characters that do require the ending tag, others don't. The jsonification allows it to take the namelist, and standardize it. Possibly by writing the tags directly, to prevent having to go through that allocation over and over. Can be done now, but is undecided. PLus, the time it takes is so short anyways.

