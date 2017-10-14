import requests
import json
import logging
from datetime import datetime
from argparse import ArgumentParser
from collections import Counter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ANSWERS_URL =  "http://api.stackexchange.com/2.2/answers?page=%s&pagesize=%s&fromdate=%s&todate=%s&order=desc&sort=activity&site=stackoverflow"
COMMENTS_URL = "http://api.stackexchange.com/2.2/answers/%s/comments?fromdate=%s&todate=%s&order=desc&sort=creation&site=stackoverflow"

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
        stats_dict = json.loads(response.text)
        stats_list.extend(stats_dict['items'])
        if stats_dict['has_more'] is True:
            #stats_list.append(stats_dict['items'])
            page += 1
            continue
        else:
            has_more = False
    logger.info('Done')




    answer_set = [element['answer_id'] for element in stats_list]
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
                comments.extend(comments_dict)
                start = start + 100
                end = end + 100

        if batch_modulo:
            remaining_batch = ';'.join(str(el) for el in answer_set[end:end+batch_modulo])
            comments_response = requests.get(COMMENTS_URL % (remaining_batch, since_date, until_date))
            comments_dict = json.loads(comments_response.text)
            comments.extend(comments_dict)

    elif not batch_size:
        if batch_modulo:
            batch = ';'.join(str(el) for el in answer_set)
            comments_response = requests.get(COMMENTS_URL % (batch, since_date, until_date))
            comments_dict = json.loads(comments_response.text)
            comments.extend(comments_dict)

    else:
        pass

    logger.info("Done")

    logger.info("Calculating total number of accepted answers")
    accepted_answers = [i for i in stats_list if i['is_accepted'] is True]
    total_accepted_answers = len(accepted_answers)
    logger.info("Done")

    logger.info("Calculating average score of accepted answers")
    scores_of_accepted_answers = [i['score'] for i in accepted_answers]
    avg_score_of_accepted_answers = float(sum(scores_of_accepted_answers)) / len(scores_of_accepted_answers)
    logger.info("Done")


    logger.info("Calculating average answer count per question")


    question_ids = [i['question_id'] for i in stats_list]
    cnt = Counter(question_ids)
    avg_answers_per_qid = float(sum(cnt.values())) / len(cnt.keys())
    logger.info("Done")


    logger.warning("Total accepted answers %s" % str(total_accepted_answers))
    logger.warning("Average score of accepted answers %s" % str(avg_score_of_accepted_answers))
    logger.warning("Average answers per qid %s" % str(avg_answers_per_qid))
    logger.warning("Comment data %s" % comments)



if __name__ == '__main__':
    main()



