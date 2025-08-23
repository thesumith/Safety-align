# PDF Viewer Feature for RSI Comparison Tool

## Overview

The RSI Comparison Tool now includes a **PDF Viewer** feature that allows users to view and compare the original PDF documents side by side. This feature complements the existing split view and full view modes, providing a visual comparison of the actual PDF documents.

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

### 📱 Responsive Design
- Desktop: Side-by-side PDF viewing
- Mobile: Stacked PDF viewing for better mobile experience
- Dark mode support for better viewing experience

## How to Use

### 1. Upload PDFs
- Upload your comparator RSI (reference document)
- Upload your RSI (document under review)

### 2. Run Comparison
- Click "Start Comparison" to process the documents
- Wait for the comparison to complete

### 3. Access PDF View
- After comparison, you'll see the results
- Click the **"PDF View"** button in the view controls
- The PDF viewer will load both documents side by side

### 4. Navigate and Compare
- Use the zoom controls to adjust the view
- Enable "Sync Zoom" to keep both PDFs at the same zoom level
- Scroll within each PDF frame to navigate through the documents
- Use the download button to save individual PDFs

## Technical Implementation

### Frontend Components

#### PDFViewer.js
- Main component for PDF display
- Handles zoom controls and synchronization
- Manages PDF loading states and error handling
- Provides responsive layout for different screen sizes

#### ComparisonView.js
- Updated to include PDF view mode
- Integrates PDFViewer component
- Maintains existing split view and full view functionality

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
- Smooth animations and transitions
- Dark mode support
- Mobile-first responsive design

## File Structure

```
react-frontend/components/
├── PDFViewer.js          # Main PDF viewer component
├── PDFViewer.css         # PDF viewer styles
├── ComparisonView.js     # Updated with PDF view mode
└── ComparisonView.css    # Updated with PDF view styles

temp-react-app/src/components/
├── PDFViewer.js          # Copied for temp-react-app
├── PDFViewer.css         # Copied for temp-react-app
├── ComparisonView.js     # Updated with PDF view mode
└── ComparisonView.css    # Updated with PDF view styles
```

## Browser Compatibility

The PDF viewer uses iframe-based PDF display, which is supported by:
- Chrome/Chromium browsers
- Firefox
- Safari
- Edge

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

## Future Enhancements

Potential improvements for the PDF viewer:
- PDF annotation capabilities
- Side-by-side text highlighting
- Page-by-page navigation controls
- PDF search functionality
- Export annotated PDFs
- Custom PDF viewer with more controls

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
