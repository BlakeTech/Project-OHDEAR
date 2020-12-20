# Project-OHDEAR
A script for compiling the latest information in explicit designs on Danbooru.

OHDEAR, or as my friend suggested, but renamed as O.H.D.E.A.R, stands for Opensource Heuristic for the Determination of Explicit Artwork Ratios, is a Python script that is a complete rewrite of my original project written in Bash, for use in more OS'es. 

Start Guide: All you need is four things. The first three are given, but the fourth is a folder called 'results'. After that, you may need to chmod +x the script.

~~For Linux users, there is a compiled version for you. You still need the options.json, but you can supply your own URLs and results folder. For Windows users... WSL?~~
^Not up to date, have not bothered recompiling it.

Each file to source from should just contain the variable, I.E. the thing that changes, so the name of the character(s) you want to return. If it includes an identifier tag, for example in cases where character names can be used across multiple series, and they have a "\_(Series)" tag on the end, if it is a new file it has not seen before, it will prompt you to add one if required in-script, so no need to touch any of the files yourself. -- Note, this is most likely going to be changed.

Special note for Kancolle and Azur Lane searchers: There is a special extra flag for you to also get the results from Paizukan, and return results of bust size of all your favourite ships. But due to the owner of said website being a bit paranoid, it is suggested that you only do this once every so often, in case they assume a (D)DOS. Basic mitigations are in place to only request the results when you choose to do so, and it's up to you to not be an arse and spam the server with requests by executing the script multiple times, and thus leading to the rest of us being unable to get the results.

Original version: https://github.com/JasperTecHK/Danbooru-comparator-script

Note: Asyncio is the only one going forward that will get updates, since it's the fastest.

Required extra libraries: aiohttp, WxPython, PySimpleGUIWx, Pandas(Maybe?), openpyxl.
