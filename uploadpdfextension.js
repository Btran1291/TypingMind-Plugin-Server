(function() {
    'use strict';

    function createButton() {
        const buttonContainer = document.querySelector('[data-element-id="upload-document-button"]')?.parentElement;
        if (!buttonContainer) {
            console.error('Upload button container not found.');
            return;
        }

        const pdfEmbedButton = document.createElement('button');
        pdfEmbedButton.id = 'pdfEmbedButton';
        pdfEmbedButton.textContent = 'Embed PDF';
        pdfEmbedButton.classList.add('upload-button');
        pdfEmbedButton.style.cssText = `
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            background-color: #f0f0f0;
            color: #333;
            margin-left: 0.5rem;
        `;

        buttonContainer.appendChild(pdfEmbedButton);

        pdfEmbedButton.addEventListener('click', function() {
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.accept = '.pdf';

            fileInput.addEventListener('change', function() {
                const file = fileInput.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const base64String = e.target.result;
                        console.log('File content (Base64):', base64String);
                        localStorage.setItem('pdfBase64', base64String);
                        alert('PDF Base64 stored in Local Storage. Check console for details.');
                    };
                    reader.readAsDataURL(file);
                } else {
                    alert('No file selected.');
                }
            });
            fileInput.click();
        });
    }


    function waitForElement(selector, callback) {
        if (document.querySelector(selector)) {
            callback();
        } else {
            const observer = new MutationObserver(mutations => {
                if (document.querySelector(selector)) {
                    callback();
                    observer.disconnect();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }

    waitForElement('[data-element-id="upload-document-button"]', createButton);

})();
