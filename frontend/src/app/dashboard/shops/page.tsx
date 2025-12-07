"use client";

import { useEffect, useState } from "react";
import { apiService, Shop } from "@/services/api";
import { ArrowLeft, Store, Plus, ExternalLink, Loader2, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function ShopsPage() {
  const [loading, setLoading] = useState(false);
  const [connecting, setConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [shopInfo, setShopInfo] = useState<any>(null);
  const [shops, setShops] = useState<Shop[]>([]);

  useEffect(() => {
    loadShops();
    checkConnection();
  }, []);

  const loadShops = async () => {
    try {
      const data = await apiService.getShops();
      setShops(data);
    } catch (error) {
      // No shops if API fails (no auth)
      setShops([]);
    } finally {
      setLoading(false);
    }
  };

  const checkConnection = async () => {
    try {
      const status = await apiService.checkShopifyConnection();
      setIsConnected(status.connected);
      if (status.connected) {
        setShopInfo(status);
      }
    } catch (error) {
      setIsConnected(false);
    }
  };

  const handleConnectShopify = async () => {
    setConnecting(true);
    
    try {
      // Call new Direct Access status endpoint
      const status = await apiService.checkShopifyConnection();
      
      if (status.connected) {
        // Success!
        setIsConnected(true);
        setShopInfo(status);
        
        // Show success toast
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in';
        toast.innerHTML = `
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span>Connected to Shopify via Direct Token!</span>
          </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
      } else {
        // Failed
        setIsConnected(false);
        
        // Show error toast
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        toast.innerHTML = `
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            <span>${status.message || 'Token not found in Backend .env'}</span>
          </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
      }
    } catch (error: any) {
      setIsConnected(false);
      alert(`Connection failed: ${error.message || 'Unknown error'}`);
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async (shopId: string) => {
    if (!confirm("Disconnect this shop?")) return;

    try {
      await apiService.disconnectShop(shopId);
      await loadShops();
    } catch (error) {
      alert("Failed to disconnect shop");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
              <ArrowLeft className="w-5 h-5 text-gray-900 dark:text-white" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Connected Shops</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Manage your Shopify integrations
              </p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Connect New Shop */}
        <div className="mb-8">
          <button
            onClick={handleConnectShopify}
            disabled={connecting || isConnected}
            className={`w-full md:w-auto p-6 border-2 rounded-lg transition-all ${
              isConnected
                ? 'bg-green-50 dark:bg-green-900/20 border-green-500 dark:border-green-600'
                : 'bg-white dark:bg-gray-800 border-dashed border-gray-300 dark:border-gray-600 hover:border-green-500 hover:bg-green-50 dark:hover:bg-green-900/20'
            } ${connecting ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex items-center justify-center gap-3">
              {connecting ? (
                <Loader2 className="w-6 h-6 text-green-600 dark:text-green-400 animate-spin" />
              ) : isConnected ? (
                <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400" />
              ) : (
                <Plus className="w-6 h-6 text-green-600 dark:text-green-400" />
              )}
              <div className="text-left">
                <div className="font-semibold text-gray-900 dark:text-white">
                  {connecting ? 'Connecting...' : isConnected ? 'Connected to Shopify' : 'Connect Shopify'}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {isConnected && shopInfo ? shopInfo.shop_name : 'Link your Shopify store via Direct Token'}
                </div>
              </div>
            </div>
          </button>
        </div>

        {/* Connected Shops List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : shops.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-12 text-center">
            <Store className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No shops connected yet
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Connect your first Shopify store to start publishing products
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {shops.map((shop) => (
              <div
                key={shop.id}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400">
                    <Store className="w-6 h-6" />
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 dark:text-white">
                      {shop.shop_name || shop.shop_id}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                      Shopify Store
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      Connected: {new Date(shop.connected_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    shop.shop_status === "active"
                      ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400"
                      : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400"
                  }`}>
                    {shop.shop_status}
                  </span>
                  <button
                    onClick={() => handleDisconnect(shop.id)}
                    className="px-4 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  >
                    Disconnect
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Help Text */}
        <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <h4 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">How it works (Direct Access Mode)</h4>
          <ul className="space-y-1 text-sm text-blue-700 dark:text-blue-400">
            <li>• Backend uses Direct Admin API Access Token (configured in .env)</li>
            <li>• Click "Connect Shopify" to verify the connection</li>
            <li>• No OAuth redirect - instant connection check</li>
            <li>• Once connected, you can publish products directly to your Shopify store</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
