
function ready() {
    const fileLists = document.querySelectorAll('.waf-uploaded-file-list');
    fileLists.forEach(list => {
        let margin = parseInt(list.dataset.gap || '32')
        let columns = parseInt(list.dataset.columns || '5')
        let trueOrder = true;
        if (list.dataset.trueOrder) {
            trueOrder = list.dataset.trueOrder === "true";
        }

        const macyInstance = Macy({
            container: list,
            trueOrder: trueOrder,
            waitForImages: true,
            margin: margin,
            columns: columns,
            breakAt: {
                1400: 4,
                1200: 3,
                940: 2,
                420: 1
            }
        });
    });

    const printButtons = document.querySelectorAll('.waf-file-print-button');
    printButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const fileUrl = button.getAttribute('data-file-url');
            const fileType = button.getAttribute('data-file-type');
            if (!fileUrl) return;
        
            const printFrame = document.createElement('iframe');
            Object.assign(printFrame.style, {
                position: 'fixed',
                visibility: 'hidden',
                width: '0', height: '0', border: '0'
            });
            document.body.appendChild(printFrame);
        
            if (fileType === 'image') {
                const doc = printFrame.contentDocument || printFrame.contentWindow.document;
                doc.write(`
                    <!DOCTYPE html>
                    <html>
                        <head>
                            <style>
                                body { 
                                    margin: 0; 
                                    display: flex; 
                                    justify-content: center; 
                                    align-items: flex-start; 
                                }
                                img { 
                                    max-width: 100%; 
                                    height: auto; /* This prevents the stretching */
                                    display: block;
                                    object-fit: contain;
                                }
                            </style>
                        </head>
                        <body>
                            <img src="${fileUrl}" onload="window.print();">
                        </body>
                    </html>
                `);
                doc.close();
            } else {
                // Standard PDF Printing (Uses your Django-exempt view)
                printFrame.src = fileUrl;
                printFrame.onload = () => {
                    printFrame.contentWindow.focus();
                    printFrame.contentWindow.print();
                };
            }
        
            // Global Cleanup
            printFrame.contentWindow.onafterprint = () => document.body.removeChild(printFrame);
            setTimeout(() => { if(document.body.contains(printFrame)) document.body.removeChild(printFrame); }, 5000);
        });
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
} else {
    ready();
}
