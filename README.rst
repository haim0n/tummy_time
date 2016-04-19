==========
Tummy Time
==========

Food delivery time analyser - say goodbye to guessing when's your next food delivery ETA.

* Free software: Apache license

Installation
------------
* Clone the repo: ``git clone git@github.com:haim0n/tummy_time.git``
* Install pip: ``sudo dnf install -y python-pip``
* Install all requirements: ``sudo python setup.py install``


Getting Started
---------------
Refer to the utility's help:::

        usage: tummy_time.py [-h] [-Z] [-F] [-q QUERY [QUERY ...]] [-e]
                             [--alias-create ALIAS_CREATE]
                             [--alias-delete ALIAS_DELETE] [--alias-list]
                             [-Q ALIAS_QUERY]

        Food arrival stats

        optional arguments:
          -h, --help            show this help message and exit
          -Z, --init-db         purge all local data
          -F, --fetch-data      fetch data and populate local db with it
          -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                                query the data for matching any of the supplied query
                                strings. e.g -q burger pizza will return all entries
                                matching 'burger' or 'pizza'
          -e, --estimate-time   calculate estimated time arrival for the resulting
                                query entries
          --alias-create ALIAS_CREATE
                                add query alias, use with -q switch. Use -q switch
                                without this option to dry-run the query
          --alias-delete ALIAS_DELETE
                                delete query alias
          --alias-list          list existing aliases
          -Q ALIAS_QUERY, --alias-query ALIAS_QUERY
                                run aliased query

Examples
--------
* Fetch messages and populate local db::

        $ tummy_time/tummy_time -F
        fetching data
        added <2065160673.9607557.1398934680559.JavaMail.zimbra@redhat.com> 2014-05-01 11:58:00
        added <1553776994.56788.1399194968464.JavaMail.zimbra@redhat.com> 2014-05-04 12:16:08
        added <1168519797.59133.1399200781476.JavaMail.zimbra@redhat.com> 2014-05-04 13:53:01
        added <1266962898.1016995.1399454545142.JavaMail.zimbra@redhat.com> 2014-05-07 12:22:25
        added <1453633013.1035433.1399459804993.JavaMail.zimbra@redhat.com> 2014-05-07 13:50:05
        added <1265521976.1460599.1399539847604.JavaMail.zimbra@redhat.com> 2014-05-08 12:04:07
        added <699473397.1878658.1399543235945.JavaMail.zimbra@redhat.com> 2014-05-08 13:00:35


* Dump stats of a single restaurant and get an ETA::

        $ ./tummy_time/tummy_time -q najima 'nagima' -e
        lunch from ludens, Ahuzat Hahumous, Najima has arrived 2016-01-20 12:20:43
        Lunch from Baharat and Najima has arrived 2016-01-25 12:23:08
        Lunch from Najima and Shnitzels has arrived 2016-01-31 13:12:30
        Lunch from Najima has arrived 2016-02-08 12:41:04
        Lunch from Najima has arrived 2016-02-16 12:26:24
        Lunch from Najima and Baharat has arrived 2016-02-21 12:10:46
        Lunch from Najima has arrived 2016-02-23 12:19:55
        Lunch from Shnitzel Bar Bari, Najima has arrived 2016-03-01 12:31:03
        Lunch from Najima has arrived 2016-03-15 12:12:53
        Lunch from Najima has arrived 2016-03-16 12:43:10
        Lunch from Najima and Lehem Tushia has arrived 2016-03-22 11:57:22
        Lunch from Najima has arrived 2016-03-23 12:44:38
        --------------------------------------------------
        estimation: 12:28:43

* Create a 'pizzas' query alias::

        $ ./tummy_time.py --alias-create pizzas -q dominos hut 'La Porchetta'
        Lunch from Pizza hut has arrived 2016-03-17 12:12:07
        Lunch from Pizza Hut has arrived 2016-03-22 12:33:15
        Luch from Pizza hut and Zozobra has arrived 2016-03-30 12:47:27


* Run a saved 'pizzas' query and get an ETA for it::

        $ ./tummy_time.py -Q pizzas -e
        Lunch from China Class has arrived 2016-03-10 12:55:34
        Lunch from Pizza hut has arrived 2016-03-17 12:12:07
        Lunch from Pizza Hut has arrived 2016-03-22 12:33:15
        Luch from Pizza hut and Zozobra has arrived 2016-03-30 12:47:27
        --------------------------------------------------
        estimation: 12:41:43

* List all existing aliases::

         $ ./tummy_time.py --alias-list
         pizzas: dominos hut La Porchetta

