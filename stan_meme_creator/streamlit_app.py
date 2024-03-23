import io
import os

import numpy as np
import requests
from utils import find_transparent_area, process_image
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

from streamlit_image_select import image_select
import extra_streamlit_components as stx

from links import twitter

from streamlit_extras.stoggle import stoggle

st.set_page_config(page_title = "$STAN Meme Template Generator", page_icon="🥤")



"""
# $STAN Meme Template Generator
This app allows you to create memes using a template image and your own image. 
You can select a meme template from the dropdown, upload your own image, and generate a meme. 
The app will automatically resize your image to fit the template and generate a meme that you can share on social media. 
"""


twitter()
"""
## Step 1: Select your meme template 
"""

# Iterate and add all paths in the image folder stan_meme_creator/static/meme_templates
meme_folder = "stan_meme_creator/static/meme_templates"
overlay_folder = "stan_meme_creator/static/overlay_templates"

with st.expander("The first step is to select a meme template.", expanded=True):

    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id='meme', title="Meme", description="Memable images"),
        stx.TabBarItemData(id='overlay', title="Overlay", description="Simple overlay images"),
    ], default='meme')


    if chosen_id == 'meme':
        images = [os.path.join(meme_folder, filename) for filename in os.listdir(meme_folder)]
    else:
        images = [os.path.join(overlay_folder, filename) for filename in os.listdir(overlay_folder)]



    template_img = image_select(
        label="Select a template",
        images=images,
        # captions=images
    )


"""
## Step 2: Upload your own image
"""
with st.expander("The second step is to upload your own image.", expanded=True):
    uploaded_file =  st.file_uploader("Upload your own image", type=["jpg", "jpeg", "png"])


"""
## Step 3: Enjoy your meme & spread the word of the cup that fucks, $STAN

"""

with st.expander("Finally enjoy & share:)", expanded = True):

    if uploaded_file:
        img = Image.open(uploaded_file)
        # st.image(img, caption="Uploaded image", use_column_width=True)
        template_complete = process_image(img, template_img)
        st.image(template_complete, caption="Meme template with your image",   use_column_width=True)
        # Add share image to twitter with pre-filled text
        

        components.html(
            """
                <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" class="twitter-share-button" 
                data-text="$STAN @StanleyCupCoin Meme Template Generator 🥤🏆" 
                data-url="https://www.stanleyco.in"
                data-show-count="false">
                data-size="Large" 
                data-hashtags="stan,stanleycupcoin"
                Tweet
                </a>
                <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
            """
        )


        
    else:
        st.info("No image uploaded yet.")
        

