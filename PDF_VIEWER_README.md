# PDF Viewer Feature Documentation

## Overview

The RSI Comparison Tool now includes a powerful side-by-side PDF viewer that allows users to compare two RSI documents with synchronized scrolling and visual indicators for differences.

## Features

### 1. Side-by-Side View
- **Split Layout**: Two PDF viewers side by side showing the comparator RSI and our RSI
- **Responsive Design**: Automatically adjusts to single column on smaller screens
- **Fullscreen Mode**: Toggle fullscreen for better viewing experience

### 2. Synchronized Scrolling
- **Real-time Sync**: When you scroll in one viewer, the other automatically scrolls to the same relative position
- **Toggle Control**: Enable/disable synchronized scrolling with the sync button
- **Smart Detection**: Only syncs when both viewers have scrollable content

### 3. Section Navigation
- **Quick Access**: Navigate directly to specific sections using the section buttons
- **Visual Indicators**: Each section button shows the similarity score with color coding
- **SMPC Order**: Sections are organized in the standard SmPC order (4.1, 4.3, 4.4, etc.)

### 4. Visual Difference Indicators
- **Color Coding**: Sections are color-coded based on similarity scores:
  - 🟢 Green: High similarity (≥80%)
  - 🟡 Yellow: Medium similarity (60-79%)
  - 🔴 Red: Low similarity (<60%)
- **Alert Messages**: Warning messages for sections with differences
- **Section Headers**: Clear section identification with SmPC numbering

### 5. Content Display
- **Formatted Text**: Clean, readable text presentation
- **Section Metadata**: Shows section numbers and similarity scores
- **Missing Content**: Graceful handling of missing sections

## How to Use

### Accessing the PDF Viewer
1. Upload two PDF files for comparison
2. Wait for the analysis to complete
3. Click the "Show PDF View" button in the results header
4. The side-by-side viewer will appear below the summary

### Navigation
- **Scroll**: Use mouse wheel or scroll bars to navigate through content
- **Section Buttons**: Click any section button to jump to that section
- **Sync Toggle**: Use the sync button to enable/disable synchronized scrolling
- **Fullscreen**: Click the fullscreen button for immersive viewing

### Understanding the Display
- **Left Panel**: Comparator RSI (reference document)
- **Right Panel**: Our RSI (target document)
- **Section Headers**: Show section name, SmPC number, and similarity score
- **Alert Messages**: Appear for sections with differences
- **Color Borders**: Indicate similarity levels

## Technical Implementation

### Components
- `PDFViewer.js`: Main viewer component
- `PDFViewer.css`: Styling for the viewer
- Integrated into `ResultsDisplay.js`

### Key Features
- **React Hooks**: Uses useState, useRef, and useEffect for state management
- **Framer Motion**: Smooth animations and transitions
- **Responsive Design**: CSS Grid and Flexbox for layout
- **Event Handling**: Custom scroll synchronization logic

### Data Structure
The viewer expects the following data structure:
```javascript
{
  detailed_results: {
    section_name: {
      similarity_score: 0.85,
      // other comparison data
    }
  },
  comparator_sections: {
    section_name: {
      content: "section text content",
      // other section data
    }
  },
  our_sections: {
    section_name: {
      content: "section text content",
      // other section data
    }
  },
  summary: {
    overall_similarity: 0.75,
    total_sections_compared: 8,
    sections_with_issues: 2
  }
}
```

## Browser Compatibility

- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile Support**: Responsive design for tablets and phones
- **Fullscreen API**: Supported in all modern browsers

## Performance Considerations

- **Lazy Loading**: Content is loaded as needed
- **Efficient Scrolling**: Optimized scroll event handling
- **Memory Management**: Proper cleanup of event listeners
- **Rendering**: Efficient React rendering with proper keys

## Future Enhancements

Potential improvements for future versions:
- **Text Highlighting**: Highlight specific differences within sections
- **Search Functionality**: Search for specific terms across both documents
- **Export Options**: Export the side-by-side view as PDF
- **Annotation Tools**: Add notes and comments to sections
- **Zoom Controls**: Adjust text size for better readability
- **Keyboard Navigation**: Keyboard shortcuts for navigation
