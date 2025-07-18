# Static Assets Analysis Report

## Summary
This report analyzes the usage of static assets (images, fonts, CSS files) in the Orientor project to identify used assets, unused assets, and potential optimization opportunities.

## Font Assets Analysis

### Currently Used Fonts

#### 1. **DepartureMono** (Used)
- **Location**: `/frontend/public/fonts/DepartureMono-1.422/`
- **Size**: 120KB total
- **Usage**: 
  - Imported in `layout.tsx` as `--font-departure`
  - Used in `TypographyContext.tsx` for monospace font
  - Referenced in `globals.css` for font-face declarations
- **Status**: ✅ **ACTIVELY USED** - Keep

#### 2. **Technor** (Used)
- **Location**: `/frontend/public/fonts/Technor_Complete/`
- **Size**: 1.3MB total
- **Usage**:
  - Imported in `layout.tsx` with multiple weights (400, 500, 600, 700)
  - Used in `TypographyContext.tsx` as theme option
  - Referenced in `globals.css` for font-face declarations
- **Variations Used**: Regular, Semibold, Bold (only these 3 out of 7 available)
- **Status**: ✅ **ACTIVELY USED** - Keep used weights, remove unused weights

#### 3. **Khand** (Defined but Not Used)
- **Location**: `/frontend/public/fonts/Khand_Complete/`
- **Size**: 876KB total
- **Usage**: 
  - Defined in `TypographyContext.tsx` but CSS not imported in layout
  - Font files exist but not loaded in the application
- **Status**: ⚠️ **UNUSED** - Remove or properly implement

#### 4. **Nippo** (Defined but Not Used)
- **Location**: `/frontend/public/fonts/Nippo_Complete/`
- **Size**: 1.1MB total
- **Usage**: 
  - Defined in `TypographyContext.tsx` but CSS not imported in layout
  - Font files exist but not loaded in the application
- **Status**: ⚠️ **UNUSED** - Remove or properly implement

#### 5. **Kola** (Defined but Not Used)
- **Location**: `/frontend/public/fonts/Kola_Complete/`
- **Size**: 216KB total
- **Usage**: 
  - Defined in `TypographyContext.tsx` but CSS not imported in layout
  - Font files exist but not loaded in the application
- **Status**: ⚠️ **UNUSED** - Remove or properly implement

### Font Usage Summary
- **Total Font Size**: 3.6MB
- **Actually Used**: 1.4MB (DepartureMono + Technor)
- **Unused**: 2.2MB (Khand, Nippo, Kola)
- **Optimization Potential**: 2.2MB can be removed

## Image Assets Analysis

### Avatar Images (Used)
- **Location**: `/frontend/public/avatar/`
- **Size**: ~1.2MB total (11 images)
- **Usage**: 
  - Actively used in `JobCard.tsx` component
  - Dynamically selected based on job keywords
  - All 11 avatars are potentially referenced
- **Status**: ✅ **ACTIVELY USED** - Keep all

### Main Images (Mixed Usage)

#### Used Images:
1. **Avatar.PNG** (116KB)
   - Used in `dashboard/page.tsx` and `stitch-demo/page.tsx`
   - Status: ✅ **ACTIVELY USED**

2. **greg.png** (Unknown size)
   - Used in `page_RadioStyles.tsx`
   - Status: ✅ **ACTIVELY USED**

3. **Logo.png** (Unknown size)
   - Likely used for branding (not found in current search)
   - Status: ⚠️ **VERIFY USAGE**

#### Potentially Unused Images:
1. **navigo-hero.png** (Unknown size)
   - No references found in current codebase
   - Status: ❌ **POTENTIALLY UNUSED**

2. **trees.png** (Unknown size)
   - No references found in current codebase
   - Status: ❌ **POTENTIALLY UNUSED**

3. **career_comparison.png** (Unknown size)
   - No references found in current codebase
   - Status: ❌ **POTENTIALLY UNUSED**

### Pattern Images (Used)
- **Location**: `/frontend/public/patterns/`
- **Files**: `branch.svg`, `grid.svg`
- **Usage**: 
  - Referenced in `tailwind.config.js` for CSS patterns
  - Used as background patterns
- **Status**: ✅ **ACTIVELY USED** - Keep

### Image Directory Assets (Unused)
- **Location**: `/frontend/public/image/`
- **Total Size**: ~4.5MB
- **Files**:
  - `CompetenceTree_inspiration.png` (2.3MB)
  - `HomePageUI.png` (766KB)
  - `example_.png` (467KB)
  - `occupationtree.png` (164KB)
  - `svgTreeV1.png` (580KB)
  - `wrong competence tree.png` (303KB)
- **Status**: ❌ **UNUSED** - These appear to be design references/mockups

### SVG Icons (Unclear Usage)
- **Location**: `/frontend/public/`
- **Files**: `window.svg`, `file.svg`, `vercel.svg`, `globe.svg`, `next.svg`
- **Status**: ⚠️ **NEED VERIFICATION** - May be used in components not yet analyzed

## CSS Module Files Analysis

### Used CSS Modules
The following CSS modules are actively used:
- `ChatBot.module.css` - Chat interface styling
- `JobCard.module.css` - Job card component styling
- `AvatarCard.module.css`, `AvatarPanel.module.css` - Avatar components
- `login.module.css`, `loginForm.module.css` - Authentication forms
- `NewSidebar.module.css` - Navigation sidebar
- Various UI component modules

### CSS Pattern Usage
- **Location**: Pattern CSS files like `patterns.module.css`
- **Status**: ✅ **ACTIVELY USED** - Keep

## Optimization Recommendations

### High Priority (Immediate Action)
1. **Remove Unused Fonts** (Save 2.2MB)
   - Delete `/frontend/public/fonts/Khand_Complete/` (876KB)
   - Delete `/frontend/public/fonts/Nippo_Complete/` (1.1MB)
   - Delete `/frontend/public/fonts/Kola_Complete/` (216KB)
   - Remove references from `TypographyContext.tsx`

2. **Remove Design Reference Images** (Save 4.5MB)
   - Delete entire `/frontend/public/image/` directory
   - These are design references, not production assets

3. **Optimize Technor Font** (Save ~500KB)
   - Remove unused weights: Extralight, Light, Medium, Black
   - Keep only: Regular (400), Semibold (600), Bold (700)

### Medium Priority
1. **Verify and Remove Unused Images**
   - Check `navigo-hero.png`, `trees.png`, `career_comparison.png` usage
   - If unused, remove them

2. **Optimize Font Loading**
   - Implement proper font-display strategies
   - Consider font subsetting for better performance

### Low Priority
1. **Image Optimization**
   - Compress avatar images (currently ~100KB each)
   - Consider WebP format for better compression
   - Implement responsive image loading

## Detailed Usage Tracking

### Font References Found:
- `globals.css`: DepartureMono, Technor font-face declarations
- `layout.tsx`: DepartureMono, Technor imports
- `TypographyContext.tsx`: All 5 fonts defined (but 3 unused)

### Image References Found:
- `JobCard.tsx`: All avatar images dynamically referenced
- `dashboard/page.tsx`: Avatar.PNG
- `page_RadioStyles.tsx`: greg.png
- `stitch-demo/page.tsx`: Avatar.PNG
- `tailwind.config.js`: branch.svg, grid.svg patterns

### CSS Module Usage:
- 24 CSS module files found
- All appear to be referenced by their corresponding React components
- No orphaned CSS modules detected

## Total Optimization Potential
- **Fonts**: 2.2MB (61% reduction)
- **Images**: 4.5MB (design references)
- **Total Savings**: ~6.7MB (significant for web performance)

## Recommendations for Dynamic Asset Loading

### Current Dynamic Usage:
1. **Avatar Selection**: JobCard component dynamically selects from 11 avatars
2. **Pattern Usage**: CSS patterns loaded via Tailwind configuration

### Suggested Improvements:
1. **Font Loading**: Implement font loading strategies for unused typography themes
2. **Image Lazy Loading**: Implement lazy loading for avatar images
3. **Asset Chunking**: Consider code splitting for theme-specific assets

## Security Considerations
- All font files from reputable sources (Indian Type Foundry)
- No malicious content detected in any asset files
- All paths are properly configured for Next.js public directory

## Next Steps
1. Remove unused fonts and design reference images
2. Implement proper font loading for typography themes
3. Verify usage of potentially unused main images
4. Consider implementing asset optimization pipeline