from collections import Counter
import numpy as np
from copy import deepcopy
import matplotlib.pyplot as plt
import random
from IPython.display import clear_output

class Tournament:
    def __init__(self, ratings, tree, k_factor=5):
        self.ratings = ratings
        self.tree = tree
        self.k_factor = k_factor

    def sim_tournament(self, tree):
        """
        Recursive simulate tournament rounds. Takes tree - draw fixtures in nested list. 
        """
        # Base case (single game)
        if isinstance(tree[0], str):
            return self.sim_game_and_update_elos(tree)

        # Else, simulate both 1st and 2nd half of draw, and combine
        else:
            first_half = self.sim_tournament(tree[0])
            second_half = self.sim_tournament(tree[1])
            combined = [first_half, second_half]
            return self.sim_tournament(combined)

    def get_win_prob(self, team_1, team_2):
        """
        Gets the chance of first team winning, 
        given two teams current elo ratings
        formula for elo: e1 = 10^(r1/400)/[10^(r1/400) + 10^(r2/400)]
        """
        rating_1 = self.ratings[team_1]/400
        rating_2 = self.ratings[team_2]/400
        q1 = 10.0 ** rating_1
        q2 = 10.0 ** rating_2
        return q1/(q1+q2)
    
    def sim_game_and_update_elos(self, teams):
        """
        Sims a game between two teams, returning name of winning team. 
        Also updates elo values (hot sim)
        """        
        team_1, team_2 = teams
       
        # How likely is 1st team to win
        win_prob = self.get_win_prob(team_1, team_2)
        outcome = np.random.binomial(n=1, p=1.0-win_prob)
        
        # Update both winner and loser ratings
        self.ratings[team_1] += (outcome-win_prob)*self.k_factor
        self.ratings[team_2] += (win_prob-outcome)*self.k_factor
        
        # Return winner's name
        if outcome == 0:
            return team_1
        else:
            return team_2


class League:
    def __init__(self, ratings, standings, fixtures, k_factor=5, draw_rate=0.3,home_advantage=0.2):
        self.ratings = ratings
        self.standings = standings
        self.fixtures = fixtures
        self.k_factor = k_factor
        self.draw_rate = draw_rate
        self.home_advantage = home_advantage

    def sim_league(self):
        '''
        Simulates a league's final standings:
            returns - standings: dict - teams' points totals
                    rankings:    dict - teams' league positions
        NOTE - doesn't account for goal difference
        '''
        for teams in self.fixtures:
            self.sim_game(teams)
        
        # Add random small number, instead of goal difference
        for k in self.standings.keys():
            self.standings[k] += (random.random() * 0.0001)

        final_rankings = {} 
        r = 0
        for i in dict(sorted(self.standings.items(), 
                        key=lambda k: k[1], reverse=True)):
            r += 1
            final_rankings[i] = r
        return self.standings, final_rankings

    def get_outcome_probs(self, team_1, team_2):
        """
        Gets the chance of first team winning, drawing or losing
        given two teams current elo ratings
        formula for elo: e1 = 10^(r1/400)/[10^(r1/400) + 10^(r2/400)]
        
        drawing rate = self.draw_rate (except when winning/ losing chance is below draw rate,
        where it it 1/2 winning/losing chance). This means proportion of draws will be slightly lower
        than draw rate
        """
        rating_1 = self.ratings[team_1]/400
        rating_2 = self.ratings[team_2]/400
        q1 = 10.0 ** rating_1
        q2 = 10.0 ** rating_2
        e1 = q1/(q1+q2)

        e1 += ((1-e1) * self.home_advantage)
        
        # Constant draw rate, except in cases where winning/losing prob exceeds draw rate
        # Leads to a hill shaped draw prob, increasing linearly, flat, and then decreasing
        if e1 < self.draw_rate:
            draw_1 = e1 / 2
        elif e1 > (1.0 - self.draw_rate):
            draw_1 = (1 - e1) / 2
        else:
            draw_1 = self.draw_rate
        
        win_1 = e1 - (draw_1 / 2)
        return e1, (win_1, draw_1, 1.0 - win_1 - draw_1)
    
    def sim_game(self, teams):
        """
        Sims a game between two teams, updating standings table
        Also updates ratings (hot sim)
        """        
        team_1, team_2 = teams
       
        # How likely is 1st team to win
        e_1, probs = self.get_outcome_probs(team_1, team_2)
        outcome = np.random.choice(a=[1,0.5,0],size=1, p=probs)[0]
        
        # Update both winner and loser ratings
        self.ratings[team_1] += (outcome-e_1)*self.k_factor
        self.ratings[team_2] += (e_1-outcome)*self.k_factor
        
        # Update league
        if outcome == 1:
            self.standings[team_1] += 3
        if outcome == 0.5:
            self.standings[team_1] += 1
            self.standings[team_2] += 1
        else:
            self.standings[team_2] += 3
        return outcome

def sim_multiple_tournaments(tree, elo_dict, n=10000):
    "Simulates tournament n times, returns each team's win % in counter" 
    # Count number of wins
    win_count = Counter()
    for i in range(n):
        # Reset 'latest elos' every time
        tourn = Tournament(ratings=deepcopy(elo_dict), tree=tree)
        winner = tourn.sim_tournament(tree)
        # Increment winner by % of total sims
        win_count[winner] += (100.0/n)
    return win_count

def sim_multiple_leagues(ratings, standings, fixtures, sample_num, 
                         k_factor =5, draw_rate =0.3,home_advantage=0.2):
    '''
    Simulates tournament multiple times
    returns:
        list of dictionaries - points totals
        list of dictionaries - league positions
    '''
    points_totals = []
    rankings = []
    for i, _ in enumerate(range(sample_num)):
        if i % 1000 == 0: 
            clear_output()
            print(f'{i}/{sample_num}')
        l = League(ratings=deepcopy(ratings),
              standings=deepcopy(standings),
              fixtures=deepcopy(fixtures),
              k_factor=k_factor,
              draw_rate=draw_rate)
        final_points, final_rankings = l.sim_league()
        points_totals.append(final_points)
        rankings.append(final_rankings)
    return points_totals, rankings


def plot_counter(plt_data, title):
    '''
    Creates bar plot of win probs from a dictionary/counter
    '''
    labels, values = zip(*sorted(plt_data.items()))
    indexes = np.arange(len(labels))
    plt.bar(indexes, values, 1)
    plt.xticks(indexes, labels, rotation=90)
    plt.ylabel("Tournament win prob. (%)")
    plt.title(title)
    plt.show()

def plot_series(labels, values, title):
    '''
    Create a bar plot of outcome probabilities from a series of values, and labels
    '''
    indexes = np.arange(len(labels))
    plt.bar(indexes, values, 1)
    plt.xticks(indexes, labels, rotation=45)
    plt.ylabel("prob. (%)")
    plt.title(title)
    plt.show()
    
    
def flatten_draw(draw):
    flattened = []
    if type(draw[0]) == str:
        return draw
    else:
        return flatten_draw(draw[0]) + flatten_draw(draw[1])