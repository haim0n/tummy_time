# Tummy Time
Food arrival stats analyser - say goodbye to guessing when's your next food delivery ETA.

## Installation

* Clone the repo `git clone git@github.com:haim0n/tummy_time.git`
* Install pip: `sudo yum install -y python-pip`
* Install all requirements: `sudo pip install -r tummy_time/requirements.txt`
* Follow **Step1 only** as described in [Google's Gmail API](https://developers.google.com/gmail/api/quickstart/python#prerequisites).
* **NOTE**: Download the JSON file from STEP1 to tummy_time/client_secret.json
    
## Getting Started
Refer to the utility's help:

```bash
$ tummy_time/tummy_time -h
usage: tummy_time [-h] [-Z] [-F] [-O OUTPUT_TO_FILE] [-L]
                  [-d DUMP_RESTAURANT_STATS]
Food arrival stats
optional arguments:
  -h, --help            show this help message and exit
  -Z, --init-db         purge all local data
  -F, --fetch-data      fetch data and populate local db with it
  -O OUTPUT_TO_FILE, --output-to-file OUTPUT_TO_FILE
                        dump db contents formatted as csv
  -L, --list-all-restaurants
                        shows a list of restaurants from local db
  -d DUMP_RESTAURANT_STATS, --dump-restaurant-stats DUMP_RESTAURANT_STATS
```

## Examples
*All examples assume you already setup your Gmail API!* 

Initialize (purge your local db)
```bash
$ tummy_time/tummy_time -Z
$ initializing DB
```

Fetch Gmail messages and populate local db
```bash
$ tummy_time/tummy_time -F
updating db
fetching data
fetched 153b7738d95d1ebd,2016-03-27 12:41:54,moses
fetched 153b7738d95d1ebd,2016-03-27 12:41:54,ahuzat hahumous
fetched 153b7738d95d1ebd,2016-03-27 12:41:54,hakalfi
fetched 153b74a0bab77382,2016-03-27 11:56:34,sushia
fetched 153a8ebe53389a72,2016-03-24 15:59:02,cafe neto
fetched 153a833d1dbee17e,2016-03-24 12:37:58,najima
fetched 153a83226f3da84a,2016-03-24 12:36:08,shnitzel zone
fetched 153a330145e685e7,2016-03-23 13:15:48,zozobra
fetched 153a3147c95f71a7,2016-03-23 12:45:40,sandwich factory
fetched 153a31393a2a0192,2016-03-23 12:44:38,najima
```

Dump all db contents to local csv file
```bash
$ tummy_time/tummy_time -O /tmp/out.csv
```

List all restaurants (only names) in db
```bash
$ tummy_time/tummy_time -L
ahuzat hahumous
baharat
bar bari
burgarim
burger bar
cafe neto
china class
domino's pizza
giraffe
```

Dump stats of a single restaurant and get an ETA
```bash
$ ./tummy_time/tummy_time -d 'najima'
15379c39d44c4e17,2016-03-15 12:12:53,najima
1537f05b6e5a15cb,2016-03-16 12:43:10,najima
1539dc1ea643ad8f,2016-03-22 11:57:22,najima
153a31393a2a0192,2016-03-23 12:44:38,najima
153a833d1dbee17e,2016-03-24 12:37:58,najima
--------------------------------------------------
estimation: 12:35:13
```
