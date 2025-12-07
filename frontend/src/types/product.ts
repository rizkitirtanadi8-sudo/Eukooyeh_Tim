/**
 * TypeScript types untuk Product domain.
 * Sync dengan backend schemas.
 */

export enum ProductCategory {
  ELECTRONICS = "electronics",
  FASHION = "fashion",
  FOOD_BEVERAGE = "food_beverage",
  BEAUTY = "beauty",
  HOME_LIVING = "home_living",
  SPORTS = "sports",
  AUTOMOTIVE = "automotive",
  BOOKS = "books",
  TOYS = "toys",
  OTHER = "other",
}

export enum MarketplacePlatform {
  SHOPEE = "shopee",
  TOKOPEDIA = "tokopedia",
  TIKTOK_SHOP = "tiktok_shop",
}

export interface PriceSuggestion {
  min_price: number;
  max_price: number;
  recommended_price: number;
  confidence: number;
  reasoning: string;
}

export interface ProductAnalysisResponse {
  category: ProductCategory;
  title: string;
  description: string;
  original_user_input?: string;
  price_suggestion: PriceSuggestion;
  hashtags: string[];
  key_features: string[];
  confidence_score: number;
}

export interface ProductAnalysisRequest {
  image: File;
  user_description?: string;
  user_specifications?: Record<string, string>;
  target_platforms?: MarketplacePlatform[];
}

export interface MarketplacePublishRequest {
  product_id: string;
  platform: MarketplacePlatform;
  title: string;
  description: string;
  price: number;
  stock: number;
  images: string[];
}

export interface MarketplacePublishResponse {
  success: boolean;
  platform: MarketplacePlatform;
  product_url?: string;
  marketplace_product_id?: string;
  message: string;
}
