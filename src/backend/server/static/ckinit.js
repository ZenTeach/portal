var options = {
    placeholder: 'Write a choice feedback...',
    theme: 'snow',
    modules: {
        toolbar: [
          [{ header: [1, 2, false] }],
          ['bold', 'italic', 'underline'],
          ['code-block', 'link']
        ]
      },
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
    var keyRegex = new RegExp('^choices-[0-9]+-feedback$')
    for( var i = 0; i < sessionStorage.length; i++) {
        var keyx = sessionStorage.key(i)
        if (keyRegex.test(keyx)) count++;
    }

    return count++;
}

window.editorCount = editorCount
window.onload = (_event) => {
    removeEditors()
    initializeQuill()
}


document.querySelector('form').addEventListener('submit', function(e) {
    var editors = Array.from(document.querySelectorAll('.ql-container'))
    if (editors.length == 0){
        return;
    }
    editors.forEach(node => {
        var id = node.id
        var inputHiddenElement = document.querySelector(`input#${id}`)
        var content = node.__quill.getContents()
        inputHiddenElement.value = JSON.stringify(content["ops"])
    })
    
})

function initializeQuill(){
    var editorContainer = document.querySelectorAll('.editor')

    for (const editorIdx in editorContainer) {
        var editor = editorContainer[editorIdx]
        var editorKey = editor.id
        if (!editorExists(editorKey) && editorKey !== undefined) {
            var editorContent = ""
            if (editor.children && 
                editor.children.length > 0 &&
                editor.children[0].innerText.length > 0){    
                
                editorContent = editor.children[0].innerText 
            }

            var quillInstance = new Quill(editor, options)
            
            try {
                var c = JSON.parse(editorContent)
                quillInstance.setContents(c)
            } catch (error) {
                quillInstance.setText(editorContent + "\n")
            }
            
            storeEditor(editorKey, quillInstance)
        }
    }

}


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
                        var storeKey = `choices-${choice_number}-feedback`
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
