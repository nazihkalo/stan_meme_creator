import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from streamlit_image_select import image_select
import extra_streamlit_components as stx
from streamlit_cropper import st_cropper
from streamlit_extras.stoggle import stoggle

from core.image_processor import ImageProcessor
from core.template_manager import TemplateManager
from utils.link_utils import twitter

# Page configuration
st.set_page_config(
    page_title="$STAN Meme Template Generator",
    page_icon="🥤"
)

# Disable deprecation warning
st.set_option('deprecation.showfileUploaderEncoding', False)

def main():
    """Main application function."""
    st.markdown("""
    # $STAN Meme Template Generator
    This app allows you to create memes using a template image and your own image. 
    You can select a meme template from the dropdown, upload your own image, and generate a meme. 
    The app will automatically resize your image to fit the template and generate a meme that you can share on social media. 
    """)

    twitter()
    
    # Template Selection Section
    st.markdown("## Step 1: Select your meme template")
    template_img = select_template()

    # Image Upload Section
    st.markdown("## Step 2: Upload your own image")
    uploaded_file = upload_image()

    # Result Section
    st.markdown("## Step 3: Enjoy your meme & spread the word of the cup that fucks, $STAN")
    process_and_display_result(uploaded_file, template_img)

def select_template() -> str:
    """Handle template selection UI."""
    with st.expander("The first step is to select a meme template.", expanded=True):
        chosen_id = stx.tab_bar(data=[
            stx.TabBarItemData(id='meme', title="Meme", description="Memable images"),
            stx.TabBarItemData(id='overlay', title="Overlay", description="Simple overlay images"),
        ], default='meme')

        template_paths = TemplateManager.get_template_paths()
        images = (template_paths["meme_templates"] if chosen_id == 'meme' 
                 else template_paths["overlay_templates"])

        return image_select(
            label="Select a template",
            images=images,
        )

def upload_image():
    """Handle image upload UI."""
    with st.expander("The second step is to upload your own image.", expanded=True):
        return st.file_uploader("Upload your own image", type=["jpg", "jpeg", "png"])

def process_and_display_result(uploaded_file: str, template_img: str):
    """Process the uploaded image with the selected template and display results."""
    with st.expander("Finally enjoy & share:)", expanded=True):
        if not uploaded_file:
            st.info("No image uploaded yet.")
            return

        img = Image.open(uploaded_file)
        
        # Image cropping options
        enable_cropping = st.toggle("Crop Image", value=False)
        maintain_aspect_ratio = st.toggle("Maintain Aspect Ratio", value=False)
        
        if enable_cropping:
            st.write("Double click to save crop")
            img = st_cropper(
                img,
                realtime_update=False,
                box_color='#0000FF'
            )

        # Process the image
        try:
            template_complete = ImageProcessor.process_image(
                img,
                template_img,
                maintain_aspect_ratio=maintain_aspect_ratio
            )
            st.image(
                template_complete,
                caption="Meme template with your image",
                use_column_width=True
            )
            
            # Twitter share button
            display_twitter_button()
        except ValueError as e:
            st.error(f"Error processing image: {str(e)}")

def display_twitter_button():
    """Display Twitter share button."""
    components.html(
        """
        <a href="https://twitter.com/share?ref_src=twsrc%5Etfw" 
           class="twitter-share-button" 
           data-text="$STAN @StanCupCoin Meme Template Generator 🥤🏆" 
           data-url="https://www.stancupcoin.com"
           data-show-count="false"
           data-size="Large" 
           data-hashtags="stan,stancupcoin">
           Tweet
        </a>
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """
    )

if __name__ == "__main__":
    main()

