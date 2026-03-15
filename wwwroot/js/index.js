function startDownload() {
    const typeSelect = document.getElementById("downloadType");
    const type = (typeSelect?.value ?? "pdf").toLowerCase();
    const ext = type;
    const url = `${location.protocol}//${window.location.hostname}:${window.location.port}/download?type=${encodeURIComponent(type)}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `document.${ext}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

window.onload = () => {
    /** @type {HTMLTextAreaElement | null}  */  
    const textArea = document.getElementById('editedarea');
    const decoder = new TextDecoder('utf-8');
    if (textArea == null) throw new Error("Couldn't find Text Area");

    wsaddress = (location.protocol === "https:"? "wss://" : "ws://") + `${window.location.hostname}:${window.location.port}/ws`;
    const socket = new WebSocket(wsaddress);
    let ready = false;

    // /** @type {HTMLButtonElement | null}  */      
    // const downloadButton = document.getElementById("downloadbutton");
    // if (downloadButton == null) throw new Error("Couldn't find Download Button");
    // downloadButton.addEventListener('onclick', (event) => {
    //     browser.downloads.download(`${window.location.hostname}:${window.location.port}/download`)
    // });

    // Connection opened
    socket.addEventListener('open', (event) => {
        ready = true
    });

    // Listen for messages
    socket.addEventListener('message', (event) => {
        console.log("Message from server ", event.data);
        let data = JSON.parse(event.data);
        textArea.value = data.data;
        textArea.setSelectionRange(data.selection.start, data.selection.end)
    });


    textArea.addEventListener('selectionchange', 
        /** @param {Event} _ */
        (_) => {
        if (ready)
        {
            socket.send(JSON.stringify({
                "Type": 0,
                "Selection": 
                {
                    "start": textArea.selectionStart,
                    "end": textArea.selectionEnd
                }
            }));
        }
    });

    textArea.addEventListener('beforeinput', 
        /** @param {InputEvent} event */
        (event) => {
            if (event.inputType == "deleteContentBackward")
            {
                if (textArea.selectionStart != textArea.selectionEnd)
                {
                    socket.send(JSON.stringify({
                        "Type": 3,
                    }));
                }
                else 
                {
                    socket.send(JSON.stringify({
                        "Type": 2,
                        "Amount": 
                        {
                            "amount": 1,
                        }
                    }));
                }
            }

            if (event.inputType == "insertText" && ready)
            {
                socket.send(JSON.stringify({
                    "Type": 1,
                    "Insertion": 
                    {
                        "Text": event.data,
                    }
                }));
            }
        }
    );

};

