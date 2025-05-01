import streamlit as st
from chinochau.data import Flashcard
from chinochau.service import ChinoChau
from chinochau.deepseek import get_examples_deepseek

# Initialize session state variables if they don't exist
if "show_pinyin" not in st.session_state:
    st.session_state.show_pinyin = False
if "show_definition" not in st.session_state:
    st.session_state.show_definition = False
if "chino" not in st.session_state:
    st.session_state.chino = ChinoChau("input.txt", fill_null_definitions=False)
if "flashcard" not in st.session_state:
    st.session_state.flashcard = Flashcard(
        "Placeholder", "Placeholder", ["Placeholder"]
    )
if "index" not in st.session_state:
    st.session_state.index = 0


file_name = st.text_input(
    "Enter the filename to generate flashcards:", placeholder="input.txt"
)


if st.button("Submit"):
    st.session_state.chino = ChinoChau(file_name, fill_null_definitions=False)
    st.session_state.chino.update_master_flashcards()
    st.session_state.flashcard = st.session_state.chino.get(0)


st.header(f"Flashcard index {st.session_state.index} of {len(st.session_state.chino)}")


c1, c2 = st.columns(2)
with c1:
    if st.button("Previous"):
        st.session_state.index -= 1
        if st.session_state.index < 0:
            st.session_state.index = len(st.session_state.chino) - 1
        st.session_state.flashcard = st.session_state.chino.get(st.session_state.index)
        st.session_state.example = None

with c2:
    if st.button("Next"):
        st.session_state.index += 1
        if st.session_state.index >= len(st.session_state.chino):
            st.session_state.index = 0
        st.session_state.flashcard = st.session_state.chino.get(st.session_state.index)
        st.session_state.example = None


chinese = st.session_state.flashcard.chinese
pinyin = st.session_state.flashcard.pinyin
definition = st.session_state.flashcard.definitions


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

if st.button("Get Examples"):
    if st.session_state.flashcard.example is not None:
        st.session_state.examples = st.session_state.flashcard.example
    else:
        new_examples = get_examples_deepseek(st.session_state.flashcard.chinese)
        st.session_state.flashcard.example = new_examples
        st.session_state.examples = st.session_state.flashcard.example


if "examples" in st.session_state:
    st.write(st.session_state.examples)
