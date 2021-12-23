"""
Here we calculate an interaction score between 0 (will not interact with us) and 1 (will interact with us).
We want a user is active, so posts a lot (media_score) and somebody worthy of following (follower_score) 
and tends to follow more users than follow them (confidence_lower_bound)
"""
import numpy as np

def get_media_score(user_table):
    """
    Returns a value between 0 (no posts) and 1 (infinite posts)
    """
    media_count = user_table['media_count']
    media_score = (2/np.pi)*np.arctan(media_count)
    return media_score

def get_follower_score(user_table):
    """
    Returns a value between 0 (no followers) and 1 (infinite followers)
    """
    follower_count = user_table['follower_count']
    follower_score = (2/np.pi)*np.arctan(follower_count/100)
    return follower_score
    
def get_confidence_lower_bound(user_table):
    """
    We model the probability p = num_following / (num_following + num_followers) with a binomial distribution
    and obtain the lower bound for a 95% confidence interval.
    """
    following_count = user_table['following_count']
    follower_count = user_table['follower_count']
    total_follow_count = following_count+follower_count
    p_hat = following_count / total_follow_count
    std_dev_hat = np.sqrt((p_hat * (1-p_hat)) / total_follow_count)
    z_score = 1.96 #for 95% confidence interval
    confidence_lower_bound = p_hat - z_score*std_dev_hat
    
    #make sure confidence interval bound is inside of [0,1]
    confidence_lower_bound.loc[confidence_lower_bound < 0] = 0
    confidence_lower_bound.loc[confidence_lower_bound > 1] = 1
    
    return confidence_lower_bound

def get_interaction_score(user_table):
    media_score = get_media_score(user_table)
    follower_score = get_follower_score(user_table)
    confidence_lower_bound = get_confidence_lower_bound(user_table)
    interaction_score = (media_score+follower_score+confidence_lower_bound)/3
    return interaction_score
    
def rank_for_interactions(user_table):
    user_table = user_table[user_table['private_status'] == False].copy() #only interact with public
    user_table['interaction_score'] = get_interaction_score(user_table)
    return user_table