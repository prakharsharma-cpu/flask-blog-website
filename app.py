import streamlit as st
import time
from datetime import datetime
from uuid import uuid4

if 'posts' not in st.session_state:
    st.session_state.posts = []

st.set_page_config(page_title='BranchBlog — Streamlit Native', layout='wide')

def now():
    return datetime.utcnow().isoformat() + 'Z'

page = st.sidebar.radio('', ['Home', 'Add Post', 'Post Detail', 'Branch Visualizer', 'Search'])

st.markdown("""
<style>
@keyframes gradientShift {0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
body {background: linear-gradient(135deg,#1e1e2f,#2b2b40,#3a1e5f,#1e3f5f); background-size:400% 400%; animation:gradientShift 18s ease infinite;}
.post {background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); border-radius:18px; padding:24px; margin-bottom:20px; box-shadow:0 4px 25px rgba(0,0,0,0.35); transition:0.25s;} 
.post:hover {transform:translateY(-6px); box-shadow:0 8px 30px rgba(0,0,0,0.45);} 
.title {font-size:26px; font-weight:800; color:#fff;} 
.meta {color:#ccc; font-size:13px;} 
.stButton>button {background:linear-gradient(135deg,#6a85ff,#5a6bff); color:#fff; border:none; padding:10px 18px; border-radius:12px; font-weight:700; transition:0.25s;} 
.stButton>button:hover {transform:scale(1.03);} 
input, textarea {background:rgba(255,255,255,0.12)!important; color:#fff!important; border-radius:12px!important;} 
label, h1, h2, h3, p {color:#fff!important;} 
</style>
""", unsafe_allow_html=True)

if page == 'Home':
    st.title('BranchBlog')
    if not st.session_state.posts:
        st.info('No posts yet.')
    for p in reversed(st.session_state.posts):
        with st.container():
            st.markdown(f"<div class='post'>", unsafe_allow_html=True)
            st.markdown(f"<div class='title'>{p['title']}</div>")
            st.markdown(f"<div class='meta'>Likes: {p['likes']} • ID: {p['id']} • Created: {p['created_at']}</div>")
            st.write(p['content'][:250] + ('...' if len(p['content'])>250 else ''))
            c = st.columns([1,1,1,6])
            if c[0].button('View', key=f'v{p["id"]}'):
                st.session_state.view = p['id']
                st.experimental_rerun()
            if c[1].button('Fork', key=f'f{p["id"]}'):
                st.session_state.fork = p['id']
                st.experimental_rerun()
            if c[2].button('Like', key=f'l{p["id"]}'):
                p['likes'] += 1
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

if page == 'Add Post':
    st.title('Add Post')
    title = st.text_input('Title')
    content = st.text_area('Content', height=200)
    if st.button('Publish'):
        pid = len(st.session_state.posts)
        st.session_state.posts.append({
            'id': pid,
            'title': title,
            'content': content,
            'likes': 0,
            'created_at': now(),
            'forks': [],
            'parent': None
        })
        st.success('Published')
        time.sleep(0.3)
        st.experimental_rerun()

if page == 'Post Detail':
    st.title('Post Detail')
    if 'view' not in st.session_state:
        st.info('Select a post first.')
    else:
        pid = st.session_state.view
        p = st.session_state.posts[pid]
        st.header(p['title'])
        st.write(p['content'])
        if st.button('Fork this post'):
            st.session_state.fork = pid
            st.experimental_rerun()

if 'fork' in st.session_state and page != 'Add Post':
    pid = st.session_state.fork
    base = st.session_state.posts[pid]
    st.title('Fork Post')
    new_title = st.text_input('Fork Title', base['title'] + ' (fork)')
    new_content = st.text_area('Fork Content', base['content'])
    if st.button('Create Fork'):
        nid = len(st.session_state.posts)
        st.session_state.posts.append({
            'id': nid,
            'title': new_title,
            'content': new_content,
            'likes': 0,
            'created_at': now(),
            'forks': [],
            'parent': pid
        })
        base['forks'].append(nid)
        del st.session_state.fork
        st.success('Forked!')
        time.sleep(0.3)
        st.experimental_rerun()

if page == 'Branch Visualizer':
    st.title('Branch Visualizer')
    pid = st.number_input('Root ID', min_value=0, step=1, value=0)
    if pid < len(st.session_state.posts):
        def render_tree(i, depth=0):
            p = st.session_state.posts[i]
            st.markdown(' ' * (depth * 4) + f"- **{p['title']}** (ID: {p['id']})")
            for f in p['forks']:
                render_tree(f, depth+1)
        render_tree(pid)
    else:
        st.error('Invalid ID')

if page == 'Search':
    st.title('Search Posts')
    q = st.text_input('Query')
    if st.button('Search'):
        res = [p for p in st.session_state.posts if q.lower() in p['title'].lower() or q.lower() in p['content'].lower()]
        st.write(f'Found {len(res)} results')
        for p in res:
            st.markdown(f"**{p['title']}** (ID: {p['id']})")
