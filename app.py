import streamlit as st
import time
import os
from gradio_client import Client

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Velo 2.0", page_icon="⚡", layout="centered")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');
:root { --bg:#090909;--surface:#111;--border:#1e1e1e;--accent:#c8ff00;--text:#f0f0f0;--muted:#555; }
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif;}
[data-testid="stHeader"]{background:transparent!important;}
#MainMenu,footer{visibility:hidden;}
.hero{text-align:center;padding:3rem 0 1.5rem;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(5rem,15vw,9rem);letter-spacing:.05em;line-height:.9;color:var(--text);margin:0;}
.hero-title span{color:var(--accent);}
.hero-sub{font-size:.85rem;font-weight:300;letter-spacing:.3em;text-transform:uppercase;color:var(--muted);margin-top:.8rem;}
.card-label{font-size:.7rem;letter-spacing:.25em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem;}
.divider{height:1px;background:var(--border);margin:1.5rem 0;}
textarea,.stTextArea textarea{background:#0e0e0e!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;font-family:'DM Sans',sans-serif!important;}
textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 0 2px rgba(200,255,0,.1)!important;}
.stButton>button{background:var(--accent)!important;color:#000!important;border:none!important;font-family:'Bebas Neue',sans-serif!important;font-size:1.3rem!important;letter-spacing:.15em!important;padding:.7rem 2.5rem!important;border-radius:6px!important;width:100%!important;transition:all .2s!important;}
.stButton>button:hover{background:#d9ff33!important;transform:translateY(-1px)!important;box-shadow:0 6px 24px rgba(200,255,0,.25)!important;}
.queue-item{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:.8rem 1rem;margin-bottom:.5rem;font-size:.8rem;color:var(--muted);display:flex;align-items:center;gap:.6rem;}
.status-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
.dot-waiting{background:#555;}
.dot-generating{background:var(--accent);animation:pulse 1.2s infinite;}
.dot-done{background:#00ff88;}
.dot-error{background:#ff3c00;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
label{color:var(--muted)!important;font-size:.75rem!important;letter-spacing:.15em!important;text-transform:uppercase!important;}
video{border-radius:10px;border:1px solid var(--border);width:100%;}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1 class="hero-title">VELO<span>2.0</span></h1>
  <p class="hero-sub">AI Video Generator &nbsp;·&nbsp; LTX-Video + MMAudio</p>
</div>
""", unsafe_allow_html=True)

GRADIO_URL = st.secrets.get("GRADIO_URL", "https://8b8e4405b7bf7efeb2.gradio.live")

if "queue" not in st.session_state:
    st.session_state.queue = []

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="card-label">Video Prompt</div>', unsafe_allow_html=True)
prompt = st.text_area(
    label="prompt", label_visibility="collapsed",
    placeholder="Describe your video — scene, camera, lighting, mood...\nTip: each line becomes a separate video in the queue.",
    height=120,
)

col1, col2 = st.columns(2)
with col1:
    resolution = st.selectbox("Resolution", ["832x480","832x624","624x832","720x720","480x832"], index=0)
with col2:
    dur_label = st.selectbox("Duration", ["3s (73 frames)","5s (121 frames)","8s (193 frames)","10s (241 frames)"], index=1)

enable_audio = st.toggle("🎵 MMAudio — Synchronized Audio", value=True)

frames_map = {"3s (73 frames)":73,"5s (121 frames)":121,"8s (193 frames)":193,"10s (241 frames)":241}

st.markdown("<br>", unsafe_allow_html=True)
add_btn = st.button("⚡ ADD TO QUEUE & GENERATE")


def extract_video(gallery):
    if not gallery:
        return None, None
    if isinstance(gallery, dict):
        gallery = gallery.get("value", [])
    for item in gallery:
        if isinstance(item, dict):
            v = item.get("video")
            if isinstance(v, str) and v:
                return v, None
            if isinstance(v, dict):
                p, u = v.get("path"), v.get("url")
                if p and os.path.exists(p):
                    return p, None
                if u:
                    return None, u
        elif isinstance(item, str) and ".mp4" in item:
            return item, None
    return None, None


def run_generation(job):
    client = Client(GRADIO_URL)

    # Save inputs
    client.predict(
        target="state",
        image_mask_guide={"background": None, "layers": [], "composite": None},
        lset_name="", image_mode=0,
        prompt=job["prompt"], alt_prompt="", negative_prompt="",
        resolution=job["resolution"],
        video_length=float(job["frames"]),
        duration_seconds=0, batch_size=1, seed=-1, force_fps="",
        num_inference_steps=8.0, guidance_scale=4.0,
        guidance2_scale=5.0, guidance3_scale=5.0,
        switch_threshold=0, switch_threshold2=0,
        guidance_phases=2, model_switch_phase=1,
        alt_guidance_scale=6.0, audio_guidance_scale=4.0,
        audio_scale=1.0, flow_shift=5.0, sample_solver="",
        embedded_guidance_scale=6.0, repeat_generation=1,
        multi_prompts_gen_type=0, multi_images_gen_type=0,
        skip_steps_cache_type="", skip_steps_multiplier=1.75,
        skip_steps_start_step_perc=0, loras_choices=[], loras_multipliers="",
        image_prompt_type="", image_start=[], image_end=[],
        model_mode=None, video_source=None, keep_frames_video_source="",
        input_video_strength=1.0, video_guide_outpainting="#",
        video_prompt_type="", image_refs=[], frames_positions="",
        video_guide=None, image_guide=None, keep_frames_video_guide="",
        denoising_strength=1.0, masking_strength=0.0,
        video_mask=None, image_mask=None,
        control_net_weight=1.0, control_net_weight2=1.0,
        control_net_weight_alt=1.0, motion_amplitude=1.0, mask_expand=0,
        audio_guide=None, audio_guide2=None, custom_guide=None,
        audio_source=None, audio_prompt_type="",
        speakers_locations="0:45 55:100",
        sliding_window_size=481, sliding_window_overlap=17,
        sliding_window_color_correction_strength=0,
        sliding_window_overlap_noise=0, sliding_window_discard_last_frames=0,
        image_refs_relative_size=50, remove_background_images_ref=1,
        temporal_upsampling="", spatial_upsampling="",
        film_grain_intensity=0, film_grain_saturation=0.5,
        MMAudio_setting=1 if job["audio"] else 0,
        MMAudio_prompt="", MMAudio_neg_prompt="",
        RIFLEx_setting=0, NAG_scale=1.0, NAG_tau=3.5, NAG_alpha=0.5,
        slg_switch=0, slg_layers=[9], slg_start_perc=10, slg_end_perc=90,
        apg_switch=0, cfg_star_switch=0, cfg_zero_step=-1,
        prompt_enhancer="", min_frames_if_references=1, override_profile=-1,
        pace=0.5, exaggeration=0.5, temperature=0.8, top_k=50,
        output_filename="", mode="",
        api_name="/save_inputs_28",
    )

    # Kick off generation via queue
    client.predict(api_name="/prepare_generate_video")
    client.predict(api_name="/init_process_queue_if_any")

    # Poll until status clears (means generation finished)
    for _ in range(120):  # max 10 min
        time.sleep(5)
        try:
            status = str(client.predict(api_name="/refresh_status_async"))
            if not status or status.strip() in ("", "null", "None"):
                break
            # If it contains a % progress it's still running, keep polling
        except Exception:
            break

    # Fetch the gallery
    gallery_result = client.predict(api_name="/refresh_gallery")
    gallery = gallery_result[1] if isinstance(gallery_result, (list, tuple)) and len(gallery_result) > 1 else []
    return extract_video(gallery)


# ── Queue rendering ───────────────────────────────────────────────────────────
def render_queue():
    if not st.session_state.queue:
        return
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-label">Queue</div>', unsafe_allow_html=True)
    for i, job in enumerate(st.session_state.queue):
        dot = {"waiting":"dot-waiting","generating":"dot-generating","done":"dot-done","error":"dot-error"}.get(job["status"],"dot-waiting")
        label = {"waiting":"Waiting","generating":"Generating...","done":"✓ Done","error":"✗ Failed"}.get(job["status"],"")
        short = job["prompt"][:65] + ("..." if len(job["prompt"]) > 65 else "")
        st.markdown(f"""
        <div class="queue-item">
            <div class="status-dot {dot}"></div>
            <span style="color:#888">{i+1}.</span>
            <span style="flex:1">{short}</span>
            <span style="color:#666;font-size:.7rem">{label}</span>
        </div>""", unsafe_allow_html=True)


# ── Main logic ────────────────────────────────────────────────────────────────
if add_btn:
    lines = [l.strip() for l in prompt.strip().splitlines() if l.strip()]
    if not lines:
        st.warning("Please enter a prompt first.")
    else:
        for line in lines:
            st.session_state.queue.append({
                "prompt": line,
                "resolution": resolution,
                "frames": frames_map[dur_label],
                "audio": enable_audio,
                "status": "waiting",
                "video_bytes": None,
                "video_url": None,
                "error": None,
            })
        st.rerun()

# Process waiting jobs one at a time
for i, job in enumerate(st.session_state.queue):
    if job["status"] == "waiting":
        render_queue()
        job["status"] = "generating"
        with st.spinner(f"Generating: {job['prompt'][:50]}..."):
            try:
                path, url = run_generation(job)
                if path and os.path.exists(path):
                    with open(path, "rb") as f:
                        job["video_bytes"] = f.read()
                    job["status"] = "done"
                elif url:
                    job["video_url"] = url
                    job["status"] = "done"
                else:
                    job["status"] = "error"
                    job["error"] = "No video returned. The generation may have completed on your PC — check the Pinokio output folder."
            except Exception as e:
                job["status"] = "error"
                job["error"] = str(e)
        st.rerun()
        break  # process one at a time, rerun handles the next

render_queue()

# ── Show results ──────────────────────────────────────────────────────────────
done = [j for j in st.session_state.queue if j["status"] in ("done", "error")]
if done:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-label">🎬 Generated Videos</div>', unsafe_allow_html=True)
    for i, job in enumerate(reversed(done)):
        st.caption(job["prompt"][:80])
        if job["status"] == "done":
            if job.get("video_bytes"):
                st.video(job["video_bytes"])
                st.download_button("⬇ DOWNLOAD", data=job["video_bytes"],
                    file_name=f"velo2_{i+1}.mp4", mime="video/mp4", key=f"dl_{i}")
            elif job.get("video_url"):
                st.video(job["video_url"])
        else:
            st.error(job["error"])

if st.session_state.queue:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear Queue"):
        st.session_state.queue = []
        st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:3rem 0 1rem;color:#222;font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;">
  Velo 2.0 &nbsp;·&nbsp; Local LTX-Video &nbsp;·&nbsp; MMAudio
</div>
""", unsafe_allow_html=True)
