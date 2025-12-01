import streamlit as st
import time
from datetime import datetime
from uuid import uuid4
from io import BytesIO
from PIL import Image

st.set_page_config(page_title='BranchBlog Multimodal', layout='wide')

if 'posts' not in st.session_state:
    st.session_state.posts = []

def now():
    return datetime.utcnow().isoformat() + 'Z'

def dominant_color(image: Image.Image):
    small = image.resize((64,64))
    result = small.convert('RGBA').getdata()
    freq = {}
    for px in result:
        if px[3] < 50:
            continue
        key = (px[0]//32*32, px[1]//32*32, px[2]//32*32)
        freq[key] = freq.get(key, 0) + 1
    if not freq:
        return (200,200,200)
    best = max(freq.items(), key=lambda x: x[1])[0]
    return best

def suggest_image_tags(image: Image.Image):
    img = image.convert('L')
    avg = sum(img.getdata())/ (img.width*img.height)
    tags = []
    if avg > 180:
        tags.append('bright')
    elif avg < 70:
        tags.append('dark')
    else:
        tags.append('balanced')
    unique_colors = len(set(image.convert('RGB').getdata()))
    if unique_colors > 10000:
        tags.append('colorful')
    else:
        tags.append('muted')
    return tags

page = st.sidebar.radio('', ['Home', 'Add Post', 'Post Detail', 'Branch Visualizer', 'Search'])

st.markdown("""
<style>
@keyframes gradientShift {0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
body {background: linear-gradient(135deg,#0f1724,#071028,#0b1020); background-size:400% 400%; animation:gradientShift 16s ease infinite;}
.post {background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.06); border-radius:16px; padding:18px; margin-bottom:16px;}
.title{font-size:22px;font-weight:800;color:#fff}
.meta{color:#ccc;font-size:12px}
.stButton>button{background:linear-gradient(135deg,#7aa0ff,#5a6bff);color:#fff;border-radius:10px;padding:8px 14px;border:none}
input, textarea{background:rgba(255,255,255,0.06)!important;color:#fff!important;border-radius:12px!important}
</style>
""", unsafe_allow_html=True)

if page == 'Home':
    st.title('BranchBlog — Multimodal')
    if not st.session_state.posts:
        st.info('No posts yet.')
    for p in reversed(st.session_state.posts):
        if p.get('deleted'):
            continue
        with st.container():
            st.markdown(f"<div class='post'>", unsafe_allow_html=True)
            st.markdown(f"<div class='title'>{p['title']}</div>")
            st.markdown(f"<div class='meta'>ID: {p['id']} • Likes: {p['likes']} • Created: {p['created_at']}</div>")
            if p.get('cover'):
                st.image(p['cover']['preview'], use_column_width=True)
            if p.get('audio'):
                st.audio(p['audio']['data'])
            if p.get('video'):
                st.video(p['video']['data'])
            st.write(p['content'][:400] + ('...' if len(p['content'])>400 else ''))
            cols = st.columns([1,1,1,6])
            if cols[0].button('View', key=f"v{p['id']}"):
                st.session_state.view = p['id']
                st.experimental_rerun()
            if cols[1].button('Fork', key=f"f{p['id']}"):
                st.session_state.fork = p['id']
                st.experimental_rerun()
            if cols[2].button('Like', key=f"l{p['id']}"):
                p['likes'] += 1
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

if page == 'Add Post':
    st.title('Create Multimodal Post')
    title = st.text_input('Title')
    tags = st.text_input('Tags (comma separated)')
    content = st.text_area('Content', height=220)
    uploaded_images = st.file_uploader('Upload images (jpg/png) — cover will be first image', type=['png','jpg','jpeg'], accept_multiple_files=True)
    uploaded_audio = st.file_uploader('Upload audio (mp3/wav)', type=['mp3','wav'])
    uploaded_video = st.file_uploader('Upload video (mp4)', type=['mp4'])
    if uploaded_images:
        first = uploaded_images[0]
        img = Image.open(first)
        buf = BytesIO()
        img.save(buf, format='PNG')
        preview = buf.getvalue()
        dom = dominant_color(img)
        suggested = suggest_image_tags(img)
    else:
        preview = None
        dom = None
        suggested = []
    if st.button('Publish'):
        pid = len(st.session_state.posts)
        post = {'id': pid, 'title': title or f'Post {pid}', 'content': content or '', 'likes': 0, 'created_at': now(), 'forks': [], 'parent': None, 'tags': [t.strip() for t in tags.split(',') if t.strip()]} 
        if preview:
            post['cover'] = {'preview': preview, 'dominant_color': dom, 'suggested_tags': suggested}
            post['tags'].extend([t for t in suggested if t not in post['tags']])
        if uploaded_audio:
            audio_bytes = uploaded_audio.read()
            post['audio'] = {'data': audio_bytes, 'filename': uploaded_audio.name}
        if uploaded_video:
            video_bytes = uploaded_video.read()
            post['video'] = {'data': video_bytes, 'filename': uploaded_video.name}
        images_data = []
        for f in uploaded_images:
            data = f.read()
            images_data.append({'name': f.name, 'data': data})
        if images_data:
            post['images'] = images_data
        st.session_state.posts.append(post)
        st.success('Published')
        time.sleep(0.4)
        st.experimental_rerun()

if page == 'Post Detail':
    st.title('Post Detail')
    if 'view' not in st.session_state:
        st.info('Select a post from Home')
    else:
        pid = st.session_state.view
        if pid >= len(st.session_state.posts):
            st.error('Post not found')
        else:
            p = st.session_state.posts[pid]
            st.header(p['title'])
            if p.get('cover'):
                st.image(p['cover']['preview'])
                dc = p['cover'].get('dominant_color')
                if dc:
                    st.markdown(f"Dominant color: rgb{dc}")
                if p['cover'].get('suggested_tags'):
                    st.markdown('Suggested tags: ' + ', '.join(p['cover']['suggested_tags']))
            st.write(p['content'])
            if p.get('images'):
                cols = st.columns(min(3, len(p['images'])))
                for i,img in enumerate(p['images']):
                    cols[i%3].image(img['data'], caption=img['name'])
            if p.get('audio'):
                st.audio(p['audio']['data'])
            if p.get('video'):
                st.video(p['video']['data'])
            if st.button('Fork this post'):
                st.session_state.fork = pid
                st.experimental_rerun()

if 'fork' in st.session_state and page != 'Add Post':
    pid = st.session_state.fork
    base = st.session_state.posts[pid]
    st.title('Fork Post')
    new_title = st.text_input('Fork Title', base['title'] + ' (fork)')
    new_content = st.text_area('Fork Content', base['content'])
    attach_images = st.file_uploader('Add/replace images (optional)', type=['png','jpg','jpeg'], accept_multiple_files=True)
    attach_audio = st.file_uploader('Add/replace audio (optional)', type=['mp3','wav'])
    if st.button('Create Fork'):
        nid = len(st.session_state.posts)
        newpost = {'id': nid, 'title': new_title or f'Post {nid}', 'content': new_content or '', 'likes': 0, 'created_at': now(), 'forks': [], 'parent': pid, 'tags': base.get('tags',[])[:]} 
        if attach_images:
            images_data = []
            for f in attach_images:
                images_data.append({'name': f.name, 'data': f.read()})
            newpost['images'] = images_data
            img = Image.open(attach_images[0])
            buf = BytesIO(); img.save(buf, format='PNG')
            newpost['cover'] = {'preview': buf.getvalue(), 'dominant_color': dominant_color(img), 'suggested_tags': suggest_image_tags(img)}
            newpost['tags'].extend([t for t in newpost['cover']['suggested_tags'] if t not in newpost['tags']])
        else:
            if base.get('images'):
                newpost['images'] = base['images'][:]
            if base.get('cover'):
                newpost['cover'] = base['cover']
        if attach_audio:
            newpost['audio'] = {'data': attach_audio.read(), 'filename': attach_audio.name}
        else:
            if base.get('audio'):
                newpost['audio'] = base['audio']
        st.session_state.posts.append(newpost)
        base['forks'].append(nid)
        del st.session_state.fork
        st.success('Fork created')
        time.sleep(0.4)
        st.experimental_rerun()

if page == 'Branch Visualizer':
    st.title('Branch Visualizer')
    pid = st.number_input('Root ID', min_value=0, step=1, value=0)
    if pid < len(st.session_state.posts):
        def render_tree(i, depth=0):
            p = st.session_state.posts[i]
            indent = ' ' * (depth*4)
            st.markdown(indent + f"- **{p['title']}** (ID: {p['id']})")
            if p.get('cover'):
                col = st.columns([1,4])
                col[0].write('')
                col[1].image(p['cover']['preview'], width=120)
            for f in p['forks']:
                render_tree(f, depth+1)
        render_tree(pid)
    else:
        st.error('Invalid ID')

if page == 'Search':
    st.title('Search Posts')
    q = st.text_input('Query')
    tag = st.text_input('Tag')
    if st.button('Search'):
        res = [p for p in st.session_state.posts if q.lower() in p['title'].lower() or q.lower() in p['content'].lower() or q.lower() in ' '.join(p.get('tags',[])).lower()]
        st.write(f'Found {len(res)} results')
        for p in res:
            st.markdown(f"**{p['title']}** (ID: {p['id']}) — Tags: {', '.join(p.get('tags',[]))}")
            if p.get('cover'):
                st.image(p['cover']['preview'], width=200)
            st.write(p['content'][:300] + ('...' if len(p['content'])>300 else ''))
