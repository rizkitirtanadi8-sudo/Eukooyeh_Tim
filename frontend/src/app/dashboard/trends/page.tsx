"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingUp, Loader2, Sparkles, Target, DollarSign, Users } from "lucide-react";
import { API_CONFIG } from "@/config/api";

interface Trend {
  product_name: string;
  viral_reason: string;
  growth_potential: string;
  price_range: string;
  target_audience: string;
}

interface TrendAnalysisResult {
  category: string;
  region: string;
  analysis_date: string;
  season: string;
  trends: Trend[];
}

const CATEGORIES = [
  { id: "Fashion", name: "Fashion & Apparel", icon: "👗" },
  { id: "Electronics", name: "Electronics", icon: "📱" },
  { id: "Beauty", name: "Beauty & Cosmetics", icon: "💄" },
  { id: "Food", name: "Food & Beverages", icon: "🍔" },
  { id: "Home", name: "Home & Living", icon: "🏠" },
  { id: "Sports", name: "Sports & Outdoor", icon: "⚽" },
  { id: "Toys", name: "Toys & Hobbies", icon: "🎮" },
  { id: "Health", name: "Health & Wellness", icon: "💊" },
];

export default function TrendsPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<TrendAnalysisResult | null>(null);
  const [error, setError] = useState<string>("");

  const handleAnalyze = async () => {
    if (!selectedCategory) {
      setError("Please select a category");
      return;
    }

    setAnalyzing(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_CONFIG.baseURL}/analyze/trends`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          category: selectedCategory,
          region: "Indonesia",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze trends");
      }

      const data = await response.json();
      setResult(data.data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze trends");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
          <TrendingUp className="w-8 h-8" />
          AI Trend Prediction
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Discover viral micro-trends powered by AI market analysis
        </p>
      </div>

      {/* Category Selection */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Select Category</CardTitle>
          <CardDescription>Choose a product category to analyze market trends</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            {CATEGORIES.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedCategory === category.id
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 dark:border-gray-700 hover:border-gray-300"
                }`}
              >
                <div className="text-3xl mb-2">{category.icon}</div>
                <div className="text-sm font-medium">{category.name}</div>
              </button>
            ))}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
              {error}
            </div>
          )}

          <Button
            className="w-full"
            size="lg"
            onClick={handleAnalyze}
            disabled={!selectedCategory || analyzing}
          >
            {analyzing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing Trends...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 mr-2" />
                Analyze Trends
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Analysis Info */}
          <Card>
            <CardContent className="pt-6">
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Category:</span>
                  <p className="font-semibold">{result.category}</p>
                </div>
                <div>
                  <span className="text-gray-500">Region:</span>
                  <p className="font-semibold">{result.region}</p>
                </div>
                <div>
                  <span className="text-gray-500">Season:</span>
                  <p className="font-semibold">{result.season}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Trends */}
          {result.trends.map((trend, index) => (
            <Card key={index} className="border-l-4 border-l-blue-500">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl mb-2">
                      #{index + 1} {trend.product_name}
                    </CardTitle>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
                        <TrendingUp className="w-3 h-3 inline mr-1" />
                        {trend.growth_potential} Growth
                      </span>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="font-semibold text-sm text-gray-600 dark:text-gray-400 mb-1 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" />
                    Why It Will Go Viral
                  </h4>
                  <p className="text-gray-700 dark:text-gray-300">{trend.viral_reason}</p>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-semibold text-sm text-gray-600 dark:text-gray-400 mb-1 flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Price Range
                    </h4>
                    <p className="text-gray-700 dark:text-gray-300">{trend.price_range}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold text-sm text-gray-600 dark:text-gray-400 mb-1 flex items-center gap-2">
                      <Users className="w-4 h-4" />
                      Target Audience
                    </h4>
                    <p className="text-gray-700 dark:text-gray-300">{trend.target_audience}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {analyzing && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <Loader2 className="w-12 h-12 mx-auto mb-4 text-blue-500 animate-spin" />
              <p className="text-gray-600 dark:text-gray-400">AI is analyzing market trends...</p>
              <p className="text-sm text-gray-400 mt-2">This may take a few moments</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
