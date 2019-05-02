# Oblivio
Author: Simon Olofsson
dotchetter@protonmail.ch for Advania Sverige AB
Website: http://github.com/dotchetter

## Algorithm designed to fetch Chrome OS devices that lay unused beyond a certain timeframe. 

### Thank you 
Oblivio is a separate module that uses GAM by Jay Lee (https://github.com/jay0lee) to query the G suite domain for devices in the domain. Without his and fellow contributor's efforts, Oblivio would not exist in the way it does today in terms of simplicity and minimalistic approach. 

Any contribution and / or feedback to this project is more than welcome.

### Use case
The main goal with Oblivio is to create an automated way to list unused or forgotten CROS devices in your domain in a Google Sheet. This way you can save time and money in your organization with better transparency of how many CROS devies are actually used and which ones that can be repurposed or maybe even deprovisioned if they're lost or sold. 

Devices that have not been used for 10 days or more (by default - you can manually select the timedelta)
are added in an .xlsx document and uploaded to the designated users' drive.  

## Get started

### Prerequisites

* Install Python 3.6 or later
	Oblivio is developed in Python and needs python 3.6.0 at least to function.
	For help on upgrading Python3, refer to your OS vendor or community.

* Set up GAM
	Oblivio requires GAM to be installed on the machine to run correctly.
	This version of Oblivio is optimized for GAMADV-XTD, however the commands
	passed are very similar to the ones used in GAM, howerver function cannot be guaranteed.

* Create the Google Drive folder
	Oblivio will automatically upload the file generated to a "Oblivio" folder in 
	the users' Drive, if present. This is to ease the sharing concept of these files. With
	a shared folder, sharing becomes easy. Create a folder in the users' Drive called 'Oblivio'
	and the files will end up in there.

### Quickstart

* Run Oblivio
	Oblivio is run by the commandline. To use Oblivio, open your terminal and navigate
	to where Oblivio is residing on your machine. Example: 

		cd ~/Oblivio (presuming you put Oblivio in a folder called Oblivio in your Home folder)

	If you have everything set up, you can try and see the Help page by typing:

		./Oblivio -h

	This will show the built-in help, to guide you with the commands.
	A minimal command will look like this:

		./Oblivio <gampath> <outpath> <user> <optionals>

	### gampath
	This switch refers to the DIRECTORY where gam is installed. Do not type the entire path
	to GAM, but only the directory in which it resides.

	### outpath
	This switch refers to the DIRECTORY where Oblivio will output the inventory .xlsx file.		Again, only the directory needs to be typed here.

	### user
	This switch needs to be complete since GAMADV-XTD needs the full username for which 
	to upload the file to. Example: captain.kirk@ussenterprise.com

	### optionals
	These are optional switches you can use:
	
	-nofile (Automatically delete the inventory file from the filesystem after upload)
	
	-timedelta (Number of days for a device to lay unused in order for it to be included)
	
	-verbose (Get all the output from Oblivio in the terminal. No file is uploaded or created.)
	CAUTION! This may crash a terminal on a very large domain with many inactive devices.
