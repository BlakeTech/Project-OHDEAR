# Project-OHDEAR
A script for compiling the latest information. in explicit designs on Danbooru.

OHDEAR, or as my friend suggested, but I like to rename as O.H.D.E.A.R, stands for Opensource Heuristic for the Determination of Explicit Artwork Ratios, is a Python script that is a complete rewrite of my original project written in Bash, for use in more OS'es. 

Differences in user execution compared to the first version include:
1. Options menu is now gone. Instead, from the GUI, just choose the file you want! No more hard-coding options into the script!
2. Less temporary files! Instead, everything is just contained within the script itself. Much cleaner when debugging, and should save on disk writes.
3. An actual GUI, instead of the old 90's-esque/automated phone answering system of "Press 1 to do X, Press 2 to do Y...."!

Note: If using the first version (Realistically, who am I kidding, no one is going to use this....), the same url files are cross compatible, with only a name change to series name instead, and are easy to set up. Just as long as you make sure the names are correct and exist on the website, you should be file.

Each file to source from should just contain the variable, I.E. the thing that changes, so the name of the character(s) you want to return. If it includes an identifier tag, for example in cases where character names can be used across multiple series, and they have a "\_(Series)" tag on the end, if it is a new file it has not seen before, it will prompt you to add one if required in-script, so no need to touch any of the files yourself.

Special note for Kancolle and Azur Lane searchers: There is a special extra flag for you to also get the results from Paizukan, and return results of bust size of all your favourite ships. But due to the owner of said website being a bit paranoid as of late, it is suggested that you only do this once every so often, in case they assume a DDOS. Mitigations are in place to only request the results when you choose to do so, and it's up to you to not be an arse and spam the server with requests by executing the script multiple times, and thus leading to the rest of us being unable to get the results.
