import os
import pickle
import tagger

datafile = os.path.join(os.path.dirname(__file__), '..', 'data/dict.pkl')
# print datafile
weights = pickle.load(open(datafile, 'rb'))
rdr = tagger.Reader()
stmr = tagger.Stemmer()
rtr = tagger.Rater(weights)

extract_tags = tagger.Tagger(rdr, stmr, rtr)
