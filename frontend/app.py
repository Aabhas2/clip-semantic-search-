import requests
import streamlit as st
import os 

API_URL = os.getenv(
    "API_URL", 
    "http://127.0.0.1:8000", 
).rstrip("/")


st.set_page_config(
    page_title="CLIP Semantic Search",
    layout="wide",
)

st.title("CLIP Semantic Search")
st.write("Search product images using natural language.")

query = st.text_input(
    "Describe the images you want to find",
    placeholder="a black handbag",
)

limit = st.slider(
    "Number of results",
    min_value=1,
    max_value=10,
    value=5,
)

search_clicked = st.button("Search")

if search_clicked:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/search",
                json={
                    "query": query,
                    "limit": limit,
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as error:
            st.error(f"Could not connect to the API: {error}")
        else:
            results = data["results"]

            if not results:
                st.info("No results found.")
            else:
                columns = st.columns(len(results))

                for column, result in zip(columns, results):
                    with column:
                        image_url = result["image_url"] 

                        st.image(
                            image_url, 
                            use_container_width=True, 
                        )

                        st.write(
                            f"**{result['product_type']}**"
                        )
                        st.write(
                            f"Score: {result['score']:.3f}"
                        )
                        st.caption(result["title"])