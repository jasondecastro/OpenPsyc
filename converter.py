from mongoTools import *

dbName, tableName = "ANS"


subject = "Subject"
posts = MongoAdmin(dbName).getTable(tableName).posts
s_ids = posts.distinct(str(subject)) 

for s_id in s_ids:
    for row in posts.find({str(subject) : s_id}):
        try:
	    if row['Stimulus_RESP'] == row['CorrectResp']:	
		row['ACC'] = 1
	    else:
		row['ACC'] = 0
	except KeyError:
	    print "Skipping row, no key"
	except:
	    raise
	    print row
	    posts.save(row)
