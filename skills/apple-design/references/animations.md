# iOS Motion Design Guidelines

Animation and motion design principles following Apple Human Interface Guidelines.

## Core Principles

### 1. Purpose
Animations should enhance understanding and provide feedback:
- Guide attention to important changes
- Reinforce spatial relationships
- Provide feedback for actions
- Create continuity between states

### 2. Subtlety
Animations should be smooth and unobtrusive:
- Avoid excessive bouncing or overshooting
- Keep durations appropriate
- Don't animate for animation's sake

### 3. Responsiveness
Animations must feel immediate:
- Start instantly on user input
- Never block user interaction
- Allow interruption when appropriate

## Standard Timing

### Duration Guidelines

| Type | Duration | Usage |
|------|----------|-------|
| Micro | 0.1-0.2s | Button presses, toggles |
| Short | 0.2-0.3s | Small UI changes |
| Medium | 0.3-0.5s | View transitions |
| Long | 0.5-1.0s | Complex reveals |

### SwiftUI Default Animations

```swift
// Default (0.35s ease-in-out)
withAnimation {
    state.toggle()
}

// Explicit default
withAnimation(.default) {
    state.toggle()
}
```

## Animation Types

### Basic Animations

```swift
// Linear (constant speed)
withAnimation(.linear(duration: 0.3)) {
    position = newPosition
}

// Ease In (starts slow)
withAnimation(.easeIn(duration: 0.3)) {
    opacity = 0
}

// Ease Out (ends slow)
withAnimation(.easeOut(duration: 0.3)) {
    opacity = 1
}

// Ease In Out (slow start and end)
withAnimation(.easeInOut(duration: 0.3)) {
    scale = 1.0
}
```

### Spring Animations

Recommended for natural-feeling motion:

```swift
// Default spring
withAnimation(.spring()) {
    isExpanded.toggle()
}

// Custom spring parameters
withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
    offset = newOffset
}

// Bouncy spring (use sparingly)
withAnimation(.spring(response: 0.3, dampingFraction: 0.5)) {
    scale = 1.2
}

// Interactive spring
withAnimation(.interactiveSpring(response: 0.3, dampingFraction: 0.7)) {
    dragOffset = .zero
}
```

### Spring Parameters

| Parameter | Range | Effect |
|-----------|-------|--------|
| `response` | 0.1-1.0 | Speed (lower = faster) |
| `dampingFraction` | 0-1.0 | Bounciness (lower = more bounce) |

Recommended values:
- **Snappy**: response: 0.3, damping: 0.8
- **Gentle**: response: 0.5, damping: 0.7
- **Bouncy**: response: 0.4, damping: 0.5

## Implicit vs Explicit Animations

### Implicit Animation

Animate when value changes:

```swift
struct AnimatedView: View {
    @State private var isExpanded = false

    var body: some View {
        Rectangle()
            .frame(height: isExpanded ? 200 : 100)
            .animation(.spring(), value: isExpanded)
            .onTapGesture {
                isExpanded.toggle()
            }
    }
}
```

### Explicit Animation

Control animation timing:

```swift
Button("Animate") {
    withAnimation(.spring()) {
        isExpanded.toggle()
    }
}
```

## View Transitions

### Built-in Transitions

```swift
// Opacity
if showView {
    ContentView()
        .transition(.opacity)
}

// Scale
if showView {
    ContentView()
        .transition(.scale)
}

// Slide
if showView {
    ContentView()
        .transition(.slide)
}

// Move
if showView {
    ContentView()
        .transition(.move(edge: .bottom))
}

// Push (iOS 16+)
if showView {
    ContentView()
        .transition(.push(from: .trailing))
}
```

### Combined Transitions

```swift
// Scale with opacity
.transition(.scale.combined(with: .opacity))

// Asymmetric (different in/out)
.transition(.asymmetric(
    insertion: .scale.combined(with: .opacity),
    removal: .opacity
))
```

### Custom Transitions

```swift
extension AnyTransition {
    static var slideUp: AnyTransition {
        .asymmetric(
            insertion: .move(edge: .bottom).combined(with: .opacity),
            removal: .move(edge: .top).combined(with: .opacity)
        )
    }
}

// Usage
ContentView()
    .transition(.slideUp)
```

## Navigation Transitions

### NavigationStack (iOS 16+)

```swift
NavigationStack {
    List {
        NavigationLink("Detail", value: item)
    }
    .navigationDestination(for: Item.self) { item in
        DetailView(item: item)
    }
}
```

### Custom Navigation Transition (iOS 18+)

```swift
NavigationStack {
    ContentView()
        .navigationTransition(.zoom(sourceID: item.id, in: namespace))
}
```

### Sheet Transitions

```swift
.sheet(isPresented: $showSheet) {
    SheetContent()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

## Gesture-Driven Animation

### Drag Gesture

```swift
struct DraggableView: View {
    @State private var offset = CGSize.zero
    @State private var isDragging = false

    var body: some View {
        Circle()
            .offset(offset)
            .scaleEffect(isDragging ? 1.1 : 1.0)
            .animation(.spring(), value: isDragging)
            .gesture(
                DragGesture()
                    .onChanged { value in
                        offset = value.translation
                        isDragging = true
                    }
                    .onEnded { _ in
                        withAnimation(.spring()) {
                            offset = .zero
                            isDragging = false
                        }
                    }
            )
    }
}
```

### Scroll-Driven Animation

```swift
ScrollView {
    ForEach(items) { item in
        ItemView(item: item)
            .scrollTransition { content, phase in
                content
                    .opacity(phase.isIdentity ? 1 : 0.5)
                    .scaleEffect(phase.isIdentity ? 1 : 0.9)
            }
    }
}
```

## Phase Animations

### Phase Animator (iOS 17+)

```swift
PhaseAnimator([false, true]) { phase in
    Circle()
        .scaleEffect(phase ? 1.2 : 1.0)
        .opacity(phase ? 0.5 : 1.0)
}
```

### Keyframe Animations (iOS 17+)

```swift
KeyframeAnimator(initialValue: AnimationState()) { value in
    Circle()
        .offset(y: value.verticalOffset)
        .scaleEffect(value.scale)
} keyframes: { _ in
    KeyframeTrack(\.verticalOffset) {
        LinearKeyframe(-50, duration: 0.2)
        SpringKeyframe(0, duration: 0.5)
    }

    KeyframeTrack(\.scale) {
        LinearKeyframe(0.8, duration: 0.1)
        SpringKeyframe(1.0, duration: 0.3)
    }
}
```

## Matched Geometry Effect

Create hero transitions:

```swift
struct HeroTransition: View {
    @Namespace private var namespace
    @State private var isExpanded = false

    var body: some View {
        VStack {
            if isExpanded {
                ExpandedView()
                    .matchedGeometryEffect(id: "hero", in: namespace)
            } else {
                ThumbnailView()
                    .matchedGeometryEffect(id: "hero", in: namespace)
            }
        }
        .onTapGesture {
            withAnimation(.spring()) {
                isExpanded.toggle()
            }
        }
    }
}
```

## Symbol Animations (iOS 17+)

```swift
// Bounce
Image(systemName: "star.fill")
    .symbolEffect(.bounce, value: count)

// Pulse
Image(systemName: "wifi")
    .symbolEffect(.pulse)

// Variable color
Image(systemName: "speaker.wave.3")
    .symbolEffect(.variableColor.iterative)

// Replace
Image(systemName: isPlaying ? "pause.fill" : "play.fill")
    .contentTransition(.symbolEffect(.replace))

// Scale
Image(systemName: "heart.fill")
    .symbolEffect(.scale.up, isActive: isLiked)
```

## Accessibility

### Reduce Motion

Always respect the Reduce Motion setting:

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var body: some View {
    Circle()
        .offset(y: offset)
        .animation(reduceMotion ? nil : .spring(), value: offset)
}

// Or use conditional animation
withAnimation(reduceMotion ? nil : .spring()) {
    isExpanded.toggle()
}
```

### Alternative for Reduced Motion

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

var body: some View {
    if showContent {
        ContentView()
            .transition(reduceMotion ? .opacity : .slide)
    }
}
```

## Performance Best Practices

### Do:
- Animate transform properties (scale, rotation, offset)
- Use implicit animations for simple cases
- Batch related animations together
- Test on actual devices

### Don't:
- Animate complex view hierarchies
- Use long durations (>1s)
- Animate during scrolling
- Animate many views simultaneously

### Optimize for Performance

```swift
// Prefer drawingGroup for complex shapes
ComplexShape()
    .drawingGroup()
    .animation(.spring(), value: state)

// Use fixed sizes when possible
AnimatedView()
    .frame(width: 200, height: 200)
```

## Common Patterns

### Button Press

```swift
struct PressableButton: View {
    @State private var isPressed = false

    var body: some View {
        Text("Press Me")
            .padding()
            .background(Color.accentColor)
            .scaleEffect(isPressed ? 0.95 : 1.0)
            .animation(.easeOut(duration: 0.1), value: isPressed)
            .onLongPressGesture(minimumDuration: .infinity, pressing: { pressing in
                isPressed = pressing
            }, perform: { })
            .simultaneousGesture(
                TapGesture().onEnded { action() }
            )
    }
}
```

### Loading Spinner

```swift
struct LoadingSpinner: View {
    @State private var isAnimating = false

    var body: some View {
        Circle()
            .trim(from: 0, to: 0.7)
            .stroke(Color.accentColor, lineWidth: 3)
            .rotationEffect(.degrees(isAnimating ? 360 : 0))
            .animation(
                .linear(duration: 1)
                .repeatForever(autoreverses: false),
                value: isAnimating
            )
            .onAppear {
                isAnimating = true
            }
    }
}
```

### Card Flip

```swift
struct FlippableCard: View {
    @State private var isFlipped = false

    var body: some View {
        ZStack {
            FrontView()
                .opacity(isFlipped ? 0 : 1)
                .rotation3DEffect(.degrees(isFlipped ? 180 : 0), axis: (0, 1, 0))

            BackView()
                .opacity(isFlipped ? 1 : 0)
                .rotation3DEffect(.degrees(isFlipped ? 0 : -180), axis: (0, 1, 0))
        }
        .onTapGesture {
            withAnimation(.spring()) {
                isFlipped.toggle()
            }
        }
    }
}
```

### Pull to Refresh

```swift
List {
    ForEach(items) { item in
        ItemRow(item: item)
    }
}
.refreshable {
    await loadData()
}
```
