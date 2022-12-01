import pandas as pd
import numpy as np
import re
import pyreadr
from nltk import sent_tokenize
from string import punctuation
import os

class PreProAnno:
    def __init__(self, notes_list):
        self.__welcome__()
        self.notes_list = notes_list
        self.clean_notes_list = []
        
    def __welcome__(self):
        print('Welcome to notes preprocessor which is used before annotation project. \n',
             'You can use this function clean up your clinical notes and \n',
             'select the notes that contains the most mention of concepts \n',
             'that you want to annotate')
    def get_notes(self,original = False):
        return (self.notes_list if (original or self.clean_notes_list==[]) 
                    else self.clean_notes_list)
    
    def __note_cleanup__(self,text):
        text = re.sub(r'\r\n',r' ',text)
        text = re.sub(r'\r',r'\n',text)

        text = re.sub(r',([A-Z])',r'\n\1',text)

        text = re.sub(r'(\s+\.)', r'. ', text)
        text = re.sub(r'(\s+\,)', r', ', text)
        text = re.sub(r'(\.\s*\,)|(\s*\,\s*\.)|(^/d(\.\s*)+)', r'. ', text)

        text = re.sub(r"\\[Xx].*?\\", " ", text)

        text = re.sub(r"(.*)\?(.*[A-Za-z]+)",r"\1 \2",text)

        text = re.sub(r"'",r"",text)
        text_list = list(map(lambda x: sent_tokenize(x),text.split('\n')))
        text = '. '.join([item.strip(punctuation) for sublist in text_list for item in sublist])

        return text+'.'
    def notes_cleanup(self):
        for note in self.notes_list:
            self.clean_notes_list.append(
                self.__note_cleanup__(note))
        return self.clean_notes_list
    
    def __keyword_freq__(self, note,keyword_dict):
        score = 0
        for keyword in keyword_dict:
            for value in keyword_dict[keyword]:
                score += note.lower().count(value)
        return score

    def __note_ranking__(self, notes_list, keyword_dict):
        score_list = []
        for note in notes_list:
            score_list.append(self.__keyword_freq__(note, keyword_dict))
        df = pd.DataFrame(data={'notes': notes_list,
                            'scores': score_list})  
        return df.sort_values(by=['scores'], ascending = False)

    def notes_selector(self, keyword_dict, num, clean = True):
        if clean:
            notes_list = self.notes_cleanup()
            print('Notes has been cleaned, if you dont want this,please set clean = False')
        else: 
            notes_list = self.notes_list
        note_df = self.__note_ranking__(notes_list, keyword_dict)
        return note_df[:num].notes.tolist()
    def save_ktop_notes(self, keyword_dict, num, path = './anno_files', clean = True):
        knotes_list = self.notes_selector(keyword_dict,num,clean)
        if not os.path.exists(path):
            os.makedirs(path)
        for i, note in enumerate(knotes_list):
            with open(path+'/notes_{}'.format(i), "w") as text_file:
                text_file.write(note)
