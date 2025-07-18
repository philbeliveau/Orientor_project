#!/bin/bash

# Orientor Project Safe Cleanup Script
# This script removes only confirmed safe files that won't break the platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧹 Orientor Project Safe Cleanup Script${NC}"
echo -e "${GREEN}======================================${NC}"
echo

# Check if we're in the right directory
if [ ! -f "CLEANUP_PLAN.md" ]; then
    echo -e "${RED}❌ Error: This script must be run from the Orientor project root directory${NC}"
    exit 1
fi

# Create backup timestamp
BACKUP_DIR="cleanup_backup_$(date +%Y%m%d_%H%M%S)"
echo -e "${YELLOW}📦 Creating backup in: $BACKUP_DIR${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup and remove file
backup_and_remove() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        local backup_path="$BACKUP_DIR/$file_path"
        mkdir -p "$(dirname "$backup_path")"
        cp "$file_path" "$backup_path"
        rm "$file_path"
        echo "  ✅ Removed: $file_path"
        return 0
    elif [ -d "$file_path" ]; then
        local backup_path="$BACKUP_DIR/$file_path"
        mkdir -p "$(dirname "$backup_path")"
        cp -r "$file_path" "$backup_path"
        rm -rf "$file_path"
        echo "  ✅ Removed: $file_path"
        return 0
    else
        echo "  ⚠️  Not found: $file_path"
        return 1
    fi
}

# Counter for removed files
removed_count=0
skipped_count=0

echo -e "${GREEN}🔧 Phase 1: Removing duplicate configuration files${NC}"
echo

# Remove duplicate configuration files
files_to_remove=(
    "package.json"
    "next.config.js"
    "tailwind.config.js"
    "tsconfig.json"
    "postcss.config.js"
    "requirements.txt"
    "requirements-simple.txt"
    "backend/requirements_deploy.txt"
    "backend/requirements_minimal.txt"
)

for file in "${files_to_remove[@]}"; do
    if backup_and_remove "$file"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
done

echo
echo -e "${GREEN}🗑️  Phase 2: Removing build artifacts and temporary files${NC}"
echo

# Remove log files
log_files=(
    "backend/app/logs/app.log"
    "backend/circuit_breaker_test.log"
    "backend/frontend.log"
    "backend/logs/app.log"
    "backend/logs/backend_dev.log"
    "backend/logs/package_creation.log"
    "backend/options_test.log"
    "backend/server_test.log"
    "backend/server.log"
    "frontend/dev.log"
    "frontend/frontend_dev.log"
    "frontend/frontend.log"
    "frontend/server_test.log"
)

for file in "${log_files[@]}"; do
    if backup_and_remove "$file"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
done

# Remove TypeScript build cache
build_cache_files=(
    "frontend/tsconfig.tsbuildinfo"
    "tsconfig.tsbuildinfo"
)

for file in "${build_cache_files[@]}"; do
    if backup_and_remove "$file"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
done

# Remove root node_modules (keep frontend/node_modules)
if [ -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Removing root node_modules directory (keeping frontend/node_modules)${NC}"
    if backup_and_remove "node_modules"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
fi

# Remove root .next directory (keep frontend/.next)
if [ -d ".next" ]; then
    echo -e "${YELLOW}📦 Removing root .next directory (keeping frontend/.next)${NC}"
    if backup_and_remove ".next"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
fi

echo
echo -e "${GREEN}🧪 Phase 3: Removing orphaned test files${NC}"
echo

# Remove orphaned test file
if backup_and_remove "__tests__/services/careerFitCalculator.test.ts"; then
    ((removed_count++))
else
    ((skipped_count++))
fi

echo
echo -e "${GREEN}🐍 Phase 4: Removing Python cache files${NC}"
echo

# Remove Python cache files
echo "  🔍 Searching for __pycache__ directories..."
while IFS= read -r -d '' dir; do
    if backup_and_remove "$dir"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
done < <(find . -name "__pycache__" -type d -print0)

echo "  🔍 Searching for .pyc files..."
while IFS= read -r -d '' file; do
    if backup_and_remove "$file"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
done < <(find . -name "*.pyc" -type f -print0)

echo
echo -e "${GREEN}🎨 Phase 5: Removing unused static assets${NC}"
echo

# Remove unused fonts
unused_fonts=(
    "frontend/public/fonts/Khand_Complete"
    "frontend/public/fonts/Nippo_Complete"
    "frontend/public/fonts/Kola_Complete"
)

for font_dir in "${unused_fonts[@]}"; do
    if backup_and_remove "$font_dir"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
done

# Remove design reference images
design_images=(
    "frontend/public/image/CompetenceTree_inspiration.png"
    "frontend/public/image/HomePageUI.png"
    "frontend/public/image/example_.png"
    "frontend/public/image/occupationtree.png"
    "frontend/public/image/svgTreeV1.png"
    "frontend/public/image/wrong competence tree.png"
)

for image in "${design_images[@]}"; do
    if backup_and_remove "$image"; then
        ((removed_count++))
    else
        ((skipped_count++))
    fi
done

echo
echo -e "${GREEN}📊 Cleanup Summary${NC}"
echo -e "${GREEN}==================${NC}"
echo -e "✅ Files removed: ${GREEN}$removed_count${NC}"
echo -e "⚠️  Files skipped: ${YELLOW}$skipped_count${NC}"
echo -e "📦 Backup created: ${GREEN}$BACKUP_DIR${NC}"
echo

# Calculate backup size
if [ -d "$BACKUP_DIR" ]; then
    backup_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    echo -e "💾 Backup size: ${GREEN}$backup_size${NC}"
fi

echo
echo -e "${GREEN}🎉 Safe cleanup completed successfully!${NC}"
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "   • All removed files have been backed up to: $BACKUP_DIR"
echo -e "   • Test your application to ensure everything works correctly"
echo -e "   • To restore files, copy them back from the backup directory"
echo -e "   • You can safely delete the backup directory after confirming everything works"
echo

echo -e "${GREEN}🧪 Next Steps:${NC}"
echo -e "   1. Test your application: npm run dev (in frontend/)"
echo -e "   2. Test backend: python -m uvicorn app.main:app --reload (in backend/)"
echo -e "   3. If everything works, you can delete the backup directory"
echo -e "   4. If issues arise, restore files from the backup directory"
echo

echo -e "${GREEN}💡 Additional Cleanup Available:${NC}"
echo -e "   • Review CLEANUP_PLAN.md for medium and low priority cleanup items"
echo -e "   • Consider running Phase 2 cleanup for additional space savings"
echo -e "   • Check for unused database migration files"
echo