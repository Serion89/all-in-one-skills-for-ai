---
name: react-native-patterns
description: Production React Native and Expo cross-platform mobile patterns. Use when building mobile apps, optimizing the Hermes JS engine, implementing smooth gesture animations with Reanimated, handling offline state sync, and native bridge performance.
---

# React Native & Cross-Platform Mobile Engineering

## Purpose
Architect robust, smooth 60/120 FPS cross-platform mobile applications for iOS and Android using React Native and Expo.

---

## Core Performance & Architecture Directives

### 1. Hermes Engine & Memory Management
- Run the **Hermes** JavaScript engine by default for precompiled bytecode, faster TTI, and lower memory footprint.
- Avoid large anonymous object/array allocations inside render paths or list render item functions.

### 2. High-Performance Lists (FlashList)
Replace legacy React Native `FlatList` with Shopify's `FlashList` for heavy feeds:
- Reuses underlying native views (view recycling) instead of destroying and recreating DOM nodes on scroll.
- Mandate `estimatedItemSize` on every list instance.

### 3. Native Gesture & Animation Threading (Reanimated 3)
Never animate layout properties (`width`, `height`, `top`) across the asynchronous JavaScript bridge:
- Run all animations and gesture responders on the native UI thread using `react-native-reanimated` and `react-native-gesture-handler`:
```javascript
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';

export function AnimatedCard() {
  const scale = useSharedValue(1);
  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: withSpring(scale.value) }],
  }));

  return <Animated.View style={[styles.card, animatedStyle]} />;
}
```

### 4. Offline First & Network Resilience
- Cache local application state in fast native SQLite or MMKV (avoid slow asynchronous `AsyncStorage` on critical startup paths).
- Implement background synchronization queues with exponential retry for offline mutations.
