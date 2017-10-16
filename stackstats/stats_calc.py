import requests
import sys
import json
import logging
from datetime import datetime
from argparse import ArgumentParser
from collections import Counter
import pprint

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ANSWERS_URL =  "http://api.stackexchange.com/2.2/answers?page=%s&pagesize=%s&fromdate=%s&todate=%s&order=desc&sort=activity&site=stackoverflow"
COMMENTS_URL = "http://api.stackexchange.com/2.2/answers/%s/comments?page=%s&pagesize=%s&order=desc&sort=creation&site=stackoverflow"


def convert_to_milis(date_string):

    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    epoch = datetime.fromtimestamp(0)
    milis = (dt - epoch).total_seconds() * 1000
    milis = '{:.0f}'.format(milis)[:10]

    return int(milis)


def main():

    parser = ArgumentParser()
    parser.add_argument("-s", "--since", dest="since", help="date since we need the statistics", required=True)
    parser.add_argument("-u", "--until", dest="until", help="date until we need the statistics", required=True)
    parser.add_argument("--output-format", dest="output", help="output file in JSON format with the results")

    args = parser.parse_args()

    since_date = convert_to_milis(args.since)
    until_date = convert_to_milis(args.until)

    logger.info('Retrieving the answer data from %s until %s' % (since_date, until_date))
    stats_list = []
    page = 1
    pagesize = 100
    has_more = True
    while has_more:
        response = requests.get(ANSWERS_URL % (page, pagesize, since_date, until_date))
        stats_dict = response.json()
        stats_list.extend(stats_dict['items'])
        if stats_dict['has_more'] is True:
            page += 1
            continue
        else:
            has_more = False
    logger.info('Done')


    answer_set = [element['answer_id'] for element in stats_list]
    logger.info('Retrieving the comment data for a given set of answers')
    comments = []
    has_more_comments = True
    page = 1
    pagesize = 100
    batch_size = len(answer_set) / 100
    batch_modulo = len(answer_set) % 100
    start = 0
    end = 100
    if batch_size:
        for i in range(batch_size):
                batch = ';'.join(str(el) for el in answer_set[start:end])
                while has_more_comments:
                    comments_response = requests.get(COMMENTS_URL % (batch, page, pagesize))
                    comments_dict = comments_response.json()
                    comments.extend(comments_dict['items'])
                    if comments_dict['has_more'] is True:
                        page += 1
                        continue
                    else:
                        has_more_comments = False

                start = start + 100
                end = end + 100
                has_more_comments = True
                page = 1

        if batch_modulo:
            remaining_batch = ';'.join(str(el) for el in answer_set[start:start + batch_modulo])
            while has_more_comments:
                comments_response = requests.get(COMMENTS_URL % (remaining_batch, page, pagesize))
                comments_dict = comments_response.json()
                comments.extend(comments_dict['items'])
                if comments_dict['has_more'] is True:
                    page += 1
                    continue
                else:
                    has_more_comments = False

    elif not batch_size:
        if batch_modulo:
            batch = ';'.join(str(el) for el in answer_set)
            while has_more_comments:
                comments_response = requests.get(COMMENTS_URL % (batch, page, pagesize))
                comments_dict = comments_response.json()
                comments.extend(comments_dict['items'])
                if comments_dict['has_more'] is True:
                    page += 1
                    continue
                else:
                    has_more_comments = False

    logger.info("Done")

    logger.info("Calculating total number of accepted answers")
    accepted_answers = [i for i in stats_list if i['is_accepted'] is True]
    total_accepted_answers = len(accepted_answers)
    logger.info("Done")

    logger.info("Calculating average score of accepted answers")
    scores_of_accepted_answers = [i['score'] for i in accepted_answers]
    accepted_answers_average_score = float(sum(scores_of_accepted_answers)) / len(scores_of_accepted_answers)
    logger.info("Done")

    logger.info("Calculating average answer count per question")

    question_ids = [i['question_id'] for i in stats_list]
    cnt_qid = Counter(question_ids)
    average_answers_per_question = float(sum(cnt_qid.values())) / len(cnt_qid.keys())
    logger.info("Done")

    logger.info("Calculating number of comments for top 10 answers(based on score)")

    top_10_answers_on_score = sorted(stats_list, key=lambda item: item['score'], reverse=True)[:10]

    answers_in_comments_list = [item['post_id'] for item in comments]
    cnt_ans = Counter(answers_in_comments_list)
    top_10_answers_comment_count = {}
    for answer in top_10_answers_on_score:
        if answer['answer_id'] in cnt_ans:
            top_10_answers_comment_count[answer['answer_id']] = cnt_ans[answer['answer_id']]
        else:
            top_10_answers_comment_count[answer['answer_id']] = 0

    logger.info("Done")



    results = {"total_accepted_answers":total_accepted_answers,
               "accepted_answers_average_score":accepted_answers_average_score,
               "average_answers_per_question":average_answers_per_question,
               "top_10_answers_comment_count":top_10_answers_comment_count
               }

    if args.output == 'json':
        logger.info(pprint.pformat(results))
    elif args.output == 'html':
        pass
        #TODO html handling and tabular handling as well



if __name__ == '__main__':
    main()



