document.addEventListener(
    "DOMContentLoaded",
    () => {


        const textarea =
            document.getElementById(
                "study-textarea"
            );


        const sendButton =
            document.getElementById(
                "study-send"
            );


        const chatForm =
            document.getElementById(
                "chat-form"
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


        const promptButtons =
            document.querySelectorAll(
                ".prompt-card"
            );


        const promptInput =
            document.getElementById(
                "prompt-id-input"
            );


        const responseLengthInput =
            document.getElementById(
                "response-length-input"
            );


        const memoryInput =
            document.getElementById(
                "memory-input"
            );


        const memoryToggle =
            document.getElementById(
                "memory-toggle"
            );


        const lengthButtons =
            document.querySelectorAll(
                "[data-length]"
            );



        function resizeTextarea() {

            if (!textarea) {
                return;
            }


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


            sendButton.disabled =
                !hasText;


            sendButton.classList.toggle(
                "has-text",
                hasText
            );
        }



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



        chatForm?.addEventListener(
            "submit",
            event => {

                if (!textarea) {
                    return;
                }


                const message =
                    textarea.value.trim();


                if (!message) {

                    event.preventDefault();

                    return;

                }

            }
        );



        function openSettings() {

            settingsPanel?.classList.add(
                "active"
            );


            settingsOverlay?.classList.add(
                "active"
            );


            document.body.classList.add(
                "settings-open"
            );

        }



        function closeSettings() {

            settingsPanel?.classList.remove(
                "active"
            );


            settingsOverlay?.classList.remove(
                "active"
            );


            document.body.classList.remove(
                "settings-open"
            );

        }



        openSettingsButton?.addEventListener(
            "click",
            event => {

                event.preventDefault();

                event.stopPropagation();

                openSettings();

            }
        );



        closeSettingsButton?.addEventListener(
            "click",
            event => {

                event.preventDefault();

                closeSettings();

            }
        );



        settingsOverlay?.addEventListener(
            "click",
            () => {

                closeSettings();

            }
        );



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



        promptButtons.forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {


                        promptButtons.forEach(
                            item => {

                                item.classList.remove(
                                    "active"
                                );

                            }
                        );


                        button.classList.add(
                            "active"
                        );


                        const promptId =
                            button.dataset.promptId;


                        if (
                            promptInput &&
                            promptId
                        ) {

                            promptInput.value =
                                promptId;

                        }

                    }
                );

            }
        );



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
                            responseLengthInput &&
                            length
                        ) {

                            responseLengthInput.value =
                                length;

                        }

                    }
                );

            }
        );



        memoryToggle?.addEventListener(
            "change",
            () => {


                if (!memoryInput) {
                    return;
                }


                memoryInput.value =
                    memoryToggle.checked
                        ? "true"
                        : "false";

            }
        );


    }
);