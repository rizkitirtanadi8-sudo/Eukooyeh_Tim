"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiService, Product, Shop } from "@/services/api";
import { ArrowLeft, ShoppingCart, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import Link from "next/link";

interface Listing {
  id: string;
  platform: string;
  platform_data: any;
  publish_status: string;
}

export default function PublishProductPage() {
  const params = useParams();
  const router = useRouter();
  const productId = params.id as string;

  const [loading, setLoading] = useState(false);
  const [product, setProduct] = useState<Product | null>(null);
  const [shops, setShops] = useState<Shop[]>([]);
  const [listings, setListings] = useState<Listing[]>([]);
  const [publishing, setPublishing] = useState<string | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, [productId]);

  const loadData = async () => {
    try {
      const [productData, shopsData, listingsData] = await Promise.all([
        apiService.getProduct(productId).catch(() => null),
        apiService.getShops().catch(() => []),
        apiService.getProductListings(productId).catch(() => ({ listings: [] })),
      ]);
      setProduct(productData);
      setShops(shopsData);
      setListings(listingsData.listings || []);
    } catch (error: any) {
      setProduct(null);
      setShops([]);
      setListings([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async (listingId: string, shopId: string) => {
    setPublishing(listingId);
    setError("");

    try {
      const result = await apiService.publishToMarketplace(listingId, shopId);
      alert(`✅ ${result.message}\n\nProduct URL: ${result.product_url || 'N/A'}`);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to publish");
    } finally {
      setPublishing(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!product) {
    return <div>Product not found</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <Link
              href={`/dashboard/products/${productId}`}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Publish to Marketplace
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">{product.name}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Check if product is ready */}
        {product.status !== "ready" && product.status !== "published" ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h3 className="font-semibold text-yellow-900 mb-2">
              Product not ready for publishing
            </h3>
            <p className="text-sm text-yellow-700 mb-4">
              Please enrich this product with AI first before publishing.
            </p>
            <Link
              href={`/dashboard/products/${productId}`}
              className="inline-flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            >
              Go back and enrich product
            </Link>
          </div>
        ) : listings.length === 0 ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <h3 className="font-semibold text-yellow-900 mb-2">
              No enriched listings found
            </h3>
            <p className="text-sm text-yellow-700 mb-4">
              Please enrich this product for at least one platform first.
            </p>
            <Link
              href={`/dashboard/products/${productId}`}
              className="inline-flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
            >
              Go back and enrich product
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-700">
                Select which marketplace to publish to. Make sure you have connected
                the corresponding shop.
              </p>
            </div>

            {/* Listings */}
            {listings.map((listing) => {
              const shop = shops.find((s) => s.platform === listing.platform);
              const isPublished = listing.publish_status === "published";
              const isPublishing = publishing === listing.id;

              return (
                <div
                  key={listing.id}
                  className="bg-white rounded-lg border border-gray-200 dark:border-gray-700 p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                        {listing.platform.replace("_", " ")}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Status:{" "}
                        <span
                          className={`font-medium ${
                            isPublished
                              ? "text-green-600"
                              : "text-yellow-600"
                          }`}
                        >
                          {listing.publish_status}
                        </span>
                      </p>
                    </div>
                    {isPublished && (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Published
                      </span>
                    )}
                  </div>

                  {/* Preview enriched data */}
                  <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Enriched Data Preview
                    </h4>
                    <dl className="space-y-2 text-sm">
                      <div>
                        <dt className="text-gray-600 dark:text-gray-400">Title:</dt>
                        <dd className="font-medium">
                          {listing.platform_data.title ||
                            listing.platform_data.item_name ||
                            product.name}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-gray-600 dark:text-gray-400">Category ID:</dt>
                        <dd className="font-medium">
                          {listing.platform_data.category_id || "N/A"}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-gray-600 dark:text-gray-400">Price:</dt>
                        <dd className="font-medium">
                          Rp {(listing.platform_data.price || product.price).toLocaleString()}
                        </dd>
                      </div>
                    </dl>
                  </div>

                  {/* Publish button */}
                  {!isPublished && shop ? (
                    <button
                      onClick={() => handlePublish(listing.id, shop.id)}
                      disabled={isPublishing}
                      className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold flex items-center justify-center gap-2"
                    >
                      {isPublishing ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Publishing...
                        </>
                      ) : (
                        <>
                          <ShoppingCart className="w-5 h-5" />
                          Publish to {shop.shop_name || shop.shop_id}
                        </>
                      )}
                    </button>
                  ) : !shop ? (
                    <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-sm text-yellow-700">
                        No shop connected for this platform.{" "}
                        <Link
                          href="/dashboard/shops"
                          className="font-semibold underline"
                        >
                          Connect a shop
                        </Link>
                      </p>
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
