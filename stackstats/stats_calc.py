import requests
import json
import logging
from datetime import datetime
from argparse import ArgumentParser

logger = logging.basicConfig(__name__)

ANSWERS_URL =  "http://api.stackexchange.com/2.2/answers?fromdate=%s&todate=%s&order=desc&sort=activity&site=stackoverflow"
COMMENTS_URL = "http://api.stackexchange.com/2.2/answers/%s/comments?fromdate=%s&todate=%s&order=desc&sort=creation&site=stackoverflow"

def convert_to_milis(date_string):

    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    epoch = datetime.fromtimestamp(0)
    return int((dt - epoch).total_seconds() * 1000)


def main():

    parser = ArgumentParser()
    parser.add_argument("-s", "--since", dest="since", help="date since we need the statistics", required=True)
    parser.add_argument("-u", "--until", dest="until", help="date until we need the statistics", required=True)
    parser.add_argument("--output-format", dest="output", help="output file in JSON format with the results")

    args = parser.parse_args()

    since_date = convert_to_milis(args.since)
    until_date = convert_to_milis(args.until)

    logger.info('Retrieving the answer data from %s until %s' % (since_date, until_date))
    response = requests.get(ANSWERS_URL % (since_date, until_date))
    stats_dict = json.loads(response.text)
    logger.info('Done')

    answer_set = [element['answer_id'] for element in stats_dict['items']]
    logger.info('Retrieving the comment data for a given set of answers %s' % (str(answer_set)))
    comments = []
    batch_size = len(answer_set) / 100
    batch_modulo = len(answer_set) % 100
    start = 0
    end = 100
    if batch_size:
        for i in range(batch_size):
                batch = ';'.join(str(el) for el in answer_set[start:end])
                comments_response = requests.get(COMMENTS_URL % (batch, since_date, until_date))
                comments_dict = json.loads(comments_response.text)
                comments.append(comments_dict)
                start = start + 100
                end = end + 100

        if batch_modulo:
            remaining_batch = ';'.join(str(el) for el in answer_set[end:end+batch_modulo])
            comments_response = requests.get(COMMENTS_URL % remaining_batch, since_date, until_date)
            comments_dict = json.loads(comments_response.text)
            comments.append(comments_dict)

    elif not batch_size:
        if batch_modulo:
            batch = ';'.join(str(el) for el in answer_set)
            comments_response = requests.get(COMMENTS_URL % (batch, since_date, until_date))
            comments_dict = json.loads(comments_response.text)
            comments.append(comments_dict)

    else:
        pass

    logger.info("Done")

    logger.info("Calculating total number of accepted answers")
    accepted_answers = [i for i in stats_dict['items'] if i['is_accepted'] is True]
    total_accepted_answers = len(accepted_answers)
    #accepted_answers_count = reduce(lambda x, y: x+y, [1 for i in stats_dict['items'] if i['is_accepted'] is True])
    logger.info("Done")

    logger.info("Calculating average score of accepted answers")
    scores_of_accepted_answers = [i['score'] for i in accepted_answers]
    avg_score_of_accepted_answers = sum(scores_of_accepted_answers) / len(scores_of_accepted_answers)
    logger.info("Done")







