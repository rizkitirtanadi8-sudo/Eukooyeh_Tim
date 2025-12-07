"use client";

import { Sparkles, ShoppingCart, TrendingUp, Zap, Target, BarChart3, CheckCircle } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            🤖 AI Product Listing SaaS
          </h1>
          
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Otomatisasi listing produk marketplace Anda dengan kekuatan AI. 
            Analisis gambar, generate deskripsi, dan prediksi harga dalam hitungan detik.
          </p>
          
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/dashboard"
              className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold text-lg shadow-lg hover:shadow-xl flex items-center gap-2"
            >
              <Sparkles className="w-5 h-5" />
              Mulai Sekarang
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              AI Product Analysis
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Upload gambar produk dan biarkan AI menganalisis kategori, spesifikasi, dan membuat deskripsi menarik secara otomatis.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-4">
              <Target className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Smart Price Prediction
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Dapatkan rekomendasi harga kompetitif berdasarkan data pasar real-time dari Google Search API.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Market Trends
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Pantau tren produk terpopuler per kategori dan prediksi micro-trends dengan AI untuk maksimalkan penjualan.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="max-w-4xl mx-auto mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
            Cara Kerja
          </h2>
          <div className="space-y-6">
            <div className="flex gap-4 items-start">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  Upload Gambar Produk
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Upload foto produk Anda dari galeri atau ambil foto langsung.
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  AI Analisis Otomatis
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  AI kami akan menganalisis gambar, mendeteksi kategori, dan membuat deskripsi produk yang menarik.
                </p>
              </div>
            </div>

            <div className="flex gap-4 items-start">
              <div className="flex-shrink-0 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                  Publish ke Marketplace
                </h3>
                <p className="text-gray-600 dark:text-gray-300">
                  Publish produk Anda ke Shopee, TikTok Shop, atau Tokopedia dengan satu klik.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Siap Meningkatkan Penjualan Anda?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Bergabung sekarang dan otomatisasi listing produk Anda dengan AI
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-gray-100 transition-colors font-semibold text-lg shadow-lg"
          >
            <Sparkles className="w-5 h-5" />
            Mulai Sekarang
          </Link>
        </div>
      </div>
    </main>
  );
}
