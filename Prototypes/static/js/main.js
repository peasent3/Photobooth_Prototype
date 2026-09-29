/* =========================================================
   STILL MOTION ARCHIVES PHOTOBOOTH
   MAIN JAVASCRIPT

   File:
   static/js/main.js
========================================================= */


/* =========================================================
   GLOBAL STATE
========================================================= */

let sessionActive = false;
let photoCount = 0;
let cameraConnected = false;
let automationRunning = false;
let currentBoothPhase = "idle";


/* =========================================================
   SHORTCUT
========================================================= */

const $ = (id) =>
    document.getElementById(id);


/* =========================================================
   ELEMENT REFERENCES
========================================================= */

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


/* =========================================================
   PHASE SYSTEM

   idle     = BLUE
   session  = YELLOW
   complete = CORAL
========================================================= */

function setBoothPhase(
    phase,
    animate = true
) {

    if (
        phase !== "idle" &&
        phase !== "session" &&
        phase !== "complete"
    ) {
        return;
    }


    const transition =
        $("phaseTransition");


    const label =
        $("phaseLabel");


    const applyPhase = () => {

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

            else if (phase === "session") {

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
        !animate ||
        !transition
    ) {

        applyPhase();

        return;
    }


    transition.className =
        "phase-transition";


    void transition.offsetWidth;


    transition.classList.add(
        `to-${phase}`
    );


    setTimeout(
        applyPhase,
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


/* =========================================================
   PHOTO BEAN STATE
========================================================= */

function setBeanState(
    state,
    message
) {

    if (!photoBean) {
        return;
    }


    /*
        Remove animation states without removing
        movement classes such as bean-hidden.
    */

    photoBean.classList.remove(
        "ready",
        "countdown",
        "capture",
        "processing",
        "celebrate",
        "error"
    );


    if (state) {

        photoBean.classList.add(
            state
        );
    }


    if (
        message &&
        beanSpeech
    ) {

        beanSpeech.textContent =
            message;
    }
}


/* =========================================================
   RESET PHOTO BEAN
========================================================= */

function resetBean() {

    if (cameraConnected) {

        setBeanState(
            "ready",
            "Ready when you are! Press Start Photo Session."
        );

    }

    else {

        setBeanState(
            "",
            "Connect the camera and I'll get us ready!"
        );
    }
}


/* =========================================================
   PHOTO BEAN ERROR
========================================================= */

function showBeanError(
    message
) {

    setBeanState(
        "error",
        message ||
        "Something went wrong."
    );
}


/* =========================================================
   SHOW PHOTO BEAN
========================================================= */

function showBean() {

    if (!photoBean) {
        return;
    }


    photoBean.classList.remove(
        "bean-hidden"
    );


    photoBean.classList.add(
        "bean-visible"
    );
}


/* =========================================================
   HIDE PHOTO BEAN
========================================================= */

function hideBean() {

    if (!photoBean) {
        return;
    }


    photoBean.classList.remove(
        "bean-visible"
    );


    photoBean.classList.add(
        "bean-hidden"
    );
}


/* =========================================================
   MOVE PHOTO BEAN DURING SESSION

   IMPORTANT:

   Bean is never intentionally placed over .camera-frame.

   We measure:
   - the real live-view position
   - Bean's real dimensions
   - the browser dimensions

   Every possible position is checked for collision with
   the live-view rectangle.

   If no safe position exists, Bean hides.
========================================================= */

function moveBeanDuringSession(
    preferredPosition
) {

    if (!photoBean) {
        return;
    }


    const camera =
        document.querySelector(
            ".camera-frame"
        );


    if (!camera) {

        hideBean();

        return;
    }


    const cameraRect =
        camera.getBoundingClientRect();


    /*
        During phase-session, the speech bubble is
        display:none.

        Therefore this rectangle represents the mascot
        itself instead of mascot + speech bubble.
    */

    const beanRect =
        photoBean.getBoundingClientRect();


    const beanWidth =
        beanRect.width || 120;


    const beanHeight =
        beanRect.height || 140;


    /*
        Bean must stay this far away from the live view.
    */

    const cameraGap =
        22;


    /*
        Bean must stay this far away from browser edges.
    */

    const screenPadding =
        10;


    const screenWidth =
        window.innerWidth;


    const screenHeight =
        window.innerHeight;


    /* =====================================================
       POSSIBLE POSITIONS
    ====================================================== */

    const positions = {


        /* LEFT TOP */

        "left-top": {

            x:
                cameraRect.left
                -
                beanWidth
                -
                cameraGap,

            y:
                cameraRect.top
                +
                25
        },


        /* LEFT MIDDLE */

        "left-middle": {

            x:
                cameraRect.left
                -
                beanWidth
                -
                cameraGap,

            y:
                cameraRect.top
                +
                (
                    cameraRect.height
                    -
                    beanHeight
                )
                / 2
        },


        /* LEFT BOTTOM */

        "left-bottom": {

            x:
                cameraRect.left
                -
                beanWidth
                -
                cameraGap,

            y:
                cameraRect.bottom
                -
                beanHeight
                -
                25
        },


        /* RIGHT TOP */

        "right-top": {

            x:
                cameraRect.right
                +
                cameraGap,

            y:
                cameraRect.top
                +
                25
        },


        /* RIGHT MIDDLE */

        "right-middle": {

            x:
                cameraRect.right
                +
                cameraGap,

            y:
                cameraRect.top
                +
                (
                    cameraRect.height
                    -
                    beanHeight
                )
                / 2
        },


        /* RIGHT BOTTOM */

        "right-bottom": {

            x:
                cameraRect.right
                +
                cameraGap,

            y:
                cameraRect.bottom
                -
                beanHeight
                -
                25
        },


        /* ABOVE LEFT */

        "top-left": {

            x:
                cameraRect.left
                +
                25,

            y:
                cameraRect.top
                -
                beanHeight
                -
                cameraGap
        },


        /* ABOVE RIGHT */

        "top-right": {

            x:
                cameraRect.right
                -
                beanWidth
                -
                25,

            y:
                cameraRect.top
                -
                beanHeight
                -
                cameraGap
        },


        /* BELOW LEFT */

        "bottom-left": {

            x:
                cameraRect.left
                +
                25,

            y:
                cameraRect.bottom
                +
                cameraGap
        },


        /* BELOW RIGHT */

        "bottom-right": {

            x:
                cameraRect.right
                -
                beanWidth
                -
                25,

            y:
                cameraRect.bottom
                +
                cameraGap
        }
    };


    /* =====================================================
       CHECK WHETHER A POSITION IS SAFE
    ====================================================== */

    function positionFits(
        candidate
    ) {

        if (!candidate) {
            return false;
        }


        const left =
            candidate.x;


        const right =
            candidate.x
            +
            beanWidth;


        const top =
            candidate.y;


        const bottom =
            candidate.y
            +
            beanHeight;


        /*
            FIRST CHECK:
            Bean must fit inside the browser.
        */

        const insideScreen =
            left >= screenPadding &&
            right <=
                screenWidth
                -
                screenPadding &&
            top >= screenPadding &&
            bottom <=
                screenHeight
                -
                screenPadding;


        if (!insideScreen) {

            return false;
        }


        /*
            SECOND CHECK:
            Bean's rectangle must NOT intersect
            the live-view rectangle.
        */

        const overlapsCamera =
            left <
                cameraRect.right &&
            right >
                cameraRect.left &&
            top <
                cameraRect.bottom &&
            bottom >
                cameraRect.top;


        if (overlapsCamera) {

            return false;
        }


        /*
            THIRD CHECK:
            Maintain a little extra safety space around
            the camera instead of merely touching it.
        */

        const expandedCamera = {

            left:
                cameraRect.left
                -
                8,

            right:
                cameraRect.right
                +
                8,

            top:
                cameraRect.top
                -
                8,

            bottom:
                cameraRect.bottom
                +
                8
        };


        const overlapsSafetyArea =
            left <
                expandedCamera.right &&
            right >
                expandedCamera.left &&
            top <
                expandedCamera.bottom &&
            bottom >
                expandedCamera.top;


        return !overlapsSafetyArea;
    }


    /* =====================================================
       TRY REQUESTED POSITION
    ====================================================== */

    let selected =
        positions[
            preferredPosition
        ];


    /*
        If requested position doesn't fit, search
        for another safe location.
    */

    if (
        !positionFits(
            selected
        )
    ) {

        const fallbackOrder = [

            "left-top",
            "right-top",

            "left-middle",
            "right-middle",

            "left-bottom",
            "right-bottom",

            "top-left",
            "top-right",

            "bottom-left",
            "bottom-right"
        ];


        selected =
            null;


        for (
            const positionName
            of fallbackOrder
        ) {

            const candidate =
                positions[
                    positionName
                ];


            if (
                positionFits(
                    candidate
                )
            ) {

                selected =
                    candidate;

                break;
            }
        }
    }


    /* =====================================================
       NO SAFE LOCATION

       Do not put Bean over the live view.
       Hide him instead.
    ====================================================== */

    if (!selected) {

        hideBean();

        return;
    }


    /* =====================================================
       MOVE BEAN
    ====================================================== */

    photoBean.style.setProperty(
        "--bean-x",
        `${selected.x}px`
    );


    photoBean.style.setProperty(
        "--bean-y",
        `${selected.y}px`
    );


    showBean();
}


/* =========================================================
   IDLE POSITION

   Outside the camera whenever enough room exists.
========================================================= */

function moveBeanToIdlePosition() {

    if (!photoBean) {
        return;
    }


    const camera =
        document.querySelector(
            ".camera-frame"
        );


    if (!camera) {

        photoBean.style.setProperty(
            "--bean-x",
            "25px"
        );


        photoBean.style.setProperty(
            "--bean-y",
            "120px"
        );


        showBean();

        return;
    }


    const cameraRect =
        camera.getBoundingClientRect();


    const beanRect =
        photoBean.getBoundingClientRect();


    const beanWidth =
        beanRect.width || 285;


    const beanHeight =
        beanRect.height || 140;


    const gap =
        20;


    /*
        First try the left side.
    */

    let x =
        cameraRect.left
        -
        beanWidth
        -
        gap;


    let y =
        cameraRect.top
        +
        25;


    /*
        If there isn't enough room on the left,
        try the right.
    */

    if (x < 10) {

        x =
            cameraRect.right
            +
            gap;
    }


    /*
        If there also isn't enough room on the right,
        place Bean in the upper-left UI margin.

        This is for idle mode only. During the actual
        photo session, the stricter collision system
        above is used.
    */

    if (
        x + beanWidth >
        window.innerWidth - 10
    ) {

        x =
            20;


        y =
            90;
    }


    /*
        Keep inside browser.
    */

    x =
        Math.max(
            10,
            Math.min(
                x,
                window.innerWidth
                -
                beanWidth
                -
                10
            )
        );


    y =
        Math.max(
            80,
            Math.min(
                y,
                window.innerHeight
                -
                beanHeight
                -
                10
            )
        );


    photoBean.style.setProperty(
        "--bean-x",
        `${x}px`
    );


    photoBean.style.setProperty(
        "--bean-y",
        `${y}px`
    );


    showBean();
}


/* =========================================================
   STATUS
========================================================= */

function setStatus(
    message
) {

    if (statusElement) {

        statusElement.textContent =
            message;
    }
}


/* =========================================================
   CONNECTION INDICATOR
========================================================= */

function setConnectionIndicator(
    connected
) {

    if (!statusDot) {
        return;
    }


    statusDot.classList.toggle(
        "connected",
        connected
    );
}


/* =========================================================
   MESSAGE
========================================================= */

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


/* =========================================================
   SESSION UI
========================================================= */

function setSessionUI(
    active
) {

    document.body.classList.toggle(
        "booth-session-active",
        active
    );
}


/* =========================================================
   SLEEP
========================================================= */

function sleep(
    milliseconds
) {

    return new Promise(
        resolve =>
            setTimeout(
                resolve,
                milliseconds
            )
    );
}


/* =========================================================
   CONNECT CAMERA
========================================================= */

async function connectCamera() {

    if (cameraConnected) {

        showMessage(
            "Camera is already connected.",
            "success"
        );

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


    showBean();


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
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Camera connection failed."
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


        const noCamera =
            $("noCamera");


        if (noCamera) {

            noCamera.style.display =
                "none";
        }


        if (startButton) {

            startButton.disabled =
                false;
        }


        showMessage(
            "Camera ready. Press Start Photo Session.",
            "success"
        );


        setBeanState(
            "celebrate",
            "Camera connected! Let's take some photos!"
        );


        moveBeanToIdlePosition();


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


        if (startButton) {

            startButton.disabled =
                true;
        }


        showMessage(
            error.message,
            "error"
        );


        showBeanError(
            "I couldn't connect to the camera."
        );
    }
}


/* =========================================================
   DISCONNECT CAMERA
========================================================= */

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
            !response.ok ||
            data.success === false
        ) {

            throw new Error(
                data.message ||
                "Could not disconnect camera."
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


        const noCamera =
            $("noCamera");


        if (noCamera) {

            noCamera.style.display =
                "flex";
        }


        if (startButton) {

            startButton.disabled =
                true;
        }


        showMessage(
            "Camera disconnected."
        );


        setBeanState(
            "",
            "Camera disconnected. I'll wait here!"
        );


        setBoothPhase(
            "idle"
        );


        moveBeanToIdlePosition();
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


/* =========================================================
   START SESSION
========================================================= */

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


    /*
        BLUE -> YELLOW
    */

    setBoothPhase(
        "session"
    );


    setSessionUI(
        true
    );


    if (startButton) {

        startButton.disabled =
            true;
    }


    resetPhotoSteps();

    updatePhotoCount();

    hideCollage();


    /*
        Hide Bean while the camera frame expands.

        We wait before measuring the new camera position.
    */

    hideBean();


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
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Could not start photo session."
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


        /*
            Camera expansion transition is 0.5 seconds.

            1.2 seconds gives it plenty of time to finish
            before Bean's safe position is calculated.
        */

        await sleep(
            1200
        );


        /* =================================================
           THREE AUTOMATIC PHOTOS
        ================================================== */

        for (
            let photoNumber = 1;
            photoNumber <= 3;
            photoNumber++
        ) {

            await captureAutomaticPhoto(
                photoNumber
            );


            if (
                photoNumber < 3
            ) {

                showMessage(
                    "Get ready for the next photo..."
                );


                await sleep(
                    900
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


        /*
            Try bringing Bean back in a safe position
            while the collage is processing.
        */

        moveBeanDuringSession(
            "right-top"
        );


        setBeanState(
            "processing",
            "Great shots! I'm making your collage..."
        );


        await sleep(
            900
        );


        hideBean();


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


        moveBeanToIdlePosition();


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


        if (
            cameraConnected &&
            startButton
        ) {

            startButton.disabled =
                false;
        }
    }
}


/* =========================================================
   CAPTURE ONE PHOTO
========================================================= */

async function captureAutomaticPhoto(
    photoNumber
) {

    const step =
        $(`step${photoNumber}`);


    /* =====================================================
       DIFFERENT PREFERRED LOCATION FOR EACH PHOTO

       These are only preferences.

       moveBeanDuringSession() will automatically reject
       any position that overlaps the live view.
    ====================================================== */

    if (
        photoNumber === 1
    ) {

        moveBeanDuringSession(
            "left-top"
        );
    }


    else if (
        photoNumber === 2
    ) {

        moveBeanDuringSession(
            "right-middle"
        );
    }


    else {

        moveBeanDuringSession(
            "left-bottom"
        );
    }


    setBeanState(
        "countdown",
        `Photo ${photoNumber} - get ready!`
    );


    if (step) {

        step.classList.add(
            "active"
        );


        const label =
            step.querySelector(
                "div:last-child"
            );


        if (label) {

            label.textContent =
                "Get ready";
        }
    }


    setStatus(
        `Preparing photo ${photoNumber}...`
    );


    /*
        Give Bean time to slide into position.
    */

    await sleep(
        500
    );


    /*
        If a safe location was found, showBean() has
        already been called.

        If no safe location was found, Bean remains hidden.
    */


    await runCountdown();


    showMessage(
        `Taking photo ${photoNumber}...`
    );


    setStatus(
        `Capturing photo ${photoNumber}...`
    );


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
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                `Could not capture photo ${photoNumber}.`
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


            const label =
                step.querySelector(
                    "div:last-child"
                );


            if (label) {

                label.textContent =
                    "Captured";
            }
        }


        showMessage(
            `Photo ${photoNumber} captured.`,
            "success"
        );


        /*
            Brief reaction.
        */

        await sleep(
            550
        );


        /*
            Bean exits before next photo.
        */

        hideBean();


        await sleep(
            400
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


/* =========================================================
   COUNTDOWN
========================================================= */

async function runCountdown() {

    if (
        !countdownOverlay ||
        !countdownNumber
    ) {

        return;
    }


    countdownOverlay.classList.add(
        "visible"
    );


    for (
        const number of
        ["3", "2", "1"]
    ) {

        countdownNumber.textContent =
            number;


        if (beanSpeech) {

            if (
                number === "3"
            ) {

                beanSpeech.textContent =
                    "Get ready!";
            }

            else if (
                number === "2"
            ) {

                beanSpeech.textContent =
                    "Hold that pose!";
            }

            else {

                beanSpeech.textContent =
                    "Smile!";
            }
        }


        countdownNumber.style.animation =
            "none";


        void countdownNumber.offsetWidth;


        countdownNumber.style.animation =
            "countdownPulse 0.8s ease-out";


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


    countdownNumber.style.animation =
        "none";


    void countdownNumber.offsetWidth;


    countdownNumber.style.animation =
        "countdownPulse 0.35s ease-out";


    await sleep(
        250
    );


    countdownOverlay.classList.remove(
        "visible"
    );
}


/* =========================================================
   FLASH
========================================================= */

function triggerFlash() {

    if (!flash) {
        return;
    }


    flash.classList.remove(
        "active"
    );


    void flash.offsetWidth;


    flash.classList.add(
        "active"
    );
}


/* =========================================================
   PHOTO COUNT
========================================================= */

function updatePhotoCount() {

    const counter =
        $("photoCount");


    if (counter) {

        counter.textContent =
            `${photoCount} / 3`;
    }
}


/* =========================================================
   RESET PHOTO STEPS
========================================================= */

function resetPhotoSteps() {

    for (
        let i = 1;
        i <= 3;
        i++
    ) {

        const step =
            $(`step${i}`);


        if (!step) {
            continue;
        }


        step.classList.remove(
            "active",
            "completed"
        );


        const label =
            step.querySelector(
                "div:last-child"
            );


        if (label) {

            label.textContent =
                "Ready";
        }
    }
}


/* =========================================================
   CREATE COLLAGE
========================================================= */

async function createCollageAutomatically() {

    try {

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
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Could not create collage."
            );
        }


        /*
            YELLOW -> CORAL
        */

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
            Hide Bean while the full collage preview is open.

            This guarantees he cannot cover the collage.
        */

        hideBean();


        if (collageImage) {

            collageImage.src =
                "/collage-image?t=" +
                Date.now();


            collageImage.style.display =
                "block";
        }


        if (collageOverlay) {

            collageOverlay.classList.add(
                "visible"
            );
        }


        if (printButton) {

            printButton.style.display =
                "block";
        }


        if (retakeButton) {

            retakeButton.style.display =
                "block";
        }


        if (menuButton) {

            menuButton.style.display =
                "block";
        }


        setSessionUI(
            false
        );
    }

    catch (error) {

        showBeanError(
            "I couldn't create the collage."
        );


        throw new Error(
            "Could not create collage: " +
            error.message
        );
    }
}


/* =========================================================
   HIDE COLLAGE
========================================================= */

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
}


/* =========================================================
   RETAKE SESSION
========================================================= */

async function retakeSession() {

    if (automationRunning) {
        return;
    }


    if (!cameraConnected) {

        hideCollage();


        setSessionUI(
            false
        );


        setBoothPhase(
            "idle"
        );


        moveBeanToIdlePosition();


        showMessage(
            "Camera is not connected.",
            "error"
        );


        showBeanError(
            "We need to reconnect the camera first."
        );


        return;
    }


    hideCollage();


    photoCount =
        0;


    sessionActive =
        false;


    resetPhotoSteps();

    updatePhotoCount();


    setBeanState(
        "ready",
        "Let's try that again!"
    );


    hideBean();


    await sleep(
        400
    );


    startSession();
}


/* =========================================================
   RETURN TO MENU
========================================================= */

function returnToMenu() {

    /*
        CORAL -> BLUE
    */

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


    /*
        Wait for the camera to return to its idle size
        before positioning Bean.
    */

    setTimeout(
        moveBeanToIdlePosition,
        550
    );


    if (cameraConnected) {

        setStatus(
            "Camera connected"
        );


        showMessage(
            "Ready for another photo session."
        );
    }

    else {

        setStatus(
            "Camera disconnected"
        );


        showMessage(
            "Connect the camera to begin."
        );
    }


    if (startButton) {

        startButton.disabled =
            !cameraConnected;
    }


    resetBean();
}


/* =========================================================
   PRINT COLLAGE
========================================================= */

async function printCollage() {

    if (printButton) {

        printButton.disabled =
            true;
    }


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
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Print failed."
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

        if (printButton) {

            printButton.disabled =
                false;
        }
    }
}


/* =========================================================
   WINDOW RESIZE
========================================================= */

window.addEventListener(
    "resize",
    () => {

        /*
            During a photo session, do not guess where Bean
            should go. Hide him until the next photo, where
            his safe location will be recalculated.
        */

        if (sessionActive) {

            hideBean();

            return;
        }


        /*
            Normal idle mode.
        */

        moveBeanToIdlePosition();
    }
);


/* =========================================================
   INITIALIZE
========================================================= */

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


        /*
            Initial UI.
        */

        setSessionUI(
            false
        );


        /*
            Start in BLUE phase.
        */

        setBoothPhase(
            "idle",
            false
        );


        /*
            Camera starts disconnected.
        */

        if (startButton) {

            startButton.disabled =
                true;
        }


        setConnectionIndicator(
            false
        );


        setStatus(
            "Camera disconnected"
        );


        resetPhotoSteps();

        updatePhotoCount();


        /*
            Give the browser time to calculate all element
            dimensions before positioning Bean.
        */

        setTimeout(
            () => {

                moveBeanToIdlePosition();

                resetBean();

            },
            200
        );
    }
);