import pandas as pd
from collections import defaultdict
import math
from copy import deepcopy
import numpy as np 

class Head_to_head():
    def __init__(self, fixtures, target):
        self.fixtures = fixtures.reset_index().sort_values(by=['date'])
        self.target = target
        h_2_h = {}
        for p_1 in fixtures.player_1.unique():
            h_2_h[p_1] = {}
            for p_2 in fixtures.player_2.unique():
                h_2_h[p_1][p_2] = {'wins':0,
                                   'losses':0}
        self.h_2_h = h_2_h
    
    def process_fixture(self, i, fixture):
        self.fixtures.at[i, 'h_2_h_wins'] =self.h_2_h[fixture.player_1][fixture.player_2]['wins']
        self.fixtures.at[i, 'h_2_h_losses'] =self.h_2_h[fixture.player_1][fixture.player_2]['losses']      
    
        if fixture[self.flipped_flag] == 1:
            if fixture[self.target == 0]:
                self.h_2_h[fixture.player_1][fixture.player_2]['wins']+=1
                self.h_2_h[fixture.player_2][fixture.player_1]['losses']+=1
           
            else:
                self.h_2_h[fixture.player_1][fixture.player_2]['losses']+=1
                self.h_2_h[fixture.player_2][fixture.player_1]['wins']+=1

      
    
    def process_all_fixtures(self):
        '''
        Processes all fixtures - updating ratings, and fixture
        Returns:
            (fixtures, ratings)
                fixtures:
                    updates every fixture in which target not null with:
                        rating of player_1 and difference vs. player_2 BEFORE the fixture occured
                        expectation of player_1's score BEFORE the fixture occured
                rating_1:
                    ratings of all players AFTER the all the fixtures have been incorporated
        '''
        for i, f in self.fixtures.iterrows():
            if not math.isnan(f[self.target]):
                self.process_fixture(i, f)
        self.fixtures['h_2_h_count'] = self.fixtures['h_2_h_wins'] + self.fixtures['h_2_h_losses']
        self.fixtures['h_2_h_ratio'] = self.fixtures['h_2_h_wins'] / (self.fixtures['h_2_h_losses']+self.fixtures['h_2_h_wins'])
        self.fixtures.loc[self.fixtures.h_2_h_count == 0, 'h_2_h_count'] = np.nan
        
        return (self.fixtures.loc[:,['index',
                                    'h_2_h_wins',
                                    'h_2_h_losses',
                                    'h_2_h_count',
                                    'h_2_h_ratio',
                                   ]], 
                self.h_2_h)


class ELO():
    '''
    Takes a dataframe of fixtures, and a target variable and 
    calculates the ELO ratings of each player.
    
    Because of analysis methodology, only works on data with every fixture 'flipped',
    adding duplicate entries with player_1, player_2 and target reversed for every fixture
        
    Intialisation Args
        fixtures (pandas df) - the matches for which ELO ratings are generated
            requried columns:
                date (datetime)  
                player_1, player_2 (string) - must uniquely identify players
                TARGET (binary or float between 1 and 0) attribute of player_1 that is being rated 
        target (string) - name of the TARGET atribute of player_1 that is being rated
        
        optional:
            k_factor (numeric) - maximum ratings can change in one fixture
            initial_ratings (dictionary) - players ratings from before fixtures started, assumed to be zero
    Attributes:
        fixtures - matches being rated
        target - attribute of player_1 that is being rated
        k_factor (numeric) - maximum ratings can change in one fixture
        ratings_1, ratings_2 - current ratings of players
    '''
    def __init__(self, fixtures, target, k_factor=15.0, initial_ratings = {}, ):
        self.fixtures = fixtures
        self.target = target
        self.k_factor = k_factor
        self.ratings = defaultdict(lambda: 1200)
        self.ratings.update(initial_ratings)

    def process_fixture(self, i, fixture):
        '''
        Processes a single fixture - updating ratings, and fixture
        Args:
            i (int) index of the fixture.
            fixture (dataframe row) fixture details.
        Effects:
            updates self.fixtures with:
                rating of player_1 and difference vs. player_2 BEFORE the fixture occured
                expectation of player_1's score BEFORE the fixture occured
            updates self.ratings, with:
                ratings of player_1/2 AFTER the fixture occured
                oppent given opp_ prefix, to avoid double-counting
        '''
        e_1, rating_1, rating_2 = self.elo_calc(player_1=fixture.player_1, 
                                                player_2=fixture.player_2, 
                                                outcome=fixture[self.target])
        self.fixtures.at[i, 'rating_1'] = self.ratings[fixture.player_1]
        self.fixtures.at[i, 'rating_2'] = self.ratings[fixture.player_2]
        self.fixtures.at[i, 'rating_diff'] = (self.ratings[fixture.player_1] - 
                                                            self.ratings[fixture.player_2])
        self.fixtures.at[i, f'e_{self.target}'] = e_1
        self.ratings[fixture.player_1] = rating_1
        self.ratings[fixture.player_2] = rating_2

    def process_all_fixtures(self):
        '''
        Processes all fixtures - updating ratings, and fixture
        Returns:
            (fixtures, ratings)
                fixtures:
                    updates every fixture in which target not null with:
                        rating of player_1 and difference vs. player_2 BEFORE the fixture occured
                        expectation of player_1's score BEFORE the fixture occured
                rating_1:
                    ratings of all players AFTER the all the fixtures have been incorporated
        '''
        for i, f in self.fixtures.iterrows():
            if not math.isnan(f[self.target]):
                self.process_fixture(i, f)

        return (self.fixtures,
                self.ratings)

    def elo_calc(self, player_1, player_2, outcome):
        '''
        Arguments:
            player_1, player_2 (string) - players being evaluated
        
            outcome (numeric) - outcome being evaluated (between 0-1 or binary)
        Returns:
            (e1, rating_1, rating_2)
            e1 (float) expecation of player_1 for target variable BEFORE match occurs
            rating_1, rating_2 (float) - ratings of players AFTER match occurs
        '''
        rating_1 = self.ratings[player_1]
        rating_2 = self.ratings[player_2]
        q1 = 10.0 ** (rating_1/400)
        q2 = 10.0 ** (rating_2/400)
        e1 = q1/(q1+q2)      
        rating_1 += (outcome-e1)*self.k_factor
        rating_2 += (e1-outcome)*self.k_factor
        return e1, rating_1, rating_2

