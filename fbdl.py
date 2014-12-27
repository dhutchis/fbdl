"""
Downloads JSON from a user/group/page. Input a Facebook Graph API node ID. Also give your authentication token.
See for guidance: https://developers.facebook.com/tools/explorer
Helpful for viewing JSON: http://jsonviewer.stack.hu/
Modified from tool by yuzawa-san: fbfeed2csv: a tool to download all posts from a user/group/page's facebook feed to a csv file
"""

import json
import urllib2
import time
import csv
import re
import argparse
import sys
import urlparse

# until moves back on next page if there are more results
# since disappears
# until stays same if no more results

def loadPage(url, since, until):
    if until != None and since != None and (int(since) > int(until)):
        return []

    par = urlparse.urlparse(url)
    parq = urlparse.parse_qs(par.query)
    if not('since' in parq) and since != None:
        url += "&since="+since
    if until != None:
        if 'until' in parq:
            #print "parq[UNTIL]: ", parq['until'][0]
            if int(parq['until'][0]) == int(until): # query stayed same
                return []
            else:
                until = parq['until'][0]
        else:
            url += "&until="+until

    # delay
    time.sleep(0.11)

    # download
    #print "URL: ",url
    response = urllib2.urlopen(url)
    content = response.read()
    payload = ''
    #print "DOWNLOAD!"
    #print('.'),
    sys.stdout.write('.')
    sys.stdout.flush()
    try:
        payload = json.loads(content)
        #with open('test.json','wb') as testf:
        #    json.dump(payload,testf)
        #print payload
    except:
        print "JSON decoding failed!"
    return payload

def countLikes(payload, since, until):
    count = 0
    if 'data' in payload:
        count = len(payload['data'])
    if 'paging' in payload and 'next' in payload['paging']:
        count += countLikes(loadPage(payload['paging']['next'], since, until), since, until)
    return count

def parseJSON(payload, since, until):
    if 'data' in payload:
        out = []
        for post in payload['data']:
            if 'message' in post:
                #print "COMMENTS:"
                #print post['comments']
                # make timestamp pretty
                #timestamp = post['created_time']
                #timestamp = re.sub(r'\+\d+$', '', timestamp)
                #timestamp = timestamp.replace('T',' ')
                #out.append({
                #    'author': post['from']['name'],#.encode('ascii', 'ignore'),
                #    #'timestamp': timestamp,
                #    'created_time': timestamp,
                #    'message': post['message'],#.encode('ascii', 'ignore').replace("\"","\\\"")
                #    'comments': post['comments']
                #    })
                #print "POST:"
                #print post
                subd = dict()
                subd['id'] = post['id']
                subd['from'] = post['from']
                subd['created_time'] = post['created_time']
                subd['message'] = post['message']
                if 'like_count' in post:
                    subd['like_count'] = post['like_count']
                elif 'likes' in post and 'data' in post['likes']:
                    subd['like_count'] = countLikes(post['likes'], since, until)
                if 'comments' in post:
                    subd['comments'] = parseJSON(post['comments'], since, until)
                #print "subd:"
                #print subd
                out.append(subd)
        #out2 = []
        if 'paging' in payload and 'next' in payload['paging']:
            #print "PAGING:"
            #print payload['paging']
            nextpage = payload['paging']['next']
            out2 = parseJSON(loadPage(nextpage, since, until), since, until)
            return out + out2
        else:
            return out
    return []


# entry point:

# get args
parser = argparse.ArgumentParser()
parser.add_argument('id', help='ID of Graph API resource')
parser.add_argument('-o', '--out', default="fbdump.json", help='Output file')
parser.add_argument('-t', '--token', help='Authentication token')
parser.add_argument('-e', '--extra', help='Extra arguments')
parser.add_argument('-i', '--input', help='Read input arguments from file')
parser.add_argument('-s', '--since', help='[Since] Begin timestamp')
parser.add_argument('-u', '--until', help='[Until] End timestamp')
args = parser.parse_args()
#print "ARGS:"
#print args
if args.input != None:
    with open(args.input,'r') as fin:
        data = fin.read()
        #print "DATA split:"
        #print data.split()
        args = parser.parse_args(args=data.split(),namespace=args)
        #print "NEW ARGS:"
        #print args

try:
    out = parseJSON(loadPage("https://graph.facebook.com/%s/feed?fields=id,from,message,created_time,comments,likes&access_token=%s%s" 
                             % (args.id, args.token, args.extra if args.extra != None else ""), args.since, args.until), args.since, args.until)
    # write output to file
    f = open(args.out,'wb')
    #w = csv.DictWriter(f,['author','timestamp','message'])
    #w.writerows(out)
    json.dump(out,f)
    f.close()
    sys.exit(0)
except urllib2.HTTPError as e:
    print "Download failed:",e
    error_message = e.read()
    print error_message
    sys.exit(1)
except KeyboardInterrupt:
    print "Canceled!"
    sys.exit(2)
