import streamlit as st
# ... (existing imports)

st.set_page_config(
    page_title="$STAN Meme Generator",
    page_icon="🥤",
    layout="wide"
)

st.markdown("# $STAN Template Generator 🎨")
st.sidebar.header("Template Generator")

st.markdown("""
This app allows you to create memes using a template image and your own image. 
You can select a meme template from the dropdown, upload your own image, and generate a meme. 
The app will automatically resize your image to fit the template and generate a meme that you can share on social media. 
""")