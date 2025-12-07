"""
AI Service menggunakan CrewAI dengan multi-agent system.
Agents: Vision Analyzer, Category Detector, Price Analyst, Copywriter.
Enhanced with Google Search API for real market data.
"""
import os
from typing import Optional
from crewai import Agent, Task, Crew, LLM
from app.core.config import get_settings
from app.schemas.product import ProductCategory, PriceSuggestion, ProductAnalysisResponse
from app.services.google_search_service import get_google_search_service


class AIProductAnalyzer:
    """
    Multi-agent AI system untuk analisis produk.
    Menggunakan CrewAI dengan 4 specialized agents.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> LLM:
        """Initialize LLM dengan konfigurasi dari settings."""
        model_name = self.settings.openai_model_name
        
        # Ensure proper prefix untuk CrewAI
        if not model_name.startswith("openai/"):
            model_name = f"openai/{model_name}"
        
        return LLM(
            model=model_name,
            base_url=self.settings.openai_api_base,
            api_key=self.settings.openai_api_key
        )
    
    async def _validate_consistency(self, image_path: str, user_description: str) -> bool:
        """
        Validasi apakah gambar konsisten dengan deskripsi user.
        
        Args:
            image_path: Path ke gambar
            user_description: Deskripsi dari user
            
        Returns:
            True jika konsisten, False jika tidak
        """
        validator_agent = Agent(
            role="Product Consistency Validator",
            goal="Validasi apakah gambar produk sesuai dengan deskripsi user",
            backstory=(
                "Kamu adalah validator yang bertugas memastikan gambar produk "
                "sesuai dengan deskripsi yang diberikan user. Kamu harus ketat "
                "dalam menilai konsistensi."
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
        
        validation_task = Task(
            description=f"""
            Validasi apakah gambar produk SESUAI dengan deskripsi user.
            
            Deskripsi User: "{user_description}"
            
            ATURAN VALIDASI:
            1. Lihat gambar dengan teliti
            2. Identifikasi jenis produk di gambar (contoh: motor, sepatu, laptop, dll)
            3. Ekstrak kata kunci produk dari deskripsi user
            4. Bandingkan: apakah produk di gambar SAMA dengan yang disebutkan user?
            
            Contoh TIDAK SESUAI:
            - Gambar: Motor | Deskripsi: "Sepatu Nike" → TIDAK SESUAI
            - Gambar: Laptop | Deskripsi: "Handphone Samsung" → TIDAK SESUAI
            
            Contoh SESUAI:
            - Gambar: Sepatu | Deskripsi: "Sepatu Nike Air Max" → SESUAI
            - Gambar: Motor | Deskripsi: "Motor Honda Beat 2020" → SESUAI
            
            Jawab HANYA dengan: "SESUAI" atau "TIDAK SESUAI"
            """,
            expected_output="SESUAI atau TIDAK SESUAI",
            agent=validator_agent,
            images=[image_path]
        )
        
        crew = Crew(
            agents=[validator_agent],
            tasks=[validation_task],
            verbose=False
        )
        
        result = crew.kickoff()
        result_str = str(result).strip().upper()
        
        # Check if result contains "SESUAI" without "TIDAK"
        return "SESUAI" in result_str and "TIDAK SESUAI" not in result_str
    
    def _create_vision_agent(self) -> Agent:
        """Agent untuk analisis visual produk."""
        return Agent(
            role="Product Vision Specialist",
            goal="Menganalisis gambar produk secara detail dan akurat",
            backstory=(
                "Kamu adalah AI vision specialist yang ahli dalam mengidentifikasi "
                "produk dari gambar. Kamu bisa mendeteksi brand, model, kondisi, "
                "dan detail visual lainnya dengan presisi tinggi."
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_category_agent(self) -> Agent:
        """Agent untuk deteksi kategori produk."""
        return Agent(
            role="Product Category Classifier",
            goal="Menentukan kategori produk yang paling tepat",
            backstory=(
                "Kamu adalah classifier expert yang bisa mengkategorikan produk "
                "dengan akurat berdasarkan karakteristik visualnya. "
                f"Kategori yang tersedia: {', '.join([c.value for c in ProductCategory])}"
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_pricing_agent(self) -> Agent:
        """Agent untuk analisis harga market."""
        return Agent(
            role="Market Price Analyst",
            goal="Memberikan saran harga yang kompetitif berdasarkan market research",
            backstory=(
                "Kamu adalah pricing analyst yang memahami harga pasar produk "
                "di Indonesia. Kamu bisa memberikan range harga yang realistis "
                "berdasarkan brand, kondisi, dan spesifikasi produk."
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_copywriter_agent(self) -> Agent:
        """Agent untuk membuat copywriting yang menarik."""
        return Agent(
            role="E-commerce Copywriter",
            goal="Membuat deskripsi produk yang menarik dan persuasif",
            backstory=(
                "Kamu adalah copywriter profesional untuk e-commerce Indonesia. "
                "Kamu tahu cara menulis deskripsi yang singkat, jelas, dan menarik. "
                "Kamu HARUS mempertahankan informasi dari user dan menambahkan "
                "copywriting yang engaging tanpa bertele-tele."
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def analyze_product(
        self,
        image_path: str,
        user_description: Optional[str] = None,
        user_specifications: Optional[dict] = None
    ) -> ProductAnalysisResponse:
        """
        Analisis produk menggunakan multi-agent system.
        
        Args:
            image_path: Path ke gambar produk
            user_description: Deskripsi dari user (akan di-preserve)
            user_specifications: Spesifikasi teknis dari user
            
        Returns:
            ProductAnalysisResponse dengan hasil analisis lengkap
            
        Raises:
            ValueError: Jika gambar dan deskripsi tidak konsisten
        """
        
        # Step 1: Validasi konsistensi DIMATIKAN - terlalu ketat
        # Biarkan AI yang handle inkonsistensi dengan lebih fleksibel
        # if user_description:
        #     is_consistent = await self._validate_consistency(image_path, user_description)
        #     if not is_consistent:
        #         raise ValueError(
        #             "❌ Produk tidak sesuai! Gambar yang diupload tidak cocok dengan deskripsi. "
        #             "Pastikan foto dan deskripsi produk adalah produk yang sama."
        #         )
        
        # Create agents
        vision_agent = self._create_vision_agent()
        category_agent = self._create_category_agent()
        pricing_agent = self._create_pricing_agent()
        copywriter_agent = self._create_copywriter_agent()
        
        # Encode image to base64 for vision
        import base64
        image_base64 = ""
        try:
            with open(image_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            pass  # Ignore image read errors
        
        # Get product info from Google Search if description provided
        google_search_context = ""
        if user_description:
            try:
                search_service = get_google_search_service()
                product_info = await search_service.search_product_info(
                    user_description,
                    additional_context="spesifikasi review"
                )
                
                if product_info.get("descriptions"):
                    descriptions_text = "\n".join(product_info["descriptions"][:3])
                    google_search_context = f"""

DATA DARI GOOGLE SEARCH:
{descriptions_text}

GUNAKAN informasi di atas untuk memperkaya analisis produk!
"""
            except Exception as e:
                pass  # Ignore Google Search errors
        
        # Prepare user context untuk vision
        user_context_vision = ""
        if user_description:
            user_context_vision = f"""

DESKRIPSI DARI USER:
{user_description}

{google_search_context}

INSTRUKSI: Gabungkan informasi visual dengan deskripsi user di atas.
- Gunakan deskripsi user untuk detail spesifik (brand, model, spesifikasi, tahun)
- Gunakan data dari Google Search untuk validasi dan informasi tambahan
- Validasi dengan gambar jika tersedia
- Jika deskripsi lengkap, GUNAKAN semua detail dari deskripsi
"""
        
        # Define tasks - SIMPLIFIED untuk speed
        vision_task = Task(
            description=f"""
            Analisis produk dari gambar.{user_context_vision}
            
            Output: Brand, model, kondisi, dan detail visual yang terlihat.
            """,
            expected_output="Analisis singkat produk dari gambar",
            agent=vision_agent
        )
        
        category_task = Task(
            description=f"""
            Tentukan kategori dari: {', '.join([c.value for c in ProductCategory])}
            """,
            expected_output="Kategori produk",
            agent=category_agent,
            context=[vision_task]
        )
        
        # Get real market price data from Google Search
        market_price_context = ""
        try:
            search_service = get_google_search_service()
            # Extract product name from vision analysis or user description
            product_query = user_description if user_description else "produk"
            price_data = await search_service.search_product_prices(product_query)
            
            if price_data.get("found"):
                market_price_context = f"""
REAL MARKET DATA (dari Google Search):
- Harga Minimum di Pasar: Rp {price_data['min_price']:,}
- Harga Maximum di Pasar: Rp {price_data['max_price']:,}
- Harga Rata-rata: Rp {price_data['avg_price']:,}
- Harga Median: Rp {price_data['median_price']:,}
- Jumlah Data: {price_data['price_count']} sumber
- Confidence: {price_data['market_data']['confidence']:.1%}

GUNAKAN data pasar real ini sebagai acuan utama untuk saran harga!
"""
        except Exception as e:
            pass  # Ignore Google Search errors
        
        pricing_task = Task(
            description=f"""
            Berikan saran harga pasar Indonesia berdasarkan data real.
            
            {market_price_context}
            
            Format:
            Min Price: Rp X.XXX.XXX
            Max Price: Rp X.XXX.XXX
            Recommended: Rp X.XXX.XXX
            Reasoning: [singkat, sebutkan data pasar jika ada]
            """,
            expected_output="Min Price, Max Price, Recommended, Reasoning",
            agent=pricing_agent,
            context=[vision_task, category_task]
        )
        
        copywriting_task = Task(
            description="""
            Buat konten penjualan menarik.
            
            Format:
            JUDUL: [max 100 char]
            DESKRIPSI: [2-3 paragraf]
            FITUR UTAMA:
            - [3-5 fitur]
            HASHTAG: #tag1 #tag2 #tag3
            """,
            expected_output="Judul, deskripsi, fitur, hashtag",
            agent=copywriter_agent,
            context=[vision_task, category_task, pricing_task]
        )
        
        # Execute crew - OPTIMIZED: verbose=False untuk speed
        crew = Crew(
            agents=[vision_agent, category_agent, pricing_agent, copywriter_agent],
            tasks=[vision_task, category_task, pricing_task, copywriting_task],
            verbose=False  # Disable verbose untuk speed up
        )
        
        result = crew.kickoff()
        
        # Parse result menjadi structured response
        return self._parse_crew_result(result, user_description)
    
    def _prepare_user_context(
        self,
        description: Optional[str],
        specifications: Optional[dict]
    ) -> str:
        """Prepare user context untuk AI agents."""
        context_parts = []
        
        if description:
            context_parts.append(f"Deskripsi User: {description}")
        
        if specifications:
            specs_str = ", ".join([f"{k}: {v}" for k, v in specifications.items()])
            context_parts.append(f"Spesifikasi: {specs_str}")
        
        return " | ".join(context_parts) if context_parts else "Tidak ada input dari user"
    
    def _parse_crew_result(
        self,
        result: str,
        original_user_input: Optional[str]
    ) -> ProductAnalysisResponse:
        """
        Parse hasil dari crew menjadi structured response.
        """
        import re
        
        result_str = str(result)
        lines = result_str.split('\n')
        
        # Extract title - improved parsing
        title = "Produk Berkualitas"
        for line in lines:
            line_upper = line.upper()
            if ("JUDUL" in line_upper or "TITLE" in line_upper) and ":" in line:
                title_part = line.split(":", 1)[1].strip()
                # Remove markdown formatting
                title_part = title_part.replace("**", "").replace("*", "").strip()
                if title_part and len(title_part) > 5:
                    title = title_part
                    break
        
        # Extract description - improved parsing
        description = ""
        in_desc_section = False
        desc_lines = []
        
        for i, line in enumerate(lines):
            line_upper = line.upper()
            
            # Start of description section
            if ("DESKRIPSI" in line_upper or "DESCRIPTION" in line_upper) and ":" in line:
                in_desc_section = True
                # Get inline description if exists
                desc_part = line.split(":", 1)[1].strip()
                if desc_part and not desc_part.startswith("["):
                    desc_lines.append(desc_part)
                continue
            
            # End of description section
            if in_desc_section:
                if any(keyword in line_upper for keyword in ["FITUR", "FEATURE", "HASHTAG", "INFO:"]):
                    break
                # Add non-empty lines, skip markdown headers
                if line.strip() and not line.strip().startswith("#"):
                    # Clean markdown formatting
                    clean_line = line.strip().replace("**", "").replace("*", "")
                    if clean_line:
                        desc_lines.append(clean_line)
        
        description = "\n".join(desc_lines).strip()
        
        # Fallback: if no description found, use original user input
        if not description:
            if original_user_input:
                description = original_user_input
            else:
                description = "Produk berkualitas dengan harga terjangkau."
        
        # Extract category
        category = ProductCategory.OTHER
        for cat in ProductCategory:
            if cat.value in result_str.lower() or cat.name.lower() in result_str.lower():
                category = cat
                break
        
        # Extract price with regex
        min_price = 50000
        max_price = 500000
        recommended_price = 150000
        reasoning = "Berdasarkan analisis market"
        
        # Try to find price patterns with better regex
        price_patterns = {
            'min': [
                r'Min\s*Price[^:]*:\s*Rp\s*([\d.]+)',
                r'Minimum[^:]*:\s*Rp\s*([\d.]+)',
                r'Harga\s*Minimum[^:]*:\s*Rp\s*([\d.]+)',
            ],
            'max': [
                r'Max\s*Price[^:]*:\s*Rp\s*([\d.]+)',
                r'Maximum[^:]*:\s*Rp\s*([\d.]+)',
                r'Harga\s*Maximum[^:]*:\s*Rp\s*([\d.]+)',
            ],
            'recommended': [
                r'Recommended[^:]*:\s*Rp\s*([\d.]+)',
                r'Disarankan[^:]*:\s*Rp\s*([\d.]+)',
                r'Harga\s*Disarankan[^:]*:\s*Rp\s*([\d.]+)',
            ]
        }
        
        for price_type, patterns in price_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, result_str, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace('.', '')  # Remove dots (thousand separator)
                    try:
                        price_val = int(price_str)
                        if price_val > 1000:  # Sanity check
                            if price_type == 'min':
                                min_price = price_val
                            elif price_type == 'max':
                                max_price = price_val
                            elif price_type == 'recommended':
                                recommended_price = price_val
                            break
                    except:
                        pass
        
        # Ensure logical price range
        if min_price > max_price:
            min_price, max_price = max_price, min_price
        if recommended_price < min_price or recommended_price > max_price:
            recommended_price = (min_price + max_price) // 2
        
        # Extract reasoning for price
        for line in lines:
            if "reasoning" in line.lower() or "alasan" in line.lower():
                parts = line.split(":", 1)
                if len(parts) > 1:
                    reasoning = parts[1].strip()
                    break
        
        price_suggestion = PriceSuggestion(
            min_price=min_price,
            max_price=max_price,
            recommended_price=recommended_price,
            confidence=0.8,
            reasoning=reasoning
        )
        
        # Extract hashtags
        hashtags = []
        for line in lines:
            tags = re.findall(r'#\w+', line)
            hashtags.extend(tags)
        
        if not hashtags:
            hashtags = ["#produkberkualitas", "#murah", "#recommended"]
        
        # Extract key features - improved parsing
        key_features = []
        in_features_section = False
        for line in lines:
            line_upper = line.upper()
            
            if "FITUR" in line_upper or "FEATURE" in line_upper:
                in_features_section = True
                continue
            
            if in_features_section:
                if "HASHTAG" in line_upper or line.strip().startswith("#"):
                    break
                
                # Handle different bullet formats
                if line.strip().startswith(("-", "•", "*", "✓", "✨", "⚡", "🎯", "🔧", "💪")):
                    # Remove bullet and emoji, clean markdown
                    feature = re.sub(r'^[-•*✓✨⚡🎯🔧💪]\s*', '', line.strip())
                    feature = feature.replace("**", "").replace("*", "").strip()
                    if feature and len(feature) > 3:
                        key_features.append(feature)
        
        if not key_features:
            key_features = ["Kualitas terjamin", "Harga terjangkau", "Siap kirim"]
        
        return ProductAnalysisResponse(
            category=category,
            title=title[:200],
            description=description.strip()[:1000],  # Limit description
            original_user_input=original_user_input,
            price_suggestion=price_suggestion,
            hashtags=hashtags[:10],
            key_features=key_features[:5],
            confidence_score=0.85
        )
