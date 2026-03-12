window.onload = () => {
    /** @type {HTMLTextAreaElement | null}  */  
    const textArea = document.getElementById('editedarea');
    const decoder = new TextDecoder('utf-8');
    if (textArea == null) throw new Error("Couldn't find Text Area");

    const socket = new WebSocket(`ws://${window.location.hostname}:${window.location.port}/ws`);
    let ready = false;

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

            if (event.inputType == "deleteContentBackward")
            {

            }
        }
    );

};

