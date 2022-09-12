// More info here - https://django-htmx.readthedocs.io/en/latest/installation.html#:~:text=You%20can%20add,js/%20sub%2Ddirectory.
// and here https://unpkg.com/browse/htmx.org@1.8.0/dist/
htmx.defineExtension('debug', {
    onEvent: function (name, evt) {
        if (console.debug) {
            console.debug(name, evt);
        } else if (console) {
            console.log("DEBUG:", name, evt);
        } else {
            throw "NO CONSOLE SUPPORTED"
        }
    }
});
