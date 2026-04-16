
function ready() {
    const form = document.getElementById("file-upload-form");
    const TOTAL_FORMS = document.getElementById("id_form-TOTAL_FORMS");
    const MAX_NUM_FORMS = document.getElementById("id_form-MAX_NUM_FORMS");
    const formDisplayArea = document.querySelector(".waf-upload-display");
    const formUploadArea = document.querySelector(".waf-upload-to");
    const fileInput = document.getElementById("file-input");
    const filePreviewTemplate = document.getElementById("file-uploaded-template");
    const notAvailableImage = form.dataset.noFilePreview;
    const zipFilePreview = form.dataset.zipFilePreview;

    const macyInstance = Macy({
        container: '.waf-upload-display',
        trueOrder: false,
        waitForImages: true,
        margin: 16, // Matches your gap: 1rem
        columns: 5,
        breakAt: {
            1400: 4,
            1200: 3,
            940: 2,
            420: 1
        }
    });

    const handle = {
        dragenter: ['stop', 'add:highlight'],
        dragover: ['stop', 'add:highlight'],
        dragleave: ['stop', 'remove:highlight'],
        drop: ['stop', 'remove:highlight']
    }

    const actions = {
        stop: (e) => e.stopPropagation(),
        add: (className) => formUploadArea.classList.add(className),
        remove: (className) => formUploadArea.classList.remove(className)
    };

    for (const event in handle) {
        const exec = handle[event];

        document.body.addEventListener(event, (e) => {
            e.preventDefault();
            
            for (const action of exec) {
                const actionParts = action.split(":");
                
                if (actionParts.length === 1) {
                    actions[actionParts[0]](e);
                }
                else if (actionParts.length === 2) {
                    actions[actionParts[0]](actionParts[1]);
                }
                else {
                    throw new Error(`Invalid action: ${action}`);
                }
            }
        });
    }

    function addFiles(files) {
        for (const file of files) {
            _ = addFileToFormset(file);
        }

        macyInstance.recalculate(true);
        macyInstance.runOnImageLoad(() => {
            macyInstance.recalculate(true);
        }, true);
    }

    formUploadArea.addEventListener("click", () => {
        fileInput.click();
    });

    document.body.addEventListener("drop", (e) => {
        if (!e.dataTransfer || !e.dataTransfer.files) {
            return;
        }

        e.preventDefault();
        const files = Array.from(e.dataTransfer.files);
        addFiles(files);
    });
    
    fileInput.addEventListener("change", () => {
        const files = Array.from(fileInput.files);
        addFiles(files);
    });

    function addFileToFormset(file) {

        const currentFormCount = parseInt(TOTAL_FORMS.value);
        if (currentFormCount >= MAX_NUM_FORMS.value) {
            alert("Maximum number of files reached");
            return;
        }

        const html = filePreviewTemplate.innerHTML.replace(/__PREFIX__/g, currentFormCount);
        const template = document.createElement("template");
        template.innerHTML = html.trim();

        const newForm = template.content.firstChild;
        const renderArea = newForm.querySelector(".waf-preview-render");
        const previewLabel = newForm.querySelector(".waf-preview-label");
        const titleInput = newForm.querySelector(`input[name$='form-${currentFormCount}-title']`);
        const fileInput = newForm.querySelector(`input[name$='form-${currentFormCount}-file']`);
        const removeButton = newForm.querySelector(".waf-file-remove-button");

        removeButton.addEventListener("click", () => {
            newForm.remove();
            TOTAL_FORMS.value = parseInt(TOTAL_FORMS.value) - 1;
            macyInstance.recalculate(true);
        });

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;

        renderArea.innerHTML = getPreviewHtml(file, {
            notAvailable: notAvailableImage,
            zip: zipFilePreview,
        });
        
        const fileTitle = file.name
            .replace(/\.[^/.]+$/, "")
            .replace(/[_]+/g, " ")
            .replace(/\s+/g, " ");
        titleInput.value = fileTitle;
        previewLabel.textContent = fileTitle;

        previewLabel.addEventListener("input", () => {
            titleInput.value = previewLabel.textContent;
        });

        formDisplayArea.appendChild(newForm);

        TOTAL_FORMS.value = currentFormCount + 1;

        return newForm;
    }
}

function getPreviewHtml(file, previewData = {}) {
    const name = file.name;
    const extension = name.split('.').pop().toLowerCase();
    const fileUrl = URL.createObjectURL(file);
    let result = "";

    if (["jpg", "jpeg", "png", "gif", "svg", "webp", "avif"].includes(extension)) {
        result = `<img src="${fileUrl}" alt="${name}" />`;
    } 
    else if (["pdf"].includes(extension)) {
        result = `<iframe src="${fileUrl}"></iframe>`;
    }
    else if (["mp4", "webm", "ogg"].includes(extension)) {
        result = `<video src="${fileUrl}" controls></video>`;
    }
    else if (["mp3", "wav"].includes(extension)) {
        result = `<audio src="${fileUrl}" controls></audio>`;
    }
    else if (["zip", "rar", "7z", "tar", "gz"].includes(extension)) {
        result = zipFile;
    }
    else {
        result = `<img src="${previewData.notAvailable}" alt="Not Available ${name}" />`;
    }

    return `<a class="waf-preview-link" href="${fileUrl}" target="_blank">${result}</a>`;
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
} else {
    ready();
}