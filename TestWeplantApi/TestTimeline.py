import requests as req
import datetime
import sys

TEST_USER_LIST = [
    {'phone': '13925285765', 'password': '123456',      'token': '4f966eecbd4ce3fba1779810ed21e98c'},
    {'phone': '17777777777', 'password': 'whz20141212', 'token': '75354a8f6391a758aaeefa5882457b50'},
    {'phone': '15555555555', 'password': 'whz20141212', 'token': '70ac3e8351dfe2a75a2a076666c8ea5f'},
    {'phone': '11255555555', 'password': 'whz20141212', 'token': '2c8a8b0693e1c3f10e389f00eeb2d48f'},
]
HOST = "http://wohuizhong.com/api/"
SECONDS_TIMEOUT = 10
SECONDS_SLOW = 6
TEST_TOPIC_COUNT = 30


def test_api(user_index, api_ver):
    if user_index >= len(TEST_USER_LIST):
        print "id out of range, max is " + str(len(TEST_USER_LIST) - 1)

    timeout_file = open('id_%d_timeout.txt' % user_index, 'w+')
    slow_file = open('id_%d_slow.txt' % user_index, 'w+')
    timeout_count = 0
    slow_count = 0
    index = 0
    test_user = TEST_USER_LIST[user_index]
    param_token = "?token=" + test_user['token']

    print "== test begin ===, timeline_api=v%s, user=%s" % (api_ver, test_user['phone'])
    print "sign in..."
    r = req.post(HOST + 'sign/in', data=test_user)
    if r.status_code != 200:
        print "signIn failed"
        return

    print "fetch topic...\n"
    topics = req.get(HOST + 'explore/topic/0/50000').json()['list']

    for topic in topics[0:TEST_TOPIC_COUNT]:
        tid = str(topic['tid'])
        title = topic['title'].encode('utf8')

        print "(%d/%d) topic = %s, %s" % (index, TEST_TOPIC_COUNT, tid, title)
        index += 1
        print "  step1. focus"
        req.post(HOST + 'focus/topic/' + tid + param_token)

        try:
            print "  step2. timeline"
            api_timeline = HOST + 'timeline/v%s/0/0%s' % (api_ver, param_token)

            time_begin = datetime.datetime.now()
            r = req.get(api_timeline, timeout=SECONDS_TIMEOUT)
            if r.status_code != 200:
                print "  result: failed! status_code=%d \n" % r.status_code
                print>>timeout_file, "tid=%s, title=%s, status_code=%d" % (tid, title, r.status_code)
                continue

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


if __name__ == '__main__':
    user_index = 0
    api_ver = 2.4

    if len(sys.argv) >= 2:
        user_index = sys.argv[1]

    if len(sys.argv) >= 3:
        api_ver = sys.argv[2]

    test_api(int(user_index), api_ver)
