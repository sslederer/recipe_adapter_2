import streamlit as st
from recipe_scrapers import scrape_me
import parsing
import dill
import tfidf
from parse_website import get_metadata


#title
st.title('Recipe Adapter')
st.write('#')

#user inputs recipe website, which we scrape
text = st.text_input('Enter recipe url',value='https://www.food.com/recipe/boiled-water-422354')
scraper = scrape_me(text,wild_mode=True)
title = scraper.title()
#scrape ingredients using our parsing module
ingredients = parsing.revise_standardize(scraper.ingredients())
target_recipe = {'label': title, 'ingredients': ingredients,'url': text}

# display original recipe
metadata = get_metadata(text)
st.write('#### Your recipe: ',target_recipe['label'])
# st.write('ingredients: ', ', '.join(target_recipe['ingredients']))
st.write('#')

# get category and relevant data
category = st.radio('Category',('Soup/stew','Pasta'))

st.write('# ')
if category == 'Soup/stew':
    # with open('edamam/soup_parsed_oneword.pkd','rb') as file:
    with open('data/soup_2_28.pkd','rb') as file:
        results = dill.load(file)
        recipes_soup = results['recipes']

    # with open('edamam/stew_parsed_oneword.pkd','rb') as file:
    with open('data/stew_2_28.pkd','rb') as file:
        results = dill.load(file)
        recipes_stew = results['recipes']
    recipes = recipes_stew + recipes_soup

elif category == 'Pasta':
    # with open('edamam/pasta_parsed_oneword.pkd','rb') as file:
    with open('data/pasta_2_28.pkd','rb') as file:
        results = dill.load(file)
        recipes = results['recipes']

st.write('### ...but make it...')
st.write('#')

# user inputs dietary restrictions 
restrictions = st.multiselect('Select dietary restrictions', ['Vegetarian','Vegan','Gluten-free','Dairy-free','Kosher'])
st.write('#')
restrictions = [restriction for restriction in restrictions]
#hit search
clicked = st.button('Search for '+', '.join([restriction.lower() for restriction in restrictions])+' substitutes')

    
number = 5   
if clicked:
    #find top matches
    scores, matches,indices = tfidf.get_best(target_recipe, recipes, \
                        restrictions=restrictions,number_results=number)
    ingredients = set(target_recipe['ingredients']) 

    #for each one display an image (if available) and link
    for match in matches:
        # st.write('#### [' + match['label'] + '](' + match['url'] + ')')
        metadata = get_metadata(match['url'])
        if 'image' in metadata:
            image_link = metadata['image']
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                if 'image' in metadata and image_link:
                    st.image(image_link, width = 120)
                # st.write(image_link)
            with col2:    
                st.write('#### [' + match['label'] + '](' + match['url'] + ')')
                # st.write('ingredients: ', ', '.join(match['ingredients']))
                common = set(match['ingredients']).intersection(set(target_recipe['ingredients']))
                st.write('Total ingredients: ', len(match['ingredients']), '. In common: ', ', '.join(list(common)))
        st.write('#')
        