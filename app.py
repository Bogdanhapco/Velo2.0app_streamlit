import streamlit as st
import time
import tempfile
import os
from gradio_client import Client

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Velo 2.0",
    page_icon="⚡",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #090909;
    --surface: #111111;
    --border: #1e1e1e;
    --accent: #c8ff00;
    --accent2: #ff3c00;
    --text: #f0f0f0;
    --muted: #555;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }

/* Hide default streamlit branding */
#MainMenu, footer { visibility: hidden; }

/* Hero */
.hero {
    text-align: center;
    padding: 3rem 0 1.5rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(5rem, 15vw, 9rem);
    letter-spacing: 0.05em;
    line-height: 0.9;
    color: var(--text);
    margin: 0;
}
.hero-title span {
    color: var(--accent);
}
.hero-sub {
    font-size: 0.85rem;
    font-weight: 300;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.8rem;
}

/* Card */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-label {
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}

/* Streamlit widget overrides */
textarea, .stTextArea textarea {
    background: #0e0e0e !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(200,255,0,0.1) !important;
}

.stSelectbox > div > div, .stSlider {
    background: transparent !important;
}

/* Generate button */
.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    border: none !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.3rem !important;
    letter-spacing: 0.15em !important;
    padding: 0.7rem 2.5rem !important;
    border-radius: 6px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #d9ff33 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(200,255,0,0.25) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Status bar */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 1rem;
    background: rgba(200,255,0,0.05);
    border: 1px solid rgba(200,255,0,0.15);
    border-radius: 8px;
    font-size: 0.8rem;
    color: var(--accent);
    margin-bottom: 1rem;
}
.dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Divider */
.divider {
    height: 1px;
    background: var(--border);
    margin: 1.5rem 0;
}

/* Expander override */
details summary {
    color: var(--muted) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
}

/* Video output */
video {
    border-radius: 10px;
    border: 1px solid var(--border);
    width: 100%;
}

/* Warning / info */
.stAlert {
    background: #111 !important;
    border-color: var(--border) !important;
    color: var(--muted) !important;
    font-size: 0.8rem !important;
}

/* Slider label */
label {
    color: var(--muted) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1 class="hero-title">VELO<span>2.0</span></h1>
    <p class="hero-sub">AI Video Generator &nbsp;·&nbsp; Powered by LTX-Video</p>
</div>
""", unsafe_allow_html=True)

# ── Gradio endpoint ───────────────────────────────────────────────────────────
GRADIO_URL = st.secrets.get("GRADIO_URL", "https://8b8e4405b7bf7efeb2.gradio.live")

# ── Main prompt ───────────────────────────────────────────────────────────────
st.markdown('<div class="card-label">Video Prompt</div>', unsafe_allow_html=True)
prompt = st.text_area(
    label="prompt",
    label_visibility="collapsed",
    placeholder="Describe your video in detail. Include camera movement, scene, characters, lighting, mood...",
    height=130,
)

negative_prompt = st.text_input(
    "Negative Prompt (optional)",
    placeholder="blurry, distorted, low quality...",
    label_visibility="visible",
)

# ── Audio section ─────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="card-label">🎵 MMAudio — Synchronized Audio</div>', unsafe_allow_html=True)

enable_audio = st.toggle("Enable synchronized audio", value=True)

col_a, col_b = st.columns(2)
with col_a:
    audio_prompt = st.text_input(
        "Audio Prompt",
        placeholder="e.g. wind, footsteps, piano",
        disabled=not enable_audio,
    )
with col_b:
    audio_neg_prompt = st.text_input(
        "Audio Negative Prompt",
        placeholder="e.g. noise, static",
        disabled=not enable_audio,
    )

# ── Advanced settings ─────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with st.expander("⚙ ADVANCED SETTINGS"):
    col1, col2 = st.columns(2)
    with col1:
        resolution = st.selectbox(
            "Resolution",
            ["832x480", "832x624", "624x832", "720x720", "480x832", "512x512"],
            index=0,
        )
        num_steps = st.slider("Inference Steps", 4, 30, 8)
    with col2:
        video_length = st.slider("Frames (24 = 1 sec)", 49, 481, 121)
        guidance_scale = st.slider("Guidance Scale (CFG)", 1.0, 10.0, 4.0, 0.5)
    seed = st.number_input("Seed (-1 = random)", value=-1, min_value=-1)

# ── Generate button ───────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
generate = st.button("⚡ GENERATE VIDEO")

# ── Output area ───────────────────────────────────────────────────────────────
if generate:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        st.markdown("""
        <div class="status-bar">
            <div class="dot"></div>
            Connecting to your local LTX-Video instance...
        </div>
        """, unsafe_allow_html=True)

        progress = st.progress(0, text="Initializing...")

        try:
            client = Client(GRADIO_URL)
            progress.progress(10, text="Connected! Sending generation request...")

            result = client.predict(
                target="state",
                image_mask_guide={"background": None, "layers": [], "composite": None},
                lset_name="",
                image_mode=0,
                prompt=prompt,
                alt_prompt="",
                negative_prompt=negative_prompt,
                resolution=resolution,
                video_length=float(video_length),
                duration_seconds=0,
                batch_size=1,
                seed=float(seed),
                force_fps="",
                num_inference_steps=float(num_steps),
                guidance_scale=float(guidance_scale),
                guidance2_scale=5.0,
                guidance3_scale=5.0,
                switch_threshold=0,
                switch_threshold2=0,
                guidance_phases=2,
                model_switch_phase=1,
                alt_guidance_scale=6.0,
                audio_guidance_scale=4.0,
                audio_scale=1.0,
                flow_shift=5.0,
                sample_solver="",
                embedded_guidance_scale=6.0,
                repeat_generation=1,
                multi_prompts_gen_type=0,
                multi_images_gen_type=0,
                skip_steps_cache_type="",
                skip_steps_multiplier="1.75",
                skip_steps_start_step_perc=0,
                loras_choices=[],
                loras_multipliers="",
                image_prompt_type="",
                image_start=[],
                image_end=[],
                model_mode=None,
                video_source=None,
                keep_frames_video_source="",
                input_video_strength=1.0,
                video_guide_outpainting="#",
                video_prompt_type="",
                image_refs=[],
                frames_positions="",
                video_guide=None,
                image_guide=None,
                keep_frames_video_guide="",
                denoising_strength=1.0,
                masking_strength=0.0,
                video_mask=None,
                image_mask=None,
                control_net_weight=1.0,
                control_net_weight2=1.0,
                control_net_weight_alt=1.0,
                motion_amplitude=1.0,
                mask_expand=0,
                audio_guide=None,
                audio_guide2=None,
                custom_guide=None,
                audio_source=None,
                audio_prompt_type="",
                speakers_locations="0:45 55:100",
                sliding_window_size=481,
                sliding_window_overlap=17,
                sliding_window_color_correction_strength=0,
                sliding_window_overlap_noise=0,
                sliding_window_discard_last_frames=0,
                image_refs_relative_size=50,
                remove_background_images_ref=1,
                temporal_upsampling="",
                spatial_upsampling="",
                film_grain_intensity=0,
                film_grain_saturation=0.5,
                MMAudio_setting=1 if enable_audio else 0,
                MMAudio_prompt=audio_prompt if enable_audio else "",
                MMAudio_neg_prompt=audio_neg_prompt if enable_audio else "",
                RIFLEx_setting=0,
                NAG_scale=1.0,
                NAG_tau=3.5,
                NAG_alpha=0.5,
                slg_switch=0,
                slg_layers=[9],
                slg_start_perc=10,
                slg_end_perc=90,
                apg_switch=0,
                cfg_star_switch=0,
                cfg_zero_step=-1,
                prompt_enhancer="",
                min_frames_if_references=1,
                override_profile=-1,
                pace=0.5,
                exaggeration=0.5,
                temperature=0.8,
                top_k=50,
                output_filename="",
                mode="",
                api_name="/save_inputs_28",
            )

            progress.progress(90, text="Processing output...")
            time.sleep(0.5)
            progress.progress(100, text="Done!")

            # result is typically a filepath or dict
            video_path = None
            if isinstance(result, str) and os.path.exists(result):
                video_path = result
            elif isinstance(result, (list, tuple)):
                for item in result:
                    if isinstance(item, str) and os.path.exists(item):
                        video_path = item
                        break
                    if isinstance(item, dict):
                        for v in item.values():
                            if isinstance(v, str) and os.path.exists(v):
                                video_path = v
                                break

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown('<div class="card-label">🎬 Generated Video</div>', unsafe_allow_html=True)

            if video_path:
                with open(video_path, "rb") as f:
                    video_bytes = f.read()
                st.video(video_bytes)
                st.download_button(
                    label="⬇ DOWNLOAD VIDEO",
                    data=video_bytes,
                    file_name="velo2_output.mp4",
                    mime="video/mp4",
                )
            else:
                st.success("Generation complete! Check your Pinokio/LTX-Video output folder.")
                st.code(str(result))

        except Exception as e:
            progress.empty()
            st.error(f"Connection error: {e}")
            st.info(
                "Make sure LTX-Video is running in Pinokio and your Gradio share link is active. "
                "Update the GRADIO_URL in your Streamlit secrets."
            )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 3rem 0 1rem; color: #2a2a2a; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase;">
    Velo 2.0 &nbsp;·&nbsp; Local LTX-Video &nbsp;·&nbsp; MMAudio
</div>
""", unsafe_allow_html=True)
