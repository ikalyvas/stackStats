import unittest

from stackstats.stats_calc import Stats
from mock import patch, Mock


class TestStackStats(unittest.TestCase):

    def setUp(self):
        self.stats = Stats('2016-1-1 00:00:0','2016-1-1 00:00:01')
        pass

    def tearDown(self):
        self.stats = None
        pass

    def test_convert_milis(self):
        date_1 = "2016-06-2 10:00:00"
        date_2 = "2016-06-3 11:00:00"
        date_3 = "2017-12-1 15:34:00"

        #GMT evaluation

        self.assertEqual(1464861600, self.stats.convert_to_milis(date_1))
        self.assertEqual(1464951600, self.stats.convert_to_milis(date_2))
        self.assertEqual(1512142440, self.stats.convert_to_milis(date_3))

    @patch.object(Stats, 'get_all_results')
    def test_assert_get_answers_get_all_is_called(self, mock_get_all_res):
        self.stats.get_answers()
        self.assertTrue(mock_get_all_res.called)

    @patch('stackstats.stats_calc.requests')
    def test_assert_get_answers_returns_OK(self, mock_requests):
        response = Mock()
        mock_requests.get.return_value = response
        response.json.return_value = {u'has_more': False,
                                      u'items':
                                          [{u'question_id': 22778640,
                                            u'last_activity_date': 1502846215,
                                            u'creation_date': 1464862159,
                                            u'score': 25, u'owner': 'me'
                                                }]
                                      }
        self.stats.get_answers()
        self.assertEqual(self.stats.stats_list, [{u'question_id': 22778640,
                                            u'last_activity_date': 1502846215,
                                            u'creation_date': 1464862159,
                                            u'score': 25, u'owner': 'me'
                                                }])


    @patch('stackstats.stats_calc.requests')
    def test_assert_get_answers_stops_when_has_more_is_False(self, mock_requests):
        response = Mock()
        mock_requests.get.return_value = response
        response.json.side_effect = [{u'has_more': True,
                                      u'items':
                                          [{u'question_id': 1,
                                            u'last_activity_date': 14,
                                            u'creation_date': None,
                                            u'score': 25, u'owner': 'me'
                                                }]
                                      },
                                     {u'has_more': False,
                                      u'items':
                                          [{u'question_id': 2,
                                            u'last_activity_date': 28,
                                            u'creation_date': None,
                                            u'score': 26, u'owner': 'you'
                                                }]
                                      }
                                     ]

        self.stats.get_answers()
        self.assertEqual(self.stats.stats_list, [{u'question_id': 1,
                                            u'last_activity_date': 14,
                                            u'creation_date': None,
                                            u'score': 25, u'owner': 'me'},
                                                 {u'question_id': 2,
                                            u'last_activity_date': 28,
                                            u'creation_date': None,
                                            u'score': 26, u'owner': 'you'
                                                }])
