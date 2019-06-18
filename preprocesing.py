if __name__  == "__main__":
    import pymorphy2
    import pickle
    import re
    import copy
    
    morph = pymorphy2.MorphAnalyzer()
    
    print('start load...')
    with open('./1grams-3.txt', 'r', encoding='utf-8') as f:
        words = f.readlines()

    print('start calc word in base...')
    pos_map = {}
    for num_word in words:
        _, word = num_word.split()

        word = word.lower()
        parse_word = morph.parse(word)[0]
        if parse_word.score < 0.95 or re.match(r"^[А-Яа-я]+$", parse_word.word) is None:
            continue
        pos = str(parse_word.tag.POS)
        if pos not in pos_map:
            pos_map[pos] = [copy.deepcopy(word)]
        else:
            pos_map[pos].append(copy.deepcopy(parse_word.word))

    print('finish calc word in base...')
    
    with open('./voyna-i-mir-tom-1.txt', 'r') as f:
        words = f.read()

    bad_char = set([  '*', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?',  
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 
                    'O', 'P', 'Q', 'R', 'S',  'T',  'U',  'V', 'W', 'X', 'Z', '[',  ']', '`'])

    all_sentenses = re.findall(r"([А-Я]+[^.!?]+)", words)
    
    final_sentenses = []
    for sentens in all_sentenses:
        if len(set(sentens) & bad_char) == 0:
            if len(sentens.split()) > 2:
                final_sentenses.append(sentens.strip())

    final_sentenses = tuple(final_sentenses)
    
    with open('final_sentenses.pkl', 'wb') as f:
        pickle.dump(final_sentenses, f)
    
    with open('pos_map.pkl', 'wb') as f:
        pickle.dump(pos_map, f)
