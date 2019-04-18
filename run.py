from psaw import PushshiftAPI
import pickledb
import praw
from time import sleep
from halo import Halo

# DO NOT EDIT ABOVE THIS LINE

test_mode = True # Self explanitory
target_time = False  # Set to epoch timestamp to set date to get to/from
target_time_before = False  # Set to True to get content from before time set

client_id = 'XXXX'
client_secret = 'XXXX'
reddit_user = 'XXXX'
reddit_pass = 'XXXX'

# DO NOT EDIT BELOW THIS LINE

spinner = Halo(text='Booting up...', spinner='dots')
spinner.start()

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='Delete all the things! (by /u/impshum)',
                     username=reddit_user,
                     password=reddit_pass)

db = pickledb.load(f'{reddit_user}.db', False)
api = PushshiftAPI()


def get_ids_pushshift(switch):
    msg = 'Getting {} ids from Pushshift'.format(switch[:-1])
    spinner.text = msg
    sleep(1)
    if switch == 'comments':
        q = list(api.search_comments(author=reddit_user))
    elif switch == 'submissions':
        q = list(api.search_submissions(author=reddit_user))
    c = do_db(q, switch)
    msg = 'Found {} new {} on Pushshift'.format(c, switch)
    spinner.text = msg
    sleep(1)
    db.dump()


def get_ids_praw(switch):
    msg = 'Getting {} ids from Reddit'.format(switch[:-1])
    spinner.text = msg
    sleep(1)
    if switch == 'comments':
        q = reddit.redditor(reddit_user).comments.new(limit=None)
    elif switch == 'submissions':
        q = reddit.redditor(reddit_user).submissions.new(limit=None)
    c = do_db(q, switch)
    msg = 'Found {} new {} on Reddit'.format(c, switch)
    spinner.text = msg
    sleep(1)
    db.dump()


def do_db(q, switch):
    c = 0
    for x in q:
        try:
            if target_time:
                if target_time_before:
                    if x.created_utc < target_time:
                        if not db.exists(x.id):
                            c += 1
                            db.set(x.id, switch)
                else:
                    if x.created_utc > target_time:
                        if not db.exists(x.id):
                            c += 1
                            db.set(x.id, switch)
            else:
                if not db.exists(x.id):
                    c += 1
                    db.set(x.id, switch)

        except Exception as e:
            print(e)
    return c


def delete_all():
    c = 0
    for x in db.getall():
        switch = db.get(x)
        if switch != True:
            if switch == 'comments':
                comment = reddit.comment(x)
                if not test_mode:
                    comment.delete()
            elif switch == 'submissions':
                submission = reddit.submission(x)
                if not test_mode:
                    submission.delete()
            c += 1
            msg = 'Deleting {}'.format(c, switch)
            spinner.text = msg
            if not test_mode:
                sleep(2)
            else:
                sleep(0.05)
            db.set(x, True)
            db.dump()


def main():
    for type in ['submissions', 'comments']:
        get_ids_pushshift(type)
    for type in ['submissions', 'comments']:
        get_ids_praw(type)
    delete_all()
    spinner.succeed('Done')


if __name__ == '__main__':
    main()
