/* ============================================================
   PHOTO BEAN
   MAIN PHOTOBOOTH JAVASCRIPT
============================================================ */


/* ============================================================
   STATE
============================================================ */

let sessionActive = false;

let photoCount = 0;

let cameraConnected = false;

let automationRunning = false;

let currentBoothPhase = "idle";

let currentGalleryUrl = null;


/* ============================================================
   SHORTCUT
============================================================ */

const $ = id =>
    document.getElementById(id);


/* ============================================================
   ELEMENT REFERENCES
============================================================ */

let statusElement;

let statusDot;

let messageElement;

let startButton;

let countdownOverlay;

let countdownNumber;

let flash;

let collageOverlay;

let collageImage;

let printButton;

let retakeButton;

let menuButton;

let photoBean;

let beanSpeech;

let digitalGalleryPanel;

let digitalGalleryUnavailable;

let qrCodeContainer;

let galleryLink;

let galleryReadyMessage;


/* ============================================================
   BOOTH PHASE
============================================================ */

function setBoothPhase(
    phase,
    animate = true
) {

    if (
        ![
            "idle",
            "session",
            "complete"
        ].includes(phase)
    ) {
        return;
    }


    const transition =
        $("phaseTransition");


    const label =
        $("phaseLabel");


    const apply = () => {

        document.body.classList.remove(
            "phase-idle",
            "phase-session",
            "phase-complete"
        );


        document.body.classList.add(
            `phase-${phase}`
        );


        currentBoothPhase =
            phase;


        if (label) {

            if (phase === "idle") {

                label.textContent =
                    "READY";

            }

            else if (
                phase === "session"
            ) {

                label.textContent =
                    "PHOTO SESSION";

            }

            else {

                label.textContent =
                    "COMPLETE";

            }

        }

    };


    if (
        !animate
        || !transition
    ) {

        apply();

        return;

    }


    transition.className =
        "phase-transition";


    void transition.offsetWidth;


    transition.classList.add(
        `to-${phase}`
    );


    setTimeout(
        apply,
        400
    );


    setTimeout(
        () => {

            transition.className =
                "phase-transition";

        },
        900
    );

}


/* ============================================================
   PHOTO BEAN STATE
============================================================ */

function setBeanState(
    state,
    message
) {

    if (!photoBean) {
        return;
    }


    photoBean.className =
        "photo-bean-host";


    if (state) {

        photoBean.classList.add(
            state
        );

    }


    if (
        message
        && beanSpeech
    ) {

        beanSpeech.textContent =
            message;

    }

}


/* ============================================================
   RESET PHOTO BEAN
============================================================ */

function resetBean() {

    setBeanState(

        cameraConnected
            ? "ready"
            : "",

        cameraConnected
            ? "Ready when you are! Press Start Photo Session."
            : "Connect the camera and I'll get us ready!"

    );

}


/* ============================================================
   PHOTO BEAN ERROR
============================================================ */

function showBeanError(
    message
) {

    setBeanState(

        "error",

        message
        || "Something went wrong."

    );

}


/* ============================================================
   STATUS
============================================================ */

function setStatus(
    message
) {

    if (statusElement) {

        statusElement.textContent =
            message;

    }

}


/* ============================================================
   CONNECTION INDICATOR
============================================================ */

function setConnectionIndicator(
    connected
) {

    if (statusDot) {

        statusDot.classList.toggle(
            "connected",
            connected
        );

    }

}


/* ============================================================
   MESSAGE
============================================================ */

function showMessage(
    message,
    type = ""
) {

    if (!messageElement) {
        return;
    }


    messageElement.textContent =
        message;


    messageElement.className =
        "message " + type;

}


/* ============================================================
   SESSION UI
============================================================ */

function setSessionUI(
    active
) {

    document.body.classList.toggle(
        "booth-session-active",
        active
    );

}


/* ============================================================
   SLEEP
============================================================ */

const sleep = milliseconds =>
    new Promise(
        resolve =>
            setTimeout(
                resolve,
                milliseconds
            )
    );


/* ============================================================
   CONNECT CAMERA
============================================================ */

async function connectCamera() {

    if (cameraConnected) {
        return;
    }


    setStatus(
        "Connecting to camera..."
    );


    showMessage(
        "Connecting to Sony α7C II..."
    );


    setBeanState(
        "processing",
        "Connecting to the camera..."
    );


    try {

        const response =
            await fetch(
                "/connect",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (
            !response.ok
            || !data.success
        ) {

            throw new Error(
                data.message
                || "Camera connection failed."
            );

        }


        cameraConnected =
            true;


        setConnectionIndicator(
            true
        );


        setStatus(
            "Camera connected"
        );


        if ($("noCamera")) {

            $("noCamera").style.display =
                "none";

        }


        startButton.disabled =
            false;


        showMessage(
            "Camera ready. Press Start Photo Session.",
            "success"
        );


        setBeanState(
            "celebrate",
            "Camera connected! Let's take some photos!"
        );


        setTimeout(
            resetBean,
            1500
        );

    }

    catch (error) {

        cameraConnected =
            false;


        setConnectionIndicator(
            false
        );


        setStatus(
            "Camera connection failed"
        );


        startButton.disabled =
            true;


        showMessage(
            error.message,
            "error"
        );


        showBeanError(
            "I couldn't connect to the camera."
        );

    }

}


/* ============================================================
   DISCONNECT CAMERA
============================================================ */

async function disconnectCamera() {

    if (automationRunning) {

        showMessage(
            "Please wait until the session finishes.",
            "error"
        );

        return;

    }


    try {

        const response =
            await fetch(
                "/disconnect",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (
            !response.ok
            || data.success === false
        ) {

            throw new Error(
                data.message
                || "Could not disconnect camera."
            );

        }


        cameraConnected =
            false;


        sessionActive =
            false;


        setConnectionIndicator(
            false
        );


        setStatus(
            "Camera disconnected"
        );


        if ($("noCamera")) {

            $("noCamera").style.display =
                "flex";

        }


        startButton.disabled =
            true;


        showMessage(
            "Camera disconnected."
        );


        setBeanState(
            "",
            "Camera disconnected. I'll wait here!"
        );

    }

    catch (error) {

        showMessage(
            error.message,
            "error"
        );


        showBeanError(
            error.message
        );

    }

}


/* ============================================================
   START PHOTO SESSION
============================================================ */

async function startSession() {

    if (!cameraConnected) {

        showMessage(
            "Please connect the camera first.",
            "error"
        );


        showBeanError(
            "Connect the camera first!"
        );


        return;

    }


    if (automationRunning) {
        return;
    }


    automationRunning =
        true;


    sessionActive =
        true;


    photoCount =
        0;


    currentGalleryUrl =
        null;


    clearDigitalGallery();


    setBoothPhase(
        "session"
    );


    setSessionUI(
        true
    );


    startButton.disabled =
        true;


    resetPhotoSteps();

    updatePhotoCount();

    hideCollage();


    try {

        const response =
            await fetch(
                "/start-session",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (
            !response.ok
            || !data.success
        ) {

            throw new Error(
                data.message
                || "Could not start session."
            );

        }


        showMessage(
            "Get ready..."
        );


        setStatus(
            "Photo session starting..."
        );


        setBeanState(
            "countdown",
            "Three photos! Get ready!"
        );


        await sleep(
            1200
        );


        for (
            let number = 1;
            number <= 3;
            number++
        ) {

            await captureAutomaticPhoto(
                number
            );


            if (number < 3) {

                showMessage(
                    "Get ready for the next photo..."
                );


                setBeanState(

                    "ready",

                    number === 1
                        ? "Nice! Try another pose!"
                        : "Great! One last photo!"

                );


                await sleep(
                    1500
                );

            }

        }


        sessionActive =
            false;


        setStatus(
            "Creating collage..."
        );


        showMessage(
            "All photos captured. Creating collage..."
        );


        setBeanState(
            "processing",
            "Great shots! I'm making your collage..."
        );


        await sleep(
            800
        );


        await createCollageAutomatically();

    }

    catch (error) {

        sessionActive =
            false;


        setSessionUI(
            false
        );


        setBoothPhase(
            "idle"
        );


        showMessage(
            error.message,
            "error"
        );


        setStatus(
            "Session failed"
        );


        showBeanError(
            "Something went wrong during the photo session."
        );

    }

    finally {

        automationRunning =
            false;


        if (cameraConnected) {

            startButton.disabled =
                false;

        }

    }

}


/* ============================================================
   CAPTURE AUTOMATIC PHOTO
============================================================ */

async function captureAutomaticPhoto(
    number
) {

    const step =
        $(`step${number}`);


    if (step) {

        step.classList.add(
            "active"
        );


        step.querySelector(
            "div:last-child"
        ).textContent =
            "Get ready";

    }


    setStatus(
        `Preparing photo ${number}...`
    );


    setBeanState(
        "countdown",
        `Photo ${number} - get ready!`
    );


    await runCountdown();


    try {

        const response =
            await fetch(
                "/take-photo",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (
            !response.ok
            || !data.success
        ) {

            throw new Error(
                data.message
                || "Capture failed."
            );

        }


        triggerFlash();


        setBeanState(
            "capture",
            "Got it! 📸"
        );


        photoCount++;


        updatePhotoCount();


        if (step) {

            step.classList.remove(
                "active"
            );


            step.classList.add(
                "completed"
            );


            step.querySelector(
                "div:last-child"
            ).textContent =
                "Captured";

        }


        await sleep(
            500
        );

    }

    catch (error) {

        if (step) {

            step.classList.remove(
                "active"
            );

        }


        showBeanError(
            "I couldn't take that photo."
        );


        throw error;

    }

}


/* ============================================================
   COUNTDOWN
============================================================ */

async function runCountdown() {

    countdownOverlay.classList.add(
        "visible"
    );


    for (
        const number
        of ["3", "2", "1"]
    ) {

        countdownNumber.textContent =
            number;


        if (beanSpeech) {

            beanSpeech.textContent =

                number === "3"
                    ? "Get ready!"

                : number === "2"
                    ? "Hold that pose!"

                : "Smile!";

        }


        countdownNumber.style.animation =
            "none";


        void countdownNumber.offsetWidth;


        countdownNumber.style.animation =
            "countdownPulse .8s ease-out";


        await sleep(
            1000
        );

    }


    countdownNumber.textContent =
        "📸";


    if (beanSpeech) {

        beanSpeech.textContent =
            "Cheese!";

    }


    await sleep(
        250
    );


    countdownOverlay.classList.remove(
        "visible"
    );

}


/* ============================================================
   CAMERA FLASH
============================================================ */

function triggerFlash() {

    flash.classList.remove(
        "active"
    );


    void flash.offsetWidth;


    flash.classList.add(
        "active"
    );

}


/* ============================================================
   PHOTO COUNT
============================================================ */

function updatePhotoCount() {

    if ($("photoCount")) {

        $("photoCount").textContent =
            `${photoCount} / 3`;

    }

}


/* ============================================================
   RESET PHOTO STEPS
============================================================ */

function resetPhotoSteps() {

    for (
        let number = 1;
        number <= 3;
        number++
    ) {

        const step =
            $(`step${number}`);


        if (!step) {
            continue;
        }


        step.classList.remove(
            "active",
            "completed"
        );


        step.querySelector(
            "div:last-child"
        ).textContent =
            "Ready";

    }

}


/* ============================================================
   CLEAR DIGITAL GALLERY
============================================================ */

function clearDigitalGallery() {

    currentGalleryUrl =
        null;


    if (qrCodeContainer) {

        qrCodeContainer.innerHTML =
            "";

    }


    if (digitalGalleryPanel) {

        digitalGalleryPanel.classList.remove(
            "visible"
        );

    }


    if (digitalGalleryUnavailable) {

        digitalGalleryUnavailable.classList.remove(
            "visible"
        );

    }


    if (galleryLink) {

        galleryLink.href =
            "#";

    }

}


/* ============================================================
   SHOW DIGITAL GALLERY
============================================================ */

function showDigitalGallery(
    galleryUrl
) {

    clearDigitalGallery();


    if (!galleryUrl) {

        showDigitalGalleryUnavailable();

        return;

    }


    currentGalleryUrl =
        galleryUrl;


    if (galleryLink) {

        galleryLink.href =
            galleryUrl;

    }


    if (!qrCodeContainer) {

        return;

    }


    /*
        QRCode comes from qrcodejs loaded
        by index.html.
    */

    if (
        typeof QRCode
        === "undefined"
    ) {

        console.error(
            "QRCode library did not load."
        );


        showDigitalGalleryUnavailable();

        return;

    }


    new QRCode(
        qrCodeContainer,
        {
            text:
                galleryUrl,

            width:
                190,

            height:
                190,

            colorDark:
                "#000000",

            colorLight:
                "#ffffff",

            correctLevel:
                QRCode.CorrectLevel.H
        }
    );


    if (digitalGalleryPanel) {

        digitalGalleryPanel.classList.add(
            "visible"
        );

    }


    if (digitalGalleryUnavailable) {

        digitalGalleryUnavailable.classList.remove(
            "visible"
        );

    }

}


/* ============================================================
   DIGITAL GALLERY UNAVAILABLE
============================================================ */

function showDigitalGalleryUnavailable() {

    currentGalleryUrl =
        null;


    if (digitalGalleryPanel) {

        digitalGalleryPanel.classList.remove(
            "visible"
        );

    }


    if (digitalGalleryUnavailable) {

        digitalGalleryUnavailable.classList.add(
            "visible"
        );

    }

}


/* ============================================================
   AUTOMATIC COLLAGE
============================================================ */

async function createCollageAutomatically() {

    const response =
        await fetch(
            "/make-collage",
            {
                method: "POST"
            }
        );


    const data =
        await response.json();


    if (
        !response.ok
        || !data.success
    ) {

        throw new Error(
            data.message
            || "Could not create collage."
        );

    }


    setBoothPhase(
        "complete"
    );


    setStatus(
        "Collage ready"
    );


    showMessage(
        "Collage created successfully.",
        "success"
    );


    setBeanState(
        "celebrate",
        "Your collage is ready! ✨"
    );


    /*
        Show the locally generated collage.
    */

    collageImage.src =
        "/collage-image?t="
        + Date.now();


    collageImage.style.display =
        "block";


    /*
        DIGITAL GALLERY

        app.py returns:

        cloud_available
        gallery_url
        session_id
    */

    if (
        data.cloud_available
        && data.gallery_url
    ) {

        showDigitalGallery(
            data.gallery_url
        );


        console.log(
            "PhotoBean gallery:",
            data.gallery_url
        );

    }

    else {

        showDigitalGalleryUnavailable();


        console.warn(
            "PhotoBean digital gallery unavailable.",
            data.cloud_error || ""
        );

    }


    /*
        Show final result screen.
    */

    collageOverlay.classList.add(
        "visible"
    );


    printButton.style.display =
        "block";


    retakeButton.style.display =
        "block";


    menuButton.style.display =
        "block";


    setSessionUI(
        false
    );

}


/* ============================================================
   HIDE COLLAGE
============================================================ */

function hideCollage() {

    if (collageOverlay) {

        collageOverlay.classList.remove(
            "visible"
        );

    }


    if (collageImage) {

        collageImage.style.display =
            "none";

    }


    if (printButton) {

        printButton.style.display =
            "none";

    }


    clearDigitalGallery();

}


/* ============================================================
   RETAKE SESSION
============================================================ */

async function retakeSession() {

    if (automationRunning) {
        return;
    }


    if (!cameraConnected) {

        hideCollage();


        setBoothPhase(
            "idle"
        );


        showMessage(
            "Camera is not connected.",
            "error"
        );


        return;

    }


    hideCollage();


    photoCount =
        0;


    resetPhotoSteps();


    updatePhotoCount();


    setBeanState(
        "ready",
        "Let's try that again!"
    );


    await sleep(
        400
    );


    startSession();

}


/* ============================================================
   RETURN TO MENU
============================================================ */

function returnToMenu() {

    setBoothPhase(
        "idle"
    );


    hideCollage();


    sessionActive =
        false;


    automationRunning =
        false;


    photoCount =
        0;


    resetPhotoSteps();


    updatePhotoCount();


    setSessionUI(
        false
    );


    setStatus(

        cameraConnected
            ? "Camera connected"
            : "Camera disconnected"

    );


    showMessage(

        cameraConnected
            ? "Ready for another photo session."
            : "Connect the camera to begin."

    );


    startButton.disabled =
        !cameraConnected;


    resetBean();

}


/* ============================================================
   PRINT COLLAGE
============================================================ */

async function printCollage() {

    printButton.disabled =
        true;


    showMessage(
        "Sending collage to printer..."
    );


    setBeanState(
        "processing",
        "Printing your collage..."
    );


    try {

        const response =
            await fetch(
                "/print-collage",
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (
            !response.ok
            || !data.success
        ) {

            throw new Error(
                data.message
                || "Print failed."
            );

        }


        showMessage(
            "Print job sent successfully.",
            "success"
        );


        setStatus(
            "Collage printed"
        );


        setBeanState(
            "celebrate",
            "Printed! Thanks for visiting! 🎉"
        );

    }

    catch (error) {

        showMessage(
            error.message,
            "error"
        );


        showBeanError(
            "I couldn't print the collage."
        );

    }

    finally {

        printButton.disabled =
            false;

    }

}


/* ============================================================
   PAGE INITIALIZATION
============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        statusElement =
            $("status");


        statusDot =
            $("statusDot");


        messageElement =
            $("message");


        startButton =
            $("startSessionButton");


        countdownOverlay =
            $("countdownOverlay");


        countdownNumber =
            $("countdownNumber");


        flash =
            $("flash");


        collageOverlay =
            $("collagePreviewOverlay");


        collageImage =
            $("collageImage");


        printButton =
            $("printButton");


        retakeButton =
            $("retakeButton");


        menuButton =
            $("menuButton");


        photoBean =
            $("photoBean");


        beanSpeech =
            $("beanSpeech");


        digitalGalleryPanel =
            $("digitalGalleryPanel");


        digitalGalleryUnavailable =
            $("digitalGalleryUnavailable");


        qrCodeContainer =
            $("qrCodeContainer");


        galleryLink =
            $("galleryLink");


        galleryReadyMessage =
            $("galleryReadyMessage");


        setSessionUI(
            false
        );


        setBoothPhase(
            "idle",
            false
        );


        startButton.disabled =
            true;


        setConnectionIndicator(
            false
        );


        setStatus(
            "Camera disconnected"
        );


        resetPhotoSteps();


        updatePhotoCount();


        clearDigitalGallery();


        resetBean();

    }
);