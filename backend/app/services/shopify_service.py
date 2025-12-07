"""
Shopify Service - Direct Admin API Integration
Publishes products directly to Shopify using Admin API credentials.
"""
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime


class ShopifyService:
    """Service for publishing products to Shopify using Admin API."""
    
    def __init__(self):
        """Initialize Shopify service with credentials from environment."""
        self.store_url = os.getenv("SHOPIFY_STORE_URL", "").replace("https://", "").replace("http://", "")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN", "")
        self.api_version = "2024-01"
        
        if not self.store_url or not self.access_token:
            raise ValueError("SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN must be set in .env")
    
    def _get_api_url(self, endpoint: str) -> str:
        """Construct full API URL."""
        return f"https://{self.store_url}/admin/api/{self.api_version}/{endpoint}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Shopify API requests."""
        return {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }
    
    def publish_product_to_shopify(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish a product to Shopify.
        
        Args:
            product_data: Dictionary containing:
                - name (str): Product name
                - description (str): Product description
                - price (float): Product price
                - stock (int, optional): Stock quantity
                - images (list, optional): List of image URLs
                - sku (str, optional): SKU code
                
        Returns:
            Dictionary containing:
                - success (bool): Whether the operation succeeded
                - product_id (str): Shopify product ID
                - product_url (str): URL to view product in Shopify admin
                - variant_id (str): Shopify variant ID
                - message (str): Status message
                - raw_response (dict): Full Shopify API response
                
        Raises:
            ValueError: If required fields are missing
            requests.RequestException: If API request fails
        """
        # Validate required fields
        if not product_data.get("name"):
            raise ValueError("Product name is required")
        
        if not product_data.get("price"):
            raise ValueError("Product price is required")
        
        # Build Shopify product payload
        payload = {
            "product": {
                "title": product_data["name"],
                "body_html": product_data.get("description", ""),
                "vendor": "AI Employee SaaS",
                "status": "active",  # Product is immediately active
                "variants": [
                    {
                        "price": str(product_data["price"]),
                        "inventory_management": "shopify",
                        "inventory_quantity": product_data.get("stock", 100)
                    }
                ]
            }
        }
        
        # Add SKU if provided
        if product_data.get("sku"):
            payload["product"]["variants"][0]["sku"] = product_data["sku"]
        
        # Add images if provided
        if product_data.get("images") and len(product_data["images"]) > 0:
            payload["product"]["images"] = [
                {"src": img_url} for img_url in product_data["images"]
            ]
        
        # Make API request
        url = self._get_api_url("products.json")
        headers = self._get_headers()
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            # Check for errors
            if response.status_code == 201:
                # Success
                data = response.json()
                product = data.get("product", {})
                product_id = product.get("id")
                variant_id = product.get("variants", [{}])[0].get("id")
                
                # Construct admin URL
                admin_url = f"https://{self.store_url}/admin/products/{product_id}"
                
                return {
                    "success": True,
                    "product_id": str(product_id),
                    "variant_id": str(variant_id),
                    "product_url": admin_url,
                    "message": f"Product '{product_data['name']}' successfully published to Shopify",
                    "published_at": datetime.now().isoformat(),
                    "raw_response": data
                }
            else:
                # Error response
                error_data = response.json() if response.text else {}
                error_message = error_data.get("errors", response.text)
                
                return {
                    "success": False,
                    "product_id": None,
                    "product_url": None,
                    "message": f"Shopify API error: {error_message}",
                    "status_code": response.status_code,
                    "raw_response": error_data
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "product_id": None,
                "product_url": None,
                "message": "Request to Shopify timed out after 30 seconds"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "product_id": None,
                "product_url": None,
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "product_id": None,
                "product_url": None,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a product from Shopify by ID.
        
        Args:
            product_id: Shopify product ID
            
        Returns:
            Product data or None if not found
        """
        url = self._get_api_url(f"products/{product_id}.json")
        headers = self._get_headers()
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception:
            return None
    
    def update_product(self, product_id: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing product in Shopify.
        
        Args:
            product_id: Shopify product ID
            product_data: Fields to update
            
        Returns:
            Update result
        """
        payload = {"product": {}}
        
        if "name" in product_data:
            payload["product"]["title"] = product_data["name"]
        if "description" in product_data:
            payload["product"]["body_html"] = product_data["description"]
        if "price" in product_data:
            payload["product"]["variants"] = [{"price": str(product_data["price"])}]
        
        url = self._get_api_url(f"products/{product_id}.json")
        headers = self._get_headers()
        
        try:
            response = requests.put(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Product updated successfully",
                    "raw_response": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to update product: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating product: {str(e)}"
            }
    
    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """
        Delete a product from Shopify.
        
        Args:
            product_id: Shopify product ID
            
        Returns:
            Deletion result
        """
        url = self._get_api_url(f"products/{product_id}.json")
        headers = self._get_headers()
        
        try:
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Product deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to delete product: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting product: {str(e)}"
            }
