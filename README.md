# smart-recipe-app
Smart Recipe Recommender is a user-friendly app designed to simplify meal planning, reduce food waste, and save money. It helps users discover recipes based on ingredients they already have at home, while also generating a smart shopping list for any missing items.

# Smart Recipe Recommender

The Smart Recipe Recommender is a Streamlit-based web application that helps users discover recipes based on ingredients they already have. It provides recipe suggestions, identifies missing ingredients, estimates cost, and generates a customizable shopping list that can be exported as a PDF.

## Features

- Select ingredients you currently have
- Filter recipes by cuisine
- Get recipe recommendations with 50% or higher match
- View missing ingredients with Walmart.ca search links
- Estimate total cost using average Canadian prices
- Add extra ingredients and adjust quantities
- Export the final shopping list as a downloadable PDF
- Link to Google search for full recipe instructions
- Includes serving estimates per recipe

## Planned Future Enhancements

- Integrate supermarket flyer scraping to highlight weekly deals for missing ingredients
- Add personalized recipe recommendations
- Multi-language support

## Try It Online

To run the app online:

1. Fork or clone this repository
2. Push it to your own GitHub account
3. Deploy using [Streamlit Cloud](https://streamlit.io/cloud)

## Run Locally

```bash
git clone https://github.com/yourusername/smart-recipe-recommender.git
cd smart-recipe-recommender
pip install -r requirements.txt
streamlit run app.py
