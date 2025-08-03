import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.hasher import Hasher
from recipe_database import recipe_database
from ingredient_prices import approx_price_map
import urllib.parse
import inflect
import os
from fpdf import FPDF
import tempfile

# -------------------- LOGIN SETUP --------------------
names = ['Alice', 'Bob','Matthew']
usernames = ['alice', 'bob','matthew']
passwords = ['123', '456','789']
hashed_pw = Hasher.hash_list(passwords)

credentials = {
    "usernames": {
        usernames[i]: {
            "name": names[i],
            "password": hashed_pw[i]
        } for i in range(len(usernames))
    }
}

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name="smart_recipe_app",
    key="abcdef",
    cookie_expiry_days=1
)

# Page config
st.set_page_config(page_title="Smart Recipe Recommender", layout="centered")

# Show login form
authenticator.login(location="main", key="Login")


# -------------------- AUTH CHECK --------------------
if st.session_state.get("authentication_status"):
    authenticator.logout("Logout", "sidebar")
    st.success(f"Welcome {st.session_state['name']}! 👋")

    # -------------------- APP START --------------------

    st.title("Smart Recipe Recommender")

    st.markdown("---")
    st.markdown("### How to Use")
    st.markdown("1. Select ingredients you have.")
    st.markdown("2. Choose cuisine and get matching recipes.")
    st.markdown("3. Select dishes to make and confirm shopping list.")
    st.markdown("4. Add optional extras, review list, then export PDF.")
    st.write("Select your ingredients and discover what you can cook!")

    def normalize_ingredient(ingredient):
        return ingredient.strip().lower()

    # Ingredient list
    all_ingredients = sorted(set(
        normalize_ingredient(i)
        for r in recipe_database
        for i in r['ingredients']
    ))

    # Session state
    st.session_state.setdefault('selected_ingredients', [])
    st.session_state.setdefault('selected_recipes', [])
    st.session_state.setdefault('custom_additions', {})
    st.session_state.setdefault('recommendations', [])
    st.session_state.setdefault('editable_shopping_list', {})

    # Ingredient selection
    st.subheader("Select Your Ingredients")
    selected = st.multiselect("Start typing an ingredient...", options=all_ingredients)
    if st.button("Confirm Ingredients"):
        st.session_state.selected_ingredients = selected

    if st.session_state.selected_ingredients:
        st.markdown("### Current Ingredients")
        st.write(", ".join(st.session_state.selected_ingredients))
        if st.button("Clear All"):
            st.session_state.selected_ingredients = []

    # Cuisine filtering
    cuisines = ["All"] + sorted(set(r['cuisine'] for r in recipe_database))
    selected_cuisine = st.selectbox("Select a cuisine", cuisines)

    # Recommendation logic
    def recommend_recipes(user_ingredients, selected_cuisine):
        user_ingredients_set = set(normalize_ingredient(i) for i in user_ingredients)
        filtered = [r for r in recipe_database if selected_cuisine == "All" or r['cuisine'] == selected_cuisine]
        results = []
        for r in filtered:
            r_ings = set(normalize_ingredient(i) for i in r['ingredients'])
            matched = user_ingredients_set & r_ings
            score = len(matched) / len(r_ings)
            if score >= 0.5:
                results.append((score, r, matched))
        results.sort(reverse=True, key=lambda x: x[0])
        return results

    if st.button("Get Recipes"):
        if st.session_state.selected_ingredients:
            matches = recommend_recipes(st.session_state.selected_ingredients, selected_cuisine)
            if matches:
                st.session_state.recommendations = matches
                st.session_state.selected_recipes = []
            else:
                st.warning("No recipes found with at least 50% matching ingredients.")

    if st.session_state.recommendations:
        matches = st.session_state.recommendations
        st.subheader("Recommended Recipes")
        recipe_names = [r['name'] for _, r, _ in matches]
        st.session_state.selected_recipes = st.multiselect(
            "Select recipes you want to make:", 
            options=recipe_names, 
            default=st.session_state.selected_recipes
        )

    # Shopping list
    def create_shopping_list(selected_names):
        shopping_list = {}
        full_map = {}
        for _, r, matched in st.session_state.recommendations:
            if r['name'] in selected_names:
                all_ings = set(normalize_ingredient(i) for i in r['ingredients'])
                missing = all_ings - set(normalize_ingredient(i) for i in st.session_state.selected_ingredients)
                for ing in missing:
                    shopping_list[ing] = shopping_list.get(ing, 0) + 1
                full_map[r['name']] = {
                    'have': list(all_ings - missing),
                    'missing': list(missing),
                    'servings': r.get('servings', 2)
                }
        return shopping_list, full_map

    if st.session_state.selected_recipes:
        shopping_list, recipe_map = create_shopping_list(st.session_state.selected_recipes)

        st.subheader("Smart Shopping List")
        total_cost = 0

        for name in st.session_state.selected_recipes:
            st.markdown(f"#### {name}")
            info = recipe_map[name]

            st.write("Ingredients you already have: " + ", ".join(info['have']) if info['have'] else "None")
            st.write("Missing ingredients: " + ", ".join(info['missing']) if info['missing'] else "None")

            query = urllib.parse.quote(name + " recipe")
            st.markdown(f"[🔍 Learn how to make it](https://www.google.com/search?q={query})", unsafe_allow_html=True)

            for ing in info['missing']:
                encoded = urllib.parse.quote(ing)
                url = f"https://www.walmart.ca/search?q={encoded}"
                price = approx_price_map.get(ing, 0.80)
                total_cost += price
                st.markdown(f"🛒 [Search {ing} on Walmart.ca]({url}) – Approx. ${price:.2f} CAD")

            st.write(f"Approximate Servings: {info['servings']}")

        st.markdown(f"### 💳 Estimated Total Cost: ${total_cost:.2f} CAD")

        # Add extras
        st.subheader("Add Extra Ingredients to Shopping List")
        extra = st.multiselect("Select additional items:", options=all_ingredients)
        extra_qty = {}
        for ing in extra:
            qty = st.number_input(f"Quantity for {ing}", min_value=1, value=1, key=f"qty_{ing}")
            extra_qty[ing] = qty

        combined_list = shopping_list.copy()
        for ing, qty in extra_qty.items():
            combined_list[ing] = combined_list.get(ing, 0) + qty

        st.session_state.editable_shopping_list = combined_list

        # Final Review
        st.subheader("🧾 Final Shopping List Review")
        updated_quantities = {}
        for ing, qty in st.session_state.editable_shopping_list.items():
            updated_qty = st.number_input(f"{ing} – Qty", min_value=1, value=qty, step=1, key=f"edit_{ing}")
            updated_quantities[ing] = updated_qty
            st.write(f"Approx. Price: ${approx_price_map.get(ing, 0.80):.2f} CAD")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm and Export Shopping List PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Smart Shopping List", ln=True)
                pdf.ln()
                for ing, qty in updated_quantities.items():
                    line = f"{ing} x{qty} - Approx. ${approx_price_map.get(ing, 0.80):.2f} CAD"
                    pdf.cell(200, 10, txt=line.encode("latin-1", "replace").decode("latin-1"), ln=True)
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                pdf.output(tmp.name)
                with open(tmp.name, "rb") as f:
                    st.download_button("Download Shopping List PDF", data=f, file_name="shopping_list.pdf", mime="application/pdf")

        with col2:
            if st.button("✏️ Edit Quantity"):
                st.session_state.editable_shopping_list = updated_quantities

    else:
        st.info("Please click 'Get Recipes' and select your dishes before proceeding to the shopping list.")

# -------------------- AUTH FAIL UI --------------------
elif st.session_state.get("authentication_status") is False:
    st.error("Incorrect username or password.")
elif st.session_state.get("authentication_status") is None:
    st.warning("Please enter your username and password.")



#cd C:\Users\longh\smart-recipe-app
#streamlit run app.py
