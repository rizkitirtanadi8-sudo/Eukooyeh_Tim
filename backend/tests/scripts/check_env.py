"""
Environment configuration checker.
Run this before starting the application to verify all required settings.
"""
import os
from pathlib import Path

def check_env():
    """Check if all required environment variables are set."""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and fill in your credentials")
        return False
    
    required_vars = [
        "OPENAI_API_KEY",
        "OPENAI_API_BASE",
        "SUPABASE_URL",
        "SUPABASE_KEY"
    ]
    
    optional_vars = [
        "GOOGLE_SEARCH_API_KEY",
        "GOOGLE_SEARCH_ENGINE_ID"
    ]
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    print("🔍 Checking environment configuration...\n")
    
    all_good = True
    
    # Check required
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            print(f"❌ {var}: Not configured")
            all_good = False
        else:
            print(f"✅ {var}: Configured")
    
    # Check optional
    print("\n📦 Optional configurations:")
    for var in optional_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            print(f"⚠️  {var}: Not configured (Google Search features disabled)")
        else:
            print(f"✅ {var}: Configured")
    
    print("\n" + "="*50)
    if all_good:
        print("✅ All required configurations are set!")
        print("🚀 You can start the application now")
        return True
    else:
        print("❌ Some required configurations are missing")
        print("📝 Please update your .env file")
        return False

if __name__ == "__main__":
    check_env()
