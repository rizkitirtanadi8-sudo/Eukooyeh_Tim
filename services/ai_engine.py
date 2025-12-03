import os
from crewai import Agent, Task, Crew, LLM
from dotenv import load_dotenv

# 1. LOAD ENV
load_dotenv()

def run_crew_generation(product_image_path: str = None, user_notes: str = ""):
    
    # --- DEBUGGING DI TERMINAL ---
    print(f"🔥 Menerima Gambar: {product_image_path}")
    print(f"🔥 Catatan User: {user_notes}")
    
    # 2. SETUP OTAK AI (Pake Konfigurasi Kolosal dari .env)
    model_name = os.getenv("OPENAI_MODEL_NAME")
    
    # Pastikan prefix 'openai/' ada biar CrewAI tau protokolnya
    if not model_name.startswith("openai/"):
        model_name = f"openai/{model_name}"

    my_llm = LLM(
        model=model_name, 
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 3. DEFINISI AGENT (KARYAWAN)
    
    # Agent 1: Si Mata (Vision Specialist)
    vision_agent = Agent(
        role='Product Vision Specialist',
        goal='Mendeskripsikan detail visual produk dari gambar secara akurat',
        backstory='Kamu adalah mata AI canggih yang bisa membaca teks dalam dokumen atau melihat detail barang.',
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    # Agent 2: Si Penulis (Copywriter)
    copywriter_agent = Agent(
        role='Senior Copywriter',
        goal='Membuat konten penjualan yang sesuai fakta visual',
        backstory='Copywriter profesional yang anti-halusinasi.',
        verbose=True,
        allow_delegation=False,
        llm=my_llm
    )

    # 4. DEFINISI TUGAS (TASK) - BAGIAN PALING PENTING!
    
    # Kita buat list gambar (karena parameter images butuh list)
    image_list = [product_image_path] if product_image_path else []

    task_analyze = Task(
        description=f"""
        Tugasmu adalah MELIHAT gambar yang dilampirkan dan membaca catatan user: "{user_notes}".
        
        Langkah kerja:
        1. Identifikasi objek apa yang ada di gambar (Apakah dokumen? Kendaraan? Elektronik?).
        2. Jika itu Dokumen/Kertas, sebutkan jenis dokumennya dan teks apa yang terbaca.
        3. Jika itu Barang Fisik, sebutkan warna, kondisi, dan bahannya.
        4. Pastikan deskripsimu COCOK dengan gambar aslinya. Jangan mengarang!
        """,
        expected_output="Laporan analisis visual yang jujur dan detail.",
        agent=vision_agent,
        # --- FITUR VISION DIAKTIFKAN DISINI ---
        images=image_list 
        # --------------------------------------
    )

    task_write = Task(
        description="""
        Berdasarkan laporan visual dari Agent Vision tadi, buatkan draf penjualan.
        
        Aturan:
        - Jika barangnya dokumen/jasa, buat deskripsi jasa yang profesional.
        - Jika barangnya fisik, buat deskripsi produk yang menarik.
        
        Output Wajib:
        1. JUDUL PRODUK (Baris pertama)
        2. DESKRIPSI (Paragraf lengkap)
        3. HASHTAG
        4. SARAN HARGA (Format: Rp XXX.XXX)
        """,
        expected_output="Konten marketing siap jual.",
        agent=copywriter_agent
    )

    # 5. EKSEKUSI TIM
    crew = Crew(
        agents=[vision_agent, copywriter_agent],
        tasks=[task_analyze, task_write],
        verbose=True
    )

    return crew.kickoff()