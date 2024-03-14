# F-R-O-G Telegram scraping tool
#### Flexible Research-Oriented Gatherer for Telegram data samples


## Table of contents
1. [Features](#features)
2. [Background](#background)
3. [Getting Started](#getting-started)
4. [Usage Manual](#usage-manual)
-  [Telegram Scraper](#telegram-scraper)
-  [Name-Id-Mapper](#name-id-mapper)
-  [Data View](#data-view)
-  [Credential Handling](#credential-handling)
-  [Error Logging](#error-logging)
5. [Credits](#credits)

### Software presentation and software review of F-R-O-G in Mobile Media & Communication
- Link to paper coming here, soon

### Studies that used FROG (if you want your paper added here, send an e-mail to f.primig@fu-berlin.de)
- Primig, F. (2024). Thinking different as an act of resistance: Reconceptualizing the German protests in the COVID-19 pandemic as an emergent counter-knowledge order. Discourse & Society, 1–18. https://doi.org/10.1177/09579265241231593

## Features
#### Current
1. Save messages from public Telegram channels and group chats (complete channels or specified timeframe)
2. Map channel references (names, links, etc.) to channel IDs and vice versa
3. Export channel data as CSV (messages) or JSON files formats (messages, metadata)
4. Use multiple credentials/phone numbers to run multiple scrapers in parallell
5. Export Name-ID-Mappings as CSV file
6. Display messages of a channel

#### Ideas for future
1. Add customization options for outputs (placeholders in .csv files, timezones for message timestamps)
2. "Lightweight" scraping to limit necessary storage => Not all message fields are saved
3. Automatically scrape new messages continously into the future (e.g., once a day)
4. Enable support for Two-Factor-Authentication


## Background
### Motivation and idea
F-R-O-G stands for Flexible Research-Oriented Gatherer for Telegram data. We have built this program to enable researchers, especially those with limited capacity or training in building and maintaining data scraping scripts (e.g. students), to be able to gather Telegram channel data easy and safe. Telegram data has proven more important in recent years for social sciences as (fringe) groups migrated to the messenger service due to deplattforming on other platforms and as dominant platforms such as Facebook or Twitter have risen their hurdles to data access for most researchers. An easy, UI-based way to gather data from Telegram has thus become a matter of accessibility for the research community which we aim to aid here. The program is completely user-interface based, that is it requires no coding to gather data at all. F-R-O-G allows researchers to collect data of multiple channels by entering a channel link or list of channel links. It also saves the list of gathered channels, which makes monitoring of multiple channels over time easier. To make data processing more accessible, F-R-O-G allows researchers to export their data as CSV or JSON. The data can be used to subsequently conduct text-based analyses or render social-network graphs.

### Technologies used
The core of F-R-O-G is written in Python and builds up on the [telethon](https://docs.telethon.dev/en/stable/) package which offers an easy to use interface to the Telegram API. To create a GUI application, the [pywebview](https://pywebview.flowrl.com/) framework was chosen to enable the usage of HTML, CSS and JavaScript for the user interface. It hosts a local webserver for which the [Flask](https://flask.palletsprojects.com/en/2.3.x/) framework was used here, as well as a Chromium-based user interface window. [TinyDB](https://tinydb.readthedocs.io/en/latest/index.html) together with [tinydb-encrypted-jsonstorage](https://pypi.org/project/tinydb-encrypted-jsonstorage/) was used to save user and application data. Further, the [tendo](https://pypi.org/project/tendo/) package was used to add necessary functionality to Python and [PyInstaller](https://pyinstaller.org/en/stable/) was used to build a executable.

### Cite as
Fröschl, F., & Primig, F. (2023). F-R-O-G Telegram scraping tool (Version 1.0.0). https://github.com/Froschi1860/F-R-O-G-Telegram-scraping-tool/tree/main

## Getting started
### Register on Telegram and obtain API ID
To use the F-R-O-G scraping tool at least one account on Telegram account is necessary: Download the mobile Telegram application and follow the registration steps. Also, a Telegram API ID must be obtained. Information about this can be found [here](https://core.telegram.org/api/obtaining_api_id).  

### Download the executable and place in a new directory
The F-R-O-G scraping tool is a self-contained executable that works without an installation. Just download the latest version, place it in a new directory and start it. Placement in an empty directory is recommended since some folders and data will be created on setup at the execution location and cluttering other folders can be avoided thus.  

### Register credentials and authorize via Telegram mobile app
The last setup step is to register and authorize the credentials used for Telegram which is done in the Credentials tab in F-R-O-G. Enter and save your data, then press the authorize button. If all credentials were entered correctly you will receive a confirmation code in the mobile Telegram app which must be entered in F-R-O-G to verify yourself. Note that F-R-O-G currently does not support 2-Factor-Authorization!  

When the credentials were successfully authorized the setup is completed and the scraping can start. Please refer to the next section for detailed instructions.

## Usage manual
### Telegram Scraper
#### Starting the scraper
In order to retrieve messages from Telegram channels, at least one set of authorized credentials is necessary. If more than one set of credentials is saved and authorized, all these will automatically scrape channels in parallell which can speed up the scraping process considerably.  

To start a scraping job, channel references (channel names or valid links to a channel) are added to the scraper via the respective input field. For convenience, it is possible to use a .txt or a .csv file containing channel references to add them to the scraper queue. A scraper job is then started by clicking the "Start new scraper job" button. If a scraper job is already running, more references can be added in the same way, only the "Add to scraper queue" button must be used in this case. An approximate number of remaining jobs can be retrieved and the remaining jobs can be deleted via the respective buttons. Mind that deleting from the queue does not abort scraping the current channel(s)!  

The Active Scraper section gives information about a currently running scraping job. This section can also be used to abort running scrapers. Mind that aborting a runnning scraper only aborts the current channel and does not reset remaining channels in the worker queue. If the whole scraping job should be aborted, first delete the remaining jobs and then abort all running scrapers.

#### Scraper configuration
By default, F-R-O-G will retrieve all available messages from a given channel from its creation. This behaviour can be altered in the Scraper configuration section by providing a timeframe for the scraper. Also, a limit of X messages to be scraped per channel (multiple of 100) can be set which is the X latest messages on the channel.  

Mind that F-R-O-G remembers the last scraped message of any channel for optimization reasons. This means that if a channel was only partially scraped earlier, future scraping will exclude all messages from the first channel message to the latest message saved locally. This behaviour can be changed by using the configuration option to force scraping of the full channel which overrides all other configuration choices. For optimization reasons, this option should only be used when explicitly necessary. Changing the configuration is not possible while a scraping job is running.

### Name-ID-Mapper
F-R-O-G offers a function to retrieve a channel´s ID from one of its valid references or the correct channel name from a known ID. To use this tool, navigate to the Name-ID Mapper section, enter either a reference or an ID and press the corresponding button. Mind that a channel name can only be retrieved from an ID if the channel was found via a reference before. This function can only be used while no scraping job is running and requires at least one authorized set of credentials.

### Data View
All data retrieved with F-R-O-G can be accessed and exported in the Data View section. Channels can be displayed and deleted in the lower section. Mind that displaying channels with many messages takes time to render and thus may freeze the programm for some time! For further analysis it is thus recommended to export the data. Channel messages can be exported as either .csv or .json files while metadata can be exported only as .json files. A convenient option to export all channels at once exists. Mind that this option overwrites existing files in the output location!  

Further, offline metadata lookup for all channels that were scraped or mapped to an ID at least once is possible here, as well as exporting or deleting saved Name-ID-Mappings. Mind that exporting Name-ID-Mappings overwrites existing files!  

As of now, timestamps in the messages are converted into CET+02:00, "NA" is used as a placeholder for empty CSV fields, and flattened messages in CSV exports receive a "_" character as delimiter between parent and child sections of the types.

### Credential Handling
F-R-O-G enables to register multiple phone numbers to make parallell scraping possible. Each phone number must be linked to a Telegram account, unique, and have an individual API ID and API hash [(obtain as described here)](https://core.telegram.org/api/obtaining_api_id). Providing a username is necessary at this point to use the underlying technologies but it can be chosen freely and serves no specific purpose at this point. Before being available for scraping, each set of credentials must be authorized via the respective button. A code is sent to the Telegram mobile app for verification which must be entered in F-R-O-G to finish the authorization. Mind that as of now Two-Factor-Authentication with password is not supported.  

When trying to scrape too many channels in too short time Flood Wait Errors can occur which Telegram uses to avoid an overload of their API. F-R-O-G tries to avoid such errors but they may occur which leads to a phone number being unusable for scraping for a period of time. The credentials overview displays the end of the waiting time for a given phone number in case a Flood Wait Error occured. F-R-O-G automatically recognises when this waiting time is over and makes the phone number available again for scraping. Further, on startup F-R-O-G checks the authorization status for all registered credentials. Thus, usually an authorization must be only done once per phone number.

### Error Logging
Errors that occur on scraping and app-internally are saved in an error log which can be accessed and exported as s .csv file in the Error Log section.


## Credits
### Code Development
Copyright (c) 2023-Present Fabian Fröschl  
Fabian Fröschl [GitHub](https://github.com/Froschi1860)

### Project overview & research implementation
Florian Primig [FH Berlin](https://www.polsoz.fu-berlin.de/en/kommwiss/arbeitsstellen/digitalisierung_partizipation/team/fprimig/index.html)

### Licence notes of packages used
#### Telethon
Copyright (c) 2016-Present LonamiWebs  

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

#### Pywebview
Copyright (c) 2014-2017, Roman Sirokov  
All rights reserved.  

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#### Flask
Copyright 2010 Pallets  

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#### TinyDB
Copyright (C) 2013 Markus Siemens <markus@m-siemens.de>  

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#### TinyDB Encrypted JSON Storage
Copyright (c) 2020 Stefan Thaler  

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

- Frog icon
Icon made by Freepik from www.flaticon.com

