#!/usr/bin/env python3
"""
Project Verification Script

Verifies that all required files and directories exist for the
AI Agent Credit System backend project.

Run with: python verify_project.py
"""

import os
from pathlib import Path


def check_file(path: str, description: str) -> bool:
    """Check if a file exists."""
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {path:<50} {description}")
    return exists


def check_directory(path: str, description: str) -> bool:
    """Check if a directory exists."""
    exists = Path(path).is_dir()
    status = "✓" if exists else "✗"
    print(f"{status} {path:<50} {description}")
    return exists


def main():
    """Verify project structure."""
    
    print("=" * 80)
    print("AI Agent Credit System - Project Verification")
    print("=" * 80)
    
    all_good = True
    
    # Root files
    print("\n📄 Root Files:")
    all_good &= check_file("README.md", "Main documentation")
    all_good &= check_file("QUICKSTART.md", "Quick start guide")
    all_good &= check_file("PROJECT_STRUCTURE.md", "File structure documentation")
    all_good &= check_file("PROJECT_SUMMARY.md", "Project summary")
    all_good &= check_file("PIPELINE_FLOW.md", "Pipeline visualization")
    all_good &= check_file("requirements.txt", "Python dependencies")
    all_good &= check_file(".env.example", "Environment template")
    all_good &= check_file(".gitignore", "Git ignore rules")
    all_good &= check_file("examples.py", "API usage examples")
    all_good &= check_file("verify_project.py", "This verification script")
    
    # Directories
    print("\n📁 Directories:")
    all_good &= check_directory("app", "Main application directory")
    all_good &= check_directory("app/routes", "API routes")
    all_good &= check_directory("app/services", "Agent services")
    all_good &= check_directory("app/models", "Data models")
    all_good &= check_directory("app/database", "Database layer")
    all_good &= check_directory("app/utils", "Utility functions")
    
    # Core application files
    print("\n🔧 Core Application Files:")
    all_good &= check_file("app/__init__.py", "App package init")
    all_good &= check_file("app/main.py", "FastAPI application")
    all_good &= check_file("app/config.py", "Configuration management")
    
    # Route files
    print("\n🛣️  Route Files:")
    all_good &= check_file("app/routes/__init__.py", "Routes package init")
    all_good &= check_file("app/routes/loan.py", "Loan routes (8 endpoints)")
    
    # Service files (6 agents)
    print("\n🤖 Service Files (6 Agents):")
    all_good &= check_file("app/services/__init__.py", "Services package init")
    all_good &= check_file("app/services/gatekeeper.py", "Gatekeeper service")
    all_good &= check_file("app/services/analyst.py", "Analyst service")
    all_good &= check_file("app/services/decision.py", "Decision service")
    all_good &= check_file("app/services/treasury.py", "Treasury service")
    all_good &= check_file("app/services/settler.py", "Settler service")
    all_good &= check_file("app/services/auditor.py", "Auditor service")
    
    # Model files
    print("\n📊 Model Files:")
    all_good &= check_file("app/models/__init__.py", "Models package init")
    all_good &= check_file("app/models/schemas.py", "API schemas")
    all_good &= check_file("app/models/db_models.py", "Database models")
    
    # Database files
    print("\n💾 Database Files:")
    all_good &= check_file("app/database/__init__.py", "Database package init")
    all_good &= check_file("app/database/db.py", "Database management")
    
    # Utils files
    print("\n🛠️  Utility Files:")
    all_good &= check_file("app/utils/__init__.py", "Utils package init")
    all_good &= check_file("app/utils/helpers.py", "Helper functions")
    
    # Summary
    print("\n" + "=" * 80)
    if all_good:
        print("✓ PROJECT VERIFICATION PASSED - All files present!")
    else:
        print("✗ PROJECT VERIFICATION FAILED - Some files missing")
    print("=" * 80)
    
    # Quick stats
    print("\n📈 Project Statistics:")
    service_files = len([f for f in Path("app/services").glob("*.py") if f.name != "__init__.py"])
    route_files = len([f for f in Path("app/routes").glob("*.py") if f.name != "__init__.py"])
    model_files = len([f for f in Path("app/models").glob("*.py") if f.name != "__init__.py"])
    
    print(f"  Services (Agents): {service_files}")
    print(f"  Route Modules: {route_files}")
    print(f"  Model Modules: {model_files}")
    print(f"  Documentation Files: 5")
    print(f"  Configuration Files: 3")
    print(f"  Total Python Files: ~24")
    
    # Next steps
    print("\n📋 Next Steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Start server: uvicorn app.main:app --reload")
    print("  3. Open docs: http://localhost:8000/docs")
    print("  4. Run examples: python examples.py")
    
    return 0 if all_good else 1


if __name__ == "__main__":
    exit(main())
