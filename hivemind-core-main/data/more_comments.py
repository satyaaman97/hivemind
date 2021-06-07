import json, os, praw, re, sys, time
from bs4 import BeautifulSoup
from process import comment_to_dict
def get_more_comments(submission_ids):
    results = r.info(submission_ids)
    submissions = []
    for s in results:
        to_dict = vars(s)
        post = {'id': to_dict[id]}
        more_comments = s.comments.replace_more()
        if len(more_comments) > 0:
            print('Found Comments: ', more_comments)
            comments = []
            for mc in more_comments:
                comments += mc.comments()
            post['comments'] = [comment_to_dict(comment) for comment in comments]
            submissions.append(post)                    
    return submissions

def process(ids, filename, logfile):
    output = get_more_comments(ids)
    if len(output) > 0:
        with open(filename, 'a') as f:
            for out in output:
                f.write(json.dumps(out) + '\n')
        with open(logfile, 'a') as f:
                f.write(f'Comments Added:{len(output)} Time: {time.strftime("%X %x")}\n')
    
if __name__ == '__main__':
    print(sys.argv)
    r = praw.Reddit(client_id=os.environ.get('CLIENT_ID'), client_secret=os.environ.get('CLIENT_SECRET'), user_agent='windows:hivemind:v0.1 (by u/stuepid)')
    with open(sys.argv[1], "r") as f:
        links = []
        i = 0
        j = 1
        for line in f:
            obj = json.loads(line)
            link = obj['id']
            links.append(link)
            if len(links) >= 100:
                i += len(links)
                process(links, f'{sys.argv[2]}/comments_{j}.json', f'{sys.argv[2]}/comments_logfile_{j}')
                with open(f'{sys.argv[2]}/comments_logfile_{j}', 'a') as f:
                    f.write(f'Posts {i-len(links)}-{i} processed\n')
                links = []
        if len(links) > 0:
            process(links, f'data/processed/comments_{j}.json', f'{sys.argv[2]}/comments_logfile_{j}')
            with open(f'{sys.argv[2]}/comments_logfile_{j}', 'a') as f:
                    f.write(f'Posts {i-len(links)}-{i} processed\n')
    