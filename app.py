import threading
import time
from datetime import datetime
from uuid import uuid4

import requests
from flask import Flask, jsonify, request, abort
import streamlit as st

flask_app = Flask(__name__)

DATA = {"posts": []}

def _now():
    return datetime.utcnow().isoformat() + "Z"

@flask_app.route('/api/posts', methods=['GET', 'POST'])
def posts_api():
    if request.method == 'GET':
        q = request.args.get('q', '').lower()
        tag = request.args.get('tag')
        results = DATA['posts'][:]
        if q:
            results = [p for p in results if q in p['title'].lower() or q in p['content'].lower()]
        if tag:
            results = [p for p in results if tag in p.get('tags', [])]
        return jsonify(results)
    payload = request.get_json() or request.form
    title = payload.get('title')
    content = payload.get('content')
    tags = payload.get('tags') or []
    parent = payload.get('parent')
    if not title or not content:
        return jsonify({'error': 'title and content required'}), 400
    pid = len(DATA['posts'])
    post = {
        'id': pid,
        'uuid': str(uuid4()),
        'title': title,
        'content': content,
        'tags': tags,
        'parent': parent,
        'forks': [],
        'likes': 0,
        'created_at': _now()
    }
    DATA['posts'].append(post)
    if parent is not None:
        try:
            DATA['posts'][int(parent)]['forks'].append(pid)
        except Exception:
            pass
    return jsonify(post), 201

@flask_app.route('/api/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def post_detail_api(post_id):
    if post_id < 0 or post_id >= len(DATA['posts']):
        abort(404)
    if request.method == 'GET':
        return jsonify(DATA['posts'][post_id])
    if request.method == 'PUT':
        payload = request.get_json() or {}
        DATA['posts'][post_id]['title'] = payload.get('title', DATA['posts'][post_id]['title'])
        DATA['posts'][post_id]['content'] = payload.get('content', DATA['posts'][post_id]['content'])
        DATA['posts'][post_id]['tags'] = payload.get('tags', DATA['posts'][post_id].get('tags', []))
        return jsonify(DATA['posts'][post_id])
    if request.method == 'DELETE':
        DATA['posts'][post_id]['deleted'] = True
        return jsonify({'status': 'deleted'})

@flask_app.route('/api/fork/<int:post_id>', methods=['POST'])
def fork_post(post_id):
    if post_id < 0 or post_id >= len(DATA['posts']):
        abort(404)
    payload = request.get_json() or request.form
    title = payload.get('title') or DATA['posts'][post_id]['title'] + ' (fork)'
    content = payload.get('content') or DATA['posts'][post_id]['content']
    tags = payload.get('tags') or DATA['posts'][post_id].get('tags', [])
    r = requests.post('http://127.0.0.1:5001/api/posts', json={'title': title, 'content': content, 'tags': tags, 'parent': post_id})
    return jsonify(r.json()), r.status_code

@flask_app.route('/api/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if post_id < 0 or post_id >= len(DATA['posts']):
        abort(404)
    DATA['posts'][post_id]['likes'] += 1
    return jsonify({'likes': DATA['posts'][post_id]['likes']})

@flask_app.route('/api/tree/<int:post_id>', methods=['GET'])
def tree_api(post_id):
    if post_id < 0 or post_id >= len(DATA['posts']):
        abort(404)
    def build(node_id):
        node = DATA['posts'][node_id]
        return {
            'id': node['id'],
            'title': node['title'],
            'forks': [build(f) for f in node.get('forks', [])]
        }
    return jsonify(build(post_id))

def run_flask():
    flask_app.run(port=5001)

threading.Thread(target=run_flask, daemon=True).start()

st.set_page_config(page_title='BranchBlog — Flask + Streamlit', layout='wide')

if 'api_base' not in st.session_state:
    st.session_state.api_base = 'http://127.0.0.1:5001/api'

theme = st.sidebar.radio('Theme', ['Dark', 'Light'])
if theme == 'Dark':
    css = """
    <style>
    body {background: linear-gradient(135deg,#1e1e2f,#2b2b40);} 
    .sidebar .sidebar-content {background: rgba(255,255,255,0.1); backdrop-filter: blur(12px); border-radius: 16px;}
    .post {background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 18px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 25px rgba(0,0,0,0.35);} 
    .title {font-size: 26px; font-weight: 800; color: #ffffff; margin-bottom: 10px;} 
    .meta {color: #c9c9c9; font-size: 13px; margin-bottom: 14px;} 
    .stButton>button {background: linear-gradient(135deg,#6a85ff,#5a6bff); color: white; border: none; padding: 10px 18px; border-radius: 12px; font-weight: 700; transition: 0.25s;} 
    .stButton>button:hover {background: linear-gradient(135deg,#4f64ff,#4358ff); transform: scale(1.03);} 
    input, textarea {background: rgba(255,255,255,0.12) !important; color: #ffffff !important; border-radius: 12px !important;}
    label, h1, h2, h3, p {color: #ffffff !important;}
    @keyframes gradientShift {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}

body {
  background: linear-gradient(135deg,#1e1e2f,#2b2b40,#3a1e5f,#1e3f5f);
  background-size: 400% 400%;
  animation: gradientShift 18s ease infinite;
}

.post {transition: transform 0.25s ease, box-shadow 0.25s ease;}
.post:hover {transform: translateY(-6px); box-shadow: 0 8px 30px rgba(0,0,0,0.45);} 
</style>
    """
else:
    css = """
    <style>
    body {background: #f0f4ff;} 
    .sidebar .sidebar-content {background: #ffffff; border-radius: 16px;} 
    .post {background: #ffffff; border-radius: 18px; padding: 22px; margin-bottom: 20px; box-shadow: 0 4px 18px rgba(0,0,0,0.08);} 
    .title {font-size: 26px; font-weight: 800; color: #000000; margin-bottom: 10px;} 
    .meta {color: #555; font-size: 13px; margin-bottom: 14px;} 
    .stButton>button {background: linear-gradient(135deg,#7aa0ff,#6b8cff); color: white; border: none; padding: 10px 18px; border-radius: 12px; font-weight: 700; transition: 0.25s;} 
    .stButton>button:hover {background: linear-gradient(135deg,#5678ff,#4c6cff); transform: scale(1.03);} 
    input, textarea {background: #ffffff !important; color: #000000 !important; border-radius: 12px !important; border: 1px solid #ccc !important;} 
    label, h1, h2, h3, p {color: #000000 !important;} 
    </style>
    """
st.markdown(css, unsafe_allow_html=True)

st.sidebar.title('Navigation')
page = st.sidebar.radio('', ['Home', 'Add Post', 'Post Detail', 'Branch Visualizer', 'Search'])

if page == 'Home':
    st.title('BranchBlog')
    st.write('A blog with collaborative branching — fork posts and build alternate storylines.')
    r = requests.get(f"{st.session_state.api_base}/posts")
    posts = r.json() if r.status_code == 200 else []
    if not posts:
        st.info('No posts yet — create one!')
    for post in reversed(posts):
        if post.get('deleted'):
            continue
        with st.container():
            st.markdown(f"<div class='post'>", unsafe_allow_html=True)
            st.markdown(f"<div class='title'>{post['title']}</div>")
            st.markdown(f"<div class='meta'>Likes: {post['likes']} • ID: {post['id']} • Created: {post['created_at']}</div>")
            st.write(post['content'][:300] + ('...' if len(post['content'])>300 else ''))
            cols = st.columns([1,1,1,6])
            if cols[0].button('View', key=f"v{post['id']}"):
                st.session_state.selected_post = post['id']
                st.experimental_rerun()
            if cols[1].button('Fork', key=f"f{post['id']}"):
                base = post
                new_title = st.text_input('Fork title', value=base['title'] + ' (fork)')
                new_content = st.text_area('Edit fork content', value=base['content'], key=f'fork_text_{post["id"]}')
                if st.button('Create Fork', key=f'create_fork_{post["id"]}'):
                    requests.post(f"{st.session_state.api_base}/fork/{post['id']}", json={'title': new_title, 'content': new_content})
                    st.success('Fork created')
                    time.sleep(0.4)
                    st.experimental_rerun()
            if cols[2].button('Like', key=f"l{post['id']}"):
                requests.post(f"{st.session_state.api_base}/like/{post['id']}")
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif page == 'Add Post':
    st.title('Create a New Post')
    title = st.text_input('Title')
    tags = st.text_input('Tags (comma separated)')
    content = st.text_area('Content', height=300)
    parent = st.number_input('Parent post ID (optional, leave blank for new)', min_value=0, step=1, value=0)
    if st.button('Publish'):
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
        payload = {'title': title, 'content': content, 'tags': tags_list, 'parent': parent if parent is not None and parent != 0 else None}
        requests.post(f"{st.session_state.api_base}/posts", json=payload)
        st.success('Published')
        time.sleep(0.4)
        st.experimental_rerun()

elif page == 'Post Detail':
    st.title('Post Detail')
    pid = st.session_state.get('selected_post')
    if pid is None:
        st.info('Select a post from Home to view details')
    else:
        r = requests.get(f"{st.session_state.api_base}/posts/{pid}")
        if r.status_code != 200:
            st.error('Post not found')
        else:
            post = r.json()
            st.header(post['title'])
            st.write(post['content'])
            st.write('Tags:', ', '.join(post.get('tags', [])))
            st.write('Likes:', post['likes'])
            if st.button('Fork this post'):
                new_title = st.text_input('Fork title', value=post['title'] + ' (fork)')
                new_content = st.text_area('Fork content', value=post['content'], key='fork_detail')
                if st.button('Create Fork Now'):
                    requests.post(f"{st.session_state.api_base}/fork/{pid}", json={'title': new_title, 'content': new_content})
                    st.success('Fork created')
                    time.sleep(0.3)
                    st.experimental_rerun()

elif page == 'Branch Visualizer':
    st.title('Branch Visualizer')
    pid = st.number_input('Root post ID', min_value=0, step=1, value=0)
    r = requests.get(f"{st.session_state.api_base}/tree/{pid}")
    if r.status_code != 200:
        st.error('Tree not found for that ID')
    else:
        tree = r.json()
        def render(node, depth=0):
            st.markdown(' ' * (depth * 4) + f"- **{node['title']}** (ID: {node['id']})")
            for f in node.get('forks', []):
                render(f, depth+1)
        render(tree)

elif page == 'Search':
    st.title('Search Posts')
    q = st.text_input('Search query')
    tag = st.text_input('Tag filter')
    if st.button('Search'):
        params = {}
        if q:
            params['q'] = q
        if tag:
            params['tag'] = tag
        r = requests.get(f"{st.session_state.api_base}/posts", params=params)
        results = r.json() if r.status_code == 200 else []
        st.write(f'Found {len(results)} results')
        for p in results:
            st.markdown(f"**{p['title']}** (ID: {p['id']})")
            st.write(p['content'][:250] + ('...' if len(p['content'])>250 else ''))

st.sidebar.markdown('---')
st.sidebar.write('Unique feature: Collaborative Branching — fork any post to create parallel storylines or alternate takes. Visualize the branch tree and remix content.')
