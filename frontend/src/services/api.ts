/**
 * API service untuk komunikasi dengan backend.
 * Menggunakan axios dengan proper error handling & auth.
 */
import axios, { AxiosInstance, AxiosError } from "axios";
import {
  ProductAnalysisRequest,
  ProductAnalysisResponse,
  MarketplacePublishRequest,
  MarketplacePublishResponse,
} from "@/types/product";

// Product types
export interface Product {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  price: number;
  stock_quantity: number;
  images: string[];
  sku?: string;
  weight_kg?: number;
  condition: "new" | "used";
  ai_enriched: boolean;
  status: "draft" | "ready" | "published" | "archived";
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  description?: string;
  price: number;
  stock_quantity?: number;
  images?: string[];
  sku?: string;
  weight_kg?: number;
  condition?: "new" | "used";
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  stock_quantity?: number;
  images?: string[];
  sku?: string;
  weight_kg?: number;
  condition?: "new" | "used";
}

// Enrichment types
export interface EnrichRequest {
  product_id: string;
  platform: "shopee" | "tiktok_shop";
  shop_integration_id: string;
}

export interface EnrichResponse {
  listing_id: string;
  product_id: string;
  platform: string;
  platform_data: any;
  status: string;
  message: string;
}

// Shop types
export interface Shop {
  id: string;
  platform: "shopee" | "tiktok_shop";
  shop_id: string;
  shop_name?: string;
  shop_status: "active" | "expired" | "revoked";
  connected_at: string;
}

class APIService {
  private client: AxiosInstance;
  private publicClient: AxiosInstance;

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
    
    // All requests are now public - no auth required
    this.client = axios.create({
      baseURL,
      timeout: 180000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.publicClient = axios.create({
      baseURL,
      timeout: 180000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // No auth interceptors - all endpoints are public
  }

  // No auth methods needed - all public

  // ============================================
  // PRODUCT ENDPOINTS
  // ============================================

  async createProduct(data: ProductCreate): Promise<Product> {
    const response = await this.client.post<Product>("/products", data);
    return response.data;
  }

  async getProducts(params?: { status?: string; limit?: number; offset?: number }): Promise<Product[]> {
    const response = await this.client.get<Product[]>("/products", { params });
    return response.data;
  }

  async getProduct(id: string): Promise<Product> {
    const response = await this.client.get<Product>(`/products/${id}`);
    return response.data;
  }

  async updateProduct(id: string, data: ProductUpdate): Promise<Product> {
    const response = await this.client.patch<Product>(`/products/${id}`, data);
    return response.data;
  }

  async deleteProduct(id: string) {
    await this.client.delete(`/products/${id}`);
  }

  async getProductStats() {
    const response = await this.client.get("/products/stats/summary");
    return response.data;
  }

  // ============================================
  // ENRICHMENT ENDPOINTS
  // ============================================

  async enrichProduct(request: EnrichRequest): Promise<EnrichResponse> {
    const response = await this.client.post<EnrichResponse>("/enrichment/enrich", request);
    return response.data;
  }

  async getProductListings(productId: string) {
    const response = await this.client.get(`/enrichment/listings/${productId}`);
    return response.data;
  }

  async predictCategory(productName: string, platform: string) {
    const response = await this.client.post("/enrichment/predict-category", {
      product_name: productName,
      platform,
    });
    return response.data;
  }

  // ============================================
  // SHOP ENDPOINTS
  // ============================================

  async getShops(): Promise<Shop[]> {
    const response = await this.client.get<Shop[]>("/shops");
    return response.data;
  }

  async initShopifyOAuth() {
    const response = await this.client.get("/shops/connect/shopify");
    return response.data;
  }

  async disconnectShop(shopId: string) {
    await this.client.delete(`/shops/${shopId}`);
  }

  // ============================================
  // MARKETPLACE ENDPOINTS
  // ============================================

  async publishToMarketplace(listingId: string, shopIntegrationId: string) {
    const response = await this.client.post("/marketplaces/publish", {
      listing_id: listingId,
      shop_integration_id: shopIntegrationId,
    });
    return response.data;
  }

  async getPublishedListings(productId: string) {
    const response = await this.client.get(`/marketplaces/published/${productId}`);
    return response.data;
  }

  // ============================================
  // SHOPIFY DIRECT PUBLISHING
  // ============================================

  async publishToShopify(productData: {
    name: string;
    description: string;
    price: number;
    stock?: number;
    images?: string[];
    sku?: string;
  }) {
    const response = await this.client.post("/publish/shopify", productData);
    return response.data;
  }

  async getShopifyProduct(productId: string) {
    const response = await this.client.get(`/publish/shopify/product/${productId}`);
    return response.data;
  }

  async checkShopifyStatus() {
    const response = await this.client.get("/publish/shopify/status");
    return response.data;
  }

  async checkShopifyConnection() {
    const response = await this.client.get("/shops/shopify/status");
    return response.data;
  }

  // ============================================
  // TREND ANALYSIS ENDPOINTS
  // ============================================

  async analyzeTrends(category: string, region: string = "Indonesia") {
    const response = await this.client.post("/analyze/trends", {
      category,
      region,
    });
    return response.data;
  }

  // ============================================
  // SETTINGS ENDPOINTS
  // ============================================

  async getSettings() {
    const response = await this.client.get("/settings");
    return response.data;
  }

  async getUserSettings() {
    const response = await this.client.get("/settings");
    return response.data;
  }

  async updateSettings(data: any) {
    const response = await this.client.patch("/settings", data);
    return response.data;
  }

  async updateUserSettings(data: any) {
    const response = await this.client.patch("/settings", data);
    return response.data;
  }

  // ============================================
  // LEGACY ENDPOINTS (Keep for compatibility)
  // ============================================

  /**
   * Analisis produk dari gambar.
   */
  async analyzeProduct(
    request: ProductAnalysisRequest
  ): Promise<ProductAnalysisResponse> {
    const formData = new FormData();
    formData.append("image", request.image);

    if (request.user_description) {
      formData.append("user_description", request.user_description);
    }

    if (request.user_specifications) {
      formData.append(
        "user_specifications",
        JSON.stringify(request.user_specifications)
      );
    }

    const response = await this.publicClient.post<ProductAnalysisResponse>(
      "/products/analyze",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  }

  /**
   * Get supported marketplace platforms.
   */
  async getSupportedPlatforms() {
    const response = await this.client.get("/marketplaces/platforms");
    return response.data;
  }

  /**
   * Health check.
   */
  async healthCheck() {
    const response = await this.client.get("/products/health");
    return response.data;
  }
}

// Export singleton instance
export const apiService = new APIService();
