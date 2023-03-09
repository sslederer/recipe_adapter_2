import dill
import numpy as np
import parsing
import heapq
from sklearn.feature_extraction.text import TfidfVectorizer



def make_corpus(target, recipes):
    """
    Join the target recipe to the preexisting list so that it can be assigned TFIDF weights
    """
    full_ingredients = [target['ingredients']] + [recipe['ingredients'] for recipe in recipes]
    return [' '.join(ingredients) for ingredients in full_ingredients]

def get_key_ingredients(title, tf):
    """
    Parse the recipe title to identify key ingredients
    """
    title = title.replace('and','')
    title = title.replace(',',' ')
    words  = [word.strip() for word in title.split()]
    key_ingredients = []
    for word in words:
        word = parsing.standardize(word)
        if word in tf.get_feature_names_out():
            key_ingredients.append(word)
    return key_ingredients 

def implement_key_ingredients(n, tf, tfidf_matrix, key_ingredients, key_ingredient_booster):
    """
    Give the key ingredients a weight equal to a multiple of 
    the (otherwise) highest weighted ingredient
    """
    ingredient_array = tf.get_feature_names_out()
    if tfidf_matrix[n].shape[0]==0:
        return
    top_priority = np.max(tfidf_matrix[n])
    for m, ingredient in enumerate(ingredient_array):
        if ingredient in key_ingredients:
            tfidf_matrix[n, m] = top_priority*key_ingredient_booster

def cosine_similarity(n, m, tfidf_matrix):
    #Compute cosine similarity, suitably normalized
    vector1 = tfidf_matrix[n].toarray()
    vector2 = tfidf_matrix[m].toarray()
    return np.sum(vector1*vector2)/np.sqrt(np.sum(vector1**2)*np.sum(vector2**2))

 

def get_best(target, recipes, number_results=5, restrictions=[],use_key_ingredients=True, key_ingredient_booster=1):
    """
    Finds recipes satisfying the restrictions, with top similarity scores
    """
    #add the recipe to the list so that its ingredients can be assigned tfidf weights
    corpus = make_corpus(target, recipes)
    tf = TfidfVectorizer()
    matrix = tf.fit_transform(corpus)
    #implement parsing of the recipe title for key ingredients
    if use_key_ingredients:
        key_ingredients = get_key_ingredients(target['label'], tf)
        implement_key_ingredients(0, tf, matrix, key_ingredients, key_ingredient_booster)
        
    #search
    result = []
    for n, recipe in enumerate(recipes):
        #check that the recipe satisfies all restrictions
        satisfies_requirements = True
        for restriction in restrictions:
            if restriction not in recipe['healthLabels']:
                satisfies_requirements = False
        if not satisfies_requirements:
            continue
        similarity = cosine_similarity(0, n+1, matrix)
        #use a heap to store results with top score
        if len(result) < number_results:
            heapq.heappush(result,(similarity,n))
        else:
            heapq.heappushpop(result,(similarity,n))
    result.sort(reverse=True)
    return [x[0] for x in result],[recipes[x[1]] for x in result], [x[1] for x in result]    

