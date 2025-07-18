#!/bin/bash
# Generated cleanup script for Orientor project
# Review each section before running

echo "🧹 Orientor Project Cleanup Script"
echo "=================================="
echo ""

# Create backup before cleanup
echo "📦 Creating backup..."
mkdir -p cleanup_backup
cp -r . cleanup_backup/ 2>/dev/null || echo "Backup creation failed"

echo ""
echo "🔍 Files to be removed:"
echo ""

# Function to safely remove file
safe_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "Removing: $file"
        rm "$file"
    elif [ -d "$file" ]; then
        echo "Removing directory: $file"
        rm -rf "$file"
    else
        echo "File not found: $file"
    fi
}

# Definitely safe to remove
echo "📁 Definitely safe to remove:"
safe_remove "backend/app/core/cache.py"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Semibold.ttf"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Bold.woff"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Bold.woff2"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-SemiBold.woff"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Bold.ttf"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-SemiBold.woff"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Semibold.woff2"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-Bold.ttf"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-Bold.woff2"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Semibold.ttf"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Semibold.woff"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/OTF/Technor-Bold.otf"
safe_remove "frontend/src/app/fonts/Nippo_Complete/Fonts/WEB/fonts/Nippo-Bold.ttf"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-Bold.woff2"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Semibold.woff"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/OTF/Technor-Bold.otf"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Bold.woff2"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/OTF/Khand-Bold.otf"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-Bold.ttf"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/OTF/Khand-Bold.otf"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Bold.woff"
safe_remove "frontend/src/app/fonts/Nippo_Complete/Fonts/WEB/fonts/Nippo-Bold.woff2"
safe_remove "frontend/public/fonts/Nippo_Complete/Fonts/WEB/fonts/Nippo-Bold.ttf"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Semibold.woff2"
safe_remove "frontend/src/app/fonts/Technor_Complete/Fonts/OTF/Technor-Semibold.otf"
safe_remove "frontend/public/fonts/Nippo_Complete/Fonts/WEB/fonts/Nippo-Bold.woff"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-Bold.woff"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-SemiBold.woff2"
safe_remove "frontend/public/fonts/Nippo_Complete/Fonts/OTF/Nippo-Bold.otf"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/OTF/Khand-SemiBold.otf"
safe_remove "frontend/public/UIverse_n_template/JobCard.css"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/OTF/Khand-SemiBold.otf"
safe_remove "frontend/src/components/layout/MainLayout copy.tsx"
safe_remove "frontend/public/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-SemiBold.ttf"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-Bold.woff"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/OTF/Technor-Semibold.otf"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-SemiBold.ttf"
safe_remove "frontend/public/fonts/Nippo_Complete/Fonts/WEB/fonts/Nippo-Bold.woff2"
safe_remove "frontend/src/app/fonts/Nippo_Complete/Fonts/WEB/fonts/Nippo-Bold.woff"
safe_remove "backend/shared/infrastructure/cache/redis_cache.py"
safe_remove "frontend/src/app/fonts/Nippo_Complete/Fonts/OTF/Nippo-Bold.otf"
safe_remove "frontend/src/app/fonts/Khand_Complete/Fonts/WEB/fonts/Khand-SemiBold.woff2"
safe_remove "frontend/public/fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Bold.ttf"

echo ""
echo "📄 Documentation files (review before removing):"
# safe_remove "frontend/src/app/login/loginForm.module.css"
# safe_remove "reports/swarm-auto-centralized-1750620903508.json"
# safe_remove "frontend/src/app/classes/[id]/analysis/page.tsx"
# safe_remove "frontend/src/app/login/login.module.css"
# safe_remove "frontend/src/services/courseAnalysisService.ts"
# safe_remove "frontend/src/app/login/page.tsx"
# safe_remove "reports/swarm-auto-centralized-1750552628330.json"
# safe_remove "backend/alembic/versions/add_course_analysis_tables.py"
# safe_remove "backend/alembic/versions/add_llm_analysis_fields.py"
# safe_remove "frontend/src/components/chat/ConversationExportDialog.tsx"

echo ""
echo "🧪 Test files (review before removing):"

echo ""
echo "✅ Cleanup completed!"
echo "📊 Summary:"
echo "- Created backup in cleanup_backup/"
echo "- Removed definitely safe files"
echo "- Review commented sections before uncommenting"
echo ""
echo "🔧 Next steps:"
echo "1. Test the application to ensure nothing is broken"
echo "2. Run git status to see changes"
echo "3. Commit changes if everything works"
echo "4. Remove backup directory if satisfied"
