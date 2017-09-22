from os import environ
import praw

client_id = environ.get('REDDIT_CLIENT_ID')
client_secret = environ.get('REDDIT_SECRET')
agent = 'script:{}:0.0.0'.format(client_id)

if client_id is None or client_secret is None:
    raise EnvironmentError(
        'No client id or secret found in your environment'
    )


reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=agent
)

humour_subreddits = [
    'paslegorafi',
    'ivrevirgule',
    'jememarre'
]

humour_subreddits_qs = '+'.join(humour_subreddits)


def get_top_humour_submissions(
    sub_qs=humour_subreddits_qs,
    additional_search_qs=None
):
    subs = reddit.subreddit(sub_qs)
    search_qs = '(/s OR satire OR sarcasme)'
    if additional_search_qs is not None:
        search_qs = (
            additional_search_qs,
            ' AND ',
            search_qs
        )

    return subs.search(search_qs, limit=None)


def filter_subs(subs):
    return [sub for sub in subs
            if sub.num_comments > 10]


def gen_comments_tree(comments):
    tree = {}
    for comment in comments:
        comment_tree = {
            'type': 'comment',
            'body': comment.body,
            'score': comment.score,
        }
        author = comment.author
        if author is not None:
            comment_tree['author_name'] = author.name
        else:
            comment_tree['author_name'] = 'deleted'

        if len(comment.replies) > 0:
            comment_tree['replies'] = gen_comments_tree(comment.replies)

        tree[comment.id] = comment_tree
    return tree


def gen_submission_dict(submission):
    submission.comments.replace_more(limit=0)
    author = submission.author
    return {
        'type': 'submission',
        'author_name': author.name,
        'title': submission.title,
        'text': submission.selftext,
        'url': submission.url,
        'comments': gen_comments_tree(
            submission.comments
        ),
        'score': submission.score,
    }


def get_submissions():
    france_subs = get_top_humour_submissions(
        'france',
        'flair:Humour'
    )
    subs = filter_subs(france_subs)
    for subreddit in humour_subreddits:
        subs += filter_subs(
            get_top_humour_submissions(subreddit)
        )

    sub_tree = {}
    for submission in subs:
        sub_tree[submission.id] = gen_submission_dict(submission)

    return sub_tree
