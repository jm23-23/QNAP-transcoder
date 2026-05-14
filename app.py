import streamlit as st
import os
import subprocess
import re

# Konfiguracja ścieżek
INPUT_DIR = "/data/input"
OUTPUT_DIR = "/data/output"

st.set_page_config(page_title="QNAP File Explorer & Transcoder", page_icon="🎬", layout="wide")

# --- FUNKCJE POMOCNICZE ---

def format_size(size_bytes):
    """Formatuje bajty na czytelny rozmiar (MB/GB)."""
    if size_bytes == 0: return "0B"
    units = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {units[i]}"

def get_dir_content(target_path):
    """Pobiera zawartość folderu z filtrowaniem i informacją o rozmiarze."""
    try:
        entries = os.listdir(target_path)
    except Exception as e:
        st.error(f"Błąd dostępu: {e}")
        return [], []

    folders = []
    files = []
    
    # Wykluczone foldery i rozszerzenia
    excluded_names = ['@Recycle', '@__thumb', '@Recently-Snapshot', '.streams', '@recently-snapshot']
    valid_exts = ('.mp4', '.mkv', '.avi', '.mov', '.m4v', '.ts')

    for entry in sorted(entries):
        if entry in excluded_names:
            continue
            
        full_path = os.path.join(target_path, entry)
        
        if os.path.isdir(full_path):
            folders.append(entry)
        elif entry.lower().endswith(valid_exts):
            size = os.path.getsize(full_path)
            files.append({"name": entry, "size": format_size(size), "raw_size": size})
            
    return folders, files

# --- ZARZĄDZANIE STANEM NAWIGACJI ---

if 'current_path' not in st.session_state:
    st.session_state.current_path = INPUT_DIR

def go_to_folder(folder_name):
    st.session_state.current_path = os.path.join(st.session_state.current_path, folder_name)

def go_up():
    if st.session_state.current_path != INPUT_DIR:
        st.session_state.current_path = os.path.dirname(st.session_state.current_path)

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("🎬 QNAP Transcoder & File Browser")

# Okruszki chleba (Breadcrumbs)
display_path = os.path.relpath(st.session_state.current_path, INPUT_DIR)
st.write(f"**Lokalizacja:** `Root / {display_path.replace('.', '')}`")

col1, col2 = st.columns([1, 4])

with col1:
    if st.button("⬅️ W górę", use_container_width=True):
        go_up()
        st.rerun()

# Pobieranie zawartości
folders, files = get_dir_content(st.session_state.current_path)

# Wyświetlanie folderów jako przyciski
st.subheader("Foldery")
if not folders:
    st.info("Brak podfolderów.")
else:
    # Wyświetlamy foldery w formie siatki
    f_cols = st.columns(4)
    for idx, folder in enumerate(folders):
        if f_cols[idx % 4].button(f"📁 {folder}", key=f"dir_{idx}", use_container_width=True):
            go_to_folder(folder)
            st.rerun()

st.divider()

# Wyświetlanie plików
st.subheader("Pliki wideo")
if not files:
    st.warning("W tym folderze nie ma plików wideo.")
    selected_file = None
else:
    # Tworzymy listę do selectboxa z informacją o rozmiarze
    file_options = {f"{f['name']} ({f['size']})": f['name'] for f in files}
    selection_label = st.selectbox("Wybierz plik do kodowania:", options=list(file_options.keys()))
    selected_file = file_options[selection_label]

# --- SEKCJA KODOWANIA ---

if selected_file:
    input_path = os.path.join(st.session_state.current_path, selected_file)
    
    with st.expander("Ustawienia i start", expanded=True):
        st.write(f"Wybrano: **{selected_file}**")
        quality = st.slider("Jakość (Global Quality - niżej lepiej)", 15, 35, 25)
        
        if st.button("🚀 Uruchom kodowanie sprzętowe"):
            # Przygotowanie nazwy wyjściowej (z zachowaniem unikalności)
            clean_name = selected_file.rsplit('.', 1)[0]
            output_path = os.path.join(OUTPUT_DIR, f"{clean_name}_HEVC.mkv")
            
            # KROK 1: ffprobe
            with st.spinner("Analizowanie..."):
                probe_cmd = [
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-count_packets", "-show_entries", "stream=nb_read_packets",
                    "-of", "csv=p=0", input_path
                ]
                total_frames = int(subprocess.check_output(probe_cmd).decode().strip())

            # KROK 2: FFmpeg (VAAPI Intel)
            progress_bar = st.progress(0)
            status = st.empty()
            
            ffmpeg_cmd = [
                "ffmpeg", "-hwaccel", "vaapi", "-hwaccel_device", "/dev/dri/renderD128", "-hwaccel_output_format", "vaapi",
                "-i", input_path,
                "-map", "0:v:0",
                "-map", "0:a:m:language:pol?", "-map", "0:a:m:language:eng?",
                "-map", "0:s:m:language:pol?", "-map", "0:s:m:language:eng?",
                "-c:v", "hevc_vaapi", "-qp", str(quality),
                "-c:a", "copy", "-c:s", "copy",
                "-y", output_path
            ]

            process = subprocess.Popen(ffmpeg_cmd, stderr=subprocess.PIPE, text=True)

            for line in process.stderr:
                frame_match = re.search(r"frame=\s*(\d+)", line)
                fps_match = re.search(r"fps=\s*([\d.]+)", line)
                if frame_match:
                    curr_frame = int(frame_match.group(1))
                    prog = min(curr_frame / total_frames, 1.0)
                    progress_bar.progress(prog)
                    fps = fps_match.group(1) if fps_match else "0"
                    status.write(f"⏳ Kodowanie: {int(prog*100)}% | FPS: {fps} | Klatka: {curr_frame}/{total_frames}")

            process.wait()
            if process.returncode == 0:
                st.success(f"✅ Gotowe! Plik zapisany w folderze Output.")