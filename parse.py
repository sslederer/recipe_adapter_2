import dill
import parsing

foods = ['stew','soup', 'pasta']
for food in foods:
    file_identifier = './data/'+food+'_all.pkd'
    with open(file_identifier,'rb') as file:
        results = dill.load(file)
    recipes = results['recipes']
    for n,recipe in enumerate(recipes):
        ingredients_new = parsing.revise_standardize(recipe['ingredients'])
        recipe['ingredients'] = ingredients_new
        recipes[n] = recipe
        title = recipe['label'].lower()
        if len(recipe['ingredients']) < 4:
            recipes[n] = False
        if 'Vegan' in recipe['healthLabels']:
            # print('rectifying vegan absent labels issue')
            recipe['healthLabels'].extend(['Dairy-free','Kosher','Vegetarian'])
        if 'Vegetarian' in recipe['healthLabels']:
            recipe['healthLabels'].append('Kosher')
            
    recipes = [recipe for recipe in recipes if recipe]
    with open('./data/'+food+'_parsed.pkd','wb') as file:
        dill.dump({'labels':results['labels'],'recipes':recipes},file)