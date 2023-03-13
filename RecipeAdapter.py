import streamlit as st
from recipe_scrapers import scrape_me
import parsing
import dill
import tfidf

#title
tab1, tab2 = st.tabs(['Main','Data and performance'])
with tab1:
    st.title('Recipe Adapter')
    st.write('###')

    #user inputs recipe website, which we scrape
    text = st.text_input('Enter recipe url',value='https://www.food.com/recipe/boiled-water-422354')
    scraper = scrape_me(text,wild_mode=True)
    title = scraper.title()

    #scrape ingredients using our parsing module
    ingredients = parsing.revise_standardize(scraper.ingredients())
    target_recipe = {'label': title, 'ingredients': ingredients,'url': text}

    # display original recipe
    st.write('#### Your recipe: ',target_recipe['label'])

    # get category and relevant data
    category = st.radio('Category',('Soup/stew','Pasta'))
    st.write('#### ')
    
    #Load relevant data 
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
        #find top matches, twice as many as the eventual output 
        # to account for possible invalid recipes
        scores, matches, indices = tfidf.get_best(target_recipe, recipes, \
                            restrictions=restrictions,number_results=2*number)
        ingredients = set(target_recipe['ingredients']) 
        
        match_count = 0
        while matches and match_count < number:
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

with tab2:
    st.header('Data standardization')
    
    st.markdown("The recipe database from which the recommendations are drawn comes from the\
        [edamam.com](https://edamam.com) API, which supplies a wealth of data for each recipe. Within the recipe corpuses, \
        which consist of approximately 10,000 recipes for pastas and 22,000 for soups and stews, \
        ingredients vary dramatically in their frequency. As shown in the left panels of Figures \
        1 and 2, the numbers of appearances range from 1 to more than 1,000. The TF-IDF processing  \
        of the recipes helps to tame this dynamic range, but additional preprocessing prior  \
        to applying the TF-IDF map was found to improve the quality of recommendations\
        ")
    
    st.markdown('This preprocessing serves to standardize the form of ingredients in the recipes, \
                and is implemented in the function parsing.py in the  \
                [github repository](https://github.com/sslederer/recipe_adapter_2/).\
                The first stage isolates ingredient names from their quantities, for instance  \
                replacing "3 garlic cloves" with "garlic". This is accomplished using the\
                ingredient_parser package, built on nltk. The next step is more discretionary,\
                making use of domain knowledge to dramatically condense the number of ingredients\
                in the corpus. For instance, we map "garlic powder" to "garlic," "chicken breast" \
                to "chicken," and remove all instances of salt and pepper due to their ubiquity.\
                The result reduces the number of ingredients in the corpus by a factor \
                of approximately 3, and also flattens the distribution , as shown in the right panels\
                of Figures 1 and 2.\
                ')
    st.image('./plots/hist_soups.png', caption='Fig. 2: ingredient frequency distribution\
        for the soup and stew corpus. The right panel shows the result after standardization.')
    
    st.image('./plots/hist_pastas.png', caption='Fig. 1: ingredient frequency distribution\
        for the pasta corpus. The right panel shows the result after standardization.')
    
    
    st.header('Recommendation performance')
    st.markdown("It would be desirable to evaluate the performance of the app\
            in some objective fashion. Necessarily, this would require some \
            form of human input, which is beyond the scope of the present effort. \
            Nevertheless, a means of numerical evaluation is available by comparing \
            the similarity scores (cosine similarities) of the top recommendation(s)\
            to the overall distribution of scores. Figure 3 illustrates the idea. The distributions\
            are strongly peaked near zero, with the largest values much greater than the mean. \
            According to this crude metric, the top recommendations are many times better\
            than choosing a recipe at random, as expected.\
            ")
    st.image('./plots/scores.png', caption='Fig. 3: distribution of similarity scores \
        for selected recipes. The vertical orange lines show the expected \
        value of the similarity score over the distribution.')
    
    st.markdown("Perhaps a more natural figure of merit to for the quality of a recommendation \
            would be the ratio of the top score to the mean of the score distribution. \
            To explore this, we consider potential vegan substitutes for all\
            the non-vegan recipes our database. The figure of merit is typically \
            has a very large variance, and has a strong negative correlation with recipe length, \
            as illustrated in the scatter plots of Figure 4.\
                ")
    st.image('./plots/score_ratios.png', caption='Fig. 4: Correlation of the figure of merit with\
        recipe length. The figure of merit is the ratio of the top score to the mean, which\
            which is here shown to vary wildly, and have a strong native correlation\
                with recipe length.')