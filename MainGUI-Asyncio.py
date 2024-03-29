#!/usr/bin/python3

# Script written by JasperTecHK, find it on my github! (If you didn't...somehow....)
# TBF/H this entire script is a bodge. The first variant was too. But this is a larger bodge, since this is literally a person who has not looked at the manual and decided to build a web scraper.
# Then again, it is the same person that decided to build the first version in bash just so a certain someone could save time. So who's the idiot now, ha!
# ...Get on with the script, instead of typing your comments, no one is going to see this anyways.
# ...Please send help.
# O.H.D.E.A.R. Opensource Heuristics for the Determination of Explicit Artwork Ratios

# Defining all the libraries required.
import sys  # Proper exiting.
import requests  # Web requests.
import asyncio  # Multithreading.
import aiohttp  # Multithreading, ASyncio Augment, Nonstandard Library.
import json  # Options parser.
import time  # Timer. Just for benchmarking.
import PySimpleGUIWx as sg  # WX wrapper. Nonstandard Library.
from openpyxl import Workbook  # Xlmx file creator/editor. Nonstandard Library.

# PySimpleGUI Theme
sg.theme("Purple")


# DEFining all the functions. Eh? Eh?
# ... I'll show myself out.
def endfind():
    danend = "https://danbooru.donmai.us/related_tag?search[category]=4&limit=500&search[query]="
    endtagstat = sg.popup_yes_no(
        "Do you have a list of the names of characters? If no, we can get that for you. But it will require manual filtering."
    )
    if endtagstat == "Yes":  # Check endtag status, if we have it or not.
        sg.popup("Okay. Moving on to series check.", title="O.H.D.E.A.R.")
    elif endtagstat == None:
        sg.popup("User closed script. :(", title="O.H.D.E.A.R.")
        sys.exit()
    else:
        # If no, we grab it but the data's messy, due to the nature of user-tagging. Best we can do, considering there is no definitive standard for fandom pages on characters, the closest thing to a central source.
        endtagstat = sg.popup_get_text(
            "Okay, type in the series name. Put an underscore, _, in place of spaces."
        )
        if endtagstat == None or endtagstat == "":
            sg.popup("User closed script. :(", title="O.H.D.E.A.R.")
            sys.exit()
        else:
            with open(endtagstat + ".txt", "w") as endsave:
                endtagstat = requests.get(danend + endtagstat)
                endsave.write(endtagstat.text)
            sg.popup(
                "Saved the results. Process them as needed, then return! Move the result into the url folder, due to OS differences, this is not able to be auutomated.",
                title="O.H.D.E.A.R.",
            )
            sys.exit()


def dirscan():  # Directory Scan. Used to allow user to locate the file to scrape.
    layout = [
        [sg.Text("Which list would you like to scour?")],
        [sg.InputText(), sg.FileBrowse(file_types=(""), initial_folder="./url")],
        [sg.Button("Confirm"), sg.Button("Cancel")],
    ]
    window = sg.Window("O.H.D.A.M.N.", layout)
    while True:
        event, values = window.read()
        if not values[0] and not event in (None, "Cancel"):
            sg.popup("No file selected. Please select a file!", title="O.H.D.E.A.R.")
        elif event in (None, "Cancel"):
            sg.popup("User closed script. :(", title="O.H.D.E.A.R.")
            sys.exit()
        elif event == "Confirm":
            sg.popup("Confirmed!", title="O.H.D.E.A.R.")
            filechosen = values[0]
            break
    window.close()
    del window
    return filechosen


def setup(
    filechoice,
):  # Setup. Might not show up for the end user, depends if the file to scrape is on file.
    with open("Options.json") as f:
        data = json.load(f)
        if "/" in filechoice:
            filtchk = filechoice.split("/")[-1]  # OS logic, without the os library!
        elif "\\" in filechoice:
            filtchk = filechoice.split("\\")[-1]
        else:  # Just in case. Not really something I expect will occur, but hey.
            sg.popup("No idea what OS you're using. to be safe, the script will die.")
            sys.exit()
        busts, end = "", ""
        if filtchk in data["busts"]:
            busts = data["busts"][filtchk]
        if filtchk in data["ignored"]:
            end = ""
        elif filtchk in data["end"]:
            end = data["end"][filtchk]
        else:
            layout = [
                [sg.Text("Would you like to add any end tags to your list?")],
                [sg.InputText()],
                [sg.Button("Add this!"), sg.Button("Nope!")],
            ]
            window = sg.Window("O.H.D.A.M.N.", layout, finalize=True)
            event, values = window.read()
            if event in (None, "Nope!"):
                data["ignored"][str(filtchk)] = None
                end = ""
            elif event == "Add this!":
                data["end"][str(filtchk)] = values[0]
                end = data["end"][filtchk]
            with open("Options.json", "w") as g:
                g.write(
                    json.dumps(
                        data, sort_keys=True, indent="\t", separators=(",", ": ")
                    )
                )
                sg.popup("Settings saved!", title="O.H.D.E.A.R.")
            window.close()
            del window
        return busts, end


def reqParse(
    filechoice, end
):  # Requests url setup here. As well as anything else that happens to need cycles matching number of items in list.
    url = "https://danbooru.donmai.us/counts/posts.json?tags="
    with open(filechoice, "r") as r:
        query = []
        names = []
        for line in r:
            line = line.rstrip("\n")  # Easier to read. Can be merged to lower line.
            link = url + line + end
            query.append(link)
            names.append(line)
    return query, names


async def Asyncquery(
    querylist,
):  # No progress bar on this version, it runs too quick to need it.
    srclist = []  # Making a copy just in case instead of referring back to it.
    list2t = []
    list3t = []
    list4t = []
    for i in range(0, len(querylist), 8):
        srclist += [querylist[i : i + 8]]
    async with aiohttp.ClientSession() as session:
        for urlset in srclist:
            for iter in range(2):
                # So... to explain the clusterfuck below... I don't even know where to start. Just don't look at it directly in the eye.
                # 1. Loops through and gets all the info into a list. 2. Requests the actual info instead of asyncio data and saves it to a list. 3. Cleans up the string and saves it into a list as a int. Stages are by each for loop.
                results = [
                    clnstr.split(":")[2].replace("}}", "")
                    for clnstr in [
                        await retxt.text()
                        for retxt in await asyncio.gather(
                            *(session.get(url) for url in urlset)
                        )
                    ]
                ]  # Holy fuck this is the longest, ugliest list comprehension I have done. Really emphasizes the "comprehension" part of it.
                # temp1 = await asyncio.gather(*(session.get(url)for url in urlset))
                # temp2 = [await retxt.text() for retxt in temp1]
                # results = [clnstr.split(":")[2].replace("}}","") for clnstr in temp2]
                if iter == 0:
                    list2t += results.copy()
                    urlset = [i + "+rating:s" for i in urlset]
                else:
                    list3t += results.copy()
            await asyncio.sleep(1)
    return list2t, list3t


def reqProcB(tag):  # Requests Busts tag.
    bust = []  # Alphabet
    cup = []  # Raw Number
    did = False
    """
	if not tag == '':
		layout = [[sg.Text('Would you like to search for bust size too?')],
			[sg.Button('Hell Yes!'), sg.Button('Nah...')]]
		window = sg.Window('O.H.D.A.M.N.', layout, finalize=True)
		event, garbval = window.read()
		if event in ('Hell Yes!'):
			sg.popup_quick_message('Please use this responsibly, as to not DOS attack the server!')
			bustsurl = 'https://paizukan.com/html/'
			toget = bustsurl + tag
			check = []
			check1 = 'data-bust="'							#rating, numerically
			try:
				response = requests.get(toget, allow_redirects=False)
				redirchk = str(response)					#Untested, but in theory it should test for 401 (or other errors) and if true, send it to except.
				if "301" in redirchk:
					sg.popup("Link no longer/doesn't exists. Skipping.")
				elif "401" in redirchk:
					sg.popup("Sign in required. Currently Unsupported.")
				else:
					did = True
					response = response.text
					check = [line for line in response.splitlines() if check1 in line]		#checking each line. I refuse to use beautifulsoup.
					for i in range(len(check)):			        #check now contains all the goodies, but has trash.
						hold = check[i].split(" d")		        #splits them into three.
						cup.append(re.sub("[^0-9]", "", hold[1]))       #getting the raw number.
						bust.append(hold[0].split(" ")[-1][:-1])        #getting the alphabetical designation.
			except:									#Temp fix for errors, usually because no auth. Anything else, they changed something on their end.
				sg.popup('Paizukan has returned an error. Skipped.', title='O.H.D.E.A.R.')
		elif event in (None, 'Nah...'):
			sg.popup('Alright then.', title="O.H.D.E.A.R.")
		window.close()
		del window
	else:
		sg.popup('Skipping bustcheck as it is unsupported.', title='O.H.D.E.A.R.')
	"""
    return bust, cup, did


def pureCalc(
    v1, v2
):  # Purity Calculation. Should be passed over to excel to deal with it, but alas.
    purity = []
    nsfw = []
    invalnk = False
    for t, p in zip(v1, v2):
        try:
            purity.append(str(int(p) / int(t) * 100))
            nsfw.append(str(int(t) - int(p)))
        except (
            ZeroDivisionError
        ):  # Divide-By-Zero catch. Prevents script from breaking by just forcing a 0.
            purity.append(int(0))
            nsfw.append(int(0))
            invalnk = True
    if invalnk:
        sg.popup(
            "Warning. One (or more) of your links are invalid. Check result for any results with a purity of 0.",
            title="O.H.D.E.A.R.",
        )
    return purity, nsfw


def dictmerge(
    d1, d2, d3, d4, d5, d6, d7, ckval, filechoice
):  # List Merge. Probably could do better, but it works as a sloppy/amateur workaround. Doesn't take long anyways.
    filetarget = filechoice.replace("url", "results") + ".xlsx"
    h1 = ["Character Name"]  # ...There has to be a better way than this.
    h2 = ["Total"]  # It's a list because for some reason, append only works with lists.
    h3 = [
        "Pure"
    ]  # Also, it must be seperate cause otherwise it just appends it one by one downwards.
    h4 = ["Bust Size"]
    h5 = ["Bust Rank"]
    h6 = ["Impure"]
    h7 = ["Purity Ratio"]
    wb = Workbook()
    ws = wb.active
    if not ckval:
        for item in zip(h1, h2, h3, h6, h7):
            ws.append(item)
        for item in zip(d1, d2, d3, d6, d5):
            ws.append(item)
    else:
        for item in zip(h1, h2, h3, h6, h4, h5, h7):
            ws.append(item)
        for item in zip(d1, d2, d3, d6, d4, d7, d5):
            ws.append(item)
    ws.auto_filter.ref = ws.dimensions
    while (
        True
    ):  # Just used to check if file is opened elsewhere, and waits until it's been closed.
        try:
            endrez = open(filetarget, "r+")
            break
        except IOError as e:
            if (
                e.errno == 2
            ):  # File doesn't exist. That's fine, as we are making it next.
                break
            elif (
                e.errno == 13
            ):  # Permission denied. Most likely because it's opened elsewhere.
                sg.popup(
                    "Permission denied. Is the file still open? And are you allowed to add new files to the folder?"
                )
            else:  # Should cover my other bases.
                sg.popup("Unknown error. Fault follows: ", e)
                sys.exit()
    wb.save(filetarget)


def main():
    # 	Script start!									Yes, I know the comments look awful. I also know there's no reason to have all these comments. I got bored, okay? OKAY?!?!?!
    endfind()  # Checks if the series is on record.
    filechoice = dirscan()  # Series Selector.
    time1 = time.time()  # Duration timer. Might be removed for compiled version.
    busts, end = setup(filechoice)  # Setting up the extra bits.
    query, list1 = reqParse(
        filechoice, end
    )  # Requests Parsing. i.e. prepping for requests to use.
    list2, list3 = asyncio.run(
        Asyncquery(query)
    )  # Progress bar not needed, moves far too quick for it.
    time1 = (
        time.time() - time1
    )  # Time break. User input delay will not be counted. Also, only reason why I'm doing this is to benchmark against my bash script.
    list7, list4, didchk = reqProcB(
        busts
    )  # Busts check. It's all about dem tiddies, innit. *sigh.*
    time2 = time.time()  # Retriggering time check
    list5, list6 = pureCalc(list2, list3)  # Purity calculation.
    dictmerge(
        list1, list2, list3, list4, list5, list6, list7, didchk, filechoice
    )  # This is used to merge it all together. The lists hold these values: 1. Name, 2. Total, 3.Pure count, 4. BustSize, 5.Purity%, 6. Impure count, 7.Alphanumeric translation.
    time2 = time.time() - time2  # End of timecheck. Script is basically over.
    time1 = round(time1)  # Time crunching.
    time2 = round(
        time2
    )  # Read above. Side note, I wonder how much larger I've made the script size because of all the tabs....
    timetotal = time1 + time2  # Final calculation.
    sg.popup(
        "Done! Now go check your results!"
    )  # No comment necessary. < READ WHAT YOU JUST TYPED IN, DUMMY. *smack*
    print(
        "Finished in", timetotal, "seconds."
    )  # Felt cute. Might remove later. *cries in cringe*


if __name__ == "__main__":
    main()  # I caved. Setting up Main. Probably for the best.
    # Spontaneous failures. Main messed stuff up.

# Todo:
# Json-ify settings, to allow for cheating in end-tagging on specifics. I.e. some series may have characters that do require the ending tag, others don't. The jsonification allows it to take the namelist, and standardize it. Possibly by writing the tags directly, to prevent having to go through that allocation over and over. Can be done now, but is undecided. PLus, the time it takes is so short anyways.
