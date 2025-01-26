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
        
        // Get the current chat ID and model
        const { chatId, model } = await getCurrentChatInfo();
        
        // Store in IndexedDB
        const pdfData = await storePdfInDatabase(file.name, base64String, chatId, model);
        
        // Store a flag to indicate that the next message should include the PDF
        localStorage.setItem('pdfToAttach', chatId);
        
        // Log for debugging
        console.log('PDF stored in database:', file.name);
        
        // Optional: Show success message
        showNotification(`PDF "${file.name}" stored successfully`);
        
        // Display the PDF indicator
        displayPdfIndicator(pdfData);
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
async function storePdfInDatabase(filename, base64String, chatId, model) {
    // Create PDF metadata
    const pdfData = {
        filename,
        base64String,
        timestamp: Date.now(),
        chatId,
        model
    };

    // Store in IndexedDB
    const db = await openDatabase();
    const transaction = db.transaction(['pdfs'], 'readwrite');
    const store = transaction.objectStore('pdfs');
    const addRequest = await store.add(pdfData);
    return { ...pdfData, id: addRequest };
}

// Get current chat ID and model from TypingMind
async function getCurrentChatInfo() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('keyval-store', 1);

        request.onerror = () => reject(request.error);

        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['keyval'], 'readonly');
            const store = transaction.objectStore('keyval');

            // Attempt to find the active chat ID
            const activeChatRequest = store.get('activeChatId');
            const activeModelRequest = store.get('activeModel');

            Promise.all([
                new Promise(resolve => activeChatRequest.onsuccess = resolve),
                new Promise(resolve => activeModelRequest.onsuccess = resolve)
            ]).then(() => {
                const activeChatId = activeChatRequest.result;
                const activeModel = activeModelRequest.result;

                const chatId = activeChatId || 'chat_' + Date.now();
                const model = activeModel || 'unknown';

                resolve({ chatId, model });
            });
        };
    });
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

// Function to retrieve PDF data from IndexedDB
async function retrievePdfFromDatabase(chatId) {
    return new Promise(async (resolve, reject) => {
        const db = await openDatabase();
        const transaction = db.transaction(['pdfs'], 'readonly');
        const store = transaction.objectStore('pdfs');
        const request = store.getAll();

        request.onsuccess = () => {
            const pdfs = request.result;
            const pdf = pdfs.find(pdf => pdf.chatId === chatId);
            resolve(pdf);
        };

        request.onerror = () => reject(request.error);
    });
}

// Function to intercept and modify the API call
async function interceptAndModifyApiCall(url, options) {
    const pdfToAttach = localStorage.getItem('pdfToAttach');
    if (pdfToAttach) {
        localStorage.removeItem('pdfToAttach');

        // Retrieve the PDF data from IndexedDB
        const pdfData = await retrievePdfFromDatabase(pdfToAttach);

        if (pdfData) {
            // Modify the request body to include the PDF data
            try {
                const requestBody = JSON.parse(options.body);
                if (url.includes('api.anthropic.com')) {
                   // Handle Anthropic Claude API
                    requestBody.messages.push({
                        "role": "user",
                        "content": [{
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdfData.base64String
                            }
                        }]
                    });
                    options.body = JSON.stringify(requestBody);
                } else {
                    console.warn("Unsupported API endpoint:", url);
                    return fetch(url, options); // Send original request
                }
            } catch (error) {
                console.error("Error modifying request body:", error);
            }
        }
    }
    // Send the original or modified request
    return fetch(url, options);
}

// Function to display PDF indicator
function displayPdfIndicator(pdfData) {
    const inputArea = document.querySelector('[data-element-id="chat-input-area"]');
    if (!inputArea) return;

    const indicator = document.createElement('div');
    indicator.className = 'pdf-indicator';
    indicator.style.cssText = `
        display: inline-flex;
        align-items: center;
        background-color: #f0f0f0;
        border-radius: 4px;
        padding: 4px 8px;
        margin-right: 8px;
        margin-top: 4px;
        font-size: 12px;
        color: #333;
    `;
    indicator.innerHTML = `
        <span style="margin-right: 4px;">📄</span>
        <span>${pdfData.filename}</span>
        <button class="delete-pdf-button" style="margin-left: 4px; background: none; border: none; cursor: pointer; color: #999;">x</button>
    `;

    // Add delete button handler
    const deleteButton = indicator.querySelector('.delete-pdf-button');
    deleteButton.addEventListener('click', async () => {
        await deletePdfFromDatabase(pdfData.id);
        indicator.remove();
    });

    inputArea.appendChild(indicator);
}

// Function to delete PDF from IndexedDB
async function deletePdfFromDatabase(pdfId) {
    const db = await openDatabase();
    const transaction = db.transaction(['pdfs'], 'readwrite');
    const store = transaction.objectStore('pdfs');
    await store.delete(pdfId);
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

    // Modify the fetch function
    const originalFetch = window.fetch;
    window.fetch = async function(url, options) {
      if (url.includes('api.anthropic.com')) {
        return interceptAndModifyApiCall(url, options);
      } else {
        return originalFetch(url, options);
      }
    };
}

// Start the extension
initializeExtension();
