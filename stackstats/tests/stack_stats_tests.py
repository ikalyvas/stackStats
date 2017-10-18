import unittest

from stackstats.stats_calc import Stats
from mock import patch, Mock


class TestStackStats(unittest.TestCase):

    def setUp(self):
        self.stats = Stats('2016-1-1 00:00:0','2016-1-1 00:00:01')
        self.stats_list_data = [{
            "owner": {
                "reputation": 816,
                "user_id": 4695752,
                "user_type": "registered",
                "accept_rate": 68,
                "profile_image": "https://graph.facebook.com/10203574071421073/picture?type=large",
                "display_name": "Jan van der Vegt",
                "link": "https://stackoverflow.com/users/4695752/jan-van-der-vegt"
            },
            "is_accepted": False,
            "score": 1,
            "last_activity_date": 1464862173,
            "creation_date": 1464862173,
            "answer_id": 37588832,
            "question_id": 37588793
        },
            {
                "owner": {
                    "reputation": 1929,
                    "user_id": 2176425,
                    "user_type": "registered",
                    "accept_rate": 75,
                    "profile_image": "https://i.stack.imgur.com/iCJ8C.jpg?s=128&g=1",
                    "display_name": "huuuk",
                    "link": "https://stackoverflow.com/users/2176425/huuuk"
                },
                "is_accepted": False,
                "score": 2,
                "last_activity_date": 1464862165,
                "creation_date": 1464862165,
                "answer_id": 37588831,
                "question_id": 37588515
            },
            {
                "owner": {
                    "reputation": 2193,
                    "user_id": 5217524,
                    "user_type": "registered",
                    "accept_rate": 67,
                    "profile_image": "https://i.stack.imgur.com/uYOQJ.png?s=128&g=1",
                    "display_name": "phongvan",
                    "link": "https://stackoverflow.com/users/5217524/phongvan"
                },
                "is_accepted": True,
                "score": 4,
                "last_activity_date": 1464862154,
                "creation_date": 1464862154,
                "answer_id": 37588826,
                "question_id": 37588646
            },
            {
                "owner": {
                    "reputation": 2193,
                    "user_id": 5217524,
                    "user_type": "registered",
                    "accept_rate": 67,
                    "profile_image": "https://i.stack.imgur.com/uYOQJ.png?s=128&g=1",
                    "display_name": "phongvan",
                    "link": "https://stackoverflow.com/users/5217524/phongvan"
                },
                "is_accepted": True,
                "score": 14,
                "last_activity_date": 1464862154,
                "creation_date": 1464862154,
                "answer_id": 1,
                "question_id": 37588646
            }
        ]
        self.accepted_answs_data = [{
                "owner": {
                    "reputation": 2193,
                    "user_id": 5217524,
                    "user_type": "registered",
                    "accept_rate": 67,
                    "profile_image": "https://i.stack.imgur.com/uYOQJ.png?s=128&g=1",
                    "display_name": "phongvan",
                    "link": "https://stackoverflow.com/users/5217524/phongvan"
                },
                "is_accepted": True,
                "score": 14,
                "last_activity_date": 1464862154,
                "creation_date": 1464862154,
                "answer_id": 1,
                "question_id": 37588646
            }, {
                "owner": {
                    "reputation": 2193,
                    "user_id": 5217524,
                    "user_type": "registered",
                    "accept_rate": 67,
                    "profile_image": "https://i.stack.imgur.com/uYOQJ.png?s=128&g=1",
                    "display_name": "phongvan",
                    "link": "https://stackoverflow.com/users/5217524/phongvan"
                },
                "is_accepted": True,
                "score": 4,
                "last_activity_date": 1464862154,
                "creation_date": 1464862154,
                "answer_id": 37588826,
                "question_id": 37588646
            }
        ]


    def tearDown(self):
        self.stats = None

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



    def test_return_total_num_accepted_answers(self):

        self.stats.stats_list = self.stats_list_data
        self.assertEqual(2, self.stats.get_total_num_accepted_answers())

    def test_get_scores_of_accepted_answers(self):
        acc_answ_avg_score = self.stats.get_scores_of_accepted_answers(self.accepted_answs_data)
        self.assertEqual(9, acc_answ_avg_score)

