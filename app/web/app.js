const API_BASE = "/api/v1";


const state = {
    currentView: "workspace",

    documents: [],

    filteredDocuments: [],

    topK: 5,

    sourceDocumentId: "",

    queryActive: false,
};


const elements = {
    navButtons: Array.from(
        document.querySelectorAll(
            "[data-view]"
        )
    ),

    views: Array.from(
        document.querySelectorAll(
            ".app-view"
        )
    ),

    viewBreadcrumb: document.getElementById(
        "view-breadcrumb"
    ),

    viewHeading: document.getElementById(
        "view-heading"
    ),

    statusDot: document.getElementById(
        "status-dot"
    ),

    statusText: document.getElementById(
        "status-text"
    ),

    openKnowledgeButton: document.getElementById(
        "open-knowledge-button"
    ),

    heroDocumentCount: document.getElementById(
        "hero-document-count"
    ),

    documentCount: document.getElementById(
        "document-count"
    ),

    documentsList: document.getElementById(
        "documents-list"
    ),

    documentSearch: document.getElementById(
        "document-search"
    ),

    fileInput: document.getElementById(
        "file-input"
    ),

    uploadZone: document.getElementById(
        "upload-zone"
    ),

    uploadStatus: document.getElementById(
        "upload-status"
    ),

    sourceFilter: document.getElementById(
        "source-filter"
    ),

    topKInput: document.getElementById(
        "top-k-input"
    ),

    topKValue: document.getElementById(
        "top-k-value"
    ),

    composerScopeLabel: document.getElementById(
        "composer-scope-label"
    ),

    queryForm: document.getElementById(
        "query-form"
    ),

    questionInput: document.getElementById(
        "question-input"
    ),

    askButton: document.getElementById(
        "ask-button"
    ),

    askButtonLabel: document.getElementById(
        "ask-button-label"
    ),

    conversation: document.getElementById(
        "conversation"
    ),

    clearButton: document.getElementById(
        "clear-button"
    ),

    evidenceCount: document.getElementById(
        "evidence-count"
    ),

    evidenceList: document.getElementById(
        "evidence-list"
    ),

    toastRegion: document.getElementById(
        "toast-region"
    ),
};


const viewConfig = {
    workspace: {
        breadcrumb: "WORKSPACE",
        heading: "Knowledge Workspace",
    },

    knowledge: {
        breadcrumb: "KNOWLEDGE",
        heading: "Source Library",
    },

    pipeline: {
        breadcrumb: "RAG PIPELINE",
        heading: "Retrieval Architecture",
    },
};


/* ==================================================
   REQUEST
================================================== */

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
                message = (
                    typeof payload.detail === "string"
                        ? payload.detail
                        : JSON.stringify(
                            payload.detail
                        )
                );
            }
        } catch {
            // Keep status message.
        }

        throw new Error(
            message
        );
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}


/* ==================================================
   HELPERS
================================================== */

function escapeHtml(
    value
) {
    const element = document.createElement(
        "div"
    );

    element.textContent = (
        value ?? ""
    );

    return element.innerHTML;
}


function sourceName(
    source
) {
    if (!source) {
        return "Unknown source";
    }

    const parts = String(
        source
    ).split(
        /[\\/]/
    );

    return (
        parts[parts.length - 1]
        || String(source)
    );
}


function shorten(
    value,
    length = 18
) {
    const text = String(
        value ?? ""
    );

    if (text.length <= length) {
        return text;
    }

    return (
        `${text.slice(
            0,
            length - 1
        )}…`
    );
}


/* ==================================================
   TOAST
================================================== */

function toast(
    title,
    message,
    type = "info"
) {
    const wrapper = document.createElement(
        "div"
    );

    wrapper.className = (
        `toast ${type}`
    );

    wrapper.innerHTML = `
        <span class="toast-dot"></span>

        <div class="toast-copy">

            <strong>
                ${escapeHtml(title)}
            </strong>

            <small>
                ${escapeHtml(message)}
            </small>

        </div>

        <button
            class="toast-close"
            type="button"
        >
            ×
        </button>
    `;


    wrapper
        .querySelector(
            ".toast-close"
        )
        .addEventListener(
            "click",
            () => {
                wrapper.remove();
            }
        );


    elements.toastRegion.appendChild(
        wrapper
    );


    window.setTimeout(
        () => {
            wrapper.remove();
        },
        4200
    );
}


/* ==================================================
   NAVIGATION
================================================== */

function switchView(
    viewName
) {
    const config = (
        viewConfig[viewName]
    );

    if (!config) {
        return;
    }


    state.currentView = (
        viewName
    );


    for (
        const button
        of elements.navButtons
    ) {
        button.classList.toggle(
            "active",
            button.dataset.view === viewName
        );
    }


    for (
        const view
        of elements.views
    ) {
        view.classList.toggle(
            "active",
            view.id === `view-${viewName}`
        );
    }


    elements.viewBreadcrumb.textContent = (
        config.breadcrumb
    );


    elements.viewHeading.textContent = (
        config.heading
    );


    window.scrollTo(
        {
            top: 0,
            behavior: "smooth",
        }
    );


    if (viewName === "workspace") {
        window.setTimeout(
            () => {
                elements.questionInput.focus();
            },
            150
        );
    }
}


/* ==================================================
   HEALTH
================================================== */

function setSystemStatus(
    online
) {
    elements.statusDot.classList.remove(
        "online",
        "offline"
    );


    if (online) {
        elements.statusDot.classList.add(
            "online"
        );

        elements.statusText.textContent = (
            "System online"
        );

        return;
    }


    elements.statusDot.classList.add(
        "offline"
    );

    elements.statusText.textContent = (
        "System unavailable"
    );
}


async function checkHealth() {
    try {
        await request(
            "/health"
        );

        setSystemStatus(
            true
        );

        return true;
    } catch {
        setSystemStatus(
            false
        );

        return false;
    }
}


/* ==================================================
   DOCUMENTS
================================================== */

function updateDocumentCounts() {
    const count = (
        state.documents.length
    );

    elements.documentCount.textContent = (
        String(count)
    );

    elements.heroDocumentCount.textContent = (
        String(count)
    );
}


function populateSourceFilter() {
    const selected = (
        state.sourceDocumentId
    );


    const options = [
        `
            <option value="">
                All indexed sources
            </option>
        `,

        ...state.documents.map(
            (document) => `
                <option
                    value="${escapeHtml(
                        document.id
                    )}"
                >
                    ${escapeHtml(
                        sourceName(
                            document.source
                        )
                    )}
                </option>
            `
        ),
    ];


    elements.sourceFilter.innerHTML = (
        options.join("")
    );


    const stillExists = (
        state.documents.some(
            (document) => (
                document.id
                === selected
            )
        )
    );


    state.sourceDocumentId = (
        stillExists
            ? selected
            : ""
    );


    elements.sourceFilter.value = (
        state.sourceDocumentId
    );


    updateComposerScope();
}


function updateComposerScope() {
    if (!state.sourceDocumentId) {
        elements.composerScopeLabel.textContent = (
            "ALL SOURCES"
        );

        return;
    }


    const document = (
        state.documents.find(
            (item) => (
                item.id
                === state.sourceDocumentId
            )
        )
    );


    elements.composerScopeLabel.textContent = (
        document
            ? sourceName(
                document.source
            ).toUpperCase()
            : "SELECTED SOURCE"
    );
}


function filterDocuments() {
    const query = (
        elements.documentSearch
            .value
            .trim()
            .toLowerCase()
    );


    state.filteredDocuments = (
        state.documents.filter(
            (document) => {
                if (!query) {
                    return true;
                }


                const searchable = [
                    document.source,
                    document.file_type,
                    document.id,
                ]
                    .filter(Boolean)
                    .join(" ")
                    .toLowerCase();


                return searchable.includes(
                    query
                );
            }
        )
    );


    renderDocumentRows();
}


function renderDocumentRows() {
    if (state.documents.length === 0) {
        elements.documentsList.innerHTML = `
            <div class="document-empty">
                No documents indexed yet.
            </div>
        `;

        return;
    }


    if (
        state.filteredDocuments.length === 0
    ) {
        elements.documentsList.innerHTML = `
            <div class="document-empty">
                No matching documents.
            </div>
        `;

        return;
    }


    elements.documentsList.innerHTML = (
        state.filteredDocuments
            .map(
                (document) => {
                    const type = String(
                        document.file_type
                        || "file"
                    ).toUpperCase();


                    return `
                        <div class="document-row">

                            <div class="document-source">

                                <div class="document-icon">
                                    ${escapeHtml(type)}
                                </div>


                                <div class="document-info">

                                    <strong
                                        title="${escapeHtml(
                                            document.source
                                        )}"
                                    >
                                        ${escapeHtml(
                                            sourceName(
                                                document.source
                                            )
                                        )}
                                    </strong>


                                    <small>
                                        Indexed knowledge source
                                    </small>

                                </div>

                            </div>


                            <span class="file-type">
                                ${escapeHtml(type)}
                            </span>


                            <span
                                class="document-id"
                                title="${escapeHtml(
                                    document.id
                                )}"
                            >
                                ${escapeHtml(
                                    shorten(
                                        document.id,
                                        20
                                    )
                                )}
                            </span>


                            <button
                                class="delete-button"
                                type="button"
                                data-document-id="${escapeHtml(
                                    document.id
                                )}"
                            >
                                ×
                            </button>

                        </div>
                    `;
                }
            )
            .join("")
    );


    for (
        const button
        of elements.documentsList
            .querySelectorAll(
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


function renderDocuments(
    documents
) {
    state.documents = (
        Array.isArray(documents)
            ? documents
            : []
    );


    state.filteredDocuments = (
        [...state.documents]
    );


    updateDocumentCounts();

    populateSourceFilter();

    filterDocuments();
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
        elements.documentsList.innerHTML = `
            <div class="document-empty">
                ${escapeHtml(
                    error.message
                )}
            </div>
        `;
    }
}


/* ==================================================
   UPLOAD
================================================== */

function setUploadStatus(
    message,
    type = ""
) {
    elements.uploadStatus.className = (
        "upload-status"
    );


    if (type) {
        elements.uploadStatus.classList.add(
            type
        );
    }


    elements.uploadStatus.textContent = (
        message
    );
}


async function uploadSingleDocument(
    file,
    index,
    total
) {
    const formData = new FormData();


    formData.append(
        "file",
        file
    );


    const prefix = (
        total > 1
            ? `${index + 1}/${total} · `
            : ""
    );


    setUploadStatus(
        `${prefix}Indexing ${file.name}...`
    );


    await request(
        `${API_BASE}/documents`,
        {
            method: "POST",
            body: formData,
        }
    );
}


async function uploadDocuments(
    fileList
) {
    const files = Array.from(
        fileList || []
    );


    if (files.length === 0) {
        return;
    }


    let completed = 0;

    const failures = [];


    for (
        let index = 0;
        index < files.length;
        index += 1
    ) {
        const file = (
            files[index]
        );


        try {
            await uploadSingleDocument(
                file,
                index,
                files.length
            );

            completed += 1;
        } catch (error) {
            failures.push(
                {
                    file: file.name,
                    message: error.message,
                }
            );
        }
    }


    elements.fileInput.value = (
        ""
    );


    await loadDocuments();


    if (completed > 0) {
        const word = (
            completed === 1
                ? "source"
                : "sources"
        );


        setUploadStatus(
            `${completed} ${word} indexed successfully.`,
            "success"
        );


        toast(
            "Knowledge base updated",
            `${completed} ${word} added.`,
            "success"
        );
    }


    if (failures.length > 0) {
        const failure = (
            failures[0]
        );


        setUploadStatus(
            `${failure.file}: ${failure.message}`,
            "error"
        );


        toast(
            "Upload failed",
            `${failures.length} file(s) could not be indexed.`,
            "error"
        );
    }
}


/* ==================================================
   DELETE
================================================== */

async function deleteDocument(
    documentId
) {
    const existing = (
        state.documents.find(
            (document) => (
                document.id
                === documentId
            )
        )
    );


    try {
        await request(
            `${API_BASE}/documents/${encodeURIComponent(
                documentId
            )}`,
            {
                method: "DELETE",
            }
        );


        if (
            state.sourceDocumentId
            === documentId
        ) {
            state.sourceDocumentId = (
                ""
            );
        }


        await loadDocuments();


        toast(
            "Source removed",
            existing
                ? `${sourceName(
                    existing.source
                )} was deleted.`
                : "Document removed.",
            "success"
        );
    } catch (error) {
        toast(
            "Delete failed",
            error.message,
            "error"
        );
    }
}


/* ==================================================
   CHAT
================================================== */

function removeWelcomeCard() {
    const welcome = (
        elements.conversation
            .querySelector(
                ".welcome-card"
            )
    );


    if (welcome) {
        welcome.remove();
    }
}


function scrollConversation() {
    elements.conversation.scrollTop = (
        elements.conversation.scrollHeight
    );
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
        <div class="message-content">
            ${escapeHtml(text)}
        </div>
    `;


    elements.conversation.appendChild(
        wrapper
    );


    scrollConversation();
}


function citationLabel(
    citation
) {
    const page = (
        citation.metadata
            ?.page_number
    );


    const source = (
        sourceName(
            citation.source
        )
    );


    return (
        page
            ? `[${citation.index}] ${source} · p.${page}`
            : `[${citation.index}] ${source}`
    );
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


    const safeCitations = (
        Array.isArray(citations)
            ? citations
            : []
    );


    const citationMarkup = (
        safeCitations.length
            ? `
                <div class="citations">

                    ${safeCitations
                        .map(
                            (citation) => `
                                <div class="citation">
                                    ${escapeHtml(
                                        citationLabel(
                                            citation
                                        )
                                    )}
                                </div>
                            `
                        )
                        .join("")}

                </div>
            `
            : ""
    );


    const noEvidenceMarkup = (
        insufficientEvidence
            ? `
                <div class="citations">

                    <div class="citation">
                        No sufficient supporting evidence was found.
                    </div>

                </div>
            `
            : ""
    );


    wrapper.innerHTML = `
        <div class="message-content">

            ${escapeHtml(
                answer
            )}

            ${
                insufficientEvidence
                    ? noEvidenceMarkup
                    : citationMarkup
            }

        </div>
    `;


    elements.conversation.appendChild(
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


/* ==================================================
   EVIDENCE
================================================== */

function renderEvidence(
    citations,
    insufficientEvidence
) {
    const safeCitations = (
        Array.isArray(citations)
            ? citations
            : []
    );


    elements.evidenceCount.textContent = (
        String(
            safeCitations.length
        )
    );


    if (safeCitations.length === 0) {
        elements.evidenceList.innerHTML = `
            <div class="evidence-empty">

                <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                >
                    <path d="M5 3h10l4 4v14H5z"></path>
                    <path d="M15 3v5h5"></path>
                    <path d="M8 13h8"></path>
                    <path d="M8 17h5"></path>
                </svg>


                <strong>
                    ${
                        insufficientEvidence
                            ? "Insufficient evidence"
                            : "No citations returned"
                    }
                </strong>


                <small>
                    ${
                        insufficientEvidence
                            ? "NexusRAG did not find enough supporting evidence."
                            : "No citation records were returned."
                    }
                </small>

            </div>
        `;

        return;
    }


    elements.evidenceList.innerHTML = (
        safeCitations
            .map(
                (citation) => {
                    const page = (
                        citation.metadata
                            ?.page_number
                    );


                    return `
                        <article class="evidence-item">

                            <div class="evidence-index">
                                [${escapeHtml(
                                    String(
                                        citation.index
                                    )
                                )}]
                            </div>


                            <div class="evidence-copy">

                                <strong
                                    title="${escapeHtml(
                                        citation.source
                                    )}"
                                >
                                    ${escapeHtml(
                                        sourceName(
                                            citation.source
                                        )
                                    )}
                                </strong>


                                <small>

                                    ${
                                        page
                                            ? `Page ${escapeHtml(
                                                String(page)
                                            )} · `
                                            : ""
                                    }

                                    chunk
                                    ${escapeHtml(
                                        shorten(
                                            citation.chunk_id,
                                            14
                                        )
                                    )}

                                </small>

                            </div>

                        </article>
                    `;
                }
            )
            .join("")
    );
}


function resetEvidence() {
    elements.evidenceCount.textContent = (
        "0"
    );


    elements.evidenceList.innerHTML = `
        <div class="evidence-empty">

            <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
            >
                <path d="M5 3h10l4 4v14H5z"></path>
                <path d="M15 3v5h5"></path>
                <path d="M8 13h8"></path>
                <path d="M8 17h5"></path>
            </svg>


            <strong>
                No citations yet
            </strong>


            <small>
                Run a query to inspect returned evidence.
            </small>

        </div>
    `;
}


/* ==================================================
   QUERY
================================================== */

async function askQuestion(
    question
) {
    if (state.queryActive) {
        return;
    }


    state.queryActive = (
        true
    );


    elements.askButton.disabled = (
        true
    );


    elements.askButtonLabel.textContent = (
        "Processing"
    );


    try {
        const body = {
            question,
            top_k: state.topK,
        };


        if (state.sourceDocumentId) {
            body.document_id = (
                state.sourceDocumentId
            );
        }


        const result = await request(
            `${API_BASE}/query`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify(
                    body
                ),
            }
        );


        appendAssistantMessage(
            result.answer,
            result.citations,
            result.insufficient_evidence
        );


        renderEvidence(
            result.citations,
            result.insufficient_evidence
        );
    } catch (error) {
        appendErrorMessage(
            error.message
        );


        toast(
            "Query failed",
            error.message,
            "error"
        );
    } finally {
        state.queryActive = (
            false
        );


        elements.askButton.disabled = (
            false
        );


        elements.askButtonLabel.textContent = (
            "Ask Nexus"
        );
    }
}


/* ==================================================
   RESET CHAT
================================================== */

function resetConversation() {
    elements.conversation.innerHTML = `
        <div class="welcome-card">

            <div class="welcome-visual">

                <div class="document-stack">
                    <span></span>
                    <span></span>

                    <strong>
                        [N]
                    </strong>
                </div>


                <div class="data-nodes">
                    <i></i>
                    <i></i>
                    <i></i>
                    <i></i>
                    <i></i>
                </div>

            </div>


            <p class="section-label">
                KNOWLEDGE LAYER READY
            </p>


            <h4>
                Retrieve. Ground. Cite.
            </h4>


            <p>
                Ask a question about your indexed
                documents and NexusRAG will answer
                from retrieved evidence.
            </p>


            <div class="capability-list">
                <span>Semantic Search</span>
                <span>BM25</span>
                <span>Hybrid RRF</span>
                <span>Local LLM</span>
                <span>Citations</span>
            </div>

        </div>
    `;


    resetEvidence();
}


/* ==================================================
   TEXTAREA
================================================== */

function autoResizeTextarea() {
    elements.questionInput.style.height = (
        "auto"
    );


    elements.questionInput.style.height = (
        `${Math.min(
            elements.questionInput.scrollHeight,
            180
        )}px`
    );
}


/* ==================================================
   EVENTS
================================================== */

for (
    const button
    of elements.navButtons
) {
    button.addEventListener(
        "click",
        () => {
            switchView(
                button.dataset.view
            );
        }
    );
}


/* ADD SOURCE BUTTON */

elements.openKnowledgeButton.addEventListener(
    "click",
    () => {
        switchView(
            "knowledge"
        );


        window.setTimeout(
            () => {
                elements.fileInput.click();
            },
            140
        );
    }
);


/* DOCUMENT SEARCH */

elements.documentSearch.addEventListener(
    "input",
    filterDocuments
);


/* SOURCE FILTER */

elements.sourceFilter.addEventListener(
    "change",
    () => {
        state.sourceDocumentId = (
            elements.sourceFilter.value
        );


        updateComposerScope();
    }
);


/* TOP K */

elements.topKInput.addEventListener(
    "input",
    () => {
        const parsed = Number.parseInt(
            elements.topKInput.value,
            10
        );


        state.topK = (
            Number.isFinite(parsed)
                ? parsed
                : 5
        );


        elements.topKValue.textContent = (
            String(
                state.topK
            )
        );
    }
);


/* FILE INPUT */

elements.fileInput.addEventListener(
    "change",
    async () => {
        await uploadDocuments(
            elements.fileInput.files
        );
    }
);


/* DRAG DROP */

for (
    const eventName
    of [
        "dragenter",
        "dragover",
    ]
) {
    elements.uploadZone.addEventListener(
        eventName,
        (event) => {
            event.preventDefault();


            elements.uploadZone.classList.add(
                "dragover"
            );
        }
    );
}


for (
    const eventName
    of [
        "dragleave",
        "drop",
    ]
) {
    elements.uploadZone.addEventListener(
        eventName,
        (event) => {
            event.preventDefault();


            elements.uploadZone.classList.remove(
                "dragover"
            );
        }
    );
}


elements.uploadZone.addEventListener(
    "drop",
    async (event) => {
        await uploadDocuments(
            event.dataTransfer?.files
        );
    }
);


/* QUERY FORM */

elements.queryForm.addEventListener(
    "submit",
    async (event) => {
        event.preventDefault();


        const question = (
            elements.questionInput
                .value
                .trim()
        );


        if (
            !question
            || state.queryActive
        ) {
            return;
        }


        appendUserMessage(
            question
        );


        elements.questionInput.value = (
            ""
        );


        autoResizeTextarea();


        await askQuestion(
            question
        );
    }
);


/* TEXTAREA RESIZE */

elements.questionInput.addEventListener(
    "input",
    autoResizeTextarea
);


/* ENTER TO SEND */

elements.questionInput.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter"
            && !event.shiftKey
        ) {
            event.preventDefault();


            elements.queryForm.requestSubmit();
        }
    }
);


/* CLEAR */

elements.clearButton.addEventListener(
    "click",
    resetConversation
);


/* KEYBOARD NAVIGATION */

document.addEventListener(
    "keydown",
    (event) => {
        const activeTag = (
            document.activeElement
                ?.tagName
                ?.toLowerCase()
        );


        const editing = (
            [
                "input",
                "textarea",
                "select",
            ].includes(
                activeTag
            )
        );


        if (
            !editing
            && event.key === "/"
        ) {
            event.preventDefault();


            switchView(
                "workspace"
            );


            return;
        }


        if (
            !editing
            && [
                "1",
                "2",
                "3",
            ].includes(
                event.key
            )
        ) {
            const viewByKey = {
                "1":
                    "workspace",

                "2":
                    "knowledge",

                "3":
                    "pipeline",
            };


            switchView(
                viewByKey[
                    event.key
                ]
            );
        }
    }
);


/* ==================================================
   INITIALIZE
================================================== */

async function initialize() {
    resetEvidence();


    const [
        online,
    ] = await Promise.all(
        [
            checkHealth(),
            loadDocuments(),
        ]
    );


    if (!online) {
        toast(
            "NexusRAG API unavailable",
            "The frontend loaded, but the local backend did not answer.",
            "error"
        );
    }
}


initialize();