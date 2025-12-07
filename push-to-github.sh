#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   GitHub Push Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if in git repository
if [ ! -d .git ]; then
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    git branch -M main
    echo -e "${GREEN}✅ Git initialized${NC}"
    echo ""
fi

# Check for .env files
echo -e "${BLUE}Checking for sensitive files...${NC}"
if [ -f "backend/.env" ]; then
    echo -e "${RED}⚠️  WARNING: backend/.env exists!${NC}"
    echo -e "${YELLOW}This file should NOT be committed.${NC}"
    echo -e "${YELLOW}Make sure it's in .gitignore${NC}"
    echo ""
fi

if [ -f "frontend/.env.local" ]; then
    echo -e "${RED}⚠️  WARNING: frontend/.env.local exists!${NC}"
    echo -e "${YELLOW}This file should NOT be committed.${NC}"
    echo -e "${YELLOW}Make sure it's in .gitignore${NC}"
    echo ""
fi

# Show what will be committed
echo -e "${BLUE}Files to be committed:${NC}"
git status --short | head -20
echo ""

# Ask for confirmation
read -p "Do you want to continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 1
fi

# Add all files
echo -e "${BLUE}Adding files...${NC}"
git add .
echo -e "${GREEN}✅ Files staged${NC}"
echo ""

# Show staged files
echo -e "${BLUE}Staged files:${NC}"
git status --short
echo ""

# Commit
echo -e "${BLUE}Creating commit...${NC}"
git commit -m "feat: initial commit - AI E-commerce Product Manager

🤖 AI Multi-Agent System
- Vision analysis with GPT-4 Vision
- Auto category detection
- Smart price suggestions
- AI copywriting

🛒 Shopify Integration
- Direct API publishing
- One-click product sync
- Inventory management

📊 Market Intelligence
- Real-time trend analysis
- Competitor monitoring
- Google Search API integration

🎨 Modern UI/UX
- Next.js 14 + TypeScript
- Dark mode support
- Responsive design
- TailwindCSS + Shadcn/ui

🏗️ Tech Stack
- Backend: FastAPI + CrewAI + Supabase
- Frontend: Next.js + TypeScript
- AI: OpenAI/Kolosal AI
- Database: PostgreSQL (Supabase)

✅ Production Ready
- Clean code architecture
- Complete documentation
- Type-safe
- Error handling
- Security best practices
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Commit created${NC}"
    echo ""
else
    echo -e "${RED}❌ Commit failed${NC}"
    exit 1
fi

# Ask for GitHub username
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}GitHub Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
read -p "Enter your GitHub username: " github_username

if [ -z "$github_username" ]; then
    echo -e "${RED}❌ Username required${NC}"
    exit 1
fi

# Repository name
repo_name="ai-ecommerce-manager"

# Check if remote exists
if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Remote 'origin' already exists. Removing...${NC}"
    git remote remove origin
fi

# Add remote
echo -e "${BLUE}Adding remote...${NC}"
git remote add origin "https://github.com/$github_username/$repo_name.git"
echo -e "${GREEN}✅ Remote added${NC}"
echo ""

# Show remote
echo -e "${BLUE}Remote URL:${NC}"
git remote -v
echo ""

# Ask to push
echo -e "${YELLOW}Ready to push to GitHub!${NC}"
echo -e "${BLUE}Repository: https://github.com/$github_username/$repo_name${NC}"
echo ""
read -p "Push now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Pushing to GitHub...${NC}"
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}   ✅ SUCCESS!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo -e "${GREEN}Repository URL:${NC}"
        echo -e "${BLUE}https://github.com/$github_username/$repo_name${NC}"
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo "1. Go to your GitHub repository"
        echo "2. Add topics/tags (ai, ecommerce, shopify, etc.)"
        echo "3. Update repository description"
        echo "4. Add website link (if deployed)"
        echo ""
        echo -e "${GREEN}Good luck with your hackathon! 🏆${NC}"
    else
        echo ""
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}   ❌ PUSH FAILED${NC}"
        echo -e "${RED}========================================${NC}"
        echo ""
        echo -e "${YELLOW}Possible reasons:${NC}"
        echo "1. Repository doesn't exist on GitHub"
        echo "   → Create it at: https://github.com/new"
        echo "2. Authentication failed"
        echo "   → Check your GitHub credentials"
        echo "3. Branch name mismatch"
        echo "   → Try: git push -u origin main"
        echo ""
    fi
else
    echo -e "${YELLOW}Push cancelled.${NC}"
    echo -e "${BLUE}You can push later with:${NC}"
    echo "git push -u origin main"
fi

echo ""
