# iOS UI Components Reference

Standard SwiftUI component patterns following Apple Human Interface Guidelines.

## Buttons

### Button Styles

```swift
// Primary action - Filled, prominent
Button("Continue") { action() }
    .buttonStyle(.borderedProminent)

// Secondary action - Bordered
Button("Skip") { skip() }
    .buttonStyle(.bordered)

// Tertiary - Plain text
Button("Learn More") { info() }
    .buttonStyle(.plain)

// Destructive
Button("Delete", role: .destructive) { delete() }
    .buttonStyle(.bordered)

// Cancel
Button("Cancel", role: .cancel) { cancel() }
```

### Button Sizing

```swift
// Control size
Button("Small") { }
    .controlSize(.small)
    .buttonStyle(.bordered)

Button("Regular") { }
    .controlSize(.regular)
    .buttonStyle(.bordered)

Button("Large") { }
    .controlSize(.large)
    .buttonStyle(.bordered)

// Full width button
Button("Full Width") { }
    .buttonStyle(.borderedProminent)
    .frame(maxWidth: .infinity)
```

### Icon Buttons

```swift
// Icon only
Button {
    action()
} label: {
    Image(systemName: "plus")
}
.buttonStyle(.bordered)
.buttonBorderShape(.circle)

// Icon with label
Button {
    action()
} label: {
    Label("Add Item", systemImage: "plus")
}
.buttonStyle(.borderedProminent)
```

### Custom Button Styling

```swift
struct PrimaryButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(.white)
            .padding(.horizontal, 24)
            .padding(.vertical, 12)
            .background(Color.accentColor)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .opacity(configuration.isPressed ? 0.8 : 1.0)
    }
}

// Usage
Button("Custom") { }
    .buttonStyle(PrimaryButtonStyle())
```

## Text Fields

### Basic Text Fields

```swift
// Simple text field
TextField("Name", text: $name)

// With prompt
TextField("Email", text: $email, prompt: Text("you@example.com"))

// Secure field
SecureField("Password", text: $password)
```

### Text Field Styles

```swift
// Rounded border (default)
TextField("Search", text: $search)
    .textFieldStyle(.roundedBorder)

// Plain
TextField("Plain", text: $text)
    .textFieldStyle(.plain)
```

### Keyboard Types

```swift
TextField("Email", text: $email)
    .keyboardType(.emailAddress)
    .textContentType(.emailAddress)
    .autocapitalization(.none)

TextField("Phone", text: $phone)
    .keyboardType(.phonePad)
    .textContentType(.telephoneNumber)

TextField("URL", text: $url)
    .keyboardType(.URL)
    .textContentType(.URL)
    .autocapitalization(.none)
```

### Validation States

```swift
TextField("Email", text: $email)
    .textFieldStyle(.roundedBorder)
    .overlay(
        RoundedRectangle(cornerRadius: 8)
            .stroke(isValid ? Color.clear : Color.red, lineWidth: 1)
    )

if !isValid {
    Text("Invalid email address")
        .font(.caption)
        .foregroundStyle(.red)
}
```

## Pickers

### Standard Picker

```swift
Picker("Category", selection: $category) {
    ForEach(categories, id: \.self) { category in
        Text(category).tag(category)
    }
}

// Picker styles
.pickerStyle(.menu)          // Dropdown menu
.pickerStyle(.segmented)     // Segmented control
.pickerStyle(.wheel)         // Wheel picker
.pickerStyle(.inline)        // Inline list
```

### Date Picker

```swift
DatePicker("Date", selection: $date)

// Specific components
DatePicker("Time", selection: $time, displayedComponents: .hourAndMinute)
DatePicker("Date", selection: $date, displayedComponents: .date)

// Date picker styles
.datePickerStyle(.compact)   // Compact button
.datePickerStyle(.graphical) // Calendar view
.datePickerStyle(.wheel)     // Wheel picker
```

### Color Picker

```swift
ColorPicker("Color", selection: $color)
ColorPicker("Color", selection: $color, supportsOpacity: false)
```

## Toggles and Sliders

### Toggle

```swift
Toggle("Notifications", isOn: $isEnabled)

// Toggle styles
Toggle("Option", isOn: $isOn)
    .toggleStyle(.switch)  // Default switch

Toggle("Option", isOn: $isOn)
    .toggleStyle(.button)  // Button style
```

### Slider

```swift
Slider(value: $volume, in: 0...100)

// With labels
Slider(value: $volume, in: 0...100) {
    Text("Volume")
} minimumValueLabel: {
    Image(systemName: "speaker")
} maximumValueLabel: {
    Image(systemName: "speaker.wave.3")
}

// With step
Slider(value: $value, in: 0...10, step: 1)
```

### Stepper

```swift
Stepper("Quantity: \(quantity)", value: $quantity, in: 1...10)

// Custom increment
Stepper("Value", value: $value, in: 0...100, step: 5)
```

## Progress Indicators

### Indeterminate

```swift
ProgressView()
ProgressView("Loading...")
```

### Determinate

```swift
ProgressView(value: progress)
ProgressView(value: progress, total: 100)

// With label
ProgressView(value: progress) {
    Text("Downloading...")
} currentValueLabel: {
    Text("\(Int(progress * 100))%")
}
```

### Progress View Styles

```swift
ProgressView()
    .progressViewStyle(.circular)

ProgressView(value: 0.5)
    .progressViewStyle(.linear)
```

## Lists

### Basic List

```swift
List {
    Text("Item 1")
    Text("Item 2")
    Text("Item 3")
}
```

### List with Sections

```swift
List {
    Section("Section 1") {
        Text("Item 1")
        Text("Item 2")
    }

    Section {
        Text("Item 3")
    } header: {
        Text("Section 2")
    } footer: {
        Text("Footer text")
    }
}
```

### List Styles

```swift
List { }
    .listStyle(.automatic)       // Platform default
    .listStyle(.insetGrouped)    // Grouped with inset
    .listStyle(.grouped)         // Grouped
    .listStyle(.plain)           // Plain list
    .listStyle(.sidebar)         // Sidebar style
```

### List Row Configuration

```swift
List {
    ForEach(items) { item in
        Text(item.name)
            .listRowBackground(Color.clear)
            .listRowSeparator(.hidden)
            .listRowInsets(EdgeInsets(top: 8, leading: 16, bottom: 8, trailing: 16))
    }
}
```

### Swipe Actions

```swift
List {
    ForEach(items) { item in
        Text(item.name)
            .swipeActions(edge: .trailing) {
                Button(role: .destructive) {
                    delete(item)
                } label: {
                    Label("Delete", systemImage: "trash")
                }

                Button {
                    archive(item)
                } label: {
                    Label("Archive", systemImage: "archivebox")
                }
                .tint(.orange)
            }
    }
}
```

## Forms

### Basic Form

```swift
Form {
    Section("Personal Info") {
        TextField("Name", text: $name)
        TextField("Email", text: $email)
    }

    Section("Preferences") {
        Toggle("Notifications", isOn: $notifications)
        Picker("Theme", selection: $theme) {
            Text("Light").tag("light")
            Text("Dark").tag("dark")
            Text("System").tag("system")
        }
    }

    Section {
        Button("Save") {
            save()
        }
    }
}
```

### Form Labels

```swift
Form {
    LabeledContent("Username") {
        Text("@johndoe")
    }

    LabeledContent("Status") {
        Text("Active")
            .foregroundStyle(.green)
    }
}
```

## Sheets and Modals

### Sheet

```swift
.sheet(isPresented: $showSheet) {
    SheetContent()
}

// With detents (iOS 16+)
.sheet(isPresented: $showSheet) {
    SheetContent()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

### Full Screen Cover

```swift
.fullScreenCover(isPresented: $showCover) {
    FullScreenContent()
}
```

### Alert

```swift
.alert("Title", isPresented: $showAlert) {
    Button("OK") { }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("Alert message")
}
```

### Confirmation Dialog

```swift
.confirmationDialog("Options", isPresented: $showOptions) {
    Button("Option 1") { }
    Button("Option 2") { }
    Button("Delete", role: .destructive) { }
    Button("Cancel", role: .cancel) { }
}
```

## Menus

### Context Menu

```swift
Text("Long press me")
    .contextMenu {
        Button {
            copy()
        } label: {
            Label("Copy", systemImage: "doc.on.doc")
        }

        Button {
            share()
        } label: {
            Label("Share", systemImage: "square.and.arrow.up")
        }

        Divider()

        Button(role: .destructive) {
            delete()
        } label: {
            Label("Delete", systemImage: "trash")
        }
    }
```

### Menu Button

```swift
Menu {
    Button("Option 1") { }
    Button("Option 2") { }

    Menu("Submenu") {
        Button("Sub 1") { }
        Button("Sub 2") { }
    }
} label: {
    Label("Menu", systemImage: "ellipsis.circle")
}
```

## Toolbars

### Navigation Toolbar

```swift
.toolbar {
    ToolbarItem(placement: .navigationBarLeading) {
        Button("Cancel") { cancel() }
    }

    ToolbarItem(placement: .navigationBarTrailing) {
        Button("Save") { save() }
    }
}
```

### Bottom Toolbar

```swift
.toolbar {
    ToolbarItemGroup(placement: .bottomBar) {
        Button { } label: {
            Image(systemName: "square.and.arrow.up")
        }

        Spacer()

        Button { } label: {
            Image(systemName: "trash")
        }
    }
}
```

### Keyboard Toolbar

```swift
TextField("Input", text: $text)
    .toolbar {
        ToolbarItemGroup(placement: .keyboard) {
            Spacer()
            Button("Done") {
                hideKeyboard()
            }
        }
    }
```

## Empty States

```swift
ContentUnavailableView {
    Label("No Results", systemImage: "magnifyingglass")
} description: {
    Text("Try searching for something else.")
} actions: {
    Button("Clear Filters") {
        clearFilters()
    }
}
```

## Cards

```swift
struct CardView<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        content
            .padding()
            .background(Color(.secondarySystemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

// Usage
CardView {
    VStack(alignment: .leading) {
        Text("Card Title")
            .font(.headline)
        Text("Card content")
            .font(.body)
    }
}
```

## Badges

```swift
// Tab badge
TabView {
    InboxView()
        .tabItem {
            Label("Inbox", systemImage: "tray")
        }
        .badge(5)
}

// List badge
List {
    Text("Messages")
        .badge(10)
}
```
