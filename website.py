import streamlit as st
from recipe_scrapers import scrape_me
import parsing
import dill
import tfidf
from parse_website import get_metadata
import time

#title

st.title('Recipe Adapter')
st.write('###')

#user inputs recipe website, which we scrape
text = st.text_input('Enter recipe url',value='https://www.food.com/recipe/boiled-water-422354')
start = time.time()
scraper = scrape_me(text,wild_mode=True)
title = scraper.title()

#scrape ingredients using our parsing module
ingredients = parsing.revise_standardize(scraper.ingredients())
target_recipe = {'label': title, 'ingredients': ingredients,'url': text}

# display original recipe
metadata = get_metadata(text)
st.write('#### Your recipe: ',target_recipe['label'])

# get category and relevant data
category = st.radio('Category',('Soup/stew','Pasta'))

st.write('#### ')
if category == 'Soup/stew':
    with open('data/soup_parsed.pkd','rb') as file:
        results = dill.load(file)
        recipes_soup = results['recipes']

    with open('data/stew_parsed.pkd','rb') as file:
        results = dill.load(file)
        recipes_stew = results['recipes']
    recipes = recipes_stew + recipes_soup

elif category == 'Pasta':
    with open('data/pasta_parsed.pkd','rb') as file:
        results = dill.load(file)
        recipes = results['recipes']

st.write('### ...but make it...')

# user inputs dietary restrictions 
restrictions = st.multiselect('Select dietary restrictions', 
                              ['Vegetarian','Vegan','Gluten-free','Dairy-free','Kosher'])
st.write('###')
restrictions = [restriction for restriction in restrictions]
#hit search
clicked = st.button('Search for '+', '.join([restriction.lower() for restriction in restrictions])
                    +' substitutes')

st.write('###')
    
number = 5   
if clicked:
    #find top matches
    start = time.time()
    scores, matches, indices = tfidf.get_best(target_recipe, recipes, \
                        restrictions=restrictions,number_results=2*number)
    ingredients = set(target_recipe['ingredients']) 
    print('finding matches took', time.time()-start)
    
    match_count = 0
    while matches and match_count < number:
        print('match count', match_count)
        match = matches.pop(0)
        index = indices.pop(0)
        #Known problem recipe that often shows up
        if category == 'Pasta' and index == 5158:
            continue
        #Must have valid title and URL
        if not match['label']:
            continue
        if not match['url']:
            continue
        
        st.write('#### [' + match['label'] + '](' + match['url'] + ')')
        st.write('###')
        match_count += 1
    if match_count == 0:
        st.write('### No suitable substitutes in database')
