
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
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
} else {
    ready();
}
