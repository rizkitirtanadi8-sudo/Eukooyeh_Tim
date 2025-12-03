import streamlit as st
import os
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI E-commerce Agent", page_icon="🤖", layout="wide")

if not os.getenv("OPENAI_API_BASE"):
    st.error("❌ FILE .ENV TIDAK TERBACA!")
    st.stop()

from services.ai_engine import run_crew_generation

if 'hasil_ai' not in st.session_state:
    st.session_state['hasil_ai'] = None

st.title("🤖 AI E-commerce Manager")
st.markdown("---")

col1, col2 = st.columns([1, 2])

# --- INPUT ---
with col1:
    st.subheader("1. Upload & Generate")
    with st.form("input_form"):
        uploaded_file = st.file_uploader("📸 Foto Produk", type=['jpg', 'png', 'jpeg'])
        user_notes = st.text_area("Catatan", placeholder="Cth: Dokumen penting, jangan sampai rusak")
        platforms = st.multiselect("Mau Jual Dimana?", ["Shopee", "Tokopedia", "TikTok"], default=["Shopee"])
        generate_btn = st.form_submit_button("🚀 Generate Konten")

    if generate_btn:
        if not uploaded_file:
            st.warning("Upload fotonya dulu dong bro!")
        else:
            with st.spinner('Mata AI sedang memindai gambar...'):
                try:
                    os.makedirs("uploads", exist_ok=True)
                    file_path = f"uploads/{uploaded_file.name}"
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    hasil_output = run_crew_generation(
                        product_image_path=file_path,
                        user_notes=user_notes
                    )

                    st.session_state['hasil_ai'] = str(hasil_output)
                    st.toast("Analisis selesai!", icon="✅")
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# --- OUTPUT DENGAN FILTER ---
with col2:
    st.subheader("2. Review & Publish")
    
    if st.session_state['hasil_ai']:
        raw_text = st.session_state['hasil_ai']
        
        # --- SATPAM FILTER: Cek apakah AI berhasil atau ngawur? ---
        # Kita cari kata kunci wajib. Kalau gak ada, berarti GAGAL.
        keywords_wajib = ["JUDUL", "DESKRIPSI", "HARGA"]
        is_valid = any(word in raw_text.upper() for word in keywords_wajib)
        
        # Tambahan: Cek kalau teksnya isinya pesan error/maaf
        is_error_text = "MAAF" in raw_text.upper() or "ERROR" in raw_text.upper() or "TIDAK DAPAT" in raw_text.upper()

        if not is_valid or is_error_text:
            # TAMPILAN KALAU GAGAL
            st.error("⛔ AI GAGAL MEMBUAT DRAF YANG BENAR")
            st.warning("Sepertinya gambar tidak jelas atau AI bingung. Silakan coba lagi dengan foto yang lebih jelas.")
            
            # Tampilkan pesan errornya apa biar user tau
            with st.expander("Lihat Pesan Error AI"):
                st.write(raw_text)
            
            if st.button("🔄 Coba Ulang (Reset)"):
                st.session_state['hasil_ai'] = None
                st.rerun()
                
        else:
            # TAMPILAN KALAU SUKSES (BARU BOLEH EDIT)
            
            # Auto-Extract Judul
            try:
                lines = raw_text.split('\n')
                judul_awal = "Judul Tidak Terdeteksi"
                deskripsi_awal = raw_text 
                for line in lines:
                    if len(line.strip()) > 5: 
                        judul_awal = line.replace("JUDUL PRODUK:", "").replace("**", "").replace("#", "").strip()
                        deskripsi_awal = raw_text.replace(line, "").strip()
                        break
            except:
                judul_awal = "Judul Manual"
                deskripsi_awal = raw_text
            
            with st.form("publish_form"):
                st.success("✅ Draf berhasil dibuat! Silakan review.")
                
                final_judul = st.text_input("Judul Produk", value=judul_awal)
                
                final_harga = st.number_input(
                    "Harga Jual (Rp)", 
                    min_value=0, 
                    step=1000, 
                    help="Wajib diisi minimal Rp 1.000"
                )
                
                final_deskripsi = st.text_area("Deskripsi Lengkap", value=deskripsi_awal, height=400)
                
                st.markdown("---")
                c1, c2 = st.columns(2)
                
                with c1:
                    if st.form_submit_button("❌ Reset Data"):
                        st.session_state['hasil_ai'] = None
                        st.rerun()
                
                with c2:
                    publish_btn = st.form_submit_button("💰 JUAL SEKARANG!")
            
            if publish_btn:
                # Validasi Akhir
                if final_harga < 1000:
                    st.error("⛔ GABISA JUAL GRATIS BOS! Rugi bandar nanti.")
                elif len(final_judul) < 5:
                    st.error("⛔ Judulnya kependekan bro!")
                else:
                    with st.status("Sedang menghubungkan ke API E-commerce...", expanded=True) as status:
                        st.write("🔄 Authenticating...")
                        time.sleep(1)
                        st.write(f"📤 Uploading: {final_judul}")
                        time.sleep(1)
                        st.write(f"💲 Setting Price: Rp {final_harga:,}")
                        time.sleep(1)
                        status.update(label="✅ SUKSES TERJUAL!", state="complete", expanded=False)
                    
                    st.success(f"Barang berhasil tayang di {', '.join(platforms)}!")
                    st.balloons()
    else:
        st.info("👈 Upload foto di kiri dulu ya.")