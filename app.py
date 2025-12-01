import streamlit as st

if "posts" not in st.session_state:
    st.session_state.posts = []

st.set_page_config(page_title="Streamlit Blog", layout="centered")

page = st.sidebar.selectbox("Navigation", ["Home", "Add Post", "Post Detail"])

if page == "Home":
    st.title("My Streamlit Blog")
    if st.session_state.posts:
        for post in st.session_state.posts:
            st.subheader(post["title"])
            st.write(post["content"][:120] + "...")
            if st.button(f"View Post {post['id']}"):
                st.session_state.selected_post = post["id"]
                st.experimental_rerun()
    else:
        st.write("No posts yet.")

elif page == "Add Post":
    st.title("Add New Blog Post")
    title = st.text_input("Title")
    content = st.text_area("Content")
    if st.button("Submit"):
        st.session_state.posts.append({"id": len(st.session_state.posts), "title": title, "content": content})
        st.success("Post added.")

elif page == "Post Detail":
    st.title("Post Detail")
    if "selected_post" in st.session_state:
        pid = st.session_state.selected_post
        if pid < len(st.session_state.posts):
            post = st.session_state.posts[pid]
            st.header(post["title"])
            st.write(post["content"])
        else:
            st.error("Post not found.")
    else:
        st.write("Select a post from Home.")
