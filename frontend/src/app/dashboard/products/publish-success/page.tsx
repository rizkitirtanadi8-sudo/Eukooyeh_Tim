"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { CheckCircle, Package, DollarSign, Tag, ArrowLeft, ExternalLink } from "lucide-react";
import Link from "next/link";

export default function PublishSuccessPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [publishData, setPublishData] = useState<any>(null);

  useEffect(() => {
    const data = searchParams.get("data");
    if (data) {
      try {
        setPublishData(JSON.parse(decodeURIComponent(data)));
      } catch (e) {
        router.push("/dashboard");
      }
    } else {
      router.push("/dashboard");
    }
  }, [searchParams, router]);

  if (!publishData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        {/* Success Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900 rounded-full mb-6">
            <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white dark:text-white mb-4">
            🎉 Produk Berhasil Dipublish!
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 dark:text-gray-300">
            Produk Anda telah berhasil dipublish ke {publishData.platform}
          </p>
        </div>

        {/* Summary Card */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white dark:text-white mb-6">
              Ringkasan Publikasi
            </h2>

            <div className="space-y-6">
              {/* Platform */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                  <Package className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white dark:text-white mb-1">
                    Platform
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 dark:text-gray-300 capitalize">
                    {publishData.platform}
                  </p>
                </div>
              </div>

              {/* Product Name */}
              {publishData.product_name && (
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                    <Tag className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white dark:text-white mb-1">
                      Nama Produk
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 dark:text-gray-300">
                      {publishData.product_name}
                    </p>
                  </div>
                </div>
              )}

              {/* Price */}
              {publishData.price && (
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                    <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 dark:text-white dark:text-white mb-1">
                      Harga
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400 dark:text-gray-300">
                      Rp {publishData.price.toLocaleString("id-ID")}
                    </p>
                  </div>
                </div>
              )}

              {/* Status */}
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-yellow-100 dark:bg-yellow-900 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white dark:text-white mb-1">
                    Status
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded-full text-sm font-medium">
                      {publishData.status || "Under Review"}
                    </span>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Produk sedang direview oleh marketplace
                    </p>
                  </div>
                </div>
              </div>

              {/* Product ID */}
              {publishData.product_id && (
                <div className="p-4 bg-gray-50 dark:bg-gray-900 dark:bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-400 dark:text-gray-300">
                    <span className="font-semibold">Product ID:</span>{" "}
                    <code className="bg-gray-200 dark:bg-gray-600 px-2 py-1 rounded">
                      {publishData.product_id}
                    </code>
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              <ArrowLeft className="w-5 h-5" />
              Kembali ke Dashboard
            </Link>
            <Link
              href="/dashboard/products/new"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white dark:text-white rounded-lg hover:bg-gray-50 dark:bg-gray-900 dark:hover:bg-gray-700 transition-colors font-semibold"
            >
              <Package className="w-5 h-5" />
              Publish Produk Lain
            </Link>
          </div>

          {/* Info Box */}
          <div className="mt-8 p-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <h3 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
              📝 Langkah Selanjutnya
            </h3>
            <ul className="space-y-2 text-sm text-blue-800 dark:text-blue-300">
              <li>• Produk Anda akan direview oleh tim marketplace dalam 1-2 hari kerja</li>
              <li>• Anda akan menerima notifikasi email setelah produk disetujui</li>
              <li>• Setelah disetujui, produk akan langsung tayang di marketplace</li>
              <li>• Pantau performa produk Anda di dashboard</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
