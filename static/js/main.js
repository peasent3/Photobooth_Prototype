/* --------------------------------------------------------------
   main.js – front‑end controller for our photobooth
   -------------------------------------------------------------- */

(() => {
    // -----------------------------------------------------------------
    //   Helper: Bootstrap toast factory
    // -----------------------------------------------------------------
    const toastContainer = document.getElementById('toastContainer');

    function showToast(message, type = 'info', autohide = true, delay = 4000) {
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                ${autohide ? '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' : ''}
            </div>
        `;

        toastContainer.appendChild(toastEl);
        const bsToast = new bootstrap.Toast(toastEl, { autohide, delay });
        bsToast.show();

        // Remove from DOM after hidden
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    }

    // -----------------------------------------------------------------
    //   UI elements
    // -----------------------------------------------------------------
    const btnConnect    = document.getElementById('btnConnect');
    const btnTake       = document.getElementById('btnTake');
    const btnPrint      = document.getElementById('btnPrint');
    const btnDisconnect = document.getElementById('btnDisconnect');
    const progressBar   = document.querySelector('.progress-bar');
    const stepLabel     = document.getElementById('stepLabel');
    const countdownEl   = document.getElementById('countdownOverlay');
    const liveViewImg   = document.getElementById('liveViewImg');

    // -----------------------------------------------------------------
    //   State machine – keep UI in sync with what the backend can do
    // -----------------------------------------------------------------
    const STATE = {
        DISCONNECTED: 'disconnected',
        CONNECTED: 'connected',
        PHOTO_TAKEN: 'photo_taken',
        COLLAGE_READY: 'collage_ready',
    };
    let currentState = STATE.DISCONNECTED;

    function setState(newState) {
        currentState = newState;
        // Reset UI first
        btnConnect.disabled    = true;
        btnTake.disabled       = true;
        btnPrint.disabled      = true;
        btnDisconnect.disabled = true;

        // Update progress bar & label
        switch (newState) {
            case STATE.DISCONNECTED:
                progressBar.style.width = '0%';
                stepLabel.textContent = 'Press **Connect** to start';
                btnConnect.disabled = false;
                break;
            case STATE.CONNECTED:
                progressBar.style.width = '25%';
                stepLabel.textContent = 'Ready – take your first photo';
                btnTake.disabled = false;
                btnDisconnect.disabled = false;
                break;
            case STATE.PHOTO_TAKEN:
                progressBar.style.width = '50%';
                stepLabel.textContent = 'Keep snapping … (need 4 total)';
                btnTake.disabled = false;
                btnDisconnect.disabled = false;
                break;
            case STATE.COLLAGE_READY:
                progressBar.style.width = '100%';
                stepLabel.textContent = 'Collage ready! Click Print';
                btnPrint.disabled = false;
                btnDisconnect.disabled = false;
                break;
        }
    }

    // -----------------------------------------------------------------
    //   AJAX helpers (using fetch)
    // -----------------------------------------------------------------
    async function postJson(url) {
        const resp = await fetch(url, { method: 'POST' });
        const data = await resp.json();
        if (!resp.ok) {
            throw new Error(data.message || 'Server error');
        }
        return data;
    }

    // -----------------------------------------------------------------
    //   Actions
    // -----------------------------------------------------------------
    btnConnect.addEventListener('click', async () => {
        try {
            await postJson('/connect');
            document.body.classList.add('connected');   // adds live‑view glow
            showToast('Camera connected ✔️', 'success');
            setState(STATE.CONNECTED);
        } catch (e) {
            showToast(e.message, 'danger');
        }
    });

    btnDisconnect.addEventListener('click', async () => {
        try {
            await postJson('/disconnect');
            document.body.classList.remove('connected');
            showToast('Camera disconnected', 'info');
            setState(STATE.DISCONNECTED);
        } catch (e) {
            showToast(e.message, 'danger');
        }
    });

    // -----------------------------------------------------------------
    //   Countdown + picture capture
    // -----------------------------------------------------------------
    async function startCountdownAndCapture() {
        // 1️⃣ Show 3‑2‑1 overlay
        countdownEl.textContent = '3';
        countdownEl.style.display = 'flex';
        for (let i = 3; i > 0; i--) {
            countdownEl.textContent = i;
            await new Promise(r => setTimeout(r, 1000));
        }
        countdownEl.style.display = 'none';

        // 2️⃣ Tell backend to take a picture
        const result = await postJson('/take-photo');
        showToast(`Photo saved: ${result.filename}`, 'success');

        // 3️⃣ Update UI state
        // If we have a collage, the server will have already fired the callback
        // which changes `#btnPrint` to enabled.  We just need to know if the
        // collage exists yet.
        const collageExists = document.body.classList.contains('collage-ready');
        setState(collageExists ? STATE.COLLAGE_READY : STATE.PHOTO_TAKEN);
    }

    btnTake.addEventListener('click', async () => {
        btnTake.disabled = true; // prevent double‑clicks
        try {
            await startCountdownAndCapture();
        } catch (e) {
            showToast(e.message, 'danger');
        } finally {
            btnTake.disabled = false;
        }
    });

    // -----------------------------------------------------------------
    //   Print collage
    // -----------------------------------------------------------------
    btnPrint.addEventListener('click', async () => {
        btnPrint.disabled = true;
        try {
            await postJson('/print-collage');
            showToast('Collage sent to printer', 'success');
        } catch (e) {
            showToast(e.message, 'danger');
        } finally {
            btnPrint.disabled = false;
        }
    });

    // -----------------------------------------------------------------
    //   Initialise UI
    // -----------------------------------------------------------------
    setState(STATE.DISCONNECTED);

    // -----------------------------------------------------------------
    //   OPTIONAL: Listen for a server‑sent event when collage is ready
    //   (If you prefer a WebSocket / SSE instead of the callback in
    //    camera.py, you could implement it here.)
    // -----------------------------------------------------------------
    // Example using EventSource:
    // const evtSource = new EventSource('/collage-ready');
    // evtSource.onmessage = (e) => {
    //     document.body.classList.add('collage-ready');
    //     setState(STATE.COLLAGE_READY);
    // };
})();