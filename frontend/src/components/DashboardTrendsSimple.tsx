"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, Sparkles, DollarSign, Loader2, ArrowRight, ChevronRight } from "lucide-react";
import { API_CONFIG } from "@/config/api";
import Link from "next/link";

interface Trend {
  product_name: string;
  category?: string;
  viral_reason?: string;
  growth_potential: string;
  price_range: string;
}

interface TrendAnalysisResult {
  category: string;
  trends: Trend[];
}

const FEATURED_CATEGORIES = ["Fashion", "Electronics", "Beauty"];

export default function DashboardTrendsSimple() {
  const [allTrends, setAllTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrends();
  }, []);

  const fetchTrends = async () => {
    setLoading(true);

    try {
      const promises = FEATURED_CATEGORIES.map(async (category) => {
        try {
          const response = await fetch(`${API_CONFIG.baseURL}/analyze/trends`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ category, region: "Indonesia" }),
          });

          if (response.ok) {
            const data = await response.json();
            return data.data.trends.slice(0, 3).map((t: Trend) => ({
              ...t,
              category: category,
            }));
          }
          return [];
        } catch {
          return [];
        }
      });

      const results = await Promise.all(promises);
      const trends = results.flat();
      setAllTrends(trends);
    } catch {
      setAllTrends([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="border-2 border-purple-200 dark:border-purple-800">
        <CardContent className="p-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-purple-600" />
            <p className="text-sm text-gray-600 dark:text-gray-400">Loading trends...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (allTrends.length === 0) {
    return (
      <Card className="border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-purple-900 dark:text-purple-100">
            <Sparkles className="w-5 h-5" />
            AI Trend Predictions
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center py-6">
          <TrendingUp className="w-12 h-12 mx-auto mb-3 text-purple-300 dark:text-purple-700" />
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Discover viral products with AI
          </p>
          <Link href="/dashboard/trends">
            <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors">
              Analyze Trends
            </button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-purple-200 dark:border-purple-800">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-purple-900 dark:text-purple-100">
            <Sparkles className="w-5 h-5" />
            AI Trend Predictions
          </CardTitle>
          <Link href="/dashboard/trends">
            <button className="flex items-center gap-1 text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium">
              View All
              <ArrowRight className="w-4 h-4" />
            </button>
          </Link>
        </div>
      </CardHeader>
      <CardContent>
        {/* Horizontal Scroll Container */}
        <div className="relative">
          <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-purple-300 dark:scrollbar-thumb-purple-700 scrollbar-track-transparent">
            {allTrends.map((trend, idx) => (
              <div
                key={idx}
                className="flex-shrink-0 w-80 bg-gradient-to-br from-white to-purple-50 dark:from-gray-800 dark:to-purple-900/20 rounded-lg border-2 border-purple-100 dark:border-purple-800 p-4 hover:shadow-lg hover:border-purple-300 dark:hover:border-purple-600 transition-all group"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-bold text-gray-900 dark:text-white text-base mb-1 line-clamp-2 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                      {trend.product_name}
                    </h3>
                    <span className="inline-block text-xs bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 px-2 py-1 rounded-full">
                      {trend.category}
                    </span>
                  </div>
                  <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    #{idx + 1}
                  </div>
                </div>

                {/* Info */}
                <div className="space-y-2">
                  {/* Price */}
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                    <span className="text-sm font-semibold text-gray-900 dark:text-white">
                      {trend.price_range}
                    </span>
                  </div>

                  {/* Growth */}
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0" />
                    <span className="text-sm font-semibold text-green-700 dark:text-green-400">
                      {trend.growth_potential}
                    </span>
                  </div>
                </div>

                {/* View Details */}
                <div className="mt-4 pt-3 border-t border-purple-100 dark:border-purple-800">
                  <button className="w-full flex items-center justify-center gap-1 text-xs text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium group-hover:gap-2 transition-all">
                    View Details
                    <ChevronRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Scroll Hint */}
        <div className="text-center mt-2">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            ← Scroll to see more trends →
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
