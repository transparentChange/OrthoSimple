import sqlalchemy as db
import pandas as pd
import numpy as np

class LanguageReader:
    """
    Provides access to the mapping between the language abbreviations and their full names, as defined by
    the languages.csv file.
    """
    
    def __init__(self):
        self.language_names = pd.read_csv("languages.csv")
        self.language_map = dict({})
        for i in self.language_names.index:
            self.language_map[self.language_names.iloc[i, 0]] = self.language_names.iloc[i, 1]
            
        self.to_abbrev = dict({})
        for i in self.language_names.index:
            self.to_abbrev[self.language_names.iloc[i, 1]] = self.language_names.iloc[i, 0]
    
    def full_name(self, abbreviation):
        if (abbreviation not in self.language_map):    
            raise ValueError(new_language + " is not supported")
        return self.language_map[abbreviation]
    
    def abbrev(self, name_language):
        if (name_language not in self.to_abbrev):
            raise ValueError(new_language + " is not supported")
        
        return self.to_abbrev[name_language]
    
    def all_languages(self):
        return self.language_names["language_name"]

        
class AssociationReader:
    """
    This class provides access to the associations.csv file in various ways.
    Retrieves new character to be inserted, character groups by language, and character mappings
    by groups.
    """
    
    def __init__(self):
        self.language_reader = LanguageReader() 
        
        AssociationReader.plain = "input_char"
        AssociationReader.new = "new_char" 
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

        self.keys_from_groups = pd.read_csv("keybindings.csv")  
        self.summary_bindings()
        
    def get_binding(self, special_group):
        return self.keys_from_groups.loc[self.keys_from_groups["special_group"] == special_group, "first_char"].iloc[0]

    def summary_bindings(self):
        keys_file = open("text_association.txt", "w")
       
        curr_index = 0; 
        while (curr_index != len(self.df_associations)):
            curr_language = self.df_associations.loc[curr_index, "language_abbrev"]
            simple_groups = set(self.keys_from_groups["special_group"])
            
            chars_to_groups = dict({})
            while ((curr_index != len(self.df_associations)) and 
                   (self.df_associations.loc[curr_index, "language_abbrev"] == curr_language)):
                self.__add_group(chars_to_groups, curr_index)
                curr_index += 1
            
            chars_sorted = self.__chars_by_occurence(chars_to_groups)
            RETAIN_ALL = set({"sub_curl", "special", "other"})
            summary = self.__max_occurences(chars_sorted, chars_to_groups, curr_language, RETAIN_ALL)
            
            keys_file.write(self.language_reader.full_name(curr_language) + "\n")
            self.__write_in_order(keys_file, summary, curr_language, RETAIN_ALL)
            
    def __add_group(self, chars_to_groups, curr_index):
        old_char = self.df_associations.loc[curr_index, "input_char"]
        group = self.df_associations.loc[curr_index, "special_group"]
        if old_char not in chars_to_groups:
            chars_to_groups[old_char] = [group]
        else:
            chars_to_groups[old_char].append(group)
    
    def __swap(self, chars_list, pos1, pos2):
        temp = chars_list[pos1]
        chars_list[pos1] = chars_list[pos2]
        chars_list[pos2] = temp
    
    def __chars_by_occurence(self, chars_to_groups):
        chars_sorted = []
        for c in chars_to_groups:
            chars_sorted.append((c, len(chars_to_groups[c])))
        self.__merge_sort(chars_sorted, 0, len(chars_sorted) - 1)
        
        return chars_sorted
     
    def __merge_sort(self, chars_with_freqs, start, end):
        if (start < end):
            middle = (start + end) // 2
            self.__merge_sort(chars_with_freqs, start, middle)
            self.__merge_sort(chars_with_freqs, middle + 1, end)
            
            self.__merge(chars_with_freqs, start, middle, end)
    
    def __merge(self, chars_with_freqs, start, middle, end):
        left = []
        for i in range(start, middle + 1):
            left.append(chars_with_freqs[i])
            
        right = []
        for i in range(middle + 1, end + 1):
            right.append(chars_with_freqs[i])
        
        curr_ind = start
        ind_left = 0
        ind_right = 0
        len_left = middle - start + 1
        len_right = end - middle
        while ((ind_left < len_left) and (ind_right < len_right)):
            if (left[ind_left][1] >= right[ind_right][1]):
                chars_with_freqs[curr_ind] = left[ind_left]
                ind_left += 1
            else:
                chars_with_freqs[curr_ind] = right[ind_right]
                ind_right += 1
            curr_ind += 1
        
        while (ind_left < len_left):
            chars_with_freqs[curr_ind] = left[ind_left]
            ind_left += 1
            curr_ind += 1
        
        while (ind_right < len_right):
            chars_with_freqs[curr_ind] = right[ind_right]
            ind_right += 1
            curr_ind += 1
    
    def __max_occurences(self, chars_sorted, chars_to_groups, language, exception_groups):
        short_summary = dict({})
        
        dest = len(self.language_groups[language])
        for group in self.language_groups[language]:
            short_summary[group] = None
            if (group in exception_groups):
                dest -= 1
        
        num_occurences = 0
        for item in chars_sorted:
            for group in chars_to_groups[item[0]]:
                if ((group in short_summary) and (short_summary[group] is None) and 
                    (group not in exception_groups)):
                    short_summary[group] = item[0]
                    num_occurences += 1
                    if (num_occurences == dest):
                        return short_summary
                    
    def __write_in_order(self, file_out, summary, curr_language, groups_write_all):
        file_out.write("(common)\n")
         
        for group in summary:
            if (group == "other"):
                file_out.write("(also)\n")
            if (group in groups_write_all):
                df_by_group = self.select_char_association(group, curr_language) 
                # relies on uniqueness within column, avoids edge cases with special characters like ı 
                df_by_group[AssociationReader.plain] = df_by_group[AssociationReader.plain].apply(lambda char: char.lower())
                df_by_group = df_by_group.drop_duplicates(subset = [AssociationReader.plain])
                
                for i in range(len(df_by_group)):
                    file_out.write("%s  +%3s  ⇒%3s\n" % (self.get_binding(group),
                        df_by_group.iloc[i, 0], df_by_group.iloc[i, 1]))
            else:
                by_language = self.df_associations.language_abbrev == curr_language
                by_input = self.df_associations.input_char == summary[group]
                by_group = self.df_associations.special_group == group
                pos_match = np.logical_and.reduce((by_language, by_input, by_group)).argmax()
                if (group != "circumflex"):
                    file_out.write("%s  +%3s  ⇒%3s\n" % (self.get_binding(group), summary[group],
                        self.df_associations.iloc[pos_match]["new_char"]))
        file_out.write("\n")
    
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
        
        cols = [AssociationReader.plain, AssociationReader.new]
        association_query = self.df_associations.loc[(self.df_associations["special_group"] == group) &
                                                     (self.df_associations["language_abbrev"] == client_language)][cols]
        uppercase_query = association_query.apply(lambda series: 
                                                  series.apply(lambda char: char.upper()))
        association_query = association_query.append(uppercase_query).drop_duplicates(subset = [AssociationReader.plain])
        return association_query
        #return [association_query[AssociationReader.plain], association_query[AssociationReader.new]] 
        