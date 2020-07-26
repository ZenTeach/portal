window.editors = []
var options = {
    debug: 'info',
    placeholder: 'Compose an epic...',
    readOnly: true,
    theme: 'snow'
  };

function storeEditor(key, value) {
    return sessionStorage.setItem(key, value)
}

function editorExists(key) {
    return sessionStorage.getItem(key) !== null
}

function removeEditor(key) {
    return sessionStorage.removeItem(key)
}

function removeEditors(){
    sessionStorage.clear()
}

function editorCount(){
    var count = 0
    var keyRegex = new RegExp('^choices-[0-9]+-feedback_text$')
    for( var i = 0; i < sessionStorage.length; i++) {
        var keyx = sessionStorage.key(i)
        if (keyRegex.test(keyx)) count++;
    }

    return count++;
}

window.editorCount = editorCount
window.onload = (_event) => {
    removeEditors()
}

function initializeQuill(){
    var editorContainer = document.querySelectorAll('.editor')

    for (const editorIdx in editorContainer) {
        var editor = editorContainer[editorIdx]
        var editorKey = editor.id
        if (!editorExists(editorKey) && editorKey !== undefined) {
            var quillInstance = new Quill(editor, options)
            storeEditor(editorKey, quillInstance)
        }
    }

}

// window.onload = initialize


const MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
const form = document.querySelector('form.admin-form.form-horizontal');
const config = {
    attributes: true,
    childList: true,
    characterData: true,
    subtree: true,
};

const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        if (mutation.type === "childList") {
            if (mutation.target && [...mutation.addedNodes].length) {
                initializeQuill()
            }
            if (mutation.target && [...mutation.removedNodes].length) {
                mutation.removedNodes.forEach((child, key, parent) => {
                    var choicePattern = new RegExp('^choices-([0-9]*)$')
                    if(choicePattern.test(child.id)) {
                        var choice_number = choicePattern.exec(child.id)[1]
                        var storeKey = `choices-${choice_number}-feedback_text`
                        if(editorExists(storeKey)){
                            removeEditor(storeKey)
                        }
                    }
                })
            }
        }
    });
});

observer.observe(form, config);
