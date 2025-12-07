"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiService, Product, Shop } from "@/services/api";
import { ArrowLeft, Sparkles, ShoppingCart, Trash2 } from "lucide-react";
import Link from "next/link";

export default function ProductDetailPage({ params }: { params: { id: string } }) {
  const productId = params.id;
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [product, setProduct] = useState<Product | null>(null);
  const [shops, setShops] = useState<Shop[]>([]);
  const [enriching, setEnriching] = useState(false);
  const [selectedShop, setSelectedShop] = useState("shopify-demo-1");
  const [selectedPlatform, setSelectedPlatform] = useState<"shopee" | "tiktok_shop" | "shopify">("shopify");

  // Hardcoded Shopify shop for Hackathon Demo
  const mockShops: Shop[] = [
    {
      id: 'shopify-demo-1',
      shop_name: 'My Shopify Store (Live)',
      shop_id: 'shopify-demo-1',
      platform: 'shopify',
      shop_status: 'active',
      connected_at: new Date().toISOString()
    }
  ];

  useEffect(() => {
    loadData();
  }, [productId]);

  const loadData = async () => {
    try {
      const [productData, shopsData] = await Promise.all([
        apiService.getProduct(productId).catch(() => null),
        apiService.getShops().catch(() => []),
      ]);
      setProduct(productData);
      // Merge API shops with hardcoded Shopify shop
      setShops([...mockShops, ...shopsData]);
    } catch (error) {
      setProduct(null);
      setShops(mockShops); // Always show Shopify shop
    } finally {
      setLoading(false);
    }
  };

  const handleEnrich = async () => {
    if (!selectedShop) {
      alert("Please select a shop first");
      return;
    }

    setEnriching(true);
    try {
      // If Shopify, publish directly
      if (selectedPlatform === 'shopify') {
        const result = await apiService.publishToShopify({
          name: product?.name || '',
          description: product?.description || '',
          price: product?.price || 0,
          stock: product?.stock_quantity || 100,
          images: product?.images || [],
          sku: product?.sku
        });
        
        if (result.success) {
          const publishData = {
            platform: 'shopify',
            product_name: product?.name,
            price: product?.price,
            status: "published",
            product_id: result.product_id,
            product_url: result.product_url
          };
          
          router.push(`/dashboard/products/publish-success?data=${encodeURIComponent(JSON.stringify(publishData))}`);
        } else {
          throw new Error(result.message || 'Failed to publish to Shopify');
        }
      } else {
        // Original enrichment flow for Shopee/TikTok
        const result = await apiService.enrichProduct({
          product_id: productId,
          platform: selectedPlatform,
          shop_integration_id: selectedShop,
        });
        
        const publishData = {
          platform: selectedPlatform,
          product_name: product?.name,
          price: product?.price,
          status: "under_review",
          product_id: result.product_id || productId,
        };
        
        router.push(`/dashboard/products/publish-success?data=${encodeURIComponent(JSON.stringify(publishData))}`);
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || error.message || "Publishing failed");
      setEnriching(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Delete this product?")) return;

    try {
      await apiService.deleteProduct(productId);
      router.push("/dashboard");
    } catch (error) {
      alert("Failed to delete product");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!product) {
    return <div>Product not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-3 sm:px-6 lg:px-8 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-4 min-w-0 flex-1">
              <Link href="/dashboard" className="p-1.5 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg flex-shrink-0">
                <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
              </Link>
              <div className="min-w-0 flex-1">
                <h1 className="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white truncate">{product.name}</h1>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 hidden sm:block">Product Details</p>
              </div>
            </div>
            <button
              onClick={handleDelete}
              className="p-1.5 sm:p-2 text-red-600 hover:bg-red-50 rounded-lg flex-shrink-0"
            >
              <Trash2 className="w-4 h-4 sm:w-5 sm:h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Product Info */}
          <div className="lg:col-span-2 space-y-4 sm:space-y-6">
            <div className="bg-white rounded-lg border p-4 sm:p-6">
              <h2 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4">Product Information</h2>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm text-gray-600 dark:text-gray-400">Name</dt>
                  <dd className="text-base font-medium">{product.name}</dd>
                </div>
                <div>
                  <dt className="text-sm text-gray-600 dark:text-gray-400">Description</dt>
                  <dd className="text-base">{product.description || "-"}</dd>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm text-gray-600 dark:text-gray-400">Price</dt>
                    <dd className="text-base font-medium">Rp {product.price.toLocaleString()}</dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-600 dark:text-gray-400">Stock</dt>
                    <dd className="text-base font-medium">{product.stock_quantity}</dd>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <dt className="text-sm text-gray-600 dark:text-gray-400">Weight</dt>
                    <dd className="text-base">{product.weight_kg} kg</dd>
                  </div>
                  <div>
                    <dt className="text-sm text-gray-600 dark:text-gray-400">Condition</dt>
                    <dd className="text-base capitalize">{product.condition}</dd>
                  </div>
                </div>
                <div>
                  <dt className="text-sm text-gray-600 dark:text-gray-400">Status</dt>
                  <dd className="text-base">
                    <span className={`inline-flex px-2 py-1 rounded text-sm font-medium ${
                      product.status === "published" ? "bg-green-100 text-green-800" :
                      product.status === "ready" ? "bg-blue-100 text-blue-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {product.status}
                    </span>
                  </dd>
                </div>
              </dl>
            </div>

            {/* Product Specifications */}
            {product.specifications && Object.keys(product.specifications).length > 0 && (
              <div className="bg-white rounded-lg border p-4 sm:p-6">
                <h2 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4">Product Specifications</h2>
                <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {Object.entries(product.specifications).map(([key, value]) => (
                    <div key={key} className="border-b pb-2">
                      <dt className="text-sm text-gray-600 dark:text-gray-400">{key}</dt>
                      <dd className="text-base font-medium">{value as string}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}

            {/* Product Images */}
            {product.images && product.images.length > 0 && (
              <div className="bg-white rounded-lg border p-4 sm:p-6">
                <h2 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4">Product Images</h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {product.images.map((img, idx) => (
                    <img
                      key={idx}
                      src={img}
                      alt={`${product.name} ${idx + 1}`}
                      className="w-full h-32 object-cover rounded-lg border"
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="space-y-4 sm:space-y-6">
            {/* AI Enrichment */}
            <div className="bg-white rounded-lg border p-4 sm:p-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-600" />
                AI Enrichment
              </h3>

              {product.ai_enriched ? (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-800">✓ Product enriched with AI</p>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Platform</label>
                    <select
                      value={selectedPlatform}
                      onChange={(e) => setSelectedPlatform(e.target.value as any)}
                      className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:text-gray-100"
                    >
                      <option value="shopify">Shopify (Direct API)</option>
                      <option value="shopee">Shopee</option>
                      <option value="tiktok_shop">TikTok Shop</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Shop</label>
                    <select
                      value={selectedShop}
                      onChange={(e) => setSelectedShop(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg dark:bg-gray-800 dark:text-gray-100"
                    >
                      <option value="">Select shop...</option>
                      {shops
                        .filter((s) => s.platform === selectedPlatform)
                        .map((shop) => (
                          <option key={shop.id} value={shop.id}>
                            {shop.shop_name || shop.shop_id}
                          </option>
                        ))}
                    </select>
                  </div>

                  <button
                    onClick={handleEnrich}
                    disabled={enriching || !selectedShop}
                    className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                  >
                    {enriching ? (selectedPlatform === 'shopify' ? "Publishing to Shopify..." : "Enriching...") : (selectedPlatform === 'shopify' ? "Publish to Shopify" : "Enrich with AI")}
                  </button>

                  {shops.length === 0 && (
                    <p className="text-xs text-gray-500">
                      <Link href="/dashboard/shops" className="text-blue-600 hover:underline">
                        Connect a shop
                      </Link>{" "}
                      first to enrich products
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg border p-4 sm:p-6">
              <h3 className="font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <Link
                  href={`/dashboard/products/${productId}/edit`}
                  className="block w-full px-4 py-2 text-center border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-900"
                >
                  Edit Product
                </Link>
                {product.status === "ready" && (
                  <Link
                    href={`/dashboard/products/${productId}/publish`}
                    className="block w-full px-4 py-2 text-center bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    <ShoppingCart className="w-4 h-4 inline mr-2" />
                    Publish to Marketplace
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
