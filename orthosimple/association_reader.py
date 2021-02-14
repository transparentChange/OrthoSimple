import sqlalchemy as db
import pandas as pd

class Reader:
    """
    This class provides access to the associations.csv file in various ways.
    Retrieves new character to be inserted, character groups by language, and character mappings
    by groups.
    """
    
    def __init__(self):
        Reader.plain = "input_char"
        Reader.new = "new_char" 
        self.df_associations = pd.read_csv("associations.csv")
        
        unique_groups = self.df_associations.drop_duplicates(subset = ["special_group", "language_abbrev"])
        groups_col = unique_groups["special_group"]
        language_col = unique_groups["language_abbrev"]
        self.language_groups = dict({})
        for (item, language) in zip(groups_col, language_col):
            if (language in self.language_groups):
                self.language_groups[language].append(item)
            else:
                self.language_groups[language] = [item]  

    def select_new_char(self, input_char, accent_type):
        """
        Returns the new character associated with input_char and accent_type from self.df_associations.
        """
        
        new_char_table = self.df_associations.loc[(self.df_associations["special_group"] == accent_type) &
                                                  (self.df_associations["input_char"] == input_char)]
        return new_char_table["new_char"].iloc[0]
    
    def get_groups(self, language):
        """
        A getter for the language_groups field that returns a list of all
        the accent types for a given language.
        """
        
        return self.language_groups[language]
    
    def select_char_association(self, group, client_language):
        """
        Returns a 2d-array that contains the input character and character that it is being mapped to
        for each character in client_language with its special_group attribute equal to group.
        """
        
        cols = [Reader.plain, Reader.new]
        association_query = self.df_associations.loc[(self.df_associations["special_group"] == group) &
                                                     (self.df_associations["language_abbrev"] == client_language)][cols]
        uppercase_query = association_query.apply(lambda series: 
                                                  series.apply(lambda char: char.upper()))
        association_query = association_query.append(uppercase_query).drop_duplicates(subset = [Reader.plain])
        return [association_query[Reader.plain], association_query[Reader.new]] 