"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { apiService, ProductUpdate } from "@/services/api";
import { uploadService } from "@/services/upload";
import { ArrowLeft, Save, Loader2, Upload, X, ImagePlus } from "lucide-react";
import Link from "next/link";

export default function EditProductPage() {
  const router = useRouter();
  const params = useParams();
  const productId = params.id as string;

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [uploadingImage, setUploadingImage] = useState(false);
  const [imageAddedMessage, setImageAddedMessage] = useState("");
  const [formData, setFormData] = useState<ProductUpdate>({
    name: "",
    description: "",
    price: 0,
    stock_quantity: 0,
    weight_kg: 0,
    condition: "new",
    images: [],
  });
  
  useEffect(() => {
  }, [formData.images]);
  
  // Clear success message after 3 seconds
  useEffect(() => {
    if (imageAddedMessage) {
      const timer = setTimeout(() => setImageAddedMessage(""), 3000);
      return () => clearTimeout(timer);
    }
  }, [imageAddedMessage]);
  
  // Handler for file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    setUploadingImage(true);
    setImageAddedMessage("");
    setError("");
    
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
      setError(err.message || "Failed to upload image");
    } finally {
      setUploadingImage(false);
    }
  };

  useEffect(() => {
    loadProduct();
  }, [productId]);

  const loadProduct = async () => {
    try {
      const product = await apiService.getProduct(productId);
      setFormData({
        name: product.name,
        description: product.description || "",
        price: product.price,
        stock_quantity: product.stock_quantity,
        weight_kg: product.weight_kg || 0.5,
        condition: product.condition,
        images: product.images || [],
        sku: product.sku,
      });
    } catch (err: any) {
      // Redirect to dashboard if product not found
      router.push("/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");

    try {
      await apiService.updateProduct(productId, formData);
      router.push(`/dashboard/products/${productId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update product");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center gap-4">
            <Link
              href={`/dashboard/products/${productId}`}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Edit Product</h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Update product details
              </p>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-6">
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
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Description
            </label>
            <textarea
              value={formData.description || ""}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              <div className="mb-2 p-3 bg-green-50 border border-green-200 rounded-lg animate-pulse">
                <p className="text-sm font-medium text-green-800">{imageAddedMessage}</p>
              </div>
            )}
            
            <div className="space-y-4">
              {/* File Upload */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 bg-gray-50 dark:bg-gray-900">
                <Upload className="w-8 h-8 mx-auto text-gray-400 mb-3" />
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  Upload Product Images
                </p>
                
                {/* File Input */}
                <input
                  type="file"
                  id="fileInputEdit"
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploadingImage}
                />
                <label
                  htmlFor="fileInputEdit"
                  className={`block w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-center cursor-pointer transition-colors ${
                    uploadingImage ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  <div className="flex items-center justify-center gap-2">
                    <ImagePlus className="w-5 h-5" />
                    {uploadingImage ? 'Uploading...' : 'Choose Image from Device'}
                  </div>
                </label>
                <p className="text-xs text-gray-500 mt-2">
                  JPG, PNG, or WebP (max 5MB)
                </p>
                
                <div className="my-4 flex items-center gap-3">
                  <div className="flex-1 h-px bg-gray-300"></div>
                  <span className="text-xs text-gray-500">OR</span>
                  <div className="flex-1 h-px bg-gray-300"></div>
                </div>
                
                {/* URL Input */}
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Paste Image URL
                </p>
                <input
                  type="text"
                  placeholder="Paste image URL and press Enter..."
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      const url = e.currentTarget.value.trim();
                      if (url) {
                        
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
                <p className="text-xs text-gray-500 mt-2">
                  Example: https://images.unsplash.com/photo-1542291026-7eec264c27ff
                </p>
              </div>

              {/* Image Preview - Show when images exist */}
              {formData.images && formData.images.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Preview:</p>
                  <div className="grid grid-cols-3 gap-3">
                    {formData.images!.map((url, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={url}
                          alt={`Product ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg border-2 border-gray-300"
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
                          className="absolute top-2 right-2 p-1.5 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* SKU */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              SKU (Optional)
            </label>
            <input
              type="text"
              value={formData.sku || ""}
              onChange={(e) =>
                setFormData({ ...formData, sku: e.target.value })
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-3 pt-4">
            <Link
              href={`/dashboard/products/${productId}`}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-900 transition-colors text-center"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-semibold flex items-center justify-center gap-2"
            >
              {saving ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
