import streamlit as st
from pathlib import Path
from utils.meme_utils import MemeGenerator
import io

# Page config
st.set_page_config(
    page_title="AI Meme Generator",
    page_icon="🤖",
    layout="wide"
)

st.markdown("# AI Meme Generator 🤖")
st.sidebar.header("AI Meme Generator")

# Initialize MemeGenerator
DATA_PATH = Path(__file__).parent.parent / "data" / "meme_data.json"
meme_gen = MemeGenerator(str(DATA_PATH))

# User input
st.markdown("## Generate a Meme")
user_input = st.text_area(
    "Enter your prompt or tweet:",
    placeholder="Example: Drake ignoring something and pointing at something else"
)

if st.button("Generate Meme"):
    if user_input:
        with st.spinner("Generating your meme..."):
            # Find relevant image
            image_url = meme_gen.find_relevant_image(user_input)
            
            if image_url:
                # Generate meme
                meme_image = meme_gen.generate_meme(image_url, user_input)
                
                # Display result
                st.image(meme_image, caption="Generated Meme", use_column_width=True)
                
                # Add download button
                buf = io.BytesIO()
                meme_image.save(buf, format="PNG")
                st.download_button(
                    label="Download Meme",
                    data=buf.getvalue(),
                    file_name="generated_meme.png",
                    mime="image/png"
                )
            else:
                st.error("Couldn't find a relevant image for your prompt. Try different keywords!")
    else:
        st.warning("Please enter a prompt first!")

# Add some usage tips
with st.expander("Usage Tips"):
    st.markdown("""
    ### How to get the best results:
    1. Be specific about the meme format you want
    2. Include relevant keywords that match meme tags
    3. Keep your text concise for better overlay
    
    ### Example prompts:
    - "Drake ignoring work and pointing at memes"
    - "Distracted boyfriend looking at crypto"
    - "Mind blown reaction to $STAN"
    """) 