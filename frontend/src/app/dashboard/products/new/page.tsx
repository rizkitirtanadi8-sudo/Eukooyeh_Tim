"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiService } from "@/services/api";
import { uploadService } from "@/services/upload";
import { Plus, X, Upload, Sparkles, Loader2, ArrowLeft, Wand2, Zap, ImagePlus } from "lucide-react";
import { API_CONFIG } from "@/config/api";
import Link from "next/link";

export default function NewProductPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState<ProductCreate>({
    name: "",
    description: "",
    price: 0,
    stock_quantity: 100,
    weight_kg: 0.5,
    condition: "new",
    images: [],
  });
  const [uploadingImage, setUploadingImage] = useState(false);
  const [imageAddedMessage, setImageAddedMessage] = useState("");
  const [useAI, setUseAI] = useState(true);
  const [aiEnhancing, setAiEnhancing] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<any>(null);
  const [specifications, setSpecifications] = useState<Record<string, string>>({});
  
  // Handler for file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    setUploadingImage(true);
    setImageAddedMessage("");
    
    try {
      const file = files[0];
      
      // Validate file
      const validation = uploadService.validateImage(file);
      if (!validation.valid) {
        setError(validation.error || "Invalid file");
        setUploadingImage(false);
        return;
      }
      
      
      // Upload to backend
      const imageUrl = await uploadService.uploadImage(file);
      
      // Add to images array
      setFormData((prev) => {
        const newImages = [...(prev.images || []), imageUrl];
        return { ...prev, images: newImages };
      });
      
      setImageAddedMessage(`✅ Image uploaded! Total: ${(formData.images?.length || 0) + 1}`);
      
      // Clear input
      e.target.value = '';
    } catch (err: any) {
      setError(typeof err === 'string' ? err : err.message || "Failed to upload image");
    } finally {
      setUploadingImage(false);
    }
  };
  
  useEffect(() => {
  }, [formData.images]);
  
  // Clear success message after 3 seconds
  useEffect(() => {
    if (imageAddedMessage) {
      const timer = setTimeout(() => setImageAddedMessage(""), 3000);
      return () => clearTimeout(timer);
    }
  }, [imageAddedMessage]);

  // AI Enhancement Handler
  const handleAIEnhancement = async () => {
    if (!formData.name || formData.images.length === 0) {
      setError("Please add product name and at least one image for AI enhancement");
      return;
    }
    
    setAiEnhancing(true);
    setError("");
    
    try {
      const response = await fetch(`${API_CONFIG.baseURL}/products/enhance`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_url: formData.images[0],
          user_description: formData.description,
          product_name: formData.name,
          price: formData.price,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Enhancement failed: ${response.statusText}`);
      }
      
      const suggestions = await response.json();
      setAiSuggestions(suggestions);
      
      // Apply AI suggestions to form (user can edit)
      setFormData(prev => ({
        ...prev,
        description: suggestions.enhanced_description,
      }));
      
      // Set specifications
      if (suggestions.specifications) {
        setSpecifications(suggestions.specifications);
      }
      
      setImageAddedMessage("✨ AI enhancement applied! You can edit the results below.");
      
    } catch (err: any) {
      const errorMsg = typeof err === 'string' ? err : (err.message || "AI enhancement failed");
      setError(errorMsg);
    } finally {
      setAiEnhancing(false);
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      
      // Include specifications in formData
      const productData = {
        ...formData,
        specifications: specifications || {}
      };
      
      const product = await apiService.createProduct(productData);
      
      // Redirect to product detail page to publish
      if (product && product.id) {
        router.push(`/dashboard/products/${product.id}`);
      } else {
        throw new Error("Product created but no ID returned");
      }
    } catch (err: any) {
      let errorMsg = "Failed to create product";
      if (typeof err === 'string') {
        errorMsg = err;
      } else if (err.response?.data?.detail) {
        errorMsg = typeof err.response.data.detail === 'string' 
          ? err.response.data.detail 
          : JSON.stringify(err.response.data.detail);
      } else if (err.message) {
        errorMsg = err.message;
      }
      setError(errorMsg);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-3 sm:px-6 lg:px-8 py-3 sm:py-4">
          <div className="flex items-center gap-2 sm:gap-4">
            <Link
              href="/dashboard"
              className="p-1.5 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors flex-shrink-0"
            >
              <ArrowLeft className="w-4 h-4 sm:w-5 sm:h-5" />
            </Link>
            <div className="min-w-0">
              <h1 className="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white truncate">
                Create New Product
              </h1>
              <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 hidden sm:block">
                Add simple product details - AI will optimize for marketplaces
              </p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8">
        {/* Info Banner */}
        <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg flex items-start gap-2 sm:gap-3">
          <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600 dark:text-blue-300 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="text-sm sm:text-base font-semibold text-blue-900 dark:text-blue-200 mb-1">
              AI-Powered Optimization
            </h3>
            <p className="text-xs sm:text-sm text-blue-700 dark:text-blue-300">
              Just provide basic details. Our AI will predict categories, fill
              attributes, and optimize your listing for each marketplace.
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-xs sm:text-sm text-red-600 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700 p-4 sm:p-6 space-y-4 sm:space-y-6">
          {/* AI Tools Toggle */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border-2 border-purple-200 dark:border-purple-700 rounded-lg p-3 sm:p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 sm:gap-3 min-w-0">
                <div className="p-1.5 sm:p-2 bg-purple-600 rounded-lg flex-shrink-0">
                  <Wand2 className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <div className="min-w-0">
                  <h3 className="text-sm sm:text-base font-semibold text-gray-900 dark:text-gray-100">AI Enhancement Tools</h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 hidden sm:block">Let AI optimize your product listing</p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={useAI}
                  onChange={(e) => setUseAI(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 dark:bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600 dark:peer-checked:bg-purple-500"></div>
              </label>
            </div>
            
            {useAI && (
              <div className="space-y-3">
                <button
                  type="button"
                  onClick={handleAIEnhancement}
                  disabled={aiEnhancing || !formData.name || formData.images.length === 0}
                  className="w-full px-3 sm:px-4 py-2.5 sm:py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2 text-sm sm:text-base"
                >
                  {aiEnhancing ? (
                    <>
                      <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
                      <span className="hidden sm:inline">Analyzing with AI...</span>
                      <span className="sm:hidden">Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 sm:w-5 sm:h-5" />
                      Enhance with AI
                    </>
                  )}
                </button>
                <p className="text-xs text-gray-600 dark:text-gray-400 text-center">
                  {!formData.name || formData.images.length === 0 
                    ? "⚠️ Add product name and at least one image first"
                    : "✨ AI will analyze your product and suggest improvements"}
                </p>
                
                {aiSuggestions && (
                  <div className="mt-3 p-4 bg-white dark:bg-blue-950/30 rounded-lg border border-purple-200 dark:border-purple-700 space-y-3">
                    <p className="text-sm font-semibold text-purple-900 dark:text-purple-300">🎯 AI Analysis Results:</p>
                    
                    {aiSuggestions.category_prediction && (
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400">Category:</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{aiSuggestions.category_prediction}</p>
                      </div>
                    )}
                    
                    {aiSuggestions.selling_points && aiSuggestions.selling_points.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Key Selling Points:</p>
                        <ul className="text-xs text-gray-700 dark:text-gray-300 space-y-1">
                          {aiSuggestions.selling_points.map((point: string, idx: number) => (
                            <li key={idx}>✓ {point}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {aiSuggestions.seo_keywords && aiSuggestions.seo_keywords.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">SEO Keywords:</p>
                        <div className="flex flex-wrap gap-1">
                          {aiSuggestions.seo_keywords.map((keyword: string, idx: number) => (
                            <span key={idx} className="px-2 py-1 bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300 text-xs rounded">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {aiSuggestions.suggested_tags && aiSuggestions.suggested_tags.length > 0 && (
                      <div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Suggested Tags:</p>
                        <div className="flex flex-wrap gap-1">
                          {aiSuggestions.suggested_tags.map((tag: string, idx: number) => (
                            <span key={idx} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 text-xs rounded">
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Product Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Product Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
              placeholder="e.g., Sepatu Sneakers Pria Casual"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Be descriptive - AI uses this to predict category
            </p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description {aiSuggestions && <span className="text-green-600 text-xs">(✨ AI Enhanced - Editable)</span>}
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
              placeholder="Brief description of your product... (AI will enhance this)"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {aiSuggestions 
                ? "✓ AI-enhanced description applied. You can edit it as needed." 
                : "Click 'Enhance with AI' to generate optimized content"}
            </p>
          </div>

          {/* Specifications (AI Generated) */}
          {Object.keys(specifications).length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Specifications {aiSuggestions && <span className="text-green-600 text-xs">(✨ AI Generated - Editable)</span>}
              </label>
              <div className="space-y-2 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-dark-border">
                {Object.entries(specifications).map(([key, value]) => (
                  <div key={key} className="grid grid-cols-3 gap-3">
                    <input
                      type="text"
                      value={key}
                      onChange={(e) => {
                        const newSpecs = { ...specifications };
                        delete newSpecs[key];
                        newSpecs[e.target.value] = value;
                        setSpecifications(newSpecs);
                      }}
                      className="col-span-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                      placeholder="Key"
                    />
                    <input
                      type="text"
                      value={value}
                      onChange={(e) => {
                        setSpecifications({
                          ...specifications,
                          [key]: e.target.value,
                        });
                      }}
                      className="col-span-2 px-3 py-2 border border-gray-300 dark:border-dark-border rounded text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                      placeholder="Value"
                    />
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => {
                    const newKey = `Spec ${Object.keys(specifications).length + 1}`;
                    setSpecifications({ ...specifications, [newKey]: "" });
                  }}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
                >
                  + Add Specification
                </button>
              </div>
            </div>
          )}

          {/* Price & Stock */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Price (Rp) *
              </label>
              <input
                type="number"
                required
                min="0"
                value={formData.price}
                onChange={(e) =>
                  setFormData({ ...formData, price: Number(e.target.value) })
                }
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
                placeholder="250000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Stock Quantity
              </label>
              <input
                type="number"
                min="0"
                value={formData.stock_quantity}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    stock_quantity: Number(e.target.value),
                  })
                }
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
                placeholder="100"
              />
            </div>
          </div>

          {/* Weight & Condition */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Weight (kg)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={formData.weight_kg}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    weight_kg: Number(e.target.value),
                  })
                }
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
                placeholder="0.5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Condition
              </label>
              <select
                value={formData.condition}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    condition: e.target.value as "new" | "used",
                  })
                }
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
              >
                <option value="new">New</option>
                <option value="used">Used</option>
              </select>
            </div>
          </div>

          {/* Product Images */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Product Images {formData.images && formData.images.length > 0 && `(${formData.images.length})`}
            </label>
            
            {/* Success Message */}
            {imageAddedMessage && (
              <div className="mb-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg animate-pulse">
                <p className="text-sm font-medium text-green-800 dark:text-green-200">{imageAddedMessage}</p>
              </div>
            )}

            <div className="space-y-4">
              {/* File Upload */}
              <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 bg-gray-50 dark:bg-gray-800">
                <Upload className="w-8 h-8 mx-auto text-gray-400 dark:text-gray-500 mb-3" />
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Upload Product Images
                </p>
                
                {/* File Input */}
                <input
                  type="file"
                  id="fileInput"
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploadingImage}
                />
                <label
                  htmlFor="fileInput"
                  className={`block w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-center cursor-pointer transition-colors ${
                    uploadingImage ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <ImagePlus className="w-5 h-5" />
                    {uploadingImage ? 'Uploading...' : 'Choose Image from Device'}
                  </div>
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  JPG, PNG, or WebP (max 5MB)
                </p>
                
                <div className="my-4 flex items-center gap-3">
                  <div className="flex-1 h-px bg-gray-300 dark:bg-gray-600"></div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">OR</span>
                  <div className="flex-1 h-px bg-gray-300 dark:bg-gray-600"></div>
                </div>
                
                {/* URL Input */}
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Paste Image URL
                </p>
                <input
                  id="imageUrlInput"
                  type="text"
                  placeholder="Paste image URL and press Enter..."
                  className="w-full px-4 py-3 border-2 border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const url = e.currentTarget.value.trim();
                      if (url) {
                        
                        // Use functional state update to ensure React detects change
                        setFormData((prev) => {
                          const newImages = [...(prev.images || []), url];
                          return { ...prev, images: newImages };
                        });
                        
                        setImageAddedMessage(`✅ Image added! Total: ${(formData.images?.length || 0) + 1}`);
                        e.currentTarget.value = '';
                      }
                    }
                  }}
                />
                <button
                  type="button"
                  onClick={() => {
                    const input = document.getElementById('imageUrlInput') as HTMLInputElement;
                    const url = input?.value.trim();
                    if (url) {
                      
                      // Use functional state update to ensure React detects change
                      setFormData((prev) => {
                        const newImages = [...(prev.images || []), url];
                        return { ...prev, images: newImages };
                      });
                      
                      setImageAddedMessage(`✅ Image added! Total: ${(formData.images?.length || 0) + 1}`);
                      input.value = '';
                    }
                  }}
                  className="mt-3 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                >
                  Add Image (or press Enter)
                </button>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-3">
                  Example: https://images.unsplash.com/photo-1542291026-7eec264c27ff
                </p>
              </div>

              {/* Image Preview */}
              <div className="border-2 border-blue-300 dark:border-blue-600 rounded-lg p-4 bg-blue-50 dark:bg-blue-900/30">
                <p className="text-sm font-semibold text-blue-900 dark:text-blue-400 mb-3">
                  Preview ({formData.images?.length || 0} images):
                </p>
                {formData.images && formData.images.length > 0 ? (
                  <div className="grid grid-cols-3 gap-3">
                    {formData.images.map((url, index) => (
                      <div key={`${url}-${index}`} className="relative group bg-white dark:bg-gray-800 rounded-lg overflow-hidden border-2 border-gray-300 dark:border-gray-600">
                        <img
                          src={url}
                          alt={`Product ${index + 1}`}
                          className="w-full h-32 object-cover"
                          onError={(e) => {
                            e.currentTarget.src = "https://via.placeholder.com/150?text=Invalid+URL";
                          }}
                        />
                        <button
                          type="button"
                          onClick={() => {
                            setFormData((prev) => {
                              const newImages = prev.images?.filter((_, i) => i !== index) || [];
                              return { ...prev, images: newImages };
                            });
                          }}
                          className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 shadow-lg"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                    <p className="text-sm">No images yet. Add one above!</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Manual Specifications */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Product Specifications
            </label>
            <div className="space-y-3">
              {specifications && Object.entries(specifications).map(([key, value], index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    value={key}
                    onChange={(e) => {
                      const newSpecs = { ...specifications };
                      delete newSpecs[key];
                      newSpecs[e.target.value] = value;
                      setSpecifications(newSpecs);
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-blue-500 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    placeholder="e.g., Brand, Material, Size"
                  />
                  <input
                    type="text"
                    value={value}
                    onChange={(e) => {
                      setSpecifications({ ...specifications, [key]: e.target.value });
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-dark-border rounded-lg focus:ring-2 focus:ring-blue-500 text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                    placeholder="Value"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      const newSpecs = { ...specifications };
                      delete newSpecs[key];
                      setSpecifications(newSpecs);
                    }}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => {
                  const newKey = `Spec ${Object.keys(specifications || {}).length + 1}`;
                  setSpecifications({ ...specifications, [newKey]: "" });
                }}
                className="w-full px-4 py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors text-sm font-medium"
              >
                + Add Specification
              </button>
            </div>
          </div>

          {/* SKU (Optional) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              SKU (Optional)
            </label>
            <input
              type="text"
              value={formData.sku}
              onChange={(e) =>
                setFormData({ ...formData, sku: e.target.value })
              }
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent"
              placeholder="SNK-001"
            />
          </div>

          {/* Submit Buttons - Fixed for Mobile */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 pb-6">
            <Link
              href="/dashboard"
              className="w-full sm:flex-1 px-4 sm:px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-center font-medium"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:flex-1 px-4 sm:px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold"
            >
              {loading ? "Creating..." : "Create Product"}
            </button>
          </div>
        </form>

        {/* Help Text */}
        <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">What happens next?</h4>
          <ul className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
            <li>• Product saved as <strong>draft</strong></li>
            <li>• Use AI enrichment to optimize for marketplaces</li>
            <li>• Connect your shops (Shopee/TikTok)</li>
            <li>• Publish with one click!</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
