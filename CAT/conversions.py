#show_conversion.py

import sys
import problem
import pylab

sid = sys.argv[1]

DB="CAT3"

pre = problem.Problems(DB, sid)
post = problem.Problems(DB, sid, exp="post")

for pid in post.distinct('id'):
	PRE = pre.query({'kind':'verified', 'id':pid})
	POST = post.query({'kind':'verified', 'id':pid})

	#find calc-mems
	if PRE.count() and POST.count():
		pre_strat = PRE[0]['strat']
		post_strat = POST[0]['strat']

		if pre_strat == post_strat:
			conversion = pre_strat
		else:
			conversion = pre_strat + "|" + post_strat

		pre.update({'id':pid}, {'$set': {'conversion': conversion}})
		post.update({'id':pid}, {'$set': {'conversion': conversion}})


	#find calc-calc-mems	
	if PRE.count():
		POST = post.query({'kind':'erratic', 'id':pid})
		if POST.count():
			print POST[0]['strat']
			print POST[0]['history']
			conv = ""
			for h in POST[0]['history'][:2]:
				conv = "%s%s-" % (conv, h['strat'])
			conv = conv.rstrip('-')
			conversion = "%s|%s" % (PRE[0]['strat'], conv)
			
			pre.update({'id':pid}, {'$set': {'conversion': conversion}})
			post.update({'id':pid}, {'$set': {'conversion': conversion}}) 


#print pre.count({'conversion':'calc-mem'})
for conv in post.distinct('conversion'):
	print conv, post.count({'conversion':conv})
