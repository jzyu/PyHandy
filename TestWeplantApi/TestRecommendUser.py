import requests as req
import datetime

HOST = "http://wohuizhong.com/api/"
TEST_USER = {'phone':'13925285765', 'password':'123456'}
TOKEN_PARAM = '?token=4f966eecbd4ce3fba1779810ed21e98c'
SECONDS_TIMEOUT = 10
SECONDS_SLOW = 6
TEST_TOPIC_COUNT = 100

timeout_file = open('topic_timeout.txt', 'w+')
slow_file = open('topic_slow.txt', 'w+')
timeout_count = 0
slow_count = 0
index = 0

print "sign in..."
req.post(HOST + 'sign/in', data=TEST_USER)
print "fetch topic..."
topics = req.get(HOST + 'explore/topic/0/50000').json()['list']

print "\n=== test begin ==="
for topic in topics[0:TEST_TOPIC_COUNT]:
    tid = str(topic['tid'])
    title = topic['title'].encode('utf8')

    print "(%d/%d) topic = %s, %s" % (index, TEST_TOPIC_COUNT, tid, title)
    index += 1
    print "  step1. focus"
    req.post(HOST + 'focus/topic/' + tid + TOKEN_PARAM)

    try:
        print "  step2. recommend"
        apiGetRecommendUser = HOST + 'user/recommend' + TOKEN_PARAM

        time_begin = datetime.datetime.now()
        req.get(apiGetRecommendUser, timeout=SECONDS_TIMEOUT)
        seconds_elapsed = (datetime.datetime.now() - time_begin).total_seconds()

        print "  result: %s, seconds=%d \n" % ('slow!' if seconds_elapsed > SECONDS_SLOW else 'pass', seconds_elapsed)

        if seconds_elapsed > SECONDS_SLOW:
            slow_count += 1
            print>>slow_file, "tid=%s, title=%s, seconds=%d" % (tid, title, seconds_elapsed)

    except req.ReadTimeout:
        timeout_count += 1
        print "  result: timeout!! \n"
        print>>timeout_file, "tid=%s, title=%s" % (tid, title)

print "==== test end ==== result: total=%d, slow=%d, timeout=%d" % (TEST_TOPIC_COUNT, slow_count, timeout_count)

