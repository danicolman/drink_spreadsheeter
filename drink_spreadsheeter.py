from tkinter import W
import requests
import json
import pprint
import csv
from tqdm import tqdm

base_ingredient = input("Pick an ingredient\n")

querystring = {"i":base_ingredient}

headers = {
    "X-RapidAPI-Key": "1",
    "X-RapidAPI-Host": "the-cocktail-db.p.rapidapi.com"
}

def search_by_ingredient(ingredient):

    url = "http://www.thecocktaildb.com/api/json/v1/1/filter.php"

    response = requests.request("GET", url, headers=headers, params={"i":ingredient})

    drinks_dict = response.json()
    return drinks_dict

try:
    drinks_dict = search_by_ingredient(base_ingredient)
except:
    base_ingredient = input("I'm sorry, I don't recognise that ingredient.  Please try another.\nPick an ingredient\n")
    drinks_dict = search_by_ingredient(base_ingredient)
    
# defining a function to create a URL from a given drink ID

def create_url(drink_name, drink_id):
    url_prefix = "https://thecocktaildb.com/drink/"
    drink_id_and_name = drink_id + " " + drink_name
    url_suffix = "-".join(drink_id_and_name.split())
    drink_url = url_prefix + url_suffix
    return drink_url

# defining a function to use the drink ID to look up the drink itself using the API

def find_drink(drink_id):
    find_url = "http://www.thecocktaildb.com/api/json/v1/1/lookup.php"
    drink_query = {"i":drink_id}
    response = requests.request("GET", find_url, headers = headers, params = drink_query)
    return response.json()

# defining a function to take all ingredients (except searched ingredient) and convert to single string

def ingredient_string(drink_id):
    details = find_drink(drink_id)
    ingredients = []
    drink = details["drinks"][0]
    for i in range(1,16):
        ingredient = drink["strIngredient{}".format(i)]
        if ingredient != None and ingredient.lower() != base_ingredient.lower():
            ingredients.append(ingredient)
    return ", ".join(ingredients)

# defining a function to create additional dictionary pairs for type, category, glass, and ingredients

def additional_info(drink_id):
    drinktionary = {}
    details = find_drink(drink_id)
    drink = details["drinks"][0]
    drinktionary.update({
        "strAlcoholic": drink["strAlcoholic"], 
        "strCategory": drink["strCategory"], 
        "strGlass": drink["strGlass"],
        "strIngredients": ingredient_string(drink_id),
        "strInstructions": drink["strInstructions"]
    })
    return drinktionary

# iterate over drinks dictionary, create url for each drink and add url and additional info to drink, remove thumbnail field
# tqdm progress bar so I don't go mad waiting

for drink in tqdm(drinks_dict["drinks"]):
    drink_url = create_url(drink["strDrink"], drink["idDrink"])
    drink["urlDrink"] = drink_url
    drink.update(additional_info(drink["idDrink"]))
    del drink["strDrinkThumb"]

# write contents of drink dictionary to csv

with open("100 Delicious {} Drinks.csv".format(base_ingredient).title(), "w") as drink_csv:
    data = drinks_dict

    drinks = (data["drinks"])

    count = 0

    csv_writer = csv.writer(drink_csv)
    for drink in drinks:
        if count == 0:
            header = ["Name", "ID", "URL", "Alcohol", "Category", "Glass", "Other Ingredients", "Instructions"]
            csv_writer.writerow(header)
            count += 1

        csv_writer.writerow(drink.values())