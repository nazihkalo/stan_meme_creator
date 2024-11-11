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

# Initialize session state
if 'current_batch' not in st.session_state:
    st.session_state.current_batch = 0
if 'current_results' not in st.session_state:
    st.session_state.current_results = None
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = None

def reset_results():
    st.session_state.current_batch = 0
    st.session_state.current_results = None

def next_batch():
    st.session_state.current_batch += 1

# Initialize MemeGenerator
DATA_PATH = Path(__file__).parent.parent / "data" / "meme_data.json"
meme_gen = MemeGenerator(str(DATA_PATH))

# User input
st.markdown("## Generate a Meme")
user_input = st.text_area(
    "Enter your prompt or tweet:",
    placeholder="Example: Drake ignoring something and pointing at something else",
    key="text_input",
    on_change=reset_results
)

def display_meme_batch(results, start_idx):
    cols = st.columns(3)
    for i, col in enumerate(cols):
        idx = start_idx + i
        if idx < len(results):
            image_url, image_id, similarity = results[idx]
            with col:
                # Generate meme
                meme_image = meme_gen.generate_meme(image_url, st.session_state.user_prompt)
                
                # Display result
                st.image(meme_image, caption=f"Similarity: {similarity:.2f}", use_column_width=True)
                
                # Add download button
                buf = io.BytesIO()
                meme_image.save(buf, format="PNG")
                st.download_button(
                    label=f"Download Meme {idx + 1}",
                    data=buf.getvalue(),
                    file_name=f"generated_meme_{image_id}.png",
                    mime="image/png",
                    key=f"download_{idx}"
                )
                st.caption(f"Template ID: {image_id}")
    
    # Show "Try More" button if there are more results
    remaining = len(results) - ((st.session_state.current_batch + 1) * 3)
    if remaining > 0:
        st.button("Try More Options", on_click=next_batch)

if st.button("Generate Meme"):
    if user_input:
        st.session_state.user_prompt = user_input
        with st.spinner("Generating memes..."):
            # Get all relevant images sorted by similarity
            results = meme_gen.find_top_images(user_input, n=9)  # Get top 9 for 3 batches
            
            if results:
                st.session_state.current_results = results
                display_meme_batch(results, st.session_state.current_batch * 3)
            else:
                st.error("Couldn't find relevant images for your prompt. Try different keywords!")
    else:
        st.warning("Please enter a prompt first!")

# If there are existing results, display them
elif st.session_state.current_results is not None:
    display_meme_batch(st.session_state.current_results, st.session_state.current_batch * 3)

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