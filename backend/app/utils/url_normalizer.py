"""URL normalization utilities for handling complex e-commerce URLs."""

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from typing import Optional


def normalize_url(url: str) -> str:
    """Normalize URL by removing tracking parameters and fragments."""
    try:
        parsed = urlparse(url)
        
        # Remove fragment
        parsed = parsed._replace(fragment='')
        
        # Parse query parameters
        query_params = parse_qs(parsed.query)
        
        # Keep only essential parameters based on site
        essential_params = get_essential_params(parsed.netloc, query_params)
        
        # Rebuild query string
        clean_query = urlencode(essential_params, doseq=True) if essential_params else ''
        
        # Rebuild URL
        clean_parsed = parsed._replace(query=clean_query)
        return urlunparse(clean_parsed)
        
    except Exception:
        return url


def get_essential_params(domain: str, params: dict) -> dict:
    """Get essential parameters to keep based on domain."""
    essential = {}
    
    if 'amazon' in domain.lower():
        # Keep product ID and variant info
        for key in ['dp', 'gp', 'asin', 'th', 'psc']:
            if key in params:
                essential[key] = params[key]
                
    elif 'jumia' in domain.lower():
        # Keep product ID
        for key in ['sku', 'catalog']:
            if key in params:
                essential[key] = params[key]
                
    elif 'konga' in domain.lower():
        # Keep product ID
        for key in ['product_id', 'pid']:
            if key in params:
                essential[key] = params[key]
                
    elif 'shopify' in domain.lower():
        # Keep variant info
        for key in ['variant']:
            if key in params:
                essential[key] = params[key]
    
    return essential


def extract_product_id(url: str) -> Optional[str]:
    """Extract product ID from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path
        query_params = parse_qs(parsed.query)
        
        # Amazon patterns
        if 'amazon' in domain:
            # /dp/PRODUCT_ID or /gp/product/PRODUCT_ID
            match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', path)
            if match:
                return match.group(1)
            # ASIN parameter
            if 'asin' in query_params:
                return query_params['asin'][0]
                
        # Jumia patterns
        elif 'jumia' in domain:
            # Extract from path or SKU parameter
            match = re.search(r'-(\d+)\.html', path)
            if match:
                return match.group(1)
            if 'sku' in query_params:
                return query_params['sku'][0]
                
        # Konga patterns
        elif 'konga' in domain:
            match = re.search(r'/product/[^/]+-(\d+)', path)
            if match:
                return match.group(1)
                
        # Generic patterns
        else:
            # Look for numeric IDs in path
            match = re.search(r'/(\d+)(?:/|$)', path)
            if match:
                return match.group(1)
                
    except Exception:
        pass
        
    return None


def is_product_url(url: str) -> bool:
    """Check if URL is likely a product page."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Known e-commerce domains
        ecommerce_domains = [
            'amazon', 'jumia', 'konga', 'shopify', 'woocommerce',
            'ebay', 'aliexpress', 'etsy', 'walmart', 'target'
        ]
        
        if any(d in domain for d in ecommerce_domains):
            return True
            
        # Product page patterns
        product_patterns = [
            r'/product[s]?/',
            r'/item[s]?/',
            r'/p/',
            r'/dp/',
            r'/gp/product/',
            r'\.html$'
        ]
        
        return any(re.search(pattern, path) for pattern in product_patterns)
        
    except Exception:
        return False