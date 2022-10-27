import 'htmx.org';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import * as monaco from 'monaco-editor';

let monacoEditor = monaco.editor.create()
export function getMonacoValue() {
    return monacoEditor.getModel().getValue()
}

export const selectedLanguage = lang => {
   monaco.editor.setModelLanguage(monacoEditor.getModel(), lang);
}
selectedLanguage(document.getElementById("id_language").value);
