from instagram_private_api import Client, ClientCompatPatch
import importlib
import api_requests
importlib.reload(api_requests)
from api_requests import (BasicUserInfo, PublicUserInfoRequests, MediaInfoRequests, 
							InteractWithUsersActions, CollectDataThroughHashtags)

import time

user_name = 'cuteanimalzzzz123'
password = 'instabotOP'

api = Client(user_name, password)
results = api.feed_timeline()

test_usernames = [#'ryanlopezzzz', too many followers... API timed out rofl
				  'xubryana',
				  #'scottt_tam' 
				  ]


def test_basic_user_info(username):
	"""
	Can check against true values by going onto Instagram app.
	"""
	basic_user_info = BasicUserInfo(api, username)
	print("User Id: " + str(basic_user_info.user_id))
	print("Follow count: " + str(basic_user_info.follower_count))
	print("Following count: " + str(basic_user_info.following_count))
	print("Media count: " + str(basic_user_info.media_count))
	print("Private status: " + str(basic_user_info.private_status))


def naive_followback_probability(username):
	"""
	Naively computes the followback probability by considering follower/following ratio. <1 means more following than followers, which is better
	"""
	basic_user_info = BasicUserInfo(api, username)
	return basic_user_info.follower_count / basic_user_info.following_count

def remove_private_accs_from_followers(username):
	"""
	Returns an array of the list of followers of a given username without private accounts
	"""
	cleaned_list = []
	puir = PublicUserInfoRequests(api, username)
	followers_usernames = puir.get_followers_usernames()
	for i in range(len(followers_usernames)):
		basic_user_info = BasicUserInfo(api, followers_usernames[i])
		if(basic_user_info.private_status == False):
			cleaned_list.append(followers_usernames[i])
	return cleaned_list

def remove_private_accs_from_following(username):
	"""
	Returns an array of the list of following of a given username without private accounts
	"""
	cleaned_list = []
	puir = PublicUserInfoRequests(api, username)
	following_usernames = puir.get_following_usernames()
	for i in range(len(following_usernames)):
		basic_user_info = BasicUserInfo(api, following_usernames[i])
		if(basic_user_info.private_status == False):
			cleaned_list.append(following_usernames[i])
	return cleaned_list

def less_naive_followback_probability(username):
	new_follower = remove_private_accs_from_followers(username)
	new_following = remove_private_accs_from_following(username)
	return (len(new_follower) / len(new_following))



def compute_follower_ratio(username):
	"""
	Calculates the follower/following ratio of a given username's list
	"""
	puir = PublicUserInfoRequests(api, username)
	
	followers_usernames = puir.get_followers_usernames()
	assert(puir.follower_count == len(followers_usernames))
	for i in range(len(followers_usernames)):
		print('Follower Ratio of '+ str(followers_usernames[i])+': ', naive_followback_probability(followers_usernames[i]))

def optimal_followers(username):
	"""
	Given a username, return the optimal people to follow on their followers list
	"""
	pre = remove_private_accs_from_followers(username)
	post = []
	for i in range(len(pre)):
		if(naive_followback_probability(pre[i])<1):
			post.append(pre[i])
	return post



t = time.process_time()
for username in test_usernames:
	
	print("Username: " + username)
	#print(remove_private_accs_from_following(username))
	#print(remove_private_accs(username))
	#compute_follower_ratio(username)
	#print('List of Optimal People to Follow from '+ username+':', optimal_followers(username))
	print(less_naive_followback_probability(username))
	print("-"*100)

elapsed_time = time.process_time() - t
print('Time Taken: ', elapsed_time)
	