# Testing Guide - Mobile Responsive Features

## How to Test

### 1. Desktop Testing
1. Open the app in your browser
2. The sidebar should be visible by default
3. Click the sidebar toggle button to collapse/expand
4. Hover over buttons to see smooth animations
5. Test theme switching (light/dark)

### 2. Mobile Testing (Browser DevTools)
1. Open Chrome/Firefox DevTools (F12)
2. Click the device toolbar icon (Ctrl+Shift+M)
3. Select different devices:
   - iPhone SE (375px)
   - iPhone 12 Pro (390px)
   - Pixel 5 (393px)
   - Samsung Galaxy S20 Ultra (412px)
   - iPad Air (820px)
   - iPad Pro (1024px)

### 3. Features to Test

#### Sidebar (Mobile < 1100px)
- [ ] Sidebar is hidden by default
- [ ] Hamburger icon (☰) appears in toggle button
- [ ] Clicking opens sidebar from left with overlay
- [ ] Clicking overlay closes sidebar
- [ ] Sidebar slides smoothly
- [ ] Body scroll disabled when sidebar open

#### Responsive Layout
- [ ] Top bar adjusts padding on mobile
- [ ] Auth button text truncates properly
- [ ] Theme label hides on small screens (<480px)
- [ ] Chat messages adapt to screen width
- [ ] Code blocks scroll horizontally if needed
- [ ] Input bar maintains proper height

#### Touch Interactions
- [ ] Buttons are at least 44px (tap targets)
- [ ] Send button becomes circular on mobile
- [ ] "Send" text hides on mobile (<768px)
- [ ] Settings dropdown positions correctly
- [ ] Smooth transitions on tap
- [ ] No hover effects on touch devices

#### Typography & Spacing
- [ ] Font sizes scale down on mobile
- [ ] Line heights remain readable
- [ ] Padding/margins adapt to screen size
- [ ] Message bubbles maintain readability

### 4. Breakpoints to Test
```
1100px - Sidebar becomes mobile
768px  - Mobile phone layout
480px  - Small phone optimizations
```

### 5. Cross-Browser Testing
Test on:
- [ ] Chrome (Desktop & Android)
- [ ] Firefox (Desktop & Android)
- [ ] Safari (Desktop & iOS)
- [ ] Edge (Desktop)

### 6. PWA Testing
1. Chrome mobile: "Add to Home Screen"
2. Check icon appears correctly
3. Opens as standalone app
4. Theme color shows in status bar

### 7. Accessibility Testing
- [ ] Keyboard navigation works
- [ ] Focus states visible
- [ ] ARIA labels present
- [ ] Screen reader compatible
- [ ] Reduced motion respected

### 8. Performance Testing
- [ ] Animations are smooth (60fps)
- [ ] No layout shifts
- [ ] Scrolling is smooth
- [ ] Transitions don't lag

## Common Issues & Solutions

### Issue: Sidebar doesn't slide in
**Solution**: Clear browser cache and reload

### Issue: Buttons too small on mobile
**Solution**: Check if touch device CSS is loading

### Issue: Theme switch not working
**Solution**: Check localStorage access

### Issue: PWA won't install
**Solution**: Ensure HTTPS (or localhost) and manifest.json accessible

## Quick Visual Checklist

### Mobile (< 768px)
- ✅ Hamburger menu visible
- ✅ Sidebar slides from left
- ✅ Dark overlay when sidebar open
- ✅ Circular send button
- ✅ Settings stack vertically
- ✅ Proper touch targets

### Tablet (768px - 1100px)
- ✅ Sidebar still mobile mode
- ✅ More breathing room in layout
- ✅ Larger font sizes than phone

### Desktop (> 1100px)
- ✅ Sidebar visible inline
- ✅ Toggle collapses in place
- ✅ Full button text visible
- ✅ Hover effects active

## Performance Metrics

Target metrics:
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Time to Interactive: < 3.5s
- Cumulative Layout Shift: < 0.1

Test with Chrome DevTools Lighthouse!
