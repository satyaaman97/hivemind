import json, os, praw, re, sys, time
from bs4 import BeautifulSoup
url_regex_pattern = r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)'

def construct_submissions(submission_ids):
    results = r.info(submission_ids)
    submissions = []
    fields = ('title', 'score', 'created_utc', 'num_comments', 'distinguished', 'id', 'over_18', 'stickied', 'upvote_ratio', 'ups', 'total_awards_received', 'downs', 'gilded', 'num_crossposts', 'num_duplicates')
    for s in results:
        title = s.title
        to_dict = vars(s)
        post = {field:to_dict[field] for field in fields if field in to_dict}
        body = s.selftext_html
        if body:
            body = ''.join(BeautifulSoup(body, features="lxml").findAll(text=True)).replace('\n',' ')
            body = re.sub(url_regex_pattern, '', body)
            post['body'] = body
        comments = s.comments
        comments.replace_more(limit=None)
        comments = comments.list()
        post['comments'] = [comment_to_dict(comment) for comment in comments]
        submissions.append(post)
    return submissions

def comment_to_dict(comment):
    fields = ('score', 'created_utc', 'distinguished', 'id', 'link_id', 'parent_id', 'stickied', 'gilded', 'controversiality', 'downs', 'total_awards_received', 'ups')
    to_dict = vars(comment)
    comment_dict = {field:to_dict[field] for field in fields}
    comment_dict['body'] = ''.join(BeautifulSoup(comment.body_html, features="lxml").findAll(text=True)).replace('\n',' ')
    comment_dict['body'] = re.sub(url_regex_pattern, ' ', comment_dict['body'])

    return comment_dict
def process(links, filename):
    output = construct_submissions(links)
    with open(filename, 'a') as f:
        for out in output:
            f.write(json.dumps(out) + '\n')
    
if __name__ == '__main__':
    print(sys.argv)
    linkSet = set([])
    r = praw.Reddit(client_id=os.environ.get('CLIENT_ID'), client_secret=os.environ.get('CLIENT_SECRET'), user_agent='windows:hivemind:v0.1 (by u/stuepid)')

    with open(sys.argv[1], "r") as f:
        links = []
        i = 0
        j = 1
        for line in f:
            obj = json.loads(line)
            link = obj['link_id']
            if link not in linkSet:
                linkSet.add(link)
                links.append(link)
            if len(links) >= 1000:
                i += len(links)
                process(links, f'{sys.argv[2]}/output_{j}.json')
                with open(f'{sys.argv[2]}/logfile_{j}', 'a') as f:
                    f.write(f'Lines:{i-len(links)}-{i} Time: {time.strftime("%X %x")}\n')
                if i >= 200000:
                    i = 0
                    j += 1
                links = []
        if len(links) > 0:
            process(links, f'data/processed/output_{j}.json')
            with open(f'{sys.argv[2]}/logfile_{j}', 'a') as f:
                f.write(f'Lines:{i-len(links)}-{i} Time: {time.strftime("%X %x")}\n')