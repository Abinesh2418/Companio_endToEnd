# Companio Admin Dashboard Template

A modern, scalable admin dashboard template built with **React**, **TypeScript**, and **Vite**. This template provides a complete foundation for building admin interfaces with a professional design, responsive layout, and reusable component architecture.

## ✨ What's Included

- ✅ **Fixed Sidebar Navigation** - Clean sidebar with Feature 1 & Feature 2
- ✅ **Persistent Top Navbar** - Search, notifications, theme toggle, user profile
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Feature Pages** - Two pages with 8 sub-feature cards each (16 total cards)
- ✅ **React Router Integration** - Seamless navigation with persistent layout
- ✅ **Modern Styling** - Light theme with soft shadows and rounded cards
- ✅ **Reusable Components** - Modular architecture (Layout, Sidebar, TopNavbar, SubFeatureCard)
- ✅ **TypeScript Support** - Full type safety
- ✅ **Icon Library** - lucide-react for modern icons

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout.tsx              # Main layout wrapper
│   │   ├── Layout.css
│   │   ├── Sidebar.tsx             # Navigation sidebar
│   │   ├── Sidebar.css
│   │   ├── TopNavbar.tsx           # Header navigation
│   │   ├── TopNavbar.css
│   │   ├── SubFeatureCard.tsx      # Reusable feature card
│   │   ├── SubFeatureCard.css
│   │   └── index.ts                # Component exports
│   ├── pages/
│   │   ├── Feature1Page.tsx        # Feature 1 page with 8 cards
│   │   ├── Feature2Page.tsx        # Feature 2 page with 8 cards
│   │   ├── FeaturePage.css         # Page styling
│   │   └── index.ts                # Page exports
│   ├── App.tsx                     # Main app component with routing
│   ├── main.tsx                    # React DOM render entry
│   └── index.css                   # Global styles
├── index.html                      # HTML entry point
├── package.json                    # Project dependencies
├── tsconfig.json                   # TypeScript configuration
├── vite.config.ts                  # Vite configuration
├── .eslintrc.cjs                   # ESLint configuration
└── README.md                       # This file
```

## 🚀 Quick Start

```bash
cd frontend
npm install
npm run dev
```

The application will open at `http://localhost:5173`

## 📦 Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## 🎨 Design System

**Colors:**
- Primary Gradient: `#667eea` → `#764ba2`
- Background: `#f8f9fa`
- Text: `#1f2937`, `#6b7280`, `#9ca3af`

**Spacing:** 8px base unit (8, 12, 16, 24, 32)

**Responsive Breakpoints:**
- Desktop: 4-column grid
- Tablet (≤1024px): 3-column grid
- Mobile (≤768px): 2-column grid
- Small (≤480px): 1-column grid

## 🧩 Components

**Layout** - Wraps app with fixed sidebar and navbar  
**Sidebar** - Navigation (Feature 1, Feature 2) + user profile  
**TopNavbar** - Search, notifications, theme toggle, user profile  
**SubFeatureCard** - Reusable card with icon, title, description  

## 🔄 Routes

```
/          → /feature1 (redirect)
/feature1  → Feature 1 page (8 cards)
/feature2  → Feature 2 page (8 cards)
/*         → /feature1 (catch-all)
```

## 🔧 Customization

### Add Navigation Item

Edit `src/components/Sidebar.tsx`:
```typescript
const navigationItems = [
  { id: 'feature1', label: 'Feature 1', path: '/feature1', icon: Grid2X2 },
  { id: 'feature2', label: 'Feature 2', path: '/feature2', icon: Zap },
  { id: 'feature3', label: 'Feature 3', path: '/feature3', icon: YourIcon },
]
```

### Add New Page

1. Create `src/pages/Feature3Page.tsx`
2. Add route in `src/App.tsx`:
```typescript
<Route path="/feature3" element={<Layout><Feature3Page /></Layout>} />
```

### Change Colors

Find and replace in CSS files:
- `#667eea` and `#764ba2` (gradient)
- `#f8f9fa` (background)
- `#1f2937`, `#6b7280` (text colors)

## 📚 Tech Stack

- React 18.2 + TypeScript 5.2
- Vite 5.0 (build tool)
- React Router 6.20 (routing)
- Lucide React 0.294 (icons)
- ESLint + Prettier (code quality)

## 🚀 Build & Deploy

```bash
npm run build    # Creates optimized build in dist/
npm run preview  # Preview production build locally
```

## 💡 Tips

- Use TypeScript for type safety
- Components are in `src/components/`
- Pages are in `src/pages/`
- All styling is in `.css` files (no CSS-in-JS)
- Icons from `lucide-react` - browse at [lucide.dev](https://lucide.dev)
- Responsive design built-in
- Mock data only - connect to your backend as needed

---

**Ready to use!** 🎉 Start customizing and building your dashboard.
