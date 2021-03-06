# This is written for PYTHON 3
# Don't forget to install requests package

import requests
import json
import datetime
import matplotlib
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.dates as mdates
import matplotlib.cbook as cbook

from datetime import datetime, timedelta

apiKey = '0e5699be695712bf95845e1388604fd4'
	
def main():
	cid = '593958bcceb8abe24251794b'
	first = 'Sherlock'
	last = 'Holmes'
	zipcode = '11111'
	
	aidc = '593958bcceb8abe24251794c'
	aids = '593958bcceb8abe24251794d'
	
 	print checkname(cid, first, last, zipcode)	
 	
 	# List of tuples of the form (account id, nickname, rewards, type, balance)
	accountlist = getaccounts(cid)
	
	# Dictionaries - key is the account id and value is a list of tuples representing withdrawals/deposits
	# Each tuple is of the form (transaction id, date, status, amount)
	withdrawallist = {}
	depositlist = {}
	
	withdrawallist['all'] = []
	depositlist['all'] = []

	for account in accountlist:
		accountid = account[0]
		withdrawallist[accountid] = getwithdrawals(accountid)
		depositlist[accountid] = getdeposits(accountid)
		
		withdrawallist['all'] = withdrawallist['all'] + withdrawallist[accountid]
		depositlist['all'] = depositlist['all'] + depositlist[accountid]
		
		print 'account', accountid, ' is a ', account[3], 'account'
	
	print depositlist[aids]
	
	plot_cashflow(depositlist['all'], None, datetime(2017, 5, 1, 0, 0), 2, 2)
	plot_dayofweek(depositlist['all'], None, datetime(2017, 5, 1, 0, 0))
	return
	

# checks whether customer information is correct
#
# returns 0 and error message if customer information incorrect
# returns 1 and correct message if customer information correct
def checkname(customerId, firstName, lastName, zipcode):
	url = 'http://api.reimaginebanking.com/customers/{}?key={}'.format(customerId, apiKey)

	# Query For Response
	response = requests.get(url)
	
	if response.status_code == 404:
		return -1, 'Customer ID does not exist'
	
	rj = response.json()
		
	rfirst = rj['first_name']
	rlast = rj['last_name']
	rzip = rj['address']['zip']
	
	if rfirst.lower().strip() != firstName.lower().strip():
		return 0, 'Customer Information not correct1'
	elif rlast.lower().strip() != lastName.lower().strip():
		return 0, 'Customer Information not correct2'
	elif rzip != zipcode:
		return 0, 'Customer Information not correct3'
	
	return 1, 'Customer information is correct'


# get the accounts associated with a specific customer id
#
# returns a list of tuples, where each tuple represents an account and contains 
# that account's id, nickname, rewards, type, and balance
def getaccounts(customerId):
	url = 'http://api.reimaginebanking.com/customers/{}/accounts?key={}'.format(customerId, apiKey)

	# Query For Response
	response = requests.get(url)
	
	rj = response.json()

	raccounts = []
	for account in rj:
		atuple = (account['_id'], account['nickname'], account['rewards'], account['type'], account['balance'])
		raccounts.append(atuple)
	
	return raccounts


# get the deposits associated with a specific account id
#
# returns a list of tuples, where each tuple represents a deposit and contains 
# that deposit's id, date made (as a datetime), status, and amount
def getdeposits(accountId):
	url = 'http://api.reimaginebanking.com/accounts/{}/deposits?key={}'.format(accountId, apiKey)

	# Query For Response
	response = requests.get(url)
	
	rj = response.json()

	rdeposits = []
	for deposit in rj:
		dtransactiondate = datetime.strptime(deposit['transaction_date'], '%Y-%m-%d')
		dtuple = (deposit['_id'], dtransactiondate, deposit['status'], deposit['amount'])
		rdeposits.append(dtuple)
		
	return rdeposits


# get the withdrawals associated with a specific account id
#
# returns a list of tuples, where each tuple represents a withdrawal and contains 
# that withdrawal's id, date made (as a datetime), status, and amount

def getwithdrawals(accountId):
	url = 'http://api.reimaginebanking.com/accounts/{}/withdrawals?key={}'.format(accountId, apiKey)

	# Query For Response
	response = requests.get(url)
	
	rj = response.json()

	rwithdrawals = []
	for withdrawal in rj:
		wtransactiondate = datetime.strptime(withdrawal['transaction_date'], '%Y-%m-%d')
		wtuple = (withdrawal['_id'], wtransactiondate, withdrawal['status'], withdrawal['amount'])
		rwithdrawals.append(wtuple)
	
	return rwithdrawals


# Get the total inflow btwn (startDay - windowSize) and startDay
# Also returns the total number of transactions
# If weekday = {0,1,2,3,4,5,6}, include only days that match that day of week (monday = 0)
def getTotalIntake(adeposits, startDay, windowSize, weekday = None):

	intake = 0.0
	count = 0.0
	
	sorted(adeposits, key=lambda x: x[1], reverse=True)
	
	for deposit in adeposits:
		# if date is less than windowSize days before current day
		if startDay - timedelta(days=windowSize) <= deposit[1] and deposit[1] <= startDay:
			if weekday == None or weekday == deposit[1].weekday():
				intake += deposit[3]
				count += 1

	if intake == 0.0:
		return 0.0, 0.0

	return intake, count
	



# Get the total outflow btwn (startDay - windowSize) and startDay
# Also returns the total number of transactions
def getTotalOutflow(awithdrawals, startDay, windowSize, weekday = None):
	return getTotalIntake(awithdrawls, startDay, windowSize, weekday)


# Get the total income btwn (startDay - windowSize) and startDay
# Also returns the total number of transactions
def getTotalIncome(adeposits, awithdrawals, startDay, windowSize, weekday = None):
	intake, incount = getTotalIntake(adeposits, startDay, windowSize, weekday)
	outflow, outcount = getTotalOutflow(awithdrawals, startDay, windowSize, weekday)
	return intake - outflow


# Create a graph from startday to today
# Add a tickmark at every incrementSize number of days
# At each tick, compute total inflow/outflow/income looking back windowSize number of days
def plot_cashflow(adeposits, awithdrawals, startDay, incrementSize, windowSize):
	day = datetime.now()
		
	xcoord = []
	ycoord = []
	
	while day >= startDay:
		xcoord.append(day)
		day = day - timedelta(days=incrementSize)
	
	fig, ax = plt.subplots()
	ax.set_xlabel('Date')

	for x in xcoord:
		
		if adeposits != None and awithdrawals == None:
			ax.set_title('Total Intake vs. Date')
			ax.set_ylabel('Total Intake')
			v, _ = getTotalIntake(adeposits, x, windowSize)
		elif awithdrawals != None and adeposits == None:
			ax.set_title('Total Outflow vs. Date')
			ax.set_ylabel('Total Outflow')
			v, _ = getTotalOutflow(awithdrawals, x, windowSize)
		elif awithdrawals != None and adeposits != None:
			ax.set_title('Total Income vs. Date')
			ax.set_ylabel('Total Income')
			v = getTotalIncome(adeposits, awithdrawals, startDay, windowSize)
		
		ycoord.append(v)
	
	ax.plot(xcoord, ycoord)	
	
	#years = mdates.YearLocator()   # every year
	#months = mdates.MonthLocator()  # every month
	#yearsFmt = mdates.DateFormatter('%Y')

	datemin = startDay
	datemax = datetime.now()
	ax.set_xlim(datemin, datemax)

	plt.show()


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d}'.format(v=val)
    return my_autopct
	
def plot_dayofweek(adeposits, awithdrawals, startDay):
	labels = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
	xcoord = []
	sizes = [0, 0, 0, 0, 0, 0, 0]

	day = datetime.now()

	while day >= startDay:
		xcoord.append(day)
		day = day - timedelta(days=1)
	
	for x in xcoord:
		if adeposits != None and awithdrawals == None:
			plt.title('Pie Chart of Daily Total Intake')
			plt.ylabel('Daily Total Intake')
			for y in range(0,7):
				v, _ = getTotalIntake(adeposits, x, 1, y)
				sizes[y] += v
		elif awithdrawals != None and adeposits == None:
			plt.title('Pie Chart of Daily Total Outflow')
			plt.ylabel('Daily Total Outflow')
			for y in range(0,7):
				v, _ = getTotalOutflow(awithdrawals, x, 1, y)
				sizes[y] += v
		elif awithdrawals != None and adeposits != None:
			plt.title('Pie Chart of Daily Total Income')
			plt.ylabel('Daily Total Income')
			for y in range(0,7):
				v, _ = getTotalIncome(adeposits, awithdrawals, x, 1, y)
				sizes[y] += v

	# ax1.pie(sizes, labels=labels, autopct=make_autopct(sizes), shadow=False, startangle=90)
	plt.bar([0, 1, 2, 3, 4, 5, 6], sizes, align='center')
	plt.xticks([0, 1, 2, 3, 4, 5, 6], labels)
	# ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

	plt.show()
		
	
		

if __name__ == '__main__':
	main()
