// Create and inject the PDF embed button
function createPdfEmbedButton() {
    // Find the existing upload button container
    const uploadButton = document.querySelector('[data-element-id="upload-document-button"]');
    if (!uploadButton || uploadButton.parentElement.querySelector('#pdf-embed-button')) return;

    // Create the new button with the same styling
    const pdfButton = document.createElement('button');
    pdfButton.id = 'pdf-embed-button';
    pdfButton.className = uploadButton.className; // Copy existing button's classes
    pdfButton.setAttribute('data-tooltip-content', 'Embed PDF (Claude)');
    pdfButton.setAttribute('data-tooltip-id', 'global');
    
    // Add PDF icon (using a simple SVG for PDF)
    pdfButton.innerHTML = `
        <svg class="w-5 h-5" width="18px" height="18px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path fill="currentColor" d="M12 16H8V8h4a4 4 0 0 1 0 8zm-6 0V8H4v8h2zm12 0V8h-2v8h2zm3 4V4H3v16h18z"/>
        </svg>
    `;

    // Create hidden file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.pdf';
    fileInput.style.display = 'none';
    pdfButton.appendChild(fileInput);

    // Add click handler
    pdfButton.addEventListener('click', () => fileInput.click());

    // Add file change handler
    fileInput.addEventListener('change', handlePdfSelection);

    // Insert the new button after the upload button
    uploadButton.parentElement.insertBefore(pdfButton, uploadButton.nextSibling);
}

// Handle PDF file selection
async function handlePdfSelection(event) {
    const file = event.target.files[0];
    if (!file || file.type !== 'application/pdf') return;

    try {
        // Read file as Base64
        const base64String = await readFileAsBase64(file);
        
        // Store in IndexedDB
        await storePdfInDatabase(file.name, base64String);
        
        // Log for debugging
        console.log('PDF stored in database:', file.name);
        
        // Optional: Show success message
        showNotification(`PDF "${file.name}" stored successfully`);
    } catch (error) {
        console.error('Error handling PDF:', error);
        showNotification('Error storing PDF', 'error');
    }
}

// Read file as Base64
function readFileAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            // Remove the data URL prefix (data:application/pdf;base64,)
            const base64String = reader.result.split(',')[1];
            resolve(base64String);
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Store PDF in IndexedDB
async function storePdfInDatabase(filename, base64String) {
    // Get the current chat ID
    const chatId = getCurrentChatId();
    
    // Create PDF metadata
    const pdfData = {
        filename,
        base64String,
        timestamp: Date.now(),
        chatId
    };

    // Store in IndexedDB
    const db = await openDatabase();
    const transaction = db.transaction(['pdfs'], 'readwrite');
    const store = transaction.objectStore('pdfs');
    await store.add(pdfData);
}

// Get current chat ID from TypingMind
function getCurrentChatId() {
    // This is a placeholder - we need to find the actual way TypingMind stores the current chat ID
    // You might find it in localStorage or window.__NEXT_DATA__
    return 'chat_' + Date.now();
}

// Open/create IndexedDB database
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('TypingMindPDFs', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pdfs')) {
                db.createObjectStore('pdfs', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

// Show notification
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed bottom-4 right-4 p-4 rounded-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    notification.textContent = message;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => notification.remove(), 3000);
}

// Initialize extension
function initializeExtension() {
    // Create button immediately
    createPdfEmbedButton();
    
    // Also watch for DOM changes in case the upload button is added dynamically
    const observer = new MutationObserver((mutations) => {
        for (const mutation of mutations) {
            if (mutation.addedNodes.length) {
                createPdfEmbedButton();
            }
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Start the extension
initializeExtension();
