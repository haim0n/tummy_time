#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_tummy_time
----------------------------------

Tests for `tummy_time` module.
"""
from datetime import datetime
import mock
import unittest

from freezegun import freeze_time

from tummy_time import data_utils


class TestFetcher(unittest.TestCase):
    dummy_url = 'http://dummy_url'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _test_get_all_archives(self):
        fist_archive_date = datetime(2015, 10, 1)
        fetcher = data_utils.Fetcher(url=self.dummy_url,
                                     first_archive_date=fist_archive_date,
                                     archive_suffix='.txt.gz')
        return fetcher

    @freeze_time("2016-04-01")
    def test_get_all_archives(self):
        fetcher = self._test_get_all_archives()
        out = fetcher._get_all_archive_dates()
        expected = {(2015, 10), (2015, 11), (2015, 12), (2016, 1), (2016, 2),
                    (2016, 3), (2016, 4)}
        self.assertSetEqual(out, expected)

    @freeze_time("2016-04-01")
    def test_get_all_archive_names(self):
        fetcher = self._test_get_all_archives()
        out = fetcher.get_all_archive_names()
        expected = ['2015-October.txt.gz', '2015-November.txt.gz',
                    '2015-December.txt.gz', '2016-January.txt.gz',
                    '2016-February.txt.gz', '2016-March.txt.gz',
                    '2016-April.txt.gz']
        self.assertItemsEqual(expected, out)

    def test_get_fetched_archives(self):
        archive_dir = '/tmp'
        suffix = '.tgz'
        fetcher = data_utils.Fetcher(url=self.dummy_url,
                                     first_archive_date=mock.Mock(),
                                     archive_suffix=suffix,
                                     archive_dir=archive_dir)
        with mock.patch('glob.glob') as mock_glob:
            fetcher.get_fetched_archives()
            mock_glob.assert_called_with(archive_dir + '/*' + suffix)

    def test_fetch_archives(self):
        fetcher = data_utils.Fetcher(url=self.dummy_url,
                                     first_archive_date=mock.Mock(),
                                     archive_suffix='.tgz',
                                     archive_dir='/tmp')

        with mock.patch('urllib2.urlopen') as mock_retrieve:
            with mock.patch('tummy_time.data_utils.open', mock.mock_open(),
                            create=True):
                dummy_archives = ['dummy1', 'dummy2']
                fetcher.fetch_archives(dummy_archives)
                for archive in dummy_archives:
                    remote_archive = self.dummy_url + '/' + archive
                    mock_retrieve.assert_any_call(remote_archive)

    @freeze_time("2016-04-01")
    def test_fetch(self):
        fetcher = data_utils.Fetcher(url=self.dummy_url,
                                     first_archive_date=datetime(2015, 12, 1),
                                     archive_suffix='.tgz',
                                     archive_dir='/tmp')
        fetcher.get_fetched_archives = mock.Mock(return_value=[])
        mock_fetch = mock.Mock()
        fetcher.fetch_archives = mock_fetch
        fetcher.fetch()
        expected = {'2016-April.tgz', '2016-February.tgz', '2016-January.tgz',
                    '2015-December.tgz', '2016-March.tgz'}
        mock_fetch.assert_called_once_with(expected)

        # if all archives exist, fetch only the latest
        fetcher.get_fetched_archives = mock.Mock(return_value=expected)
        fetcher.fetch()
        mock_fetch.assert_called_with({'2016-April.tgz'})


class TestParser(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_filter_messages(self):
	pass

if __name__ == '__main__':
    import sys

    sys.exit(unittest.main())
