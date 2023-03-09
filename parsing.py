import re 
import nltk
nltk.download('averaged_perceptron_tagger')
from ingredient_parser import parse_ingredient
import sys

    
def revise_standardize(ingredients):
    new_ingredients = []
    for ingredient in ingredients:
        new_ingredient = parse_ingredient(ingredient)['name']
        new_ingredient = standardize(new_ingredient)
        # new_ingredient = pin(new_ingredient)['name']
        if new_ingredient != '':
            new_ingredients.append(new_ingredient)
    return list(set(new_ingredients))

def standardize(ingredient):
    ingredient = ingredient.lower()
    ingredient = ingredient.strip()
    ingredient = re.sub('\s',' ',ingredient)
    ingredient = re.sub('-',' ',ingredient)
    ingredient = re.sub('[^a-zA-Z\d\s]','',ingredient)
    ingredient = replacements(ingredient)
    ingredient = ingredient.strip()
    ingredient = ''.join(ingredient.split())
    return ingredient
    
def do_replacements(ingredient,replacements):
    for replacement in replacements:
        # print((replacement,ingredient))
        ingredient = re.sub(replacement[0],replacement[1],ingredient)
        ingredient = ingredient.strip()
    return ingredient

def replacements(ingredient):
    # print('initial:', ingredient)    
    ingredient = replace_quantity(ingredient)
    # print('replaced quantities:', ingredient)    
    ingredient = replace_other(ingredient)
    # print('replaced other:', ingredient)
    ingredient = replace_produce(ingredient)
    # print('replaced produce:', ingredient)
    ingredient = replace_meat(ingredient)
    # print('replaced meat:', ingredient)
    ingredient = replace_pasta(ingredient)
    # print('replaced pasta:', ingredient)
    ingredient = replace_dairy(ingredient)
    # print('replaced dairy:', ingredient)
    ingredient = replace_pluralized(ingredient)
    # print('replaced plurals:', ingredient)
    ingredient = replace_pantry(ingredient)
    # print('replaced pantry:', ingredient)
    return ingredient

def replace_quantity(ingredient):
    quantities = (['\bcup\b','\bc.?','\bpint\b','pt\b','\bquart\b','qt','gallon','gal\b','(fluid)? ? ounce','\boz\b','can\b',
                   'carton','tbl?sp.?','tablespoon','teaspoon','tsp.?','pinch','gram\b','g\b','ml','milliliter','pound','\blbs?.?\b'
                   ])
    replacements = []
    for quantity in quantities:
        replacements.append((quantity+'s?',''))
    return do_replacements(ingredient,replacements)

def replace_other(ingredient):
    replacements = ([
                    ('^fresh(ly)?',''),('^dried',''),('grated',''),('(fresh)?-? ?ground',''),('frozen',''),('cooked',''),
                    ('(low|non|full)-? ?fat',''),('fat free',''),('low-? ?(sodium|salt)',''), ('baby',''),
                    ('no (sodium|salt) added',''),('(small|medium|large)',''),('(can|cans|canned) ','')
                     ])
    return do_replacements(ingredient,replacements)
    
def replace_meat(ingredient):
    meats = ['chicken','turkey','duck','pork','beef','veal','lamb']
    replacements_broths = [(meat+'\s(stock|broth|bouillon)','broth') for meat in meats]
    replacements_meats = [('.*'+meat+'.*',meat) for meat in meats]+[('.*steak\b.*','beef')]
    
    return do_replacements(ingredient,replacements_broths+replacements_meats)

def replace_pluralized(ingredient):
    vegetables = (['onion','leek','egg','pepper','bean','scallion',
                   'mushroom','beet','avocado','carrot','shallot','turnip'
                  ])
    fruits = ['lemon','lime','apple','pear','banana','pineapple']
    replacements =[(item+'s',item) for item in fruits + vegetables]
    return do_replacements(ingredient,replacements)

def replace_pasta(ingredient):    
    pastas = (['bow-?\s?tie pasta','farfalle','penne(\srigate)?','rigatoni','ziti','macaroni','fusilli','paccheri',
            'angel hair pasta','(thin)?\s?spaghetti','linguin[ie]','bucatini','fettucin[ei]',
            'tagliatelle','papardelle','capellini','spaghettini','tortellini','ravioli','(egg )?noodles'
            ]) 
    replacements = [(pasta,'pasta') for pasta in pastas]
    return do_replacements(ingredient,replacements)

def replace_tomato(ingredient):
    tomato_products = (['crushed tomato(es)?', 'tomato pur[ée]e', 'tomato sauce', 
                        '(whole )?peeled tomatoes', 'tomato paste', 'diced tomatoes'
                        ])
    replacements = [(tomato_product, 'tomato') for tomato_product in tomato_products]
    return do_replacements(ingredient, replacements)

def replace_dairy(ingredient):
    replacements = ([
                    ('margarine','butter'),('unsalted butter','butter'), ('salted butter','butter'),
                    ('(heavy|light|whipping) cream','cream'),('half\s?(and|&|-)\s?half','cream'),
                    ('(whole|skim|[12]%|nonfat) milk','milk'),('.*(yogh?urt)$','yogurt'),('cream cheese','creamcheese'),
                    ('cottage cheese','cottagecheese'),(' cheese',''),('parmigiano\s(reggiano)?','parmesan'),
                    ('pecorino( romano)?','parmesan')
                    ])
    return do_replacements(ingredient,replacements)

def replace_produce(ingredient):
    replacements = ([
                        ('green onion','scallion'),('((yellow|white|cooking) )?onion','onion'),
                        ('(button|portobello|white|crimini|cremini|oyster)\smushroom','mushroom'), 
                        ('(baking|brown|white|russet|red|yukon gold)?\s?potato(es)?','potato'), 
                        ('tomatoes','tomato'),('.*(tomato)$','tomato'),('chilli|chile|chilie|chili','chili'),
                        ('celery (ribs?|stalks?|hearts?)','celery'),('rocket','arugula'),
                        ('leaves?','leaf'),('coriander leaf|fresh coriander','cilantro'),
                        ('(yellow|white|sweet) corn','corn'),('lemon (juice|zest)','lemon'),
                        ('lime (juice|zest)','lime'),('bell pepper','pepper')
                        ])
    return do_replacements(ingredient,replacements)

def replace_pantry(ingredient):
    replacements = ([
                        ('(kosher|sea|coarse)? ?salt and (black )?pepper',''),('(sea|kosher|coarse)? ?salt',''),
                        ('^(black|white)? ?pepper(corns?)?$',''),
                        ('.*(olive oil)$','olive oil'),
                        ('(canola|vegetable|cooking|safflower|avocado|grape seed|corn|peanut|olive|rapeseed) oil','oil'),
                        ('all-? ?purpose flour','flour'),('(white|granulated) sugar','sugar'),
                        ('(light|dark) brown sugar','brown sugar'),('wild rice','wildrice'),('(sticky|glut[ei]nous) rice','stickyrice'),('.*\srice','rice'),
                        ('(boiling|hot|warm|luke ?-?warm|cool|cold|iced?|filtered)? ?water','')
                        ,('dry white wine','white wine'),
                        ('dry red wine','red wine'),
                        ('(white wine|red wine|(apple )?cider|sherry|white|rice( wine)?) vinegar','vinegar'),
                        ('.*(soy sauce)$','soy sauce'),('(purple|dark|golden) raisins','raisins'),
                        ('.*(pasta)$','pasta'),('.*(olives)$','olives'),('green beans?','greenbean'),('.*\sbean','bean'),
                        ('crushed red pepper( flakes)?','red pepper flakes')    ]
                        +[('vegetable\s(stock|broth|bouillon)',' broth'),('.*\s bread','bread')]
                          )
    return do_replacements(ingredient,replacements)

running_list = (['bow-tie pasta','fusilli','spaghetti','yellow onions','celery ribs','bay leaves','fresh coriander','sweet corn','lemon zest',
                'sea salt','fresh black pepper','extra-virgin olive oil','canola oil','all purpose flour',
                 'dark brown sugar','white rice','brown rice','luke warm water','lukewarm water','luke-warm water','red wine vinegar','no sodium added soy sauce',' canned black beans','fresh basil','dried basil','low-fat yogurt',
                 'low sodium chicken stock','unsalted butter','half and half','2% milk','greek yogurt', 'boneless skinless chicken breasts','ground turkey'
                ])
# print(revise_standardize(running_list))
# print(running_list)
if __name__ == '__main__':
    print(' '.join(sys.argv[1:]))
    print(standardize(' '.join(sys.argv[1:])))
    running_list = (['bow-tie pasta','fusilli','spaghetti','yellow onions','celery ribs','bay leaves','fresh coriander','sweet corn','lemon zest',
                'sea salt','fresh black pepper','extra-virgin olive oil','canola oil','all purpose flour',
                 'dark brown sugar','white rice','brown rice','luke warm water','lukewarm water','luke-warm water','red wine vinegar','no sodium added soy sauce',' canned black beans','fresh basil','dried basil','low-fat yogurt',
                 'low sodium chicken stock','unsalted butter','half and half','2% milk','greek yogurt', 'boneless skinless chicken breasts','ground turkey'
                ])
