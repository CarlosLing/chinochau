import streamlit as st
from ..chinochau.service import ChinoChau

# Initialize session state variables if they don't exist
if "show_string2" not in st.session_state:
    st.session_state.show_string2 = False
if "show_string3" not in st.session_state:
    st.session_state.show_string3 = False

chino = ChinoChau("input.txt")
chino.update_master_flashcards()
example = chino.get(0)

chinese = example.chinese
pinyin = example.pinyin
definition = example.definitions[0]

# Display the always-visible string
st.subheader(chinese)

# Create two columns for the buttons
col1, col2 = st.columns(2)

# Button 1 to toggle String 2
with col1:
    if st.button("Button 1"):
        st.session_state.show_string2 = not st.session_state.show_string2

# Button 2 to toggle String 3
with col2:
    if st.button("Button 2"):
        st.session_state.show_string3 = not st.session_state.show_string3

# Display String 2 if toggled on
if st.session_state.show_string2:
    st.write(pinyin)

# Display String 3 if toggled on
if st.session_state.show_string3:
    st.write(definition)
