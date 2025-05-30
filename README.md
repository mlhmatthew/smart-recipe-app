# Smart Recipe Recommender

The Smart Recipe Recommender is an interactive web app that helps users discover what they can cook based on the ingredients they already have. Users can select ingredients, filter by cuisine, view recipe suggestions, and generate a smart shopping list with estimated prices and store links.

## 🌐 Try the App Online
No installation is required — just click and start using it:

🔗 [Launch Smart Recipe App](https://mlhmatthew-smart-recipe-app.streamlit.app/)

## 🛠 Features
- Select ingredients from your kitchen.
- Filter recipes by cuisine.
- See which ingredients you're missing.
- Generate a shopping list with estimated prices.
- Export the list to PDF.
- Optionally add extra ingredients and adjust quantities.
- Google search links to learn how to cook each selected recipe.

## 🚀 Future Plans
- Integrate flyer scraping to highlight supermarket deals for missing ingredients.
- Support personalized recommendations based on dietary preferences and meal types.

## 💻 Run Locally (Optional)
If you'd like to run the app on your own machine:

### 1. Clone this repository
```bash
git clone https://github.com/mlhmatthew/smart-recipe-recommender.git
cd smart-recipe-recommender
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

## 📂 Files Included
- `app.py`: Main Streamlit application.
- `recipe_database.py`: Contains the recipe dataset.
- `ingredient_prices.py`: Ingredient price estimates.
- `requirements.txt`: List of required Python packages.

---

Enjoy cooking smarter!
