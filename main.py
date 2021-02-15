from datetime import datetime
import instaloader
import json, csv
import sys, os, time,random

def update_progress(progress):
    barLength = 40 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def getPosts(username,password,hashtags):
    '''
    Returns a list of captions of top 700 posts of relative hashtags.
    :param str username: username of the account.
    :param str password: password of the account.
    :param list hashtags: list of hashtag to be scraped.
    :rtype None
    '''

    L = instaloader.Instaloader()

    post_data = []
    # Caching the session to save file.
    try:
        L.load_session_from_file(username,f'session-{username}')
    except:
        L.login(username,password)
        L.save_session_to_file(f'session-{username}')
    
    for hashtag in hashtags:
        print(f"Hashtag: {hashtag}")
        posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts()

        k = 1 
        data = []
        for post in posts:
            update_progress(k/700)
            if k >=700:
                break
            
            data.append(post.caption_hashtags)
            k += 1

        mostCommon(hashtag,data)
        print('Waiting before next search...')
        time.sleep(random.randint(30,60))
    

def mostCommon(hashtag,data):
    '''
    Finds the top 30 hashtags in the scraped posts and saves it to a text file in 'output/hashtag.txt'
    :param str hashtag: Name of the hashtag that is scraped. Used for naming the output file.
    :param list data: List of list of hashtags scraped from the posts.
    :rtype None
    '''
    # Hashing the list to find the most used hashtag.
    word_counter = {}
    for hashtags in data:
        for word in hashtags:
            if word in word_counter:
                word_counter[word] += 1
            else:
                word_counter[word] = 1
    
    popular_words = sorted(word_counter, key = word_counter.get, reverse = True)
    top_30 = popular_words[:30]

    # Saving the list to a string to be saved to a text file.
    hashtag_str = ''
    for i in range(len(top_30)):
        hashtag_str = hashtag_str + '#' + top_30[i]
        if i%10 == 0 and i != 0:
            hashtag_str += '\n'
        else:
            hashtag_str += ' '

    filename = f'output/{hashtag}.txt'
    with open(filename,'w',encoding='utf-8-sig') as writefile:
        writefile.write(hashtag_str)
    
    print(f'File Saved at: {filename}')

if __name__ == '__main__':
    if len(sys.argv) < 4 or len(sys.argv) > 6:
        print("Usage: python main.py username password hashtag1 hashtag2 hashtag3")
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        hashtags = []
        for i in range(3,len(sys.argv)):
            hashtags.append(sys.argv[i])
        getPosts(username,password,hashtags)