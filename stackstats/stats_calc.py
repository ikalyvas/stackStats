import logging
from datetime import datetime
from argparse import ArgumentParser
from collections import Counter
import pprint

import requests
from html import HTML

logger = logging.getLogger('main')
logging.basicConfig(level=logging.INFO)

ANSWERS_URL =  "http://api.stackexchange.com/2.2/answers?page={page}&pagesize={pagesize}&fromdate={since_date}&todate={until_date}&order=desc&sort=activity&site=stackoverflow"
COMMENTS_URL = "http://api.stackexchange.com/2.2/answers/{batch}/comments?page={page}&pagesize={pagesize}&order=desc&sort=creation&site=stackoverflow"


class Stats(object):

    def __init__(self, since, until, output_format='json'):

        self.logger = logging.getLogger(self.__class__.__name__)
        self.since_date = self.convert_to_milis(since)
        self.until_date = self.convert_to_milis(until)
        self.output_format = output_format
        self.stats_list = []
        self.comments = []
        self.accepted_answers = None

    @staticmethod
    def convert_to_milis(date_string):

        dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        epoch = datetime.fromtimestamp(0)
        milis = (dt - epoch).total_seconds() * 1000
        milis = '{:.0f}'.format(milis)[:10]

        return int(milis)

    def get_answers(self):

        self.get_all_results(ANSWERS_URL, self.stats_list)

    def get_all_results(self, URL, results, batch=None):

        has_more = True
        page = 1
        pagesize = 100

        while has_more:
            response = requests.get(URL.format(batch=batch,
                                               page=page,
                                               pagesize=pagesize,
                                               since_date=self.since_date,
                                               until_date=self.until_date)
                                    )
            stats_dict = response.json()
            results.extend(stats_dict['items'])
            if stats_dict['has_more'] is True:
                page += 1
                continue
            else:
                has_more = False

    def get_comments(self):

        answer_set = [element['answer_id'] for element in self.stats_list]
        batch_size = len(answer_set) / 100
        batch_modulo = len(answer_set) % 100
        start = 0
        end = 100
        if batch_size:
            for i in range(batch_size):
                batch = ';'.join(str(el) for el in answer_set[start:end])
                self.get_all_results(COMMENTS_URL, self.comments, batch)
                start = start + 100
                end = end + 100

            if batch_modulo:
                remaining_batch = ';'.join(str(el) for el in answer_set[start:start + batch_modulo])
                self.get_all_results(COMMENTS_URL, self.comments, remaining_batch)

        elif not batch_size:
            if batch_modulo:
                batch = ';'.join(str(el) for el in answer_set)
                self.get_all_results(COMMENTS_URL, self.comments, batch)

    def get_total_num_accepted_answers(self):
        self.accepted_answers = [i for i in self.stats_list if i['is_accepted'] is True]
        total_accepted_answers = len(self.accepted_answers)
        return total_accepted_answers

    def get_scores_of_accepted_answers(self, accepted_answers):
        scores_of_accepted_answers = [i['score'] for i in accepted_answers]
        accepted_answers_average_score = float(sum(scores_of_accepted_answers)) / len(scores_of_accepted_answers)
        return accepted_answers_average_score

    def get_average_answer_count_per_question(self):
        question_ids = [i['question_id'] for i in self.stats_list]
        cnt_qid = Counter(question_ids)
        average_answers_per_question = float(sum(cnt_qid.values())) / len(cnt_qid.keys())
        return average_answers_per_question

    def get_top_10_answers_on_score(self):
        top_10_answers_on_score = sorted(self.stats_list, key=lambda item: item['score'], reverse=True)[:10]
        answers_in_comments_list = [item['post_id'] for item in self.comments]
        cnt_ans = Counter(answers_in_comments_list)
        top_10_answers_comment_count = {}
        for answer in top_10_answers_on_score:
            if answer['answer_id'] in cnt_ans:
                top_10_answers_comment_count[answer['answer_id']] = cnt_ans[answer['answer_id']]
            else:
                top_10_answers_comment_count[answer['answer_id']] = 0

        return top_10_answers_comment_count

    def log_results(self, output_format, results):

        if output_format == 'json':
            self.logger.info(pprint.pformat(results))
        elif output_format == 'html':
            h = HTML()
            t = h.table(border='1')
            for key, value in results.items():
                if isinstance(value, dict):
                    r = t.tr
                    r.td(str(key))
                    for k, v in value.items():
                        r = t.tr
                        r.td()
                        r.td(str(k))
                        r.td(str(v))
                else:
                    r = t.tr
                    r.td(key)
                    r.td(str(value))
            with open('results.html','w') as f:
                f.write(str(t))
        else:
            for row, data in results.items():
                if isinstance(data, dict):
                    self.logger.info(str(row).ljust(50))
                    for k, v in data.items():
                        self.logger.info(str(k).ljust(50) + str(v))
                else:
                    self.logger.info(str(row).ljust(50) + str(data))


def main():

    parser = ArgumentParser()
    parser.add_argument("-s", "--since", dest="since", help="date since we need the statistics", required=True)
    parser.add_argument("-u", "--until", dest="until", help="date until we need the statistics", required=True)
    parser.add_argument("--output-format", dest="output", help="output file in JSON format with the results", default='json')

    args = parser.parse_args()

    stats = Stats(args.since, args.until, args.output)

    logger.info('Retrieving the answer data from %s until %s' % (args.since, args.until))
    stats.get_answers()
    logger.info("Done")

    logger.info('Retrieving the comment data for a given set of answers')
    stats.get_comments()
    logger.info("Done")

    logger.info("Calculating total number of accepted answers")
    total_accepted_answers = stats.get_total_num_accepted_answers()
    logger.info("Done")

    logger.info("Calculating average score of accepted answers")
    accepted_answers_average_score = stats.get_scores_of_accepted_answers(stats.accepted_answers)
    logger.info("Done")

    logger.info("Calculating average answer count per question")
    average_answers_per_question = stats.get_average_answer_count_per_question()
    logger.info("Done")

    logger.info("Calculating number of comments for top 10 answers(based on score)")

    top_10_answers_comment_count = stats.get_top_10_answers_on_score()

    logger.info("Done")

    results = {"total_accepted_answers": total_accepted_answers,
               "accepted_answers_average_score": accepted_answers_average_score,
               "average_answers_per_question": average_answers_per_question,
               "top_10_answers_comment_count": top_10_answers_comment_count
               }

    stats.log_results(args.output, results)


if __name__ == '__main__':
    main()



