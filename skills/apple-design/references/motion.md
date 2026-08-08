# Motion (iOS 26+)

Most motion in a well-built iOS 26 app comes from the system. Liquid Glass has its own
fluid behavior: it responds with greater emphasis to direct touch than to a trackpad, morphs
between shapes during transitions, and adapts when accessibility settings change. Standard
components give you all of that for free.

Design custom motion only where the system doesn't already speak.

## Principles

**Purposeful.** Motion should convey status, give feedback, or clarify a spatial
relationship. Gratuitous animation distracts and can cause physical discomfort.

**Optional.** Never make motion the only channel for important information. Pair it with
haptics, audio, or text.

**Reversible and honest.** If a view arrives by sliding down from the top, it should leave
by sliding back up. Feedback that contradicts the gesture disorients people.

**Brief and precise.** Short, tightly-coupled feedback communicates more effectively than a
prominent animation, and it stays out of the way.

**Interruptible.** Don't make people wait for an animation to finish before they can act —
especially an animation they'll see repeatedly.

**Restrained on frequent interactions.** The system already animates standard controls.
Adding your own to something people touch dozens of times a session just costs them time.

## SwiftUI animation

```swift
withAnimation(.smooth) { isExpanded.toggle() }

// Spring presets
.animation(.smooth,  value: state)   // no bounce
.animation(.snappy,  value: state)   // slight bounce, responsive
.animation(.bouncy,  value: state)   // pronounced bounce

// Tuned spring
.animation(.spring(response: 0.4, dampingFraction: 0.8), value: state)

// Duration-based, for simple property changes
.animation(.easeInOut(duration: 0.25), value: opacity)
```

Rough durations when you need explicit numbers:

| Kind | Duration |
|---|---|
| Micro-feedback (press, toggle) | 0.1–0.2 s |
| Small UI change | 0.2–0.3 s |
| View transition | 0.3–0.5 s |
| Complex reveal | 0.5–1.0 s |

Prefer the spring presets over hand-tuned durations — they match system behavior and stay
correct as the platform evolves.

## Glass transitions

Glass morphing is the signature motion of iOS 26. See `liquid-glass.md` for the full API;
in short:

```swift
GlassEffectContainer(spacing: 40) {
    // views with .glassEffect() and .glassEffectID(_:in:)
}
```

- `.matchedGeometry` — default; shapes morph into each other when within the container's
  spacing
- `.materialize` — for effects farther apart than the container spacing, or a simpler
  transition

Set via `glassEffectTransition(_:)`. Use these two consistently so the experience matches
the rest of the system. Both only apply during view-hierarchy transitions and animations.

**iOS 27:** sheets can use the `crossFade` transition to fade in over content instead of
sliding up.

## Matched geometry

```swift
@Namespace private var namespace

// Source
Thumbnail(item)
    .matchedGeometryEffect(id: item.id, in: namespace)

// Destination
DetailHero(item)
    .matchedGeometryEffect(id: item.id, in: namespace)
```

## Symbol animation

Symbol effects are usually the right amount of motion for state changes.

```swift
Image(systemName: "bell").symbolEffect(.bounce, value: unreadCount)
Image(systemName: "arrow.clockwise").symbolEffect(.rotate, isActive: isRefreshing)
Image(systemName: "checkmark.circle").symbolEffect(.drawOn, isActive: isComplete)

Image(systemName: isPlaying ? "pause.fill" : "play.fill")
    .contentTransition(.symbolEffect(.replace))
```

Guidelines from the Controls HIG that generalize well:
- For a toggle, animate the transition in **both** directions.
- For an action with a duration, animate indefinitely while it runs; stop on completion.

## Reduce Motion

```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion

withAnimation(reduceMotion ? nil : .snappy) {
    isExpanded.toggle()
}
```

Standard components adapt automatically. Any custom animation you write must check this —
particularly parallax, large-scale movement, zoom, and anything that fills a large portion
of the screen.

Reduce Motion also modifies Liquid Glass's fluid morphing, so verify custom glass under it.

## Haptics

Haptics are the non-visual half of feedback. Pair them with audio cues so people who can't
hear (or have sound off) still get the signal — and pair audio with visuals for the reverse.

```swift
.sensoryFeedback(.success, trigger: didSave)
.sensoryFeedback(.impact(weight: .light), trigger: selectionIndex)
.sensoryFeedback(.selection, trigger: selectedTab)
```

Use the semantic feedback types rather than raw impact generators where one fits — they
convey meaning and adapt across devices.
