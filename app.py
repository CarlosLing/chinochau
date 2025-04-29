import streamlit as st
from chinochau.service import ChinoChau

# Initialize session state variables if they don't exist
if "show_pinyin" not in st.session_state:
    st.session_state.show_pinyin = False
if "show_definition" not in st.session_state:
    st.session_state.show_definition = False

chino = ChinoChau("input.txt", fill_null_definitions=True)
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
    if st.button("PinYin"):
        st.session_state.show_pinyin = not st.session_state.show_pinyin

# Button 2 to toggle String 3
with col2:
    if st.button("Definition"):
        st.session_state.show_definition = not st.session_state.show_definition

# Display String 2 if toggled on
if st.session_state.show_pinyin:
    st.write(pinyin)

# Display String 3 if toggled on
if st.session_state.show_definition:
    st.write(definition)
