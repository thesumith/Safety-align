# PDF Viewer Feature for RSI Comparison Tool

## Overview

The RSI Comparison Tool now includes a powerful **PDF Viewer** feature that allows users to view and compare the original PDF documents side by side. This feature complements the existing split view and full view modes, providing a visual comparison of the actual PDF documents with synchronized scrolling and visual indicators for differences.

## Features

### 🎯 PDF Side-by-Side Comparison
- View both comparator and our RSI PDFs simultaneously
- Synchronized zoom controls for easy comparison
- Independent zoom controls for detailed inspection
- Responsive design that works on desktop and mobile devices

### 🔧 Interactive Controls
- **Zoom Controls**: Adjust zoom level from 50% to 300%
- **Sync Zoom**: Keep both PDFs at the same zoom level for synchronized viewing
- **Reset Zoom**: Quickly return to 100% zoom
- **Download**: Download individual PDF files
- **Toggle Controls**: Show/hide control panel
- **Synchronized Scrolling**: Real-time sync when scrolling in one viewer
- **Section Navigation**: Quick access to specific sections with visual indicators

### 📱 Responsive Design
- Desktop: Side-by-side PDF viewing
- Mobile: Stacked PDF viewing for better mobile experience
- Dark mode support for better viewing experience
- Fullscreen mode for immersive viewing

### 🎨 Visual Difference Indicators
- **Color Coding**: Sections are color-coded based on similarity scores:
  - 🟢 Green: High similarity (≥80%)
  - 🟡 Yellow: Medium similarity (60-79%)
  - 🔴 Red: Low similarity (<60%)
- **Alert Messages**: Warning messages for sections with differences
- **Section Headers**: Clear section identification with SmPC numbering

## How to Use

### 1. Upload PDFs
- Upload your comparator RSI (reference document)
- Upload your RSI (document under review)

### 2. Run Comparison
- Click "Start Comparison" to process the documents
- Wait for the comparison to complete

### 3. Access PDF View
- After comparison, you'll see the results
- Click the **"PDF View"** or **"Show PDF View"** button in the view controls
- The PDF viewer will load both documents side by side

### 4. Navigate and Compare
- Use the zoom controls to adjust the view
- Enable "Sync Zoom" to keep both PDFs at the same zoom level
- Scroll within each PDF frame to navigate through the documents
- Use the download button to save individual PDFs
- Click section buttons to jump to specific sections
- Toggle synchronized scrolling for coordinated viewing

## Technical Implementation

### Frontend Components

#### PDFViewer.js
- Main component for PDF display
- Handles zoom controls and synchronization
- Manages PDF loading states and error handling
- Provides responsive layout for different screen sizes
- Implements synchronized scrolling logic
- Section navigation with visual indicators

#### ComparisonView.js
- Updated to include PDF view mode
- Integrates PDFViewer component
- Maintains existing split view and full view functionality

#### ResultsDisplay.js
- Integrated PDF viewer functionality
- Section navigation with similarity scores
- Visual difference indicators

### Backend API

#### New Endpoints
- `GET /api/pdf/comparator?output_dir=<dir>` - Serves comparator PDF
- `GET /api/pdf/our?output_dir=<dir>` - Serves our RSI PDF

#### File Management
- Original PDFs are saved to output directory during comparison
- Files are served with proper MIME types for browser viewing
- Automatic cleanup of temporary files

### CSS Styling
- Modern, responsive design with gradient headers
- Smooth animations and transitions using Framer Motion
- Dark mode support
- Mobile-first responsive design
- Color-coded section indicators

## File Structure

```
react-frontend/components/
├── PDFViewer.js          # Main PDF viewer component
├── PDFViewer.css         # PDF viewer styles
├── ComparisonView.js     # Updated with PDF view mode
├── ComparisonView.css    # Updated with PDF view styles
└── ResultsDisplay.js     # Integrated with PDF viewer

temp-react-app/src/components/
├── PDFViewer.js          # Copied for temp-react-app
├── PDFViewer.css         # Copied for temp-react-app
├── ComparisonView.js     # Updated with PDF view mode
└── ComparisonView.css    # Updated with PDF view styles
```

## Data Structure

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

The PDF viewer uses iframe-based PDF display, which is supported by:
- Chrome/Chromium browsers
- Firefox
- Safari
- Edge
- Mobile browsers with responsive design

### PDF Display Methods
1. **Native PDF Viewer**: Most modern browsers display PDFs natively
2. **Fallback**: If native viewing is not available, users can download the PDFs

## Security Considerations

- PDFs are served from the same domain to prevent CORS issues
- Files are served with appropriate MIME types
- Temporary files are cleaned up after processing
- No sensitive data is stored permanently

## Performance Optimizations

- PDFs are loaded on-demand when PDF view is selected
- Zoom controls use CSS transforms for smooth performance
- Loading states provide user feedback
- Error handling prevents application crashes
- Efficient scroll event handling
- Proper cleanup of event listeners
- Optimized React rendering with proper keys

## Future Enhancements

Potential improvements for the PDF viewer:
- PDF annotation capabilities
- Side-by-side text highlighting
- Page-by-page navigation controls
- PDF search functionality
- Export annotated PDFs
- Custom PDF viewer with more controls
- Text highlighting for specific differences within sections
- Export options for side-by-side view as PDF
- Annotation tools for adding notes and comments
- Keyboard navigation shortcuts

## Troubleshooting

### Common Issues

1. **PDFs not loading**
   - Check if the comparison was completed successfully
   - Verify the output directory exists
   - Check browser console for errors

2. **Zoom controls not working**
   - Ensure JavaScript is enabled
   - Try refreshing the page
   - Check for browser compatibility

3. **Mobile display issues**
   - The viewer automatically switches to stacked view on mobile
   - Ensure proper viewport settings

4. **Synchronized scrolling not working**
   - Ensure both viewers have scrollable content
   - Check if sync toggle is enabled
   - Verify browser supports scroll events

### Debug Mode

To enable debug mode, check the browser console for detailed error messages and loading states.

## Dependencies

The PDF viewer feature uses:
- React 18.2.0+
- Framer Motion for animations
- React Icons for UI icons
- CSS Grid and Flexbox for layout
- Modern browser APIs for PDF display

No additional PDF libraries are required as the feature uses native browser PDF viewing capabilities.
