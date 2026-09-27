document.addEventListener("DOMContentLoaded", () => {

    /*
    ==========================================================
    ELEMENTOS
    ==========================================================
    */

    const textarea =
        document.getElementById(
            "study-textarea"
        );

    const sendButton =
        document.getElementById(
            "study-send"
        );


    const settingsPanel =
        document.getElementById(
            "chat-settings-panel"
        );

    const settingsOverlay =
        document.getElementById(
            "chat-settings-overlay"
        );

    const openSettingsButton =
        document.getElementById(
            "open-chat-settings"
        );

    const closeSettingsButton =
        document.getElementById(
            "close-chat-settings"
        );


    const modeButtons =
        document.querySelectorAll(
            ".mode-card"
        );


    const lengthButtons =
        document.querySelectorAll(
            ".segmented-control button"
        );


    const memoryToggle =
        document.getElementById(
            "memory-toggle"
        );


    const clearChatButton =
        document.getElementById(
            "clear-chat-button"
        );



    /*
    ==========================================================
    INPUTS OCULTOS PARA DJANGO
    ==========================================================
    */

    const modeInput =
        document.getElementById(
            "chat-mode-input"
        );


    const responseLengthInput =
        document.getElementById(
            "response-length-input"
        );


    const memoryInput =
        document.getElementById(
            "memory-input"
        );



    /*
    ==========================================================
    TEXTAREA - AUTO RESIZE
    ==========================================================
    */

    function resizeTextarea() {

        if (!textarea) return;


        textarea.style.height =
            "auto";


        const newHeight =
            textarea.scrollHeight;


        const maxHeight =
            150;


        textarea.style.height =
            Math.min(
                newHeight,
                maxHeight
            ) + "px";


        textarea.style.overflowY =
            newHeight > maxHeight
                ? "auto"
                : "hidden";
    }



    /*
    ==========================================================
    ESTADO DEL BOTÓN ENVIAR
    ==========================================================
    */

    function updateSendButton() {

        if (
            !textarea ||
            !sendButton
        ) {
            return;
        }


        const hasText =
            textarea.value
                .trim()
                .length > 0;


        /*
            Activa/desactiva botón
        */

        sendButton.disabled =
            !hasText;


        /*
            Cambia visualmente
            ✦  →  ↑
        */

        sendButton.classList.toggle(
            "has-text",
            hasText
        );

    }



    /*
    ==========================================================
    EVENTO AL ESCRIBIR
    ==========================================================
    */

    if (textarea) {

        textarea.addEventListener(
            "input",
            () => {

                resizeTextarea();

                updateSendButton();

            }
        );


        resizeTextarea();

        updateSendButton();

    }



    /*
    ==========================================================
    IMPORTANTE

    ENTER YA NO ENVÍA EL FORMULARIO.
    ==========================================================
    */

    textarea?.addEventListener(
        "keydown",
        event => {

            /*
                Enter funciona normalmente.

                El navegador crea una
                nueva línea porque estamos
                dentro de un textarea.

                NO hacemos requestSubmit().
            */

            if (event.key === "Enter") {

                /*
                    No enviamos absolutamente
                    nada desde teclado.
                */

                return;

            }

        }
    );



    /*
    ==========================================================
    SEGURIDAD EXTRA DEL FORMULARIO

    Sólo permitimos enviar si hay texto.
    ==========================================================
    */

    const chatForm =
        document.getElementById(
            "chat-form"
        );


    chatForm?.addEventListener(
        "submit",
        event => {

            const message =
                textarea.value.trim();


            if (!message) {

                event.preventDefault();

                return;

            }

        }
    );



    /*
    ==========================================================
    ABRIR PANEL
    ==========================================================
    */

    function openSettings() {

        settingsPanel?.classList.add(
            "active"
        );


        settingsOverlay?.classList.add(
            "active"
        );

    }



    /*
    ==========================================================
    CERRAR PANEL
    ==========================================================
    */

    function closeSettings() {

        settingsPanel?.classList.remove(
            "active"
        );


        settingsOverlay?.classList.remove(
            "active"
        );

    }



    openSettingsButton?.addEventListener(
        "click",
        openSettings
    );


    closeSettingsButton?.addEventListener(
        "click",
        closeSettings
    );


    settingsOverlay?.addEventListener(
        "click",
        closeSettings
    );



    /*
        ESC CIERRA SETTINGS
    */

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Escape"
            ) {

                closeSettings();

            }

        }
    );



    /*
    ==========================================================
    MODOS IA
    ==========================================================
    */

    modeButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    modeButtons.forEach(
                        item => {

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    button.classList.add(
                        "active"
                    );


                    const mode =
                        button.dataset.mode;


                    if (modeInput) {

                        modeInput.value =
                            mode;

                    }


                    localStorage.setItem(
                        "ai_chat_mode",
                        mode
                    );


                    updatePlaceholder(
                        mode
                    );

                }
            );

        }
    );



    /*
    ==========================================================
    PLACEHOLDER
    ==========================================================
    */

    function updatePlaceholder(
        mode
    ) {

        if (!textarea) return;


        const placeholders = {

            general:
                "Preguntá lo que quieras...",

            study:
                "¿Qué querés estudiar?",

            explain:
                "¿Qué querés que te explique?",

            exam:
                "¿Qué tema querés practicar?"

        };


        textarea.placeholder =
            placeholders[mode]
            ||
            placeholders.general;

    }



    /*
    ==========================================================
    LONGITUD
    ==========================================================
    */

    lengthButtons.forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    lengthButtons.forEach(
                        item => {

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    button.classList.add(
                        "active"
                    );


                    const length =
                        button.dataset.length;


                    if (
                        responseLengthInput
                    ) {

                        responseLengthInput.value =
                            length;

                    }


                    localStorage.setItem(
                        "ai_response_length",
                        length
                    );

                }
            );

        }
    );



    /*
    ==========================================================
    MEMORIA
    ==========================================================
    */

    memoryToggle?.addEventListener(
        "change",
        () => {

            const enabled =
                memoryToggle.checked;


            if (memoryInput) {

                memoryInput.value =
                    enabled
                        ? "true"
                        : "false";

            }


            localStorage.setItem(
                "ai_memory_enabled",
                enabled
            );

        }
    );



    /*
    ==========================================================
    CARGAR CONFIGURACIÓN
    ==========================================================
    */

    function loadSettings() {

        /*
            MODO
        */

        const savedMode =
            localStorage.getItem(
                "ai_chat_mode"
            )
            ||
            "general";


        if (modeInput) {

            modeInput.value =
                savedMode;

        }


        modeButtons.forEach(
            button => {

                button.classList.toggle(

                    "active",

                    button.dataset.mode
                    === savedMode

                );

            }
        );


        updatePlaceholder(
            savedMode
        );



        /*
            LONGITUD
        */

        const savedLength =
            localStorage.getItem(
                "ai_response_length"
            )
            ||
            "normal";


        if (
            responseLengthInput
        ) {

            responseLengthInput.value =
                savedLength;

        }


        lengthButtons.forEach(
            button => {

                button.classList.toggle(

                    "active",

                    button.dataset.length
                    === savedLength

                );

            }
        );



        /*
            MEMORIA
        */

        const savedMemory =
            localStorage.getItem(
                "ai_memory_enabled"
            );


        const memoryEnabled =
            savedMemory === null
                ? true
                : savedMemory === "true";


        if (memoryToggle) {

            memoryToggle.checked =
                memoryEnabled;

        }


        if (memoryInput) {

            memoryInput.value =
                memoryEnabled
                    ? "true"
                    : "false";

        }

    }


    loadSettings();



    /*
    ==========================================================
    LIMPIAR CHAT
    ==========================================================
    */

    clearChatButton?.addEventListener(
        "click",
        () => {

            const messages =
                document.querySelector(
                    ".chat-messages"
                );


            if (messages) {

                messages.innerHTML =
                    "";

            }


            closeSettings();

        }
    );

});