#!/usr/bin/python3

#Script written by JasperTecHK, find it on my github! (If you didn't...somehow....)
#TBF/H this entire script is a bodge. The first variant was too. But this is a larger bodge, since this is literally a person who has not looked at the manual and decided to build a web scraper.
#Then again, it is the same person that decided to build the first version in bash just so a certain someone could save time. So who's the idiot now, ha!
#...Get on with the script, instead of typing your comments, no one is going to see this anyways.
#...Please send help.
#O.H.D.E.A.R. Opensource Heuristics for the Determination of Explicit Artwork Ratios

#Defining all the libraries required.
import re
from multiprocessing import Pool, Value						#Parallel processing. AsyncIO is massively slower in testing. And returns garbage data. For now, using this.
import json									#Parsing the options menu.
import requests									#Web requests.
import time									#Time(r). Not necessary at all. Just for benchmarking.
import tkinter									#Basic (RE:Ugly) GUI maker.
import PySimpleGUI as sg							#Nonstandard Library. Tkinter augment.
import pandas as pd								#Nonstandard Library. Excel Processor.
from openpyxl import Workbook							#Nonstandard Library. Pandas Augment.

#PySimpleGUI Themes
sg.theme('Purple')

#DEFining all the functions. Eh? Eh?
#... I'll show myself out.
def endfind ():
	danend = 'https://danbooru.donmai.us/related_tag?search[category]=4&limit=500&search[query]='
	endtagstat = sg.popup_yes_no('Do you have a list of the names of characters? If no, we can get that for you. But it will require manual filtering.')
	if endtagstat == 'Yes':							#Check endtag status, if we have it or not.
		sg.popup('Okay. Moving on to series check.')
	else:									#If no, we grab it but the data's messy. IT's also currently not cleaned up.
		endtagstat = sg.popup_get_text('Okay, type in the series name. Put an underscore, _, in place of spaces.')
		if endtagstat == None or endtagstat:
			exit()
		else:
			endsaven = endtagstat
			endtagstat = danend + endtagstat
			endtagstat = requests.get(endtagstat)
			endtagstat = endtagstat.text
			endsave = open(endsaven, 'w')
			endsave.write(endtagstat)
			sg.popup('Saved the results. Process them as needed, then return! Move the result into the url folder, due to OS differences, this is not able to be auutomated.')
			exit()

def dirscan ():									#Directory Scan. Used to allow user to locate the file to scrape.
	layout = [[sg.Text('Which list would you like to scour?')],
		[sg.InputText(), sg.FileBrowse(file_types=(''), initial_folder='./url')],
		[sg.Button('Confirm'), sg.Button('Cancel')]]
	window = sg.Window('O.H.D.A.M.N.', layout)
	event, values = window.read()
	conf = False
	while not conf:
		if not values[0] and not event in (None, 'Cancel'):
			sg.popup('No file selected. Due to limitations of GUI, script must die.')	#Confirming without selecting file causes the death. Due to poor looping, it causes it to spiral infinitely. 
			exit()
		elif event in (None, 'Cancel'):
			sg.popup('User closed script. :(')
			exit()
		elif event == 'Confirm':
			sg.popup('Confirmed!')
			filechosen = values[0]
			conf = True
	window.close()
	del window
	return filechosen

def setup (filechoice):								#Setup. Might not show up for the end user, depends if the file to scrape is on file.
	with open('Options.json') as f:
		data=json.load(f)
		if '/' in filechoice:
			filtchk=filechoice.split('/')[-1]				#Shit. Just realised this is os-specific. Though....
		elif '\\' in filechoice:
			filtchk=filechoice.split('\\')[-1]				#That should fix the above. Assuming the escape escapes properly.
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
				with open('Options.json') as g:
					g.write(json.dumps(data, sort_keys=True, indent='\t', separators=(',', ': ')))
				end = ""
			elif event == 'Add this!':
				sg.popup('Added to the settings!')
				data["end"][str(filtchk)] = values[0]
				with open('Options.json') as g:
					g.write(json.dumps(data, sort_keys=True, indent='\t', separators=(',', ': ')))
				end = data["end"][filtchk]
			window.close()
			del window
		return busts, end

def reqParse (filechoice,end): 							#Requests url setup here. As well as anything else that happens to need cycles matching number of items in list.
	url = 'https://danbooru.donmai.us/counts/posts.json?tags='
	with open(filechoice, 'r') as r:
		query = []
		names = []
		for line in r:
			line = line.rstrip("\n")
			link = url + line + end
			query.append(link)
			names.append(line)
	return query, names

def reqParseS (infodmp):							#Appending "s" tag.
	secend = '+rating:s'
	query = []
	for line in infodmp:
		link = line + secend
		query.append(link)
	return query

def reqProc (toget):								#Requests urls and processes it. Asyncronous Multiprocessing. The bodged way. Don't need BeautifulSoup when you can just request for the json, much less crap to sift out.
	response = requests.get(toget)
	response = response.text
	response = int(response.replace('{"counts": {"posts"', '').replace('}}', '').replace(':', ''))
	return response

def progbar (querylist):
	count = 0
	result = []
	layout = [[sg.Text('Getting the latest info for you...')],
		[sg.ProgressBar(len(querylist), orientation='h', size=(20, 20), key='progbar')],
		[sg.Cancel()]]
	window = sg.Window('Processing...', layout)
	asycry = Pool()
	for i in asycry.imap(reqProc, querylist):
		event, values = window.read(timeout=0)
		if event == 'Cancel' or event == sg.WIN_CLOSED:
			sg.popup("Aborting script.")
			exit()
		count += 1
		window['progbar'].update_bar(count)
		result.append(i)
	window.close()
	asycry.close()								#Best practices to avoid memory leaks, or sommat.
	asycry.join()
	return result

#It took 7 different attempts. It's finally working! ^

def reqProcB(tag):								#Requests Busts tag.
	if not tag == '':
		layout = [[sg.Text('Would you like to search for bust size too?')],
				  [sg.Button('Hell Yes!'), sg.Button('Nah...')]]
		window = sg.Window('O.H.D.A.M.N.', layout)
		event, garbval = window.read()
		bust = []	#Alphabet
		cup = []	#Raw number
		did = '0'
		if event in ('Hell Yes!'):
			sg.popup('Please use this responsibly, as to not DOS attack the server!')
			bustsurl = 'https://paizukan.com/html/'
			toget = bustsurl + tag
			check = []
			check1 = 'data-bust="'					#rating, numerically
			try:
				response = requests.get(toget)
				response.raise_for_status()			#untested, but in theory it should test for 401 (or other errors) and if true, send it to except.
				did = '1'
				response = response.text
				for line in response.splitlines():		#checking each line. I refuse to use beautifulsoup.
					if check1 in line:
						check.append(line)
				for i in range(len(check)):			#check now contains all the goodies, but has trash.
					hold = check[i].split(" d")		#splits them into three.
					cuptemp = re.sub("[^0-9]", "", hold[1]) #getting the raw number.
					cup.append(cuptemp)
					bustemp = hold[0].split(" ")[-1][:-1]	#getting the alphabetical designation.
					bust.append(bustemp)
			except requests.exceptions.HTTPError as err:		#Temp fix for errors, usually because no auth. Anything else, they changed something on their end.
				sg.popup('Paizukan has returned an error. Skipped. Error code ',err)
		elif event in (None, 'Nah...'):
			sg.popup('Alright then.')
		window.close()
		del window
	else:
		sg.popup('Skipping bustcheck as is unsupported.')
	return bust, cup, did

def pureCalc(v1, v2):							#Convertion Process, for dictionary translation.
	purity = []
	nsfw = []
	for t, p in zip(v1, v2):
		try:
			purity.append(str(p/t*100))
			nsfw.append(t-p)
		except ZeroDivisionError:					#Divide-By-Zero catch. Prevents script from breaking by just forcing a 0.
			purity.append(int(0))
			nsfw.append(int(0))
			print('Warning. One (or more) of your links are invalid. Check result for any results with a purity of 0.')
	return purity, nsfw

def dictmerge(d1, d2, d3, d4, d5, d6, d7, ckval,filechoice): 			#List Merge. Probably could do better, but it works as a sloppy/amateur workaround. Doesn't take long anyways.
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
	#Script start!									Yes, I know the comments look awful. I also know there's no reason to have all these comments. I got bored, okay? OKAY?!?!?!
	endfind()									#Checks if the series is on record.
	filechoice = dirscan()								#Series Selector.
	time1 = time.time()								#Duration timer. Might be removed for compiled version.
	busts, end = setup(filechoice)							#Setting up the extra bits.
	query1, list1 = reqParse(filechoice,end)					#Requests Parsing. i.e. prepping for requests to use, as well as anything that happens to need a loop equal to the number of things in the list. Asycry = Asyncronous requests (crying)
	list2 = progbar(query1)							#7th time's the charm. Or something.
	list2 = list(list2)								#Re-sorting into list.
	query2 = reqParseS(query1)							#Appending the requests list. I'm lazy, so I'm just going to reuse the prior requests function.
	list3 = progbar(query2)							#Taking over by combining the map with the bar.
	list3 = list(list3)								#See three lines above.
	time1 = time.time() - time1							#Time break. User input delay will not be counted. Also, only reason why I'm doing this is to benchmark against my bash script.
	list7, list4, didchk = reqProcB(busts)						#Busts check. It's all about dem tiddies, innit. *sigh.*
	time2 = time.time()								#Retriggering time check
	list5, list6 = pureCalc(list2, list3)				#Conversion and calculation.
	dictmerge(list1, list2, list3, list4, list5, list6, list7, didchk, filechoice)	#This is used to merge it all together. The lists hold these values: 1. Name, 2. Total., 3.Pure, 4. BustSize, 5.Purity%, 6. Impure count, 7.Alphanumeric translation.
	time2 = time.time() - time2							#End of timecheck. Script is basically over.
	time1 = round(time1)								#Time crunching.
	time2 = round(time2)								#Read above. Side note, I wonder how much larger I've made the script size because of all the tabs....
	timetotal = time1 + time2							#Final calculation.
	sg.popup('Done! Now go check your results!')					#No comment necessary. < READ WHAT YOU JUST TYPED IN, DUMMY. *smack*
	print('Finished in', timetotal,'.')						#Felt cute. Might remove later. *cries in cringe*

if __name__ == "__main__":
    main()										#I caved. Setting up Main. Probably for the best.
											#Spontaneous failures. Main messed stuff up.

#Todo:
#Json-ify settings, to allow for cheating in end-tagging on specifics. I.e. some series may have characters that do require the ending tag, others don't. The jsonification allows it to take the namelist, and standardize it. Possibly by writing the tags directly, to prevent having to go through that allocation over and over. Can be done now, but is undecided. PLus, the time it takes is so short anyways.
