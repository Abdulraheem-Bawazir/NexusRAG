const API_BASE = "/api/v1";

const statusDot = document.getElementById(
    "status-dot"
);

const statusText = document.getElementById(
    "status-text"
);

const documentCount = document.getElementById(
    "document-count"
);

const documentsList = document.getElementById(
    "documents-list"
);

const fileInput = document.getElementById(
    "file-input"
);

const uploadStatus = document.getElementById(
    "upload-status"
);

const queryForm = document.getElementById(
    "query-form"
);

const questionInput = document.getElementById(
    "question-input"
);

const askButton = document.getElementById(
    "ask-button"
);

const conversation = document.getElementById(
    "conversation"
);

const clearButton = document.getElementById(
    "clear-button"
);


async function request(
    url,
    options = {}
) {
    const response = await fetch(
        url,
        options
    );

    if (!response.ok) {
        let message = (
            `Request failed with status ${response.status}`
        );

        try {
            const payload = await response.json();

            if (payload.detail) {
                message = payload.detail;
            }
        } catch {
            // Preserve the default message.
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}


function setSystemStatus(
    online
) {
    statusDot.classList.remove(
        "online",
        "offline"
    );

    if (online) {
        statusDot.classList.add(
            "online"
        );

        statusText.textContent = (
            "System online"
        );

        return;
    }

    statusDot.classList.add(
        "offline"
    );

    statusText.textContent = (
        "System unavailable"
    );
}


async function checkHealth() {
    try {
        await request(
            "/health"
        );

        setSystemStatus(true);
    } catch {
        setSystemStatus(false);
    }
}


function escapeHtml(value) {
    const element = document.createElement(
        "div"
    );

    element.textContent = value;

    return element.innerHTML;
}


function renderDocuments(
    documents
) {
    documentCount.textContent = (
        String(documents.length)
    );

    if (documents.length === 0) {
        documentsList.innerHTML = `
            <div class="empty-state">
                No documents indexed yet.
            </div>
        `;

        return;
    }

    documentsList.innerHTML = (
        documents
            .map(
                (document) => `
                    <div class="document-card">
                        <div class="document-icon">
                            ${escapeHtml(
                                document.file_type
                            ).toUpperCase()}
                        </div>

                        <div class="document-info">
                            <strong>
                                ${escapeHtml(
                                    document.source
                                )}
                            </strong>

                            <span>
                                ${escapeHtml(
                                    document.file_type
                                )}
                            </span>
                        </div>

                        <button
                            class="delete-button"
                            type="button"
                            title="Delete document"
                            data-document-id="${
                                escapeHtml(
                                    document.id
                                )
                            }"
                        >
                            ×
                        </button>
                    </div>
                `
            )
            .join("")
    );

    for (
        const button
        of documentsList.querySelectorAll(
            ".delete-button"
        )
    ) {
        button.addEventListener(
            "click",
            async () => {
                const documentId = (
                    button.dataset.documentId
                );

                if (!documentId) {
                    return;
                }

                await deleteDocument(
                    documentId
                );
            }
        );
    }
}


async function loadDocuments() {
    try {
        const documents = await request(
            `${API_BASE}/documents`
        );

        renderDocuments(
            documents
        );
    } catch (error) {
        documentsList.innerHTML = `
            <div class="empty-state">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;
    }
}


async function uploadDocument(
    file
) {
    uploadStatus.className = (
        "upload-status"
    );

    uploadStatus.textContent = (
        "Indexing document..."
    );

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    try {
        await request(
            `${API_BASE}/documents`,
            {
                method: "POST",
                body: formData,
            }
        );

        uploadStatus.className = (
            "upload-status success"
        );

        uploadStatus.textContent = (
            "Document indexed successfully."
        );

        await loadDocuments();
    } catch (error) {
        uploadStatus.className = (
            "upload-status error"
        );

        uploadStatus.textContent = (
            error.message
        );
    } finally {
        fileInput.value = "";
    }
}


async function deleteDocument(
    documentId
) {
    try {
        await request(
            `${API_BASE}/documents/${encodeURIComponent(
                documentId
            )}`,
            {
                method: "DELETE",
            }
        );

        uploadStatus.className = (
            "upload-status success"
        );

        uploadStatus.textContent = (
            "Document removed."
        );

        await loadDocuments();
    } catch (error) {
        uploadStatus.className = (
            "upload-status error"
        );

        uploadStatus.textContent = (
            error.message
        );
    }
}


function removeWelcomeCard() {
    const welcome = (
        conversation.querySelector(
            ".welcome-card"
        )
    );

    if (welcome) {
        welcome.remove();
    }
}


function appendUserMessage(
    text
) {
    removeWelcomeCard();

    const wrapper = document.createElement(
        "div"
    );

    wrapper.className = (
        "message user-message"
    );

    wrapper.innerHTML = `
        <div class="message-label">
            YOU
        </div>

        <div class="message-content">
            ${escapeHtml(text)}
        </div>
    `;

    conversation.appendChild(
        wrapper
    );

    scrollConversation();
}


function appendAssistantMessage(
    answer,
    citations,
    insufficientEvidence
) {
    removeWelcomeCard();

    const wrapper = document.createElement(
        "div"
    );

    wrapper.className = (
        "message assistant-message"
    );

    const citationMarkup = (
        citations.length
            ? `
                <div class="citations">
                    ${citations
                        .map(
                            (citation) => `
                                <div class="citation">
                                    [${citation.index}]
                                    ${escapeHtml(
                                        citation.source
                                    )}
                                    ${
                                        citation.metadata
                                            ?.page_number
                                            ? ` · page ${
                                                escapeHtml(
                                                    String(
                                                        citation
                                                            .metadata
                                                            .page_number
                                                    )
                                                )
                                            }`
                                            : ""
                                    }
                                </div>
                            `
                        )
                        .join("")}
                </div>
            `
            : ""
    );

    wrapper.innerHTML = `
        <div class="message-label">
            NEXUSRAG
        </div>

        <div class="message-content">
            ${escapeHtml(answer)}

            ${
                insufficientEvidence
                    ? `
                        <div class="citations">
                            <div class="citation">
                                No supporting evidence
                                was found.
                            </div>
                        </div>
                    `
                    : citationMarkup
            }
        </div>
    `;

    conversation.appendChild(
        wrapper
    );

    scrollConversation();
}


function appendErrorMessage(
    message
) {
    appendAssistantMessage(
        `Error: ${message}`,
        [],
        false
    );
}


function scrollConversation() {
    conversation.scrollTop = (
        conversation.scrollHeight
    );
}


async function askQuestion(
    question
) {
    askButton.disabled = true;
    askButton.textContent = "Thinking...";

    try {
        const result = await request(
            `${API_BASE}/query`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify(
                    {
                        question,
                        top_k: 5,
                    }
                ),
            }
        );

        appendAssistantMessage(
            result.answer,
            result.citations,
            result.insufficient_evidence
        );
    } catch (error) {
        appendErrorMessage(
            error.message
        );
    } finally {
        askButton.disabled = false;
        askButton.textContent = (
            "Ask Nexus"
        );
    }
}


fileInput.addEventListener(
    "change",
    async () => {
        const file = fileInput.files[0];

        if (!file) {
            return;
        }

        await uploadDocument(
            file
        );
    }
);


queryForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();

        const question = (
            questionInput.value.trim()
        );

        if (!question) {
            return;
        }

        appendUserMessage(
            question
        );

        questionInput.value = "";

        await askQuestion(
            question
        );
    }
);


questionInput.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {
            event.preventDefault();

            queryForm.requestSubmit();
        }
    }
);


clearButton.addEventListener(
    "click",
    () => {
        conversation.innerHTML = `
            <div class="welcome-card">
                <div class="welcome-symbol">
                    N
                </div>

                <h4>
                    NexusRAG is ready.
                </h4>

                <p>
                    Ask another grounded question
                    about your indexed documents.
                </p>
            </div>
        `;
    }
);


async function initialize() {
    await Promise.all([
        checkHealth(),
        loadDocuments(),
    ]);
}


initialize();