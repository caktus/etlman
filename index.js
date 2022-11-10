import 'htmx.org';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import * as monaco from 'monaco-editor';

window.createEditor = function (id, model) {
    return monaco.editor.create(document.getElementById(id), {
        model: monaco.editor.createModel(model),
        theme: "vs-dark",
        wordWrap: "on",
        automaticLayout: true,
        minimap: {
          enabled: false,
        },
        scrollbar: {
          vertical: "auto",
        },
        language: "",
    });
}


window.selectedLanguage = function (model, lang) {
    monaco.editor.setModelLanguage(model, lang);
};
