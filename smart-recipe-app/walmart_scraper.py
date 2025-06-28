# walmart_scraper.py

import requests
from bs4 import BeautifulSoup
import statistics
from rapidfuzz import fuzz

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Enriched search terms for better results
search_queries = {
    "lime": ["lime", "fresh lime"],
    "lemon": ["lemon", "fresh lemon"],
    "onion": ["onion", "yellow onion", "white onion", "red onion"],
    "garlic": ["garlic", "fresh garlic", "garlic bulb"],
    "olive oil": ["olive oil", "extra virgin olive oil"],
    "vegetable oil": ["vegetable oil", "canola oil"],
    "butter": ["butter", "unsalted butter", "salted butter"],
    "basil": ["basil", "fresh basil"],
    "oregano": ["oregano", "dried oregano"],
    "parsley": ["parsley", "fresh parsley"],
    "cilantro": ["cilantro", "coriander leaves"],
    "thyme": ["thyme", "fresh thyme"],
    "rosemary": ["rosemary", "fresh rosemary"],
    "tomato": ["tomato", "fresh tomatoes", "roma tomatoes"],
    "tomato sauce": ["tomato sauce", "marinara sauce"],
    "pasta": ["pasta", "spaghetti", "penne", "fusilli"],
    "rice": ["rice", "white rice", "basmati rice", "brown rice"],
    "bread": ["bread", "baguette", "whole wheat bread"],
    "egg": ["egg", "eggs", "large eggs", "organic eggs"],
    "milk": ["milk", "2% milk", "whole milk", "almond milk"],
    "cream": ["cream", "heavy cream", "whipping cream"],
    "yogurt": ["yogurt", "greek yogurt", "plain yogurt"],
    "cheese": ["cheese", "cheddar cheese", "mozzarella", "parmesan"],
    "mozzarella": ["mozzarella", "shredded mozzarella"],
    "cheddar": ["cheddar", "mild cheddar", "old cheddar"],
    "parmesan": ["parmesan", "grated parmesan"],
    "cucumber": ["cucumber", "english cucumber"],
    "carrot": ["carrot", "carrots", "baby carrots"],
    "zucchini": ["zucchini", "courgette"],
    "spinach": ["spinach", "baby spinach", "fresh spinach"],
    "lettuce": ["lettuce", "romaine", "iceberg lettuce"],
    "bell pepper": ["bell pepper", "red pepper", "green pepper", "yellow pepper"],
    "chili pepper": ["chili pepper", "red chili", "hot pepper"],
    "potato": ["potato", "russet potato", "baby potato"],
    "sweet potato": ["sweet potato", "yam"],
    "mushroom": ["mushroom", "white mushrooms", "cremini mushrooms"],
    "chicken": ["chicken", "chicken breast", "chicken thighs"],
    "beef": ["beef", "ground beef", "stewing beef"],
    "pork": ["pork", "pork chops", "ground pork"],
    "lamb": ["lamb", "ground lamb", "lamb chops"],
    "shrimp": ["shrimp", "frozen shrimp", "raw shrimp"],
    "fish": ["fish", "tilapia", "salmon fillet", "cod fillet"],
    "tofu": ["tofu", "firm tofu", "extra firm tofu"],
    "tempeh": ["tempeh", "soy tempeh"],
    "tortilla": ["tortilla", "flour tortilla", "corn tortilla"],
    "beans": ["beans", "black beans", "kidney beans", "chickpeas"],
    "chickpeas": ["chickpeas", "garbanzo beans"],
    "lentils": ["lentils", "red lentils", "green lentils"],
    "corn": ["corn", "sweet corn", "frozen corn"],
    "peas": ["peas", "frozen peas", "green peas"],
    "cabbage": ["cabbage", "green cabbage", "red cabbage"],
    "coconut milk": ["coconut milk", "unsweetened coconut milk"],
    "soy sauce": ["soy sauce", "kikkoman soy sauce"],
    "vinegar": ["vinegar", "white vinegar", "apple cider vinegar"],
    "flour": ["flour", "all purpose flour", "whole wheat flour"],
    "sugar": ["sugar", "white sugar", "brown sugar"],
    "honey": ["honey", "raw honey"],
    "peanut butter": ["peanut butter", "natural peanut butter"],
    "jam": ["jam", "strawberry jam", "raspberry jam"],
    "oats": ["oats", "rolled oats", "quick oats"],
    "cereal": ["cereal", "corn flakes", "granola"],
    "banana": ["banana", "ripe banana"],
    "apple": ["apple", "gala apple", "granny smith apple"],
    "orange": ["orange", "navel orange", "mandarin orange"],
    "strawberries": ["strawberries", "fresh strawberries"],
    "blueberries": ["blueberries", "frozen blueberries"],
    "yams": ["yams", "sweet potato"],
}


def get_walmart_price(ingredient):
    queries = search_queries.get(ingredient.lower(), [ingredient])
    all_products = []
    all_prices = []

    for query in queries:
        search_url = f"https://www.walmart.ca/search?q={query}"
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        found_items = 0

        for item in soup.select('div[data-automation="product"]')[:12]:  # Check top 12 items
            title_tag = item.select_one('[data-automation="name"]')
            price_tag = item.select_one('[data-automation="price"]')

            if title_tag and price_tag:
                name = title_tag.get_text(strip=True)
                similarity = fuzz.partial_ratio(name.lower(), ingredient.lower())

                if similarity < 60:  # Only keep decently matched results
                    continue

                price_text = price_tag.get_text(strip=True).replace("$", "").replace(",", "")
                try:
                    price = float(price_text)
                    link_tag = title_tag.find("a")
                    link = "https://www.walmart.ca" + link_tag['href'] if link_tag else search_url
                    all_prices.append(price)
                    all_products.append({
                        "name": name,
                        "price": f"${price:.2f}",
                        "link": link
                    })
                    found_items += 1
                except ValueError:
                    continue

        if found_items >= 1:
            break

    if not all_prices:
        return {"ingredient": ingredient, "error": "No prices found"}

    avg_price = statistics.mean(all_prices)

    return {
        "ingredient": ingredient,
        "average_price": f"${avg_price:.2f}",
        "top_items": all_products
    }

# Example:
# print(get_walmart_price("onion"))
