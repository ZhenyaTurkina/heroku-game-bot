import pymorphy2
import numpy as np

import re
import pickle

morph = pymorphy2.MorphAnalyzer()


def get_tags(word):
    parse_word = morph.parse(word)[0]
    pos = parse_word.tag.POS
    animacy = parse_word.tag.animacy
    aspect = parse_word.tag.aspect
    case = parse_word.tag.case
    gender = parse_word.tag.gender
    involvement = parse_word.tag.involvement
    mood = parse_word.tag.mood
    number = parse_word.tag.number
    person = parse_word.tag.person
    tense = parse_word.tag.tense
    transitivity = parse_word.tag.transitivity
    voice = parse_word.tag.voice


    tags = set()
    for tag in [pos, animacy, aspect, case,
               gender, involvement, mood, number,
               person, tense, transitivity, voice]:
        if tag is not None:
            tags.add(str(tag))
    return tags


def replace_words(sentens):
    words = re.findall(r"[А-Яа-я]+", sentens)
    word_2_replace_count = max(1, int(len(words) * 0.1))
    
    index = np.random.choice(range(len(words)), size=word_2_replace_count, replace=False)
    
    for i in index:
        word = sentens[i]
        
        parse_word = morph.parse(words[i])[0]

        pos = str(parse_word.tag.POS)
        tags = get_tags(word)

        rnd_index  = np.random.choice(range(len(pos_map[pos])),  size=len(pos_map[pos]), replace=False)
        new_word = None
        for ind in  rnd_index[:500]:
            rnd_word = pos_map[pos][ind]
            parse_rnd_word = morph.parse(rnd_word)[0]
            new_word = parse_rnd_word.inflect(tags)
            
            if new_word is not None:
                break
        
        if new_word is  None:
            continue
            
        sentens = sentens.replace(words[i], new_word.word)
    
    return sentens


def  get_sample(sentenses, count ):
    

    indexes = np.random.choice(range(len(sentenses)), size=count, replace=False)

    sample = np.array(final_sentenses)[indexes]

    final_sentens = []
    for i in range(count //2):
        cur_sentens = sample[i].strip()

        final_sentens.append((replace_words(cur_sentens), True))

    for i in range(count //  2, count):
        final_sentens.append((sample[i].strip(), False))
    
    final_sentens = np.array(final_sentens)
    index_shuffle = np.random.choice(range(count), size=count, replace=False)
    return final_sentens[index_shuffle]


with open('final_sentenses.pkl','rb') as f:
    final_sentenses = pickle.load(f)

with open('pos_map.pkl', 'rb') as f:
    pos_map = pickle.load(f)


game_sets = []

for i in  range(500):
    game_sets.append((get_sample(final_sentenses, 10).tolist()))
game_sets = list(game_sets)

with open('games_precalc.pkl', 'wb') as f:
    pickle.dump(game_sets, f)