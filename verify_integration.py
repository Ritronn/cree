"""
Simple verification script to check if all files are in place
"""
import os
from pathlib import Path

def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def main():
    print("\n" + "="*60)
    print("ADAPTIVE LEARNING INTEGRATION VERIFICATION")
    print("="*60)
    
    all_good = True
    
    # Backend files
    print("\n📁 Backend Files:")
    all_good &= check_file(
        "learning/adaptive_learning/coursera_service.py",
        "Coursera Service"
    )
    all_good &= check_file(
        "learning/adaptive_learning/adaptive_suggestion_views.py",
        "Adaptive Suggestion Views"
    )
    all_good &= check_file(
        "learning/adaptive_learning/recommendation_service.py",
        "Recommendation Service"
    )
    all_good &= check_file(
        "learning/adaptive_learning/urls.py",
        "URL Configuration"
    )
    
    # Frontend files
    print("\n🎨 Frontend Files:")
    all_good &= check_file(
        "frontend/src/pages/AdaptiveSuggestions.jsx",
        "Adaptive Suggestions Page"
    )
    all_good &= check_file(
        "frontend/src/pages/CourseSuggestions.jsx",
        "Course Suggestions Page"
    )
    all_good &= check_file(
        "frontend/src/pages/Dashboard.jsx",
        "Dashboard (Updated)"
    )
    all_good &= check_file(
        "frontend/src/App.jsx",
        "App Router (Updated)"
    )
    
    # Web Scraper
    print("\n🕷️ Web Scraper:")
    all_good &= check_file(
        "WebScrappingModule/Scripts/selenium_scraper_2026.py",
        "Selenium Scraper"
    )
    
    # Documentation
    print("\n📚 Documentation:")
    all_good &= check_file(
        "ADAPTIVE_LEARNING_FEATURES.md",
        "Features Documentation"
    )
    all_good &= check_file(
        "INTEGRATION_COMPLETE.md",
        "Integration Summary"
    )
    
    # Summary
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL FILES VERIFIED - INTEGRATION COMPLETE!")
        print("="*60)
        print("\n🚀 Next Steps:")
        print("1. Start Django backend:")
        print("   cd learning")
        print("   python manage.py runserver")
        print("\n2. Start React frontend:")
        print("   cd frontend")
        print("   npm run dev")
        print("\n3. Open browser and navigate to:")
        print("   http://localhost:5173")
        print("\n4. Login and click:")
        print("   - 'Adaptive Suggestions' button (purple)")
        print("   - 'Course Suggestions' button (blue)")
    else:
        print("❌ SOME FILES ARE MISSING")
        print("="*60)
        print("\nPlease check the missing files above.")
    
    print("\n" + "="*60)
    
    # Check if servers might be running
    print("\n🔍 Quick Server Check:")
    import socket
    
    def check_port(port, service):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            print(f"✅ {service} appears to be running on port {port}")
        else:
            print(f"⚠️  {service} not detected on port {port}")
    
    check_port(8000, "Django Backend")
    check_port(5173, "React Frontend")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
